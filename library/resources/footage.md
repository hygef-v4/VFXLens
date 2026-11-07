# Footage: Selecting Shots and Inspecting Stream Data

## Identification

Distinguish raw source footage, pre-interpolated "flow" packs, intermediate prerenders, demo edits, and final master renders. Sharing the same character or frame rate does not prove a clip is the original source asset of a project. A "4K" label in a filename does not replace actual resolution metadata, and a high container FPS does not prove every frame contains unique motion.

## Selection and Application

1. Choose shots based on physical action, motion direction, negative space for typography, and emotional tone.
2. Inspect resolution, aspect ratio, frame rate / presentation timestamps, duration, and audio tracks.
3. Check whether the clip already contains baked-in cuts, duplicate frames, retiming warps, LUTs/color grades, watermarks, HUDs, or subtitles.
4. Review handle frames before and after the main action when choosing `in`/`out` points; maintain directional continuity across cuts when desired.
5. Verify true frame cadence before applying slow motion, and check audio quality before mixing.
6. Crop or reframe deliberately; never assume upscaling a low-resolution clip restores lost detail.

## Common Pitfalls

Relinking footage solely by matching basenames or similar thumbnails without verifying content; assuming all authoring layers are actively rendered when a prerender layer sits above them; or mapping demo timestamps directly onto composition time simply because durations look similar. Keep measured metadata and direct visual observations separate from inferences.

**Related:** [Timing and Easing](../foundations/timing-and-easing.md), [Speed Ramp Retiming](../techniques/retiming/speed-ramp.md), [Takt Op Case Study](../case-studies/takt-op.md).
