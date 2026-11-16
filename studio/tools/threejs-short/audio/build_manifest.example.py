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
segs = PROD / 'segs.txt'; segs.write_text(''.join(f"file 'engine/out/seg{i}.mp4'\n" for i in range(1, len(C['SETS']) + 1)))   # one segment per set (cues SETS)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', segs, '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-g', '15', '-pix_fmt', 'yuv420p', '-r', '30', OUT / 'picture.mp4'], check=True, cwd=PROD)   # re-encode: clean timestamps + short GOP so Remotion seeks fast
# ---- light leaks, pre-cut to 9:16 (blended with mix-blend-mode: screen in the browser, i.e. in RGB) ----
def leak(src, ss, dur, name):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', src, '-vf', 'scale=-2:1920,crop=1080:1920,fps=30', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', OUT / name], check=True)
    return f'media/{SLUG}/{name}'
leaks = []   # e.g. leaks.append({'src': leak(LK / '13.mp4', 0, 1.0, 'leak_a.mp4'), 'from': fr(C['l3'] - 0.45), 'durationInFrames': 30, 'opacity': 0.7})
# Film burns: put the burn's brightest frame (measure with signalstats YAVG) on the cut frame, e.g.
# FB = RES / 'Overlays/Film Burn'; src, pk = FB / 'c8.mov', 1.23
# leaks.append({'src': leak(src, pk - 0.42, 0.9, 'burn0.mp4'), 'from': fr(C['l3'] - 0.42), 'durationInFrames': fr(0.9), 'opacity': 0.85})
# ---- voice + ducked music (measured loudness, 0.35 s release) ----
voice = copy(PROD / 'voice.wav')
music = copy(next(f for f in (A / 'music.mp3', P / 'music.wav') if f.exists()))   # ElevenLabs Music (paid plans allow commercial use), else audio/music_fallback.py
talk = np.zeros(NF)
for l in T['lines']:
    for w in l['words']: talk[max(0, fr(w['t']) - 2):min(NF, fr(w.get('e', w['t'] + 0.3)) + 2)] = 1
g = np.zeros(NF); s = 0.0
for i, x in enumerate(talk): s = x if x > s else s + (x - s) * (1 - np.exp(-1 / (0.35 * FPS))); g[i] = s
def lufs(path):   # integrated loudness (EBU R128) of a file
    out = subprocess.run(['ffmpeg', '-v', 'info', '-i', str(path), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[0-9.]+) LUFS', out)[-1])
# Music level from measured loudness: -10 LU under speech, -5 LU in pauses (-14/-7 LU is a quieter approved choice).
# (static -23/-33 dB gains put a -18 LUFS track ~30 dB under the voice: present in the mix but inaudible)
vL, mL = lufs(PROD / 'voice.wav'), lufs(OUT / Path(music).name)
if vL < -50: vL = -20.0   # silent draft voice (voice/silent_timing.py): assume speech at -20 LUFS
duck_db, open_db = vL - 10 - mL, vL - 5 - mL
print(f'voice {vL:.1f} LUFS, music {mL:.1f} LUFS -> music gain {duck_db:.1f} dB under speech, {open_db:.1f} dB in pauses')
mvol = [round(db(open_db) * (1 - v) + db(duck_db) * v, 4) for v in g]
for i in range(min(15, NF)): mvol[i] *= i / 15   # fade in
for i in range(min(18, NF)): mvol[NF - 1 - i] *= i / 18   # fade out into the loop cut
# ---- ambience beds ----
amb = A / 'ambience.mp3'   # room tone; use one bed per set when the film changes set
beds = [{'src': copy(amb), 'from': 0, 'durationInFrames': NF, 'volume': db(-36)}] if amb.exists() else []
# ---- SFX: (file, target time, gain dB, max seconds, align mode, what it hits) — only sounds with a visible cause ----
L = lambda n: A / 'lib' / n; E = lambda n: A / n
# 25-30 SFX in a 50 s Short is plenty; keep the hook's first seconds sparse. Example entries:
#   (E('bubble.mp3'), C['l2'] + 0.17, -14, None, 'peak', 'thought bubble pops'),
#   (L('whoosh_soft.wav'), C['l3'], -17, 1.4, 'peak', 'light-leak transition'),
EV = []
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
# ---- captions (word pop; keywords coloured, numbers always yellow) ----
GREEN = set()   # brand words, e.g. {'nvidia', 'gpu'}
YELLOW = set()  # story keywords, e.g. {'nobody', 'crushed'}
ws = [w for l in T['lines'] for w in l['words']]; words = []
for i, w in enumerate(ws):
    key = re.sub(r'[^a-z0-9]', '', w['w'].lower()); nxt = ws[i + 1]['t'] if i + 1 < len(ws) else w['t'] + 0.8
    col = '#9cff4a' if key in GREEN else '#ffd400' if (key in YELLOW or any(ch.isdigit() for ch in key)) else '#ffffff'
    words.append({'text': w['w'].strip('"“”'), 'from': fr(w['t']), 'to': fr(min(nxt, w['t'] + 1.2, max(w['e'] + 0.35, w['t'] + 0.3))), 'color': col, 'speaker': w.get('spk', 'narrator')})
# word times come from forced alignment (voice/align.py); never hard-code a word onset (one went stale after a refit)
cards = []
font = copy(PROD / 'engine' / 'film' / 'Inter-Black.otf')
M = {'fps': FPS, 'durationInFrames': NF, 'width': 1080, 'height': 1920, 'video': f'media/{SLUG}/picture.mp4', 'font': font, 'captionY': 0.70,
     'voice': {'src': voice, 'volume': 1.0}, 'music': {'src': music, 'volumes': mvol}, 'beds': beds, 'sfx': sfx, 'leaks': leaks, 'words': words, 'cards': cards,
     'irises': []}   # e.g. [{'from': fr(C['l8'] - 0.45), 'mid': fr(C['l8']), 'to': fr(C['l8'] + 0.3), 'cx': 0.62, 'cy': 0.25}]; other cuts: hard cuts on words
assert NF == int(round(T['duration'] * FPS)) and words   # frame count follows timing.json
assert all(0 <= w['from'] < w['to'] <= NF for w in words)
assert all(0 <= i['from'] < i['mid'] < i['to'] < NF for i in M['irises'])
(OUT / 'manifest.json').write_text(json.dumps(M, ensure_ascii=False), encoding='utf-8')
for s_ in sfx: print(f"{s_['from'] / FPS:6.2f}s lag {s_['lag']:.2f}  {s_['note']}")
print('frames', NF, '| sfx', len(sfx), '| words', len(words), '->', OUT / 'manifest.json')
