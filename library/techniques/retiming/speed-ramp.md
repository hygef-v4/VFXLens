# Retiming and Speed Ramps

**Purpose:** Shape the apparent speed of action over time. No complete, render-verified speed-ramp curve has been confirmed from the current static project sources; this guide documents the inspection and recreation workflow.

## Distinguish Mechanisms Before Editing

| Mechanism | What It Actually Changes |
| --- | --- |
| Time Stretch / Time Remap / Retiming plugin | Mapping between source clip time and composition timeline |
| Speed ramp | Time-varying playback speed within a shot |
| Posterize Time | Sample-and-hold frame update cadence |
| Trails / Echo / Wide Time | Temporal accumulation or multi-frame blending |
| Motion blur | Directional motion smear (does not by itself prove retiming) |

## Proposed Recreation Workflow

1. Inspect source FPS, presentation timestamps/cadence, and baked-in cuts within the clip.
2. Identify the key action frame to accent and the surrounding slow-in / fast-burst / slow-out windows.
3. Shape the speed or Time Remap curve and verify that the source action lands on the intended beat.
4. Check optical-flow interpolation artifacts around hair, fast hands, occlusions, and scene cuts.
5. Add motion blur only after verifying motion at the target speed, and confirm the exact effect stacking order.

The mere presence of Twixtor on a layer does not prove an active speed ramp; always inspect static speed parameters, child property groups, Time Remapping, layer stretch, and parent precompositions. Twixtor retiming and RSMB motion blur solve distinct tasks; see [Render Effects](../../tools/render-effects.md).

**Sources and Limitations:** [Takt Op, Section 6](../../case-studies/takt-op.md#6-retiming-and-speed-ramps), [White Ferrari](../../case-studies/white-ferrari.md), [Chal7z: trails and wide time](../../case-studies/chal7z-presets.md). **Resource:** [Footage](../../resources/footage.md).
