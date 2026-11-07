# Matte Reveal and Wipe Transitions

**Purpose:** Use the luminance or alpha channel of one layer to drive the visible region of another layer. Applicable to custom wipes, ink bleeds, procedural noise masks, and graphic frames; this guide presents a proposed working workflow.

## Proposed Recreation Workflow

1. Place outgoing shot A as the base layer and incoming shot B above it.
2. Choose the matte type: `Alpha Matte` when the control layer carries true transparency, or `Luma Matte` when luminance drives visibility.
3. With a standard `Luma Matte`, bright white reveals shot B and black hides it; invert the matte when the opposite direction is needed.
4. Trim or retime the matte clip to match the transition beat, verifying full coverage at both the start and end of the wipe.
5. Inspect transition edges and mid-gray feathering before boosting contrast or applying a hard threshold.

As documented in [Adobe: Track mattes and traveling mattes](https://helpx.adobe.com/after-effects/desktop/work-with-transparency-and-compositing/work-with-track-mattes-and-traveling-mattes/track-mattes-and-traveling-mattes.html), alpha and luminance are two distinct control signals. A black-and-white MP4 clip is fully opaque (`Alpha = 1.0` everywhere), so assigning it as an `Alpha Matte` will not produce the intended wipe reveal.

## Common Pitfalls

Picking the wrong matte channel or inversion state; using a matte asset that fails to reach full white/black at the transition endpoints; scaling up a low-resolution matte and exposing blocky edges; or retiming the matte layer without adjusting the overlap of shots A and B. Direct plugin wipe effects documented in case studies represent an effect-based alternative rather than proof that a separate footage matte layer was used.

**Further Reading:** [Overlays](../../resources/overlays.md), [Compositing Foundations](../../foundations/compositing.md), [The Less I Know: keyframed plugin wipes](../../case-studies/the-less-i-know-the-better.md).
