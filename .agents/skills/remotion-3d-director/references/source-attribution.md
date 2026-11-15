# Inspected sources and reuse boundaries

Research date: 2026-11-15. Repositories were sparse-cloned outside VFXLens and
resolved to the full commit IDs below. Inspection used README, documentation,
licenses, agent skills and real implementation files. Upstream applications,
installers and scripts were not executed; no source assets were imported into
this skill. Examples/helper/demo here are independently written. Public source
availability does not establish reuse rights or successful rendering.

## remotion-webGPU

- Repository: [rayBlock/remotion-webGPU](https://github.com/rayBlock/remotion-webGPU).
- Commit: `8da62da1acd4e9990263d6e4961c6b1348be3497`.
- License: [MIT, copyright 2025 rayBlock](https://github.com/rayBlock/remotion-webGPU/blob/8da62da1acd4e9990263d6e4961c6b1348be3497/LICENSE).
- Inspected: `README.md`, `package.json`, `TSL_REFERENCE.md`, renderer/config,
  `WebGPUCanvas`, `WebGPUSync`, backend detection, TSL hash helper,
  `HolographicRibbon`, `MorphingShapes`, `SpiralGalaxy`, `BoidsScene`, `SPHFluidScene`.
- Adopted concepts: memoized node graphs, explicit time uniforms, instanced
  analytical morphs, shader warmup and a GPU-completion capture barrier.
- Rejected as production guarantees: random/stateful boid/fluid initialization,
  unawaited compute effects, wall-clock advance as animation time, error swallowing
  and old `waitForGPU()` handling. See [WebGPU guidance](webgpu-shaders.md).
- Code evidence: [canvas](https://github.com/rayBlock/remotion-webGPU/blob/8da62da1acd4e9990263d6e4961c6b1348be3497/src/components/Canvas/WebGPUCanvas.tsx),
  [morph](https://github.com/rayBlock/remotion-webGPU/blob/8da62da1acd4e9990263d6e4961c6b1348be3497/src/scenes/particleforge/MorphingShapes.tsx),
  [boids](https://github.com/rayBlock/remotion-webGPU/blob/8da62da1acd4e9990263d6e4961c6b1348be3497/src/scenes/BoidsScene.tsx).

## remotionshorts

- Repository: [4mJ0k3r/remotionshorts](https://github.com/4mJ0k3r/remotionshorts).
- Commit: `60135cf44fffdd2c6cecc68b63ee90f69e86b377`.
- License: **no project license found** in the tracked tree or inspected root
  manifests/docs. Third-party-looking GLB/media rights were not established.
  Source/asset copying is not authorized by this research; conceptual summaries
  and original implementations are used instead.
- Inspected: `PROJECT_MANIFEST.md`, engine `ShortPlayer.tsx`, `camera.ts`, `pool.ts`,
  ink/lensblur shaders, coaster `story.ts`/`world.ts`/`lights.ts`, authoring skill/cel
  contract, still/video scripts and `short_qa.py`.
- Adopted concepts: a world with frame-addressable update/dispose, shot-specific
  camera/focus/light data, ordered postprocessing, texture ownership and observable
  QA. Do not port the substantial lens shaders or specific assets.
- Rejected defaults: forced camera drift, universal FOV/motion floors, renderer
  call-count checks as proof of a correct frame, and numeric QA as aesthetic approval.
- Evidence: [shared player](https://github.com/4mJ0k3r/remotionshorts/blob/60135cf44fffdd2c6cecc68b63ee90f69e86b377/src/engine/ShortPlayer.tsx),
  [camera](https://github.com/4mJ0k3r/remotionshorts/blob/60135cf44fffdd2c6cecc68b63ee90f69e86b377/src/engine/camera.ts),
  [world](https://github.com/4mJ0k3r/remotionshorts/blob/60135cf44fffdd2c6cecc68b63ee90f69e86b377/src/videos/coaster/world.ts),
  [QA](https://github.com/4mJ0k3r/remotionshorts/blob/60135cf44fffdd2c6cecc68b63ee90f69e86b377/scripts/short_qa.py).

## explainer-3d

- Repository: [htekdev/explainer-3d](https://github.com/htekdev/explainer-3d).
- Commit: `033344ec754e2ad36c171167028e460e0d1545f7`.
- License evidence: [README declares MIT — Hector Flores Rocha](https://github.com/htekdev/explainer-3d/blob/033344ec754e2ad36c171167028e460e0d1545f7/README.md#-license);
  no standalone license text was found in the tracked snapshot. Exact reuse terms
  need confirmation before copying substantial code; none was copied here.
- Inspected: `Scene3D`, `AnimatedCamera`, `ParticleField`, `DataFlow`, `TokenStream`,
  scene/time hooks, RNG, AIDevFlow composition, renderer registry/local/Lambda paths,
  tests and CI workflows.
- Adopted concepts: small named explanatory entities, explicit camera keys, seeded
  base attributes, absolute-time flow, and a composition/render contract.
- Adaptations: stable buffers instead of per-frame allocation/jitter reseeding;
  Remotion-compatible camera scheduling; no implicit addition of Drei, React
  postprocessing wrappers or cloud rendering. Use shell-free render arguments.
- Evidence: [camera](https://github.com/htekdev/explainer-3d/blob/033344ec754e2ad36c171167028e460e0d1545f7/src/components/AnimatedCamera.tsx),
  [flow](https://github.com/htekdev/explainer-3d/blob/033344ec754e2ad36c171167028e460e0d1545f7/src/components/DataFlow.tsx),
  [composition](https://github.com/htekdev/explainer-3d/blob/033344ec754e2ad36c171167028e460e0d1545f7/src/compositions/AIDevFlow/AIDevFlow.tsx).

## facecammaxxing

- Repository: [aaksa/facecammaxxing](https://github.com/aaksa/facecammaxxing).
- Commit: `a9976a70b02c8b60bbb7ebf5e055271b79b12db4`.
- License: [MIT includes repository and upstream claude-video-effects notices](https://github.com/aaksa/facecammaxxing/blob/a9976a70b02c8b60bbb7ebf5e055271b79b12db4/LICENSE).
  Keep both notices for substantial copied portions; model/media rights are
  separate (YuNet MIT, MediaPipe Apache-2.0, downloaded RVM GPL-3.0 per its notice).
- Inspected: `SKILL.md`, director/motion rules, stage/layer core, layout helpers,
  paused GSAP timeline, Three prop helpers, chart and caption effects, package pins.
- Adopted concepts: evidence-backed beats, one focal accent, object-led handoffs,
  layered compositing, paused timeline seeking and reserved caption layout.
- Rejected assumptions: oval masks as semantic mattes, spoken-cue offsets as
  automatic caption behavior, and intentional light flicker as a house default.
- Evidence: [director](https://github.com/aaksa/facecammaxxing/blob/a9976a70b02c8b60bbb7ebf5e055271b79b12db4/docs/director.md),
  [seekable core](https://github.com/aaksa/facecammaxxing/blob/a9976a70b02c8b60bbb7ebf5e055271b79b12db4/remotion/src/lib/core.ts),
  [captions](https://github.com/aaksa/facecammaxxing/blob/a9976a70b02c8b60bbb7ebf5e055271b79b12db4/remotion/src/effects/reels.tsx).

## motion-tools-and-skills

- Repository: [VisualxIntelligence/motion-tools-and-skills](https://github.com/VisualxIntelligence/motion-tools-and-skills).
- Commit: `b72d62c5ee75743a04279607f0a75e8c9087652a`.
- License: [root MIT, copyright 2026 Ahmed Albadri](https://github.com/VisualxIntelligence/motion-tools-and-skills/blob/b72d62c5ee75743a04279607f0a75e8c9087652a/LICENSE).
  Included folders carry separate terms: adapted video-shotcraft is Apache-2.0,
  copyright Wei Yihao; Emil Kowalski/iart/awwwards material includes MIT notices.
  Root licensing does not override embedded licenses or media rights.
- Inspected: source/license notes, shotcraft pipeline/camera/QA cards, motion
  helpers, choreography guide, motion-study notes, smoke/capture and diorama scripts.
- Adopted concepts: styleframe before replication, intent/parameter/failure shot
  cards, lead/support choreography, finite-difference/delayed frame evaluation,
  and contact-sheet/playback review. No manuals or starter tree were copied.
- Rejected defaults: fixed recipe values as universal rules, live-time browser
  capture replacing Remotion random access, and an upstream `useFrame` camera rig
  as a Remotion animation pattern.
- Evidence: [pipeline](https://github.com/VisualxIntelligence/motion-tools-and-skills/blob/b72d62c5ee75743a04279607f0a75e8c9087652a/skills/video-shotcraft/references/pipeline.md),
  [choreography](https://github.com/VisualxIntelligence/motion-tools-and-skills/blob/b72d62c5ee75743a04279607f0a75e8c9087652a/docs/guides/emil-kowalski/choreograph/SKILL.md),
  [sources](https://github.com/VisualxIntelligence/motion-tools-and-skills/blob/b72d62c5ee75743a04279607f0a75e8c9087652a/SOURCES.md).

## Official and local compatibility evidence

- [Remotion ThreeCanvas](https://www.remotion.dev/docs/three-canvas),
  [capture holds](https://www.remotion.dev/docs/delay-render),
  [flickering/determinism](https://www.remotion.dev/docs/flickering).
- [Three WebGPURenderer](https://threejs.org/docs/pages/WebGPURenderer.html),
  [TSL](https://github.com/mrdoob/three.js/wiki/Three.js-Shading-Language),
  [renderer API](https://threejs.org/docs/pages/Renderer.html).
- [R3F canvas](https://r3f.docs.pmnd.rs/api/canvas),
  [object ownership](https://r3f.docs.pmnd.rs/api/objects).
- [OpenAI repo-local skills and progressive disclosure](https://developers.openai.com/blog/skills-agents-sdk).
- Installed code was also inspected: `studio/node_modules/@remotion/three/dist/cjs/ThreeCanvas.js`,
  Three `src/renderers/common/Renderer.js`, WebGPU backend/types and Remotion GL
  option code. These paths are installed evidence, not committed dependencies.

See [compatibility and ranking](compatibility.md) for adoption priority and the
distinction between static inspection, observed demo images and executed tests.

## Additional upgrade sources (15)

These sources extend the original five-source audit above. Ranks below are
within the named directing, component-discovery, or modeling/VFX audit in
`local/setup/director-skill-demo/`; they are not visual-quality rankings.
“Visual: unreviewed” means no rendered demo was inspected. License statements
are from each pinned checkout; third-party media may carry separate terms.

| Source and pinned commit | License | Inspected evidence | Technical/reuse rank and decision |
| --- | --- | --- | --- |
| [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft/tree/6700db2ba80572ebc777b99d72049679fed9840c) `6700db2ba80572ebc777b99d72049679fed9840c` | Apache-2.0 | `references/pipeline.md`; `references/shots/camera/space-camera-moves.md`; `demos/camera/space-camera-moves/ExplodedView.tsx` | Directing **1/5**: strong purpose-to-choreography example; recipe is placeholder-tuned and needs real-asset review. Visual: unreviewed. |
| [cinecode](https://github.com/sarpstar/cinecode/tree/c8a3e7552699360a2b0142c9620882af2069eedb) `c8a3e7552699360a2b0142c9620882af2069eedb` | MIT | `SKILL.md`; `references/craft.md`; `references/camera-moves.md`; `starter/camera.mjs` | Directing **4/5**: treatment/review prompts transfer; user gates and standalone Three runtime do not. Visual: unreviewed. |
| [lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6) `3a7132b996be0241c1ea0ab180d519f06e6f10b6` | File-specific: code MIT; Markdown CC-BY-NC-4.0; images/media and third-party material have separate terms (`REUSE.toml`) | `DIRECTOR.md`; `TECHNIQUE.md`; `core/render/video.mjs`; `core/render/page.mjs` | Directing **5/5**: story/timeline principles transfer. Renderer calls `render(t)` and gates READY, but is its own HTML/Canvas/Three pipeline. No prose/assets copied. Visual: unreviewed. |
| [claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts/tree/e3b817b6afc6cd413466d43f11ba31209e034bbf) `e3b817b6afc6cd413466d43f11ba31209e034bbf` | MIT | `SKILL.md`; `templates/bridge/story.ts`; `templates/audio/timeline.py` | Directing **3/5**: pure time-derived story choreography; separate TS/Python copies can drift and are not an adapter. Visual: unreviewed. |
| [cinetic](https://github.com/Leonxlnx/cinetic/tree/f4bbfc844877891fe92279d47b7874fb44d485ae) `f4bbfc844877891fe92279d47b7874fb44d485ae` | MIT | `skills/cinetic/references/concept-and-story.md`; `skills/cinetic/scripts/render.sh`; `skills/cinetic/scripts/check-sync.py` | Directing **1/5**: useful treatment and concrete conditional render/audio gates; substantial renderer/check system is not VFXLens sign-off. Visual: unreviewed. |
| [Remocn](https://github.com/Remocn/remocn/tree/1d15141a76d06ad469faf31d7b12f8c21f772489) `1d15141a76d06ad469faf31d7b12f8c21f772489` | MIT | `plugins/remocn/skills/remocn/SKILL.md`; `registry/remocn/typewriter/index.tsx`; `registry/remocn/whip-pan/index.tsx` | Component **1/4**: best small motion candidate; upstream Remotion 4.0.542 vs local 4.0.543 remains untested. Visual: unreviewed (poster unavailable in sparse checkout). |
| [motion-skills](https://github.com/iart-ai/motion-skills/tree/9b9ce041932da787cc856d4cdf23afb6cd13d4bf) `9b9ce041932da787cc856d4cdf23afb6cd13d4bf` | Root MIT; embedded packages may retain their own terms | `README.md`; `tools/verify/README.md`; tools tree | Component workflow **1/4**: useful deliver/verify concept; hub rather than complete skill source, POSIX scripts not used in Windows workflow. Visual: unreviewed. |
| [React Bits](https://github.com/DavidHDev/react-bits/tree/cf2801031f07f53d4684e65b961bde7c2e2a6921) `cf2801031f07f53d4684e65b961bde7c2e2a6921` | MIT + Commons Clause | `src/content/Backgrounds/Ballpit/Ballpit.jsx`; `src/content/Backgrounds/DotGrid/DotGrid.jsx`; package manifest | Component **2/4**: visual/mechanical reference only; mutable RAF/`Math.random` conflicts with arbitrary-frame seeking; restrictive redistribution clause. Visual: unreviewed. |
| [rea-video](https://github.com/JuneYaooo/rea-video/tree/ebe853e330d63719a1f91754f789647c515eac19) `ebe853e330d63719a1f91754f789647c515eac19` | Apache-2.0; NOTICE read | `skills/rea-video/SKILL.md`; `docs/videomd.md`; `rea_video/{cli,shots,speech,probe}.py` | Reference-analysis **1/4**: two-stage review and VFR locators transfer; separate schema/ASR/VLM stack not integrated. Visual: unreviewed. |
| [img2threejs](https://github.com/img2threejs/img2threejs/tree/0c0c49bc168e648dbaf9c8c080474de0b3a941b6) `0c0c49bc168e648dbaf9c8c080474de0b3a941b6` | Apache-2.0 | `grimoire/intake/validation_rubric.md`; `grimoire/character/reconstruction.md`; `grimoire/build/implicit_sdf_modeling.md` | Modeling/VFX **1/6**: strongest explicit image-to-model uncertainty and comparison workflow; not photogrammetry, no model render reviewed. |
| [threejs-skills](https://github.com/CloudAI-X/threejs-skills/tree/0e181866f095b5f06d005133876e926515390d95) `0e181866f095b5f06d005133876e926515390d95` | MIT | `skills/threejs-geometry/SKILL.md`; `skills/threejs-react-three-fiber/SKILL.md`; `skills/threejs-animation/SKILL.md`; `skills/threejs-performance/SKILL.md` | Modeling/VFX **3/6**: strong API lookup; Three r186, R3F 9.8, React 19 are close, but `useFrame(delta)`/Drei examples need adaptation. Visual: unreviewed. |
| [teardown](https://github.com/elvarofficial/teardown/tree/a91262ac1109051e014662d42ecb0b7bc1f113b1) `a91262ac1109051e014662d42ecb0b7bc1f113b1` | MIT | `README.md`; `SKILL.md` | Modeling/VFX **2/6**: useful pure `render(t)` and one-input/many-readouts principle; standalone HTML simulator, no frames reviewed. |
| [Three VFX](https://github.com/mustache-dev/Three-VFX/tree/c5533097adbccf22b4701f2f2527fb2fec951bd1) `c5533097adbccf22b4701f2f2527fb2fec951bd1` | MIT | `examples/r3f/src/Particles.tsx`; `packages/r3f-vfx/src/VFXParticles.tsx`; `packages/core-vfx/src/particle-system.ts`; shader update/spawn | Modeling/VFX **6/6**: broad particle implementation, but stock async stateful `useFrame(delta)` is not seekable; CPU fallback unverified. Visual: unreviewed. |
| [Plume](https://github.com/travisdmathis/plume/tree/7ec1d66667a16b36d423df49c5a1189b9837edd4) `7ec1d66667a16b36d423df49c5a1189b9837edd4` | MIT | `packages/plume/src/particle-buffer.ts`; `packages/plume/src/index.ts`; package README | Modeling/VFX **5/6**: packed storage/modules are an architecture reference; pre-1.0 WebGPU-only, no Remotion lifecycle or render validated. Visual: unreviewed. |
| [Stylized Components](https://github.com/cortiz2894/stylized-components/tree/1cece0a296b29299d1380c34feb5c158b2f04500) `1cece0a296b29299d1380c34feb5c158b2f04500` | MIT | `src/components/grassField/shaders/grassBlade.ts`; `src/components/grassField/utils/scatter.ts`; `src/components/godRaysScene/DustMotes.tsx` | Modeling/VFX **4/6**: seeded surface scatter transfers as a concept; Three 0.182/WebGL `onBeforeCompile` and time-driven dust are not direct TSL/seekable code. Visual: unreviewed. |

Ranks are within separate source audits and describe technical usefulness/reuse
fit, not popularity, performance, or image quality. No demo from these fifteen
sources was visually inspected or rendered in VFXLens. Detailed adaptation and
rejection guidance lives in [compatibility](compatibility.md) and the focused
references linked from [the skill](../SKILL.md).
