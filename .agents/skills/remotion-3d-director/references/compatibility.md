# Compatibility and source selection

## Current VFXLens baseline

Inspected 2026-11-15: Remotion / `@remotion/three` 4.0.543, React 19.3.1,
R3F 9.8.2, Three 0.187.0, GSAP 3.15.1 and postprocessing 6.39.6. The lockfile and
installed package are authoritative for a later run. No dependencies were added
for this skill. Drei and the React postprocessing wrapper used by some sources
are not declared here; adapt with existing APIs or justify a scoped installation.

| Path | Status and required evidence |
| --- | --- |
| Frame-driven R3F/WebGL through ThreeCanvas | Baseline; local demo/render/seek evidence must be checked separately from TypeScript |
| GSAP | Paused evaluator with explicit time seeking; test reverse seeks and teardown |
| TSL material graphs | Exports can be checked locally; needs a compatible renderer and actual shader/render test |
| Native WebGPU compute | Experimental per backend/driver; own initialization, queue barrier and seek-safe state |
| Physics/fluids/destruction | Bake or deterministic checkpoint replay; live simulation is not an arbitrary-frame export path |
| Cloud generation/render/TTS | Not enabled by skill installation; preserve task-specific authorization and cost boundaries |

Version-specific findings: Three r187 `waitForGPU()` is a removed-method stub;
`renderAsync()` is deprecated, and `computeAsync()` does not await GPU completion.
R3F's old PCFSoft shadow default also differs from r187. Remotion ThreeCanvas's
manual draw scheduling is synchronous; do not call it a native WebGPU barrier.
Read [WebGPU](webgpu-shaders.md) and [camera/look](cinematic-camera.md) before porting.

## How sources are ranked

Priority is a task-specific adoption judgment, not a benchmark or popularity
score. **A** = directly useful pattern with a clear adaptation; **B** = useful
specialized branch needing more work; **C** = inspiration/discovery rather than a
drop-in renderer. Technical evidence is source inspection. Visual evidence is
listed separately: implementation/readme promises are not viewed demo quality.
No upstream application was installed or fully rendered during this research.

| Source | Priority | Technical/reuse assessment | Visual evidence | Fit/adaptation |
| --- | --- | --- | --- | --- |
| remotionshorts | A directing/world architecture | Strong shot/world/lifecycle separation and explicit QA; license absent prevents code/asset transplant | Source/shader structure inspected; upstream film not independently rendered | Closest package generation to local stack; remove forced drift and validate capture |
| explainer-3d | A explainers | Small meaningful components and frame paths; avoid allocation/jitter issues | Composition code inspected; upstream output not judged | Older Three r173/Remotion 4.0.429; missing local wrappers; original implementation |
| facecammaxxing | A motion/directing | Seekable GSAP, beat evidence and compositing lanes; heuristic matte limits | Effects/docs inspected; creator-signature looks are not a reusable house style | Older Three r179/Fiber9.3; use installed APIs, preserve licenses |
| remotion-webGPU | B experimental VFX | Strong analytical TSL examples; simulations/sync helpers need correction | Node graphs inspected; no native GPU render certification | Written for Three r178; adapt to r187 readiness/removal changes |
| motion-tools-and-skills | A methodology / C runtime reuse | Useful shot cards/choreography/QA across differently licensed packages | Examples/reference cards inspected; visual quality not benchmarked | Mixed frameworks/capture harnesses; extract decisions, not dependency trees |

Attribution, exact SHAs, licenses and inspected paths: [source-attribution](source-attribution.md).

## Fifteen additional source selections

Ranks below remain inside each source audit (directing / component discovery /
modeling and VFX); they are technical or reuse-fit decisions, not a shared
benchmark. None has an independently reviewed rendered output. The detailed
commit, license and inspected-file ledger is in [source attribution](source-attribution.md).

| Source (pinned commit) | Rank | Compatibility status and decision |
| --- | --- | --- |
| [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft/tree/6700db2ba80572ebc777b99d72049679fed9840c) `6700db2` | Directing 1/5 | Remotion recipes in its own architecture; use shot intent/choreography, not components or numeric defaults. |
| [cinecode](https://github.com/sarpstar/cinecode/tree/c8a3e7552699360a2b0142c9620882af2069eedb) `c8a3e75` | Directing 4/5 | Standalone Three camera helper and user-gated workflow; adapt story prompts only. |
| [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6) `3a7132b` | Directing 5/5 | Own HTML/Canvas/Three renderer invokes `render(t)`; readiness is explicit, but determinism is delegated to scene code. Not a Remotion adapter. Docs have CC-BY-NC terms. |
| [claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts/tree/e3b817b6afc6cd413466d43f11ba31209e034bbf) `e3b817b` | Directing 3/5 | Time-derived TS scene math and separate Python cue mirror; good model, but duplicate constants can drift. No bridge to local renderer verified. |
| [cinetic](https://github.com/Leonxlnx/cinetic/tree/f4bbfc844877891fe92279d47b7874fb44d485ae) `f4bbfc8` | Directing 1/5 | Remotion pipeline has resumable chunks and conditional audio/spec gates; substantial shell system and checks are not a VFXLens integration or visual approval. |
| [Remocn](https://github.com/Remocn/remocn/tree/1d15141a76d06ad469faf31d7b12f8c21f772489) `1d15141` | Components 1/4 | Best small component candidate; upstream Remotion 4.0.542 is close to local 4.0.543 but untested; verify each component's dependency list. |
| [motion-skills](https://github.com/iart-ai/motion-skills/tree/9b9ce041932da787cc856d4cdf23afb6cd13d4bf) `9b9ce04` | Components 1/4 (workflow) | Pack hub and POSIX verification helpers; reuse review discipline, not scripts or missing pack code. |
| [React Bits](https://github.com/DavidHDev/react-bits/tree/cf2801031f07f53d4684e65b961bde7c2e2a6921) `cf28010` | Components 2/4 | Ballpit/DotGrid use RAF and mutable state; rewrite analytically or bake. Three 0.180 / R3F 9.3 differ from local; MIT + Commons Clause restricts redistribution. |
| [rea-video](https://github.com/JuneYaooo/rea-video/tree/ebe853e330d63719a1f91754f789647c515eac19) `ebe853e` | Reference analysis 1/4 | Read-only review ideas and VFR locators transfer; its ASR/VLM/schema are separate and may download models or use configured providers. |
| [img2threejs](https://github.com/img2threejs/img2threejs/tree/0c0c49bc168e648dbaf9c8c080474de0b3a941b6) `0c0c49b` | Modeling 1/6 | Procedural image-based model workflow and confidence limits; no model renderer or asset pipeline adopted. |
| [teardown](https://github.com/elvarofficial/teardown/tree/a91262ac1109051e014662d42ecb0b7bc1f113b1) `a91262a` | Modeling 2/6 | Pure `render(t)`/mechanism separation is portable as a principle; standalone HTML/capture runtime is not. |
| [threejs-skills](https://github.com/CloudAI-X/threejs-skills/tree/0e181866f095b5f06d005133876e926515390d95) `0e18186` | Modeling 3/6 | Useful API lookup near local versions (Three r186 vs r187); convert `useFrame(delta)` examples to Remotion frame evaluation; Drei is absent. |
| [Stylized Components](https://github.com/cortiz2894/stylized-components/tree/1cece0a296b29299d1380c34feb5c158b2f04500) `1cece0a` | Modeling 4/6 | Seeded scatter concept transfers; its Three 0.182 WebGL `onBeforeCompile` shader and time-driven dust are not direct TSL/seekable code. |
| [Plume](https://github.com/travisdmathis/plume/tree/7ec1d66667a16b36d423df49c5a1189b9837edd4) `7ec1d66` | Modeling 5/6 | Packed storage architecture only; pre-1.0 WebGPU-only, no Remotion capture lifecycle verified. |
| [Three VFX](https://github.com/mustache-dev/Three-VFX/tree/c5533097adbccf22b4701f2f2527fb2fec951bd1) `c553309` | Modeling 6/6 | R3F wrapper uses asynchronous stateful delta updates; not seekable as-is. README CPU fallback was not tested. |

All fifteen were inspected from pinned source/docs; no demos were executed or
visually inspected. Do not assign visual quality from README images, repository
rank, API shape, or source sophistication. Use the relevant focused guide and
verify the selected technique with a local representative render.

## Local validation scope

The representative composition is `DirectorSkillDemo` in
[`studio/src/director/DirectorDemo.tsx`](../../../../studio/src/director/DirectorDemo.tsx):
silent 1280×720, 30fps, 120 frames, a lit product, camera motion and seeded
analytical instancing. Outputs/check reports stay ignored under
`local/setup/director-skill-demo/`. Only actual completed checks may be claimed;
see that evidence and [QA instructions](rendering-and-qa.md).

That example does not certify native WebGPU, upstream asset/model pipelines,
all component imports, character animation, final narration quality or the
unfinished Nvidia film. Test the selected branch on each production's real assets.
