# Shared cue times, computed from ../timing.json with the same formulas as the film code (engine/film_cuda.inc.js, object S).
import json, re
from pathlib import Path
P = Path(__file__).resolve().parent.parent

def cues():
    T = json.load(open(P / 'timing.json', encoding='utf-8')); L = T['lines']
    n = lambda s: re.sub(r'[^\w-]', '', s.lower()); fr = lambda x: round(x * 30) / 30
    def wt(i, w, k=0):
        ws = [x['t'] for x in L[i - 1]['words'] if n(x['w']).startswith(w)]
        return ws[k] if len(ws) > k else L[i - 1]['start']
    ls = lambda i: L[i - 1]['start']
    S = dict(END=T['duration'], nob=wt(2, 'nobody') - 0.08, cuda=wt(2, 'cuda'), math=wt(2, 'math'), l3=ls(3) - 0.1, inv=wt(3, 'investors') - 0.06,
             fifty=wt(3, 'fifty'), so=wt(3, 'so'), calc=wt(3, 'calculator'), l4=ls(4) - 0.1, keep=wt(4, 'keep'), l5=ls(5) - 0.1, lapse=wt(5, 'outside') + 0.4,
             H0=fr(ls(6) - 0.15), H1=fr(wt(7, 'worlds') - 0.1), y2012=wt(6, '2012'), stu=wt(6, 'student') + 0.3, two=wt(6, 'two') - 0.05, bed=wt(6, 'in', 2) - 0.05,
             l7=ls(7) - 0.06, crush=wt(7, 'every') - 0.05, crushed=wt(7, 'crushed'), l8=ls(8) - 0.08, normal=wt(8, 'normal'), four=wt(8, 'four'), that=wt(8, 'that') - 0.1,
             card8=wt(8, 'card'), five=wt(8, 'five'), l9=ls(9) - 0.1, like=wt(9, 'like'), beat=wt(9, 'beat'), l10=ls(10) - 0.1, all=wt(10, 'all') - 0.06)
    S['ins'] = S['math'] - 0.12
    S['qend'] = wt(3, 'open') + 0.45
    return S

if __name__ == '__main__':
    for k, v in cues().items(): print(f'{k:>8} {v:7.3f}')
