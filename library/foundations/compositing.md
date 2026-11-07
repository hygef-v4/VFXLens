# Compositing: Alpha, Blend, and Matte

**Purpose:** Choose the compositing method based on the asset's actual channel data and visual role.

## Three Mechanisms to Distinguish

- **Alpha** describes transparency. A PNG or MOV file may or may not contain an alpha channel; inspect the actual channels and pixels.
- **Blend mode** combines color values between layers. Try Screen/Add for bright elements on a dark background, or Multiply for dark strokes on a bright background; decide by previewing rather than trusting pack names.
- **Matte** controls the visible region of another layer. Luma Matte uses luminance, while Alpha Matte uses transparency; invert the matte when you need to swap visible and hidden areas.

Straight and premultiplied alpha must be interpreted properly. If an object's silhouette exhibits dark or bright fringing, check **Interpret Footage** before keying or choking edges. See [Adobe: Alpha channels, masks, and mattes](https://helpx.adobe.com/after-effects/desktop/work-with-transparency-and-compositing/work-with-alpha-channels-and-masks/alpha-channels-masks-mattes.html).

Screen does not replace a true alpha channel when dark object regions must remain opaque. Add can push highlights aggressively; watch skin tones and bright regions. Gray-, bright-, and dark-backed textures require different blending modes. See [Adobe: Blending modes and layer styles](https://helpx.adobe.com/after-effects/desktop/work-with-layers/work-with-layer-blending-modes/blending-modes-layer-styles.html).

## Order of Operations and Frame Edges

Transforms, effects, mattes, and precompositions interact with one another; record the exact stack order of an example rather than merely listing plugin names. When applying camera shake, zoom, or warp effects, check whether frame borders pull inward and expand edges beforehand if appropriate. Motion Tile / Mirror Edges is one option, though mirrored borders can introduce unwanted reflections.

**Inspection Practice:** Test against both light and dark backgrounds to inspect contours; solo/toggle individual layers; check both steady frames and motion peaks. Neither keep a layer solely because it carries a well-known plugin nor delete a disabled layer before checking its dependencies.

**Further Reading:** [Overlays](../resources/overlays.md), [Cutouts and Frames](../resources/cutouts-and-frames.md), [Matte Reveal Transition](../techniques/transitions/matte-reveal.md).
