# Component discovery

Use this as a shortlist method alongside [architecture](architecture.md),
[render and QA](rendering-and-qa.md), and [attribution](source-attribution.md).
An upstream demo proves a component can run in its own app; it does not prove
Remotion seekability, headless compatibility, safe ownership, or visual fit.

## Rank by fit, not catalog size

1. Search the local `studio/` dependency tree and source first. Prefer a house
component already built on the pinned Remotion / R3F APIs.
2. Shortlist one or two candidates by the shot's job and desired visual evidence.
Inspect source, its README/docs, exact dependencies, license, and a real demo
frame or clip. Record the commit and specific source path in
[source-attribution](source-attribution.md) when reuse matters.
3. Choose a frame-driven implementation when the reference is a rendered film.
Treat browser interaction, scroll, hover, pointer position, wall-clock time,
and autonomous RAF animation as input signals that need a designed deterministic
replacement. A drop-in web component is not assumed.
4. Probe one representative frame and seek/repeat it before adopting. Check
mount/unmount cleanup, async asset readiness, missing fonts/media, actual browser
backend and package versions. Reject a component if its core visual depends on
unavailable inputs or unowned GPU resources.

## Findings from pinned sources

| Source | Useful evidence | Reuse decision |
| --- | --- | --- |
| [Remocn `remocn` skill](https://github.com/Remocn/remocn/blob/1d15141a76d06ad469faf31d7b12f8c21f772489/plugins/remocn/skills/remocn/SKILL.md), [typewriter](https://github.com/Remocn/remocn/blob/1d15141a76d06ad469faf31d7b12f8c21f772489/registry/remocn/typewriter/index.tsx), and [whip-pan](https://github.com/Remocn/remocn/blob/1d15141a76d06ad469faf31d7b12f8c21f772489/registry/remocn/whip-pan/index.tsx) | MIT-licensed Remotion component catalog; animation tier is frame-driven and the skill distinguishes duration (`Length`), `speed`, transition factories, and state-driven UI primitives. `whip-pan` derives transforms from Remotion transition progress; typewriter calls the package's timeline hook. | Best upstream candidate for small, explicitly selected text/transition components. Verify the selected entry's current docs and registry dependency list. Upstream pins Remotion 4.0.542; VFXLens uses 4.0.543, so source-level compatibility is plausible, not tested. |
| [React Bits Ballpit source](https://github.com/DavidHDev/react-bits/blob/cf2801031f07f53d4684e65b961bde7c2e2a6921/src/content/Backgrounds/Ballpit/Ballpit.jsx), [DotGrid source](https://github.com/DavidHDev/react-bits/blob/cf2801031f07f53d4684e65b961bde7c2e2a6921/src/content/Backgrounds/DotGrid/DotGrid.jsx), [README](https://github.com/DavidHDev/react-bits/blob/cf2801031f07f53d4684e65b961bde7c2e2a6921/README.md) | Concrete WebGL background ideas and live demos. Ballpit initializes from `Math.random`, advances mutable particle state via RAF, and cancels RAF on cleanup; DotGrid likewise schedules RAF and cancels it. Cleanup alone does not make their visible state a function of frame. | Reference the look/mechanics; do not drop these components into a Remotion shot. Rebuild only the needed treatment with seeded static particle parameters and absolute frame evaluation, or pre-render/bake it. License is MIT + Commons Clause; do not redistribute the component itself or a port as a component/product. A film render is not the source component, but use the exact license terms before any source reuse. |
| [motion-skills README](https://github.com/iart-ai/motion-skills/blob/9b9ce041932da787cc856d4cdf23afb6cd13d4bf/README.md), [verify-loop README](https://github.com/iart-ai/motion-skills/blob/9b9ce041932da787cc856d4cdf23afb6cd13d4bf/tools/verify/README.md) | MIT-licensed index of skills/packs, including Remotion and canvas work; its deliver-and-verify pattern captures frames/contact sheets and probes encoded output. This checkout is a hub (README plus verification tools), not the full individual skill packs. | Reuse the compact evidence loop concept, already covered by VFXLens QA. Shell helpers are POSIX and require external tools; do not add them to the Windows studio workflow unchanged. |

## Compatibility and lifecycle gate

The local studio pins Remotion / `@remotion/three` 4.0.543, Three 0.187.0,
R3F 9.8.2, and React 19.3.1. Recheck `studio/package.json` and its lockfile at
implementation time. Upstream catalog manifests are not proof that transitive
packages exist locally; do not install dependencies or run upstream setup as part
of discovery.

Audit each candidate for: (a) state written relative to previous render/time,
(b) randomness generated during render or initialization, (c) browser-only APIs
and pointer/scroll input, (d) external fonts/images/shaders and when ready, (e)
RAF/timer/listener cancellation, (f) ownership of renderer, geometry, materials,
textures, targets and caches. Convert mutable motion to `frame → absolute value`
and allocate random seeds once from stable inputs. Preserve or replace its
visible purpose; do not preserve scheduling mechanics merely to keep the source
familiar. See [architecture](architecture.md#one-frame-clock) and
[allocation/disposal](architecture.md#allocation-and-disposal).

Visual evidence inspected for this research was source/demo documentation only;
no candidate was rendered in VFXLens Studio. Component appearance and fit remain
unverified until a local styleframe and seek probe are reviewed.
