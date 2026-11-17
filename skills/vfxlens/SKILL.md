---
name: vfxlens
description: Use when learning VFX or motion graphics from PDF/docs, analyzing video or AE projects (.aep/.aepx), writing video scripts or narration, or creating and continuing a video through MP4 export with VFXLens.
---

# VFXLens

Use the shared knowledge library, existing read-only analyzer, and local video
studio. Preserve the user's requested scope: studying ends with evidence-backed
notes; making a video includes implementation; requested MP4 export includes the
actual file and checks.

## Locate the shared repo first

The skill may be loaded through a global symlink/junction while working in another
project. Resolve its **actual skill directory** supplied by the skill loader,
including the junction path, rather than deriving anything from the current cwd:

```powershell
python -c "from pathlib import Path; print(Path(r'<actual skill directory>').resolve().parents[1])"
```

Replace the placeholder with the loaded directory containing this `SKILL.md`, not
the file itself. `skills/vfxlens/` resolves to `<repo>/skills/vfxlens/`, so
`parents[1]` is `<repo>`. Verify `<repo>/AGENTS.md`, `library/README.md`, and
`pyproject.toml` exist. A copied skill without the repo beside it needs the actual
checkout located before executing commands; do not guess a machine-specific path.
All repo paths below refer to this resolved root, regardless of cwd.

Read `<repo>/AGENTS.md` and applicable instructions in the user's active project
and the directories being changed. Resolve relative user inputs against their
original working directory before running tools in VFXLens. Inspect existing
production files and changes before continuing another agent's work.

## Route by the requested outcome

| Request | Read and act |
| --- | --- |
| Learn from a PDF, document, article, video or AE reference | Read `<repo>/workflows/study-reference.md`; use the analysis commands below when applicable. |
| Analyze a video or `.aep`/`.aepx` | Read the study workflow's media section; run the existing analyzer and inspect actual artifacts. |
| Write a hook, outline, video script or narration | Read `<repo>/library/content-writing/README.md`; draft sourced visual beats in the production checkpoint or its linked script. Finish with the requested writing, without expanding a script-only task into rendering. |
| Create, recreate, revise or continue a video | Read `<repo>/workflows/create-video.md`; study supplied references first when relevant. |
| Story Short with 3D cartoon characters (three.js picture, ElevenLabs audio, Remotion assembly) | Read `<repo>/workflows/create-video.md`, then `<repo>/workflows/threejs-character-short.md`. |
| Long-form 2D explainer or story video (16:9, Remotion SVG puppets, GSAP text, three.js shots, ElevenLabs voices) | Read `<repo>/workflows/create-video.md`, then `<repo>/workflows/2d-long-form-video.md` (skill `longform-2d`). |

Read `<repo>/library/README.md` to find canonical techniques, styles, resources and
case studies. Reuse those articles; keep exact source evidence separate from a
proposed new creative treatment. Follow `library/CONTRIBUTING.md` when adding
reusable knowledge, including its English article convention. Write user-facing notes
and production documents in the user's language.

## Existing analysis CLI

Use absolute input/output paths so running from another project is predictable.
Choose a fresh analysis directory under `<repo>/outputs/`:

```powershell
uv --directory "<repo>" run vfx doctor
uv --directory "<repo>" run vfx analyze-project "<absolute input.aep>" --output "<repo>/outputs/<analysis-id>"
uv --directory "<repo>" run vfx analyze-video "<absolute input.mp4>" --output "<repo>/outputs/<analysis-id>"
uv --directory "<repo>" run vfx inspect "<repo>/outputs/<analysis-id>/video-analysis.json"
```

For projects, inspect `project-analysis.json` instead. The analyzer does not
produce a new video; use studio render scripts for production. Use
`analyze-folder --help` for batch analysis and command-specific `--help` for options.

## Boundaries and continuation

Keep original PDFs, projects, videos and assets untouched. AE bridge operations
remain read-only: isolated temporary project copy, close with
`CloseOptions.DO_NOT_SAVE_CHANGES`; inspect expressions statically and never load
untrusted plugins/scripts. Use local processing by default; paid services require
explicit configuration and authorization.

Keep private inputs, episode documents, generated scenes and exports under
`<repo>/local/productions/<slug>/`; keep analysis artifacts under `outputs/`.
Commit reusable production code in `studio/src/`. Copy renderer-needed assets
into the ignored `studio/public/media/<slug>/` only after checking ignore rules.
Respect an explicitly requested alternate output location and its instructions.
Do not put private media, inventories or model caches in tracked files.

For handoff, update the existing production checkpoint described in the creation
workflow. A checkpoint supports another Claude/Codex session; it does not launch
background work or promise execution after the current session ends.
