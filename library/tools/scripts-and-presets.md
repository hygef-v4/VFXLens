# Scripts and Presets: Dependencies and Scope of Impact

## Distinguishing Roles

- **Render plugins** generate or process pixels when the host renders a frame.
- **Scripts/panels** manipulate project structure, automate setup, or generate controllers and expressions.
- **`.ffx` presets** store effect configurations, keyframes, or expressions; they do not bundle the referenced plugins, footage, fonts, or target layers.
- **Workflow utilities** such as [FX Console](https://www.videocopilot.net/blog/2016/10/new-workflow-plug-in-fx-console-is-now-available/) accelerate effect application and snapshots rather than producing a visible look in rendered video.

## Pre-Use Inspection Checklist

1. **Check the target host:** An Adobe extension panel may target Premiere Pro rather than After Effects.
2. **Check companion dependencies:** A `.jsx` script may require external equation folders, icon assets, pseudo-effect definitions, or plugins.
3. **`.jsx` extension does not guarantee readable source:** A file may contain compiled `JSXBIN` markers or obfuscated `eval` payloads. When the payload is unreadable, mark it unverified rather than guessing its behavior or safety.
4. **For `.ffx` presets:** Inspect the stored effects/controllers, keyframes, expressions, and raw storage units; without a known composition timebase, never convert raw integer ticks directly into seconds or frames.
5. **For structure-mutating scripts:** Test only on a disposable working copy, never on original reference projects.

## Lessons from a Layer Cleanup Script

Static inspection of a Hidden Layer Cleaner 1.0.0.1 script showed that while its selection step filters out certain parent/matte/effect references when selecting disabled layers, its `Delete Selected` action deletes every currently selected layer without re-checking. Moreover, the inspected code did not parse expression strings or cross-composition references. This documents a limitation of that specific script version rather than a blanket claim about all cleanup scripts.

A disabled layer (`enabled == false`) may still serve as an expression/effect reference target or preserve pre-prerender structure. Never treat `enabled == false` as proof that a layer is safe to delete. Selecting layers and deleting layers are two distinct operations that require separate verification.

**Case Studies:** [Chal7z: FFX structure, time units, and scalar storage](../case-studies/chal7z-presets.md), [White Ferrari: disabled layers](../case-studies/white-ferrari.md). **Conventions:** [Evidence and Validation](../foundations/evidence-and-validation.md).
