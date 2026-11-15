# VFXLens AI Video Studio Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for independent skill/document tasks and inline execution for environment installation. Track completed checks below.

**Goal:** Install a local analysis/video-production toolchain and one shared VFXLens skill for Claude Code and Codex.

**Architecture:** Keep the existing read-only analyzer and knowledge library. Add a separately locked Remotion studio and voice environment; a repo-owned skill routes learning, analysis and video creation. Register the skill for both local agents without overwriting existing configuration.

**Tech Stack:** Python/uv, PyMuPDF/pypdf, React/TypeScript/Remotion, Whisper/PyTorch, existing FFmpeg, existing Blender plus MCP.

**Spec:** [Accepted installation proposal](../../ai-video-installation-proposal.md).

## Global Constraints

- Preserve original media/projects and all existing machine configuration.
- Local processing by default; no paid APIs or executing embedded project code.
- Distinguish measured evidence, inference, unavailable data and creative decisions.
- Reuse installed Blender and FFmpeg; install published packages instead of cloning every runtime repository.
- Keep production dependencies separate from the analyzer and private artifacts Git-ignored.

## Review Focus

- Skill resolution from another working directory and Windows paths containing spaces.
- Existing skill/MCP entries must not be overwritten or duplicated.
- Blender integration must use the discovered installation, preserve startup data and bind locally.
- Rendering must produce an actual decodable video with audio and expected frame count.
- Documentation must distinguish installed tools from optional repositories and tested capabilities from pending checks.

## Tasks

- [x] Task 1: Baseline a realistic agent request, create `skills/vfxlens/SKILL.md` and two routed `workflows/`, validate discovery/retrieval against the baseline.
- [x] Task 2: Update `AGENTS.md`, add `CLAUDE.md`, installation/repository requirements, and README pointers while retaining all original safety rules.
- [x] Task 3: Add locked `studio/` Remotion setup and small render verification composition; install and type-check/render/probe it.
- [x] Task 4: Install PDF readers and isolated Whisper environment; verify imports, CLI and audio handling without paid services.
- [x] Task 5: Install upstream Remotion/Lottie skills, link repo skill for both agents, configure and verify existing Blender/MCP safely.
- [x] Task 6: Run analyzer tests/doctor, verify final changes and record exact installed versions and verification limits.

## Evidence

- Initial tree contained only two untracked survey/proposal documents; both are preserved.
- Blender discovered through installed-program metadata at `E:/SteamLibrary/steamapps/common/Blender`; verify executable before integration.
- Analyzer: 25 tests passed; doctor reports ready; the full generated 300-frame video was analyzed successfully.
- Studio: TypeScript passed; actual H.264/AAC MP4 verified at 1080x1920, 30 fps, 300 frames, 10 seconds. Encoded frames inspected and four audio cue windows measured; perceptual listening was not performed.
- PDF readers opened both supplied PDFs. Whisper CLI/imports/audio decoding/mel extraction passed in its isolated CPU environment; no speech weights were downloaded.
- Both user skill junctions resolve to the one repo source from another working directory. Frontmatter validation and independent retrieval audit passed; native interactive skill-menu invocation requires fresh client sessions and was not exercised.
- Blender 5.2.3, addon protocol 16: live scene query and 256px render passed. Only the isolated verification instance was closed afterward. Existing client MCP entries were preserved and changed configurations/addon backed up.
- Independent review findings fixed: nested installed-skill ignore patterns and missing audio preparation before fresh preview.
- Exact versions, local paths, backups and honest verification limits are recorded in ignored `local/setup/status.json`.
