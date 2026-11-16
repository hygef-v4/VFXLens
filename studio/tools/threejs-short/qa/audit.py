# Perceptual QA gates for a three.js short (from the v7 audit: stop-start cuts, uneven shots, masked SFX).
# python audit.py <final.mp4> --timing timing.json [--manifest .../manifest.json --sfx-stem sfx.wav --voice voice.wav]
# Make the SFX stem with an audio-only Remotion render: --codec=wav --props '{"manifestFile":...,"music":false,"voiceDb":-60,"sfxDb":0,"ambienceDb":-60}'
import argparse, json, re, subprocess, sys, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--timing', required=True); ap.add_argument('--manifest'); ap.add_argument('--sfx-stem'); ap.add_argument('--voice')
a = ap.parse_args(); fails = []
W, H = 90, 160
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.video, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32); N = len(x); d = np.r_[0, np.abs(np.diff(x, axis=0)).mean((1, 2))]
cuts = [0] + [i for i in range(2, N - 2) if d[i] > max(18, 3.5 * np.median(d[max(1, i - 8):i + 9])) and d[i] == d[i - 2:i + 3].max()]
sh = list(zip(cuts, cuts[1:] + [N])); dur = np.array([(b - c) / 30 for c, b in sh])
jolts = []
for c in cuts[1:]:
    bm, am = d[max(1, c - 5):c].mean(), d[c + 1:c + 6].mean()
    if (bm < 2.5 and am > 6) or (bm > 6 and am < 2.5): jolts.append((round(c / 30, 2), round(float(bm), 1), round(float(am), 1)))
static = [(round(c / 30, 2), round(float(du), 2)) for (c, b), du in zip(sh, dur) if du > 2.0 and d[c + 1:b].mean() < 1.5]
print(f'shots {len(sh)} | duration mean {dur.mean():.2f} sd {dur.std():.2f} min {dur.min():.2f} max {dur.max():.2f}')
print('stop/go jolts at cuts:', jolts or 'none'); print('static shots > 2 s:', static or 'none')
if len(jolts) > 2: fails.append(f'{len(jolts)} stop/go cuts')
if static: fails.append('static shots')
T = json.load(open(a.timing, encoding='utf-8')); r = [sum(3 if re.fullmatch(r'\d{4}', re.sub(r'\D', '', w['w'])) else 1 for w in l['words']) / (l['end'] - l['start']) for l in T['lines']]   # spoken words: a year ~3 (same rule as evenpace)
print('words/s per line: ' + ' '.join(f'{v:.2f}' for v in r) + f' | spread {max(r) - min(r):.2f}')
if max(r) - min(r) > 0.6: fails.append('uneven narration pace')
if a.manifest and a.sfx_stem and a.voice:
    pcm = lambda p: np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout, '<f4').astype(np.float64)
    s, v, SR = pcm(a.sfx_stem), pcm(a.voice), 16000; M = json.load(open(a.manifest, encoding='utf-8')); bad = []
    for e in M['sfx']:
        t0 = e['from'] / 30; t1 = t0 + (e['durationInFrames'] or 30) / 30; seg = s[int(t0 * SR):int(t1 * SR)]; w = 800; k = len(seg) // w
        if not k: continue
        pk = 20 * np.log10(np.sqrt((seg[:k * w].reshape(k, w) ** 2).mean(1)).max() + 1e-9); vs = v[int(t0 * SR):int(t1 * SR)]; vl = 20 * np.log10(np.sqrt((vs ** 2).mean()) + 1e-9) if len(vs) else -120
        if pk - vl < -6: bad.append((round(t0, 2), round(pk - vl, 1), e['note'][:40]))
    print(f"SFX under the voice by > 6 dB: {len(bad)}/{len(M['sfx'])}", bad or '')
    if bad: fails.append(f'{len(bad)} masked SFX')
print('RESULT:', 'PASS' if not fails else 'FAIL — ' + '; '.join(fails)); sys.exit(1 if fails else 0)
