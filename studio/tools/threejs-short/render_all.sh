#!/usr/bin/env bash
# Render the picture in segments: one browser load per SET (the engine builds one set per load: office / home ...).
# EDIT per film: H0/H1 are the set-change cuts and must use the SAME formula as the film code (S.H0/S.H1) and audio/cues.py.
# A film with one set renders a single segment: t0=0, dur=END.
set -euo pipefail; cd "$(dirname "$0")"
read H0 H1 END < <(python - <<'PY'
import json, re
T = json.load(open('timing.json')); L = T['lines']; n = lambda s: re.sub(r'[^\w-]', '', s.lower())
fr = lambda x: round(x * 30) / 30
wt = lambda i, w: next(x['t'] for x in L[i - 1]['words'] if n(x['w']).startswith(w))
print(f"{fr(L[5]['start'] - 0.15):.4f} {fr(wt(7, 'worlds') - 0.1):.4f} {T['duration']}")
PY
)
echo "H0=$H0 H1=$H1 END=$END"
cd engine && python build.py && export PAGE=film.html
XQ="&viewer=1&film=1&t0=0&dur=$H0" node render.cjs out/seg1.mp4 1080 1920 30 > out/seg1.log 2>&1; grep -E "frames in" out/seg1.log
XQ="&viewer=1&film=1&set=home&t0=$H0&dur=$(python -c "print($H1-$H0)")" node render.cjs out/seg2.mp4 1080 1920 30 > out/seg2.log 2>&1; grep -E "frames in" out/seg2.log
XQ="&viewer=1&film=1&t0=$H1&dur=$(python -c "print($END-$H1)")" node render.cjs out/seg3.mp4 1080 1920 30 > out/seg3.log 2>&1; grep -E "frames in" out/seg3.log
