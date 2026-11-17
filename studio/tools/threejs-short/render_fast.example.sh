#!/usr/bin/env bash
# Faster full pipeline: picture segments in parallel (one browser each), Remotion at --concurrency $RC (default 3) with
# a bounded video cache, automatic fallback to 1 thread on out-of-memory, then loudnorm + limiter, verify and audit.
# Usage: SEGS="2" RC=3 OUTV=v2 [SEQ=1] bash render_fast.sh   (SEGS = segments to (re)render, " " = none; SEQ=1 = one browser at a time when memory is short)
# AUDIO_ONLY=1: stop after the manifest and write the normalized full mix to audio-preview/ for a listening sign-off.
# Segments come from cues SETS in audio/cues.py: one (set, start, end) per browser load, frame-rounded.
set -uo pipefail; cd "$(dirname "$0")"
RC=${RC:-3}
mapfile -t SEGDEF < <(cd audio && python -c "
from cues import cues
fr = lambda x: round(x * 30) / 30
for i, (st, a, b) in enumerate(cues()['SETS'], 1): print(i, st, f'{fr(a):.4f}', f'{fr(b) - fr(a):.4f}')")
SEGS=${SEGS:-$(seq -s ' ' 1 ${#SEGDEF[@]})}
echo "segments: ${#SEGDEF[@]} (rendering [$SEGS]) remotion concurrency=$RC"
(cd engine && python build.py >/dev/null); export PAGE=film.html
seg() { read -r n st t0 dur <<< "${SEGDEF[$(($1 - 1))]}"
  (cd engine && XQ="&viewer=1&film=1&set=$st&t0=$t0&dur=$dur" node render.cjs out/seg$n.mp4 1080 1920 30 > out/seg$n.log 2>&1; grep -E "frames in" out/seg$n.log) }
for s in $SEGS; do rm -f engine/out/seg$s.mp4; if [ -n "${SEQ:-}" ]; then seg $s; else seg $s & fi; done; wait   # SEQ=1: one browser at a time when memory is short
for i in $(seq 1 ${#SEGDEF[@]}); do [ -s engine/out/seg$i.mp4 ] || { echo "SEG$i MISSING"; exit 1; }; done
python audio/build_manifest.py > audio/manifest.log || { tail -5 audio/manifest.log; exit 1; }; tail -1 audio/manifest.log
SLUG=$(basename "$PWD")
if [ -n "${AUDIO_ONLY:-}" ]; then mkdir -p audio-preview; (cd ../../../studio && npx remotion render src/index.ts ThreeShort ../local/productions/$SLUG/audio-preview/mix_full.wav --codec=wav --concurrency=$RC --props="{\"manifestFile\":\"media/$SLUG/manifest.json\"}" --log=error)
  A=audio-preview/mix_full.wav; M=$(ffmpeg -hide_banner -i $A -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python -c "import sys,re,json; d=json.loads(re.findall(r'\{[^{}]*\}', sys.stdin.read())[-1]); print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
  ffmpeg -v error -y -i $A -af "loudnorm=I=-14:TP=-1.5:LRA=11:$M:linear=true,alimiter=limit=0.82:level=false" -c:a libmp3lame -b:a 256k audio-preview/$SLUG-audio.mp3 && echo "listen: audio-preview/$SLUG-audio.mp3"; exit 0; fi
cd ../../../studio; P=../local/productions/$SLUG; rm -f $P/remotion-raw.mp4
rr() { npx remotion render src/index.ts ThreeShort "$@" --concurrency=$C --offthreadvideo-cache-size-in-bytes=268435456 --log=error 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -vE "^\s+at " | tail -2; }
C=$RC; rr $P/remotion-raw.mp4 --codec=h264 --crf=18 --props="{\"manifestFile\":\"media/$SLUG/manifest.json\"}"
if [ ! -s $P/remotion-raw.mp4 ]; then echo "retrying Remotion with 1 thread"; C=1; rr $P/remotion-raw.mp4 --codec=h264 --crf=18 --props="{\"manifestFile\":\"media/$SLUG/manifest.json\"}"; fi
[ -s $P/remotion-raw.mp4 ] || { echo "REMOTION FAILED"; exit 1; }
C=$RC; rr $P/qa/${OUTV:-v1}_sfx.wav --codec=wav --props="{\"manifestFile\":\"media/$SLUG/manifest.json\",\"music\":false,\"musicDb\":0,\"voiceDb\":-60,\"sfxDb\":0,\"ambienceDb\":-60}"
cd $P
M=$(ffmpeg -hide_banner -i remotion-raw.mp4 -vn -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | python -c "
import sys,re,json; d=json.loads(re.findall(r'\{[^{}]*\}', sys.stdin.read())[-1]); print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -v error -y -i remotion-raw.mp4 -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11:$M:linear=true,alimiter=limit=0.82:level=false,aresample=48000" -c:a aac -b:a 192k -movflags +faststart $SLUG-${OUTV:-v1}.mp4
[ -s $SLUG-${OUTV:-v1}.mp4 ] || { echo "LOUDNORM FAILED"; exit 1; }
NF=$(python -c "import json;print(json.load(open('../../../studio/public/media/$SLUG/manifest.json'))['durationInFrames'])")
python ../../../.agents/skills/remotion-3d-director/scripts/verify_render.py $SLUG-${OUTV:-v1}.mp4 --width 1080 --height 1920 --fps 30 --frames $NF --audio required | python -c "import json,sys;d=json.load(sys.stdin);print('verify',d['ok'],d['errors'],d.get('observed',{}).get('frames'))"
ffmpeg -v info -i $SLUG-${OUTV:-v1}.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):" | tail -2
echo "black: $(ffmpeg -v info -i $SLUG-${OUTV:-v1}.mp4 -vf blackdetect=d=0.03:pix_th=0.05 -an -f null - 2>&1 | grep -o 'black_start:[0-9.]*' | tr '\n' ' ')"
python qa/audit.py $SLUG-${OUTV:-v1}.mp4 --timing timing.json --manifest ../../../studio/public/media/$SLUG/manifest.json --sfx-stem qa/${OUTV:-v1}_sfx.wav --voice voice.wav
