# WebGPU / TSL: experimental rendering branch

## Choose and freeze a backend

The material/compute examples in rayBlock/remotion-webGPU were written against
Three r178, while this studio currently uses r187. Verify exports and installed
source before using an example. `three/webgpu` and `three/tsl` are already Three
subpaths; their presence does not establish a working GPU, R3F integration or
headless capture.

Probe in the **same Chromium/backend/flags** used for export. A WebGPURenderer can
internally fall back to WebGL2; `isWebGPURenderer` does not identify its backend.
Record native backend/adapter availability and test the specific material/kernel.
Freeze the chosen backend and quality across all worker pages. If initialization,
device limits, shader compilation or seeking fails, rerender with an explicitly
chosen WebGL analytical effect, baked sequence, or alternate local renderer.
Keep the fallback's story/timing; do not silently switch looks mid-export.

`--gl=angle` is a Chromium backend option used upstream, not a guarantee of native
WebGPU/hardware acceleration. Avoid importing global renderer flags from a demo.

## Prefer functions of index, seed and time

Useful patterns in the inspected source are TSL uniforms, node-material vertex
displacement/Fresnel color, and analytical particle morphs. Build graphs once and
update parameters at the requested frame:

```ts
import {MeshBasicNodeMaterial} from 'three/webgpu';
import {uniform, positionLocal, sin, vec3, color} from 'three/tsl';

const frameTime = uniform(0);
const material = new MeshBasicNodeMaterial();
material.colorNode = color('#8ac6ff');
material.positionNode = positionLocal.add(vec3(
  0, sin(positionLocal.x.mul(3).add(frameTime)).mul(0.12), 0,
));
// Inside the controlled render transaction, before submission:
frameTime.value = requestedFrame / fps;
```

This compact pattern needs a lit/physical node material when the look requires
lighting. A hologram can combine rim response, scan phase and bounded opacity;
set transparent/depth-write/blend intentionally and inspect edge sorting.

For morphing particles: generate stable `a[i]`, `b[i]` from seed and index, compute
`position[i] = mix(a[i], b[i], easedProgress(frame))`, then add bounded analytical
noise. Instancing/storage buffers let many instances share geometry. CPU-seeded
base arrays are preferable when consistent initialization across GPU vendors
matters; a GPU sine hash is repeatable on a fixed setup, not a cross-vendor
bit-identical guarantee. Set bounds explicitly when shader-displaced geometry
would otherwise be culled using its undeformed CPU bounds.

### Stateful compute needs a separate solution

Boids/SPH examples initialize with `Math.random()` and increment buffers in
`useFrame`. A frame-time uniform does not repair their state history or unordered
parallel buffer dependencies. Likewise, a frame-keyed `computeAsync()` effect
without a capture hold can race the screenshot.

Use a closed-form field, bake stable results, or reset and replay fixed steps to
the requested frame from a reproducible checkpoint. For a coupled simulation,
read from a previous-state buffer and write into a separate next-state buffer;
define swap/substep order. Verify jumping forward/backward and fresh-page renders
before claiming deterministic concurrent rendering. Reduce counts rather than
shipping the upstream O(N²) stress test as a production default.

## Own the complete frame transaction

Create one owner for initialization, frame state, compute, draw and readiness.
An imperative canvas is an option when an R3F adapter would require private
Remotion context internals. This is the required protocol, not a drop-in adapter:

```ts
// Native branch; retain the device you requested instead of guessing its queue.
const adapter = await navigator.gpu.requestAdapter();
if (!adapter) throw new Error('No native adapter; choose a fallback profile');
const device = await adapter.requestDevice();
const renderer = new WebGPURenderer({canvas, device, antialias: true});
await renderer.init();
if (!renderer.backend.isWebGPUBackend) throw new Error('Unexpected backend');
await renderer.compileAsync(scene, camera);

// Serialize submissions; these values belong to this requested frame.
applyAbsoluteState(requestedFrame, fps, seed);
if (computeNode) renderer.compute(computeNode);
renderer.render(scene, camera);
await device.queue.onSubmittedWorkDone();
// Only now release this transaction's Remotion delay handle.
```

Import `WebGPURenderer` from `three/webgpu`; supply viewport/pixel ratio and a
complete scene. Device acquisition/feature checks can require narrowing of WebGPU
types absent from a project's DOM typings; confirm installed types before adding
packages. Treat those identifiers as adapter-owned, not global mutable state.

Implementation checklist:

1. Acquire a labelled `delayRender` handle at committed initialization and for
   each pending capture, including frame zero. Bound initialization timeout.
2. Initialize viewport, device/renderer, assets and scene; await compilation and
   warmup without advancing authored simulation state.
3. Queue each requested frame with captured frame/seed/inputs, then apply state,
   compute, draw and await the actual queue. `computeAsync` in r187 initializes
   and submits; it does not itself wait for GPU completion.
4. Release that exact handle after its draw. During rapid Studio seeks, discard
   obsolete transactions and keep the latest frame's own hold; stale callbacks
   must not release a handle kept in a mutable shared ref.
5. On failure/device loss use `cancelRender(error)` and report the frame/backend.
   Cleanup releases obsolete holds on unmount, waits for in-flight owned work,
   then disposes resources and an explicitly owned device. Respect StrictMode's
   setup/cleanup cycle. Swallowing errors and continuing can export blank frames.

**Version trap found in installed r187:** `waitForGPU()` still exists but only
logs that it was removed. `renderAsync()` is deprecated and does not mean queued
GPU work has completed. Avoid copying the upstream helper's existence checks.
The plain ThreeCanvas manual renderer also acknowledges a draw synchronously;
that is not an asynchronous WebGPU barrier. Validate any custom bridge separately.

Required experiment: frame zero, material changes, a nonzero frame from a fresh
page, reverse seeks, repeated frame, worker concurrency and device failure.
The stable local demo validates WebGL; it must not be reported as a GPU-kernel test.

Sources: [rayBlock inspected code](source-attribution.md#remotion-webgpu),
[Three renderer](https://threejs.org/docs/pages/Renderer.html),
[WebGPURenderer](https://threejs.org/docs/pages/WebGPURenderer.html),
[TSL reference](https://github.com/mrdoob/three.js/wiki/Three.js-Shading-Language).
