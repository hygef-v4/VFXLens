# The Less I Know the Better — Collage, Text and Camera

Companion to the [editing handbook](../README.md), read on 2026-11-04. It separates the structure/keyframes stored in the project from what is built through a prerender. No layer's contribution has been verified with an AE render.

## Source

- Project: `evidence:the-less-i-know-the-better-01`.
- Results: `evidence:the-less-i-know-the-better-02` and `project-report.md`.
- SHA-256: `a37042c63022661bcdb6d7fd6973f78900310d3b241f40a98b03ed43c8b48f34`; it matched when rechecked after the analysis. The original file was not modified and AE was not opened.
- AE project `17.5x40`, 8-bit; 18 compositions, 148 layers; the parser extracted no expression entries. The keyframed motion below needs no expressions.
- `Comp 1`: 1920×1080, 24 fps, 45 s long. A composition's duration does not prove 45 s of finished content.
- The parser reports 26 assets missing at their stored paths; `(Footage)` has 25 basename matches. Hash/content, sequences and relinking are not verified. A 2023 collect report lists one missing item; that is an older state, different from the current path check.
- The footage includes `Pre-comp 6.mp4` and `Pre-comp 6 p 2.mp4`. These are source/prerender videos, not assumed to be the finished render of `Comp 1`.
- `Pre-comp 6.mp4` was analyzed: 1920×1080, 24 fps, 17.666667 s, all 424 frames; the source hash matched afterwards. Report/timeline/contact sheet in `evidence:the-less-i-know-the-better-03`.
- The reviewed contact sheet shows a white spiral on black, stars/moon/rocket and loose letters, then a pink paper layout, a framed cat photo, hearts, clouds, planets and flowers, with rotated/zoomed layouts between frames. This is an observation of the prerender; its motifs match assets/comps stored in the project, but the separate contribution of camera or effects is not confirmed.
- The 9.25–12.54 s times printed on the contact sheet belong to the MP4 and do not convert to `Comp 1` or authoring precomp times. The sheet picks only 25 images and does not represent the whole video. `Pre-comp 6 p 2.mp4` and the online reference were not analyzed.

## 1. Staggered Icon Wipe Reveals

**Source:** composition `then i saw your face`, layers 6–9. Layers and effects all enabled. Shared order `S_DropShadow → S_WipePlasma`.

| Layer | Wipe Percent: seconds → value |
| --- | --- |
| 9 `pngegg (5).png` | 0.291667 → 100; 1.125 → 0 |
| 8 `ae` | 0.583333 → 100; 1.083333 → 0 |
| 7 `discord` | 0.833333 → 100; 1.333333 → 0 |
| 6 `spotify` | 1.125 → 100; 1.583333 → 0 |

The Wipe Percent keys have BEZIER in/out. Start times are offset by about 6–7 frames at 24 fps, but each icon's wipe length differs.

**Takeaway:** the order of appearance comes from offsetting each layer's animation, with no per-character expression. These are wipes on separate icons/images, unlike the TextEvo selector in Takt Op.

**Not confirmed:** the actual reveal shape, wipe direction and plasma seed. An icon's name does not prove its source file is that logo; check the source item/footage when rebuilding. This composition is stored in the authoring branch below a prerender and is not assumed to render directly from live layers.

## 2. Collage with Separate Shadows for Text and Stickers

**Source:** `then i saw your face`.

| Layer / S_DropShadow effect | Shadow Opacity | Shadow Blur | Shift X | Shift Y |
| --- | --- | --- | --- | --- |
| 2 `Then I Saw  Your Face` | 0.72 | 23 | -9.680008 | 20.319992 |
| 6 `spotify` | 0.79 | 12 | -9.680008 | 40.319992 |
| 9 `pngegg (5).png` | 0.79 | 22 | -9.680008 | 40.319992 |

Shadow Color is stored as `[0,0,0,1]`. The opacity values are on the effect's stored scale, not 0.72%.

**Takeaway:** the shadow colour stays the same while blur and offset change between text and images to separate the layers. This structure suggests a collage; the specific paper/sticker feel needs the render and the source alpha to judge.

**Separating the main image from a fill layer:** `Pre-comp 2`, layers 1 and 2 both named `cut cat.jpg`, both enabled, same in/out 0–2.625 s; layer 2 sits below with `Fill → S_DropShadow`, layer 1 has no effect. Whether the Fill layer is an outline/silhouette is not concluded: check the masks, alpha and transforms of both copies.

## 3. Camera Motion Split across a Null Chain

**Source:** `3d stroke`, parent chain by index: `7 → 8 → 9 → 10 → Camera 1 (11)`. All layers enabled; many shapes, images and text layers are 3D.

| Controller | Property | Keyframes: seconds → value |
| --- | --- | --- |
| Null layer 9 | Position | 0.333333 → [0,0,0]; 0.916667 → [2,-1,188] |
| Null layer 9 | Z Rotation | 0.333333 → 0; 0.916667 → 110 |
| Null layer 10 | Position | -0.041667 → [0,0,10]; 0.5 → [0,0,71] |
| Null layer 10 | Z Rotation | -0.041667 → -219; 0.5 → -10 |

These keys have BEZIER in/out. Layer 9 also has Orientation `[0,0,0] → [0.1,0.1,12]` at the same times as Position.

**Takeaway:** the camera's rotate/advance stages are split across several controllers so parent motion adds to local motion. Do not simply add the vectors/rotations into world coordinates; 3D transforms have their own order and axes.

**Missing for a rebuild:** camera options/point of interest, positions of the 3D layers, anchors, full easing and how the precomp maps onto the parent timeline. These branches belong to the stored authoring structure; it is not proven that the prerender's images came from that exact revision.

## 4. Flower and Decoration Reveals with Wipe/Scale/Opacity

**Source:** `fine without u`.

- Layer 9 `rose`: S_WipeLine enabled; Wipe Percent `11.5 → 100`, `12.166667 → 0`, BEZIER.
- Layer 6 `circle`: Wave Warp enabled; Scale `12.333333 → [26,26,26]`, `12.791667 → [39,39,39]`, BEZIER. Opacity `12.333333 → 0`, `12.625 → 100`, LINEAR.
- Wave Warp static values: Wave Type enum `1` (enum name not decoded), Height `9`, Width `38.1`, Direction `98`, Speed `1.15`.

**Takeaway:** a decoration layer can use scale for motion, opacity to bring it in and Wave Warp for extra distortion. Not every effect parameter needs animating.

**Not confirmed:** the final outline/silhouette, wipe direction and Wave Warp result. These local times are not mapped to MP4 times.

## 5. Circle Wipe and Fade to Join a Prerender

**Enabled sources in `Comp 1`:**

| Layer | In/out, seconds | Main data |
| --- | --- | --- |
| 9 `Pre-comp 6` | 8.958333–17.583333 | S_WipeCircle enabled; Wipe Percent rises from 0 at 16.5 to 97 at 17.416667 over 15 keys; Opacity 100 at 17.166667 → 0 at 17.583333 |
| 12 `Pre-comp 6 p 2.mp4` | 17.541667–25.958333 | S_WipeCircle enabled; Wipe Percent from 0 at 24.375 to 97 at 25.583333 over 13 keys; Opacity 100 at 25.5 → 0 at 25.708333 |

Layer 9's Wipe Percent curve uses BEZIER and layer 12's uses LINEAR; both opacity fades use BEZIER. Layer 9 also has a 0 key at 16.541667, and layer 12 a 0 key at 24.75 before rising. The wipe's endpoint is 97, not 100.

**Takeaway:** the ending combines a wipe with opacity; the fade to 0 still removes the layer although the wipe never reaches 100. A rebuild must keep both curves rather than collapsing them to two wipe keys and calling it equivalent.

**Limits:** centre, direction/reverse, softness and the layers below are needed to describe exactly what is revealed or covered. Only the joining structure in the project is known; no full AE render confirms it.

## 6. 3D Stroke with a Path, No Evidence of Animated Strokes

**Source:** `3d stroke`, layer 19 `3d stroke`, an enabled solid with one mask and enabled `tc 3DStrokePath`. Static: Path enum `0`, Thickness `1.2`, Start `0`, End `100`; no keyframes on these direct parameters.

**Lesson:** having a 3D Stroke plugin does not mean there is a draw-on animation through Start/End. Camera or geometry can produce other motion; read the mask/path and related groups before writing a draw-on recipe.

## 7. Prerender Replacing the Original Build Branch

In `Pre-comp 6`, layer 1 `Pre-comp 6.mp4` is enabled, in/out 0–17.666667 s; layers 2–19 are all off, including the camera, Nulls, text and `Pre-comp 4`. The disabled layers can be studied as authoring structure, but they do not contribute directly to rendering the current state.

`Comp 1` layer 2 RSMB Pro and layer 3 Deep Glow are also off at layer level although their effects are individually enabled. Leave this global blur/glow out of the active recipe.

**New lesson for the handbook:** track the live render path and the stored authoring path separately. A prerendered MP4 may contain baked effects; the current project does not prove that each stored effect produced that exact MP4.

## Reuse

Pick one group at a time: staggered icon wipes, collage shadows, a multi-stage Null camera or circle wipe + fade. Take the full dependencies, easing speed/influence, sources and parent chain from the JSON before testing in a new project. Do not run untrusted expressions/plugins, and do not modify or relink the original project.

## Reading the Source and Reuse

This article keeps measurements and references from the recorded analysis; the project, evidence images and private reports are not distributed with the library. `evidence:` codes are source identifiers, not files needed to read the article. The source holder resolves them in local records; other contributors record their own sources and verification level. See [evidence conventions](../foundations/evidence-and-validation.md).
