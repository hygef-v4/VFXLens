# Chal7z Presets — Learning from FFX Structure

Read on 2026-11-04 as a companion to the [editing handbook](../README.md). These are the author's own presets (chal7z). This is a binary inventory with sourced examples, not the result of applying the presets or rendering them in AE.

## Source, Scope and Confidence

- Source: `evidence:chal7z-presets-01`.
- Archive SHA-256: `909dc286a54e363f2814dc1f8d446bd7d0dc0bd773f392372b1d6b9a0f758732`.
- Only the FFX files were extracted into `evidence:chal7z-presets-02`; the original archive was left intact. No preset was installed, no embedded script or plugin was run and AE was not opened.
- Inventory: 673 files, about 130.3 MB extracted; 654 distinct SHA-256 values, i.e. 19 files duplicate another file's bytes. Different names do not mean 673 different techniques.
- All 673 files have a `RIFX:FaFX` root. A structural scan read 169,848 property chunks with the `py_aep` library and reported no structure/property errors in this pass. That does not prove every property, opaque payload or data type was interpreted fully and exactly as AE does.
- 280 presets have at least one readable keyframe list. 92 expression sources were read from 44 presets; whether every expression is enabled or runs validly in the host is not established, and no expression was executed.
- **Keyframe time_units are not converted to seconds/frames:** the host FPS, timebase and how a preset is placed at the playhead are not established. The integer times below are storage units, not milliseconds or frame numbers.
- **Static storage values are not assumed to be AE UI values:** they may contain padding, normalized coordinates, enums or plugin-specific conventions. Do not copy whole arrays into the UI.
- **Property paths are references:** the enabled state of each effect and the compositing order after application are not confirmed. The lists below give reference paths in file order and do not claim to be the rendering stack.

## Library Map

| Folder group | FFX files |
| --- | ---: |
| General / CC | 139 |
| General / One Frame | 132 |
| General / Shake | 120 |
| General / STYLES | 59 |
| General / Text | 52 |
| General / Distort | 18 |
| General / Optical Flare | 18 |
| General / Particular | 18 |
| General / VFX | 15 |
| General / Audio | 12 |
| General / Fractal Noise | 8 |
| General / Transition&Dissolve | 8 |
| General / Twixtor | 8 |
| General / Flicker | 7 |
| General / Time | 5 |
| General / Vhs - Crt | 5 |
| General / Noise | 3 |
| General / 3d | 2 |
| General / Glitch | 2 |
| General / Pixel | 2 |
| Valorant / !Random, Effects, Extra | 40 |

Groups and file names are packaging labels. Names such as "One Frame", "4K", "Bouncy" or "Typing" do not prove duration, upscaling ability or the actual motion.

## 1. Decaying Shake and Dissolve-Shake

### BEETLX SHAKE 6 BOUNCY

**Source:** `General/Shake/BEETLX SHAKE 6 BOUNCY.FFX`.

Reference path `ADBE Effect Parade / S_Shake`. Property `S_Shake-0050`, named `Amplitude`, has keys:

| Stored time units | Value read | In/out interpolation |
| ---: | ---: | --- |
| 0 | 1.7 | BEZIER / BEZIER |
| 22527 | 0 | BEZIER / BEZIER |

**Takeaway:** the preset stores a shake envelope that decays to 0. The name Bouncy does not prove a bouncing camera or amplitude overshoot; read frequency, axes, easing speed/influence and the preview.

### D2 DISSOLVE 1

**Source:** `General/Transition&Dissolve/D2 DISSOLVE 1.FFX`.

References `S_DissolveShake`; Amplitude `2` at time units `7000`, back to `0` at `18000`, BEZIER on both sides. This is an example of reusing a decaying intensity envelope in another effect type; it does not establish that Wipe/Dissolve Percent follows the same curve.

**Inferred application:** separate the intensity envelope from the static shake settings. Choose the clip, FPS and target duration before retiming; do not read 22527 or 11000 as seconds or frames.

## 2. Light-and-Blur Transition with Two Synchronized Curves

**Source:** `General/Transition&Dissolve/LIGHT BLUR TRANSITION.FFX`.

The paths reference Bokeh (`CROSSPHERE_Bokeh`), then `S_Gamma`.

| Property | Time units 362400 | Time units 369600 | Interpolation |
| --- | ---: | ---: | --- |
| Bokeh / Blur Radius (`-0003`) | 0 | 29 | LINEAR |
| S_Gamma / Gamma (`-0050`) | 1 | 1.5 | LINEAR |

**Takeaway:** both parameters start and end at the same stored times, `7200` units apart. A blur envelope paired with a gamma envelope is worth testing as a transition, but there is no evidence of a complete "blur then clear" cycle: both curves read here only rise.

**Still missing:** effect state, plugin definition/version, timebase, actual application order and what follows. Gamma is not Exposure; do not rename the parameter to EV or treat it as an equivalent exposure flash.

## 3. Smooth Text: Per-Second Delay with a Decaying Cosine

**Source:** `General/Text/Text Animation/BEETLX TEXT SMOOTH ANIMATION.FFX`.

Property `ADBE Text Expressible Amount` contains this source:

```javascript
delay = .05;
myDelay = delay*textIndex;
t = (time - inPoint) - myDelay;
if (t >= 0){
  freq = 2;
  amplitude = 80;
  decay = 8.0;
  s = amplitude*Math.cos(freq*t*2*Math.PI)/Math.exp(decay*t);
  [s,s]
}else{
  value
}
```

This is **source quoted for reading**, not an expression that was test-run or guaranteed valid in every selector. The property metadata records dimensions=3 while the expression branch returns two elements; check how AE accepts or coerces this in the selector before reusing it.

The Position animator starts at `[0,-56,0]`. Scale starts at `[100,100,100]`, Rotation at `0`. Amount scales the animator; it is not directly the final position or scale.

**Takeaway:** delay `.05` is seconds per textIndex, unlike Standard, which uses one frame per textIndex. At 24 fps, `.05s` is 1.2 frame intervals; do not call it a fixed one-frame delay. Per the source, the first character is already delayed by `.05s` because textIndex starts at 1.

`freq=2`, `amplitude=80`, `decay=8` describe a cosine that decays exponentially after the delay. This is a reading of the static formula, not an assessment of how the motion feels.

### Typing Preset: Mechanism Not Established

`BEETLX TEXT TYPING PRESET.FFX` has Text Document and Text Animator paths and Slider/Checkbox/Color controls. The reader did not retrieve expressions or keyframes from the scanned properties of this file. Only its dependency structure is recorded; whether typing uses Source Text, a selector or a script is not inferred from the file name.

## 4. Trail and Wide Time Differ from Time Posterization

### TIMETRAIL

**Source:** `General/Time/TIMETRAIL.FFX`, referencing `S_Trails`.

First storage scalars: Prev Brightness about `0.9199877929687499`, New Opacity `1`, Blur Amount `2`. No keyframes were read from this file's scanned properties.

**Inference:** a trail built from old/new contribution plus blur is worth testing; trail length, history reset, frame sampling, feedback and artifacts at cuts are not confirmed. Do not call this physical shutter motion blur.

### SHUTTER_WIDETIME

**Source:** `General/Time/SHUTTER_WIDETIME.FFX`.

References `CC Wide Time`, `ADBE Posterize`, `ADBE Shift Channels`. First scalar data:

- Wide Time / Forward Steps `6`, Backward Steps `6`, Native Motion Blur enum `2`.
- Posterize / Level `12`.
- Shift Channels / Take Red From enum `10`, Green `10`, Blue `4`; enum names not decoded.

**Key lesson:** `ADBE Posterize` here is a different effect from `ADBE Posterize Time`; Level 12 is not 12 fps. Do not infer the actual mechanism from the Time folder or the SHUTTER name.

## 5. One Frame: A Static Offset Does Not Create a One-Frame Duration

**Source:** `General/One Frame/BASIC OFFSET.FFX`.

References `ADBE Offset`. `Shift Center To` has dimensions=2 with first storage scalars `[0.5,1.0018518518518518]`; Blend With Original starts at `0`. No keyframes were read from this file.

**Takeaway:** the One Frame folder may describe the intent to use the preset on a short layer, not a preset that trims the layer to one frame. Stored coordinates may be normalized to the layer size; do not instruct entering `0.5 px`/`1.00185 px` directly.

## 6. Effect References and Overall Limits

Files with an effect reference path, for example: Curves `91`, PEDG `83`, Looks `74`, S_Shake `71`, S_Flicker `44`, S_DissolveShake `36`, Particular `23`. These are counts of files with a reference, not of enabled effect instances or of machines with the plugin installed.

The CC/Particular/Element/Optical Flare presets were not studied one by one and no variants were rendered; the 673 files had a **structural inventory**, and the recipes above were examined in detail. Opaque/plugin data, script/control dependencies and render behaviour need checking per selected preset.

## Data for Further Study

In `evidence:chal7z-presets-03`:

- `archive-inventory.json`: archive list and original hashes.
- `preset-catalogue.json`: 673 files, property paths, byte positions, storage scalars, raw keyframe time_units, interpolation and readable expression sources.
- `catalogue-summary.json`: counts by attribute and number of files referencing each effect.
- `selected-recipes.json`: the eight examples read in detail, with relative names to locate the files.
- `inspect_ffx.py`: a local inventory tool reusing py_aep, with a valid/truncated chunk self-check; not an officially supported VFXLens CLI feature.

The JSON, media and original presets stay local in `outputs/`. To study more, choose an edit type and a specific preset, establish its dependencies first, then test it on a new authorized working copy. Do not claim a preview looks right before applying it and viewing the result.

## Reading the Source and Reuse

This article keeps measurements and references from the recorded analysis; the project, evidence images and private reports are not distributed with the library. `evidence:` codes are source identifiers, not files needed to read the article. The source holder resolves them in local records; other contributors record their own sources and verification level. See [evidence conventions](../foundations/evidence-and-validation.md).
