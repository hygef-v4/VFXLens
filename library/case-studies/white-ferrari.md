# White Ferrari — Editing Techniques Read from the Project

Companion to the [editing handbook](../README.md). The values below were read from the project `white-ferrari.aep` on 2026-11-04. These are sourced reference examples, not complete presets or verified per-effect renders.

## Source and Status

- Source folder: `evidence:white-ferrari-01`.
- Data: `evidence:white-ferrari-02` and `project-report.md` in the VFXLens workspace.
- Project SHA-256: `a98c718b0e37996e6dd68eedc747cf671571eb91e22eceb61792ecce0eb8fe85`; it matched after the analysis. AE was not opened and the original project was not modified.
- 82 compositions, 816 layers, 73 expression entries; AE stores version `25.0x2`, 16-bit colour. The CUDA setting stored in the project does not prove the analyzer used the GPU.
- `Main`: 1920×1080, about 23.976 fps, 18.518519 s, 65 layers.
- Existing render `final 2.mp4`: 3840×2160, 24000/1001 fps, 18.5185 s. Its duration/fps nearly match Main but that does not prove the same revision or shot alignment.
- All 444 frames of the render were analyzed; the source kept its hash. Results in `evidence:white-ferrari-03`: report, timeline, contact sheet and evidence images.
- **Timestamp limit:** ffprobe timed out after 120 s reading per-frame PTS; the analyzer fell back to nominal-fps timestamps. So `VFR=False`, jitter=0 and the report timestamps are not verified original PTS. The JSON warnings do not currently record this fallback; the CLI log does.
- The reviewed contact sheet shows cold blue frames, strong highlights, distortion and bright edges, then loose letters over the image. This describes what is visible and is not attributed with certainty to any plugin or layer. The sheet picked many early peaks, so it concentrates on about 0–3.63 s and does not represent all 18.52 s.
- 74 assets are reported missing at their stored paths. `(Footage)` has 7 basename matches; content and relinking are not verified. The accompanying collect report lists 57 files, about 4.9 GB; that does not mean every dependency of the whole project is present.
- Times below belong to the named composition. For a precomp, trace the parent's start/stretch/time remap before deriving Main times.

## 1. Short Shake with Edge Handling

**Source:** `Main` → layer 20 `shake 2`, enabled adjustment layer; in/out `14.014014–14.597931` s, effects active.

**Enabled order:** `ADBE Tile` (Motion Tile) → `S_Shake`.

- Motion Tile: Output Width `400`, Output Height `400`, Mirror Edges `1`; Tile Width/Height `100`.
- S_Shake / Amplitude: `14.014014 → 0`, `14.055722 → 0.28`, `14.264264 → 0`; keys have BEZIER in/out.
- The envelope peaks after about one frame and returns to 0 about six frames after the first key at Main's fps. `0.28` is the effect's Amplitude value, not pixels.

**Takeaway:** extending the image edges and creating the shake are two separate, ordered steps. Mirror Edges is inferred to cover empty edges while the image moves; it was not rendered on its own to confirm how much it is needed.

**Before reuse:** take frequency, shake axes, seed, motion blur and full easing speed/influence from the JSON. Do not attribute every shake in the render to this layer.

## 2. Longer Dissolve-Shake Stacked on the Same Shot

**Source:** `Main` → layer 21 `shake`, enabled adjustment layer; in/out `13.596930–14.764765`.

**Enabled order:** Motion Tile → S_Shake → S_DissolveShake. Motion Tile again uses Output Width/Height `400`, Mirror Edges `1`.

S_DissolveShake / Dissolve Percent: `13.596930 → 38`, `14.139139 → 0`, BEZIER keys.

**Takeaway:** layers 20 and 21 overlap in time, each with its own envelope. One can learn to separate a longer background motion from a short shake accent; this is inferred from structure, and each layer's contribution to the render was not measured. Check the scope of the adjustment layers and the layers below before rebuilding.

## 3. One-Frame Layer Transitions

**Direct sources in `Main`:**

| Layer | In → out, seconds | Enabled effects in order |
| --- | --- | --- |
| 5 `OneFramer for Pre-comp 35` | 14.723056 → 14.764765 | Offset → BCC Directional Blur |
| 11 `1frame` | 14.055722 → 14.097431 | Median → Mosaic Plane |
| 17 `OneFramer for Null 23` | 13.596930 → 13.638639 | OLM Directional Blur → Transform |
| 32 `Adj for Silent Voice Dub.mp4` | 13.555222 → 13.596930 | OLM Directional Blur → Deep Glow (`PEDG`) |

These layers are enabled adjustment layers about `0.041709s` long, one frame at about 23.976 fps. A very short change can therefore come from a layer's in/out points, not necessarily from a pair of effect keyframes.

**Blur leading into a shot change:** `Main`, layer 51 `Adj for Pre-comp 22`, in/out `8.883884–9.134134`; S_BlurDirectional / Blur Amount from `0` at `8.883884` to `120` at `9.092426`, BEZIER. Check the blur direction and the next layer to confirm how the shots join.

**Inferred application:** use a one-frame layer as a very short accent, distinct from a blur with a rising envelope. This is a timing technique, not a recommendation to use every plugin in the table at once.

## 4. Changing Picture Cadence with Posterize Time

**Sources in `Main`; adjustment layers and effects enabled:**

| Layer | Visible range, seconds | Posterize Time frame rate |
| --- | --- | --- |
| 60 `Adj for Pre-comp 18` | 1.835169–2.335669 | 12 |
| 54 `Adj for Pre-comp 18` | 5.839173–6.798465 | 16 |

**Takeaway:** the author sets a separate time-sampling rate per section while the main composition stays at about 23.976 fps. Posterize Time changes how often the picture updates; it does not prove the playback speed changed.

**Before rebuilding:** check layer overlap, adjustment position and footage motion. Posterize Time, Twixtor and speed ramps are different things.

## 5. VHS/Film Look from Expressions with Bounded Amplitude

**Static expressions read, not executed:**

- `Main` → layer 6 `Adj for Null 27`: in/out `14.347681–14.472806`, Universe VHS enabled; Opacity has an enabled expression `random(0,60)`.
- `Pre-comp 13` → layer 16 `vhs`: in/out `0.208542–0.333667`, Universe VHS enabled; Opacity `random(0,50)`.
- `Pre-comp 17` → layer 26 `Pre-comp 4`: Fast Bokeh / Blur Radius `random(0,5)`. Enabled stack Motion Tile → FC NITRATE → Curves → Colorista IV → Fast Bokeh.

**Takeaway:** the VHS visibility and blur are driven by expressions rather than necessarily by keyframes. Static/pre-expression values in the JSON are not the final rendered values.

**Inferred application:** bound the range of texture/blur variation to get controlled randomness. Perceived frequency, seed, subframe behaviour and how film-like it looks are not confirmed. Read and rewrite expressions only in a new authorized build; do not run the project's embedded expressions to explore.

## 6. Light and Atmosphere Overlays by Blend Mode

| Source | State and data read |
| --- | --- |
| `Pre-comp 17`, layer 3 `LENS 25 .mp4` | Enabled, SCREEN, in/out 0.041708–1.084418; enabled Opacity expression `random(50,65)` |
| `Pre-comp 14`, layers 41 and 42 `1 Fog Atmosphere Side.mp4` | Both enabled, ADD, in/out 0–1.042709; Curves enabled, stored Opacity 100 |
| `Pre-comp 13`, layer 12 `D2 Butterflies (1).mp4 Comp 1` | Enabled, SCREEN, in/out 0–0.959293; Posterize Time → Curves → Hue/Saturation enabled |

**Takeaway:** one edit uses overlay footage with several blend modes, some layers driving opacity with expressions and others with their own colour treatment. Do not infer that every overlay uses Screen or that every butterfly is a particle plugin.

**Still missing:** the footage content/alpha, transforms, parents and full layer order needed to explain each duplicated fog layer's contribution. Why the author needed both layers is not confirmed.

## 7. Retime and Prerender — Limited Evidence

The project has `Twixtor 45` instances; a review of the enabled instances' direct parameters found no speed keyframes to record as a speed-ramp recipe.

The footage folder and report contain names with `8x-RIFE-RIFE4.0-191.8082fps` and many rendered `Pre-comp ...` files. **File names are only traces of a workflow**; how they were made, each clip's real fps and the interpolation settings are not verified. Do not use file names to conclude that RIFE produced clean frames or that the current render still needs Twixtor.

**Lesson worth keeping:** study the prerender/interpolation of source footage separately from the motion/effects inside AE. A complete retime recipe needs the right instance, child groups, static parameters and clip source.

## 8. Avoid Learning from Disabled Effects

`Main` layer 1 `cc` has several individually enabled effects but **layer enabled=false**; the Position expression `wiggle(6,2)` sits on this layer. Do not record it as a camera shake contributing to the current render.

`Main` layer 2 has Posterize Time but the layer is off. Layer 40 `tritione 2` with Screen blend is also off, while layer 42 `tritione` is on. Check layer enabled, effects_active, each effect's enabled state, in/out and the path from Main to the precomp together. A precomp existing does not mean it is rendered.

## Next Verification

Compare the contact sheet/render with Main's times to pick shots worth deeper study, then read each shot's full dependencies. Attribute a specific image to an effect only after comparing a preview on a safe copy; never open or change the original project on your own.

## Reading the Source and Reuse

This article keeps measurements and references from the recorded analysis; the project, evidence images and private reports are not distributed with the library. `evidence:` codes are source identifiers, not files needed to read the article. The source holder resolves them in local records; other contributors record their own sources and verification level. See [evidence conventions](../foundations/evidence-and-validation.md).
