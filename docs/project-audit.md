# Project audit — 2026-11-15

What this repo does: VFXLens studies After Effects projects and video references locally, stores reusable editing knowledge, and provides a shared Claude/Codex production workflow. This review assumes one person running local analysis and production. It follows the video input, timestamp, scene-detection and report-writing paths in depth; it also checks the toolchain layout and Git exclusions.

## Resolved findings

The three issues below were reproduced on generated media, then fixed at the shared write/decode boundaries. Their original failure cases are retained here for context.

1. **An output hard link can overwrite the source video** (`src/vfx_engine/cli/main.py:123`, `src/vfx_engine/reports/video_reporter.py:17`).
   - **What this is:** A hard link gives the same file another name. The CLI writes its reports after the analyzer's read-only guard ends.
   - **Problem:** A generated MP4 linked as the output `video-analysis.json` was replaced with JSON; the CLI exited successfully and the source checksum changed. Resolving the two paths does not detect hard links.
   - **Implemented fix:** `core.safety.validate_output_path` refuses symbolic links and files with multiple hard links before writing. Both report writers preflight every report; evidence JPEGs, contact sheets and batch summaries use the same guard. This also protects links to other reference files, not only the currently analyzed input.
   - **Regression checks:** `tests/test_output_safety.py` verifies unchanged source checksums and refusal through report APIs, evidence export, the video CLI and batch CLI, including file symlinks and hard links. It also confirms regular output reports can still be overwritten; choose a fresh output directory when an existing destination is linked. Directory junctions remain supported.

2. **Failed timestamp probing silently fabricates constant-rate timestamps** (`src/vfx_engine/video_analyzer/decoder/ffprobe_decoder.py:116`, `src/vfx_engine/video_analyzer/analyzer.py:72`).
   - **What this is:** FFprobe supplies each frame's presentation timestamp. Variable-frame-rate video does not have evenly spaced timestamps.
   - **Problem:** When the frame probe fails or returns no timestamps, nominal-FPS estimates are returned without a result warning or provenance field. In the generated test, the measured third timestamp was 0.3 seconds; the fallback reported 0.2 seconds with no warning.
   - **Implemented fix:** The prober raises a clear error on failed, empty, malformed, missing or non-finite frame timestamps. The decoder also refuses frames beyond measured timestamp coverage instead of synthesizing timestamps from FPS or OpenCV.
   - **Regression checks:** `tests/test_video_timestamps.py` covers probe failures/timeouts, incomplete timestamp data, CLI error propagation without reports, and preservation of measured VFR timestamps. This deliberately replaces the old silent fallback with a failed analysis; no schema or two-value prober API change is required.

3. **The frame cap does not bound scene-detection work** (`src/vfx_engine/video_analyzer/analyzer.py:84`, `src/vfx_engine/video_analyzer/scene_detection/scene_detector.py:12`).
   - **What this is:** `--max-frames` limits the main decoder, but scene detection opens the clip again.
   - **Problem:** A generated ten-frame clip analyzed with `--max-frames 1` reported one decoded frame while PySceneDetect read all ten.
   - **Implemented fix:** PySceneDetect receives an exclusive frame fence at the final analyzed signal index plus one, including capped and incomplete analyses.
   - **Regression checks:** `tests/test_scene_detection.py` measures successful reads from the real secondary decoder. The repro read 30 frames for seven signals before the fix and stays within seven after it. The OpenCV/PySceneDetect passes follow the analyzed frame limit; FFprobe's full-source frame/timestamp probe remains uncapped.

## Changes completed during setup review

- Expanded `.gitignore` for private media, production files, environments, caches, model weights, downloaded installers and local agent configuration. Shared skill sources, manifests, lockfiles, configuration examples and existing parser fixtures remain trackable. Checked representative paths and confirmed private setup/environment files are not already tracked.
- Kept incompatible AI libraries in separate environments on the selected tools drive. Repository configuration contains lockfiles and instructions; machine-specific status belongs under ignored `local/setup/`.
- Corrected malformed YAML in the locally installed upstream kinetic-reel skill. The original revision and one-line patch are recorded in `studio/tools/creative/manual-skills.json`.
- Added the [full toolchain map](full-toolchain.md), with branches, checks and model requirements for both agents.
- Regenerated four creative skill entries from official GitHub URLs with exact commit references, removing machine-specific source paths from their lockfile. Verified all 25 installed upstream skill frontmatters and both-client links.

## Verification and scope

Remediation verification: `uv run pytest` passed **47 tests**; `uv run ruff check src tests` passed. The original setup suite had 25 tests; the three new regression files add 22 cases. Fresh evidence is recorded in ignored `local/setup/pytest-remediation.log` and `local/setup/ruff-remediation.log`.

Earlier setup checks passed for studio TypeScript and libraries, Remotion/Blender renders, compatibility in six Python environments, npm audit, ComfyUI startup/API/CUDA and CosyVoice imports/CLI/CUDA. They are installation evidence and do not establish complete production quality.

All destructive repro work and the new regression cases use newly generated scratch media. Original user reference files were not used. Detailed original repro results and machine checks remain in ignored `local/setup/`.

Verdict: all three findings have implementation fixes and regression coverage. Linked output destinations are refused; unavailable exact timestamps now produce an explicit error.

Not checked: a full reread of the After Effects parser, every library guide, live OBS capture/microphone, interactive LosslessCut editing, native Jolt GPU backends, model-based speech/generation quality or a complete production episode. See [the toolchain guide](full-toolchain.md) for the distinction between installed dependencies and missing model/input checks.
