# Ink Puppet Night — Character-Led 2D Long-Form

## Classification

| Axis | Classification |
| --- | --- |
| Video family | 2D animation |
| Communication format | Documentary-style story or explainer, 16:9, 20 s to 20 min |
| Visual style | Flat ink-line puppets (round head, pill body, stick legs) in dense night sets |
| Production route | [2D long-form workflow](../../workflows/2d-long-form-video.md), style id `ink-puppet-night`, demo episode `demo-2d` |

Best for stories carried by people: money and history stories, true crime, a con or a heist, a founder's bet. The
characters act the story; the narrator connects the scenes.

## Defining Characteristics

- **Ink**: one near-black outline (`INK`, about 6 px at 1080p) on characters, props, buildings and map shapes.
- **Characters**: a new `Look` per cast member (skin, suit, hair, glasses, hat). Dot / half / wide / closed eyes,
  smile / smirk / flat / o / mid / open / frown mouths, sweat, brows. Mouths follow `useSpeech(speaker)`; blink with
  `blinking(frame, fps, period, phase)`; idle bob; a squash at the start of each shot; poses snap with
  `{from, to, k}` (overshoot), never drift. Real people are generic puppets with a name tag, never a likeness.
- **Camera**: every shot pushes in 5–10 % (`Camera zoom`), a small rotation on table and map shots, `whipOut` /
  `whipIn` between related shots, `shakes` on stamp hits. No static frame longer than about 2 s.
- **Light**: draw the set flat, then `Night` (navy multiply with holes for lamps, windows, spill), `Glow` on bulbs,
  `GroundShadow` under feet, `Vignette` on top.
- **Sets**: dense with props (window with a night city, curtains, clock, calendar, picture, lamp, desk, rug). Copy
  `Room` into the episode and add the story's own objects.
- **Info graphics live in the world**: newspapers with a marker circle, documents, bills, price tags, `Stamp`
  ("SOLD", "TOP SECRET"), counters, maps with dotted routes.
- **Text**: lime or cream hand-lettered `PopLabel`s; chapter and punchline cards are white handwriting on black
  (`TextCard`, `ChapterTitle`); `LowerThird` for names; `LocationTag` lower left.
- **Ending**: `PolaroidEnding`: flash, freeze, tilted instant photo, red marker ring, handwritten payoff line.

## Script Structure

Cold open in the middle of the action → "here's the strange part" → stakes → a promise → chapters, each opened by a
black title card → a short two-character exchange roughly every 30 s → a callback ending → a teaser line. Give every
big number an everyday comparison.

## Shot Vocabulary (kit: `studio/src/longform/kit/`)

| Shot | How |
| --- | --- |
| Wide set, small full-body characters | `Room` (or the episode's own set) + `Puppet` at `s` 0.6–1.2, `Night` + `Glow` |
| Close-up | Same set behind a blur, `Puppet` at `s` ≈ 2, feet below frame |
| Top-down table | Paper rect, documents and bills sliding in with `back()`, sleeves and hands as simple shapes |
| Map | `MapGrid`, land as ink-outlined paths, `City`, `Route` with a marker riding the dotted line |
| Landmark / object in 3D | `@remotion/three`: toon materials + inverted-hull outline, low angle, frame-driven orbit; `Stamp` on top |
| Chapter card | `ChapterTitle` (SplitText chars) or `TextCard` (words land when the narrator says them) |
| Street walk | Exterior set, `walkLegs(t * 11)` with `bob = 6·|sin|`, settle with a squash |
| Ending | `PolaroidEnding` |

## Sound

A pop on every pop-in, whooshes on whips, paper rustle on documents, footsteps on walks, a thud for stamps, a shutter
on the polaroid, a low boom under black cards; music ducked under speech and cut on `card` scenes.

## Inspection Criteria and Pitfalls

- **Same-family risk.** Round-headed puppets in detailed night sets are a crowded genre. Give the series its own
  topics, angle, cast silhouettes and voice, and run a mute test: muted, name hidden, can viewers tell the clips are
  yours? (See the [argument-board](argument-board.md) style for a contrasting route.)
- **Fonts are Latin only.** Caveat Brush, Kalam and Permanent Marker miss most Vietnamese letters (ơ, ư, ạ, ặ…). For
  Vietnamese text use `FONT.sans` / `FONT.mono` (Be Vietnam Pro, JetBrains Mono), or add a handwriting face that
  covers the language after checking its glyphs.
- GSAP inside the camera: use the kit's `PopLabel` / `Stamp` (proxy tween); GSAP's own `svgOrigin` is wrong inside the
  CSS-scaled camera.
- Check stills of the busiest frames for cut-off labels, characters too low in close-ups and overlapping text.

Verification level: demo episode rendered end to end with a silent draft voice; real voices, music and SFX not yet
exercised. Workflow ideas adapted from aivxer's "2D Animation Long Form" skill (no code or assets included).
[Back to Styles](README.md).
