# Build the Remotion assembly manifest (studio/src/shorts/ShortAssembly.tsx) and copy its media into the ignored
# studio/public/media/nvidia-cuda-bet/. Three.js renders the picture only; Remotion does captions, cards, light leaks
# (screen blend), voice, ducked music, ambience beds and SFX.
# SFX are pinned so the sound's PEAK (or onset, for textures) lands on the target frame: from = target - peakLag
# (video-shotcraft sound-design 4.6). Run from anywhere: python audio/build_manifest.py
import json, os, re, shutil, subprocess, numpy as np
from pathlib import Path
from cues import cues
P = Path(__file__).resolve().parent; PROD = P.parent; REPO = PROD.parents[2]
SLUG = os.environ.get('SHORT_SLUG', PROD.name)
OUT = REPO / 'studio' / 'public' / 'media' / SLUG; OUT.mkdir(parents=True, exist_ok=True)
FPS = 30; C = cues(); T = json.load(open(PROD / 'timing.json', encoding='utf-8')); END = C['END']; NF = int(round(END * FPS))
A = PROD / 'assets' / 'sfx'; RES = Path(os.environ.get('VFX_RESOURCES', 'local-resources'))   # your editing resource library (path recorded in production.md)
LK = RES / 'Overlays/Light Leaks/LIGHT — LEAKS'
fr = lambda t: int(round(t * FPS)); db = lambda x: round(10 ** (x / 20), 4)

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
# film burns on the four act changes (user library Overlays/Film Burn), the burn's brightest frame on the cut frame:
# c17 peaks 1.50 s (bright 0.80-1.63), c8 peaks 1.23 s (bright 0.13-2.77) - measured with signalstats YAVG
FB = RES / 'Overlays/Film Burn'
BURN = {'c17': (FB / 'c17.mov', 1.50), 'c8': (FB / 'c8.mov', 1.23)}
for k, (cut, which) in enumerate([(C['l3'], 'c8'), (C['l5'], 'c17'), (C['l8'], 'c8'), (C['l10'], 'c17')]):
    src, pk = BURN[which]; pre, dur = 0.42, 0.9
    leaks.append({'src': leak(src, pk - pre, dur, f'burn{k}_{which}.mp4'), 'from': fr(cut - pre), 'durationInFrames': fr(dur), 'opacity': 0.85})
# ---- voice + ducked music (per-frame volume: -23 dB, -33 dB while someone speaks, 0.35 s release) ----
voice = copy(PROD / 'voice.wav'); music = copy(A / 'el_music.mp3')   # ElevenLabs Music (Starter, commercial licence); procedural audio/music.py was the free-tier stand-in
talk = np.zeros(NF)
for l in T['lines']:
    for w in l['words']: talk[max(0, fr(w['t']) - 2):min(NF, fr(w.get('e', w['t'] + 0.3)) + 2)] = 1
g = np.zeros(NF); s = 0.0
for i, x in enumerate(talk): s = x if x > s else s + (x - s) * (1 - np.exp(-1 / (0.35 * FPS))); g[i] = s
mvol = [round(db(-23) * (1 - v) + db(-33) * v, 4) for v in g]
for i in range(min(15, NF)): mvol[i] *= i / 15   # fade in
for i in range(min(18, NF)): mvol[NF - 1 - i] *= i / 18   # fade out into the loop cut
# ---- ambience beds ----
amb_o, amb_n = copy(A / 'el_office_amb.mp3'), copy(A / 'el_night_amb.mp3')
beds = [{'src': amb_o, 'from': 0, 'durationInFrames': fr(C['H0']) + 6, 'volume': db(-36)}, {'src': amb_n, 'from': fr(C['H0']) - 6, 'durationInFrames': fr(C['H1'] - C['H0']) + 12, 'volume': db(-31)},
        {'src': amb_o, 'from': fr(C['H1']) - 6, 'durationInFrames': NF - fr(C['H1']) + 6, 'volume': db(-37)}]
# ---- SFX: (file, target time, gain dB, max seconds, align mode, what it hits) — only sounds with a visible cause ----
L = lambda n: A / 'lib' / n; E = lambda n: A / n
EV = [(L('gleam.wav'), 2.15, -16, 2.0, 'peak', 'x-ray: 512 cores light up'),
      (E('el_bubble.mp3'), C['nob'] + 0.17, -14, None, 'peak', '"?" bubble 1'), (E('el_bubble.mp3'), C['nob'] + 0.32, -15, None, 'peak', '"?" bubble 2'),
      (E('el_typing.mp3'), C['cuda'] - 0.3, -22, 1.8, 'onset', 'he types (OTS)'),
      (L('glitch.wav'), C['ins'], -18, 0.6, 'peak', 'screen flips to math'),
      (L('swish.wav'), C['qend'] + 0.44, -14, None, 'peak', 'whip pan (mid-whip)'),
      (E('el_laugh.mp3'), C['qend'] + 0.45, -13, None, 'onset', 'coworkers laugh'),
      (E('el_bubble.mp3'), C['qend'] + 0.37, -15, None, 'peak', 'HA bubble 1'), (E('el_bubble.mp3'), C['qend'] + 0.49, -16, None, 'peak', 'HA bubble 2'),
      (L('tick.wav'), C['l5'] + 0.05, -19, C['H0'] - C['l5'] - 0.1, 'onset', 'wall clock spins'),
      (L('riser.wav'), C['H0'], -22, 2.2, 'peak', 'riser lands on "Then in 2012" cut'), (L('whoosh_soft2.wav'), C['H0'], -17, 1.4, 'peak', 'light-leak transition'),
      (E('el_typing.mp3'), C['stu'], -22, 1.4, 'onset', 'student types'), (E('el_fans.mp3'), C['two'] - 0.05, -17, 1.6, 'onset', 'card fans (ECU)'),
      (E('el_ding.mp3'), C['crush'] + 0.02, -12, None, 'peak', 'YES! / all checks'), (E('el_bubble.mp3'), C['crush'] + 0.07, -15, None, 'peak', 'YES bubble'),
      (L('scratch.wav'), C['H1'], -11, None, 'peak', 'record scratch on the dolly-zoom cut'), (E('el_gasp.mp3'), C['H1'] + 0.15, -14, None, 'peak', 'sting: investor pales'),
      *[(L('popa2.mp3'), C['four'] - 0.05 + i * 0.1 + 0.12, -21, 0.35, 'peak', f'CPU core {i + 1} pops') for i in range(4)],
      (L('popa4.mp3'), C['five'] + 0.15, -17, 1.0, 'peak', '512 cores pop in a wave'),
      *[(L(f'beep{1 + i % 4}.wav'), C['like'] + i * 0.45, -26, None, 'onset', 'GPU grading') for i in range(5)],
      (E('el_ding.mp3'), C['beat'], -14, None, 'peak', 'GPU bar full'),
      (L('whoosh_soft1.wav'), END - 0.35, -19, 2.4, 'peak', 'push into the card (loop)'),
      # paper swipes on the main cuts (two takes, alternating; peak on the cut)
      *[(E(f'el_paper{1 + k % 2}.mp3'), t, -17 if k % 2 else -16, None, 'peak', f'paper swipe: {name}') for k, (t, name) in enumerate([
          (C['nob'], 'to the stares'), (C['l3'], 'investor walks in (film burn)'), (C['l4'], 'to "keep shipping it"'), (C['l5'], 'time-lapse (film burn)'),
          (C['H0'], 'into 2012'), (C['l8'], 'science (film burn)'), (C['l9'], 'both boards'), (C['l10'], 'finale (film burn)')])]]
sfx, lags = [], {}
for f, t, gdb, mx, mode, note in EV:
    k = (str(f), mode); lags[k] = lags.get(k) if k in lags else lag(f, mode)
    start = t - lags[k]; skip = max(0.0, -start); start = max(0.0, start)
    sfx.append({'src': copy(f), 'from': fr(start), 'trimBefore': fr(skip), 'durationInFrames': fr(mx) if mx else None, 'volume': db(gdb), 'note': note, 'lag': round(lags[k], 3)})
# ---- captions (word pop, keywords coloured) + the year cards ----
GREEN = {'nvidia', 'cuda', 'ai', 'gpu'}; YELLOW = {'supercomputer', 'nobody', 'investors', 'calculator', 'crushed', 'bedroom', 'cores', 'professors', 'students', 'math'}
ws = [w for l in T['lines'] for w in l['words']]; words = []
for i, w in enumerate(ws):
    key = re.sub(r'[^a-z0-9]', '', w['w'].lower()); nxt = ws[i + 1]['t'] if i + 1 < len(ws) else w['t'] + 0.8
    col = '#9cff4a' if key in GREEN else '#ffd400' if (key in YELLOW or any(ch.isdigit() for ch in key)) else '#ffffff'
    words.append({'text': w['w'].strip('"“”'), 'from': fr(w['t']), 'to': fr(min(nxt, w['t'] + 1.2)), 'color': col, 'speaker': w.get('spk', 'narrator')})
cards = [{'text': c['text'], 'from': fr(c['from']), 'to': fr(c['to']), 'color': c.get('color', '#ffd400')} for c in json.load(open(PROD / 'cards.json', encoding='utf-8'))]
font = copy(PROD / 'engine' / 'film' / 'Inter-Black.otf')
M = {'fps': FPS, 'durationInFrames': NF, 'width': 1080, 'height': 1920, 'video': f'media/{SLUG}/picture.mp4', 'font': font, 'captionY': 0.78,
     'voice': {'src': voice, 'volume': 1.0}, 'music': {'src': music, 'volumes': mvol}, 'beds': beds, 'sfx': sfx, 'leaks': leaks, 'words': words, 'cards': cards}
(OUT / 'manifest.json').write_text(json.dumps(M, ensure_ascii=False), encoding='utf-8')
for s_ in sfx: print(f"{s_['from'] / FPS:6.2f}s lag {s_['lag']:.2f}  {s_['note']}")
print('frames', NF, '| sfx', len(sfx), '| words', len(words), '->', OUT / 'manifest.json')
