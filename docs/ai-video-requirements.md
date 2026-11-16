# VFXLens local video toolchain

VFXLens keeps analysis, video rendering and speech dependencies in separate environments. Agent instructions are in [AGENTS.md](../AGENTS.md); the shared entrypoint is [skills/vfxlens/SKILL.md](../skills/vfxlens/SKILL.md).

The user subsequently requested the **full toolchain**, including the tools initially marked optional. See [full-toolchain setup and routing](full-toolchain.md). Optional/branch labels below describe when a film needs a tool, not a claim that it was omitted from the full installation. Use recorded check results to distinguish installed packages, runnable applications and missing model weights.

## Required components and boundaries

| Component | Location / purpose | Install source |
| --- | --- | --- |
| Analyzer + document readers | Root `.venv`; read projects, video and PDF text/pages | Root `pyproject.toml` / `uv.lock`; `documents` extra adds PyMuPDF and pypdf |
| Remotion + React/TypeScript | `studio/`; frame-driven composition, caption, audio and export | `studio/package.json` / `package-lock.json`; published npm packages |
| VFXLens skill | Repo-owned `skills/vfxlens/`; one source shared by both agents | Link into user skill directories below |
| Remotion and LottieFiles skills | Project-scoped under `studio/`; rendering guidance and motion principles | Skills CLI; tracked `studio/skills-lock.json` records sources |
| FFmpeg + ffprobe | Existing system installation if available; decode, encode and inspect | [Official download routes](https://ffmpeg.org/download.html); check `PATH` before installing |
| Blender + MCP | Existing Blender if available; scene production for 3D/2.5D shots | [Blender](https://www.blender.org/download/) + [MCP for Blender](https://github.com/ahujasid/mcp-for-blender); community integration |
| Whisper + CPU PyTorch | Separate Python 3.11 environment in `studio/voice/`; local speech/caption timing | Its `pyproject.toml` / `uv.lock`; published `openai-whisper` package |

The studio pins `remotion`, `@remotion/cli`, `@remotion/media` and `@remotion/three` to the same version. Optional npm packages in the table below are not installed by default: add one with `npm --prefix studio install <package>` when a shot needs it. Use the checked-in manifests and lockfiles as the version authority. Blender is needed for the Blender production branch, not for an analyzer run or a Remotion-only composition. Whisper is needed for transcription, not for rendering a video with supplied caption timing.

Actual machine paths, installed versions, client configuration backups and observed check results belong in ignored `local/setup/status.json` and neighboring `local/setup/` files. Consult that record for this installation; this document makes no claim that a connected client, downloaded speech model or complete production has been tested.

## Repeatable setup and checks

Run from the repository root in PowerShell, with Python/uv, Node/npm and FFmpeg available. Use a Node version supported by the installed [Remotion CLI](https://www.remotion.dev/docs/cli). Reuse existing application installations instead of installing a second copy.

```powershell
$env:PYTHONUTF8 = '1'
uv sync --locked --extra dev --extra documents
uv run vfx doctor
uv run pytest

npm --prefix studio ci
npm --prefix studio run typecheck
npm --prefix studio run prepare:smoke
npm --prefix studio run studio
```

The studio command starts the local preview server. In another terminal, render the `SmokeTest` setup sample or a still:

```powershell
npm --prefix studio run verify:render
npm --prefix studio run still -- SmokeTest ../local/setup/studio-smoke.png --frame=30
```

`SmokeTest` is a 10-second, 1080×1920, 30 fps setup sample. `verify:render` prepares its local test audio and writes `local/setup/studio-smoke.mp4`. For another composition, use `npm --prefix studio run render -- <CompositionId> <output-path>`; paths are relative to `studio/`. Inspect the actual MP4 with ffprobe, view successive frames around transitions, and listen to its audio before reporting a successful delivery. A sample render verifies its exercised components; it does not validate a Blender character pipeline or transcription quality.

Install the isolated voice environment without downloading a model:

```powershell
uv sync --locked --directory studio/voice
uv run --directory studio/voice whisper --help
```

When transcription is requested, provide an explicit model, language and output location. Use absolute paths for media/output to avoid ambiguity from the voice environment's working directory:

```powershell
uv run --directory studio/voice whisper "C:/path/to/voice.wav" --model base --language vi --device cpu --fp16 False --word_timestamps True --output_format all --output_dir "C:/path/to/production/captions" --model_dir "C:/path/to/model-cache"
```

This last command downloads the selected weights if they are absent. Setup and CLI help do not download them. Python 3.11 is isolated here because Whisper's documented compatibility includes it; FFmpeg is also required. Word timestamps are estimates: listen, correct the transcript and check caption boundaries. The CPU environment is the reproducible default; GPU setup is a separate change. [Whisper setup](https://github.com/openai/whisper#setup), [word timestamp implementation](https://github.com/openai/whisper/blob/main/whisper/transcribe.py).

## Register one skill for both agents

Keep `skills/vfxlens/` as the authoritative source. Register directory links that resolve to that source:

| Agent | User skill directory link | Target |
| --- | --- | --- |
| Codex | `~/.agents/skills/vfxlens` | `<VFXLens checkout>/skills/vfxlens` |
| Claude Code | `~/.claude/skills/vfxlens` | Same target |

On Windows, a directory junction can provide this local link without copying the skill. Resolve the checkout to an absolute path, create missing parent directories, and create each link only if that destination is absent. If a destination exists, inspect its resolved target and preserve it; do not overwrite unrelated personal skills. On systems without directory links, maintain a synchronized copy from the repo source and record its revision.

The root `CLAUDE.md` uses `@AGENTS.md` to import the shared rules. Relative imports resolve from the importing file. [Claude Code imports](https://code.claude.com/docs/en/memory#import-additional-files).

From `studio/`, install the two upstream skills for both agents at project scope:

```powershell
Push-Location studio
npx skills add remotion-dev/skills --skill remotion-best-practices -a codex -a claude-code
npx skills add LottieFiles/motion-design-skill --skill motion-design -a codex -a claude-code
Pop-Location
```

Choose the linked installation method. The canonical project copies live in `studio/.agents/skills/`; Claude links point to those copies in `studio/.claude/skills/`. Keep the generated lockfile. Skills are instructions, so these commands do not replace `npm ci`. Review upstream changes before updating their installed source. [Skills CLI scopes and links](https://github.com/vercel-labs/skills/blob/main/docs/commands.md), [Remotion skill](https://github.com/remotion-dev/skills), [LottieFiles skill](https://github.com/LottieFiles/motion-design-skill).

Restart or refresh agent discovery after registration. Check the resolved link targets, then invoke `vfxlens` from both the repo and an unrelated working directory. The skill must resolve the real checkout from its own location, read the relevant workflow and find the studio instructions. A directory listing proves registration layout, not successful invocation in both clients.

## Blender and MCP

Locate the existing Blender executable through installed-application metadata or its launcher; absence from `PATH` is not evidence that Blender is absent. Record the discovered path locally, rather than embedding a workstation path in shared docs.

MCP for Blender is distributed as the published `mcp-for-blender` Python tool plus a Blender addon. Use the same reviewed package version for addon installation and client registration; keep that pin in local setup records. The upstream manual route is `uvx --python 3.11 mcp-for-blender install-addon`, followed by enabling **MCP for Blender** in Blender's add-ons and starting its sidebar server. Inspect the destination and preserve an existing addon before replacing it. Register a stdio server in each client that launches `uvx --python 3.11 mcp-for-blender`; keep existing MCP entries. [Upstream installation and client instructions](https://github.com/ahujasid/mcp-for-blender#installation).

Keep the addon socket on localhost. Use one controlling client at a time for a scene. Query scene state before editing; create new production scenes and save only into the designated production workspace. Keep external asset services and AI-generation integrations disabled unless explicitly configured for the request. Verify a real scene query and a temporary production render separately from merely listing the MCP configuration. The analyzer's AE safety rules still apply independently.

## Reference repositories

These are roles and installation routes. **Core** means needed by the primary workflow; **branch** means used by a named workflow; **optional** means a film can omit it and the repository does not install it.

| # | Repository | Role / need | Installation route |
| --- | --- | --- | --- |
| 01 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Core: React video composition/render | Locked npm packages in `studio/`; no source clone |
| 02 | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Core: agent guidance | Skills CLI command above; no runtime clone |
| 03 | [juliangarnier/anime](https://github.com/juliangarnier/anime) | Optional: SVG/DOM animation | Published npm `animejs` |
| 04 | [motiondivision/motion](https://github.com/motiondivision/motion) | Optional: UI/React animation | Published npm `motion`; agent skill is a separate source |
| 05 | [ManimCommunity/manim](https://github.com/ManimCommunity/manim) | Optional: mathematical animation | Published Python `manim` in a separate environment; follow native prerequisite docs |
| 06 | [airbnb/lottie-web](https://github.com/airbnb/lottie-web) | Optional: play supplied Lottie assets | Published npm `lottie-web` |
| 07 | [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | Blender branch: agent scene control | Published `mcp-for-blender` tool + addon; existing Blender |
| 08 | [mrdoob/three.js](https://github.com/mrdoob/three.js) | Optional: browser 3D alternative | Published npm `three` |
| 09 | [gkjohnson/three-gpu-pathtracer](https://github.com/gkjohnson/three-gpu-pathtracer) | Optional: Three.js path tracing | Published npm `three-gpu-pathtracer`; check peer dependency versions |
| 10 | [jrouwe/JoltPhysics](https://github.com/jrouwe/JoltPhysics) | Optional: dedicated physics simulation | Source clone + upstream C++ build; no need for ordinary Blender scenes |
| 11 | [pmndrs/postprocessing](https://github.com/pmndrs/postprocessing) | Optional: Three.js post effects | Published npm `postprocessing` |
| 12 | [Alchemist0823/three.quarks](https://github.com/Alchemist0823/three.quarks) | Optional: Three.js particles | Published npm `three.quarks`; optional `quarks.r3f` for React Three Fiber |
| 13 | [cocopon/tweakpane](https://github.com/cocopon/tweakpane) | Optional: interactive parameter panel | Published npm `tweakpane` |
| 14 | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Optional: local model-generated assets | Official desktop/portable release, or source clone with separate environment and selected models |
| 15 | [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice) | Optional: synthesized narration | Upstream recursive source clone + separate environment/model weights; validate target language first |
| 16 | [librosa/librosa](https://github.com/librosa/librosa) | Optional: music/onset/beat analysis | Published Python `librosa` |
| 17 | [m-bain/whisperX](https://github.com/m-bain/whisperX) | Optional: forced alignment beyond Whisper | Published Python `whisperx` in a separate environment; language/model requirements apply |
| 18 | [obsproject/obs-studio](https://github.com/obsproject/obs-studio) | Optional: screen/footage capture | Official application release; no source clone |
| 19 | [mifi/lossless-cut](https://github.com/mifi/lossless-cut) | Optional: quick footage trimming/remux | Official application release; no source clone |
| 20 | [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | Core: media processing and probing | Existing binary or platform build linked by ffmpeg.org; no source build required |

Whisper (`studio/voice`) is the local transcription option; WhisperX is an optional alternative for stricter alignment. Blender's own renderer supplies the initial 3D branch; Three.js, physics, particles and a path tracer are alternatives or additions, not prerequisites. Any animation library brought into Remotion must be driven by composition frames and tested for deterministic seeking/rendering. [Remotion animation model](https://www.remotion.dev/docs/animating-properties).

## Related agent skills

Install these per machine when a production needs them; they are not part of the repository.

| Source | Use |
| --- | --- |
| [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion guidance (`remotion-best-practices` router) |
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | Timing, easing and staging guidance |
| [thuann-vn/claude-3d-animated-shorts](https://github.com/thuann-vn/claude-3d-animated-shorts) | three.js character engine used by the Short toolkit |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | Shot recipes and sound-design rules |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | GSAP animation branches |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | Code-rendered film styles (Claude Code plugin) |
| [ANVEAI/motion-pack](https://github.com/ANVEAI/motion-pack) | Story, frame design, publishing copy and render lint (Claude Code plugin) |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | Discovery catalogue; evaluate each original source |

Follow [study-reference](../workflows/study-reference.md) for evidence and [create-video](../workflows/create-video.md) for production, rather than treating a tutorial's example parameters as measurements of an original pipeline.

## Cost and license boundaries

Processing is local by default; the analyzer's vision provider stays `noop`. Installing these packages does not authorize paid APIs, hosted renders, TTS calls or publication. Voice recordings, model weights and assets have their own rights and license terms. Remotion's free license is eligibility-dependent; check the current [official license and pricing](https://www.remotion.dev/docs/license/pricing) before organizational/commercial use. Local rendering alone does not establish that every use is free.
