# Shared cue times from ../timing.json. Keep these formulas identical to the film code's own S object
# (engine/film.inc.js): a mismatch moved a laugh cut off its word in the first production.
# Add one named cue per story beat, e.g. S['reveal'] = wt(3, 'reveal') - 0.05; set-change cuts go in SETS.
import json, re
from pathlib import Path
P = Path(__file__).resolve().parent.parent

def cues():
    T = json.load(open(P / 'timing.json', encoding='utf-8')); L = T['lines']
    n = lambda s: re.sub(r'[^\w-]', '', s.lower())
    def wt(i, w, k=0):   # start of the k-th word in line i (1-based) beginning with w; the line start if absent
        ws = [x['t'] for x in L[i - 1]['words'] if n(x['w']).startswith(w)]
        return ws[k] if len(ws) > k else L[i - 1]['start']
    S = {'END': T['duration']}
    for i, l in enumerate(L, 1): S[f'l{i}'] = l['start'] - 0.1   # cut 0.1 s before each line
    S['SETS'] = [('office', 0.0, T['duration'])]   # (set, start, end) per browser load; render_fast.sh renders one segment each
    return S

if __name__ == '__main__':
    for k, v in cues().items(): print(f'{k:>8} {v}')
