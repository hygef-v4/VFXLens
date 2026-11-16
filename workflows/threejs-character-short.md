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
python voice/voice_quote_splice.py                   # optional: quoted line from a separate take in the same voice
python voice/tighten.py --maxgap 0.2 --keep-after-line l3  # shrink silences, keep the reaction beat
python voice/evenpace.py --wps 3.2 --cap l1=1.12     # even spoken words/s per line; cap a hook that sounds rushed
python voice/fit.py --target 50 --max 1.0 --gap 0.3  # voice.wav + timing.json (--max 1.0: no global speed-up)
python voice/align.py                                # forced alignment: true word times (TTS starts are ~0.13 s early)
copy timing.json engine\film\timing.json
```

After rebuilding the voice, move `voice_raw_loose.*`, `timing_raw_loose.json`, `voice_raw_uneven.mp3` and
`timing_raw_uneven.json` into a version folder: `tighten.py` and `evenpace.py` re-derive from those backups and would
silently ignore the new take. Then listen before rendering the picture: `AUDIO_ONLY=1 SEGS=" " bash render_fast.sh`
writes `audio-preview/<slug>-audio.mp3` (full mix at −14 LUFS; needs rendered segments from any version). In the first
production the user caught a clipped word, a swallowed "So" and a rushed hook by ear in this file; the meters had passed all three.

- Choose the voice with the ElevenLabs MCP `creative_list_voices` (narrative/social, accent, gender). Keep one
  timbre for the whole film. A quoted line can be a separate take with an audio tag such as `[sarcastic]` in
  the **same voice** (a different voice for one line sounded out of place), spliced with a reaction pause:
  see `examples/voice_quote_splice.example.py`. Generate the quote with a filler after it
  (`... open? [short pause] Okay.`): a take that ended on the quote came back truncated mid-word. Cut it from the
  waveform (speech onset; the point where the tail falls below −45 dB), not from TTS timestamps: the first word after a
  `[tag]` was stamped 0.55 s late. A slow delivery can be sped with `atempo` (`QT`, pitch kept) instead of a new take.
- Pace is measured in spoken words: "2006" is three. Hold the line spread under 0.6 words/s (`qa/audit.py`).
- The CLI drops everything after a newline in `--text`: join lines with spaces. The script caches the take in
  `voice/el_full.json`; delete it only when you want (and pay for) a new take.
- Check the fit: no audio fragment shorter than ~0.15 s right after the inserted pause, and each line's timing
  start within ~0.3 s of the audible onset.
- `tighten.py` retains `voice_raw_loose.mp3` and `timing_raw_loose.json` and derives reruns from them.
  Use it on generated production voice; inspect the fitted result for clipped consonants before export.

## 4. Picture: cast, sets, shots (three.js)

Write the film in `engine/film.inc.js`, starting from the example. Rebuild with `python engine/build.py`.

- **Cast**: `SR.build({...base, jacket, details, pattern, hat})`. Same head size for everyone; identity comes
  from clothes and hats. Review the cast before shots (the skill's `viewer.html`; skipping this caused
  late fixes).
- **Sets**: one set per browser load (`&set=office|home`). A 9:16 frame holds about two desks: pull clusters
  together (2.1 m apart) instead of widening the lens. Build any prop whose screen or pose matters (laptop,
  GPU card, desk) from boxes so its geometry is known.
- **Shots**: one `if (t < S.next)` branch per shot, 2–3.5 s each, cut on words (`WT(line, 'word')`). Every shot
  moves. Camera curve `cm(u) = 0.75u + 0.25·eio(u)` keeps velocity through every cut (ease-in-out, or a settle to
  zero, read as stop-start). A shot that follows a busy one (flipping pages) enters fast: `u = 0.55b + 0.45(1 − (1 − b)²)`.
  Pans between faces take 0.8–0.9 s (0.22 s read as a jump). Over-the-shoulder pushes can pass through the near head:
  frame singles from beside the listener instead.
  Gestures, bubbles and pops use `spr()` (spring with overshoot); heads get secondary motion (`alive()`).
- **Light and look**: grade around exposure 0.43, saturation 1.4, contrast 1.17, vignette 0.4; a key and a rim
  light follow every shot (`lightRig`); shadow-camera size per shot (3–9 m) for crisp contact shadows.
  Lens: depth of field on every shot (default focus on the look target), rack focus on two-shots,
  `uCA` 0.035, `uDist` 0.06, `uGrain` 0.045. Bokeh aperture ×1.2 (creative choice for subject separation);
  screen inserts at ~1 m, not 0.5 m.
- **Particles** (creative choice): a few small additive motes (`motesTick`, 140–420 points, 0.012–0.02 m), bright
  only inside light (dust columns under ceiling lamps, around a desk lamp), hidden within ~1 m of the lens. Thousands of
  large motes read as a dust storm and as bokeh blobs in close-ups.
- **Loop**: the first and last frame use the same camera on the same subject.
- **Diegetic props**: put years, prices, counters and results on physical props or screens. Check canvas text
  bounds as well as camera framing. Place counter digits ahead of the tilted panel and keep monitors outside
  the insert camera's sightline. Show each prop only inside its own shot window. These are creative choices, not measured properties of a reference.
- Stills (from `engine/`): `PAGE=film.html XQ="&viewer=1&film=1[&set=home]" node render.cjs out/s/x.mp4 540 960 30 <seconds...>`;
  then, from the production folder, `python qa/grid.py engine/out/s engine/out/s/grid.jpg` and `python qa/luma.py engine/out/s`.
  Target luma 100–135 (dark screens and night shots may sit lower by design); heads are the brightest thing.
- Full picture and assembly: `OUTV=v1 RC=3 bash render_fast.sh` (segments in parallel; `SEQ=1 RC=2` when Windows
  commit memory is near its limit, which crashed three parallel browsers). `render_all.sh` renders the segments only.
- Hold the cut until a quoted line's last word has died away (word end + 0.2 s); reaction SFX start after the cut.

## 5. Sound

1. **Music**: ElevenLabs Music (CLI `music compose --json '{"prompt": ..., "music_length_ms": ..., "force_instrumental": true}'`;
   the CLI validator rejects `--prompt` alone). Brief: understated, sparse, low energy under narration.
2. **SFX and ambience**: ElevenLabs `text-to-sound-effects` for specific actions (typing, laughter, ding,
   paper swipes, fans, room tone), plus licensed library files. Only sounds with a visible cause; no whoosh on
   ordinary cuts. Transitions: a paper swipe on each major cut, a film burn on act changes. Fewer is better:
   52 SFX in 45 s read as spam (25–30 is enough), and the first seconds need room for the hook. `build_manifest`
   auto-gains each SFX to at least voice RMS − 5 dB at its moment (−2 dB sounded crowded); drop any that stays
   under (`qa/audit.py`).
3. **Peak alignment** (the main cause of "sound not matching the picture"): place each file so its RMS peak (hits)
   or onset (textures) lands on the target frame: `from = target − lag`. `build_manifest.py` measures the lag.
4. **Levels**: set the music from measured loudness, not fixed gains: v7 uses −10 LU under the voice while anyone speaks,
   −5 LU in pauses; v5's quieter −14/−7 LU remains an approved alternative (`build_manifest.py` measures both files). Fixed −23/−33 dB gains put a
   −18 LUFS track ~30 dB under the voice and the music disappeared. Ambience −31 to −37 dB; SFX −11 to −26 dB.
   Check the bed by rendering audio only with and without music (`--codec=wav --props='{"music":false,...}'`)
   and measuring the difference. Loudness at the end: −14 LUFS, true peak −1.5 dBTP.

## 6. Assemble in Remotion

```powershell
python audio/build_manifest.py   # writes studio/public/media/<slug>/manifest.json and copies media (ignored folder)
cd studio
npx remotion render src/index.ts ThreeShort ../local/productions/<slug>/remotion-raw.mp4 --props="{\"manifestFile\":\"media/<slug>/manifest.json\"}" --codec=h264 --crf=18 --concurrency=4
```

Then a two-pass loudnorm on the audio only (`-c:v copy`) with a limiter at 0.82 (AAC pushed a 0.89 limit to −0.9 dBTP). Captions are one word at a time with a spring pop and
keyword colours; cards only for what the voice does not say (a year, a ticker). Overlays (light leaks, film
burns) use `mix-blend-mode: screen` in the browser. The picture must be re-encoded with a short GOP: a
stream-copied concat made Remotion time out while seeking. Open `npm run studio` to adjust layers by name. The Props panel has `musicDb`, `voiceDb`, `sfxDb` and `ambienceDb` trims (dB on top of the manifest levels): drag, listen, then render from the Studio or pass them in `--props`. A Studio render is not loudness-normalized; run the two-pass loudnorm on it before upload.

## 7. QA before upload

Optional manifest transitions (frame numbers, normalized `cx`/`cy`):
`irises: [{from, mid, to, cx, cy}]` closes the picture and captions to black at `mid`, then opens the incoming shot.
Require `from < mid < to`; align `mid` with the picture cut and the iris SFX peak near the close.
`whips: [{at, dir: 1}]` (or `-1`) adds translation and horizontal SVG blur within ±3 frames of the cut.
Avoid it over a still 3D camera: the v7 audit found 2D smears read as jumps; v8 uses `whips: []` and hard cuts on words. Older manifests can omit both arrays.
For diegetic text use `cards: []`; v7 places captions at `captionY: 0.70`. Check transitions on encoded frames,
including the intentionally black iris midpoint, rather than suppressing all black-frame warnings.

- `verify_render.py` (`.agents/skills/remotion-3d-director/scripts/`): dimensions, fps, exact frame count, audio stream.
- `ffmpeg -vf blackdetect`: no black frames (a camera inside a head and a GPU out-of-memory both produced them).
- Loudness `ebur128`: −14 LUFS ±0.5, peak ≤ −1 dBFS.
- Contact sheet of every shot from the encoded file (colours, captions clear of faces and screens, loop frame).
- ElevenLabs Scribe on the final mix: the transcript matches the script; quoted lines and reaction beats land where planned.
- `qa/audit.py <final.mp4> --timing timing.json --manifest … --sfx-stem sfx.wav --voice voice.wav`: stop/go jolts at cuts
  (≤ 2), no static shot > 2 s, words/s spread ≤ 0.6, no SFX more than 6 dB under the voice at its moment.
- Listen on a phone before upload. Record what was and was not checked in `production.md`.

## Pitfalls met in the first production

| Symptom | Cause | Fix |
| --- | --- | --- |
| Render hangs at the same early frames | shaders compiled mid-render | warm-up frames before frame 0 (`render.cjs`) |
| All frames black after a point | GPU out of memory, context lost | relaunch and redo the frame; recycle the browser |
| Purple cast | screen blend done in YUV by ffmpeg | blend in RGB, or in the browser (Remotion) |
| Black insert shot | camera inside a character's head | hide off-camera characters; check stills at shot starts |
| Laugh before the question ends | cut placed on a word inside the question | hold the shot to the end of the line (`e` of the last word + 0.2 s) |
| Quote's last word cut off even with a late cut | the ElevenLabs take itself ended mid-word (file shorter than its own timestamps) | filler word after the quote; cut where the waveform tail dies |
| First word of a spliced quote barely audible | TTS stamped it 0.55 s late after an audio tag; the splice started there | start the splice at the waveform onset |
| Stutter before the last line; captions early | `fit.py` cut inside a word; timing shifted by the lead silence | fixed `fit.py` |
| Code silently disabled | a `//` comment inserted mid-line swallowed `}` | use `/* */` for inline notes; syntax-check the built file |
| Sound late against the picture | files placed by their start, peaks 0.3–0.8 s later | peak alignment |
| Peak-aligned hit never sounds on cue | duration cap ends before the source peak | trim excess source lead, recalculate effective lag; retain source lag in the manifest |
| Laugh spills into the hero's reply | old fixed offset and a long laugh take survived a faster voice fit | use the measured final word end, shorten/fade the laugh into the actual pause, retime pan and bubbles together |
| Whip reverses one frame before the cut | nearest-frame rounding vs engine `t >= cue` | use `ceil(cue * fps)` for both whip center and swish target |
| Background louder than the voice | static music level | per-frame ducking, lower beds |
| No music audible on a phone | music ducked to −33 dB under near-continuous speech | music relative to measured voice loudness (−14 LU chosen by ear), `musicDb` trim in Studio |
| Cuts feel broken, "camera stops then lunges" | shot curve eased to zero velocity at both ends | `cm(u) = 0.75u + 0.25·eio(u)`: keep velocity through the cut |
| Pace "slow then fast" | per-line words/s spread 1.0 after silence shrinking | `voice/evenpace.py` (atempo per line, clamp 0.92–1.25) |
| SFX "missing" though placed | 13/52 SFX > 8 dB under the voice | fewer SFX; manifest auto-gain to voice RMS − 2 dB; peak-normalize/compress quiet sources |
| Remotion render: Chrome out of memory | high concurrency + big offthread video cache | `--offthreadvideo-cache-size-in-bytes=268435456`, concurrency 3, fallback to 1 (`render_fast.sh`) |
| Captions pop before the word | TTS timestamps include the lead silence; a hard-coded onset went stale after a refit | `voice/align.py` after `fit.py`; never hard-code word times |
| Particles read as dust storm / bokeh blobs | many large motes in the whole room, some in front of the lens | few small motes, brightness from light-shaft distance, hide motes < 1 m from the camera |
| Last word of a spliced quote clipped / laugh over it | take cut 0.12 s after the aligned word end; cut at the word end | keep ~0.35 s tail with a short fade; cut and laugh ≥ 0.2 s after the last word |
| Prop flashes into another shot for 1–2 frames | a diegetic prop left visible outside its beat | show props only inside their own shot window |
| Hook reads rushed | `evenpace` counted a year as one word | count spoken words (a year ≈ 3); cap the hook tempo (`--cap l1=1.12`) |

[Back to create-video](create-video.md)
