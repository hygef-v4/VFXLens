# AE Notes — Editing Techniques from Reference Notes

Compiled from `evidence:ae-notes-01` (inspected 2026-11-04) as a companion to the [main library](../README.md). The source consists of user study notes and static UI screenshots rather than an After Effects project file with parser-measured keyframes or render-verified recipes.

## Source and Lookup Conventions

- DOCX SHA-256: `09fb93d63e664d97d895e976595cd1934bd0ed697e12ed5a02dec5b78fc7b16c`.
- Extracted 472 body paragraphs and 105 embedded PNG images (0 Word tables; 32 paragraphs contain YouTube links). All text paragraphs, all five contact-sheet index boards, and seven individual parameter/impact screenshots were inspected directly; external YouTube tutorial videos were not watched.
- `P...` references below denote **paragraph indices in the extracted transcript, not Word page numbers**. The verbatim text extract, image relationships, and media files reside under `evidence:ae-notes-02`.
- `extracted-text.txt` preserves paragraph text and image positions; `extracted-notes.json` records relationships/hyperlinks; `media/` holds all 105 PNGs. The five `image-index-*.jpg` sheets serve as visual indexes only and never replace reading the full-resolution PNGs for numeric values.
- Certain arrows or punctuation marks in the original document were already garbled as `[garbled character in source]`; they are never silently guessed or reconstructed into commands or numbers. The original DOCX file was left untouched.
- Epistemic distinction: **documented in notes** means written in the text body; **read from screenshot** means visible in a static UI capture; **inferred / proposed for testing** means not yet executed on a clip. No embedded expressions or binary plugins were executed.

## 1. Faux 3D Extrusion via Stacked 3D Layers

**Source P2–6.** The `Position` expression adds X/Y offsets scaled by `index` and Sliders `x - offset`, `y - offset`, while computing Z as `index + index*z_offset/10`. It hardcodes a reference to `comp("Comp 1").layer("Shape Layer 2 controller")`.

**Takeaway:** Duplicating a 3D layer across multiple Z slices driven by a shared controller creates the illusion of extruded thickness; this does not convert a 2D image into a true 3D polygon mesh.

**Before Reusing:** You must create the exact controller layer/effect names and enable the 3D layer switch (do not mistake this for importing a 3D model). Note that the source Z formula ignores the layer's original Z coordinate, and using absolute `index` means inserting or reordering layers shifts the extrusion stack. When building fresh, use relative layer indices and preserve the base position. Not yet verified in a live AE session.

## 2. Damped Cosine Text and Velocity-Driven Overshoot

### Per-Character Staggered Text

**Source P9–22.** Expression Selector: `delay = .05`, `freq = 2`, `amplitude = 100`, `decay = 8`; offsets time by `textIndex`, evaluates `cos(2π*freq*t)/exp(decay*t)`, returning `[s,s]` when `t >= 0` and `value` beforehand.

**Cross-Reference:** Shares the exact formula structure of the [Chal7z smooth text preset](chal7z-presets.md#3-smooth-text-per-second-delay-and-damped-cosine-oscillation), except the Notes use `amplitude = 100` whereas the preset stores `80`. Do not merge them into a single "canonical" number. Both the Expression Selector and Animator properties must be transferred together, and returning a 2-element array `[s,s]` is not guaranteed to fit every 3D property without coercion.

### Overshoot from Keyframe Incoming Velocity

**Source P32–53.** Locates the most recent keyframe at or before the current time, samples `velocityAtTime(keyTime - frameDuration/10)`, multiplies by an amplitude Slider and `sin(2π*freq*t)/exp(decay*t)`, and adds the result to `value`.

**Takeaway:** Oscillation amplitude scales with the incoming velocity entering the keyframe—fundamentally different from a fixed-amplitude cosine wave. Because it selects the nearest preceding keyframe, it triggers after each keyframe rather than only the final one. Requires active keyframes plus three Sliders named `Position amplitude`, `Position frequency`, and `Position decay`; if incoming velocity is zero, the oscillation term evaluates to zero.

**Unverified:** Behavior across tightly spaced multi-keyframe curves, property dimensions, Bezier easing handles, and controller ranges. Do not apply blindly as a standalone preset.

### Wiggle and Property Linking

**Source P25–30, P54–56.** The notes mention `position+value`, `wiggle(frequency, amplitude)`, and one capitalized example `Wiggle(1,10,2,.25)`.

When writing expressions, always use lowercase `wiggle` per the [Adobe Expression Language Reference](https://helpx.adobe.com/after-effects/desktop/work-with-expressions/expression-language-reference/expression-language-reference.html). Frequency is in cycles per second (Hz) and amplitude is in the target property's units. Do not copy the capitalized `Wiggle` typo or treat the note's "max ±50 px" remark as a verified engine limit.

For `position+value`, always verify which property hosts the expression and whether both coordinate spaces match; placing `position+value` directly on `Position` itself doubles the coordinate rather than linking two separate transforms.

## 3. Warp, Stretch, and Scatter Transitions

**Source P61–85, P164–216.** Mentioned effects include `S_DissolveLuma`, `S_WipeBlobs`, `BCC 2D Particles`/scatter, `S_WarpVortex`, `Minimax`, `BCC Scatterize`, `S_Diffuse`, `RetroGrade Transition`, and warps such as `FishEye`, `Magnify`, `Bubble`, `Chroma`, `HeatDistortion`, `Polar`, `Puddle`, `Wave Warp`, and `Warp`.

Keep numeric fragments in their exact context:

- **P71–75:** Notes vortex `0` to `-20` without specifying the exact parameter name or keyframe timing—insufficient to reconstruct a complete curve.
- **P77–81:** Notes a `Minimax` sequence `0`, `500`, `0` (with garbled separator characters). Screenshot `image8.png` confirms `Operation = Maximum`, `Radius = 500`, `Channel = Color`, `Direction = Just Horizontal`. This illustrates horizontal directional block stretching, not a universal rule that every clip needs `Radius = 500`.
- **P177–180:** Notes `FishEye` `Amount` from `-1.5` to `0`; `image41.png` confirms `Amount = -1.50`, `Wrap X/Y = Reflect`, and `Center = [960, 540]` at that frame, without duration or easing curves.
- **P165:** Remarks that `Scale Wipe` is "same as CC Smear"—treat this as the author's visual association rather than algorithmic or parameter equivalence.

**How to Apply:** Pick a target shot, establish the warp center/axis and border wrapping mode first, then shape the envelope to the cut beat. Never hardcode `[960, 540]` from a `1920x1080` screenshot into compositions of different dimensions.

## 4. Luma Mattes for Selective Lighting and Flicker

**Source P92–124.** Two distinct compositing patterns:

1. Prepare a high-contrast luminance map of the subject using `Black & White` $\rightarrow$ `Levels` $\rightarrow$ `Gaussian Blur` (screenshot P97 shows `Blurriness = 6.9`), then use `Luma Matte` to restrict an animated texture/light layer to that luminance region.
2. Draw random shapes, blur and adjust `Levels`, and pair with `Luma Inverted Matte` over the main scene to create localized regional flicker (P117–124).

**Takeaway:** Flicker does not have to be a full-frame `Exposure` pump; luma mattes can isolate flicker to specific tonal ranges or shapes. Because layer roles, inversion flags, blending modes, and stack order are only partially shown, this is recorded as a compositing concept rather than a fixed preset.

`CC Blobbylize` appears alongside an ambiguous blend-mode note in P110–116 with a colored texture screenshot; keep the texture-driven overlay concept without guessing the exact blend mode from the garbled text.

## 5. Impact Frames and Invert Chains

**Source P318–342.** The notes describe using standard `Invert` on frame 1 and `S_Invert` (with chroma inversion disabled) on frame 2. Screenshots P321 and P324 show two distinct high-contrast looks over `ERROR` typography.

Screenshot `image93.png` (P326) confirms the `S_Invert` panel state: **`Invert Luma` enabled**, while `Invert Chroma` and `Invert Red/Green/Blue/Alpha` are disabled; `Scale Lights = 1`, `Offset Darks = 0`, `Saturation = 1`. Without an `.aep` timeline, static screenshots cannot confirm whether the two captures are consecutive frames or their exact duration.

P328–334 suggests inserting a single energy frame immediately before the main impact frame—record this as an editorial timing hypothesis to test rather than a mandatory rule.

P336–342 mentions `AE Pixel Sorter 2` with `Sort by = XOR`. Because pixel sorting pulls long color streaks across the frame, always bound the threshold/mask region and check the exact plugin version; do not conflate pixel sorting with bitstream datamoshing.

## 6. Directional Blur and Depth of Field

**Source P226–245.** Lists `OLM DirectionalBlur`, `BCC Fast Lens Blur`, `Radial Blur`, and `FL Depth of Field` alongside a depth-scanner workflow.

Screenshot `image61.png` (P236) shows exact `OLM DirectionalBlur` values:

| Parameter in Screenshot | Value |
| --- | ---: |
| Angle | 35° |
| Brightness Gain | 1 |
| Front Blur Strength | 155 |
| Back Blur Strength | 75 |
| Front/Back Alpha Fade | 0 |
| Front/Back Sharp Tail | 0% |
| Noise Variation | 0% |
| Thickness | 10 |

**Takeaway:** `Front Blur Strength` and `Back Blur Strength` can be weighted asymmetrically along the blur axis. Without keyframe data, do not assume `Angle = 35°` or `155 / 75` fits the motion vector of other shots.

**Source P346–348:** Screenshot `image98.png` (`Camera Options`) shows `Depth of Field = On`, `Focus Distance = 1309 px`, `Aperture = 262.3 px`, `Blur Level = 100%`, `Zoom = 2000 px`. These values depend on the specific 3D camera distance, layer Z depths, and composition resolution; never equate 3D Camera DOF with a 2D blur filter or a depth-map post effect.

## 7. Texture, Sketch, Halftone, and Pixel Effects

**Source P88–163, P217–225, P246–280.** Cataloged as a visual taxonomy rather than complete recipes:

| Visual Intent in Notes | Mentioned Effects / Families |
| --- | --- |
| Compression / digital corruption | `S_JpegDamage`, `S_DigitalDamage`, `JPEG Glitch` |
| Scanline / CRT / analog TV | `BCC Damaged TV`/`Dissolve`, `Bad TV`, `Signal`, `uni.VHS Transition` |
| Sketch / painterly stylization | `BCC Pencil Sketch`, `S_AutoPaint`, `S_Cartoon`, `S_CartoonPaint` |
| Halftone / dot matrix / display grid | `BCC Halftone`, `BCC Tile Mosaic`, `BCC LED` |
| Surface grunge / film wear | `BCC Grunge`, `Noise HLS`, `S_FilmDamage` |
| Pixel sorting / stretching | `AE Pixel Sorter`, `Pixel Melt`, `Pixel Stretch`, `Pixelocybe` |

Side-by-side screenshots on the same base frame are helpful for browsing visual directions, but lack controlled A/B renders. Always tune noise, chroma shift, and edge thresholds to the specific source footage.

## 8. Time-Based and Temporal RGB Effects

**Source P282–304.** Describes `S_TimeWarpRGB` offsetting R, G, and B channels in time—mechanically consistent with the per-channel frame shifts extracted from [Standard](standard.md#4-temporal-rgb-time-shift-combined-with-threshold).

Other temporal effects noted: `S_TimeSlice` (mentions animating slice count without listing exact property matchNames), `S_Trails`, `S_GetFrame`/freeze, `CC Wide Time`, `S_JitterFrames`, `S_MotionDetect`, `S_RandomEdits`, and `Posterize Time`.

**Operational Distinctions:** Freeze holds a single frame, trails accumulate historical frames, temporal RGB shifts sample channels at different frame offsets, and `Posterize Time` reduces the frame update cadence. Do not treat them as interchangeable with optical-flow speed ramps.

## 9. Colorama, Tritone, and Blending

**Source P105–109:** `Colorama` paired with `Hue` blending mode; the screenshot shows aggressive palette remapping without full `Input Phase` / `Output Cycle` wheels.

**Source P393–395:** Darkening midtones via `Tritone`, stacking `Deep Glow` / `Curves` / `Levels`, and setting the layer blend mode to `Screen` to make a subject pop. In practice, isolating a subject requires a mask, matte, or rotoscoped layer—`Tritone` + `Screen` does not automatically segment foreground subjects on its own.

**Evidence Cross-Check:** [White Ferrari](white-ferrari.md) contains `Screen` layers with `Tritone + PEDG`, including both enabled and disabled duplicates. Sharing the same tool pair does not prove an identical recipe.

## 10. Particles and Shatter Simulations

**Source P352–364:** `Trapcode Particular` setup notes covering emitter type, `Particles/sec`, `Emitter Size XYZ -> Individual`, direction/spread, and velocity (suggesting a `Box` emitter, `Uniform`/`Disc`, and spread around `25–40` as a starting point rather than fixed universal constants).

**Source P307–317:** `CC Pixel Polly`, `CC Cylinder`, and `BCC 3D Image Shatter` illustrated with shattering fragments or curved paper cylinders. Without source geometry, alpha channels, force fields, or camera data, treat these as effect leads rather than physical paper-folding simulations.

## 11. SFX Filtering and Reverb

**Source P365–390.** Proposes muffling audio before an impact hit using `High-Low Pass` combined with `Reverb` and level keyframes. The text mentions a cutoff sequence `4000`, `800`, `4000` (with garbled separators and no timestamps/easing), which should be treated as a conceptual sweep rather than a measured curve.

Screenshot `image104.png` (P370) shows the following static inspector values:

| Effect / Parameter | Value in Screenshot |
| --- | --- |
| High-Low Pass / Filter Options | Low Pass |
| Cutoff Frequency | 2400 |
| High-Low Pass Dry/Wet Out | 0% / 100% |
| Reverb Time | 100 ms |
| Diffusion / Decay / Brightness | 75% / 25% / 10% |
| Reverb Dry/Wet Out | 86% / 16% |

This single-frame snapshot differs from the `4000 -> 800 -> 4000` text note; both are preserved without conflating them.

Per [Adobe Audio Effects](https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/list-of-effects/audio-effects.html), `Dry Out` and `Wet Out` control the unprocessed and processed signal mix (`0% Dry / 100% Wet` is standard for a full low-pass filter). Do not generalize the note's "always decrease dryout" remark into a universal mixing rule—always audition in context and watch output headroom.

## 12. Tutorials and Next Learning Steps

All 32 paragraphs containing YouTube links are preserved in `extracted-text.txt` (P397–470), covering title cards, 3D VHS typography, vector blur, dissolves, print-copy looks, shockwaves, glitch/VHS, DOF, smoke, 3D cameras, audio transitions, and scene selection. **Because those external videos were not opened or watched**, their contents are not claimed as verified library knowledge.

When testing any item above: inspect the source image, identify exact property names, units, layer order, controllers, and plugin versions, and test inside an authorized working project before recording a verified recipe. The original DOCX file remains untouched.

## Source Provenance and Reuse

This case study preserves measurements and references from the recorded analysis run; private projects, evidence images, and raw reports are not redistributed with the library. `evidence:` tokens serve as source identifiers rather than files required to read the article. See [Evidence and Validation](../foundations/evidence-and-validation.md).
