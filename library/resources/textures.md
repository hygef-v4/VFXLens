# Textures: Selecting Surface Overlays and Blending

## Identification

Paper, plastic wrap, film grain, scratches, dust, and lens dirt can be still images or video loops. Always inspect the actual pixels: a filename containing `PAPER` does not guarantee a bright white background, and `Film Burn` does not prove authentic celluloid halation. Distinguish full-frame surface textures from lens dirt that should only light up around bright highlights.

## Selection and Application

1. Decide whether the shot needs tactile surface grain, contrast shaping, vintage aging, or foreground lens detail.
2. Check resolution, background luminance (white, black, or neutral 50% gray), alpha channel, and grain scale at final export dimensions.
3. Test `Multiply` for dark ink/folds on a white background; `Overlay` or `Soft Light` for neutral-gray contrast textures; and `Screen` for bright dust/scratches on a black background. Compare candidates visually.
4. Dial in opacity and mask/localize the coverage so skin tones, eyes, and typography remain clean and legible.
5. When animating a still texture (e.g., stepped position/rotation jumps for a stop-motion paper feel), drive it deliberately rather than mistaking a high-res still for a video loop.

## Common Pitfalls

Non-uniformly stretching a texture and warping grain/scratches; choosing a blend mode that crushes shadows or lifts blacks; leaving a surface texture static when it is supposed to track a moving cutout; or exposing an obvious loop cut. Never apply a blind opacity or scale value across unrelated shots.

**Related:** [Compositing Foundations](../foundations/compositing.md), [Retro / VHS Style](../styles/retro-vhs.md), [Collage Style](../styles/collage.md). Cross-reference [Standard](../case-studies/standard.md): even when a texture layer is present in a composition, verify the active render path and prerenders.
