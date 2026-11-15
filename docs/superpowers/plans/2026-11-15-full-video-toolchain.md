# Complete video toolchain installation

User authorization: install all remaining tools/libraries/skills from the two supplied PDFs, superseding the earlier minimal-install selection.

Keep the existing analyzer, studio and original media intact. Pin compatible versions, separate conflicting Python environments, preserve installed applications and verify each executable/library rather than equating a clone with installation. Do not activate paid services or download every possible model checkpoint.

## Tasks

- [x] Install and verify JavaScript animation, Three.js effects/particles, physics and vector runtimes in the studio.
- [x] Install additional creative skills and standalone HTML/p5 toolkits from PDF 1, preserving existing skills.
- [x] Install Manim/librosa/WhisperX and official earshot with isolated dependencies and functional checks.
- [x] Install ComfyUI and CosyVoice source/dependencies with startup/import checks and explicit model availability.
- [x] Reuse/install OBS and LosslessCut, and build/test native Jolt when the available compiler permits.
- [x] Update requirements/workflow routing and record all versions, sources, checks and remaining limitations.

## Environment decisions

- Existing root and studio environments stay in place.
- New heavy source checkouts/environments use `E:/VFXLensTools` (about 190 GB initially free), with local junctions where needed; F initially has about 18 GB free.
- Machine-specific paths and observed installation state stay in ignored `local/setup/` files.
- JS, Python, AI-app and desktop/native tasks have disjoint writable paths.
