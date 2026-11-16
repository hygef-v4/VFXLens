# Takt Op — Transitions, Shake and Text

Project/demo case study, read 2026-11-04. The figures below are the source's data, not default settings. [See the shared techniques](../techniques/README.md).

Times in the tables belong to the named composition and are not assumed to be demo-video times. To compare them, trace start time, stretch, Time Remap and parent precomps; matching fps does not establish that two timelines are aligned.

## 1. Chroma, Invert and Displacement Transition

**From AE Notes:** [warp/scatter and stretch](ae-notes.md#3-warp-stretch-and-scatter-transitions), [impact frame/invert](ae-notes.md#5-impact-frames-and-invert-chains); many examples lack duration/easing.

**Compare Standard:** [warp combined with blur/mosaic/brightness](standard.md#3-shot-opening-transition-fast-warp-with-decaying-blurmosaicbrightness) and [time-offset RGB per channel](standard.md#4-time-offset-rgb-with-threshold-not-just-position-offset-rgb).

**Another transition type:** [circle wipe combined with an opacity fade](the-less-i-know-the-better.md#5-circle-wipe-and-fade-to-join-a-prerender), with both animation curves and a wipe endpoint below 100.

**Compare White Ferrari:** [one-frame layer transitions with blur leading into the cut](white-ferrari.md#3-one-frame-layer-transitions).

**Source:** Takt Op → `Pre-comp 11` → layer 106, `a5e631f4dd4b96f69d91af16d23a40ef.mp4 Comp 1`; in/out 3.35–4.05 s.

**Read from the project:** all seven effects enabled, in this order:

`S_DistortChroma → S_Invert → Motion Tile → Displacement Map → CC Vector Blur → Exposure → Bokeh`

| Property | Keyframes: seconds → value | Interpolation |
| --- | --- | --- |
| S_Invert / Invert Luma | 3.65 → 1; 3.70 → 0 | HOLD |
| S_Invert / Invert Chroma | 3.65 → 1; 3.80 → 0 | HOLD |
| Displacement / Max Horizontal Displacement | 3.35 → -323; 3.65 → 57; 4.00 → 57 | LINEAR, then BEZIER handles |
| CC Vector Blur / Amount | 3.35 → 0; 3.65 → 136 | LINEAR |
| CC Vector Blur / Angle Offset | 3.35 → 0; 3.65 → 60 | LINEAR |
| Exposure / Exposure | 3.65 → 0; 4.00 → -0.59 | LINEAR |
| Exposure / Offset | 3.65 → 0; 4.00 → -1.26 | LINEAR |

**Takeaway:** the author stacks several transforms on one layer, uses HOLD for abrupt invert state changes and continuous keyframes for blur/displacement. At 20 fps the two invert spans last 1 and 3 frame intervals.

**How to try it — inference:** build displacement/blur first, add a short invert at the accent, then refine colour and bokeh. Keep the source order as the comparison reference; the order of trying steps is not a new render order.

**Still missing:** the displacement map source, the remaining static parameters, transform/mask/blend and precomp links. The table is not enough to become a standalone preset.

## 2. Decaying Shake after an Accent

**From AE Notes:** [velocity-driven overshoot and reading wiggle](ae-notes.md#2-damped-cosine-text-and-velocity-driven-overshoot), distinct from a plugin's amplitude envelope.

**Preset example:** [S_Shake and S_DissolveShake in Chal7z](chal7z-presets.md#1-decaying-shake-and-dissolve-shake); the timebase of FFX keyframes is not established.

**Compare White Ferrari:** [shake with Motion Tile 400% and Mirror Edges](white-ferrari.md#1-short-shake-with-edge-handling).

**Source:** Takt Op → `Pre-comp 11` → layer 19, `Adj for a5e631f4dd4b96f69d91af1`; in/out 5.85–6.70 s.

**Read from the project:** the layer has `S_Shake` enabled. `Amplitude`: 5.85 s → 1; 6.405566 s → 0.

**Takeaway:** shake intensity is driven by an envelope that decays to 0 over about 0.556 s. This is the effect's normalized amplitude, not a 1-pixel displacement.

**How to try it — inference:** set a high amplitude at the accent and bring it to 0 so the shot settles. Read frequency, shake axes, random seed, motion blur and easing before reproducing the source exactly.

**Not confirmed:** whether this accent matches a music beat or a position in the demo.

## 3. Dissolve with Shake

**Compare White Ferrari:** [dissolve-shake stacking a short shake envelope](white-ferrari.md#2-longer-dissolve-shake-stacked-on-the-same-shot).

**Source:** Takt Op → `Pre-comp 3` → layer 1, `ones.`; in/out 0.40–0.95 s.

**Read from the project:** `S_DissolveShake` enabled.

| Property | Keyframes: seconds → value |
| --- | --- |
| Dissolve Percent | 0.40 → 33; 0.942188 → 0 |
| Y Phase | 0.40 → 3; 0.535547 → -0.55; 0.738867 → 0.15; 0.942188 → 0 |
| Tilt Phase | 0.40 → -1; 0.535547 → 0.35; 0.738867 → -0.02; 0.942188 → 0 |

**Takeaway:** the phases change sign with decreasing amplitude while the dissolve goes to 0. The author does more than reduce the shake: the shake's rhythm and phase are keyframed too.

**How to try it — inference:** use a back-and-forth oscillation that shrinks to give a bounce before settling. Take the full easing and the Amplitude/Frequency/X/Y/Tilt parameters from the JSON; the three curves above are not the whole preset.

## 4. Glow, Color and Bokeh

**From AE Notes:** [color remap/Tritone and blending](ae-notes.md#9-colorama-tritone-and-blending), [directional blur/DOF](ae-notes.md#6-directional-blur-and-depth-of-field).

**Preset example:** [Bokeh paired with Gamma](chal7z-presets.md#2-light-and-blur-transition-with-two-synchronized-curves); only rising envelopes were read, so the whole transition cycle is not established.

**Compare White Ferrari:** [film look and Blur Radius driven by expressions](white-ferrari.md#5-vhsfilm-look-from-expressions-with-bounded-amplitude).

**Example source:** Takt Op → `Pre-comp 11` → layer 26, `a5e631f4dd4b96f69d91af16d23a40ef.mp4 Comp 3`.

**Read from the project:** order `PEDG` (Deep Glow per the classifier) → `ADBE Tritone` → `CROSSPHERE_Bokeh`, all enabled. Deep Glow / Exposure has keys 5.85 → 0.26; 6.25 → 1.23; 6.65 → 0.02.

**Important:** this layer is only visible from 6.65 to 6.70 s. The first two keyframes fall outside its visible range; do not describe that whole exposure curve as a flash shown on this layer. Trace the related layers before concluding.

**Demo observation:** the contact sheet has strong pink highlights and blurred frames. Which part comes from Glow, Bokeh, the source footage or other compositing layers is not separated.

**How to try it — inference:** control brightness, colour cast and blur one step at a time. Do not carry glow values to other footage before checking input brightness, bit depth and effect order.

## 5. Per-Character Delayed Text

**Preset example:** [per-second delay with a decaying cosine](chal7z-presets.md#3-smooth-text-per-second-delay-with-a-decaying-cosine), distinct from Standard's per-frame delay.

**Compare Standard:** [Expression Selector with a decaying oscillation](standard.md#1-per-character-bouncing-text-with-an-expression-selector), [matte outline for stickers](standard.md#2-sticker-outline-from-an-expanded-matte-and-re-composited-image), and [two collage variants on the same timing frame](standard.md#7-two-collage-versions-on-the-same-time-frame).

**Other builds:** [staggered icon/image wipes](the-less-i-know-the-better.md#1-staggered-icon-wipe-reveals), [collage with shadows](the-less-i-know-the-better.md#2-collage-with-separate-shadows-for-text-and-stickers), and [camera through a Null chain](the-less-i-know-the-better.md#3-camera-motion-split-across-a-null-chain). These are layer-level keyframes/parenting, not per-character selectors.

**Source:** Takt Op → `juice Comp 1` → layer 1, `juice 2` → `Text/Animators/TextEvo/Selectors/textevo/Amount`.

**Static expression read:** it reads the `effect("TextEvo")` controls, computes an offset from `textIndex`, `textTotal` and `thisComp.frameDuration`, and samples the value with `v.valueAtTime(time - offset)`.

| Mode | Offset formula read |
| --- | --- |
| Mode 1 | `(textIndex - 1) * frameDuration * delay` |
| Mode 2 | `(textTotal - textIndex) * frameDuration * delay` |

The expression also has branches by centre, edges, selected characters and random; random is seeded with `textIndex + fx(5)` with the timeless parameter on. Read every branch before using it.

**Takeaway:** animate one shared control, then let each character sample that animation curve at a different delayed time. No per-character keyframes are needed.

**How to try it — inference:** change the direction and the number of delay frames to reveal text one character after another. The TextEvo control, parameter indices and animation curve are required dependencies; this is not an expression to paste into a new project on its own. The expression was not executed.

## 6. Retime and Speed Ramp

**Another time-accumulation type:** [S_Trails / CC Wide Time](chal7z-presets.md#4-trail-and-wide-time-differ-from-time-posterization); trail, colour posterize, time posterize and speed ramp are different things.

**Compare White Ferrari:** [Posterize Time picture cadence](white-ferrari.md#4-changing-picture-cadence-with-posterize-time) versus [prerender/interpolation traces](white-ferrari.md#7-retime-and-prerender--limited-evidence).

**Source:** Takt Op → composition `a5e631f4dd4b96f69d91af16d23a40ef.mp4 Comp 1` → layer 1, footage of the same name.

**Read from the project:** `Twixtor 45` enabled; layer in/out 3.35–3.70 s. The direct parameters of this instance showed no keyframes or enabled expressions.

**Not enough evidence:** having Twixtor does not mean there is a speed ramp. Check static speed, child groups, time remap, stretch, source fps and other instances. The video detector has speed-ramp candidates but does not prove they come from this instance.

**Current lesson:** only the retime structure is recorded; no speed-up/slow-down formula is stored. Do not invent a curve or speed ratio.

## 7. Overlays and Audio Visualizer

**From AE Notes:** [luma mattes for selective flicker](ae-notes.md#4-luma-mattes-for-selective-lighting-and-flicker) and [particles/shatter simulation](ae-notes.md#10-particles-and-shatter-simulations).

**Compare White Ferrari:** [lens, fog and butterfly overlays in Screen/Add](white-ferrari.md#6-light-and-atmosphere-overlays-by-blend-mode).

**Source:** Takt Op → `Pre-comp 11` → layer 34, `Solid for Adj for Watch Takt Op`; in/out 8.20–10.20 s.

**Read from the project:** `BCC_AUDIOVISUALIZER` enabled on a solid layer. Direct parameters showed no keyframes or enabled expressions.

**Demo observation:** text and graphic lines overlap the character. Which lines come from the Audio Visualizer, or react to sound, is not confirmed.

**Missing before rebuilding:** the referenced audio source, visualizer mode, frequency range, geometry parameters and blend/compositing. There is no complete recipe for this form yet.

## 8. SFX and Audio Processing

[AE Notes: High-Low Pass + Reverb](ae-notes.md#11-sfx-filtering-and-reverb) has screenshot parameters and a proposed envelope; no audio was listened to or measured to confirm the effect. When studying further projects, record the source sound, timing, cutoff, dry/wet, gain and the listening result.

## Sources and General Limits

- Project: `evidence:takt-op-01`.
- Project JSON: `evidence:takt-op-02`; report `project-report.md` in the same folder.
- Demo JSON: `evidence:takt-op-03`; timeline, contact sheet and evidence frames in the same folder.
- The project has 46 compositions, 290 layers and 82 expression entries; 82 entries are not 82 different techniques.
- Demo 13.2 s at 20 fps; `Comp 1` lasts 42.8 s. The two timelines are not aligned.
- 32 assets are missing at the paths stored in the project. AE was not rendered and each effect's contribution was not verified separately.
- Plugin labels from the classifier and effect labels from the video detector need cross-checking; do not use them to decide what to buy or install.

## Reading the Source and Reuse

This article keeps measurements and references from the recorded analysis; the project, evidence images and private reports are not distributed with the library. `evidence:` codes are source identifiers, not files needed to read the article. The source holder resolves them in local records; other contributors record their own sources and verification level. See [evidence conventions](../foundations/evidence-and-validation.md).
