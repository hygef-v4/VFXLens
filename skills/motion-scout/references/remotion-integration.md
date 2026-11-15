# Handoff and optional build

Scout owns discovery, comparison, evidence, selection and adaptation strategy.
Director owns storyboard, scene implementation, compositing, render, visual
review and delivery. Use the [structured handoff](report-template.md) with
`request_mode`, source/commit/license/dependencies, visual evidence and verification
states. Keep a small complementary selection; technology discovery is not a reason
to replace VFXLens's stack or import complete templates.

In VFXLens, detect and read the existing
[Remotion 3D Director](../../../.agents/skills/remotion-3d-director/SKILL.md) when
implementation is authorized. Its location is project-specific; do not assume
another checkout has it. If absent, hand off to the existing production workflow
with the same evidence and explain the missing specialized guidance.

The direction is one-way: Scout report → production checkpoint → Director build.
Director can consume the handoff without invoking Scout again. A concrete new
research question can trigger a separate bounded research pass; do not recurse
until every candidate has been inspected or keep a background process running.

For each selected unit:

1. Compare its manifest/API with the actual lockfile. Record missing wrappers,
   shader backend, assets/fonts/models and peer dependencies; close versions are
   not compatibility proof.
2. Identify the render clock. Translate RAF/delta/GSAP playback/CSS motion into
   absolute Remotion frame evaluation. Seeded initial particles still need
   analytical evaluation, baking or checkpoint replay when stateful.
3. Define lifecycle and capture readiness: stable resources, disposal ownership,
   async assets/shaders/GPU submission, first frame, reverse seek and concurrency.
4. Define the smallest representative test and fallback before integration.
   Preserve the visual job even if native GPU is unavailable.
5. In build mode only, review the actual import/install/diff and permission scope,
   implement, typecheck, render and inspect. Report changes and unverified checks.

Research-only stops before step 5. It may recommend commands but must not execute
package/component installers or mutate studio code/locks. The source research and
handoff should say explicitly whether a component was merely read, visually
observed, compiled, rendered locally or validated at the delivery settings.
