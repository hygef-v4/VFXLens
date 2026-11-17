---
name: longform-2d
description: Make long-form 16:9 animated explainer and story videos (20 s to 20 min) in a flat ink-line 2D style with original puppet characters, night lighting, hand-lettered GSAP text, chapter cards, maps, three.js shots, ElevenLabs narrator and character voices, music and SFX, assembled in Remotion. Use for a YouTube explainer, documentary-style money, history or true-crime story, "2D long video", or when the user names this skill.
---

# 2D long-form video

Remotion draws the picture (SVG puppets, sets, lighting), GSAP animates the text, three.js takes the shots that need
depth, ElevenLabs makes one voice take per line, and `LongForm-<slug>` assembles everything from a manifest.

Find the VFXLens repository root (the folder with `AGENTS.md` and `studio/package.json`) and read, in order:

1. `<repo>/AGENTS.md`: propose the toolset first; say which steps cost ElevenLabs credits or long render time.
2. `<repo>/workflows/create-video.md`: production checkpoint, privacy, delivery.
3. `<repo>/workflows/2d-long-form-video.md`: the full pipeline, style rules, commands and pitfalls.

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
| Scene hooks `useLine`, `useSpeech`, `useScene` | `studio/src/longform/context.ts` |
| Worked example with every piece and a three.js shot | `studio/src/longform/episodes/demo-2d/episode.tsx` |
| Scaffold, voices, timeline/manifest | `studio/tools/longform-2d/` |

For GSAP details beyond the kit, the `gsap-animation` skill (notedit/happy-skills) can be installed locally into
`studio/.claude/skills/`; its determinism rules already apply here.

---
Workflow ideas adapted from aivxer's "2D Animation Long Form" skill.
