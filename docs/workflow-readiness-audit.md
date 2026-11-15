# Workflow and Skill Readiness — 2026-11-15 remediation

VFXLens combines offline AE/video analysis, a reusable writing/editing library,
live technology discovery, and agent-guided Remotion/3D production. This review
assumes one operator on the configured Windows workstation. It describes the
current checkout; ignored assets, environments and application sessions are not
included in a Git clone.

**Verdict:** usable as an agent-guided workflow. The software defects found in
the earlier readiness review have regression fixes. Live commercial-host behavior,
real Vision model accuracy and final film quality still need their own checks.

## Resolved regressions

| Earlier defect | Current behavior and regression evidence |
| --- | --- |
| AE preview string injection and unsafe output | Arguments are JSON-serialized; non-finite/negative time, non-PNG, existing/linked files and missing directories are refused before dispatch. Dispatched JSX is checked. The host also refuses existing destinations and times outside the composition. Tests execute captured JSX in an isolated Node VM; no live AE project is opened or saved. |
| Vision endpoint dropped and configured status misleading | Factory forwards the endpoint. An optional loopback OpenAI-compatible adapter validates image/response budgets, refuses cloud URLs/credentials/redirects/proxies and labels successful model claims inferred/unverified. Doctor separates configuration from a tested connection. Protocol tests use mock transport and a real localhost fixture server; no model inference is claimed. |
| Broken evidence/recipe anchors | Seventeen broken section links were reproduced and corrected against current headings. The earlier review reported eighteen. A regression check now validates authored local Markdown files and section anchors. |
| Script-only routing implicit | The shared VFXLens description and route table explicitly cover hooks, outlines, scripts and narration; script-only work stops at writing. |
| Director absent from Claude discovery | The shared link helper now registers all three authored skills for both project clients. It preserves existing unrelated folders and Director's canonical source. |

Source regression tests:
[AE preview](../tests/test_ae_bridge_preview.py),
[Vision/protocol/reporting](../tests/test_vision.py),
[documentation links](../tests/test_documentation_links.py), and
[skill registration](../skills/motion-scout/scripts/test_sync_skill.py).

## Current production and discovery routes

- [VFXLens](../skills/vfxlens/SKILL.md): study, analyze, write, create and continue.
- [motion-scout](../skills/motion-scout/SKILL.md): live discovery, comparison and a
  source-backed handoff. Research-only leaves video code/dependencies untouched.
- [Director](../.agents/skills/remotion-3d-director/SKILL.md): storyboard, renderer,
  camera/light/material/animation, actual render and visual review.
- [Production workflow](../workflows/create-video.md): one private checkpoint,
  sources/assets/timing, implementation, encoded media and delivery checks.

The studio now registers four compositions: `SmokeTest`, `ThreeCheck`,
`DirectorSkillDemo` and `EditorialExplainer`. The older statement that only two
smoke components exist is obsolete. The editorial composition requires private
assets and is a draft; correct encoding does not establish visual approval.
Character/isometric component names in the specialized workflow remain proposed
roles, rather than a complete prebuilt asset/rig library.

## Repeatable checks

```powershell
uv run pytest
uv run ruff check src tests skills/motion-scout/scripts
uv run python -m unittest discover -s skills/motion-scout/scripts -p 'test_*.py'
uv run vfx doctor --json
npm --prefix studio run typecheck
npm --prefix studio run verify:libraries
foreach ($skillName in 'vfxlens', 'motion-scout', 'remotion-3d-director') {
    uv run python skills/motion-scout/scripts/sync_skill.py --skill $skillName --check
}
```

Render the affected composition after studio changes, then inspect actual encoded
frames and audio. The setup/link check verifies filesystem discoverability, not a
fresh interactive client UI session. Fresh execution evidence stays under ignored
`local/setup/`, with the run timestamp and any unverified branch stated separately.

## Remaining production limits

Completed remediation checks on 2026-11-15: **81 pytest cases and 18 helper
unit tests passed**, plus Ruff, studio typecheck/library checks, all six skill
frontmatter checks and all three shared-link checks. A fresh 4-second H.264
Director demo passed dimensions/fps/frame count/audio policy/full decode; one
encoded frame was visually inspected. This silent demo does not test narration
or certify the unfinished editorial film.

- Live AE bridges were offline during verification; host PNG writing was not
  exercised. The adapter inspects the active project and never opens/closes it;
  use an isolated copy whenever a host project must be opened.
- Real model accuracy, pronunciation, word alignment and perceptual listening are
  separate from package installation and protocol tests. Setup-era model status
  is not a current cache inventory. No model download or paid call is implied.
- Native WebGPU capture/seek, full character acting/lip sync and a polished
  reference-matched episode need representative production tests.
- Ten-minute study/ASR sampling still uses per-study helpers; the public CLI is
  an analyzer, not a one-command full video generator.
- Existing uncommitted studio/skill work is preserved. A clone of the last commit
  does not include those changes or the ignored private media/environments.
