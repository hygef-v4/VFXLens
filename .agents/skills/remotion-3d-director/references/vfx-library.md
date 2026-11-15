# VFX library patterns for Remotion

Use this reference to choose a particle, foliage, water, or shader pattern. The
existing [architecture](architecture.md) and [WebGPU capture contract](webgpu-shaders.md)
remain authoritative: an interactive frame loop is not a deterministic Remotion
timeline, and a successful preview does not prove headless export.

## Adapt the state model first

For every visible effect, decide whether its state is a direct function of
`(frame, fps, inputs, seed)` or history-dependent.

- Prefer analytical motion and fixed per-instance seeds when the look permits.
- For a history-dependent effect, bake its trajectory once into stable arrays,
  or replay fixed simulation steps from a reproducible checkpoint to the requested
  frame. A seeded start alone is not enough when the update depends on prior frames.
- Keep GPU storage, graphs, and materials stable. Set uniforms or buffers for
  the requested frame; do not allocate a new system in each render pass.
- If compute is stateful, define source/target buffers and step order, serialize
  frame submissions, await the submitted GPU work, and hold capture until that
  frame is complete. Stale asynchronous work must not release a newer frame's
  hold. Follow [WebGPU readiness and cleanup](webgpu-shaders.md#own-the-complete-frame-transaction).
- Keep a tested fallback that preserves the authored timing. Record the backend
  actually used and freeze it for the export.

## Patterns worth adapting

- **Reusable GPU particle systems:** Three VFX and Plume separate particle data,
  emitters, compute, and rendering. Borrow the separation only when a shot needs
  the scale or feature set. These libraries advance state; their stock R3F
  `useFrame(delta)` integration needs a frame-addressable adapter or baked state
  for Remotion.
- **Deterministic surfaces and scatter:** Stylized Components uses seeded,
  area-weighted surface sampling for stable grass placement, then moves detail
  through shader uniforms. The pattern can seed static layout at setup and drive
  wind from absolute frame time. Its separate DustMotes example uses
  `Math.random()` and a time-growing wander, so it is not deterministic without
  seeded setup and absolute-time evaluation.
- **Useful image-space looks:** Custom GLSL for foliage, water, god rays, and
  painterly filters can provide a strong target look. Check the renderer and
  shader API before reuse: the inspected stylized project uses WebGL
  `onBeforeCompile`, which is not a TSL/WebGPU shader, and its dependencies are
  not part of this studio.
- **Modules and data layout:** Plume's packed storage and update modules are
  useful design references for a large GPU system. They do not justify adding
  a new abstraction to a small shot; reuse VFXLens's current entities and
  renderer ownership where sufficient.

## Library selection and evidence limits

| Reference | Strongest use | Remotion fit | Main limit |
| --- | --- | --- | --- |
| [Stylized Components](https://github.com/cortiz2894/stylized-components/tree/1cece0a296b29299d1380c34feb5c158b2f04500) | Reusable authored GLSL looks; seeded surface scatter | R3F/React concepts transfer, but it targets Three 0.182 and WebGL shader hooks | Its `useFrame` and random dust path are interactive; shader code is not TSL. |
| [Three VFX](https://github.com/mustache-dev/Three-VFX/tree/c5533097adbccf22b4701f2f2527fb2fec951bd1) | Feature-rich GPU particle implementation and CPU fallback | R3F and React shape are close; current dependencies and backend still need audit | `useFrame` passes delta into async stateful updates; GPU/CPU paths are not seekable by themselves. |
| [Plume](https://github.com/travisdmathis/plume/tree/7ec1d66667a16b36d423df49c5a1189b9837edd4) | Modular WebGPU particle architecture, packed storage, seeded fixed-step effects | Three TSL conceptually aligns with the existing WebGPU branch | README marks it pre-1.0 and WebGPU-only; no Remotion adapter or cross-backend proof. |

The ranking above is about technical/reuse fit for this studio, not a visual
quality score. The README describes demos and includes linked footage, but no
demo image or video was opened during this inspection. Treat all looks as
unverified until the representative Remotion frame is rendered and viewed.

## Provenance

- [Three VFX README](https://github.com/mustache-dev/Three-VFX/blob/c5533097adbccf22b4701f2f2527fb2fec951bd1/README.md), [R3F component](https://github.com/mustache-dev/Three-VFX/blob/c5533097adbccf22b4701f2f2527fb2fec951bd1/packages/r3f-vfx/src/VFXParticles.tsx), [particle system lifecycle and updates](https://github.com/mustache-dev/Three-VFX/blob/c5533097adbccf22b4701f2f2527fb2fec951bd1/packages/core-vfx/src/particle-system.ts), [CPU fallback implementation](https://github.com/mustache-dev/Three-VFX/blob/c5533097adbccf22b4701f2f2527fb2fec951bd1/packages/core-vfx/src/webgl-fallback/cpu-update.ts). Inspected at commit `c5533097adbccf22b4701f2f2527fb2fec951bd1`, MIT.
- [Plume README](https://github.com/travisdmathis/plume/blob/7ec1d66667a16b36d423df49c5a1189b9837edd4/README.md), [particle buffer](https://github.com/travisdmathis/plume/blob/7ec1d66667a16b36d423df49c5a1189b9837edd4/packages/plume/src/particle-buffer.ts), [module exports](https://github.com/travisdmathis/plume/blob/7ec1d66667a16b36d423df49c5a1189b9837edd4/packages/plume/src/index.ts). Inspected at commit `7ec1d66667a16b36d423df49c5a1189b9837edd4`, MIT.
- [Stylized Components README](https://github.com/cortiz2894/stylized-components/blob/1cece0a296b29299d1380c34feb5c158b2f04500/README.md), [grass shader](https://github.com/cortiz2894/stylized-components/blob/1cece0a296b29299d1380c34feb5c158b2f04500/src/components/grassField/shaders/grassBlade.ts), [seeded scatter](https://github.com/cortiz2894/stylized-components/blob/1cece0a296b29299d1380c34feb5c158b2f04500/src/components/grassField/utils/scatter.ts), [dust motes](https://github.com/cortiz2894/stylized-components/blob/1cece0a296b29299d1380c34feb5c158b2f04500/src/components/godRaysScene/DustMotes.tsx). Inspected at commit `1cece0a296b29299d1380c34feb5c158b2f04500`, MIT.
