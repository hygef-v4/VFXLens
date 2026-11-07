# Technical Limitations & Untested Scenarios — VFX Learning Engine (Phase 1)

This document transparently and comprehensively lists the technical limitations of **VFX Learning Engine (Phase 1)** as well as features that have full adapter implementations but have not been tested against a live running commercial host in the current session.

---

## 1. Limitations of After Effects Project Analyzer (`project_analyzer`)

### 1.1. Offline Binary/XML Parsing (`offline_py_aep` & `offline_aepx`)
1. **No Runtime Expression Evaluation**:
   - The offline parser extracts the **complete JavaScript/ExtendScript expression source code** (e.g., `wiggle(8, 35)`, `time * 150`, `valueAtTime(...)`) and its enabled state (`expression_enabled`), but **does not execute** the After Effects JavaScript runtime engine.
   - Consequently, the post-expression evaluated value at each frame (`expression_evaluated_value_status`) is explicitly marked as `unavailable` in offline mode.
2. **Opaque Binary Internal Parameters (`ARBITRARY_DATA` / `NO_VALUE`) of Third-Party Plugins**:
   - For standard third-party plugin parameters (Slider, Angle, Point 2D/3D, Color, Checkbox, Popup/Dropdown) in **Sapphire (`S_*`)**, **Deep Glow**, **BCC**, **Trapcode**, and **Twixtor**, After Effects stores parameter definition chunks (`LIST:parT` -> `tdmn`, `pard`, `pdnm`) and static/keyframe values (`LIST:tdgp` -> `cdat`, `ldat`) directly inside the `.aep` file. The offline parser extracts the full name, `matchName`, static value, and keyframes for these parameters.
   - However, certain plugins store 3D scene graphs or custom curves as proprietary opaque binary blobs (`PropertyControlType.UNKNOWN` / `PropertyValueType.NO_VALUE` or custom `bdata`, such as the internal 3D scene blob of **Video Copilot Element 3D (`VIDEOCOPILOT 3DArray`)** or custom curve data). For these parameters, the name, `matchName`, and keyframe timings are extracted, while the proprietary binary payload is marked as `unsupported` rather than guessed.
3. **Default Values of Unmodified Properties in `.aepx` Fallback Mode**:
   - When analyzing an `.aepx` file through the XML-to-RIFX transcode pipeline (`aepx_transcoded_py_aep`), the full property tree is synthesized identically to a binary `.aep`.
   - If an `.aepx` file is truncated or contains non-standard XML tags that require falling back to `offline_aepx_xml_fallback`, only chunks explicitly stored in the XML DOM are surfaced; omitted fields are marked as `unavailable`.
4. **Refusal to Load or Execute `.aex` Binary Plugins**:
   - An `.aex` file is a compiled Windows dynamic-link library (PE/DLL) containing native machine code. By safety policy, the engine **refuses to open or execute `.aex` files** (`UnsafeFileError`). It identifies plugins referenced inside `.aep`/`.aepx` projects solely via their `matchName` and the `PluginRegistry`.

### 1.2. After Effects Read-Only Live Bridge (`ae_bridge`)
1. **Live Testing Status (`live_bridge_tested = false`)**:
   - On the target workstation, **Adobe After Effects 2026** is installed (`C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe`), but **After Effects is not actively running with a CEP MCP Extension listening** on port `11488` (JUNKDOGE `after-effects-mcp`) or `7788` (Solomon `aftereffects-mcp`).
   - Therefore, `live_bridge_tested` is honestly recorded as `false` across offline runs.
   - Complete implementations are provided for:
     - `ae-scripts/vfx_readonly_extract.jsx`: Strictly read-only ExtendScript (never calls `app.open()`, never mutates properties, never calls `app.project.save()`).
     - `AfterEffectsReadOnlyBridge`: HTTP/JSON-RPC adapter for both MCP protocols (`11488` and `7788`) with a strict blocklist (`FORBIDDEN_JSX_PATTERNS`) preventing any write/mutation operations.
     - `compare_offline_and_live()`: Automated comparator between offline parser output and live AE bridge payloads.

---

## 2. Limitations of Video VFX Analyzer (`video_analyzer`)

1. **Non-Invertibility from Rendered MP4/MOV Pixels to After Effects Project Structure**:
   - From a rendered video alone (especially after 8-bit H.264/HEVC compression), it is **impossible to determine with 100% certainty** the exact plugin name used. For example, an intense highlight bloom could be created by **Deep Glow**, **Sapphire `S_Glow`**, or **three stacked `ADBE Glo2` (Built-in Glow) instances in 32-bpc mode**.
   - Therefore, every event in `video-analysis.json` strictly separates four fields:
     - `observations` (signal measurements directly observed from frames),
     - `possible_ae_techniques` (plausible AE recreation workflows),
     - `possible_plugins` (candidate plugins — always marked `verified: false`),
     - `undetermined_parameters` (parameters that cannot be recovered from video pixels alone).
2. **Computer Vision Heuristics & Optical Flow Limitations**:
   - **Motion Blur vs. Defocus Blur**: The detector combines Laplacian variance drop with structure-tensor gradient anisotropy (`gradient_anisotropy`) and Optical Flow velocity to distinguish directional motion blur from isotropic out-of-focus blur. However, strongly oriented background stripes combined with defocus blur can affect confidence.
   - **Speed Ramp vs. Fast Physical Subject Motion**: Optical Flow measures apparent 2D image-plane velocity (px/frame). A rapid physical camera whip or subject burst produces a velocity envelope similar to Time Remapping / Twixtor.
   - **Kinetic Typography & Semantic Compositing**: When no AI Vision provider is configured (`VFX_VISION_PROVIDER=none`), the detector flags candidates (`kinetic_typography_candidate`) based on localized high-contrast sharp edge density; OCR text reading and semantic 3D object recognition are marked `unavailable`.
3. **AI Vision Provider (`VisionAnalyzer`)**:
   - By default, the engine runs `NoOpVisionAnalyzer` (100% local, zero paid API calls, zero hallucinated AI descriptions).
   - The engine exports `contact-sheet.jpg` and timestamped `evidence-frames/` ready for consumption by a Vision model when explicitly configured by the user.
