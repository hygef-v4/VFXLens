# Cinematic camera, light and material

## Author a camera with a reason

Choose perspective to reveal scale/occlusion and orthographic for a stable
isometric system. Inspect framing at the delivery aspect ratio. Subject depth,
near/far clipping, lens/FOV, target and safe areas form one decision; moving the
camera without retargeting is not a reliable reveal.

Use absolute camera and target tracks. A locked hold remains locked; do not import
the remotionshorts helper's forced movement or fixed FOV clamp as universal rules.
For an imperative R3F camera, update before capture:

```tsx
const frame = useCurrentFrame();
const {camera} = useThree();
useLayoutEffect(() => {
  const u = interpolate(frame, [0, 90], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.2, 0, 0.2, 1),
  });
  camera.position.set(6 - 2 * u, 3, 8);
  camera.lookAt(0, 0.5, 0);
  camera.updateProjectionMatrix();
}, [camera, frame]);
```

Use Remotion/R3F imports for the named hooks and `Easing`. The delivery fps owns
conversion from seconds to the example frame keys. Smooth position and target
separately when their motion has different meaning. For paths, sample an authored
curve at absolute progress; inspect roll, tangents, velocity and acceleration at
joins. Ease-in/out at every key can produce repeated stopping; preserve travel
through a multi-key move when intended. Keep camera away from the look target.

## Light the subject, not every pixel

- Begin with key direction/size, fill ratio and rim separation. Use practical
  lights or a local warm pool against a cool set when the story needs a place.
- Check silhouette in grayscale; preserve contact shadows and usable face/label
  contrast. Brightest pixels should support the focal action.
- Metallic surfaces need something coherent to reflect. Use an authorized HDRI,
  light cards or geometric environment; a metalness value alone creates no look.
- Material scale, roughness, normals and color management matter before bloom.
  Keep a consistent renderer/tone-mapping pipeline; avoid applying output color
  conversion twice. Compare highlights and brand colors in the encoded result.
- Use bounded shadow frusta and an appropriate fixed map size. The local Three
  r187 removed PCFSoftShadowMap: R3F's `shadows="percentage"` selects supported
  PCF instead of relying on the older `shadows={true}` soft-map default.

## Focus and postprocessing

DOF is optional emphasis: focus tracks the subject, not an arbitrary plane.
Depth-of-field settings are not transferable numbers between engines. Check edges,
transparent objects, near-field blur and focus changes at real playback speed.
Keep captions outside the blurred pass; make 3D labels legible or mask them when
the chosen pipeline supports that intentionally.

Remotionshorts demonstrates ink/depth treatment followed by a two-stage lens blur,
bloom, tone mapping and grading. Adopt deliberate ordering, not its substantial
custom shader code. WebGL postprocessing wrappers are not interchangeable with a
WebGPU/TSL post graph. Add one pass at a time and inspect a pre/post still; remove
the pass when it obscures the story or exceeds the render budget.

See [source evidence](source-attribution.md#remotionshorts) and
[the local representative demo](../../../../studio/src/director/DirectorDemo.tsx).
