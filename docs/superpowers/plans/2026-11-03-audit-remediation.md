# Audit Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Track steps with checkboxes. The user authorized execution by the existing Gemini 4 Argon agent in the neighboring Orca tab. Do not spawn extra agents unless needed and authorized.

**Goal:** Fix the seven audited correctness, memory, safety, CLI, and test-portability issues without expanding Phase 1 features.

**Architecture:** Preserve the Python CLI, existing analyzers, Pydantic output models, and report writers. Change shared code at the source of each issue, preserve public contracts where possible, and document any necessary output-schema change.

**Tech Stack:** Python, uv, pytest, Pydantic, Typer, OpenCV, ffprobe, py-aep.

**Spec:** The seven reproduced/static findings below, plus repository `AGENTS.md` and `docs/limitations.md`. Baseline: `c4baee3` on `master`; audit changed no source code.

## Global Constraints

- Read and obey `AGENTS.md`: never overwrite, delete, rename, or move original projects/videos.
- Never execute untrusted project expressions, scripts, or plugin binaries.
- Keep processing local by default; do not add paid/cloud calls.
- Separate `observed`, `inferred`, `unavailable`, `unsupported`, and `error` honestly.
- Use Superpowers debugging/test/verification workflows and Ponytail full: the smallest complete change, existing dependencies first, no unrelated cleanup.
- Work in the existing `F:\code\git\VFXLens` checkout; preserve unrelated user edits and do not reset or amend existing commits.
- Run a failing regression before each nontrivial fix, verify it passes afterwards, and commit the completed task using explicit paths.

## Review Focus

- High-resolution and long videos must not retain all original frames in RAM (Task 1).
- Partial/malformed AEPX input must not invent dimensions or timing (Task 2).
- A different project, malformed payload, or unsuccessful AE response must not count as verified comparison (Task 3).
- Empty or partially decoded video and invalid frame caps must not produce misleading success/coverage (Task 4).
- Failed parsing must still check source integrity; fresh checkouts must have explicit fixture behavior (Tasks 6 and 7).

## Baseline Verification

- `uv run ruff check src tests --output-format concise`: passed.
- `uv run pytest -q`: 13 passed, 1 failed in 96.09s. The failure was `tests/test_cli.py::test_cli_analyze_video_and_inspect`, where analyze-video exited 1; the original test did not show the captured CLI error.
- Running that exact test alone passed in 14.26s. Its cause is UNKNOWN: do not label it fixed or blame memory without evidence. Improve failure diagnostics if necessary and investigate if it recurs.
- No live AE bridge or commercial plugin execution was tested.

### Task 1: Bound video-frame memory

**Files:** `src/vfx_engine/video_analyzer/analyzer.py`, `decoder/ffprobe_decoder.py`, `frame_analysis/signal_extractor.py`, `frame_analysis/contact_sheet.py`; `tests/test_video_analyzer.py`.

**Interfaces:** Preserve `VideoVFXAnalyzer.analyze(video_path, output_dir, max_frames=None)` and its result/timeline tuple. Reuse `DecodedFrame`, `iter_decoded_frames`, signal extraction, and evidence export; update their internal callers together if signatures must change.

**Evidence:** The analyzer appends every decoded full-resolution BGR image to a list before analysis. A 3840x2160, 60fps, 15-second clip requires 20.86 GiB for those image buffers alone. Adaptive analysis does not reduce that allocation.

- [ ] Add a regression that instruments decoded image lifetime/buffering across increasing frame counts, asserting retained full-resolution frames are bounded rather than proportional to clip length. Do not allocate a real 20 GiB fixture.
- [ ] Run the regression and confirm it fails on the current implementation.
- [ ] Process frames incrementally or retain only bounded/compact analysis data; reread selected original frames for evidence. Preserve chronological metrics, adaptive windows, evidence timestamps, and source read-only behavior. Audit all callers before changing contracts.
- [ ] Run the regression and existing video tests; verify evidence exports still exist and match their requested frames. Include empty/failed decode behavior.
- [ ] Commit the relevant implementation and tests with `fix: bound video analysis frame memory`.

### Task 2: Represent missing AEPX data honestly

**Files:** `src/vfx_engine/project_analyzer/parsers/aepx_parser.py`, `src/vfx_engine/schemas/project_schema.py`, `src/vfx_engine/reports/project_reporter.py`, affected comparator/callers; `tests/test_project_analyzer.py`.

**Interfaces:** Preserve `parse_aepx_project(project_path, analysis_id, rerun_command) -> ProjectAnalysisResult`. Inspect schema requirements and every consumer before deciding how unavailable numeric fields are represented.

**Evidence:** `<AfterEffectsProject><Item><string>UnknownComp</string><cdta /></Item></AfterEffectsProject>` returns width=1920, height=1080, frame_rate=30.0, duration=10.0 without source data for any of them.

- [ ] Add a regression for that exact XML: missing dimensions/timing must be unavailable or unsupported, never asserted as measured 1920x1080/30fps/10s. Include a partial valid dimension case and malformed XML rejection.
- [ ] Run the regression and confirm the existing fabricated values fail it.
- [ ] Remove invented defaults; expose missing-field provenance and update schema/report/comparator consumers only as required. Preserve values actually present in XML.
- [ ] Run affected project/report tests and the regression; document any necessary JSON schema compatibility change.
- [ ] Commit with `fix: report unavailable AEPX metadata honestly`.

### Task 3: Require project identity before live comparison

**Files:** `src/vfx_engine/project_analyzer/analyzer.py`, `ae_bridge/bridge_client.py`, `normalizer/comparator.py`, `ae-scripts/vfx_readonly_extract.jsx`; `tests/test_project_analyzer.py`.

**Interfaces:** Keep offline analysis available regardless of bridge availability. Extend live payload identity only as required by `analyze_ae_project(..., use_ae_bridge=True)`.

**Evidence:** `fetch_live_project_state()` inspects the current `app.project`, without relating it to the input file. Mocking an unrelated project B while analyzing A still yields `live_bridge_tested=True` and `extraction_method='hybrid_compared'`.

- [ ] Add mocked bridge regressions for matching identity, different project identity, identity missing, and an unsuccessful/malformed bridge response. Only the matching successful payload may produce a verified hybrid comparison.
- [ ] Run those tests and confirm the mismatched case fails on current code.
- [ ] Verify the live project's canonical file identity before comparison; when identity cannot be established, return the offline result with an honest warning. Do not open the original or silently replace the user's active project. Any snapshot-based solution must obey AGENTS.md.
- [ ] Run project tests without contacting or modifying a real AE session. Record that live integration remains untested unless actually exercised safely.
- [ ] Commit with `fix: verify AE project identity before live comparison`.

### Task 4: Preserve source totals for capped analysis

**Files:** `src/vfx_engine/video_analyzer/analyzer.py`, `src/vfx_engine/cli/main.py`, relevant video schemas/reporter; `tests/test_video_analyzer.py`, `tests/test_cli.py`.

**Interfaces:** Keep the CLI option `--max-frames` and the analyzer parameter. Distinguish source totals, decoded/analyzed counts, and dense-sampling coverage explicitly; maintain existing meaning for uncapped runs.

**Evidence:** A 10-frame, 1-second video analyzed with max_frames=3 reports metadata.frame_count=3, total_video_frames=3, coverage_ratio=1.0, no warning, and a rerun command lacking the cap.

- [ ] Add a 10-frame fixture regression capped at 3: source total remains 10, processed count is 3, partial coverage is explicit, and rerun command contains `--max-frames 3`. Test zero/negative caps and incomplete decoder output too.
- [ ] Run the regression and confirm it fails on the current behavior.
- [ ] Stop overwriting source counts, represent partial processing honestly, preserve the cap in rerun commands, and reject non-positive caps at CLI and programmatic trust boundaries.
- [ ] Run affected CLI/video tests; verify uncapped behavior and reports retain correct totals.
- [ ] Commit with `fix: report capped video coverage accurately`.

### Task 5: Make batch errors visible to automation

**Files:** `src/vfx_engine/cli/main.py`; `tests/test_cli.py`.

**Interfaces:** Preserve `analyze-folder` options and `batch-summary.json`. Successful batches exit 0; any per-file errors must produce nonzero exit after the summary is written.

**Evidence:** A directory containing only a corrupt `.aep` produces 0 successful projects, 1 error, and exit code 0.

- [ ] Add tests for all-failed and mixed-success batches: summary is present and preserves successes/errors, exit code is nonzero. Keep an all-success exit-0 case.
- [ ] Run the tests and confirm current error batches incorrectly exit 0.
- [ ] After writing the summary, exit 1 if errors exist. Keep processing other files and preserve the current `.aex` skip behavior.
- [ ] Run the CLI suite and commit with `fix: return failure status for batch analysis errors`.

### Task 6: Check integrity even when parsing raises

**Files:** `src/vfx_engine/core/safety.py`; `tests/test_project_analyzer.py` (or a focused `tests/test_safety.py` if clearer).

**Interfaces:** Preserve `readonly_file_guard(path)`, `ReadOnlyFileGuard`, and `FileIntegrityViolationError`; retain the original parser error as chained context when integrity also fails.

**Evidence:** Inside the guard, modifying a disposable file then raising `ValueError('parser failed')` bypasses the post-yield hash check and reports only ValueError.

- [ ] Add tests for unchanged success, changed success, unchanged parser error, and changed parser error. Use temporary disposable files only.
- [ ] Confirm changed-plus-error fails to produce `FileIntegrityViolationError` before the fix.
- [ ] Move the post-operation integrity check into exception-safe cleanup. Preserve the original parser exception when unchanged and its context when integrity fails.
- [ ] Run all safety/project tests and commit with `fix: verify source integrity on exceptional exits`.

### Task 7: Make fixture setup reproducible

**Files:** `tests/conftest.py`, `README.md`, a fixture setup script only if needed, and test files required to separate optional external-fixture integration tests.

**Interfaces:** Preserve self-contained unit tests. Do not commit proprietary user files or silently fetch executable/untrusted data while running pytest.

**Evidence:** `real_ae2026_complete_aep` asserts a file under `references/py-aep/samples/versions/ae2026/complete.aep` exists. No references files are tracked; `.gitignore` excludes that directory, and README setup does not provision it.

- [ ] Reproduce fixture behavior with the optional reference file absent using a temporary/mocked path; do not move/delete the actual reference checkout.
- [ ] Document exact reference repository/revision and deterministic setup if integration tests require it. For missing optional fixtures, skip clearly with a setup reason while keeping core unit tests runnable; use a redistributable tracked fixture only if its license is verified.
- [ ] Verify both provisioned integration tests and absent-reference behavior. Ensure skipped tests are reported rather than described as full integration success.
- [ ] Commit with `test: make external AE fixture setup reproducible`.

## Final Verification and Delivery

- [ ] Run `uv run ruff check src tests --output-format concise` and `uv run pytest -q` after all fixes. Read exit codes and complete failure output.
- [ ] Investigate the baseline CLI video failure if it recurs; do not accept a single isolated pass as proof that it is fixed.
- [ ] Check `git diff --check`, `git status --short`, and commits. Confirm source inputs remained unchanged during integration tests.
- [ ] Report each of the seven issues as fixed or explicitly blocked, with test evidence, schema/CLI behavior changes, and remaining limitations. Do not claim real live AE/GPU/4K verification without running it.
- [ ] Stop after delivery; do not publish, push, or expand Phase 2 scope unless separately requested.
