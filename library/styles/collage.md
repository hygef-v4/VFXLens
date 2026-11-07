# Collage

**Defining Characteristics:** Multiple image cutouts, text fragments, or icons with distinct borders, layered overlap, framing elements, tactile textures, and shifting layouts. This is an orienting description—not every collage requires every element.

## Proposed Assembly Workflow

1. Establish the spatial layout and reading order; place the background and primary subject.
2. Add [cutouts and frames](../resources/cutouts-and-frames.md), preserving proportions and negative space for typography.
3. Choose [fonts](../resources/fonts.md) or ransom/paper-cut letter assets; unify stroke borders and drop shadows.
4. Drive group motion via a parent Null/camera or transform, then layer in [staggered text](../techniques/typography/staggered-text.md) if needed.
5. Add subtle [textures](../resources/textures.md) and sound effects; preview at real-time playback speed.

## Inspection Checklist

Verify layer stacking order, alpha edges, shadow direction, text legibility, and frame borders; check whether cutout pieces move within a coherent coordinate space. Adding a 3D Camera does not create parallax if all layers remain at the same Z depth. Avoid keyframing every cutout individually when a parent Null controller suffices.

**Case Studies:** [The Less I Know](../case-studies/the-less-i-know-the-better.md) demonstrates camera/Null parenting and drop shadows; [Standard](../case-studies/standard.md) illustrates text/sticker layering across two layout setups. These document specific techniques without claiming every layer is visible in a final prerender.
