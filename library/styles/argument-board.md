# Argument Board — Evidence-Led 2D Explainer

## Classification

| Axis | Classification |
| --- | --- |
| Video family | Motion graphics |
| Communication format | Explainer / analysis, 16:9, 20 s to 20 min |
| Visual style | Dark board, editorial sans + mono type, concrete diagrams, one accent colour |
| Production route | [2D long-form workflow](../../workflows/2d-long-form-video.md), style id `argument-board`, demo episode `demo-board` |

Best for technology, science and money explainers whose payoff is a corrected idea ("you thought X; it is Y"). The
argument is the hero; a small skeptic character voices the objection.

**Essence:** the argument stands still, evidence arrives on cue, and only the correction draws attention.
**Never:** a drifting camera, a pop on every word, per-word blur-ins, glowing holograms or node graphs, white keynote
slides, a character at the centre of every shot, a number without a source.

## Signatures (repeat in every episode)

1. **Argument rail**: a vertical line at x = 128 with one node per chapter; the open chapter's name runs down the
   rail beside its node (mono, 30 px). Viewers always see where they are in the argument.
2. **Question title**: the chapter question lands large in the centre (72 px), holds about 1 s, then demotes to the
   board title, top left (34 px, 62 % opacity) in 22 frames.
3. **Line-carry**: the pen underline of a claim runs on and draws the frame of the evidence region (34 frames,
   ease-in-out). Regions change by a line, not a cut.
4. **Revise**: once per chapter, after 0.5–1 s of quiet, the wrong words are struck in the accent colour (8 frames)
   and the right words are written above (10 frames, tilted −2°) with a wobbly pen underline.
5. **Skeptic**: an index card with a folded corner and ruled lines peeks in from the bottom margin only when the
   argument has a real objection; its question also appears in a boxed note so it reads with the sound off.

## Look

| Role | Hex |
| --- | --- |
| Paper (board, 48 px dot grid at 7 %) | `#1C1B19` |
| Ink | `#EEE7D8` |
| Muted (labels, items that stepped back) | `#8E887C` |
| Accent (revise, open chapter, the winning value only) | `#FF6B2C` |
| Core / faint (inactive blocks, bar tracks) | `#3A3833` / `#2A2926` |

All text pairs pass 4.5:1 on the board (checked with motion-pack `frame-design` `contrast.py`). One accent per frame.
Whatever is no longer the hero drops to 32 % opacity in 10 frames (`focus()`), so a board that keeps building stays
readable.

**Type:** Be Vietnam Pro 500/700 (`FONT.sans`) and JetBrains Mono (`FONT.mono`), both with full Vietnamese coverage.
Request only 500 and 700. Claims 96 px, question 72 → 34 px, rewrite about 92 px, labels and captions ≥ 32 px, honesty
labels ("minh họa", sources) ≥ 28 px held ≥ 2 s. Grid: 12 columns, 96 px margins; content column from x = 300,
evidence region about x 1090–1824.

## Motion

Base unit 4 frames; cubic ease-out for text and data, cubic ease-in-out for lines and region moves; no overshoot except
the skeptic (4 % cap); hold ≥ 30 frames after each key action. Camera locked: motion comes from meaning accumulating.

| Verb | How |
| --- | --- |
| Place | Meaning chunks land on their word times: opacity + 10 px rise in 6 frames (`Placed`, `QuestionTitle`) |
| Count | Numbers and bars move with the narration; tabular figures; never bounce |
| Revise | Signature 4 (`Revise`) |
| Build | Groups arrive faster and faster (`accel(i, n, span)`, delay ∝ √i), never at a flat stagger |

Show concrete things: cores as squares, work as bars, real screenshots and documents as evidence. Abstract glow reads
as filler.

## Script Structure

Each chapter (60–120 s) follows question → wrong model → evidence → revise. One revise per chapter, on the line that
says the corrected idea. The skeptic speaks only when the argument has a real objection; there is no fixed dialogue
cadence. Cue every element from word times (`useLine(id).words[i].from`).

## Shot Vocabulary (kit: `studio/src/longform/kit/Board.tsx`)

| Shot | How |
| --- | --- |
| Chapter open | `ArgumentRail` advances, `QuestionTitle` lands and demotes |
| Wrong model | `Revise` with `label` ("Nhiều người nghĩ"), `lead` and `wrong`; its underline is drawn automatically |
| Evidence region | `LineCarry` from the claim underline into a box; the episode draws the mechanism inside |
| Mechanism / race | Episode code: squares, bars, counters built with `accel`, dimmed with `focus` (see `demo-board`) |
| Objection | `Skeptic` + `BoardNote` |
| Conclusion | `Revise` strike and rewrite; evidence dims, the claim returns to full brightness |

## Sound

One consistent narrator. A pen scratch on revise, a soft tick when a chapter node lights, a faint paper sound while the
line-carry draws, quiet before each revise, music per chapter. Candidate CC0 sources: motion-pack `sfx/paper`,
`sfx/ui`, `music/bed_*` (must be built locally first).

## Inspection Criteria and Pitfalls

- Mute test: three 3-second clips, muted and unnamed, mixed with clips of similar channels; most viewers should pick
  yours and restate the conclusion.
- Watch at phone size: every text that must be read is ≥ 32 px; nothing overlaps the evidence frame.
- `measure()` uses the loaded font; render only after `loadFonts()` (LongForm does this).
- Accent appears only on the revise, the open chapter and the winning value; a second accent means two heroes.

Sources: motion-pack `frame-design` (tone cell, motion personality, one hero per frame, real weights, sizes),
video-shotcraft `aesthetic-rules.md` (R1 hold, R2 acceleration, Q4 restraint, Q11 effective text height) and its shot
cards `title-demote-to-label` and `line-carry-transition`, motion-pack `patterns/structures.json` explainer beat sheet.
Verification level: the demo was rendered end to end with a silent draft voice (2026-11-17); the mute test with real
viewers, real voices, music and SFX are not yet done. [Back to Styles](README.md).
