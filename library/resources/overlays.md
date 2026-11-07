# Overlays: Light, Atmosphere, and Mattes

## Identification

- **Light leaks, bokeh, electricity, or particles on black:** Check whether the black background is truly clean (`RGB 0,0,0`) and whether any dark interior colors need to be preserved.
- **Discrete objects (butterflies, petals, debris):** Verify whether a true alpha channel is present; a `.mov` container does not guarantee transparency.
- **Smoke, fog, or haze:** Inspect density and spatial coverage over time; a dark first frame does not mean the clip is empty.
- **High-contrast black-and-white wipes filling the frame:** Often designed to act as Luma Mattes driving a reveal rather than decorative layers placed directly over the image.
- **Baked-in HUDs, viewfinder text, or borders:** Inspect the full clip beforehand so baked graphics do not surprise you in the composite.

## Selection and Application

1. Define the editorial role: highlight accent, atmospheric depth, action hit, or scene transition.
2. Check alpha presence, resolution, FPS, duration, and sample frames across the clip.
3. For objects with true alpha: start with `Normal`. For bright elements on a clean black background: test `Screen` or `Add`. For transition wipes: assign as `Alpha Matte` or `Luma Matte`.
4. Align the emission point or motion origin with the scene's light source or physical action; trim the strongest segment rather than forcing the entire clip duration.
5. Match color temperature, scale, softness/defocus, subject occlusion, and camera drift to the base shot; toggle the overlay on and off to verify its contribution.

## Common Pitfalls

Using `Screen` on opaque objects and losing dark body details; heavy fog lifting black levels into a milky gray; `Add` clipping highlight detail; obvious loop repetitions; or electricity/shockwaves floating detached from the subject's motion. Always inspect alpha interpretation before reaching for a keyer. Blending choices follow [Compositing Foundations](../foundations/compositing.md) rather than fixed preset rules.

**Related:** [Dreamy Style](../styles/dreamy.md), [Impact Style](../styles/impact.md), [Matte Reveal Transition](../techniques/transitions/matte-reveal.md). Project example: [White Ferrari](../case-studies/white-ferrari.md).
