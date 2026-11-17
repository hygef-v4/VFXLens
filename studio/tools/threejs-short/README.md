# three.js character-short toolkit

Reusable pieces for the [three.js character short workflow](../../../workflows/threejs-character-short.md):
a three.js engine renders the picture (from the `claude-3d-animated-shorts` skill), ElevenLabs makes the voice,
SFX and music, and Remotion (`studio/src/shorts/ShortAssembly.tsx`) assembles captions, overlays and audio.

| Path | What it is |
| --- | --- |
| `scaffold.py` | Creates `local/productions/<slug>/` with the engine copied from the skill, the fixes below applied, the `film` hook added, and the scripts copied in |
| `engine/render.cjs` | Resilient Puppeteer → ffmpeg renderer: shader warm-up before frame 0, 60 s cap per frame, browser relaunch on hang/OOM/lost context/blank frame, recycle every 300 frames, drained ffmpeg stderr |
| `engine/post.js` | The skill's post chain plus lens uniforms: `uCA` (edge chromatic aberration), `uDist` (barrel distortion), `uGrain` |
| `voice/tts_eleven.py` | Whole-script ElevenLabs TTS with character timestamps → `voice_raw.mp3` + `timing_raw.json`. Caches the take so reruns are free |
| `voice/fit.py` | Tempo fit (≤ ×1.3) + pause before the last line → `voice.wav` + `timing.json`. **Fixed**: the original cut inside the last word of the previous line and placed every word 0.26 s early |
| `voice/tighten.py` | Optional waveform-silence shrink before fit; keeps the original generated take as `*_loose.*`, preserves named reaction beats with `--keep-after-line l3` |
| `voice/evenpace.py` | Per-line atempo toward one spoken-words/s target (a year counts as ~3 words); `--cap l1=1.12` limits a line that would sound rushed. Keeps `*_uneven.*` |
| `voice/silent_timing.py` | Draft `timing.json` and a silent `voice.wav` from `script.json` at a fixed pace: block shots and render a captions-only cut before any TTS |
| `voice/align.py` | ElevenLabs forced alignment on the final `voice.wav` → true word times in `timing.json` (TTS starts are ~0.13 s early). Keeps `timing_tts.json` |
| `audio/cues.example.py` | One place for event times derived from word timings, using the same formulas as the film code |
| `audio/build_manifest.example.py` | Writes `studio/public/media/<slug>/manifest.json` and copies media: picture, leaks/film burns (pre-cut to 9:16), voice, ducked music volumes, ambience beds, peak-aligned SFX, captions, cards |
| `audio/music_fallback.py` | Procedural underscore, only when ElevenLabs Music is unavailable (free plan returns 402) |
| `qa/luma.py`, `qa/grid.py` | Luma/saturation per still (target 100–135) and labelled contact sheets |
| `qa/audit.py` | Perceptual gates on the final file: stop/go jolts at cuts, static shots, spoken-pace spread, SFX masked by the voice |
| `render_fast.example.sh` → `render_fast.sh` | Whole pipeline: segments (parallel, or `SEQ=1` when memory is short), manifest, Remotion (`RC` threads, 256 MB video cache, falls back to 1), loudnorm + limiter, verify, audit. `AUDIO_ONLY=1 SEGS=" "` writes a normalized full mix to `audio-preview/` for a listening sign-off (needs rendered segments) |
| `examples/starter.film.inc.js` | Minimal film the scaffold starts from: one presenter, one moving shot per narration line, the frame contract. Replace cast, props and shots with your story |
| `examples/voice_quote_splice.example.py` | Replacing one quoted line with a separate take in the same voice plus a reaction pause; cuts from the waveform, filler word after the quote, optional tempo `QT` |

Requirements: the skill installed with `npm install` and `bash scripts/fetch-assets.sh` run in its folder;
Chrome; ffmpeg; Python 3 with numpy and Pillow; the ElevenLabs CLI (`npm i -g @elevenlabs/cli`, `elevenlabs auth login`).
Set `VFX_RESOURCES` to your local editing library (overlays, SFX) and record that path in the production's `production.md`.

The film hook, if `scaffold.py` reports that `main.js` changed upstream: in the copied `main.js`, make the viewer branch
also wait when `film` is in the query (`if (Q.has('skit') || Q.has('film')) window.ready = false;`) and replace
`if (!Q.has('skit')) loop(); else {` with `if (Q.has('film')) {` + a `// @@FILM@@` line + `} else if (!Q.has('skit')) loop(); else {`.

Diegetic props: put dates, prices, counters and leaderboards in the 3D scene, inspect their canvas text bounds, then set
`cards: []` and `captionY: 0.70`. Keep digits in front of tilted boards, insert cameras clear of monitors, and show each prop only
inside its own shot window (a board left visible flashed into another shot for 1–2 frames). The assembly accepts optional
`irises: [{from, mid, to, cx, cy}]` for an iris close/open; cut on words with continuous camera motion instead of 2D whips
(the v8 audit found a smear over a still 3D camera reads as a jump). Music bed: −10/−5 LU below speech (v7) or the quieter −14/−7 LU (v5). SFX auto-gain floor: voice RMS − 5 dB.
Run `node --test studio/tools/threejs-short/qa/transitions.test.mjs` from the repo root for transition boundary checks.
