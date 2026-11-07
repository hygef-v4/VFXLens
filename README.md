# VFX Learning Engine — Phase 1

## Editing Knowledge Library

Browse the [Markdown Knowledge Library](library/README.md) by technique, style, resource, tool, and case study. Guides are designed to work independently of any personal asset collection, with source parameters and verification levels documented explicitly.

An independent analysis engine for **Adobe After Effects projects (`.aep` / `.aepx`)** and **VFX Videos (`.mp4` / `.mov` / FFmpeg)** on Windows (optimized for hardware with NVIDIA RTX 4060 8GB GPU and full CPU fallback support).

---

## 1. Core Features (Phase 1)

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
  - When After Effects or the MCP panel is not running, transparently records `live_bridge_tested = false` and operates standalone via the Offline Parser.
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

## 2. Windows Installation

### System Requirements
- Windows 10/11 (64-bit)
- Python >= 3.11 (tested on Python 3.14)
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg & FFprobe available in `PATH`

### Installation Steps
```powershell
# 1. Navigate to the repository directory
cd VFXLens

# 2. Initialize the virtual environment and install dependencies
uv sync --extra dev

# 3. Run environment diagnostics (Python, FFmpeg, RTX 4060 GPU, After Effects, Packages)
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

## 5. Detailed Documentation
- Research & evaluation of 9 GitHub repositories: [`docs/repository-research.md`](docs/repository-research.md)
- Technical limitations & untested live scenarios: [`docs/limitations.md`](docs/limitations.md)
- AI Agent guidelines: [`AGENTS.md`](AGENTS.md)
