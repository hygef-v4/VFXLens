# three.js character short (story Short, 9:16)

The pipeline used for the first full production of this kind (a ~50 s story Short about Nvidia's CUDA bet,
November 2026). Use it for a vertical story Short with 3D cartoon characters, a voice-over, word captions,
SFX, ambience and music. It extends [create-video](create-video.md): keep its production checkpoint,
privacy and delivery rules. Tools live in [`studio/tools/threejs-short/`](../studio/tools/threejs-short/README.md).

| Layer | Owner |
| --- | --- |
| Story, script | `claude-3d-animated-shorts` story formula, [Content Writing](../library/content-writing/README.md), `humanizer` skill for the read-aloud pass |
| Direction (shots, camera, light, QA) | [`remotion-3d-director`](../.agents/skills/remotion-3d-director/SKILL.md) |
| Characters, sets, 3D picture | `claude-3d-animated-shorts` engine (three.js), copied per production |
| Voice, SFX, music | ElevenLabs (CLI for anything that needs timestamps or files; MCP for browsing voices) |
| Sound design rules | `video-shotcraft` `references/sound-design.md` (peak alignment, layering, ducking) |
| Captions, cards, overlays, audio mix, export | Remotion: `ThreeShort` composition (`studio/src/shorts/ShortAssembly.tsx`) |

Skills to have installed (global): `claude-3d-animated-shorts` (with `npm install` + `scripts/fetch-assets.sh` in it),
`remotion-3d-director` (project), `vfxlens` (project), `text-to-speech`, `sound-effects`, `music`,
`speech-to-text` (ElevenLabs), `video-shotcraft`, `humanizer`. ElevenLabs: Starter or higher for the Music API
and commercial use; the free plan returns HTTP 402 for music and gives no commercial licence.

## 1. Start the production

```powershell
python studio/tools/threejs-short/scaffold.py <slug>
```

Write the contract in `local/productions/<slug>/production.md`: audience, 1080×1920 at 30 fps, length target,
language, platform, sources, licence of every asset library you will use, and `VFX_RESOURCES` (your local
overlay/SFX library). Label every choice that is not a measured fact as a creative decision.

## 2. Story and script

1. Pick one surprising true story with a physical cause and effect. Verify each claim; record the source and
   its level (own recollection vs. audited data) in a fact-check table.
2. Write 8–10 lines with the formula: an odd act stated as fact in line 1, context, a doubter's quip, the hero's
   short stubborn reply, time passing, the turn, the science with one real number and one everyday analogy, and a
   last line cut mid-sentence so the Short loops into line 1. About 140 words for ~50 s.
3. Run `humanizer` on the narration, then read it aloud. Quotes from real people must be real; label paraphrases
   ("investors basically asked") in the fact-check.
4. Save `script.json` (`{"voice": ..., "lines": [{"id": "l1", "vo": "..."}]}`). One line per narrative beat:
   the film code addresses lines by index and words by their first letters.

## 3. Voice and timing

```powershell
python voice/tts_eleven.py <voice_id> eleven_v3      # whole script in one take: voice_raw.mp3 + timing_raw.json
python voice/fit.py --target 53 --max 1.15 --gap 0.35  # voice.wav + timing.json
copy timing.json engine\film\timing.json
```

- Choose the voice with the ElevenLabs MCP `creative_list_voices` (narrative/social, accent, gender). Keep one
  timbre for the whole film. A quoted line can be a separate take with an audio tag such as `[sarcastic]` in
  the **same voice** (a different voice for one line sounded out of place), spliced with a reaction pause:
  see `examples/voice_quote_splice.example.py`.
- The CLI drops everything after a newline in `--text`: join lines with spaces. The script caches the take in
  `voice/el_full.json`; delete it only when you want (and pay for) a new take.
- Check the fit: no audio fragment shorter than ~0.15 s right after the inserted pause, and each line's timing
  start within ~0.3 s of the audible onset.

## 4. Picture: cast, sets, shots (three.js)

Write the film in `engine/film.inc.js`, starting from the example. Rebuild with `python engine/build.py`.

- **Cast**: `SR.build({...base, jacket, details, pattern, hat})`. Same head size for everyone; identity comes
  from clothes and hats. Review the cast before shots (the skill's `viewer.html`; skipping this caused
  late fixes).
- **Sets**: one set per browser load (`&set=office|home`). A 9:16 frame holds about two desks: pull clusters
  together (2.1 m apart) instead of widening the lens. Build any prop whose screen or pose matters (laptop,
  GPU card, desk) from boxes so its geometry is known.
- **Shots**: one `if (t < S.next)` branch per shot, 2–3.5 s each, cut on words (`WT(line, 'word')`). Every shot
  moves. Camera curve `cm()` starts already moving and settles (ease-in-out at every cut reads as stop-start).
  Gestures, bubbles and pops use `spr()` (spring with overshoot); heads get secondary motion (`alive()`).
- **Light and look**: grade around exposure 0.43, saturation 1.4, contrast 1.17, vignette 0.4; a key and a rim
  light follow every shot (`lightRig`); shadow-camera size per shot (3–9 m) for crisp contact shadows.
  Lens: depth of field on every shot (default focus on the look target), rack focus on two-shots,
  `uCA` 0.035, `uDist` 0.06, `uGrain` 0.045.
- **Loop**: the first and last frame use the same camera on the same subject.
- Stills (from `engine/`): `PAGE=film.html XQ="&viewer=1&film=1[&set=home]" node render.cjs out/s/x.mp4 540 960 30 <seconds...>`;
  then, from the production folder, `python qa/grid.py engine/out/s engine/out/s/grid.jpg` and `python qa/luma.py engine/out/s`.
  Target luma 100–135 (dark screens and night shots may sit lower by design); heads are the brightest thing.
- Full picture: `bash render_all.sh` (one segment per set; set-change cuts computed like `S.H0/S.H1`).

## 5. Sound

1. **Music**: ElevenLabs Music (CLI `music compose --json '{"prompt": ..., "music_length_ms": ..., "force_instrumental": true}'`;
   the CLI validator rejects `--prompt` alone). Brief: understated, sparse, low energy under narration.
2. **SFX and ambience**: ElevenLabs `text-to-sound-effects` for specific actions (typing, laughter, ding,
   paper swipes, fans, room tone), plus licensed library files. Only sounds with a visible cause; no whoosh on
   ordinary cuts. Transitions: a paper swipe on each major cut, a film burn on act changes.
3. **Peak alignment** (the main cause of "sound not matching the picture"): place each file so its RMS peak (hits)
   or onset (textures) lands on the target frame: `from = target − lag`. `build_manifest.py` measures the lag.
4. **Levels**: voice 0 dB; music −23 dB, −33 dB while anyone speaks (per-frame volume); ambience −31 to −37 dB;
   SFX −11 to −26 dB. Loudness at the end: −14 LUFS, true peak −1.5 dBTP.

## 6. Assemble in Remotion

```powershell
python audio/build_manifest.py   # writes studio/public/media/<slug>/manifest.json and copies media (ignored folder)
cd studio
npx remotion render src/index.ts ThreeShort ../local/productions/<slug>/remotion-raw.mp4 --props="{\"manifestFile\":\"media/<slug>/manifest.json\"}" --codec=h264 --crf=18 --concurrency=4
```

Then a two-pass loudnorm on the audio only (`-c:v copy`). Captions are one word at a time with a spring pop and
keyword colours; cards only for what the voice does not say (a year, a ticker). Overlays (light leaks, film
burns) use `mix-blend-mode: screen` in the browser. The picture must be re-encoded with a short GOP: a
stream-copied concat made Remotion time out while seeking. Open `npm run studio` to adjust layers by name.

## 7. QA before upload

- `verify_render.py` (`.agents/skills/remotion-3d-director/scripts/`): dimensions, fps, exact frame count, audio stream.
- `ffmpeg -vf blackdetect`: no black frames (a camera inside a head and a GPU out-of-memory both produced them).
- Loudness `ebur128`: −14 LUFS ±0.5, peak ≤ −1 dBFS.
- Contact sheet of every shot from the encoded file (colours, captions clear of faces and screens, loop frame).
- ElevenLabs Scribe on the final mix: the transcript matches the script; quoted lines and reaction beats land where planned.
- Listen on a phone before upload. Record what was and was not checked in `production.md`.

## Pitfalls met in the first production

| Symptom | Cause | Fix |
| --- | --- | --- |
| Render hangs at the same early frames | shaders compiled mid-render | warm-up frames before frame 0 (`render.cjs`) |
| All frames black after a point | GPU out of memory, context lost | relaunch and redo the frame; recycle the browser |
| Purple cast | screen blend done in YUV by ffmpeg | blend in RGB, or in the browser (Remotion) |
| Black insert shot | camera inside a character's head | hide off-camera characters; check stills at shot starts |
| Laugh before the question ends | cut placed on a word inside the question | hold the shot to the end of the line (`e` of the last word) |
| Stutter before the last line; captions early | `fit.py` cut inside a word; timing shifted by the lead silence | fixed `fit.py` |
| Code silently disabled | a `//` comment inserted mid-line swallowed `}` | use `/* */` for inline notes; syntax-check the built file |
| Sound late against the picture | files placed by their start, peaks 0.3–0.8 s later | peak alignment |
| Background louder than the voice | static music level | per-frame ducking, lower beds |

[Back to create-video](create-video.md)
