# Audit Follow-up Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Track steps with checkboxes. The user explicitly authorized the existing Gemini 4 Argon tab to fix these findings. No additional planning approval is needed.

**Goal:** Fix the four remaining issues reproduced during the second audit, with minimal changes and meaningful regression tests.

**Architecture:** Preserve the existing parser, bridge adapter, streaming analyzer, and report contracts. Let safety failures propagate, validate bridge data at the boundary, and correct the shared image exporter rather than patching callers independently.

**Tech Stack:** Python, pytest, uv, OpenCV, Pydantic, Typer.

**Spec:** The four reproduced findings and acceptance criteria below; repository `AGENTS.md` remains mandatory. Baseline commit: `07a5be0`.

## Global Constraints

- Follow Superpowers debugging, TDD, execution, and verification skills and Ponytail full. No unrelated refactors, new frameworks, cloud calls, or Phase 2 features.
- Never change original project/video files. Corruption tests may modify disposable temporary fixtures only.
- Preserve source hash checks, existing exception context, streaming frame processing, event evidence exports, and honest data-availability status.
- Use the current checkout at `F:\code\git\VFXLens`; preserve unrelated edits. Do not reset, amend, push, or start extra workers.
- Each task: reproduce with a failing regression, apply the smallest complete fix, run relevant tests, then commit explicit affected paths.
- Baseline independently verified: `uv run pytest -q` -> 21 passed in 145.35s; Ruff and `git diff --check` clean. These passing tests do NOT cover the four failures below.

## Review Focus

- Integrity failure during binary parsing of AEPX must never return a DOM fallback success (Task 1).
- A failed evidence JPEG or final contact-sheet write must not produce a successful artifact result (Task 2).
- A live response with malformed composition, layer, or effect entries must remain an offline result (Task 3).
- More event peaks than sheet slots must not cause more thumbnails than the sheet limit (Task 4).
- The bounded-thumbnail change must preserve all successfully written per-event evidence, including generator input without frame_indices (Tasks 2 and 4).

### Task 1: Propagate AEPX integrity violations

**Files:** `src/vfx_engine/project_analyzer/parsers/aepx_parser.py`; `tests/test_project_analyzer.py`.

**Interfaces:** Preserve `parse_aepx_project(project_path: Path, analysis_id: str, rerun_command: str) -> ProjectAnalysisResult`. Reuse `FileIntegrityViolationError` from `core/safety.py`; do not replace it with a generic parser warning.

**Evidence:** The broad exception handler near line 469 catches `FileIntegrityViolationError` from `parse_aep_with_py_aep` and returns DOM fallback success. A reproduction changed a temporary AEPX inside the patched binary parser, raised that error, and still received a result whose metadata SHA differed from the current file.

- [ ] Add `test_aepx_integrity_failure_never_falls_back`: write minimal XML to a temporary file, patch the inner parser to change that disposable file and raise `FileIntegrityViolationError`, and assert that same safety failure propagates. Spy on `_parse_aepx_dom_fallback` and assert it was not called.
- [ ] Run `uv run pytest tests/test_project_analyzer.py::test_aepx_integrity_failure_never_falls_back -q`; confirm it fails before the fix.
- [ ] Explicitly re-raise integrity violations before the broad fallback catch. Keep ordinary unsupported-format fallback and malformed XML rejection unchanged.
- [ ] Run the new test and `uv run pytest tests/test_project_analyzer.py -q`; all must pass, including existing partial XML fallback and guard tests.
- [ ] Commit with `fix: propagate AEPX integrity violations`.

### Task 2: Detect failed artifact writes

**Files:** `src/vfx_engine/video_analyzer/frame_analysis/contact_sheet.py`; `tests/test_video_analyzer.py`; `tests/test_cli.py` only if needed to verify error reporting.

**Interfaces:** Preserve `export_evidence_frames_and_contact_sheet(...) -> tuple[str, str, list[str]]`. A successful return must mean requested image writes succeeded. Use an informative `OSError` or existing equivalent on failed writes; include the destination path.

**Evidence:** Patching `cv2.imwrite` to return False still returns `contact-sheet.jpg` and evidence JPEG paths, although those files do not exist. Both write sites near lines 83 and 147 ignore the boolean result.

- [ ] Add parameterized regressions that return False for (a) an evidence JPEG and (b) the final contact sheet. Assert the exporter raises with the failed destination; it must not return successful artifact paths.
- [ ] Run those targeted tests and confirm they fail on the baseline.
- [ ] Check the return value at both write sites and raise clearly on failure. Only record a saved evidence path after its write succeeds. Preserve existing OpenCV exceptions and let analyzer/CLI/batch error handling propagate the failure; do not add a framework or delete user output directories.
- [ ] Run `uv run pytest tests/test_video_analyzer.py tests/test_cli.py -q`; verify normal export still creates all reported evidence and contact-sheet files.
- [ ] Commit with `fix: report failed evidence image writes`.

### Task 3: Reject malformed live comparison payloads

**Files:** `src/vfx_engine/project_analyzer/ae_bridge/bridge_client.py`, `src/vfx_engine/project_analyzer/analyzer.py` if required; `tests/test_project_analyzer.py`.

**Interfaces:** Preserve `verify_live_project_identity(target_path: Path, target_sha256: str, live_payload: Any) -> tuple[bool, str, str]`. Invalid comparison data returns False with `LIVE_BRIDGE_INVALID_RESPONSE`. Preserve current path/hash checks and offline fallback warnings.

**Evidence:** A payload `{'ok': True, 'project_file': <matching input path>, 'compositions': [123]}` passes validation. Through `analyze_ae_project(..., use_ae_bridge=True)` it produces `live_bridge_tested=True` and `extraction_method='hybrid_compared'` with no valid live composition.

- [ ] Add mocked regressions for the exact `[123]` payload, malformed layers/effects, and invalid values consumed by comparator indexing. Assert offline extraction method, `live_bridge_tested is False`, no comparison, and invalid-response warning. Test a legitimate empty composition list and a normal matching payload so validation is not over-restrictive.
- [ ] Run those targeted tests; confirm the exact reproduced case fails before the fix.
- [ ] Validate the structure and required types consumed by the comparator at the bridge boundary. Reject malformed entries rather than silently dropping them or pretending a missing collection is observed empty. Keep legitimate zero-composition/zero-layer projects valid.
- [ ] Ensure hybrid state is set only after validation and successful comparison; exceptions must not leave `extraction_method='hybrid_compared'` while `live_bridge_tested=False`.
- [ ] Run `uv run pytest tests/test_project_analyzer.py -q`; do not contact or modify real AE state.
- [ ] Commit with `fix: validate live AE comparison payload structure`.

### Task 4: Bound thumbnails before allocating images

**Files:** `src/vfx_engine/video_analyzer/frame_analysis/contact_sheet.py`; `tests/test_video_analyzer.py`.

**Interfaces:** Keep the exporter signature and `max_sheet_tiles=25` default. Bound thumbnail arrays independently of event count while still saving all requested event evidence JPEGs.

**Evidence:** A 60-frame stream with 60 distinct event peaks and `max_sheet_tiles=25` calls `cv2.resize` 60 times and retains all thumbnails. The list is truncated only afterwards near line 104. Existing RAM tests track full-resolution buffers and miss these thumbnail arrays.

- [ ] Add a regression using 60 temporary synthetic frames and 60 event peaks; count thumbnail resize calls or live thumbnail arrays and assert at most 25. Test both supplied frame_indices and generator-only input without frame_indices. Assert every event still references its successfully saved evidence image.
- [ ] Run the targeted regression and confirm the baseline exceeds 25.
- [ ] Select at most max_sheet_tiles unique valid peak indices before thumbnail creation; fill unused slots with existing uniform anchors. For unknown-length streams, enforce the same cap while streaming. Use deterministic ordering, no new dependency, and do not cap event evidence JPEGs.
- [ ] Run the new regression plus `uv run pytest tests/test_video_analyzer.py -q`, including existing bounded-original-frame-memory, VFR, and capped-analysis tests.
- [ ] Commit with `fix: bound contact sheet thumbnail allocation`.

## Final Verification and Delivery

- [ ] Run `uv run ruff check src tests --output-format concise`, `uv run pytest -q`, and `git diff --check`; inspect complete results and exit codes.
- [ ] Review the four original reproductions again against the fixes; tests passing alone is not proof of the acceptance criteria.
- [ ] Report in Vietnamese: each finding's status, commits, test counts, public behavior changes, and anything not verified. Do not claim real live AE, commercial plugin, or 4K load validation unless actually performed.
- [ ] End with remaining risks and `git status --short`. Do not push or expand scope.
