# Standard — Bouncing Text, Stickers and Layered Transitions

Companion to the [editing handbook](../README.md), read on 2026-11-04. Parameters are sourced from the JSON; visual intent is inferred unless marked as an image observation. AE was not rendered to isolate effects.

## Source and Scope

- Project: `evidence:standard-01`.
- Project JSON/report: `evidence:standard-02`.
- Project SHA-256: `8810ab59251ceb7c5c0399b2723ad78e7a34f247695d3d928ce5b4e16fd8f6f1`; it matched after the analysis. The analyzed source video kept its hash as well.
- AE `22.0x111`, 8-bit colour, 17 compositions, 137 layers, 5 expression entries extracted.
- `cc2 standard.mp4` in `(Footage)`: 1650×1080, 24 fps, 6.916667 s; all 166 frames analyzed. Results in `evidence:standard-03`.
- The contact sheet shows a purple background, paper/portrait photos, collage letters, a sun, clouds, diamonds and icons, with layout/zoom/rotation changes between frames. This is an observation of the prerender; the effect behind each change is not identified.
- 50 assets are missing at their stored paths; 27 basename matches exist in `(Footage)`. Content and relinking are not verified. An older collect report lists one missing item and collected only selected comps; that does not mean the whole project has its footage now.
- Times below are per comp. Two comps are named `bg`: item 18 is 1650×1080 with 1 layer; item 857 is 1920×1080 with 4 layers. Look them up by item_id and structure, never merge them by name.

## 1. Per-Character Bouncing Text with an Expression Selector

**Source:** `trans`, layer 11 `i got ` and `trans 2`, layer 11 `Kool-Aid`. Both text layers are enabled; Animator 1 has an enabled Expression Selector Amount.

The expression stores the constants `freq=2.5`, `decay=4`, `duration=0.15`; the delay is `textIndex * thisComp.frameDuration * 1`. It computes `t = time - (inPoint + retard)`; before `duration` it goes linearly from `[100,100,100]` to `[0,0,0]`; after that it uses a sine oscillation divided by `exp(decay*(t-duration))` with `w=freq*2π`.

**Animator properties read:** Position `[0,41,0]`, Scale `[0,0,100]`, Rotation `12`. Amount scales this combination of animator properties; it is not directly a character's final position or scale.

**Takeaway:** one expression serves many characters, offset by one frame per textIndex, then oscillating with decay. textIndex starts at 1, so the first character is also one frame behind inPoint, not zero delay.

At 24 fps one frame is about 0.041667 s. `duration=0.15` is expression time, not a whole number of frames. The expression source was not executed; selector mode/combination, perceived easing and the font on this machine were not checked. A rebuild must carry the animator properties and the selector, not only Amount.

## 2. Sticker Outline from an Expanded Matte and Re-Composited Image

**Source:** `trans`, layer 4 `discord`: layer and effects enabled, in this order:

`Simple Choker → Fill → CC Composite → S_DropShadow`

| Parameter | Stored value |
| --- | --- |
| Simple Choker / Choke Matte | -48.5 |
| Fill / Color | [1,1,1,1] |
| Fill / Opacity | 1 |
| CC Composite / Opacity | 100 |
| CC Composite / Composite Original | enum 3, name not decoded |
| CC Composite / RGB Only | 1 |

**Inference for a test build:** expand the matte, fill it white, composite the original image back and add a shadow to separate the layer. Confirm the alpha and the name of the Composite Original mode before calling this a complete outline preset.

**Variant:** `cat cig Comp 1`, layer 2 `saitama`: order `Fill → Simple Choker → CC Composite`, Choke Matte `-37.2`; do not swap it with the stack above and assume the same result. `trans` layers 5/6 have the same stack as layer 4, but identical values are not assumed without reading them.

## 3. Shot-Opening Transition: Fast Warp with Decaying Blur/Mosaic/Brightness

**Source:** `effects`, 1650×1080, 24 fps, 6.916667 s. The layers below are enabled adjustment layers.

| Layer | Visible range | Effect and keyframes |
| --- | --- | --- |
| 7 `warp` | 0–0.166667 | Warp Bend: 0 → 45; 0.125 → 0 |
| 6 `blur` | 0–0.291667 | Bokeh Blur Radius: 0 → 20; 0.291667 → 0; Mosaic Pixelate X: 25 → 0 at the same times; Brightness: 60 → 0 at the same times |
| 3 `blur 2` | 3.458333–3.75 | The same three curves 20/25/60 to 0 at 3.75 |

In the layer 6 row, `0 → 20` means the value is 20 at 0 s, not an animation from 0 up to 20. Each effect has two keys with BEZIER in/out.

**Blur layer order:** Bokeh → BCC Mosaic (`Boris3Pixelate`) → Brightness & Contrast. The warp layers contain Motion Tile but the **effect is disabled**; leave it out of the active stack.

**Takeaway:** the warp finishes in about three frames while blur/pixelation/brightness decay over about seven. Envelopes of different lengths join a fast distortion accent to a longer return to a clear image.

**Limits:** the last key of layers 6/3 coincides with the out point, so do not claim the 0 value is shown for a whole frame before the layer ends. Warp style/axis and all static values need checking. The prerender `cc2 standard.mp4` on layer 8 is an input to the `effects` comp, so watching that video cannot verify the effects applied after it.

## 4. Time-Offset RGB with Threshold, Not Just Position-Offset RGB

**Source:** `fx`, adjustment layer 7, in/out 0–1.666667; `S_TimeWarpRGB → CC Threshold RGB`, both enabled.

- S_TimeWarpRGB: Red Shift Frames `1`, Green `0`, Blue `-1`.
- CC Threshold RGB: Red/Green/Blue Threshold all `0.5`.
- Blend w. Original: `0.041667 → 0`, `1.208333 → 1`, BEZIER.
- Layer 2 is the next variant, in/out 1.666667–3.458333; Blend w. Original `1.708333 → 0`, `2.875 → 1`.

**Takeaway:** sampling the channels from different frames can create motion-dependent colour fringes; this differs from shifting R/G/B in image coordinates. Whether a positive shift samples the future or the past in this plugin is not verified, and its contribution was not rendered separately.

**Inferred application:** combine a threshold level that returns to the original with a time-based colour effect. `record.mp4` was not viewed, so the input content of this section is not described.

## 5. Clock Wipe for Decorations

**Source:** `trans`, layer 16 `flower`; in/out 2.458333–3.458333, layer and effect enabled. Stack `S_WipeClock → S_DropShadow`.

Wipe Percent: `2.666667 → 100`, `3.0 → 0`, BEZIER — about eight frames. This wipe reveals one decoration layer, not the whole composition. Read centre, direction/reverse and softness to describe the reveal exactly.

## 6. Time-Based Texture and Loops — Stored in the Source, Check the Render Path

- `bg` item 857, layer 2 `PYn.gif`: enabled Time Remap expression `loopOutDuration(type = "cycle", duration = 0)`.
- Same comp, layer 3 `fx`: Roughen Edges / Random Seed has an enabled expression `time*9`.
- `got standard`, layer 5 `turbulent`: Random Seed expression `time*7`, but the **layer is disabled**. Layer 6, referencing `bg`, is also off.

**Takeaway:** inspect property expressions, not just keyframe counts, to find loops or textures that change over time. `time*9` drives the seed; it is not claimed to equal exactly nine new random states per second without checking the plugin. Do not describe the two expressions in `bg` as contributing to the final output while the parent path is disabled.

## 7. Two Collage Versions on the Same Time Frame

`trans` and `trans 2` both have 42 layers, 1650×1080, 24 fps, 3.458333 s long. Matching positions swap content, e.g. layer 11 `i got ` ↔ `Kool-Aid`, layer 10 `Standards` ↔ `Jammer`; both layer 11s use the same bouncing-text expression and the animator properties read in section 1.

**Reuse lesson:** separate the timing/animation frame from the text/asset content to make variants. Do not assume all 42 layers share transforms or parameters just because the counts match.

**Important state:** in the `transition` comp, the two layers referencing `trans` and `trans 2` are both off. In `effects`, the `cc2 standard.mp4` video is on and the `transition` layer is off. In `got standard`, the video `got standard  prefinal.mp4` is on, with enabled Deep Glow and Sharpen/Unsharp Mask/Looks/Flicker adjustments above it; the prefinal video was not found in the supplied folder. Do not treat the accompanying 6.9 s MP4 as the complete 18.29 s output of this comp.

## Next Test Builds

Choose one technique, take the full source alpha/matte, effect settings, animator/selector or time dependencies from the JSON, and build it in a new authorized project. These notes are sourced structure and test hypotheses; promote one to a verified recipe only after a comparison preview. Do not open or modify the original project or execute embedded expressions to explore.

## Reading the Source and Reuse

This article keeps measurements and references from the recorded analysis; the project, evidence images and private reports are not distributed with the library. `evidence:` codes are source identifiers, not files needed to read the article. The source holder resolves them in local records; other contributors record their own sources and verification level. See [evidence conventions](../foundations/evidence-and-validation.md).
