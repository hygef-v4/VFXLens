# Internet Global Explainer — Isometric Visual Storytelling

## Source and Scope

- Classification for reuse: **motion graphics → explainer/editorial infographic → isometric/2.5D**. The proposed production route is **AI-assisted, code-driven**; original AI involvement and software remain unverified. See the [style guide](../styles/isometric-explainer.md) and [production workflow](../../workflows/ai-assisted-motion-graphics.md).
- Source identifier: `internet-global-a2ghs06am5w`; supplied Vietnamese explainer video, studied 2026-11-15. The filename contains `A2Ghs06Am5w`; no external publication or production credits were verified.
- SHA-256: `d3d7534d469ce813a39e067c9c9ef4cb326f8e61a0a8b9cdcd6b2b02e37f686f`.
- Observed stream: 1920×1080, H.264, 30 fps CFR, 22,915 frames. Video duration is 763.833333 seconds; the container/audio extends to about 763.890 seconds. Frame indices below are zero-based and timestamps are source PTS.
- Visual evidence: 154 overview samples approximately five seconds apart across the whole source; denser 0.2-second samples in four selected windows; consecutive frames 3981–4005 for a stamp entrance. Private images, transcripts and machine paths stay outside this library.
- Automated VFX analysis completed on two lossless derived windows: f1854–2003 (150 frames) and f3954–4025 (72 frames), with full coverage of each window. These are selected clips, not full-source automated coverage. Clip frame indices were mapped back to the source PTS list; extracted MKV timestamps have millisecond quantization.
- Scope: visual storytelling and reconstruction choices. Statements about incidents shown in the source are not independently fact-checked here.

## Observed Design System

| Locator | Direct observation | Reusable lesson / inference |
| --- | --- | --- |
| 0.000–15.000s, f0/f450 | An isometric room and desks lead into a phone login graphic; short white labels identify the relevant action/device. | Start with a familiar situation before widening the subject. Keep a coherent set of props and labels. |
| 50.000s, f1500 | Five previously introduced incident illustrations are arranged as a compact row of cards. | Reuse established visual tokens in a recap instead of introducing new illustrations for the same entities. |
| 60.000s, f1800; 305.000–310.000s, f9150/f9300; 450.000s, f13500 | A recurring three-column board separates different certainty/attribution categories and is populated as the explanation advances. | Give uncertain information an explicit visual state. A recap board can become a navigation system for a long explanation. |
| 63.600–64.000s, f1908/f1920 | Horizontal displacement, duplicated edges and noise interrupt the category board before the next scene. | A brief glitch can mark a structural break; this does not establish a specific plugin or procedural implementation. |
| 64.600–66.000s, f1938/f1980 | A coin/central node scene gains server nodes and connecting lines in successive samples. | Reveal a system in the order needed to explain its relationships, rather than exposing the entire diagram at once. |
| 95.000–105.000s, f2850/f3150 | Opposing attribution/response cards use a consistent split layout, strong headings and small source labels. | Separate an allegation, response and missing evidence instead of visually merging them into one assertion. |
| 132.900–133.200s, f3987–f3996 | A tilted red stamp appears oversized/cropped, then contracts to a stable visible extent below two existing cards. | A short entrance followed by a stable hold makes an editorial qualifier conspicuous without keeping the whole scene moving. |
| 213.000s, f6390; 312.200s, f9366; 455.000s, f13650 | Chapter changes combine a new dominant background palette with a familiar isometric/label system. | Use color to orient the viewer while preserving component consistency. These are visible examples, not a complete frame-exact chapter list. |
| 355.000–375.000s, f10650/f11250 | A horizontal event timeline is paired with statement cards, highlights and a later split comparison. | Use a timeline to expose chronology and disagreement, rather than adding more prose to a scene. |
| 410.000–435.000s, f12300/f13050 | A power/control-system illustration changes labels, connection states and countdown displays while keeping the same scene vocabulary. | Build a scene once, then explain state changes through a few controlled properties. |
| 565.000–575.000s, f16950/f17250 | A simplified control UI is followed by a normal/abnormal split comparison. | Make consequences visible through a before/after state. Keep reconstructed UI distinct from documentary screenshots. |
| 730.000–750.000s, f21900/f22500 | Advice is grouped into recognizable account, backup, password and device illustrations; short labels carry the action. | End with concrete actions using the same established visual language. |

The recurring appearance is **isometric illustration**, not proof of a true 3D scene. Parallel edges, outlined shapes, platform thickness and shadows are observable; Blender, After Effects, SVG, procedural code, exact fonts and original layer structures are unavailable from the MP4. The early on-screen mention of Claude Code is part of the story about a login problem, not a production credit.

## Measured Stamp Example

Consecutive frames were inspected from 132.700 through 133.500 seconds. In the lower image region, a threshold for red pixels detected the first small contribution at f3987 (132.900s). The stamp extends beyond the image boundaries in the next frames, then has a stable detected bounding box from f3996 (133.200s) through the end of the inspected interval: approximately x284–1635, y736–943 in the 1920×1080 source.

This gives an observed entrance interval of about **0.300 seconds / nine frame intervals**. The threshold is a measurement aid, affected by compression, antialiasing and opacity; it does not recover original keyframes, scale values or an easing curve. The clear hold is also visible in the later 0.2-second samples through 136.000s.

## Proposed Recreation in This Repo

For the hook, explanatory structure and narration-to-image decisions, start at [Content Writing](../content-writing/README.md); the observations above remain this reference's evidence.

Use the [AI-assisted motion-graphics production workflow](../../workflows/ai-assisted-motion-graphics.md) for the maintained scene-planning, tool-selection and delivery steps. It is a **creative reconstruction plan**, not the recovered source pipeline. This case study owns the source measurements and locators above; the workflow owns new-production decisions. A rendered comparison with the source has not been performed.

Related foundations: [timing and easing](../foundations/timing-and-easing.md), [compositing](../foundations/compositing.md), and [evidence and validation](../foundations/evidence-and-validation.md). Related assembly approach: [collage](../styles/collage.md). Treat [staggered text](../techniques/typography/staggered-text.md) as one implementation option, not a verified description of every text entrance here.

## Audio Evidence

The encoded source mix measured approximately −17.3 LUFS integrated, 2.1 LU loudness range and −3.9 dBTP true peak with FFmpeg. These describe this source, not universal delivery targets. A silence threshold of −48 dBFS for at least 250 ms found a pause at 63.295–63.646s, near the visually inspected opening chapter transition. This supports trying a short transition accent in a new production; it does not identify the original sound or establish musical synchronization. Lower RMS over the closing seconds accompanies the sparse closing images.

An existing cached small Whisper model produced a full offline Vietnamese transcript to aid navigation. No new model was downloaded. The transcript and its estimated word/segment times were not perceptually checked; technical names contain recognition errors. Private transcript/audio/logs remain outside the library.

## Limits

- Sparse overview images cannot establish every shot boundary, transition duration, camera path or text animation. Dense study was limited to selected windows; automated detector output is supporting evidence rather than proof of technique/plugin identity.
- Speech recognition, when available, is a machine-generated aid. Proper names and technical terms require correction; word timings are estimates, separate from measured video PTS.
- The encoded audio mix can be measured, but music/SFX stems and exact sound choices cannot be recovered from those measurements alone.
- No original project, editable assets, production software, plugin stack, font files or source animation curves were supplied. No reconstruction render or perceptual audio comparison was performed.

[Back to case studies](README.md)
