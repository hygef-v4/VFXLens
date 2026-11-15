# Architecture and frame ownership

## Choose the smallest engine that fits

Use VFXLens's existing `studio/`, scripts and pinned packages. Inspect installed
APIs before adapting examples: researched repos span Three r173, r178, r179 and
r187. Dependencies such as Drei and `@react-three/postprocessing` occur upstream
but are not automatically available here. The installed `postprocessing` package
alone does not provide the React wrapper.

Separate responsibilities without cloning an upstream framework:

- **Composition:** declared resolution/fps/duration, scene timing, audio/captions.
- **World/set:** stable geometry, materials, textures and meaningful entity IDs.
- **Shot evaluation:** camera, visibility, transforms, focus and cues at frame `f`.
- **Renderer:** backend initialization, submission/readiness and ownership cleanup.

For a small film, React scene components are sufficient. For a large stable set,
an imperative world can expose `create → evaluate(frame) → dispose`; keep its
factory stable. Assign every changing property at each evaluation, including
properties restored when seeking backward. Keep story data separate from renderer
mechanics. This combines the world interface in remotionshorts with the small
entity components in explainer-3d; it is not a port of either engine.

## One frame clock

```tsx
const frame = useCurrentFrame();
const {fps} = useVideoConfig();
const seconds = frame / fps;
const rise = spring({frame: frame - cueFrame, fps, config: {damping: 22}});
const angle = interpolate(frame, [0, 90], [-0.4, 0.4], {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
});
return <mesh position={[0, rise, 0]} rotation={[0, angle, 0]} />;
```

These are authored example values, not a fixed duration or easing prescription.
Inside a `Sequence`, the hook returns sequence-local frame; subtracting the global
start again is an offset bug. Pass global time explicitly for effects crossing cuts.
Inside a canvas, `Sequence` needs `layout="none"` because DOM wrappers are invalid
in the Three scene graph.

`ThreeCanvas` handles Remotion/R3F context and capture scheduling. Use declarative
properties or frame-keyed layout effects for camera/buffer mutations. R3F's
`useFrame`/clock delta, GSAP playback, timers and CSS animations are not the film's
clock. Stateless sine motion from `frame/fps` is seekable; `position += velocity`
depends on history. Bake physics/fluid/boid results or replay exact fixed steps
from a known checkpoint for arbitrary frame access. GPU work must also satisfy
the [WebGPU submission contract](webgpu-shaders.md).

## Allocation and disposal

- Memoize base geometry, seed arrays, node graphs and materials by actual inputs.
  Update uniforms/buffer contents instead of reconstructing GPU objects each frame.
  An upstream seeded DataFlow still reallocates and changes jitter every frame;
  preserve per-particle offsets and animate the path analytically for continuity.
- Use instancing/points for repeated small objects. Choose particle count,
  shadow size, DPR and postprocessing at export start, then keep them fixed.
- R3F manages declarative geometry/material lifetime. An object supplied through
  `primitive`, cached loader resources and an externally supplied renderer have
  different ownership: track the owner and dispose only what it owns.
- Disposing a material does not dispose its textures. Release owned render
  targets, textures, geometries, materials, composers and renderer; release shared
  caches only when their last consumer is gone. `dispose={null}` requires an owner.
- Scope cleanup to each mount. During asynchronous initialization/unmount, wait
  for owned in-flight work to settle before disposing its device/resources;
  prevent an obsolete completion callback from releasing a new frame's hold.

The performance goal is predictable frame cost and stable memory, not maximal
effect count. Profile the heaviest shot and repeat seeks before a long render.

Sources: [explainer components](source-attribution.md#explainer-3d),
[world/lifecycle engine](source-attribution.md#remotionshorts),
[R3F ownership](https://r3f.docs.pmnd.rs/api/objects),
[Three disposal](https://threejs.org/manual/en/how-to-dispose-of-objects.html).
