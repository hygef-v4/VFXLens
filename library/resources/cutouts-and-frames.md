# Cutouts, Stickers, and Frames

## Identification

Cutouts isolate subjects from their background; stickers may include baked-in strokes or drop shadows; frames combine opaque borders with transparent apertures; rasterized ransom/paper-cut letter images are not editable text layers. Check transparency on indexed-palette PNGs as well as RGBA files, and distinguish a baked-in checkerboard pattern from a real alpha channel.

## Selection and Application

1. Inspect silhouette edges over both bright and dark backgrounds and check the final display scale, especially for small paper-cut letter graphics.
2. Position the anchor point around the natural pivot for rotation or scaling while preserving aspect ratio.
3. Use `Normal` blending when preserving opaque colors and alpha contours. When adding strokes or drop shadows, keep stroke weight and light direction consistent across pieces.
4. For collages, animate pieces via parent groups or Null controllers first, then introduce deliberate stagger offsets.
5. For multi-panel frames or split screens, place clips beneath the frame apertures and mask each clip so it does not bleed into adjacent cells.
6. Re-check face and title placement after adding letterbox or framing borders; a "Cinemascope" filename does not guarantee standard top/bottom matte bars.

## Common Pitfalls

Upscaling low-resolution cutouts excessively; using `Screen` blend mode and losing dark interior details; inconsistent shadow angles across collage pieces; assuming a three-hole PNG frame automatically crops three footage layers without individual masks; or applying text-animator scripts like TextEvo to raster letter images.

**Related:** [Collage Style](../styles/collage.md), [Staggered Text](../techniques/typography/staggered-text.md), [Standard: matte borders](../case-studies/standard.md), [The Less I Know: shadow/camera setup](../case-studies/the-less-i-know-the-better.md).
