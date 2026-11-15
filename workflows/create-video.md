# Create or continue a video

Use the repo resolved by `skills/vfxlens/SKILL.md`. A planning-only request ends
with populated decisions and a next action. A production request continues through
implementation; a request including MP4 export ends with a real checked file or
a concrete blocker and the editable work completed so far.

## Resume and define the film

Inspect existing work and instructions first, including uncommitted source and
the current production documents. Reuse their names and decisions. For a new
production, maintain one compact
`<repo>/local/productions/<slug>/production.md`; split it only when useful. Capture:

- Brief, audience, message, duration, dimensions, fps, composition ID and outputs.
- Actual reference/assets with provenance, permissions and missing inputs.
- Chosen style, storyboard intervals, global event frames and shared audio cues.
- Voice/caption timing, implementation/source locations, progress and open issues.
- Exact commands, observed review/export results and the next executable action.

Write these user-facing notes in Vietnamese by default. Fill real decisions;
empty templates are not a handoff. On continuation, check that documented files
and exports still exist, then advance from the recorded next action. Do not reset
another agent's work or imply that a handoff automatically runs in the background.

Honor the user's format. If only “10s vertical” is supplied, a useful recorded
assumption is 1080×1920 at 30 fps: 300 frames. This is a contract for that film,
not a setting to inherit from a PDF or overwrite in an existing production.
Study supplied references through `workflows/study-reference.md` as needed.

For hooks, the narrative outline and narration written for visuals, read
[Content Writing](../library/content-writing/README.md) before locking the script
and storyboard. Keep the current script in the production checkpoint or its linked draft.

For AI-assisted motion graphics, isometric or cartoon explainers, or infographic videos,
follow [the specialized production route](ai-assisted-motion-graphics.md) for
classification, scene planning and tool selection, then use this workflow's
shared render/review and handoff steps.

## Choose and prepare local tools

When the brief requires discovering or choosing new animation technology, use
[motion-scout](../skills/motion-scout/SKILL.md) for a live research-only pass first.
Reuse adequate local code; otherwise record its selected source/commit, license,
dependencies and adaptation/tests in the existing production checkpoint. The
Director consumes that handoff for the authorized build; it does not recursively
restart scouting. Research alone does not authorize installation.

Use the existing `<repo>/studio/`, its package lock and package scripts. For any
Remotion work, explicitly read
`<repo>/studio/.agents/skills/remotion-best-practices/SKILL.md` **when it exists**;
it is outside global skill discovery when invoked from another project. Follow
its relevant references and the installed package APIs. If missing, report that
and offer/run installation within the authorized setup scope, from `studio/`:

```powershell
npx skills add remotion-dev/skills --skill remotion-best-practices -a codex -a claude-code
```

Check the target before installation and preserve existing skills. Missing
upstream guidance does not block study, planning or all production: use the
existing studio code and official docs for the installed version. For environment
setup, read `<repo>/docs/ai-video-requirements.md`; do not create a new dependency
tree for each agent or film, or treat the analysis CLI as a renderer.

For the installed Three.js, audio-analysis, HyperFrames or creative-toolkit
branches, read `<repo>/docs/full-toolchain.md` and then only the relevant tool's
instructions. Treat model availability separately from package installation.

Use Remotion for typography, graphic motion, compositing and assembly. Add Blender
only for shots that benefit from spatial sets/cameras. Inspect the live Blender
session before acting; preserve existing and unsaved work. Generate a new scene
in a separate file/process as needed, save it inside the production directory,
and never clear or overwrite the user's scene. Reference AE projects remain
read-only; make new production sources separately.

For cinematic 3D, procedural shaders/particles, image-based procedural modeling,
or 3D explainers, read the project [Remotion 3D Director skill](../.agents/skills/remotion-3d-director/SKILL.md).
Use its relevant references with this workflow's existing production checkpoint;
it does not replace the shared study, privacy or delivery rules.

Keep production code under `studio/src/`, private scene/media/documents under
`local/productions/<slug>/`, and renderer copies under ignored
`studio/public/media/<slug>/`. Check ignore coverage before copying private files.
Use authorized/licensed assets. Local tools are the default; do not initiate paid
services or large model downloads merely because a workflow mentions them.

## Build from timing to image

If narration is required, use the user's actual recording first. Measure its
pauses and phrase boundaries before finalizing shots/captions; local Whisper can
assist when installed. Read the voice environment instructions before using it.
Transcription and word timing require listening/correction, especially for
Vietnamese. Without actual voice, label timing/caption estimates; choose a silent
or text-led version only when compatible with the brief. Do not present estimated
captions as aligned to speech or use English words-per-minute as Vietnamese timing.

Storyboard each shot's entrance, landing, readable hold, action and exit. Share
event IDs/global frame numbers between picture and audio. Use half-open shot
intervals `[start, end)`; Remotion starts at frame 0. A Blender sequence starting
at frame 1 maps Blender frame `f + 1` to Remotion frame `f` for equal fps; document
any other origin, offset or resampling. Source VFR uses measured PTS, while the
production timeline uses its declared fps. CLI frame-range endpoints may be
inclusive: a 300-frame film runs from 0 through 299.

Render a still per shot before detailed motion, then a short moving test. For
2.5D, test a simple set and camera, light and dress it, place flat artwork, establish
contact shadows, expression changes and parallax, then composite the shot. Keep
the technique proportional to this brief. Inspect at phone size: readable copy,
safe placement, clean cutout edges and clear visual hierarchy matter more than
adding effects. Keep animation deterministic from frames; use the upstream
Remotion skill for implementation details instead of wall-clock/CSS timing.

## Review, render and hand off

Read `studio/package.json` before invoking scripts. From `<repo>/studio/`, the
shared scripts accept the composition and explicit production output path:

```powershell
npm run typecheck
npm run still -- <CompositionId> "<production>/preview.png" --frame=<frame>
npm run studio
npm run render -- <CompositionId> "<production>/final.mp4"
```

Choose an unused output name or revise only a generated output for this task;
never use an original reference as the destination. Stills verify composition;
also inspect moving previews, neighboring frames around transitions/cue hits,
the contact sheet and the audible mix. Correct observed problems before delivery.

When MP4 was requested, render it and inspect the encoded file, for example:

```powershell
ffprobe -v error -count_frames -show_entries stream=index,codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,sample_rate,channels:format=duration -of json "<production>/final.mp4"
ffmpeg -v error -i "<production>/final.mp4" -f null -
```

Check dimensions, fps, frame count/duration and expected audio streams against
the film contract. Listen to the final mix and inspect representative encoded
frames plus cut/cue boundaries. A successful render or probe alone proves neither
visual quality nor audibility; record any review the environment cannot perform.

Update the checkpoint with editable sources, assets, final MP4 path, exact render
command, checks actually observed, remaining issues and next action. Report these
concisely to the user. A failed export stays failed until the specific blocker is
resolved; do not label a storyboard, preview or smoke-test composition as the
requested finished film.
