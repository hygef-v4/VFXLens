# AGENTS.md — VFX Learning Engine (Phase 1)

## 1. System Objective
`VFX Learning Engine` is a professional VFX and Motion Graphics technical analysis system comprising two core subsystems in Phase 1:
1. **After Effects Project Analyzer (`vfx_engine.project_analyzer`)**: Reads `.aep` (binary RIFX/RIFF) and `.aepx` (XML) files in Offline mode (powered by `py-aep` + clean-room `.aepx` transcoder/parser) or via a Read-only AE Bridge (MCP HTTP / ExtendScript `.jsx` operating on an isolated temporary copy).
2. **Video VFX Analyzer (`vfx_engine.video_analyzer`)**: Analyzes high-speed VFX videos (5–15s or longer) per frame and exact presentation timestamp (`ffprobe` + OpenCV + `PySceneDetect` + Optical Flow + Multi-cue Signal Detectors + optional AI Vision Adapter).

## 2. Data Safety & Security Rules (MANDATORY)
- **Strictly read-only with respect to user data:** Never overwrite, delete, rename, or move the user's original `.aep`, `.aepx`, or video files.
- **Opening via After Effects:** When using the Live AE Bridge or ExtendScript, always copy the `.aep` file to an isolated temporary directory before opening and close it with `CloseOptions.DO_NOT_SAVE_CHANGES`.
- **Never execute untrusted code:** Never load or execute `.aex` binary plugins, and never automatically execute scripts embedded inside user projects.
- **No automatic paid cloud calls:** All processing runs 100% locally by default. `VisionAnalyzer` defaults to `noop` (offline) mode unless the user explicitly configures a valid provider.
- **Strictly distinguish data availability states (`DataAvailabilityStatus`):**
  - `observed`: Directly read or measured from binary/XML/frames.
  - `inferred`: Evidence-backed inference derived from measured signals or heuristics.
  - `unavailable`: Not present in the static data source (e.g., post-expression evaluated values during offline analysis, or exact plugin parameters from an MP4 video).
  - `unsupported`: Format or data field not yet supported by the parser.
  - `error`: An error occurred during reading or extraction.

## 3. Core CLI Commands
```powershell
uv run vfx doctor
uv run vfx analyze-project "path/to/project.aep"
uv run vfx analyze-video "path/to/video.mp4"
uv run vfx analyze-folder "path/to/folder" --recursive
uv run vfx inspect "outputs/<analysis-id>"
```

## 4. Testing
```powershell
uv run pytest
```
