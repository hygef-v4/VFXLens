# AGENTS.md — VFXLens

## 1. System Objective
`VFXLens` combines VFX/Motion Graphics reference analysis, a reusable knowledge library, and agent-driven local video production. Its Phase 1 analysis subsystems remain:
1. **After Effects Project Analyzer (`vfx_engine.project_analyzer`)**: Reads `.aep` (binary RIFX/RIFF) and `.aepx` (XML) files in Offline mode (powered by `py-aep` + clean-room `.aepx` transcoder/parser) or via a Read-only AE Bridge (MCP HTTP / ExtendScript `.jsx` operating on an isolated temporary copy).
2. **Video VFX Analyzer (`vfx_engine.video_analyzer`)**: Analyzes high-speed VFX videos (5–15s or longer) per frame and exact presentation timestamp (`ffprobe` + OpenCV + `PySceneDetect` + Optical Flow + Multi-cue Signal Detectors + optional AI Vision Adapter).

Production uses the shared `skills/vfxlens/` entrypoint, Remotion in `studio/`, and Blender when a shot needs 3D. `uv run vfx ...` provides analysis commands; production is orchestrated through workflows and studio scripts.

## 2. Data Safety & Security Rules (MANDATORY)
- **Strictly read-only with respect to user data:** Never overwrite, delete, rename, or move the user's original `.aep`, `.aepx`, or video files.
- **Separate production workspace:** Edit newly generated code, assets and scenes in the designated production workspace. Keep episode documents, private media, `.blend` files and exports in `local/productions/<slug>/`; retain reusable studio code in `studio/`. A generated scene is editable; original reference data remains read-only.
- **Opening via After Effects:** When using the Live AE Bridge or ExtendScript, always copy the `.aep` file to an isolated temporary directory before opening and close it with `CloseOptions.DO_NOT_SAVE_CHANGES`.
- **Never execute untrusted code:** Never load or execute `.aex` binary plugins, and never automatically execute scripts embedded inside user projects.
- **No automatic paid cloud calls:** All processing runs 100% locally by default. `VisionAnalyzer` defaults to `noop` (offline) mode unless the user explicitly configures a valid provider.
- **Strictly distinguish data availability states (`DataAvailabilityStatus`):**
  - `observed`: Directly read or measured from binary/XML/frames.
  - `inferred`: Evidence-backed inference derived from measured signals or heuristics.
  - `unavailable`: Not present in the static data source (e.g., post-expression evaluated values during offline analysis, or exact plugin parameters from an MP4 video).
  - `unsupported`: Format or data field not yet supported by the parser.
  - `error`: An error occurred during reading or extraction.
- **Creative decisions:** Label choices for a new production as creative decisions; never present them as measured properties of the reference.

## 3. Task Routing

- **Study, analyze or create video:** Read [`skills/vfxlens/SKILL.md`](skills/vfxlens/SKILL.md); follow its reference-study or production workflow for the requested branch.
- **Install, repair or audit the toolchain:** Read [`docs/ai-video-requirements.md`](docs/ai-video-requirements.md). Check lockfiles for dependency versions and ignored `local/setup/status.json` for this machine's recorded checks; configuration alone does not prove a live connection or successful render.
- **Look up an editing technique:** Start at [`library/README.md`](library/README.md). Keep private source paths and episode-specific material out of the reusable library.

## 4. Core CLI Commands
```powershell
uv run vfx doctor
uv run vfx analyze-project "path/to/project.aep"
uv run vfx analyze-video "path/to/video.mp4"
uv run vfx analyze-folder "path/to/folder" --recursive
uv run vfx inspect "outputs/<analysis-id>"
```

## 5. Verification
```powershell
uv run pytest
```

For studio changes, use the scripts in `studio/package.json`, render the affected composition, and inspect its output. Report separately which checks ran and which visual/audio or live application checks remain unverified.
