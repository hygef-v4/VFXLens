# Chromatic, Invert, and Displacement Transitions

**Purpose:** Combine spatial warp distortion with brief color/luminance state flips around a cut boundary. The steps below describe a proposed workflow; a statically extracted project example is documented in [Takt Op, Section 1](../../case-studies/takt-op.md#1-chromatic-invert-and-displacement-transition).

## Proposed Recreation Workflow

1. Choose the transition direction and the settling frame where the incoming shot stabilizes.
2. Configure the displacement map source, center/axis, and border wrapping mode. Shape the displacement envelope first.
3. Layer in directional or vector blur to bridge the motion across the cut; if a sharp visual punctuation is desired, insert a 1–3 frame `HOLD` invert pulse at the peak.
4. Check final exposure/color balance and inspect each effect stage individually in the stack.

## Controls and Dependencies

Displacement amount, map/channel selection, blur amount, luma/chroma inversion flags, keyframe interpolation (`HOLD` vs. continuous `LINEAR`/`BEZIER`), and effect stacking order all alter the final look. Spatial chromatic aberration plugins and temporal per-channel RGB frame shifts operate via distinct mechanisms.

## Verification and Common Pitfalls

Inspect the cut boundary, black border pull-in, mirrored edge reflections, faces/typography, and resting end state. Never copy pixel-based displacement amounts across different composition resolutions without rescaling. Keep the original source effect order as your baseline reference; the order in which you audition effects during setup does not replace the actual render stack order.

**Cross-References:** [Standard: warp and temporal RGB frame shift](../../case-studies/standard.md), [AE Notes: warp and scatter family](../../case-studies/ae-notes.md). **Resource:** [Overlays](../../resources/overlays.md). **Tools:** [Render Effects](../../tools/render-effects.md).
