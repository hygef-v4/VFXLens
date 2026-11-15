# Story direction and shot choreography

Use this with the existing [production workflow](../../../../workflows/create-video.md),
[reference study](../../../../workflows/study-reference.md), [shot contract](scene-composition.md),
and [motion direction](motion-design.md). This adds story and editorial continuity;
it does not add a second checkpoint or approval gate.

## Find the film's turn

Before choosing effects, write one sentence for what changes for the audience. For
a product or explainer, name the non-obvious behavior and its visible consequence;
show that behavior using the product's own objects/data or a clearly marked
creative metaphor. For a character story, state who wants what, what changes, and
how the ending answers the opening. If the idea only works as a slogan, find a
visible action that proves it.

Give the film one dramatic spine: a recurring object, number, shape, gesture, or
camera direction that changes meaning as the story advances. It may return in a
new state at the ending. Each beat should advance the turn, prove a claim, or give
the audience time to read; remove beats that do none of these. Treat these as
prompts for the existing treatment/shot list, not mandatory additional documents.

## Give each shot an editorial reason

Add a reason to the existing shot contract for the framing and move: what becomes
visible, what is concealed, or what scale/relationship changes? A push can close
on the control that changes; a pull can reveal context; a track can follow the
thing that travels; a crane or dive can connect overview to a meaningful detail.
Hold when the audience needs to understand the result. A locked camera is a valid
choice. Do not add camera movement to satisfy a quota.

Choreograph the lead action as anticipation → action → consequence/settle. Give
secondary actions a supporting role and offset them only when order or emphasis
helps comprehension. Preserve contact, silhouette, prop attachment, and the
subject's screen position through the move. A camera and object may share an
absolute progress parameter when that makes the move read as one motivated action.

At a cut, identify what carries the viewer's eye: object, shape, scale, direction,
velocity, light, or sound. Match only the properties that serve the idea; use a
clean cut or a deliberate hold when continuity would confuse. Record the handoff
in the existing shot/event data. Do not turn a technique library's preferred
seam ratio, camera count, or shot length into a universal target.

## Direct and review with evidence

For a reference-led film, separate observed source details from inferred story or
camera grammar and from new creative decisions. Keep actual frame/PTS locators,
transcript limits, and source status in the production's existing reference/checkpoint
files. A style prompt or short demo is not proof of how an original shot was made.

Review a representative still and a short moving render at delivery aspect ratio
before extending a treatment. Ask whether the subject and action read, the intended
change is visible, the camera earns its move, the handoff is clear, text is legible,
and timing leaves a readable hold. Inspect entrance, action/contact, text completion,
and exit/cut neighbors as required by the shot contract. Turn each issue into one
specific change and inspect the affected frames again. Keep visual approval based
on viewed output; automated scores, a contact sheet, a successful render, or a
reference repository's claim do not establish it.

For longer work, review each shot while building and review the complete film for
story, continuity, pace, sound, and delivery. Update the one existing
`local/productions/<slug>/production.md` with observed checks, remaining limits,
and the next action. Do not require an extra user sign-off during autonomous work;
follow the user's existing authorization and the workflow's stated checkpoints.

## Stack and reproducibility

These are directing practices, not drop-in code. Keep implementation in the
installed VFXLens stack and use Remotion's absolute-frame model. A useful
upstream pattern is to author one timeline/cue map for picture and sound, then
review the actual rendered result. External kits that add a second engine,
renderer, runtime, model service, or dependency tree are references only.

For every animated state, preserve the existing render invariant:
`state = f(frame, fps, inputs, seed)`. Do not import a browser playback loop,
wall clock, stateful integrator, automatic cloud call, or random unseeded
choice from a reference implementation. Verify installed APIs and package
compatibility before adapting any code; references may target different Remotion,
Three.js, React Three Fiber, browser, or rendering versions.

Source notes: these five pinned repositories informed the directing prompts, not
the implementation. [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft/tree/6700db2ba80572ebc777b99d72049679fed9840c),
[cinecode](https://github.com/sarpstar/cinecode/tree/c8a3e7552699360a2b0142c9620882af2069eedb),
[lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6),
[claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts/tree/e3b817b6afc6cd413466d43f11ba31209e034bbf),
[cinetic](https://github.com/Leonxlnx/cinetic/tree/f4bbfc844877891fe92279d47b7874fb44d485ae).
License boundaries, inspected paths, implementation limits, and rejected patterns
are recorded in the external audit notes.
