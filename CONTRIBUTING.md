# Contributing to VFXLens

Thanks for helping. VFXLens has three parts; pick the one your change touches:

| Part | Where | Checks |
| --- | --- | --- |
| Analyzer (`vfx` CLI) | `src/vfx_engine/`, `tests/` | `uv run ruff check src tests`, `uv run pytest` |
| Studio and Short toolkit | `studio/` (Remotion), `studio/tools/threejs-short/` | `npm --prefix studio run typecheck`, `node --test studio/tools/threejs-short/qa/transitions.test.mjs`, a render of the affected composition |
| Knowledge library and workflows | `library/`, `workflows/`, `docs/`, `skills/` | `uv run pytest tests/test_documentation_links.py` (links and section anchors) |

## Setup

```bash
uv sync --locked --extra dev --extra documents
npm --prefix studio ci
```

FFmpeg/ffprobe must be on `PATH`. The three.js Short toolkit also needs the
[`claude-3d-animated-shorts`](https://github.com/thuann-vn/claude-3d-animated-shorts) skill installed locally.

## Rules

- **Never commit private media or episodes.** Productions live in ignored `local/productions/<slug>/`; rendered media in
  ignored `studio/public/media/`. Shared code must not point at a private file.
- **Original user data is read-only.** Never overwrite `.aep`, `.aepx` or source videos; see `AGENTS.md`.
- **No paid calls by default.** Optional services (ElevenLabs and others) stay opt-in.
- **Label evidence.** In the library, separate what was observed or measured from inference and creative decisions
  (`library/CONTRIBUTING.md`, `library/foundations/evidence-and-validation.md`).
- **English** for code, comments and documentation.
- Keep changes small and focused; one tool per job. Explain any new dependency in `docs/full-toolchain.md`.

## Pull requests

Describe what changed and why, list the checks you ran, and say what you could not verify (for example a render you did
not watch or audio you did not listen to). CI runs the analyzer tests, lint and the studio typecheck.

By contributing you agree that your contribution is licensed under the MIT License of this repository.
