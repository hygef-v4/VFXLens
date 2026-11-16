# Glow, Color, and Bokeh

**Purpose:** Control highlight bloom, color remapping/tinting, and defocus blur as independent, modular stages. No single numeric preset fits all footage; see [Takt Op, Section 4](../../case-studies/takt-op.md#4-glow-color-and-bokeh) for an example where keyframes fall outside a layer's active `in`/`out` trim.

## Proposed Recreation Workflow

1. Evaluate the input footage's luminance range, color palette, and highlight detail that must be preserved.
2. Dial in glow independently first, checking threshold, radius, and intensity for the specific tool in use.
3. Add color remapping/tinting and bokeh/defocus blur as separate steps; compare stacking orders when the visual interaction changes.
4. When pulsing glow or blur on an action beat, keyframe a clear envelope and verify that the keys lie inside the layer's visible `in`/`out` span.
5. Compare before and after on the same frame, checking skin tones, bright whites, typography, and silhouettes.

## Key Distinctions

A bokeh video overlay is a pre-rendered asset composited on top of the shot, whereas a bokeh/DOF effect processes the underlying image pixels according to its blur parameters. Glow does not replace exposure control, and a 2D blur does not automatically generate a 3D depth map. Color bit depth (`8-bpc` vs. `16/32-bpc`), working color space, and input highlight levels strongly affect bloom behavior—record them when documenting verification.

**Cross-References:** [White Ferrari](../../case-studies/white-ferrari.md), [Chal7z: synchronized bokeh and gamma](../../case-studies/chal7z-presets.md). **Used In:** [Dreamy Style](../../styles/dreamy.md), [Overlays](../../resources/overlays.md). **Tools:** [Render Effects](../../tools/render-effects.md).
