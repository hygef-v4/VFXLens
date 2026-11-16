# v3 underscore (procedural; ElevenLabs Music needs a paid API plan, the free MCP queue stayed busy): a warm, sparse bed
# that stays out of the voice's way — soft detuned pad chords + a felt-piano note per half bar, no plucky arpeggios.
# I-vi-IV-V in C at 90 BPM; drops to the pad only at night, stops for the dolly zoom, a slightly fuller last third.
import numpy as np, wave
from pathlib import Path
from cues import cues
SR = 48000; P = Path(__file__).resolve().parent
C = cues(); END = C['END']; N = int(END * SR) + SR
out = np.zeros((N, 2)); midi = lambda m: 440 * 2 ** ((m - 69) / 12)

def put(sig, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if j > i: out[i:j, 0] += sig[:j - i] * g * np.sqrt(0.5 * (1 - pan)); out[i:j, 1] += sig[:j - i] * g * np.sqrt(0.5 * (1 + pan))
def lp(x, a=0.08):   # one-pole low-pass: soft, felt-like
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s += a * (v - s); y[i] = s
    return y
def pad(notes, dur):
    t = np.arange(int(dur * SR)) / SR; env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    x = sum(np.sin(2 * np.pi * midi(m) * d * t + d) for m in notes for d in (0.997, 1.003)) / (2 * len(notes))
    return lp(x, 0.12) * env
def felt(m, dur=2.2):
    t = np.arange(int(dur * SR)) / SR; f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6) + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 9)
    return lp(x * np.exp(-t * 2.2) * np.minimum(1, t / 0.006), 0.25)
bar = 4 * 60 / 90; CH = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [55, 59, 62])]
MEL = [72, 67, 69, 64, 69, 65, 71, 67]
k = 0; t = 0.0
while t < END:
    root, tri = CH[k % 4]; stop = C['H1'] - 0.1 <= t < C['l8'] - 0.2; night = C['H0'] <= t < C['H1']; late = t >= C['l8']
    if not stop:
        put(pad([root + 12] + tri, bar + 0.8), t, 0.5 if not night else 0.35, pan=-0.15)
        if not night:
            put(felt(MEL[(2 * k) % 8]), t, 0.32, pan=0.2); put(felt(MEL[(2 * k + 1) % 8] - (0 if late else 12)), t + bar / 2, 0.26, pan=0.25)
            if late: put(felt(root, 1.6), t, 0.22)
    t += bar; k += 1
out = out[:int(END * SR)]; f = int(0.03 * SR); out[-f:] *= np.linspace(1, 0, f)[:, None]
out /= max(1e-6, np.abs(out).max()) / 0.8
with wave.open(str(P / 'music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
print('music.wav', round(END, 2), 's')
