# VFXLens

**Learn from reference edits, then make your own videos with an AI agent.**
VFXLens analyzes After Effects projects and VFX videos offline, keeps what it learns in an editing knowledge
library, and gives Claude Code or Codex a production pipeline for vertical Shorts: three.js picture, Remotion
captions and mix, optional ElevenLabs voice.

<p align="center"><img src="docs/media/hello-short.gif" alt="Frames from the hello-short demo: a 3D cartoon presenter at an office desk, wide shot to close-up, with word captions" width="270"></p>

## What is inside

| Part | What it does | Entry point |
| --- | --- | --- |
| **Analyzer** (`vfx` CLI) | Reads `.aep`/`.aepx` projects without opening After Effects (layers, effect stacks, keyframes, expressions) and analyzes videos frame by frame (cuts, flashes, shake, speed ramps, glow…) | [CLI usage](#3-cli-usage-vfx) |
| **Studio** (Remotion) | `ThreeShort` assembles a three.js picture with word captions, light leaks, voice, ducked music and peak-aligned SFX | [`ShortAssembly.tsx`](studio/src/shorts/ShortAssembly.tsx) |
| **Long-form 2D kit** | `LongForm-<slug>`: SVG puppets, night lighting, GSAP text cards and labels, maps, polaroid ending, three.js shots; per-line ElevenLabs voices, timeline and ducking scripts | [2D long-form workflow](workflows/2d-long-form-video.md) |
| **Short toolkit** | Scaffold, starter film, voice timing (`tighten`, `evenpace`, `fit`, `align`), manifest builder, render script, perceptual QA | [three.js Short workflow](workflows/threejs-character-short.md) |
| **Agent skills** | `vfxlens` (router), `remotion-3d-director`, `longform-2d`, `motion-scout` for Claude Code and Codex | [`skills/vfxlens`](skills/vfxlens/SKILL.md), [`AGENTS.md`](AGENTS.md) |
| **Knowledge library** | Techniques, styles, resources and evidence-labelled case studies | [`library/`](library/README.md) |

## Quick start

Requirements: Python ≥ 3.10 with [uv](https://docs.astral.sh/uv/), Node.js ≥ 22, FFmpeg/ffprobe on `PATH`.

```bash
uv sync --locked --extra dev          # analyzer
uv run vfx doctor                      # check the environment
npm --prefix studio ci                 # Remotion studio
npm --prefix studio run studio         # preview compositions in the browser
```

**Render the demo Short** (no API key needed; also needs the
[`claude-3d-animated-shorts`](https://github.com/thuann-vn/claude-3d-animated-shorts) skill installed for its 3D engine):

```bash
python studio/tools/threejs-short/scaffold.py hello-short   # creates local/productions/hello-short/
cd local/productions/hello-short                              # write your lines into script.json first
python voice/silent_timing.py                                 # draft timing + silent voice track (no TTS)
(cd audio && python music_fallback.py)                        # procedural music
OUTV=v1 bash render_fast.sh                                   # picture, assembly, loudness, verify, audit
```

Swap in a real voice later with the ElevenLabs steps in the [workflow](workflows/threejs-character-short.md).

**Render the 2D long-form demo** (no API key, no extra skill):

```bash
python studio/tools/longform-2d/scaffold.py demo-2d
cd local/productions/demo-2d
python ../../../studio/tools/longform-2d/voice_lines.py --silent   # draft voice timing, no credits
python ../../../studio/tools/longform-2d/build.py                  # timeline + manifest
cd ../../../studio && npx remotion render src/index.ts LongForm-demo-2d ../local/productions/demo-2d/renders/demo.mp4
```

## Workflows

| Task | Start here |
| --- | --- |
| Study a reference video, PDF or AE project | [study-reference](workflows/study-reference.md) |
| Write a script, hook or narration | [Content Writing](library/content-writing/README.md) |
| Make a story Short with 3D cartoon characters | [threejs-character-short](workflows/threejs-character-short.md) |
| Make a long-form 2D explainer or story (16:9) | [2d-long-form-video](workflows/2d-long-form-video.md) |
| Make or continue any video | [create-video](workflows/create-video.md) |
| Diagram/isometric/cartoon explainer | [ai-assisted-motion-graphics](workflows/ai-assisted-motion-graphics.md) |
| Direct cinematic 3D | [remotion-3d-director](.agents/skills/remotion-3d-director/SKILL.md) |
| Find current animation technology | [motion-scout](skills/motion-scout/SKILL.md) |

Agents read [`AGENTS.md`](AGENTS.md) (Claude Code loads it through `CLAUDE.md`); it routes each request to a workflow
and proposes the skills to use. Register the repository skills for both agents:

```powershell
foreach ($skillName in 'vfxlens', 'motion-scout', 'remotion-3d-director', 'longform-2d') {
    uv run python skills/motion-scout/scripts/sync_skill.py --skill $skillName
}
```

See [setup](skills/motion-scout/references/capabilities-and-setup.md) for link checks, the
[requirements guide](docs/ai-video-requirements.md) and the [toolchain map](docs/full-toolchain.md) for optional tools,
and [docs/limitations.md](docs/limitations.md) for known analyzer limits. Productions and their media stay in ignored
`local/productions/<slug>/` and `studio/public/media/`; a fresh clone contains none.

---

## 1. Analyzer features

### A. After Effects Project Analyzer (`project_analyzer`)
- **Method A — Offline Binary/XML Parser (`offline_py_aep` & `offline_aepx`)**:
  - Directly reads binary `.aep` files (RIFX/RIFF via `py-aep`) and XML `.aepx` files (via XML-to-RIFX transcoder + XML DOM fallback) **without opening After Effects**.
  - Extracts comprehensive project data:
    - Project metadata, AE version (`ae_version`), color bit depth (`bits_per_channel`), `working_space`, `expression_engine`.
    - Composition & Precomposition inventory, dependency graph (`composition_hierarchy`).
    - Layer hierarchy, parenting (`parent_index`), Track Matte (`Alpha`/`Luma`), Blending Mode, 3D switch, Adjustment Layer, Collapse Transformation, Motion Blur, Time Remapping.
    - Transform, Masks (`ADBE Mask Parade`), Shapes, Text Animators (`ADBE Text Animators`), 3D Cameras & Lights.
    - **Full Effect Stack (`ADBE Effect Parade`) in exact layer order**, including third-party plugins (**Boris FX Sapphire `S_*`, Continuum `BCC*`, Deep Glow, Maxon Trapcode, Video Copilot Element 3D/Optical Flares, RE:Vision Twixtor/RSMB**).
    - Effect parameters (`EffectParameterSchema`), static values, Keyframe timing/values, interpolation (`LINEAR`, `BEZIER`, `HOLD`), temporal/spatial easing, and JavaScript/ExtendScript Expressions source code.
    - Missing footage detection (`missing_assets`) and third-party plugin inventory (`missing_effects`).
  - **Strict Safety Guarantees**:
    - Explicitly distinguishes `.aep` (binary project), `.aepx` (XML project), and `.aex` (Windows DLL binary plugin). **Refuses to open or execute `.aex`** (`UnsafeFileError`).
    - Verifies `SHA-256` checksums before and after reading (`ReadOnlyFileGuard`) to ensure the original project file is never modified.
- **Method B — After Effects Read-Only Live Bridge (`ae_bridge`)**:
  - Supports read-only connection to JUNKDOGE `after-effects-mcp` (`http://127.0.0.1:11488/mcp`) or Solomon `aftereffects-mcp` (`http://127.0.0.1:7788/call`) alongside `ae-scripts/vfx_readonly_extract.jsx`.
  - Blocks all project write/save/mutation commands (`FORBIDDEN_JSX_PATTERNS`).
    - When After Effects or the MCP panel is not running, transparently records `live_bridge_tested = false` and operates standalone via the Offline Parser. Preview arguments are serialized as data and require a fresh PNG destination; actual host rendering needs a separate live check.
- **Normalizer & Comparator (`normalizer`)**:
  - Normalizes outputs with explicit epistemic provenance: `observed`, `inferred`, `unavailable`, `unsupported`, `error`.

### B. Video VFX Analyzer (`video_analyzer`)
- Decodes MP4, MOV, and all FFmpeg-supported formats via `ffprobe` + OpenCV, extracting **exact presentation timestamps (`pts_time`)** per frame and automatically detecting **Variable Frame Rate (VFR)**.
- **Adaptive & Full-Frame Analysis**:
  - Performs full-frame analysis (`full_frame_with_adaptive_windows`) on short/fast VFX clips (5–20 seconds, including 60 FPS clips with 0.1-second = 6-frame micro-effects), combined with high-activity window detection (`high_activity_windows`).
- **Visual & Motion Signal Detectors**:
  - `scene_cut` (Hybrid PySceneDetect + per-frame 12x9 grid RGB change)
  - `flash_frame` (Luminance impulse & highlight saturation)
  - `camera_shake` (High-frequency global optical flow velocity sign reversals)
  - `zoom_punch_transition` (Radial optical flow expansion/contraction)
  - `speed_ramp` (Intra-scene optical flow velocity dynamic envelope)
  - `motion_blur` (Structure-tensor gradient anisotropy + Laplacian sharpness drop)
  - `rgb_split_chromatic_aberration` (Phase correlation R-G / R-B spatial edge offset + chromatic fringe)
  - `glow_bloom` (Annular highlight halo luminance excess)
  - `distortion_displacement` (Non-affine optical flow residual + horizontal scanline tear)
  - `motion_trail_echo` (Lagged edge residual correlation)
  - `masking_reveal` (Progressive partial-grid boundary wipe)
  - `particles_overlay` (Morphological Top-Hat moving high-contrast speckles)
  - `kinetic_typography_candidate` & `camera_3d_parallax`
- **Epistemic Separation**:
  - Clearly separates: `observations` (measured directly from frames), `possible_ae_techniques` (plausible AE recreation workflows), `possible_plugins` (suspected plugins — `verified: false`, never claiming plugin identity with certainty from MP4 pixels alone), and `undetermined_parameters`.

---

## 2. Installation

### System Requirements
- Windows, macOS or Linux (developed and CI-tested on Windows)
- Python >= 3.10 (tested on Python 3.14)
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg & FFprobe available in `PATH`

### Installation Steps
```powershell
# 1. Navigate to the repository directory
cd VFXLens

# 2. Initialize the virtual environment and install dependencies
uv sync --extra dev

# 3. Run environment diagnostics (Python, FFmpeg, GPU, After Effects, packages)
uv run vfx doctor
```

---

## 3. CLI Usage (`vfx`)

### 3.1. Environment Diagnostics
```powershell
uv run vfx doctor
uv run vfx doctor --json
```

### 3.2. Analyze an After Effects Project (`.aep` / `.aepx`)
```powershell
uv run vfx analyze-project "path/to/project.aep" --output outputs/run1
```
Generated artifacts in `outputs/run1/`:
- `project-analysis.json`: Normalized JSON conforming to `ProjectAnalysisResult`.
- `project-report.md`: Detailed Markdown report covering Compositions, Layers, Effect Stacks, Keyframes, Expressions, and Missing Assets.

### 3.3. Analyze a VFX Video (`.mp4` / `.mov`)
```powershell
uv run vfx analyze-video "path/to/video.mp4" --output outputs/run2
```
Generated artifacts in `outputs/run2/`:
- `video-analysis.json`: Normalized JSON conforming to `VideoAnalysisResult`.
- `timeline.json`: Per-frame / exact-timestamp signal series (`FrameSignalEntry`).
- `video-report.md`: Markdown report detailing scene cuts, VFX events, plausible AE techniques, and candidate plugins.
- `contact-sheet.jpg`: Annotated contact sheet of representative event frames.
- `evidence-frames/`: Directory containing exported evidence frames (`frame_00030_1.000s.jpg`, ...).

### 3.4. Batch Folder Analysis
```powershell
uv run vfx analyze-folder "path/to/folder" --recursive --output outputs/batch1
```
Automatically analyzes all `.aep`, `.aepx`, and video files in the folder while safely skipping `.aex` binary plugins and writing `batch-summary.json`.

### 3.5. Quick Terminal Inspection
```powershell
uv run vfx inspect "outputs/run1/project-analysis.json"
uv run vfx inspect "outputs/run2/video-analysis.json"
```

---

## 4. Running the Test Suite

Some deep integration tests on RIFX binary files (`.aep` AE 2026) use reference sample files from `references/py-aep`. On a fresh clone (since `references/` is listed in `.gitignore`), provision the reference sample with:

```powershell
# Clone the py-aep reference repository (only needed once on a fresh clone)
git clone https://github.com/forticheprod/py-aep.git references/py-aep

# Run the full test suite
uv run pytest -v
```
*(If `references/py-aep` is not present, tests that depend on the external sample will automatically `SKIP` with actionable setup instructions instead of raising an `AssertionError`, while all self-contained tests continue to run normally.)*

---

## 5. More documentation
- Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md) · Security: [`SECURITY.md`](SECURITY.md) · Changes: [`CHANGELOG.md`](CHANGELOG.md)
- Technical limitations & untested live scenarios: [`docs/limitations.md`](docs/limitations.md)
- AI Agent guidelines: [`AGENTS.md`](AGENTS.md)

---

## License

VFXLens is released under the [MIT License](LICENSE) © 2026 chal7z.

- Remotion, which the studio uses to render, has its own [licence](https://www.remotion.dev/license): free for
  individuals and companies of up to three people; larger companies need a company licence.
- Adapted code and dependency notes are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- Case studies in `library/` describe and measure third-party works for education; their media and source files are not included.
- Optional services such as ElevenLabs follow their own terms; nothing in the repository calls a paid service by default.
