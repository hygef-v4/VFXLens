# Render Effects: Selecting by Problem

| Problem to Solve | Reference Tool Family | Check Before Selecting |
| --- | --- | --- |
| Variable speed and motion interpolation | [Twixtor](https://revisionfx.com/products/twixtor/) | Source FPS/cadence, retiming curve, occlusions, and warping artifacts |
| Estimate motion blur from pixel motion | [RSMB](https://revisionfx.com/products/rsmb/) | Source motion vectors, object silhouettes, and stack order |
| Map-driven spatial distortion | [Displacer Pro](https://aescripts.com/displacer-pro/) | Map/channel source, displacement amount, border behavior, and version |
| Progressive fill reveal within layer bounds | [AutoFill](https://aescripts.com/autofill/) | Source alpha/boundaries, growth origin, and timing |
| Glow, bokeh, color grading, camera shake | Built-in effects or dedicated third-party plugins | `matchName`, parameter units, effect stack order, and input color depth |

This is a task mapping rather than a purchasing or installation recommendation. Twixtor and RSMB solve two distinct problems, and the mere presence of a retiming effect does not prove an active speed ramp. Many effects can be approximated with native tools, though visual parity with a specific third-party plugin is not guaranteed.

## Reading Versions and `matchName`

Display names, project `matchName` strings, folder labels, and binary versions are distinct sources of information. Current vendor documentation may describe features or bug fixes absent in older binaries. For example, Displacer Pro's changelog notes fixes for scale and anti-aliasing; verify the exact version before comparing render output rather than assuming from a folder name.

Never assert a plugin name from rendered video pixels alone. When analyzing project files, record the exact instance, `enabled` state, parameter tree, and plugin version when readable. Automated classifiers provide leads until taxonomy is verified.

**Related Techniques:** [Speed Ramp Retiming](../techniques/retiming/speed-ramp.md), [Chromatic Displacement](../techniques/transitions/chromatic-displacement.md), [Glow, Color, and Bokeh](../techniques/lighting-and-color/glow-color-bokeh.md). **Sources:** [Takt Op](../case-studies/takt-op.md), [White Ferrari](../case-studies/white-ferrari.md).
