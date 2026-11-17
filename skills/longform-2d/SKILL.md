---
name: longform-2d
description: Make long-form 16:9 animated explainer and story videos (20 s to 20 min) in Remotion, in one of two styles the user chooses - ink-puppet-night (flat ink-line puppets, night sets, hand-lettered text, polaroid ending) or argument-board (dark board, argument rail, revise, evidence diagrams, skeptic card) - with three.js shots, ElevenLabs narrator and character voices, music and SFX. Use for a YouTube explainer, technology or science explainer, documentary-style money, history or true-crime story, "2D long video", or when the user names this skill.
---

# 2D long-form video

Remotion draws the picture, GSAP or frame math animates the text, three.js takes the shots that need depth, ElevenLabs
makes one voice take per line, and `LongForm-<slug>` assembles everything from a manifest. The look comes from one of
two styles; **the user chooses it**.

## First: ask which style

Unless the user already named a style, ask before writing any script, and wait for the answer:

| Style | One line | Demo |
| --- | --- | --- |
| `ink-puppet-night` | Character-led story: ink-line puppets in night sets, pushing camera, hand-lettered labels | `LongForm-demo-2d` |
| `argument-board` | Evidence-led explainer: dark board, argument rail, question title, line-carry, revise, skeptic card | `LongForm-demo-board` |

Offer to show the demo renders. Suggest `argument-board` for technology, science and analysis, `ink-puppet-night` for
stories carried by people, but let the user decide. Record the choice in `production.md` and pass it to
`scaffold.py --style`. Never mix the two styles in one episode.

Find the VFXLens repository root (the folder with `AGENTS.md` and `studio/package.json`) and read, in order:

1. `<repo>/AGENTS.md`: propose the toolset first; say which steps cost ElevenLabs credits or long render time.
2. `<repo>/workflows/create-video.md`: production checkpoint, privacy, delivery.
3. `<repo>/workflows/2d-long-form-video.md`: the full pipeline, commands and pitfalls.
4. The chosen style article: `<repo>/library/styles/ink-puppet-night.md` or `<repo>/library/styles/argument-board.md`.

## Hard rules

- Original characters only: copy a drawing style, never a channel's characters, logos, thumbnails or frames. Real
  people are generic puppets with a name tag. No brand mascots.
- Facts: research or flag them in `production.md`; tell the user which were not checked.
- Draft first with `voice_lines.py --silent` (free); pay for voices only once the script is approved.
- Check a tiled sheet of the busiest stills before any full render; aim for one full render per request.
- Deliver a full-mix audio preview for sign-off before the video render when the audio changed.
- You cannot hear or watch the result: transcribe the final mix (ElevenLabs Scribe) and ask the user to watch once
  for timing.
- Private productions stay in `local/productions/<slug>/` and `studio/src/longform/episodes/<slug>/` (both ignored).

## Pieces

| Need | Where |
| --- | --- |
| Puppet, poses, expressions, walk, blink | `studio/src/longform/kit/Puppet.tsx` |
| Camera push/rotate/whip/shake, stage | `kit/Camera.tsx` |
| Night lighting, glow, ground shadow | `kit/Light.tsx` |
| Text card, chapter title, pop label, stamp, lower third, location tag (GSAP) | `kit/Text.tsx` |
| Map grid, city, dotted route | `kit/Map.tsx` |
| Starter office set + matching lights | `kit/Room.tsx` |
| Polaroid ending | `kit/Ending.tsx` |
| Board pieces: rail, question title, placed text, revise, line-carry, skeptic, note, focus/accel helpers | `kit/Board.tsx` |
| Scene hooks `useLine`, `useSpeech`, `useScene` | `studio/src/longform/context.ts` |
| Worked examples | `studio/src/longform/episodes/demo-2d/episode.tsx` (ink-puppet-night, with a three.js shot), `demo-board/episode.tsx` (argument-board) |
| Scaffold, voices, timeline/manifest | `studio/tools/longform-2d/` |

For GSAP details beyond the kit, the `gsap-animation` skill (notedit/happy-skills) can be installed locally into
`studio/.claude/skills/`; its determinism rules already apply here.

---
Workflow ideas adapted from aivxer's "2D Animation Long Form" skill.
