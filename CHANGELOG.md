# Changelog

## Unreleased

- 2D long-form video: `LongForm-<slug>` Remotion assembly and kit (SVG puppets, camera, night lighting, GSAP text
  cards, labels, stamps, lower thirds, maps, polaroid ending), `@remotion/three` shots, per-line ElevenLabs voices with
  a free silent draft, timeline/mouth-track/ducking builder, demo episode, workflow and `longform-2d` skill.
- `gsap` added to the studio; `useGsapTimeline` hook and `GsapThreeDemo` composition.
- Bundled handwriting fonts (Caveat Brush, Kalam, Permanent Marker).
- Long-form styles: `ink-puppet-night` (the original puppet look) and `argument-board` (argument rail, question title,
  line-carry, revise, skeptic card, focus dimming) with `kit/Board.tsx`, the `demo-board` episode, library style
  articles, `scaffold.py --style`, and the skill asking the user which style to use. Be Vietnam Pro and JetBrains Mono
  bundled for Vietnamese text; the voice and build scripts print UTF-8 on Windows consoles.

## 0.1.0 — 2026-11-17

First open-source release.

- `vfx` CLI: offline After Effects project analyzer (`.aep`/`.aepx`) and video VFX analyzer (scenes, optical flow,
  signal-based effect candidates, contact sheets, reports).
- Remotion studio with `ThreeShort`, a manifest-driven assembly for three.js Shorts (captions, overlays, voice, ducked
  music, peak-aligned SFX, iris transitions).
- three.js character-Short toolkit: scaffold, starter film, voice timing tools (`tighten`, `evenpace`, `fit`, `align`,
  `silent_timing`), manifest builder, procedural music fallback, render script and perceptual QA (`qa/audit.py`).
- Agent skills (`vfxlens`, `motion-scout`, `remotion-3d-director`), workflows and an editing knowledge library.
