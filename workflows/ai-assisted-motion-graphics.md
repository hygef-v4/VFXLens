# Explainers with AI-assisted motion graphics

Read after the [shared production workflow](create-video.md) when the request is AI-assisted motion graphics, a diagram explainer, isometric/2.5D or a cartoon with characters. This workflow makes a new video; it is not a command that generates a whole video on its own.

## Classification and scope

**Motion graphics/animation → explainer → pick the visual branch.** Proposed production method: **AI-assisted, code-driven**. The AI writes the script, prepares scene data and assets, programs the motion, runs the render and checks the result. Choose each capability by the tools and inputs actually available.

| Branch | Traits and guides |
| --- | --- |
| Isometric/2.5D infographic | [Style guide](../library/styles/isometric-explainer.md), [Internet Global case](../library/case-studies/internet-global-explainer.md): spatial props, diagrams, source/status cards and recaps |
| 2D cartoon with characters | [Style guide](../library/styles/cartoon-explainer.md), [Nvidia Chips case](../library/case-studies/nvidia-chips-cartoon-explainer.md): expressions, story props, layered backgrounds, local light pools and dialogue/questions |

Record how each asset type is produced: shapes/SVG written in code, 3D scenes built in code, AI-generated images, synthesized voice or source footage. "AI-assisted" does not prove that every asset of a reference video was AI-generated; the source's original tools and degree of AI use remain unverified.

Visual traits and criteria live in the matching style guide; evidence and measured locators live in the case study. Choices made for a new video are recorded as creative decisions.

## Tools by task

| Task | Choice in this project | What to confirm |
| --- | --- | --- |
| Brief, script, shot list, code, checks | Claude/Codex through the VFXLens skill | Use the shared production checkpoint; source every claim that needs one |
| Labels, info cards, UI, timelines, stamps, assembly | Remotion + React + SVG | Frame-driven animation; read the studio's Remotion skill |
| Fixed-angle isometric illustration | Layered SVG/shapes; Three.js/R3F when 3D geometry is needed | Pick the simplest route that serves the shot; keep text on a readable 2D layer |
| 3D camera, occlusion or light | Three.js through `@remotion/three`, or Blender + MCP | Check the real shot; never replace a scene the user is working on |
| Narration | A supplied recording, or TTS (ElevenLabs, `edge-tts`) when allowed | Online calls need permission; test the voice and pronunciation before a long take |
| ASR, subtitles, word cues | Whisper (`studio/voice`); ElevenLabs forced alignment | Correct names and spellings; listen to check the timings |
| Accents and mix | FFmpeg; librosa for signal measurements | Confirm cues by ear; a speech onset is not a music beat |
| Export and file checks | Remotion + FFmpeg/ffprobe | Match the picture/audio contract and decode without errors |

Check the [toolchain](../docs/full-toolchain.md) before running anything. ComfyUI, CosyVoice and other local models are optional branches; installing a package does not mean a model, voice or suitable quality is available. Do not make cloud calls, download large models or change dependencies just because a document mentions them.

## Steps

### 1. Fix the contract and the argument

Use [Content Writing](../library/content-writing/README.md) to choose the hook, the explanation structure and how narration turns into visual ideas; apply it to the current production's script.

Create or update `local/productions/<slug>/production.md` following the shared workflow. Record the message, audience, length, size/fps, composition ID, sources, output location and missing inputs. The case study's 1920×1080 at 30 fps is reference data; use it for a new video only when chosen explicitly.

Choose the structure from the video's question and the Content Writing lessons; object-led stories and evidence classifications may need different outlines. For each claim, keep its source and its status (observed, inferred or unknown). Illustrations are not documentary evidence.

**Done when:** the contract is clear and every main point has a source and status, or is marked as missing data.

### 2. Prepare the narration and a cue-based storyboard

With narration, prepare the recording or test a short, permitted TTS sample first. Measure the real audio, then place picture cues; without audio, mark times as estimates and keep the final alignment open.

Each shot in the checkpoint has these fields:

| Field | Content |
| --- | --- |
| ID and `[start, end)` | Frame range on the production timeline |
| Idea/narration and source | One main idea; unverified parts marked |
| Layout/assets | Subject, labels, diagram and where each asset comes from |
| Picture states | In → settle → hold → accent/change → out |
| Shared cues | ID and frame for picture, voice, SFX or points to re-listen |
| Checks | Reading time, small text, asset rights and open issues |

**Done when:** every shot has a purpose and a reading order; times without audio are marked as estimates.

### 3. Build a component system and one sample shot

Choose a palette by idea group or state, a font that supports the script's language, and one outline/shadow treatment. For the isometric branch keep one consistent viewing angle; suggested components are `IsometricPlatform`, `EntityLabel`, `ClaimCard`, `SourceFooter`, `StatusStamp`, `Timeline`, `RecapBoard`. These are a proposed design, not components that already exist in the studio.

For the cartoon branch keep a character sheet for proportions, silhouette, expressions, poses and prop attachment points. Replace the platform/recap set with `CharacterRig`, `ExpressionState`, `Prop`, `BackgroundLayers`, `LightPool`, `Intertitle` and `RouteMap` where they fit. Gradient/mask layers, contact shadows and low-contrast backgrounds are a proposed way to rebuild 2D lighting; they do not prove the source used a rig or real lights. Take the hook, questions, metaphors and causal chain from the transcript with its recognition limits recorded, and separate sponsor segments from the main story.

Build one representative shot that holds props, text and states. Use SVG/shapes for fixed layouts and add 3D where space has to change. Render a still first, then a short moving version. For a long video, check the sample shot before multiplying scenes.

**Done when:** the sample shot is rendered and reviewed; text, reading direction, viewing angle and contrast work at the target viewing size.

### 4. Animate and assemble

The AI writes reusable code in `studio/src/` and keeps production data and assets in the workspace defined by the shared workflow. Reveal nodes and connectors in step with the explanation; change the state of the same prop instead of constantly replacing the whole scene. Use a recap board to return to information groups and change the palette at chapter boundaries.

The case study's roughly nine-frame stamp is one measured example. Choose entry time, scale, tilt, easing and hold for the new layout and narration; do not call it an original keyframe. Text that has settled should stay still long enough to read. A glitch is one option for marking a boundary, not a requirement for every transition.

**Done when:** shots run on the right frames, transitions keep the idea, the timeline and cues match the audio in use, and no estimated timing is presented as aligned.

### 5. Sound, render and hand-off

Mix voice, bed and SFX on the shared cues; listen for levels, masking and transition tails. The source's loudness and pause figures are reference measurements, not required targets. Onsets from audio analysis are only cue candidates.

Do the **Review, render and hand off** part of the [shared workflow](create-video.md): typecheck, still and moving previews, MP4 render, ffprobe, decode check, encoded-frame review and a listen to the mix. Fix what you observe and list the checks not done.

**Done when:** a requested MP4 exists as a real, checked file that meets the contract; the checkpoint holds the edit sources, assets, render command, results, open issues and next step. A documentation-only request ends with a document of decisions and a concrete workflow, without starting video production.

## Known limits

The case study has sample frames across the source, two VFX windows analyzed in full, one measured frame sequence of a red stamp, and ASR/audio measurements. It has no original project, no full listening pass and no complete comparison build. This is therefore a **proposed reconstruction workflow**, not a pipeline proven to reproduce the source.
