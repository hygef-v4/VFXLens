# Overlays and Audio Visualizers

**Purpose:** Composite secondary atmospheric or graphic layers over primary footage; for audio visualizers, verify the actual link between visual geometry and the audio source rather than guessing from appearances.

## Proposed Recreation Workflow

1. Define the layer's visual role: foreground framing, light accent, depth atmosphere, graphic callout, or audio-reactive spectrum.
2. For pre-rendered overlay assets, inspect alpha/background, timing, and blending mode following [Overlays](../../resources/overlays.md).
3. For an audio visualizer effect, configure the target audio layer, frequency band/display mode, geometry, gain, and blending mode.
4. Test by swapping or muting the audio source and toggling the layer to confirm its actual audio reactivity and visual contribution.
5. Verify visual hierarchy: do faces, typography, and primary action remain clearly legible?

## Current Evidence Level

[Takt Op, Section 7](../../case-studies/takt-op.md#7-overlays-and-audio-visualizer) records an active `BCC_AUDIOVISUALIZER` instance on a solid layer, but static offline analysis has not confirmed which graphic lines in the demo video originate from that effect or react to audio. It is therefore not yet a complete, verified visualizer recipe.

**Used In:** [Dreamy Style](../../styles/dreamy.md) and [Collage Style](../../styles/collage.md). **Foundations:** [Compositing](../../foundations/compositing.md).
