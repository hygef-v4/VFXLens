# Render and QA gates

## Configure the actual deliverable

Read the local `studio/package.json` and lockfile. Register width, height, fps,
duration and props explicitly. Frame intervals are half-open; a 120-frame clip
uses frames `0..119`. CLI range endpoints may be inclusive. Record renderer/backend,
DPR, seed, quality and concurrency. Use absolute input/output paths when invoking
from another directory; preserve original references and choose a fresh export.

In VFXLens, from the repo root:

```powershell
npm --prefix studio run typecheck
npm --prefix studio run still -- DirectorSkillDemo "<production>/frame-60.png" --frame=60
npm --prefix studio run render -- DirectorSkillDemo "<production>/demo.mp4" --codec=h264 --concurrency=2
```

The included demo is a silent four-second 1280×720/30fps composition. Its metadata
is a test contract, not a default for other films. It needs no private media.
Normal film assets and episode data stay in ignored production/media locations.

## Capture the right evidence

1. **Styleframe:** inspect the key subject/action against the chosen reference.
   Check stage depth, silhouette, contact, readable text and focal light.
2. **Moving proof:** render the hardest short interval. Inspect entrance/settle,
   camera speed, blur/focus, caption cues and adjacent cut frames at real speed.
3. **Seek proof:** render a middle frame directly from a fresh page, seek forward
   then backward, and repeat it. Compare pixels on the same backend; also compare
   that frame against sequential/concurrent output. Tiny GPU floating-point
   differences may need a documented tolerance; meaningful state changes fail.
4. **Export:** render the requested composition, fully decode the encoded file,
   inspect representative encoded frames/cut boundaries, verify audio presence
   against the brief, and listen when possible. A render exit code is insufficient.

The following helper uses Python's standard library plus installed FFmpeg/ffprobe:

```powershell
uv run python .agents/skills/remotion-3d-director/scripts/verify_render.py "<production>/demo.mp4" --width 1280 --height 720 --fps 30 --frames 120 --audio none --report "<production>/checks.json"
```

It checks exact dimensions, rational frame rate, decoded frame count, codec,
duration, audio policy and full decoding. It reads media only and creates a fresh
optional report. It does **not** certify visual quality, speech alignment, rights,
native WebGPU, or perceptual sound quality. A mismatch exits nonzero; treat it as
a failed check, not a warning to suppress.

For encoded inspection, use FFmpeg to extract chosen actual frame numbers and a
contact sheet; open the files. Include planned holds separately from unexpected
frozen frames. Luma/black-frame/flicker thresholds are diagnostic signals, not
universal aesthetic rules. A deliberately dark reveal should be reviewed in context.

## Asynchronous and compatibility failure checks

- Asset/font errors cancel rendering; release obsolete delay handles on cleanup.
  Verify the actual longest copy and Vietnamese glyphs with the loaded font.
- For WebGPU, run the extra [initialization/queue/seek tests](webgpu-shaders.md).
  Merely compiling node graphs or rendering a WebGL fallback is not GPU validation.
- Ensure source visibility, focus, exposure and material values restore on reverse
  seeks. Check cuts with both incoming/outgoing scenes, including transition overlap.
- Use a backend-specific short probe before changing CLI GL flags. Installed
  Three r187 still exposes removed/deprecated methods; feature existence is not
  a compatibility test.
- Watch memory, draw calls, shader/texture allocations and frame cost in the
  heaviest shot. Keep quality fixed during export; record any intentional fallback.

## Completion record

Deliver the file path, editable source/manifest, exact render command, contract
check report, frames/clips actually viewed, audio checks actually performed and
remaining limits. Keep local evidence in `local/productions/<slug>/` or `local/setup/`.
New skill discovery is a separate check: the frontmatter validator and direct
`$remotion-3d-director` task prove different things. A new Codex session may be
needed to refresh the skill catalog; do not claim UI discovery without observing it.

Sources: [QA patterns](source-attribution.md),
[ThreeCanvas](https://www.remotion.dev/docs/three-canvas),
[flicker/determinism](https://www.remotion.dev/docs/flickering).
