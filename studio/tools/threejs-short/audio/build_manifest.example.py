# Build the Remotion assembly manifest (studio/src/shorts/ShortAssembly.tsx) and copy its media into the ignored
# studio/public/media/<slug>/. Three.js renders the picture only; Remotion does captions, cards, light leaks
# (screen blend), voice, ducked music, ambience beds and SFX.
# SFX are pinned so the sound's PEAK (or onset, for textures) lands on the target frame: from = target - peakLag
# (video-shotcraft sound-design 4.6). Run from anywhere: python audio/build_manifest.py
import json, math, os, re, shutil, subprocess, numpy as np
from pathlib import Path
from cues import cues
P = Path(__file__).resolve().parent; PROD = P.parent; REPO = PROD.parents[2]
SLUG = os.environ.get('SHORT_SLUG', PROD.name)
OUT = REPO / 'studio' / 'public' / 'media' / SLUG; OUT.mkdir(parents=True, exist_ok=True)
FPS = 30; C = cues(); T = json.load(open(PROD / 'timing.json', encoding='utf-8')); END = C['END']; NF = int(round(END * FPS))
A = PROD / 'assets' / 'sfx'; RES = Path(os.environ.get('VFX_RESOURCES', 'local-resources'))   # your editing resource library (path recorded in production.md)
LK = RES / 'Overlays/Light Leaks/LIGHT — LEAKS'
fr = lambda t: int(round(t * FPS)); cutfr = lambda t: math.ceil(t * FPS - 1e-6); db = lambda x: round(10 ** (x / 20), 4)

def pcm(path, sr=48000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<f4').astype(np.float64)
def lag(path, mode):   # seconds from file start to its peak (10 ms RMS) or onset (-24 dB below peak)
    x = pcm(path); w = 480; n = len(x) // w; r = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1) + 1e-12)
    pk = int(r.argmax()); return pk * 0.01 if mode == 'peak' else int(np.argmax(r > r[pk] * 10 ** (-24 / 20))) * 0.01
def copy(src, name=None):
    dst = OUT / (name or Path(src).name); shutil.copyfile(src, dst); return f'media/{SLUG}/{dst.name}'

# ---- picture: the three.js segments, concatenated without re-encoding ----
segs = PROD / 'segs.txt'; segs.write_text(''.join(f"file 'engine/out/seg{i}.mp4'\n" for i in (1, 2, 3)))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', segs, '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-g', '15', '-pix_fmt', 'yuv420p', '-r', '30', OUT / 'picture.mp4'], check=True, cwd=PROD)   # re-encode: clean timestamps + short GOP so Remotion seeks fast
# ---- light leaks, pre-cut to 9:16 (blended with mix-blend-mode: screen in the browser, i.e. in RGB) ----
def leak(src, ss, dur, name):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', src, '-vf', 'scale=-2:1920,crop=1080:1920,fps=30', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', OUT / name], check=True)
    return f'media/{SLUG}/{name}'
leaks = [{'src': leak(LK / '13.mp4', 0, 1.0, 'leak_2012.mp4'), 'from': fr(C['H0'] - 0.45), 'durationInFrames': 30, 'opacity': 0.7},
         {'src': leak(LK / '10.mp4', 23.5, 1.5, 'leak_yes.mp4'), 'from': fr(C['crush']), 'durationInFrames': 45, 'opacity': 0.6}]
# film burns on two act changes (iris/whips own the other transitions) (user library Overlays/Film Burn), the burn's brightest frame on the cut frame:
# c17 peaks 1.50 s (bright 0.80-1.63), c8 peaks 1.23 s (bright 0.13-2.77) - measured with signalstats YAVG
FB = RES / 'Overlays/Film Burn'
BURN = {'c17': (FB / 'c17.mov', 1.50), 'c8': (FB / 'c8.mov', 1.23)}
for k, (cut, which) in enumerate([(C['l3'], 'c8'), (C['l5'], 'c17')]):
    src, pk = BURN[which]; pre, dur = 0.42, 0.9
    leaks.append({'src': leak(src, pk - pre, dur, f'burn{k}_{which}.mp4'), 'from': fr(cut - pre), 'durationInFrames': fr(dur), 'opacity': 0.85})
# ---- voice + ducked music (measured loudness, 0.35 s release) ----
voice = copy(PROD / 'voice.wav'); music = copy(A / 'el_music.mp3')   # ElevenLabs Music (Starter, commercial licence); procedural audio/music.py was the free-tier stand-in
talk = np.zeros(NF)
for l in T['lines']:
    for w in l['words']: talk[max(0, fr(w['t']) - 2):min(NF, fr(w.get('e', w['t'] + 0.3)) + 2)] = 1
g = np.zeros(NF); s = 0.0
for i, x in enumerate(talk): s = x if x > s else s + (x - s) * (1 - np.exp(-1 / (0.35 * FPS))); g[i] = s
def lufs(path):   # integrated loudness (EBU R128) of a file
    out = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(path), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[0-9.]+) LUFS', out)[-1])
# v5 used -14/-7 LU (user favourite); v7 reference-study decision: -10/-5 LU under the measured voice.
# (static -23/-33 dB gains put a -18 LUFS track ~30 dB under the voice: present in the mix but inaudible)
vL, mL = lufs(PROD / 'voice.wav'), lufs(OUT / Path(music).name); duck_db, open_db = vL - 10 - mL, vL - 5 - mL
print(f'voice {vL:.1f} LUFS, music {mL:.1f} LUFS -> music gain {duck_db:.1f} dB under speech, {open_db:.1f} dB in pauses')
mvol = [round(db(open_db) * (1 - v) + db(duck_db) * v, 4) for v in g]
for i in range(min(15, NF)): mvol[i] *= i / 15   # fade in
for i in range(min(18, NF)): mvol[NF - 1 - i] *= i / 18   # fade out into the loop cut
# ---- ambience beds ----
amb_o, amb_n = copy(A / 'el_office_amb.mp3'), copy(A / 'el_night_amb.mp3')
beds = [{'src': amb_o, 'from': 0, 'durationInFrames': fr(C['H0']) + 6, 'volume': db(-36)}, {'src': amb_n, 'from': fr(C['H0']) - 6, 'durationInFrames': fr(C['H1'] - C['H0']) + 12, 'volume': db(-31)},
        {'src': amb_o, 'from': fr(C['H1']) - 6, 'durationInFrames': NF - fr(C['H1']) + 6, 'volume': db(-37)}]
# ---- SFX: (file, target time, gain dB, max seconds, align mode, what it hits) — only sounds with a visible cause ----
L = lambda n: A / 'lib' / n; E = lambda n: A / n
EV = [   # v8b: opening thinned (user: SFX spam in the first seconds) — no gleam, one bubble
      (E('el_bubble.mp3'), C['nob'] + 0.17, -14, None, 'peak', '"?" bubble'),
      (L('glitch_n.wav'), C['ins'], -18, 0.6, 'peak', 'screen flips to math'),
      (E('el_v8_laugh.wav'), C['qend'] + 0.08,   # v11: let the tail of 'open?' ring out
       -10, None, 'onset', 'coworkers laugh (2.2 s, fades under Jensen)'),
      (E('el_bubble.mp3'), C['qend'] + 0.07, -15, None, 'peak', 'HA bubble'),
      (L('whoosh_soft2.wav'), C['H0'], -17, 1.4, 'peak', 'light-leak transition'),
      (E('el_ding.mp3'), C['crush'] + 0.02, -12, None, 'peak', 'YES! / all checks'), (E('el_bubble.mp3'), C['crush'] + 0.07, -15, None, 'peak', 'YES bubble'),
      (L('scratch.wav'), C['H1'], -11, None, 'peak', 'record scratch on the dolly-zoom cut'), (E('el_gasp.mp3'), C['H1'] + 0.15, -14, None, 'peak', 'sting: investor pales'),
      *[(L('popa2.mp3'), C['four'] - 0.05 + i * 0.1 + 0.12, -21, 0.35, 'peak', f'CPU core {i + 1} pops') for i in range(4)],
      (E('el_ding.mp3'), C['beat'], -14, None, 'peak', 'GPU bar full'),
      (L('whoosh_soft1.wav'), END - 0.35, -19, 2.4, 'peak', 'push into the card (loop)'),
      (E('el_paper1.mp3'), C['fifty'] + 0.3, -16, None, 'peak', '+50% tag lands'),
      (E('el_v7_cash_hit.wav'), C['fifty'] + 0.3, -16, None, 'peak', '+50% cash register'),
      *[(E('el_v7_calendar_hit_n.wav'), C['l5'] + 0.05 + k * C['calStep'] + 0.06, -20, None, 'peak', f'calendar flick {k + 1}') for k in (0,)],   # v11: 1 flick (later ones sat under speech)
      *[(E('el_v7_counter_hit_n.wav'), C[key], -17, None, 'peak', f'counter flip {key}') for key in ('nobody5',)],   # v8b: the 'labs' click sat under continuous speech
      *[(E('el_v7_thunder.mp3'), t, -16, None, 'peak', f'lightning {i + 1}') for i, t in enumerate(C['bolts'])],
      (E('el_v7_iris_n.wav'), C['l8'] - 0.1, -16, None, 'peak', 'iris closes into science'),
      *[(E(f'el_paper{1 + k % 2}_n.wav'), t, -17, None, 'peak', f'paper swipe: {name}') for k, (t, name) in enumerate([
          (C['l3'], 'investor (film burn)'), (C['l5'], 'calendar (film burn)'), (C['H0'], 'into 2012')])]]
_vx = pcm(PROD / 'voice.wav'); _VSR = 48000
def _db_rms(x): return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
def _peak50(x): w = 2400; k = len(x) // w; return 20 * np.log10(np.sqrt((x[:k * w].reshape(k, w) ** 2).mean(1)).max() + 1e-9) if k else -120
_srcpk = {}
sfx, lags = [], {}
for f, t, gdb, mx, mode, note in EV:
    k = (str(f), mode); lags[k] = lags.get(k) if k in lags else lag(f, mode)
    lead = min(lags[k], mx / 2) if mx and mode == 'peak' else lags[k]
    source_trim = lags[k] - lead
    start = t - lead; skip = source_trim + max(0.0, -start); start = max(0.0, start)
    assert not mx or mode != 'peak' or fr(lead) < fr(mx), (note, lead, mx)
    _srcpk[str(f)] = _srcpk.get(str(f)) or _peak50(pcm(f)); win = _vx[int(t * _VSR):int((t + (mx or 0.6)) * _VSR)]; vlev = _db_rms(win) if len(win) else -60
    gain = min(0.0, max(gdb + 3, (vlev - 5) - _srcpk[str(f)]))   # audible floor: voice RMS − 5 dB (−2 dB sounded crowded)
    sfx.append({'src': copy(f), 'from': fr(start), 'trimBefore': fr(skip), 'durationInFrames': fr(mx) if mx else None, 'volume': db(gain), 'note': note, 'lag': round(lead, 3), 'sourceLag': round(lags[k], 3)})
# ---- captions (word pop, keywords coloured) + the year cards ----
GREEN = {'nvidia', 'cuda', 'ai', 'gpu'}; YELLOW = {'supercomputer', 'nobody', 'investors', 'calculator', 'crushed', 'bedroom', 'cores', 'professors', 'students', 'math'}
ws = [w for l in T['lines'] for w in l['words']]; words = []
for i, w in enumerate(ws):
    key = re.sub(r'[^a-z0-9]', '', w['w'].lower()); nxt = ws[i + 1]['t'] if i + 1 < len(ws) else w['t'] + 0.8
    col = '#9cff4a' if key in GREEN else '#ffd400' if (key in YELLOW or any(ch.isdigit() for ch in key)) else '#ffffff'
    words.append({'text': w['w'].strip('"“”'), 'from': fr(w['t']), 'to': fr(min(nxt, w['t'] + 1.2, max(w['e'] + 0.35, w['t'] + 0.3))), 'color': col, 'speaker': w.get('spk', 'narrator')})
# word times come from forced alignment (tools/align.py); the old hard-coded Jensen onset (16.70 s) showed the word 1.3 s early
cards = []
font = copy(PROD / 'engine' / 'film' / 'Inter-Black.otf')
M = {'fps': FPS, 'durationInFrames': NF, 'width': 1080, 'height': 1920, 'video': f'media/{SLUG}/picture.mp4', 'font': font, 'captionY': 0.70,
     'voice': {'src': voice, 'volume': 1.0}, 'music': {'src': music, 'volumes': mvol}, 'beds': beds, 'sfx': sfx, 'leaks': leaks, 'words': words, 'cards': cards,
     'irises': [{'from': fr(C['iris']), 'mid': fr(C['l8']), 'to': fr(C['l8'] + 0.3), 'cx': 0.62, 'cy': 0.25}],
     'whips': []}   # v8 audit: 2D smears over a still 3D camera read as jumps; cuts are hard cuts on words with continuous camera motion
assert NF == int(round(T['duration'] * FPS)) and len(words) > 130   # frame count follows timing.json (was hard-coded to the v7 length)
assert all(0 <= w['from'] < w['to'] <= NF for w in words)
assert all(0 <= i['from'] < i['mid'] < i['to'] < NF for i in M['irises'])
assert all(0 <= w['at'] < NF and w['dir'] in (-1, 1) for w in M['whips'])
(OUT / 'manifest.json').write_text(json.dumps(M, ensure_ascii=False), encoding='utf-8')
for s_ in sfx: print(f"{s_['from'] / FPS:6.2f}s lag {s_['lag']:.2f}  {s_['note']}")
print('frames', NF, '| sfx', len(sfx), '| words', len(words), '->', OUT / 'manifest.json')
