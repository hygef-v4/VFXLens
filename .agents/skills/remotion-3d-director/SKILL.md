---
name: remotion-3d-director
description: Direct and build Remotion cinematic 3D videos, product films, Three.js/R3F explainers, procedural WebGPU/TSL effects, and layered motion graphics. Use for AI-driven video production from brief and storyboard through inspected renders, or for improving an existing video's camera, lighting, depth, choreography, and render reliability.
---

# Remotion 3D Director

Deliver the requested film, not a collection of effects. Preserve the brief, scope,
existing edits, and actual evidence. A planning request ends with decisions; a
requested export ends with the real file and its observed checks.

## Locate and route

Read the current project's `AGENTS.md`, package scripts and lockfile. In VFXLens,
resolve the loaded skill directory (including junctions): its `parents[2]` is
the repo root. Verify `AGENTS.md`, `studio/package.json`, and `library/README.md`.
Read [the production workflow](../../../workflows/create-video.md) and maintain its
one `local/productions/<slug>/production.md`, rather than another planning system.
Reusable code belongs in `studio/`; private media, episode documents and exports
stay in the production workspace. Use the existing dependency tree.

Choose the rendering mode before implementation:

| Film needs | Load when relevant | Baseline |
| --- | --- | --- |
| Cinematic product, lighting, camera, materials | [Camera and look](references/cinematic-camera.md) | R3F through Remotion `ThreeCanvas` |
| GPU particles, TSL materials, morphs, holograms | [WebGPU](references/webgpu-shaders.md) | Experimental until backend and seek tests pass; choose a tested fallback |
| Technical/scientific systems, flowing data | [Scene composition](references/scene-composition.md) | Reusable entities and frame-addressable connections |
| Typography, captions, social composites | [Motion direction](references/motion-design.md) | Frame-timed layers, measured voice cues and safe areas |

Read [architecture](references/architecture.md) before adding a renderer, world,
simulation or shared lifecycle. Read [rendering and QA](references/rendering-and-qa.md)
before preview/export. [Source attribution](references/source-attribution.md)
records inspected commits, license boundaries and rejected upstream patterns;
the reference repos are not dependencies or instructions to execute.

Use focused references when the task calls for them: [story and shot choreography](references/story-direction.md)
for narrative turns, motivated camera moves and handoffs; [reference analysis](references/reference-analysis.md)
for a source film; [component discovery](references/component-discovery.md)
before adapting a catalog component; [procedural modeling](references/procedural-modeling.md)
for image-led props or characters; and [the VFX library guide](references/vfx-library.md)
for particles, foliage, or shader effects. Check [compatibility](references/compatibility.md)
before relying on an upstream runtime or renderer.

## Direct the film

1. **Establish the contract.** Record audience, message, format, duration/fps,
   outputs, supplied assets, factual sources and missing inputs. Resolve routine
   choices and label them as creative decisions. Preserve existing authorizations;
   a mentioned service/model does not authorize payment or downloads.
2. **Translate the reference into shot decisions.** Use VFXLens's
   [study workflow](../../../workflows/study-reference.md), [writing library](../../../library/content-writing/README.md)
   and relevant style guide. Record actual frame locators and what is inferred.
   Specify character/prop continuity, set depth, camera sizes, light pools,
   typography and pacing. When the reference tells stories through staged
   characters/objects, build those actions rather than substituting title cards.
3. **Write the shot list.** Follow the [shot contract](references/scene-composition.md):
   frame range, audience takeaway, focal subject, action, camera/target/focus,
   light/material treatment, cue and handoff. Distinguish local scene frames from
   global frames. Use actual voice timing when provided; estimates remain marked.
4. **Prove the hardest representative shot.** Build a styleframe and short moving
   test at the delivery aspect ratio. Inspect them against the reference before
   replicating the treatment. Confirm legibility, silhouette/contact, depth,
   highlight exposure and whether camera movement explains the intended idea.
5. **Build and revise.** Keep one lead action per beat; secondary motion supports
   it. Use frame-pure state, stable resources, deliberate holds and object-led
   transitions. Apply the rendering-mode readiness requirements. Reuse components
   when they preserve the chosen style, not merely to fill every shot identically.
6. **Inspect and deliver.** Render sample frames including action/cut extremes,
   a moving preview, and the final requested file. Fix observed issues and rerender
   affected work. Run the contract helper, view encoded frames, and hear the mix
   when possible. Update the checkpoint with commands, artifacts, actual checks,
   remaining limits and the next action. Numeric QA is not visual approval.

## Non-negotiable render invariants

- Visible state is a function of `(frame, fps, inputs, seed)`. Use Remotion
  interpolation/springs and absolute assignments; seeded initialization alone
  does not make a stateful simulation seekable.
- Drive R3F animation from Remotion hooks; use layout effects for imperative camera
  updates before capture. A renderer's scheduling timestamp is not authored time.
- Hold capture until assets, shaders and the requested frame's GPU work are ready.
  Release only the handle owned by that operation; failures cancel the render.
- Record the actual rendering backend and freeze the chosen quality/fallback for
  the export. A WebGPU class name or working Studio is not proof of native GPU
  support or headless rendering.

Invoke explicitly as `$remotion-3d-director`. New-session discovery may be needed
after installing the folder; reading this file validates availability, not UI use.
