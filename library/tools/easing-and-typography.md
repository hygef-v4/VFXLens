# Easing and Typography Tools

## Selecting by Operation

| Task | Reference Tool | Dependencies / Limitations to Check |
| --- | --- | --- |
| Design and reuse easing curves | [Flow](https://aescripts.com/flow/) | Target curve and property compatibility; supported AE versions |
| Copy easing independently of values | [EaseCopy](https://aescripts.com/easecopy/) | Target keyframes and copy mode (ease vs. value) |
| Interpolate via expressions | [Ease and Wizz](https://aescripts.com/ease-and-wizz/) | External equation files, keyframe count, existing expressions |
| Stagger text by character/word/line | [TextEvo](https://aescripts.com/textevo/) | Pseudo-effect controls and linked text animator selectors |
| Split text into separate layers | [TextExploder](https://aescripts.com/textexploder/) | Font/style preservation, spatial layout, and host/version |

Flow shapes Bezier curves, EaseCopy transfers easing handles, and Ease and Wizz injects expressions: choose based on the workflow operation rather than treating them as interchangeable visual presets. Native After Effects keyframes/Graph Editor or built-in text animators can be used whenever they meet the goal; see [Timing and Easing](../foundations/timing-and-easing.md) and [Staggered Text](../techniques/typography/staggered-text.md).

## Lessons from Static Script Inspection

Static inspection of an Ease and Wizz 2.6.1 script showed that it loads equation files from `easingExpressions` and assigns an expression to properties that have at least two keyframes and support expressions. This demonstrates that standalone `.jsx` files can fail if companion directories are missing, and applying an expression tool can overwrite an existing expression on the property. Do not assume all versions behave identically to the inspected script; the script was not executed during static analysis.

TextEvo selectors and TextExploder split layers serve two distinct structural needs. If you only need per-character time offsets, keep a single text layer with an animator/controller; if each fragment needs independent parenting, 3D depth, or custom drop shadows, consider splitting into separate layers.

**Project Sources:** [Standard](../case-studies/standard.md), [Takt Op](../case-studies/takt-op.md), [AE Notes](../case-studies/ae-notes.md). Vendor links above describe the commercial products without certifying the reader's local installation.
