# Voice track: narrator take (el_full) with one quoted line replaced by a separate take in the SAME voice (an audio tag such as
# [sarcastic]) and a reaction beat after it. Writes ../voice_raw.mp3 + ../timing_raw.json for tighten → evenpace → fit → align.
# Generate the quote with a filler after it ('... open? [short pause] Okay.'): a take that ends on the quote came back truncated.
# Cut the quote from the waveform (onset, and where the tail dies), not from TTS timestamps: the first word after a tag was
# aligned 0.55 s late (clipped 'So') and the last word's tail ran past the file end. QT speeds a slow delivery (atempo, pitch kept).
import base64, json, subprocess, wave, numpy as np
from pathlib import Path
R = Path(__file__).resolve().parent; PROD = R.parent; SR = 44100; LEAD = 0.3; LAUGH = 1.1; QT = 1.25   # question: Ian (narrator voice) [sarcastic]; QT = question tempo (v11: it read slow)
S = json.loads((PROD / 'script.json').read_text(encoding='utf-8'))

def words_of(al):
    out, cur = [], None
    for c, a, b in zip(al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']):
        if c.isspace():
            if cur: out.append(cur); cur = None
            continue
        if cur is None: cur = {'w': '', 't': a, 'e': b}
        cur['w'] += c; cur['e'] = b
    if cur: out.append(cur)
    return [w for w in out if not (w['w'].startswith('[') or w['w'].endswith(']'))]   # drop v3 audio tags
def pcm(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(mp3), '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, '<i2').astype(np.float64) / 32768
nar = json.load(open(R / 'el_full.json', encoding='utf-8')); inv = json.load(open(R / 'el_investor.json', encoding='utf-8'))
NA, IA = pcm(R / 'el_full.mp3'), pcm(R / 'el_investor.mp3'); NW, IW = words_of(nar['alignment']), words_of(inv['alignment'])
iso = next(i for i, w in enumerate(NW) if w['w'].lower().startswith('so') and NW[i - 1]['w'].lower().startswith('asked'))
ije = next(i for i, w in enumerate(NW) if w['w'].lower().startswith('jensen'))
cutA, cutC = NW[iso]['t'] - 0.04, NW[ije]['t'] - 0.08
IW = IW[:next(i for i, w in enumerate(IW) if w['w'].endswith('?')) + 1]   # v12: the take has a filler word after the question so the last word is not truncated
_r = np.sqrt(np.convolve(IA ** 2, np.ones(441) / 441, 'same'))[::441]; _th = _r.max() * 10 ** (-45 / 20)   # 10 ms RMS
_j = next(j for j in range(int(IW[-1]['e'] * 100) - 10, len(_r) - 3) if (_r[j:j + 4] < _th).all())   # the question's tail has died away
_j0 = next(j for j in range(len(_r)) if _r[j] > _th * 10 ** (5 / 20))   # v12: speech onset from the waveform; the aligned 'So' started 0.55 s late and clipped it
IW[0] = dict(IW[0], t=_j0 / 100); i0, i1 = max(0, _j0 / 100 - 0.03), _j / 100 + 0.05; print('question tail ends', round(i1, 2), '(aligned end', round(IW[-1]['e'], 2), ')')
A, B, Cc = NA[:int(cutA * SR)], IA[int(i0 * SR):int(i1 * SR)], NA[int(cutC * SR):]
rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2)); B = B * (rms(A) / rms(B))   # match the character's loudness to the narrator
B[-int(0.08 * SR):] *= np.linspace(1, 0, int(0.08 * SR))   # fade the tail, no click
B = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={QT}', '-f', 's16le', '-'], input=(np.clip(B, -1, 1) * 32767).astype('<i2').tobytes(), capture_output=True, check=True).stdout, '<i2').astype(np.float64) / 32768
gapq = 0.12   # breath between "asked:" and the question
track = np.concatenate([np.zeros(int(LEAD * SR)), A, np.zeros(int(gapq * SR)), B, np.zeros(int(LAUGH * SR)), Cc, np.zeros(int(0.4 * SR))])
oB = LEAD + len(A) / SR + gapq; oC = oB + len(B) / SR + LAUGH
words = [dict(w, t=w['t'] + LEAD, e=w['e'] + LEAD) for w in NW[:iso]] + [dict(w, t=(w['t'] - i0) / QT + oB, e=(w['e'] - i0) / QT + oB, spk='investor') for w in IW] + [dict(w, t=w['t'] - cutC + oC, e=w['e'] - cutC + oC) for w in NW[ije:]]
lines, k = [], 0
for l in S['lines']:
    n = len(l['vo'].split()); ws = words[k:k + n]; k += n
    assert [w['w'].strip('.,?!:').lower() for w in ws] == [x.strip('.,?!:').lower() for x in l['vo'].split()], (l['id'], [w['w'] for w in ws])
    ws = [{**{'w': w['w'], 't': round(w['t'], 3), 'e': round(w['e'], 3)}, **({'spk': w['spk']} if 'spk' in w else {})} for w in ws]
    lines.append({'id': l['id'], 'text': l['vo'], 'start': ws[0]['t'], 'end': ws[-1]['e'], 'words': ws})
with wave.open(str(R / 'voice_v3.wav'), 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(track, -1, 1) * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', R / 'voice_v3.wav', '-c:a', 'libmp3lame', '-q:a', '2', PROD / 'voice_raw.mp3'], check=True)
json.dump({'voice': 'Ian uC1r2TVqMMkHyjSAteKk (narration + sarcastic question take)', 'duration': round(len(track) / SR, 3), 'lines': lines}, open(PROD / 'timing_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('duration', round(len(track) / SR, 2), '| question', round(oB, 2), '-', round(oB + len(B) / SR, 2), '| Jensen at', round(oC, 2))
