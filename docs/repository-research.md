# GitHub Repository Research & Evaluation Report (`docs/repository-research.md`)

This document summarizes the empirical inspection, source code analysis, architecture review, license verification, Windows compatibility check, and maturity evaluation of the 9 reference repositories cloned into `references/` (which is excluded via `.gitignore` to keep third-party checkouts separate from the main source tree).

---

## 1. Repository Status & Metrics Summary

| Repository | Category | Status | Primary Language | Stars / Forks | Commits / Contributors (Inspected) | License | Windows Compatibility | Adoption Decision |
|---|---|---|---|---|---|---|---|---|
| [`forticheprod/py-aep`](https://github.com/forticheprod/py-aep) | AEP Parsing | Actively maintained (updated 11/2026) | Python | 81 ⭐ / 14 🍴 | >50 recent commits / 7+ contributors (Fortiche Production) | **MIT** (full `LICENSE` file present) | **Excellent** (OS Independent, pure Python + `struct`, `attrs`, `fonttools`, `uharfbuzz`) | **SELECTED AS CORE PACKAGE** (`py-aep` via PyPI/dependency) for the Offline `.aep` Parser |
| [`ChenxingM/AEP-Tools`](https://github.com/ChenxingM/AEP-Tools) | AEP Parsing | Active (updated 09/2026) | Python + Rust (`PyO3`/`maturin`) | 7 ⭐ / 0 🍴 | ~50 commits / 1 contributor | Declares `license = "MIT"` in `pyproject.toml` but **lacks a root `LICENSE` file** | Moderate (requires Rust toolchain & `maturin` to build `_core`, has pure-Python fallback) | **DO NOT COPY CODE** (due to missing explicit `LICENSE` file); consult RIFX/AEPX format documentation only to build a clean-room `.aepx` parser |
| [`boltframe/aftereffects-aep-parser`](https://github.com/boltframe/aftereffects-aep-parser) | AEP Parsing | Unmaintained (since 02/2022) | Go + Kaitai Struct | 131 ⭐ / 13 🍴 | 22 commits / 3 contributors | **MIT** (`LICENSE` file present) | Runs via Go runtime | **SKIPPED FOR DIRECT INTEGRATION** (written in Go; much lower chunk coverage than `py-aep`) |
| [`JUNKDOGE-JOE/after-effects-mcp`](https://github.com/JUNKDOGE-JOE/after-effects-mcp) | After Effects MCP | Actively maintained (v0.11.1, 10/2026) | JS / ExtendScript (`.jsx`) / C++ AEGP | 90 ⭐ / 8 🍴 | 59+ commits / 4 contributors | **MIT** (`LICENSE` file present) | **Good** (supports Windows x64 + CEP + HTTP `:11488/mcp` + Named Pipe) | **SELECTED FOR ADAPTER SUPPORT** in `ae_bridge` (Read-only connection over HTTP `:11488/mcp` and snapshot-copy pattern inspired by `readonly-worker.jsx`) |
| [`solomondivyananth/aftereffects-mcp`](https://github.com/solomondivyananth/aftereffects-mcp) | After Effects MCP | Active (10/2026) | Node.js / ExtendScript (`bridge.jsx`) | 81 ⭐ / 9 🍴 | 19 commits / 1 contributor | **MIT** (`LICENSE` file present) | **Good** (CEP panel listening on HTTP `127.0.0.1:7788`, token at `~/.ae-mcp-bridge.json`) | **SELECTED FOR ADAPTER SUPPORT** in `ae_bridge` (supports Read-only HTTP `:7788/call` protocol and ES3 JSON spill-file patterns) |
| [`Breakthrough/PySceneDetect`](https://github.com/Breakthrough/PySceneDetect) | Video Analysis | Mature (v0.7.2, 11/2026) | Python | 5,326 ⭐ / 552 🍴 | >95 recent commits / 18+ contributors | **BSD-3-Clause** (`LICENSE` file present) | **Excellent** (full Windows support with OpenCV/PyAV + FFmpeg) | **SELECTED AS PACKAGE DEPENDENCY** (`scenedetect`) combined with custom multi-cue frame signal analyzers |
| [`pouyashahrdami/mimic-mcp`](https://github.com/pouyashahrdami/mimic-mcp) | Video Analysis | Active (08/2026) | TypeScript (Node.js + Remotion) | 30 ⭐ / 0 🍴 | 73 commits / 1 contributor | **MIT** (`LICENSE` file present) | Partial (OCR and TTS rely on macOS Vision/`say`; mathematical signal analysis is cross-platform) | **ALGORITHMIC REFERENCE** (Adaptive MAD threshold `median + k*MAD`, grid-cell change area to distinguish full-frame cuts vs. dissolves vs. localized overlays) |
| [`moshspro-dev/video-effect-reel`](https://github.com/moshspro-dev/video-effect-reel) | Video Analysis | Early stage (10/2026) | Python | 1 ⭐ / 0 🍴 | 5 commits / 1 contributor | **MIT** (`LICENSE` file present) | Partial (uses POSIX `fcntl` and `setup.sh`, falls back to `fcntl = None` on Windows) | **CATALOG & CONTACT SHEET REFERENCE** (organization of evidence frames and timestamped contact sheet grids) |
| [`docsforadobe/after-effects-scripting-guide`](https://github.com/docsforadobe/after-effects-scripting-guide) | Reference Docs | Active (updated for AE 26.5, 09/2026) | Markdown (MkDocs) | 185 ⭐ / 41 🍴 | 93+ commits / 15+ contributors | Community documentation (Copyright Adobe Systems Inc., educational/reference use) | Platform-independent (documentation) | **USED AS AUTHORITATIVE REFERENCE** for ExtendScript DOM, Match Names (`ADBE ...`), `KeyframeInterpolationType`, `TrackMatteType`, `BlendingMode` |

---

## 2. Detailed Analysis by Repository Category

### 2.1. AEP Parsing

#### A. `forticheprod/py-aep`
- **Architecture & Source:**
  - Developed by animation studio **Fortiche Production** (authored by Aurore Delaunay).
  - Organized into clear subsystems under `src/py_aep/`:
    - `binary/`: Decodes `RIFX` / `RIFF` (`Egg!`) container structures and chunks (`Fold`, `Item`, `Layr`, `tdgp`, `tdbs`, `cdat`, `ldat`, `lhd3`, `sspc`, `parT`, `pard`, `btdk`).
    - `parsers/`: Specialized parsers for `application`, `project`, `composition`, `layer`, `property`, `effect`, `text`, `mask`, `marker`, `essential_graphics`, and `render_queue`.
    - `models/`: Object model closely mirroring the ExtendScript API (`Application`, `Project`, `CompItem`, `AVLayer`, `TextLayer`, `ShapeLayer`, `CameraLayer`, `LightLayer`, `PropertyGroup`, `Property`, `Keyframe`).
    - `synthesis/` & `resolvers/`: Automatically synthesizes default properties omitted from the binary file when unmodified in After Effects, and merges `parT`/`pard` parameter definitions for both built-in effects and **third-party plugins** (e.g., Sapphire `S_BlurDirectional`, `S_Shake`, Deep Glow).
  - Includes validation scripts comparing parsed output directly against After Effects (`scripts/jsx/export_project_json.jsx`) and hundreds of sample `.aep` files from AE 2018 through AE 2026 under `samples/`.
- **Dependencies:** `attrs>=21.3.0`, `PyYAML>=5.1`, `fonttools>=4.38`, `uharfbuzz>=0.39`. Officially compatible up to Python 3.14.
- **Technical Limitations:**
  - Does not evaluate expressions at runtime: when `expression_enabled == True`, `Property.value` returns the pre-expression static/keyframe value stored in the binary (though the `Property.expression` string is extracted in full).
  - `Property.expression_error` is always empty during offline parsing because AE computes expression errors at runtime.
  - Purely runtime application attributes (`Application.effects`, `Application.fonts`, `memoryInUse`, window state) are not stored inside `.aep` files.
  - Directly parses binary `.aep` (`RIFX`/`RIFF`) files only; does not include a built-in `.aepx` (XML) reader.

#### B. `ChenxingM/AEP-Tools`
- **Architecture & Source:**
  - Combines a Rust core (`rust/lib.rs` via `PyO3`) for fast RIFF chunk splitting with Python packages (`python/aep_parser/` and `python/aep_tools/`) for data modeling and a PySide6 GUI.
  - Notably includes `docs/aep-format.md`, which documents byte layouts for `idta`, `cdta`, `ldta`, `tdb4`, `cdat`, `lhd3`, `ldat`, `EfDf`, `parT`, `mkif`, `shph`, `btdk`, and the mapping between `.aep` (binary) and `.aepx` (XML).
- **Limitations & Reason for Non-Integration:**
  - Alpha stage (`0.1.0a1`), requiring Rust compilation via `maturin`.
  - Lower fidelity than `py-aep` when reconstructing property trees, spatial tangents, text animators, and third-party effect parameters.
  - **Licensing Precaution:** The repository declares `license = "MIT"` in `pyproject.toml` but lacks a `LICENSE` file in the source tree. Adhering strictly to license compliance rules, we **do not copy any code** from `AEP-Tools`, and instead implement our own clean-room `.aepx` parser/transcoder based on standard After Effects XML/RIFX structures.

#### C. `boltframe/aftereffects-aep-parser`
- **Architecture & Source:**
  - Go library (`project.go`, `item.go`, `layer.go`, `property.go`) accompanied by a Kaitai Struct specification in the README.
- **Limitations:**
  - Unmaintained since February 2022.
  - Parses only basic subsets of `idta`, `cdta`, `ldta`, and `tdgp`; does not decode keyframe spatial/temporal ease, text layer COS structures, shape paths, or complex third-party `parT` parameter blocks.

---

### 2.2. After Effects MCP & Automation Bridges

#### D. `JUNKDOGE-JOE/after-effects-mcp`
- **Architecture & Source:**
  - Comprises a CEP Extension (`plugin/`), a Node host listening on Streamable HTTP at `http://127.0.0.1:11488/mcp`, a stdio shim (`clients/ae-mcp-jkdg`), and a native C++ AEGP plugin (`native/`).
  - Exposes 16 MCP tools (`ae_status`, `ae_read`, `ae_exec`, `ae_previewFrame`, `ae_validateExpressions`, `ae_instances`, etc.).
  - Key architectural highlight: **`plugin/jsx/readonly-worker.jsx`** — to inspect or preview without touching the user's original project, it opens only an isolated copy (`snapshot.aep`) in a temporary directory, verifies `project.file.fsName`, suppresses modal dialogs, and closes with `CloseOptions.DO_NOT_SAVE_CHANGES`.
- **Limitations:**
  - Requires the user to install the ZXP CEP extension and open `Window > Extensions > ae-mcp` inside a running After Effects session.

#### E. `solomondivyananth/aftereffects-mcp` (AE MCP Bridge)
- **Architecture & Source:**
  - Lightweight, zero-npm-dependency architecture: `mcp/ae-mcp.js` communicates over HTTP `127.0.0.1:7788/call` (authenticated via `X-AE-Bridge-Token` read from `~/.ae-mcp-bridge.json`) with a CEP panel running `panel/jsx/bridge.jsx` (>3,100 lines of ES3 ExtendScript).
  - Handles real-world ES3 ExtendScript quirks effectively:
    - Includes a custom `JSON.stringify` / `JSON.parse` polyfill since ES3 ExtendScript lacks a standard `JSON` object.
    - Wraps execution in `app.beginSuppressDialogs()` / `app.endSuppressDialogs(false)` to prevent AE modal hangs on missing fonts or plugins.
    - **Spill File mechanism**: writes payloads larger than 100 KB to a UTF-8 temporary file in `Folder.temp` rather than returning huge strings over `evalScript`.
    - Verifies PNG completion by checking the trailing `IEND` chunk after `saveFrameToPng`.
- **Limitations:**
  - Also requires opening the `AE MCP Bridge` CEP panel inside a running After Effects instance to listen on HTTP port `:7788`.

---

### 2.3. Video Analysis

#### F. `Breakthrough/PySceneDetect`
- **Architecture & Source:**
  - Industry-standard Python library for cut and transition detection (`ContentDetector`, `AdaptiveDetector`, `ThresholdDetector`, `FlashDetector`/`HistogramDetector`).
  - Supports both OpenCV (`VideoStreamCv2`) and PyAV backends with frame-accurate timecodes (`FrameTimecode`).
- **Limitations for Fast VFX Videos (5–15 seconds):**
  - Default `ContentDetector` settings (`threshold=27.0`, `min_scene_len=15`) are tuned for long-form cinema and miss 1–3 frame flash frames or rapid micro-cuts occurring every 4–8 frames in fast VFX edits.
  - Therefore, in `VFX Learning Engine`, we combine `PySceneDetect` (configured with a short `min_scene_len` and `AdaptiveDetector` / `ContentDetector`) **with** our own per-frame timestamped signal analyzer.

#### G. `pouyashahrdami/mimic-mcp`
- **Architecture & Source:**
  - TypeScript MCP server designed to analyze reference video reels and recreate them in Remotion.
  - `src/analysis.ts` contains compact, effective computer vision heuristics:
    - Computes maximum per-channel difference (`max(|R1-R2|, |G1-G2|, |B1-B2|)`) rather than luminance alone, catching isoluminant color cuts.
    - Divides frames into a grid (`cols x rows`, e.g., `12 x 9`) to measure changed cell fraction (`area`): a spike in `area` that immediately collapses on the next frame indicates a **hard cut**; sustained change over a window indicates a **fade/dissolve**; localized change (`area < 0.5`) indicates an **overlay / text / graphic reveal**.
    - Adaptive threshold based on median and median absolute deviation: `max(floor, median + k * MAD)`.
    - Intra-scene motion (pan/zoom) and camera shake estimation from inter-frame displacement vectors.
- **Limitations:**
  - Written in TypeScript/Node.js and targeted toward social media reel generation in Remotion rather than deep After Effects VFX signal analysis (RGB split, glow/bloom, optical flow speed ramps, directional motion blur, distortion, particles).

#### H. `moshspro-dev/video-effect-reel`
- **Architecture & Source:**
  - Provides a catalog of 123 effect recipes (`library/effects.json`) and `reel_effects.py` for generating timestamp-annotated contact sheets via FFmpeg + Pillow.
- **Limitations:**
  - Lacks automated computer vision detectors, relying entirely on invoking the `claude` CLI on contact sheet images.
  - Uses POSIX `fcntl` (requires `fcntl = None` fallback on Windows).

---

### 2.4. Reference Documentation

#### I. `docsforadobe/after-effects-scripting-guide`
- Provides authoritative documentation for:
  - Object hierarchy: `app.project` -> `items` (`CompItem`, `FootageItem`, `FolderItem`) -> `layers` (`AVLayer`, `TextLayer`, `ShapeLayer`, `CameraLayer`, `LightLayer`) -> `PropertyGroup` / `Property`.
  - Official **Match Names** (`docs/matchnames/`):
    - Layer Transform (`ADBE Transform Group`, `ADBE Anchor Point`, `ADBE Position`, `ADBE Position_0/1/2`, `ADBE Scale`, `ADBE Orientation`, `ADBE Rotate X/Y/Z`, `ADBE Opacity`).
    - Effects (`ADBE Effect Parade`), Masks (`ADBE Mask Parade`, `ADBE Mask Atom`, `ADBE Mask Shape`, `ADBE Mask Feather`, `ADBE Mask Opacity`, `ADBE Mask Offset`).
    - Text (`ADBE Text Properties`, `ADBE Text Document`, `ADBE Text Animators`, `ADBE Text Animator`, `ADBE Text Selectors`, `ADBE Text Animator Properties`).
    - Shapes (`ADBE Root Vectors Group`, `ADBE Vector Group`, `ADBE Vector Shape - Rect/Ellipse/Star/Group`, `ADBE Vector Filter - Trim/Repeater/...`).
    - 3D Layer, Camera (`ADBE Camera Options Group`), Light (`ADBE Light Options Group`), Material Options (`ADBE Material Options Group`), Time Remapping (`ADBE Time Remapping`), Layer Styles (`ADBE Layer Styles`).

---

## 3. Technology Stack Decisions for `VFX Learning Engine` (Phase 1)

Based on empirical evaluation and the target hardware environment (**Windows, NVIDIA GeForce RTX 4060 8GB, Python, FFmpeg 8.1.1, Adobe After Effects 2026**):

1. **Package & Environment Management:**
   - Standard PEP 621 `pyproject.toml` managed with `uv` / `pip`.
   - **Pydantic v2** (`pydantic>=2.0`) for all data schemas, enforcing strict typing and explicit epistemic provenance (`observed`, `inferred`, `unavailable`, `unsupported`, `error`).
   - **Typer** + **Rich** for an ergonomic CLI (`vfx`) and structured console output.

2. **Module A — After Effects Project Analyzer (`vfx_engine.project_analyzer`):**
   - **Method A (Offline Project Parsing):**
     - Integrates **`py-aep`** (MIT License) as the primary engine for binary `.aep` parsing. `py-aep` extracts compositions, precompositions, layer hierarchy, parenting, track mattes, blending modes, transforms, masks, shapes, text animators, cameras, lights, **complete effect stacks and parameters including third-party plugins** (via `parT`/`pard` and `tdgp` decoding), keyframes (values, timing, interpolation, temporal/spatial easing, roving), expressions, time remapping, motion blur, adjustment layers, and missing footage/dependencies.
     - Implements a **Clean-room `.aepx` Parser & Transcoder** (`parsers/aepx_parser.py`): reads XML `.aepx` structures directly, transcodes `.aepx` XML trees losslessly into in-memory `RIFX` binary buffers to leverage the full `py-aep` decoding pipeline, and provides a direct XML DOM fallback parser if an `.aepx` file is truncated or non-standard.
     - Implements a **Third-Party Plugin & Missing Dependency Classifier** (`effect_extractor/`): identifies plugin families (Sapphire `S_*`, Boris FX Continuum `BCC*`, Deep Glow, Trapcode `tc*`/`Particular`/`Form`/`Mir`/`Tao`/`Shine`/`Starglow`, Video Copilot `VIDEOCOPILOT*`/`Element`/`Optical Flares`/`Saber`, RE:Vision `Twixtor*`/`RSMB*`, Red Giant Universe `uni.*`, Rowbyte `Plexus*`, Frischluft, Plugin Everything, etc.) from `matchName` and `EfdG` definitions **without ever loading or executing `.aex` binaries**.
   - **Method B (After Effects Read-only Bridge):**
     - `ae_bridge/` supports three safe **Read-only** inspection modes (always operating on temporary snapshots or read-only queries, never overwriting original user projects):
       1. **JUNKDOGE `ae-mcp` HTTP Adapter** (`http://127.0.0.1:11488/mcp` — `ae_status`, `ae_read`, `ae_exec`, `ae_previewFrame`).
       2. **Solomon `aftereffects-mcp` HTTP Adapter** (`http://127.0.0.1:7788/call` — authenticated via `~/.ae-mcp-bridge.json`).
       3. **Standalone ExtendScript Read-only Exporter (`ae-scripts/vfx_readonly_extract.jsx`)**: self-contained ES3 script with JSON polyfill and `beginSuppressDialogs()` that reads the project/composition/layer/effect/keyframe/expression tree and serializes it to JSON.
   - **Normalizer & Comparator (`normalizer/`):**
     - Normalizes both Offline Parser and Live AE Bridge outputs into `ProjectAnalysisResult` and compares them (`compare_offline_and_live`) to report `matched`, `only_in_live`, `only_in_offline`, `value_mismatch`, and `expected_runtime_difference` (such as `Property.value` when an expression is active).

3. **Module B — Video VFX Analyzer (`vfx_engine.video_analyzer`):**
   - **Decoder & Exact Timestamps (`decoder/`):**
     - Combines **`ffprobe`** (stream metadata, codec, audio, VFR/CFR detection, and per-frame `pkt_pts_time` presentation timestamps) with **OpenCV (`cv2.VideoCapture`)**. Never assumes `timestamp = frame_index / fps` on Variable Frame Rate (VFR) videos.
   - **Scene & Flash Detection (`scene_detection/`):**
     - Combines **`PySceneDetect`** (`ContentDetector`, `AdaptiveDetector`) with a **Per-Frame Multi-Channel Change & Grid Area** analyzer (inspired by `mimic-mcp`'s MAD threshold + cell grid) to detect:
       - Hard cuts (even in rapid 5–15s VFX edits).
       - Flash frames (1–5 frame bright/dark/color luminance impulses).
       - Dissolve / Fade transitions.
       - Localized overlays / Mask reveals / Text pop-ins (localized partial-grid changes).
   - **Motion & Optical Flow Analysis (`motion_analysis/`):**
     - Uses **Dense Optical Flow (Farneback)** and radial/global motion estimation to separate:
       - **Camera Shake / Impact Shake:** high-frequency sign reversals of global velocity vectors $(dx, dy)$ over short windows.
       - **Zoom / Punch-in / Pull-out Transitions:** rapid radial expansion/contraction divergence spikes.
       - **Speed Ramp / Time Remapping:** strong non-linear intra-scene optical flow velocity envelope changes (slow -> fast burst -> slow).
       - **3D Camera Motion & Parallax:** depth-stratified foreground vs. background flow variance during translational camera motion.
   - **Visual Effect Signal Detectors (`effect_detection/`):**
     - Directly measures verifiable visual signals:
       - **RGB Split / Chromatic Aberration:** phase-correlation spatial offset and Sobel edge shift between R–B and R–G channels along high-contrast edges.
       - **Glow / Bloom:** highlight saturation ratio combined with annular low-frequency Gaussian halo luminance excess around bright cores.
       - **Motion Blur / Directional Blur:** Laplacian variance sharpness drop paired with strong structure-tensor gradient anisotropy aligned with motion velocity peaks.
       - **Distortion / Displacement / Glitch:** non-affine optical flow spatial residuals and horizontal scanline row tearing.
       - **Motion Trails / Echo:** lagged frame edge residual correlation across $I_{t-1}, I_{t-2}, \dots$.
       - **Particles / High-frequency Emitters & Kinetic Typography / Masking Candidates:** morphological Top-Hat moving bright speckles and localized high-contrast sharp edge appearances, distinguishing measured signals (`observed` / `inferred`) from semantic interpretations requiring `VisionAnalyzer`.
   - **Adaptive Frame Sampler & Contact Sheet Generator:**
     - Performs full-frame analysis on short clips (5–20s) and exports timestamped evidence frames (`evidence-frames/`) at event peaks alongside an annotated `contact-sheet.jpg` with `Frame #` and `Timestamp (s)` badges.

4. **Module C — AI Vision Adapter (`vfx_engine.vision`):**
   - Abstract `VisionAnalyzer` interface with implementations:
     - `NoOpVisionAnalyzer` (default when offline or unconfigured: preserves local CV measurements, marks higher-level semantic descriptions as `unavailable`, never fabricates AI outputs, and makes zero network calls).
     - `OpenAICompatibleVisionAnalyzer` (activated only when explicitly configured via environment variables, supporting local Ollama/LM Studio on RTX 4060 8GB as well as OpenAI-compatible endpoints).
