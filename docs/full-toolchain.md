# Video toolchain

What the repository installs, what each production route uses, and which tools stay optional. Use
[the requirements guide](ai-video-requirements.md) for setup and safety rules. Machine paths and observed checks
belong in ignored `local/setup/`; a successful install does not prove a finished-film workflow.

## Routes

Start from the [shared VFXLens skill](../skills/vfxlens/SKILL.md), then pick
[study](../workflows/study-reference.md), [create a video](../workflows/create-video.md),
the [three.js character Short](../workflows/threejs-character-short.md) or the
[AI-assisted motion-graphics explainer](../workflows/ai-assisted-motion-graphics.md).
`AGENTS.md` lists which skill to propose for each kind of request.

## Installed by the repository

| Environment | Used for | Versions from |
| --- | --- | --- |
| Analyzer and document readers | `uv run vfx ...` | `pyproject.toml` + `uv.lock` |
| Remotion studio | Composition, captions, overlays, audio mix, export; React Three Fiber scenes | `studio/package.json` + `studio/package-lock.json` |
| Whisper (CPU PyTorch) | Free local transcription and word timing | `studio/voice/pyproject.toml` + `studio/voice/uv.lock` |
| three.js Short toolkit | Scaffold, voice timing, manifest, QA for the character-Short route | `studio/tools/threejs-short/` (engine from the `claude-3d-animated-shorts` skill) |

```powershell
uv sync --locked --extra dev --extra documents
npm --prefix studio ci
npm --prefix studio run typecheck
npm --prefix studio run verify:render        # renders the SmokeTest composition
uv sync --locked --directory studio/voice      # only for local Whisper
```

## Optional, installed only when a film needs it

None of these are dependencies of the repository. Install the one a shot needs, in its own environment when its
dependencies conflict, and record what was checked in `production.md`.

| Need | Tool |
| --- | --- |
| Extra web animation, particles, path tracing, physics, Lottie | `npm --prefix studio install <package>`: animejs, gsap, motion, three.quarks, three-gpu-pathtracer, jolt-physics, lottie-web |
| Paid voice, SFX, music, forced alignment | ElevenLabs CLI and skills (`text-to-speech`, `sound-effects`, `music`, `speech-to-text`) |
| Heavier 3D scenes | Blender + [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) |
| HTML-video templates, style films | The `motion-pack` and `lemo-opuscar` plugins manage their own runtimes |
| Local image or TTS models | [ComfyUI](https://github.com/Comfy-Org/ComfyUI), [CosyVoice](https://github.com/QwenAudio/CosyVoice): separate environments and model weights; check language support first |
| Beat/onset analysis, math animation | [librosa](https://github.com/librosa/librosa), [Manim](https://github.com/ManimCommunity/manim) |

Online or paid services stay subject to the boundaries in `AGENTS.md`. Review a real production with real assets before
claiming that acting, word alignment or a complete episode is verified.
