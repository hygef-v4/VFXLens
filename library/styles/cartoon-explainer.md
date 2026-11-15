# Character-Led 2D Cartoon Explainer

## Classification and Indicators

**Character animation / motion graphics → narrative explainer → 2D cartoon or cutout staging.** AI assistance describes a proposed production method, separately from this visual style and any source's unverified production claims.

Recognizable character silhouettes, expression/pose changes, expressive props, layered locations and brief text/diagram inserts carry the story. Local light pools, cool/warm separation and foreground/background treatment create emphasis. Depth can be simulated in 2D; source pixels alone do not establish a true 3D renderer.

## Proposed Assembly Workflow

Use the shared [AI-assisted motion-graphics production workflow](../../workflows/ai-assisted-motion-graphics.md), with these branch choices:

1. Extract the source transcript over the selected study interval. Identify the hook, questions, reversals, concrete metaphor and object/character that connects scenes. Keep a narrative summary separate from raw ASR and source factual claims.
2. Create a small character sheet: proportions, silhouette, expression states, pose range and prop attachments. Plan narration and dialogue as separate roles; test any authorized synthesized voices before locking shot durations.
3. Build a layered rig and reusable scene components. For example: character, expression state, prop, background layers, local light pool, handwritten intertitle and map/route. These are proposed component roles, not prebuilt studio assets.
4. Animate from frame-driven pose/state changes: eye/mouth expression, hand/prop movement, entrance, emphasis and readable hold. A talking character need not move every part continuously; lip synchronization requires its own audio/viseme evidence and testing.
5. Stage one representative shot. Check character/prop overlap, feet/contact shadow, focal contrast and motion against actual speech. SVG/Canvas/Remotion can handle 2D rigs; add Three.js/Blender only where spatial behavior justifies it.
6. Use character scenes for motivation/action, diagrams for mechanisms/scale and text for short pivots. Preserve the same narrative object across these representation changes.
7. Finish through the shared render, encoded-frame and audio-review steps. Treat source measurements as examples, not a preset for the new video.

## Pitfalls and Checks

- Preserve character proportions and identities across poses and camera sizes. Keep hand/prop and mouth/face layers coherent.
- Tie the brightest area to the current story focus; shadows, blur and vignette must preserve text and expressions.
- Check progressively revealed text at real playback speed. Sparse images with partial text do not prove a useful reading duration.
- Mark promotional segments separately from editorial content. An embedded product pitch is source testimony, not independent verification of its claims.
- Validate named people, numbers and allegations before using a source's script as factual material. Keep private transcripts and media outside the public library.

## Verification and Sources

The [Nvidia Chips case study](../case-studies/nvidia-chips-cartoon-explainer.md) contains first-ten-minute image locators, selected dense filmstrips and ASR-based narrative analysis. The guide is **proposed and not recreation-render verified**. Original production tools, rigs, fonts and per-layer animation parameters remain unavailable.

Related: [timing and easing](../foundations/timing-and-easing.md), [compositing](../foundations/compositing.md), [fonts](../resources/fonts.md), and the separate [isometric explainer style](isometric-explainer.md).

[Back to styles](README.md)
