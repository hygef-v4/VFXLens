# Story to scene composition

## Shot contract

Maintain this information in the existing production document or its linked shot
data; the fields are a useful interface, not a requirement for a new schema file.

| Field | Decision it carries |
| --- | --- |
| ID, `[start,end)` and local origin | Exact scheduling and audio/caption mapping |
| Takeaway and evidence | What becomes understandable; source/status for factual claims |
| Subject/action | Character, product, prop or diagram change that carries the idea |
| Blocking | Positions, contact, silhouettes, foreground/midground/background |
| Camera | Start/end position and target, lens, move purpose, holds/cut |
| Look | Key/fill/rim, focal contrast, palette, material and focus plane |
| Event IDs | Narration, readable hold, reveal, SFX, outgoing handoff |
| Review frames | Entrance, peak action, contact, text completion, exit/cut neighbors |

Example creative specification: at `[90,210)` on a 30fps timeline, an opaque shell
opens to expose a processing core; data reaches the core only after the reveal.
A camera arc changes occlusion so the internal relationship becomes visible.
The opening lands before the label's readable hold. These timings are a proposed
shot, not extracted facts or universal settings.

## Compose by explanatory responsibility

- Product film: silhouette → material/detail → meaningful operation → payoff.
- 3D explainer: introduce an entity → change a connection/state → expose a
  mechanism/scale → revisit the same objects in a recap.
- Character explainer: establish place and recurring prop → pose/expression and
  action → consequence → next location/question. Preserve rig proportions and
  prop attachments; keep foot/hand contact in frame.
- Social composite: footage/world → behind-subject content → subject → front
  accents → screen captions. A heuristic face guard is not a verified matte.

Use explicit authored scene instances when independent editing matters. External
shot data can drive a template, but explain which parts are data-controlled.
Avoid mounting a WebGL context for every small object; share a world per shot or
continuous set. Keep screen-readable typography/captions outside the 3D canvas
unless perspective or occlusion is part of their purpose.

## Data paths and transitions

For a particle moving from `a` to `b`, use an absolute phase, not an integrator:

```ts
const t = localFrame / fps;
const phase = ((t * cyclesPerSecond + particleSeed) % 1 + 1) % 1;
const position = a.clone().lerp(b, phase);
```

For large fields, reuse vectors and arrays or evaluate in a shader; the snippet
expresses the math, not an allocation strategy. Seeds identify particles and
remain stable between frames. Curve paths need a meaningful direction and label;
decorative flowing dots do not establish technical causation.

Use object/gesture matches or camera continuation when they preserve meaning.
For a crossfade of `a` and `b` frames with `o` frames overlap, the combined span is
`a+b-o`; both worlds exist during the overlap and double resource cost. Avoid
unintended inherited visibility or additive audio. A hard cut plus a short
intentional settling action is often clearer than an expensive transition.

VFXLens style references: [character staging](../../../../library/styles/cartoon-explainer.md),
[isometric explanation](../../../../library/styles/isometric-explainer.md).
Source patterns: [explainer-3d](source-attribution.md#explainer-3d),
[remotionshorts](source-attribution.md#remotionshorts),
[facecammaxxing](source-attribution.md#facecammaxxing).
