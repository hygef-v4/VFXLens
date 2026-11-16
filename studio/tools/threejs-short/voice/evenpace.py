# Even out the narration pace line by line (TTS reads "dramatic" lines slower), after tighten.py and before fit.py.
# Each line (from its first word to its last word end) is time-stretched with ffmpeg atempo (pitch kept) toward
# --wps words/s, clamped to [--min, --max]; the silences between lines are kept. In/out: voice_raw.mp3 + timing_raw.json
# (in place; the input is kept as *_uneven.*). Usage: python tools/evenpace.py --wps 3.1
import argparse, json, re, shutil, subprocess, wave, numpy as np
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument('--wps', type=float, default=3.1); ap.add_argument('--min', type=float, default=0.92); ap.add_argument('--max', type=float, default=1.25); ap.add_argument('--cap', nargs='*', default=[], help='per-line max tempo, e.g. l1=1.05 (a hook that sounds rushed)')
a = ap.parse_args(); SR = 44100
if not Path('timing_raw_uneven.json').exists(): shutil.copy('timing_raw.json', 'timing_raw_uneven.json'); shutil.copy('voice_raw.mp3', 'voice_raw_uneven.mp3')
T = json.load(open('timing_raw_uneven.json', encoding='utf-8')); L = T['lines']
dec = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout, '<i2').astype(np.float64) / 32768
x = dec('voice_raw_uneven.mp3')
# segment boundaries: middle of the silence between line i end and line i+1 start
b = [0.0] + [(L[i]['end'] + L[i + 1]['start']) / 2 for i in range(len(L) - 1)] + [len(x) / SR]
out, t_new = [], 0.0; maps = []
for i, l in enumerate(L):
    s0, s1 = b[i], b[i + 1]; seg = x[int(s0 * SR):int(s1 * SR)]
    spoken = sum(3 if re.fullmatch(r'\d{4}', re.sub(r'\D', '', w['w'])) else 1 for w in l['words'])   # a year is read as ~3 words ('two thousand six')
    rate = spoken / max(0.3, l['end'] - l['start']); cap = dict((k, float(v)) for k, v in (c.split('=') for c in a.cap)); f = min(cap.get(l['id'], a.max), max(a.min, a.wps / rate))
    # stretch only the speech part [start, end]; keep the lead-in/lead-out silence of the segment as is
    a0, a1 = l['start'] - s0, l['end'] - s0; pre, sp, post = seg[:int(a0 * SR)], seg[int(a0 * SR):int(a1 * SR)], seg[int(a1 * SR):]
    with wave.open('_seg.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(sp, -1, 1) * 32767).astype('<i2').tobytes())
    sp2 = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', '_seg.wav', '-af', f'atempo={f:.4f}', '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout, '<i2').astype(np.float64) / 32768
    maps.append((s0, l['start'], l['end'], t_new + len(pre) / SR, f)); out += [pre, sp2, post]; t_new += (len(pre) + len(sp2) + len(post)) / SR
    print(f"{l['id']}: {rate:.2f} -> {rate * f:.2f} w/s (x{f:.3f})")
Path('_seg.wav').unlink(missing_ok=True); y = np.concatenate(out)
for (s0, st, en, nst, f), l in zip(maps, L):
    for w in l['words']: w['t'] = round(nst + (w['t'] - st) / f, 3); w['e'] = round(nst + (w['e'] - st) / f, 3)
    l['start'], l['end'] = l['words'][0]['t'], l['words'][-1]['e']
T['duration'] = round(len(y) / SR, 3)
with wave.open('voice_even.wav', 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'voice_even.wav', '-c:a', 'libmp3lame', '-q:a', '2', 'voice_raw.mp3'], check=True)
json.dump(T, open('timing_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1); print('duration', T['duration'])
