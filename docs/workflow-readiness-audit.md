# Workflow and Skill Readiness — 2026-11-15

What this repo does: VFXLens combines local AE/video analysis, a reusable writing/editing library, and an agent-guided production workflow. This review assumes one person using Claude/Codex on the configured Windows workstation, with original reference files kept read-only.

**Verdict:** sufficient for a repo-backed **v1 skill and agent-guided workflow**. Full production readiness is not established: the live AE preview boundary has a confirmed injection issue, and the documented isometric/cartoon production route still needs a representative end-to-end pilot. This is a readiness report; application code was not changed during the review.

## What Is Ready

| Area | Evidence and present limit |
| --- | --- |
| Skill packaging and repo location | Skill Creator validation passed with UTF-8 enabled. Both client junctions resolve to the canonical skill; resolving from an unrelated working directory found the repo and workflow files. Fresh interactive invocation in both client UIs remains unchecked. |
| Knowledge and writing | Content Writing, foundations, techniques, styles, resources and case studies are connected to the workflows. File-link checks across 68 library/docs/workflow pages found no missing local files, but 18 section anchors are broken. |
| Reference learning | The workflow includes an approximately ten-minute initial scope, source-language TXT/SRT/JSON and separate Vietnamese writing lessons. Two private studies have actual offline transcripts; the latest has 207 segments over 0–600s. ASR quality/timing has not been listening-verified. |
| Analysis core | Fresh `uv run pytest`: **47 passed**. Fresh Ruff passed. Doctor reports ready for local analysis, FFmpeg/ffprobe and GPU available; live AE bridges are offline. |
| Installed dependencies | Fresh compatibility checks passed in all six Python environments. Studio TypeScript and library smoke checks passed. This establishes installed package compatibility, not every creative branch's output quality. |
| Remotion output | A fresh H.264/AAC smoke MP4 rendered: 1080×1920, 30 fps, 300 video frames, about ten seconds. Full decode passed; frames 30/180 were inspected and all four audio cues had measured nonzero RMS. No perceptual listening was performed. |
| Browser 3D | A fresh Three.js cube still rendered and was visually inspected. This does not validate a complete isometric set or character scene. |
| Continuation | Workflows specify a production checkpoint, editable sources, actual commands, checked artifacts, open issues and the next action. A full handoff between fresh Claude/Codex sessions has not been demonstrated. |

## Must Fix Before Live AE Preview Use

1. **Preview arguments can escape into executable JSX** — `src/vfx_engine/project_analyzer/ae_bridge/bridge_client.py:337–367`, `ae-scripts/vfx_readonly_extract.jsx:260–268`.
   - **What this is:** `export_preview_frame` constructs a script from a composition name and output path, then dispatches it through the live AE bridge.
   - **Problem:** Only double quotes in the composition name are escaped; a backslash/quote combination can break out of the literal. A harmless offline repro captured the actual dispatched payload and executed it with stub objects in a Node VM: a marker assignment ran. The defined read-only validator was called zero times. An existing non-PNG destination was also accepted by the mocked adapter; actual AE file writing was deliberately not tested.
   - **Smallest fix:** Serialize JS string arguments safely, validate a finite time and a fresh PNG destination before dispatch, and apply the intended script-validation boundary. Keep snapshot/project safety intact; add transport-level regression tests for hostile names and unsafe destinations.
   - **If skipped:** Composition names or caller-supplied paths can cross from data into host script execution. Do not treat this preview API as a verified read-only boundary. It is not used by the current offline analysis CLI or Remotion workflow.

## Should Fix

2. **Vision configuration is not a working vision adapter** — `src/vfx_engine/vision/base.py:51–98`, `src/vfx_engine/core/doctor.py:101–109`, `docs/limitations.md:46–48`.
   - **What this is:** The CLI exposes provider/model/base-URL configuration and a configured adapter class.
   - **Problem:** The factory does not forward the configured base URL, and the adapter returns `unavailable` even with an endpoint. A local check with a dummy provider/model/base URL confirmed `analyzed=false`, effective endpoint `None`, and no network request. Doctor's configured flag does not establish usable inference.
   - **Smallest fix:** Make documentation and doctor explicitly distinguish a placeholder/configuration from implemented inference. Implement and test an explicitly authorized provider separately when needed; do not enable external calls as an audit side effect.
   - **If skipped:** An agent may expect semantic analysis after setting configuration. An assistant can still inspect exported images with its available tools; that is separate from this CLI adapter.

3. **Eighteen evidence/recipe section links point to obsolete headings** — examples: `library/techniques/camera-and-motion/shake-envelope.md:17`, `library/case-studies/takt-op.md:9`, `library/case-studies/ae-notes.md:28`.
   - **What this is:** Local Markdown links use fragments to jump directly to relevant source sections.
   - **Problem:** Several case-study headings changed language/title while incoming fragments kept older English or different Vietnamese identifiers. Files exist, so a file-only link check misses this failure. The audit recorded 18 exact source-line/target-heading mismatches.
   - **Smallest fix:** Update the fragments or introduce stable explicit anchors, then check both files and fragments.
   - **If skipped:** The library is readable, but agents/readers cannot reliably reach the cited recipe or evidence section.

## Narrow Discovery Improvement

4. **Script-only work is implicit in the entrypoint** — `skills/vfxlens/SKILL.md:3,35–42`.
   - **What this is:** Content Writing now supports hooks, outlines and narration; production docs also define document-only outcomes.
   - **Problem:** The skill description and route table name learning, analysis and video creation, without a dedicated video-script/voiceover-writing branch. Explicit skill invocation can reach the material; automatic selection for a script-only request has not been demonstrated.
   - **Smallest fix:** Add a narrow video-script/outline/narration trigger and route to Content Writing plus the existing production checkpoint. Preserve script-only scope without rendering a video.
   - **If skipped:** Manual invocation remains usable, but automatic discovery is less explicit than the project's actual writing capability.

## Production Work Still Needed

These are capability gaps, not claims that every skill must ship a full application:

- **One representative production pilot.** `studio/src/` currently contains registration plus `SmokeTest` and `ThreeCheck`. The component names in `workflows/ai-assisted-motion-graphics.md:64–66` are proposed roles, not implemented asset/character libraries. Build one 10–15-second isometric or cartoon shot from a real brief/script, with the selected voice/captions, render it and record visual/audio review. This proves more than adding further tool families.
- **Reusable study execution.** The ten-minute sampling, selected-clip mapping and TXT/SRT/JSON extraction used private per-study helpers. The shared CLI remains an analyzer, without a bounded study/transcription command. Promote only the recurring, validated operations into a small shared helper when making the workflow repeatable; preserve scope and exact source locators. This is not necessary for skill format validity, but reduces repeated agent scripting and path mistakes.
- **A selected narration path.** Cached faster-whisper supports local recognition; it is not speech synthesis. Vietnamese TTS/voice quality, model availability for synthesis branches and complete lip/caption alignment remain unverified. Use an authorized supplied recording or explicitly selected/tested synthesis route for the pilot.
- **A complete repository snapshot.** Current learning/content-writing/style/workflow additions include uncommitted files. They work in this checkout but are not all present in the last commit; a checkout of that commit does not reproduce the current knowledge base. Review and commit them when packaging this version.

## Recommended Order

1. Close the live-preview script/output boundary and add regression tests before enabling that branch.
2. Correct the section anchors and capability reporting; clarify script-only routing.
3. Run one representative script-to-MP4 pilot and a fresh-session continuation. Record the working commands, assets, chosen voice and observed quality limits.
4. Package the proven study helpers and commit the reviewed knowledge/workflows. Further model/tool additions should follow a concrete production need.

## Verification Scope

The review covered the repo entrypoints/workflows, library Markdown, source analyzer/bridge/vision/report code, tests, studio code/scripts and tool manifests/setup guides. Fresh checks were pytest, Ruff, doctor, six Python dependency checks, studio typecheck/library checks, MP4 rendering/decoding/probing, encoded-frame inspection, a Three.js still, skill validation/path resolution and local file/fragment link checks. Evidence is kept in ignored setup records.

**Not checked:** live After Effects execution or actual preview file writing; fresh skill UI invocation in both clients; new TTS/image-generation inference; complete cartoon/isometric reconstruction; perceptual audio listening; fresh-machine reinstallation of every external application. No paid services, model downloads or original-reference mutations were performed. A passing test suite does not cover the preview injection found by this review.
