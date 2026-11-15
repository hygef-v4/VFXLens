# Full video toolchain

The full profile was requested after the initial minimal setup. It installs the tools named in the two supplied PDFs, with separate environments where their dependencies conflict. A tool's role can remain optional for a particular film even when that tool is installed.

Use [the requirements guide](ai-video-requirements.md) for the source repository list, safety rules and core setup. Current machine paths, observed checks and model availability are recorded in ignored `local/setup/` JSON files; installation and a successful import do not establish finished-film quality.

## Quy trình đầu-cuối

Nhánh **AI-assisted motion graphics → explainer** có [workflow sản xuất riêng](../workflows/ai-assisted-motion-graphics.md), với hai hướng [isometric/2.5D](../library/styles/isometric-explainer.md) và [cartoon 2D có nhân vật](../library/styles/cartoon-explainer.md). Các style guide liên kết tới case study và bằng chứng tương ứng.

Theo [skill VFXLens dùng chung](../skills/vfxlens/SKILL.md), rồi chọn nhánh [nghiên cứu](../workflows/study-reference.md) hoặc [sản xuất](../workflows/create-video.md):

1. **Nghiên cứu:** kiểm tra tư liệu video/AE, ghi bằng chứng và giới hạn; tra bài học phù hợp trong thư viện.
2. **Lên kế hoạch:** ghi brief, storyboard, mốc frame, tài sản, cue âm thanh và quyết định còn mở vào checkpoint tiếng Việt.
3. **Dựng:** chuẩn bị tài sản được phép dùng trong thư mục sản xuất riêng; dùng Remotion cho đồ họa chuyển động và lắp dựng, thêm Blender/3D khi cảnh cần.
4. **Hoàn thiện:** xử lý lời thoại, phụ đề và âm thanh từ bản thu thật hoặc ghi rõ phần ước tính; render, xem frame/điểm chuyển cảnh, nghe bản mix và kiểm tra thông số tệp.
5. **Bàn giao:** cập nhật checkpoint với đường dẫn nguồn, lệnh render, kết quả đã kiểm tra, vấn đề còn lại và bước tiếp theo. Nếu yêu cầu MP4, bàn giao tệp đã kiểm tra hoặc nêu blocker cụ thể.

Repo có **25 skill upstream**: 2 skill Remotion/motion design, 14 skill creative toolkit và 9 skill HyperFrames. Skill `skills/vfxlens/` của repo là entrypoint riêng để định tuyến theo yêu cầu. Nguồn khóa skill là `studio/skills-lock.json`, `studio/tools/creative/skills-lock.json` cùng `manual-skills.json`, và `studio/tools/hyperframes/skills-lock.json`; lockfile ghi nguồn/revision khi upstream hỗ trợ. [Thư viện dùng lại](../library/README.md) gồm foundations, techniques, styles, resources, tools, case studies và templates.

| Nhóm skill | Các skill đã cài |
| --- | --- |
| Studio (2) | `remotion-best-practices`, `motion-design` |
| GSAP (8) | `gsap-core`, `gsap-frameworks`, `gsap-performance`, `gsap-plugins`, `gsap-react`, `gsap-scrolltrigger`, `gsap-timeline`, `gsap-utils` |
| Creative khác (6) | `blender-claymation`, `painted-animation`, `kinetic-reel`, `earshot`, `real-sound`, `lemo-opuscar` |
| HyperFrames (9) | `figma`, `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `remotion-to-hyperframes`, `reverse-any-video`, `slideshow`, `style-sampling` |

Đọc skill theo công việc được chọn; hướng dẫn upstream về dịch vụ online hoặc trả phí vẫn phải tuân theo các ranh giới trong `AGENTS.md`.

Phiên bản phụ thuộc lấy từ manifest và lockfile được theo dõi trong repo, không lấy từ hồ sơ cài đặt máy:

| Môi trường | Nguồn phiên bản |
| --- | --- |
| Analyzer and document readers | `pyproject.toml` + `uv.lock` |
| Main Remotion studio | `studio/package.json` + `studio/package-lock.json` |
| Voice / Whisper | `studio/voice/pyproject.toml` + `studio/voice/uv.lock` |
| Manim, librosa, WhisperX, earshot | `studio/tools/analysis/pyproject.toml` + `studio/tools/analysis/uv.lock` |
| HyperFrames | `studio/tools/hyperframes/package.json` + `studio/tools/hyperframes/package-lock.json` |
| Lemo | `studio/tools/lemo/pyproject.toml` + `studio/tools/lemo/uv.lock` |
| ComfyUI, CosyVoice | Each tool's `requirements.in` is the reviewed input; `requirements.lock` is the frozen install set. Source commit pins and setup steps are in each linked tool guide. |

Hồ sơ status bị ignore ghi nhận smoke check cho `vfx doctor`, typecheck, thư viện studio, render Remotion, ảnh Three.js/painted animation, Blender và import công cụ. Kiểm tra lại bằng `uv run pytest`, `uv run vfx doctor`, `npm --prefix studio run typecheck`, `npm --prefix studio run verify:libraries` và các lệnh smoke ở phần dưới; xem `local/setup/full-toolchain-status.json` cùng status lân cận để biết bằng chứng cụ thể. Chưa tải model weights hoặc gọi dịch vụ trả phí. Chất lượng nhận dạng/căn chỉnh lời thoại, một tập phim hoàn chỉnh, skill hiện trong giao diện mới của cả hai agent và nghe kiểm tra bản mix vẫn chưa được xác minh.

## Runtime and instruction locations

| Work | Runtime / source | Instructions |
| --- | --- | --- |
| Analysis and PDF reading | Root `pyproject.toml`, `uv.lock` | [Shared VFXLens skill](../skills/vfxlens/SKILL.md) |
| Remotion, Three.js, particles, post effects, Anime.js, Motion, Lottie, GSAP, Jolt WASM, p5 | `studio/package.json`, `package-lock.json` | `studio/.agents/skills/remotion-best-practices/`, `motion-design/` |
| Manim, librosa, WhisperX, official earshot | `studio/tools/analysis/pyproject.toml`, `uv.lock` | [Analysis tools](../studio/tools/analysis/README.md) |
| Whisper | `studio/voice/pyproject.toml`, `uv.lock` | Requirements guide voice section |
| ComfyUI | `studio/tools/comfyui/`, reviewed source in `references/ComfyUI` | [ComfyUI setup](../studio/tools/comfyui/README.md) |
| CosyVoice | `studio/tools/cosyvoice/`, reviewed source in `references/CosyVoice` | [CosyVoice setup](../studio/tools/cosyvoice/README.md) |
| HTML video / HyperFrames | `studio/tools/hyperframes/package.json`, `package-lock.json` | `studio/tools/hyperframes/.agents/skills/hyperframes/` |
| GSAP, claymation, painted animation, kinetic reels, earshot, Lemo styles | `studio/tools/creative/.agents/skills/` | [Creative toolkit notes](../studio/tools/creative/README.md) |
| Lemo core, voice and music libraries | `studio/tools/lemo/pyproject.toml`, `uv.lock`, `references/lemo-opuscar` | [Lemo notes](../studio/tools/lemo/README.md) |
| Painted p5 starter | `references/ClaudeAnimationBase` and its npm environment | Source `ANIMATION_GUIDE.md` |
| Native Jolt, OBS, LosslessCut and CMake | System/portable installations outside the repo | Observed versions, archive hashes and commands in `local/setup/desktop-native-status.json` |
| More skill discovery | `references/awesome-claude-video-skills` | A catalogue, not another 180 runtimes to install |

Project-scoped upstream skills have linked Claude copies next to their canonical `.agents/skills/` directories. Read the branch actually needed by the requested production; loading every toolkit at once adds conflicting defaults. Root `vfxlens` remains the common entrypoint for both agents.

## Install and check the locked packages

From the repo root:

```powershell
$env:PYTHONUTF8 = '1'
uv sync --locked --extra dev --extra documents
npm --prefix studio ci
npm --prefix studio run verify:libraries
npm --prefix studio run typecheck
npm --prefix studio run prepare:smoke
npm --prefix studio run still -- ThreeCheck ../local/setup/three-smoke.png --frame=15

uv sync --locked --directory studio/voice
uv sync --locked --directory studio/tools/analysis
# Windows: set VFXLENS_FFMPEG_SHARED_BIN first, following the analysis tools README.
uv run --directory studio/tools/analysis python verify.py
npm --prefix studio/tools/hyperframes ci
npm --prefix studio/tools/hyperframes run hyperframes -- --version
uv sync --locked --directory studio/tools/lemo
```

Existing `.venv` junctions place heavy packages on the selected tools drive. A fresh checkout has no such links: either create a virtual environment at the desired location and link it into the corresponding project first, or allow uv to create a local environment. Do not replace an existing environment or junction blindly.

The analysis environment needs a compatible shared FFmpeg build for TorchCodec on Windows. This is separate from the existing FFmpeg command-line executable; follow [its setup notes](../studio/tools/analysis/README.md) and use the documented WhisperX launcher so the DLL search path applies to actual work as well as verification.

`VFXLENS_TOOLS_ROOT` identifies the selected external tools directory in new terminals. ComfyUI and CosyVoice have their own source pins and frozen requirements; use their linked setup guides rather than mixing their PyTorch versions into the analyzer or voice environment. Source checkouts and model caches stay outside tracked source.

## What still needs a production input

- ComfyUI requires a chosen generation checkpoint and workflow. No collection of all possible checkpoints is part of a library install.
- CosyVoice requires compatible model weights and a supported language; the inspected upstream language list does not establish Vietnamese support.
- Whisper/WhisperX require speech/aligner weights and an actual recording to verify transcription/timestamps. Diarization models may have separate access conditions.
- earshot's DSP/synthesis tools can run offline; semantic audio-model features require their own cached model.
- Manim geometry and Pango text do not require TeX. Formula rendering needs a separate TeX installation.
- Lemo's optional online TTS and HyperFrames Pro instructions do not authorize network generation or paid calls. Select local branches under the repo's rules.

Review a concrete production with real assets before claiming that character acting, word alignment, a full path-traced scene or an entire 2.5D episode is verified.
