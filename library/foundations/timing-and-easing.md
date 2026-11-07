# Timing and Easing

**Purpose:** Align motion with action and musical rhythm while keeping time units unambiguous. This is a general guide; numeric values in case studies belong strictly to their named sources.

## Distinguish the Clocks

- A video stream has its own presentation timestamps and FPS; compositions and precompositions can differ in frame rate, start time, time stretch, or Time Remapping.
- A span of `n` frames at frame rate `f` equals `n / f` seconds within that specific timebase. Do not map precomposition time directly to a demo render's timeline without checking nested offsets and time remapping.
- Still images carry no intrinsic edit duration. Image sequences require an interpreted frame rate, and preset files (`.ffx`) may store raw time units without an explicit composition FPS.
- High-FPS encoded videos may contain duplicate frames. Until frame cadence is measured, do not assume extra motion samples exist for smooth slow motion.

## Designing a Motion Curve

1. Identify the action landmarks: anticipation/start, peak accent, and settled rest state.
2. Block out values at those landmarks and preview at real-time playback speed.
3. Shape incoming/outgoing easing curves to control acceleration; use `HOLD` keyframes for deliberate stepped state changes.
4. When adding overshoot or camera shake, verify the decay envelope and resting end state rather than merely cranking up peak amplitude.
5. Across multiple layers or text characters, distinguish stagger offset (start delay) from each element's individual duration and easing curve.

## How to Verify

Inspect both the local keyframe graph and the composite result inside the parent composition; check motion blur, frames immediately before and after cuts, and expression dependencies. Never conclude a speed ramp is active merely because Twixtor is present on a layer. See [Speed Ramp Retiming](../techniques/retiming/speed-ramp.md) and [Staggered Text](../techniques/typography/staggered-text.md) for detailed workflows.

**Cross-References:** [White Ferrari: Posterize Time and prerenders](../case-studies/white-ferrari.md), [Chal7z: FFX preset time units](../case-studies/chal7z-presets.md).
