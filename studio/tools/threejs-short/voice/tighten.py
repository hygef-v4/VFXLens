# Shorten long pauses between words (natural voice, faster read) before fit.py.
# in/out: voice_raw.mp3 + timing_raw.json (in place; originals kept as *_loose.*). Gaps longer than MAXGAP shrink to MAXGAP
# (cut from the middle of the silence, 10 ms crossfade). Keep listed beats untouched: --keep <after-word-index>...
# Usage: python tools/tighten.py [--maxgap 0.22] [--keep-after-line l3]
import argparse, json, shutil, subprocess, wave, numpy as np
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('--maxgap', type=float, default=0.22); ap.add_argument('--keep-after-line', nargs='*', default=[])
a = ap.parse_args(); P = Path('.'); SR = 44100
if not Path('timing_raw_loose.json').exists(): shutil.copy('timing_raw.json', 'timing_raw_loose.json'); shutil.copy('voice_raw.mp3', 'voice_raw_loose.mp3')
T = json.load(open('timing_raw_loose.json', encoding='utf-8'))
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'voice_raw_loose.mp3', '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout, '<i2').astype(np.float64) / 32768
words = [(li, w) for li, l in enumerate(T['lines']) for w in l['words']]
keep = {li for li, l in enumerate(T['lines']) if l['id'] in a.keep_after_line}
cuts = []   # (start, end) seconds of silence to remove — found on the waveform (word end times include trailing silence)
w = int(0.01 * SR); n = len(x) // w; r = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1)); thr = r.max() * 10 ** (-38 / 20)
keep_spans = []   # beats to leave alone: the pause after each listed line (e.g. the laugh after the question)
for li in keep:
    if li + 1 < len(T['lines']): keep_spans.append((T['lines'][li]['words'][-1]['t'], T['lines'][li + 1]['start']))
i = 0
while i < n:
    if r[i] < thr:
        j = i
        while j < n and r[j] < thr: j += 1
        g0, g1 = i * 0.01, j * 0.01
        if g1 - g0 > a.maxgap and g0 > 0.35 and j < n and not any(k0 - 0.05 <= g0 and g1 <= k1 + 0.6 for k0, k1 in keep_spans):
            mid = (g0 + g1) / 2; rm = (g1 - g0) - a.maxgap; cuts.append((mid - rm / 2, mid + rm / 2))
        i = j
    else: i += 1
xf = int(0.01 * SR); out = []; pos = 0
for c0, c1 in cuts:
    i0, i1 = int(c0 * SR), int(c1 * SR); seg = x[pos:i0].copy()
    if out and len(seg) > xf: seg[:xf] *= np.linspace(0, 1, xf)
    if len(seg) > xf: seg[-xf:] *= np.linspace(1, 0, xf)
    out.append(seg); pos = i1
out.append(x[pos:]); y = np.concatenate(out)
def shift(t):   # map an old time to the new timeline
    return t - sum(min(max(0.0, t - c0), c1 - c0) for c0, c1 in cuts)
for l in T['lines']:
    for w in l['words']: w['t'], w['e'] = round(shift(w['t']), 3), round(shift(w['e']), 3)
    l['start'], l['end'] = l['words'][0]['t'], l['words'][-1]['e']
T['duration'] = round(len(y) / SR, 3)
with wave.open('voice_tight.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'voice_tight.wav', '-c:a', 'libmp3lame', '-q:a', '2', 'voice_raw.mp3'], check=True)
json.dump(T, open('timing_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'removed {sum(c1 - c0 for c0, c1 in cuts):.2f} s in {len(cuts)} gaps -> {T["duration"]:.2f} s')
