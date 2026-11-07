# Dissolve Combined with Shake

**Purpose:** Pair a visibility/dissolve transition with a decaying oscillation to introduce or bridge layers across a cut. No standalone render-verified preset is assumed; see [Takt Op, Section 3](../../case-studies/takt-op.md#3-dissolve-combined-with-shake) and [White Ferrari](../../case-studies/white-ferrari.md) for source-extracted parameters.

## Proposed Recreation Workflow

1. Identify the incoming/outgoing layer and the underlying background shot being revealed.
2. Keyframe the dissolve progression according to the specific plugin's semantics; never assume a parameter value of `0` always means fully transparent.
3. Keyframe a sign-reversing oscillation that damps down to rest, distinguishing phase, amplitude, and frequency controls.
4. When stacking a separate camera shake layer on top, verify that the two envelopes do not compound excessively or extend beyond the layer's active `in`/`out` span.

## Dependencies and Inspection

Record layer `in`/`out` points, alpha, blending mode, dissolve percentage, per-axis phase keyframes, amplitude/frequency, and easing. Preview both the local layer and the parent composition against the background as visibility changes. Sign-reversing phase keyframes prove explicit phase control, but do not by themselves specify every static parameter of the plugin.

**Further Reading:** [Shake Envelope](../camera-and-motion/shake-envelope.md), [Timing and Easing](../../foundations/timing-and-easing.md), [Scripts and Presets](../../tools/scripts-and-presets.md).
