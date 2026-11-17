# 2D long-form video (16:9 explainer, 20 s to 20 min)

Animated explainer or documentary-style story, 16:9, with a narrator, optional character voices, music and SFX. The
picture is Remotion (SVG/HTML), text motion is GSAP seeked by frame or frame math, and three.js (`@remotion/three`)
takes the shots that need real depth. The pipeline is shared; the look comes from one of the styles below, which the
user chooses. It extends [create-video](create-video.md): keep its production checkpoint, privacy and delivery rules.

| Layer | Owner |
| --- | --- |
| Story, script, read-aloud pass | [Content Writing](../library/content-writing/README.md), `humanizer` |
| Shot direction, camera, light, visual QA | [`remotion-3d-director`](../.agents/skills/remotion-3d-director/SKILL.md) (3D shots), this workflow (2D shots) |
| Look, shot vocabulary, motion rules | The chosen style article in [`library/styles/`](../library/styles/README.md) |
| Puppets, sets, lighting, labels, map, ending, board pieces | Kit in [`studio/src/longform/kit/`](../studio/src/longform/kit/index.ts) |
| Text animation | GSAP through [`useGsapTimeline`](../studio/src/gsap/useGsapTimeline.ts) (paused timeline, seeked to `frame / fps`) |
| 3D shots (landmarks, globes, product, objects) | `@remotion/three` inside a scene component |
| Voice per line, SFX, music | ElevenLabs CLI (`text-to-speech`, `sound-effects`, `music` skills) |
| Timeline, mouth tracks, ducking, manifest | [`studio/tools/longform-2d/`](../studio/tools/longform-2d/README.md) |
| Assembly and render | Remotion `LongForm-<slug>` composition ([`LongForm.tsx`](../studio/src/longform/LongForm.tsx)) |

Workflow ideas (script structure, shot vocabulary, line-by-line voice cueing) are adapted from aivxer's "2D Animation
Long Form" skill; the code here is a separate Remotion implementation.

## 0. Choose the style (ask the user)

Before writing the script, ask the user which style the video should use, unless they already named one. Show both
options with one line each and offer the demo renders; record the choice in `production.md`.

| Style id | Look | Best for | Demo episode |
| --- | --- | --- | --- |
| [`ink-puppet-night`](../library/styles/ink-puppet-night.md) | Flat ink-line puppets in dense night sets, pushing camera, hand-lettered labels, polaroid ending | Character-led stories: history, money, true crime, a founder's bet | `demo-2d` ("The Missing Cent") |
| [`argument-board`](../library/styles/argument-board.md) | Dark board, locked camera, argument rail, question title, line-carry, revise, skeptic card | Evidence-led explainers: technology, science, analysis | `demo-board` ("Vì sao GPU chạy AI nhanh hơn CPU?") |

If neither fits, say so and propose adapting one; a new style gets its own article before the build. Never mix two
styles in one episode.

## 1. Start the production

```powershell
python studio/tools/longform-2d/scaffold.py <slug> --style ink-puppet-night|argument-board --title "Episode title"
```

This creates `local/productions/<slug>/` (`script.json`, `sfx.json`, `production.md`, all ignored by git) and
`studio/src/longform/episodes/<slug>/episode.tsx` copied from the style's demo (also ignored; only the demos
`demo-2d` and `demo-board` are tracked). The slug becomes the composition id `LongForm-<slug>`: lowercase letters,
digits and dashes.

Before any paid step, propose the toolset (AGENTS.md) and say what costs credits: ElevenLabs voice per line, music,
SFX, and the full render time.

## 2. Script

- English: about 150 spoken words per minute (2 min ≈ 300 words, 12 min ≈ 1,800). Vietnamese: about 4.2 words per
  second for the silent draft (`voice_lines.py --silent --wps 4.2`). Short sentences.
- Structure: follow the chosen style article ("Script Structure").
- Give every big number an everyday comparison. Facts: research them or list them under "Facts to check" in
  `production.md`, and tell the user which ones were not checked.
- Real people appear as generic figures identified by a name tag, never as a likeness. Never draw brand mascots,
  logos or another channel's characters; copy a style, not a cast.
- Natural spoken language, no headings inside the voice-over. Run the `humanizer` pass on the narration.

`script.json`:

```json
{
 "title": "The Missing Cent", "fps": 30, "width": 1920, "height": 1080,
 "cast": {
  "narrator": {"voice": "<voice id>", "role": "narrator"},
  "mira": {"voice": "<voice id>", "role": "character", "pan": 0.22}
 },
 "music": {"src": "music.mp3", "volume": 0.36, "duck": 0.6},
 "scenes": [
  {"id": "s1", "kind": "office", "tail": 0.6},
  {"id": "s2", "kind": "card", "card": true}
 ],
 "lines": [
  {"id": "l1", "scene": "s1", "speaker": "narrator", "vo": "Every night at nine, Mira checked the books."},
  {"id": "l2", "scene": "s1", "speaker": "mira", "vo": "One cent is missing. Again.", "gap": 0.4}
 ]
}
```

`kind` names a scene component in the episode file; several scenes can share a kind. `card: true` silences the music
for that scene. Optional per scene: `lead` (s before the first line, default 0.3), `tail` (s after the last line,
default 0.5), `hold` (length of a scene without lines, default 1.5), `props` (passed through to the component).
Optional per line: `gap` (s after it, default 0.26).

## 3. Shot list

One visual idea per beat, taken from the chosen style's "Shot Vocabulary" table. Mark which beats need a 3D shot
(`@remotion/three`) and which need real material (screenshots, documents) as evidence.

## 4. Voice

```powershell
cd local/productions/<slug>
python ../../../studio/tools/longform-2d/voice_lines.py --silent   # draft: silent audio + even word times, no credits
python ../../../studio/tools/longform-2d/voice_lines.py            # ElevenLabs, one take per line, cached
python ../../../studio/tools/longform-2d/voice_lines.py --only l7 l12   # redo just these lines
```

- Pick each speaker's `voice` with the ElevenLabs voice list (`creative_list_voices` / CLI) and record the choice in
  `production.md`. One distinct voice per character; the narrator stays centred, characters pan ±0.2–0.3.
- Takes are cached in `voice/raw/` by text, voice, model and speed: rerunning never pays twice for the same line.
- Trimming uses the waveform (onset and the tail above −45 dB), not alignment times, so word endings are kept.
- Listen to each new character line; regenerate a line instead of stretching it. Names the model mispronounces:
  respell them in `vo` (e.g. "Eiffel" → "Eye-ful") and keep the real spelling in labels.

## 5. Timeline and manifest

```powershell
python ../../../studio/tools/longform-2d/build.py
```

Scenes follow script order; inside a scene the first line starts 0.3 s in and each line follows the previous one by
0.26 s. The script writes `timeline.json` (seconds, for planning cues) and
`studio/public/media/<slug>/longform.json` (frames: scenes, lines with word times and mouth tracks, ducked music
volumes, SFX). Rerun it after any voice or script change; the picture follows automatically.

## 6. Picture (episode file)

`studio/src/longform/episodes/<slug>/episode.tsx` exports `episode = {slug, title, scenes: {kind: Component}}`. A
scene component gets `{scene, lines}` (frames relative to the scene) and the hooks `useLine(id)`,
`useSpeech(speaker)` and `useScene()`. Cue everything from the voice: `useLine('l5').words[3].from / fps` is the
second a word is heard.

Follow the chosen style article for ink, characters, camera, light, sets, text and motion. Shared rules:

- **3D shots**: build geometry once at module level; drive the camera from the frame in a child component
  (`useThree`), never with `useFrame`. In `ink-puppet-night`, toon shading with an inverted-hull outline matches the
  ink look.
- **Fonts**: the handwriting faces are Latin only; Vietnamese text uses `FONT.sans` / `FONT.mono`.

GSAP rules (from the `gsap-animation` skill): timelines are built paused and seeked to `frame / fps`; no
`Math.random`, timers, ScrollTrigger or `play()`. For SVG elements inside the camera, use the kit's pieces (they
tween a proxy object and write `transform`), because GSAP's `svgOrigin` math is wrong inside a CSS-scaled parent.

Preview: `cd studio; npx remotion studio`, open `LongForm-<slug>`. Before any full render, render stills of the
6–9 busiest frames and tile them into one sheet:

```powershell
cd studio
npx remotion bundle src/index.ts --out-dir ../local/productions/<slug>/bundle
npx remotion still ../local/productions/<slug>/bundle LongForm-<slug> ../local/productions/<slug>/stills/f0400.png --frame=400
```

Fix framing (labels cut off, characters too low in close-ups, overlapping text) before the full render.

## 7. Sound

- **SFX** (`sfx.json`, ElevenLabs `sound-effects` or `VFX_RESOURCES`): use the chosen style's sound palette
  ("Sound" in its article). Anchor each one to the voice or a scene so it follows retimes:

  ```json
  [{"src": "sfx/pop.wav", "at": "l2#1", "volume": 0.5, "note": "pop $0.01"},
   {"src": "sfx/thud.wav", "at": "l6#9", "offset": 0.18, "volume": 0.7, "note": "SOLD stamp"},
   {"src": "sfx/boom.wav", "at": "s2", "volume": 0.6, "note": "card boom"}]
  ```

  `l2#1` = word 1 of line l2 (0-based), `l2.end`, `s2`, `s2.end` or seconds. Align an SFX on its peak, not its
  start: read `video-shotcraft` `references/sound-design.md`.
- **Music**: ElevenLabs `music` (paid plan) or a licensed track; set `music` in `script.json`. The build ducks it
  60 % under speech and cuts it on `card` scenes.
- **Sign-off before the video**: render the full mix as audio only and have the user listen before the picture
  render:

  ```powershell
  npx remotion render src/index.ts LongForm-<slug> ../local/productions/<slug>/audio-preview/mix.mp3 --codec=mp3
  ```

  Layer trims live in the Props panel (`musicDb`, `voiceDb`, `sfxDb`).

## 8. Render

```powershell
cd studio
npx remotion render src/index.ts LongForm-<slug> ../local/productions/<slug>/renders/<slug>-v1.mp4 --concurrency=4
ffmpeg -i ../local/productions/<slug>/renders/<slug>-v1.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 ../local/productions/<slug>/renders/<slug>-v1-final.mp4
```

The 30 s demo renders in about 40 s at concurrency 4 on the reference machine; long episodes scale roughly linearly.
Skip loudnorm on a silent draft (it measures −inf). Render one version per request; keep only the latest render
(`v1`, `v2`…) and delete stale ones when the user approves the new cut.

## 9. QA before delivery

- `uv run python .agents/skills/remotion-3d-director/scripts/verify_render.py <final.mp4> --width 1920 --height 1080 --fps 30 --frames <n> --audio required`
- Contact sheet: `ffmpeg -i <final.mp4> -vf "fps=1/5,scale=384:216,tile=6x4" -frames:v 1 sheet.png`; look for cut-off
  labels, overlapping text, characters too low, static stretches.
- ElevenLabs Scribe (`speech-to-text`) on the final mix: the transcript matches the script, no clipped words.
- Loudness: `ffmpeg -i <final.mp4> -af ebur128 -f null -` ≈ −14 LUFS integrated.
- Deliver with the length, what is in it, which facts were not checked, and a request to watch once for timing.

## Pitfalls

| Symptom | Cause | Fix |
| --- | --- | --- |
| A label or stamp is missing or far off screen | GSAP `svgOrigin` computed inside the CSS-scaled camera | Use the kit's `PopLabel`/`Stamp` (proxy tween) or animate HTML outside the camera |
| GSAP text pops before fonts load or is mis-measured | SplitText measured fallback glyphs | `useGsapTimeline` waits for `document.fonts.ready`; load fonts through `loadFonts()` only |
| A GSAP piece crashes in a scene that starts before it should show | The hook builds on mount and needs its root element | Keep the root mounted (hide with opacity), or drive that piece from frame math |
| 3D camera does not move | R3F `camera` prop applies once | Set position and `lookAt` from the frame in a child using `useThree` |
| Memory grows over a long render | Geometry or materials created per frame | Build them once at module level |
| Ring/marker misses the character in the ending | Coordinates were stage units, the shot is zoomed | Convert: `screen = 960 + zoom·(x − focusX)`, same for y with 540 |
| Music audible on a black card | Scene not marked `card: true` | Mark it and rebuild |
| Diacritics fall back to another font | A handwriting face without Vietnamese glyphs | Use `FONT.sans` / `FONT.mono`; check a new font's coverage before adopting it |
| A board label sits on the wrong spot on the first frame | `measure()` ran before the font loaded | Render inside `LongForm` (it waits for `loadFonts()`); never measure at module level |
