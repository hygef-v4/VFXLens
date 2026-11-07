# Shake with a Decaying Envelope

**Purpose:** Create a sharp impact accent and smoothly return the frame to rest. This guide proposes a workflow informed by source-extracted envelopes; beat synchronization is not assumed across all reference sources.

## Proposed Recreation Workflow

1. Choose the accent frame and the settling window required to return to rest.
2. Keyframe a peak amplitude at the accent and decay it down to your baseline level.
3. Tune frequency, X/Y axes, and Z-tilt rotation to match the shot's motion direction; inspect easing handles and random seed if applicable.
4. Check frame edges during translation, rotation, or zoom; apply edge expansion/mirroring beforehand when needed and evaluate motion blur.
5. Toggle the shake effect on and off to verify that it reinforces the action rather than obscuring the subject.

## Units and Dependencies

A plugin's normalized `Amplitude` parameter does not directly equal pixels. Expression `wiggle()` and keyframed phase curves do not carry the same semantics as an amplitude envelope. Always check the layer's `in`/`out` trim points, keyframes falling outside the active trim range, and additional shake effects applied on parent precompositions.

**Evidence:** [Takt Op, Section 2](../../case-studies/takt-op.md#2-decaying-shake-after-an-accent) documents a decaying `Amplitude` curve; [White Ferrari](../../case-studies/white-ferrari.md) shows `Motion Tile` / `Mirror Edges` placed before `S_Shake`; [Chal7z](../../case-studies/chal7z-presets.md) preserves unscaled `.ffx` time units.

**Used In:** [Impact Style](../../styles/impact.md), [Dissolve-Shake Transition](../transitions/dissolve-shake.md).
