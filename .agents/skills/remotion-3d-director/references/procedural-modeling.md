# Procedural modeling from image references

Use this when a shot needs a new prop, character, or stylized environment built
from supplied images. Keep it inside the director's existing [architecture](architecture.md),
shot contract, render checks, and [source attribution](source-attribution.md); this
reference adds a modeling workflow, not another renderer or project scaffold.

## Start with image evidence

1. Confirm the image depicts one sufficiently visible target, with a readable
   silhouette and visible major materials. Ask for more views when identity or
   hidden structure depends on them. A single view supports a camera-facing
   approximation; it does not reveal the unseen side, exact dimensions, rig, or
   manufacturing geometry.
2. Write a small quality contract before modeling: target style, shot distance,
   which silhouette/details must read, allowable approximation, and evidence
   needed to accept the result. Keep observed measurements, inferred structure,
   and creative choices distinct. Record confidence by region or component.
3. Block out the silhouette and largest masses first. Compare the same camera
   framing against the supplied image. Add only identity-defining components,
   material regions, and animation pivots the shot needs. Use primitives and
   custom geometry where they fit; a detailed shader or texture cannot repair a
   wrong outline.
4. Iterate by visible pass: structure, form, material, lighting, then shot use.
   Render the representative Remotion frame and inspect it next to the source.
   Reject a pass when a defining feature is wrong even if the rest looks polished.
5. Before reuse, check licensing for actual borrowed code and assets. Research
   repositories, screenshots, external tools, and model services are references;
   they are not dependencies or permission to send source images to a service.

## Choosing procedural detail

- Use primitive assemblies for clear hard-surface masses and low-detail stylized
  subjects. Give meaningful moving parts stable pivots and IDs.
- Use custom buffer geometry or a bounded implicit surface when separate
  primitives visibly fail at a welded silhouette. Keep resolution bounded and
  check normals, bounds, and export/runtime cost.
- For a humanoid from one view, measure head/body proportions and visible joint
  angles from that image. Hair clumps/cards and simplified cloth folds can match
  a stylized silhouette; strand-level hair, accurate anatomy, and hidden pose
  details need more views or a deliberately limited style target.
- Treat generated code as an approximation. Compare silhouette, proportion,
  visible details, material blocks, and camera match separately; report what was
  inferred and what remains unseen.

## What the inspected references contribute

`img2threejs` is the strongest workflow reference for staged image-to-code
sculpting: suitability checks, a component/detail inventory, per-pass visual
comparison, and explicit single-view confidence limits. Its claim is
reconstruction by procedural code, not photogrammetry or mesh extraction. It is
an external agent workflow with its own state and gates, so adopt the evidence
discipline rather than its harness or command sequence.

`threejs-skills` is a quick API lookup for geometry, materials, R3F, animation,
and performance. Its inspected material targets Three r186 and R3F 9.8 with
React 19, close to this studio's Three 0.187 / R3F 9.8.2 / React 19.3.1. Its
examples still include browser-driven `useFrame` animation, and the Drei
examples are not usable here unless that dependency is separately present.

`teardown` shows a useful split between pure mechanism math, geometry posing,
stage, and a `render(t)` function that can be sampled out of order. Its examples
are a custom standalone HTML simulator and capture kit, not a Remotion adapter.
Reuse the one-input-to-many-readouts idea and pure-time discipline inside the
existing scene; do not transplant its runtime.

No referenced demo frame or image was visually inspected for this guidance.
Repository demo listings and source are not visual approval of a new model.

## Provenance

- [img2threejs `SKILL.md`](https://github.com/img2threejs/img2threejs/blob/0c0c49bc168e648dbaf9c8c080474de0b3a941b6/SKILL.md), [image validation rubric](https://github.com/img2threejs/img2threejs/blob/0c0c49bc168e648dbaf9c8c080474de0b3a941b6/grimoire/intake/validation_rubric.md), [character reconstruction](https://github.com/img2threejs/img2threejs/blob/0c0c49bc168e648dbaf9c8c080474de0b3a941b6/grimoire/character/reconstruction.md), [implicit modeling limits](https://github.com/img2threejs/img2threejs/blob/0c0c49bc168e648dbaf9c8c080474de0b3a941b6/grimoire/build/implicit_sdf_modeling.md). Inspected at commit `0c0c49bc168e648dbaf9c8c080474de0b3a941b6`, Apache-2.0.
- [threejs-skills README](https://github.com/CloudAI-X/threejs-skills/blob/0e181866f095b5f06d005133876e926515390d95/README.md), [geometry](https://github.com/CloudAI-X/threejs-skills/blob/0e181866f095b5f06d005133876e926515390d95/skills/threejs-geometry/SKILL.md), [R3F](https://github.com/CloudAI-X/threejs-skills/blob/0e181866f095b5f06d005133876e926515390d95/skills/threejs-react-three-fiber/SKILL.md), [animation](https://github.com/CloudAI-X/threejs-skills/blob/0e181866f095b5f06d005133876e926515390d95/skills/threejs-animation/SKILL.md). Inspected at commit `0e181866f095b5f06d005133876e926515390d95`, MIT.
- [teardown README](https://github.com/elvarofficial/teardown/blob/a91262ac1109051e014662d42ecb0b7bc1f113b1/README.md), [skill and render contract](https://github.com/elvarofficial/teardown/blob/a91262ac1109051e014662d42ecb0b7bc1f113b1/SKILL.md). Inspected at commit `a91262ac1109051e014662d42ecb0b7bc1f113b1`, MIT.
