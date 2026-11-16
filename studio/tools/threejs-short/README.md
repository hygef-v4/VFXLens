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
| `audio/cues.example.py` | One place for event times derived from word timings, using the same formulas as the film code |
| `audio/build_manifest.example.py` | Writes `studio/public/media/<slug>/manifest.json` and copies media: picture, leaks/film burns (pre-cut to 9:16), voice, ducked music volumes, ambience beds, peak-aligned SFX, captions, cards |
| `audio/music_fallback.py` | Procedural underscore, only when ElevenLabs Music is unavailable (free plan returns 402) |
| `qa/luma.py`, `qa/grid.py` | Luma/saturation per still (target 100–135) and labelled contact sheets |
| `render_all.sh` | Renders the picture in segments, one per set; edit the set-change cuts per film |
| `examples/film_nvidia_cuda.example.inc.js` | The worked film: cast, props, lighting rig, spring/camera curves, every shot. Start a new film from it |
| `examples/voice_quote_splice.example.py` | Replacing one quoted line with a separately generated take (another delivery) plus a reaction pause |

Requirements: the skill installed with `npm install` and `bash scripts/fetch-assets.sh` run in its folder;
Chrome; ffmpeg; Python 3 with numpy and Pillow; the ElevenLabs CLI (`npm i -g @elevenlabs/cli`, `elevenlabs auth login`).
Set `VFX_RESOURCES` to your local editing library (overlays, SFX) and record that path in the production's `production.md`.

The film hook, if `scaffold.py` reports that `main.js` changed upstream: in the copied `main.js`, make the viewer branch
also wait when `film` is in the query (`if (Q.has('skit') || Q.has('film')) window.ready = false;`) and replace
`if (!Q.has('skit')) loop(); else {` with `if (Q.has('film')) {` + a `// @@FILM@@` line + `} else if (!Q.has('skit')) loop(); else {`.
