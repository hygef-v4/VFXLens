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
- **Make a story Short with 3D cartoon characters (three.js engine + Remotion assembly):** Read [`workflows/threejs-character-short.md`](workflows/threejs-character-short.md); it lists the skills per stage and the toolkit in `studio/tools/threejs-short/`.
- **Direct cinematic 3D, procedural VFX or a 3D explainer:** Read [`.agents/skills/remotion-3d-director/SKILL.md`](.agents/skills/remotion-3d-director/SKILL.md) alongside the production workflow; it owns renderer selection, shot direction and visual/render QA.
- **Discover or choose current video technology:** Read [`skills/motion-scout/SKILL.md`](skills/motion-scout/SKILL.md). Use its live research pass before adopting new animation technology; research-only work does not authorize installation, and selected findings hand off to the existing production/Director workflow.
- **Write a video script, outline or narration:** Read [`library/content-writing/README.md`](library/content-writing/README.md) through the shared VFXLens skill; keep script-only requests scoped to writing.
- **Install, repair or audit the toolchain:** Read [`docs/ai-video-requirements.md`](docs/ai-video-requirements.md). Check lockfiles for dependency versions and ignored `local/setup/status.json` for this machine's recorded checks; configuration alone does not prove a live connection or successful render.
- **Look up an editing technique:** Start at [`library/README.md`](library/README.md). Keep private source paths and episode-specific material out of the reusable library.

### Propose the toolset before a video task
Before starting any video request, reply with a short proposal and wait for the user's OK. Name one route, the skills per
stage, what is optional, and any paid or long step (ElevenLabs credits, a full render). Ask only when two routes fit equally.
Skills marked *(user plugin)* are installed per machine; when one is missing, say so and use the repo route.

| Request | Route (primary) | Add when useful |
| --- | --- | --- |
| Story Short with 3D cartoon characters | `workflows/threejs-character-short.md`: `claude-3d-animated-shorts`, ElevenLabs, Remotion `studio/` | `video-shotcraft` (cuts, sound design), `humanizer` (narration) |
| Film in a named visual style (watercolor, newsreel, blueprint, toon…) | `lemo-opuscar` *(user plugin)*, its own pipeline | Borrow a style's `STYLE.md` into the three.js route instead when the user wants their characters |
| Cinematic 3D, product film, procedural VFX, 3D explainer | `remotion-3d-director` | Blender MCP for heavy models; `motion-stack` *(user plugin)* to choose or debug a library |
| Study a reference video or AE project | `vfxlens` (`uv run vfx analyze-video/-project`) | `ae-edit-recipes`, `video-shotcraft` |
| Script, hook, narration | `library/content-writing` via `vfxlens`, then `humanizer` | `story-script` *(motion-pack)* for extra hook variants |
| Voice, SFX, music | ElevenLabs `text-to-speech`, `sound-effects`, `music` (CLI for timestamps and files) | `speech-to-text` (check the mix), `voice-isolator`, `dubbing` |
| Captions, thumbnail, cover, safe zones | `frame-design` *(motion-pack)* | `open-design` MCP for the cover image |
| QA before delivery | `verify_render.py`, `qa/audit.py`, Scribe ASR | `mp lint` *(motion-pack)* |
| Publish | `social-video` *(motion-pack)* drafts copy, cover, AI disclosure | `postiz` to schedule; the user approves every post |
| New animation technology | `motion-scout` | `motion-stack` *(user plugin)* |
| Promo of a web or desktop product (real page captures) | `video-shotcraft` *(user skill)*: Ink Press template or its 124 shot cards | `remotion-3d-director` for 3D shots |
| Remotion how-to (captions, render, Studio, upgrade, licence) | `remotion-best-practices` router (`studio/.claude/skills`, also global) | `remotion-render`, `remotion-captions`, `remotion-upgrade` |

**When to use `video-shotcraft`:** (1) sound design for any video: read only its `references/sound-design.md` (peak alignment,
layering, ducking, BGM) and `sfx-sourcing.md` (Freesound search; it lists candidates and downloads nothing on its own);
(2) one shot effect for any video: pick a recipe from its shot cards (`references/shots`, gallery); (3) a full promo for a
web or desktop product, where it owns the pipeline; (4) beat-synced cuts (`music-beat-sync.md`). Do not run its full promo
pipeline for a story Short: the three.js route owns story, picture and assembly there.

Do not build with `mp render` (motion-pack) or another plugin's pipeline when the request fits a repo route; plugin skills that
claim "any video" request still yield to this table. For audio changes, deliver a full-mix preview for sign-off before the video render.

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
