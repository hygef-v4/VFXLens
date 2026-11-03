# VFX Learning Engine — Phase 1

Hệ thống độc lập phân tích dự án **Adobe After Effects (`.aep` / `.aepx`)** và **Video VFX (`.mp4` / `.mov` / FFmpeg)** trên Windows (tối ưu cho phần cứng có GPU NVIDIA RTX 4060 8GB và hỗ trợ hoàn chỉnh CPU fallback).

---

## 1. Tính năng cốt lõi (Phase 1)

### A. After Effects Project Analyzer (`project_analyzer`)
- **Method A — Offline Binary/XML Parser (`offline_py_aep` & `offline_aepx`)**:
  - Đọc trực tiếp file nhị phân `.aep` (RIFX/RIFF qua `py-aep`) và file XML `.aepx` (qua bộ transcode XML-sang-RIFX + XML DOM fallback) **không cần mở After Effects**.
  - Trích xuất đầy đủ:
    - Project metadata, phiên bản AE (`ae_version`), độ sâu màu (`bits_per_channel`), `working_space`, `expression_engine`.
    - Danh sách Composition & Precomposition, đồ thị phụ thuộc (`composition_hierarchy`).
    - Layer hierarchy, parenting (`parent_index`), Track Matte (`Alpha`/`Luma`), Blending Mode, 3D switch, Adjustment Layer, Collapse Transformation, Motion Blur, Time Remapping.
    - Transform, Masks (`ADBE Mask Parade`), Shapes, Text Animators (`ADBE Text Animators`), 3D Cameras & Lights.
    - **Toàn bộ chuỗi Effect Stack (`ADBE Effect Parade`) theo đúng thứ tự layer**, bao gồm cả plugin bên thứ ba (**Boris FX Sapphire `S_*`, Continuum `BCC*`, Deep Glow, Maxon Trapcode, Video Copilot Element 3D/Optical Flares, RE:Vision Twixtor/RSMB**).
    - Thông số effect (`EffectParameterSchema`), giá trị tĩnh, Keyframe timing/values, interpolation (`LINEAR`, `BEZIER`, `HOLD`), temporal/spatial easing, và mã nguồn JavaScript/ExtendScript Expressions.
    - Phát hiện missing footage (`missing_assets`) và danh mục plugin bên thứ ba (`missing_effects`).
  - **An toàn tuyệt đối**:
    - Phân biệt rõ `.aep` (binary project), `.aepx` (XML project), và `.aex` (Windows DLL binary plugin). **Từ chối mở hoặc thực thi `.aex`** (`UnsafeFileError`).
    - Kiểm tra băm `SHA-256` trước và sau khi đọc (`ReadOnlyFileGuard`) đảm bảo không bao giờ làm thay đổi project gốc.
- **Method B — After Effects Read-Only Live Bridge (`ae_bridge`)**:
  - Hỗ trợ kết nối chỉ đọc tới JUNKDOGE `after-effects-mcp` (`http://127.0.0.1:11488/mcp`) hoặc Solomon `aftereffects-mcp` (`http://127.0.0.1:7788/call`) kèm script `ae-scripts/vfx_readonly_extract.jsx`.
  - Chặn mọi lệnh ghi/lưu/chỉnh sửa project (`FORBIDDEN_JSX_PATTERNS`).
  - Nếu After Effects / MCP panel không chạy, hệ thống ghi nhận trung thực `live_bridge_tested = false` và hoạt động độc lập bằng Offline Parser.
- **Normalizer & Comparator (`normalizer`)**:
  - Chuẩn hóa đầu ra với trạng thái minh bạch: `observed`, `inferred`, `unavailable`, `unsupported`, `error`.

### B. Video VFX Analyzer (`video_analyzer`)
- Giải mã MP4, MOV và mọi định dạng FFmpeg hỗ trợ qua `ffprobe` + OpenCV, trích xuất **timestamp trình chiếu thực tế (`pts_time`)** của từng frame và tự động phát hiện **Variable Frame Rate (VFR)**.
- **Adaptive & Full-Frame Analysis**:
  - Phân tích toàn bộ frame (`full_frame_with_adaptive_windows`) cho các đoạn video VFX ngắn/nhanh (5–20 giây, kể cả 60 FPS với hiệu ứng kéo dài 0.1 giây = 6 frame), kết hợp phát hiện các cửa sổ biến động mạnh (`high_activity_windows`).
- **Bộ phát hiện tín hiệu thị giác & chuyển động**:
  - `scene_cut` (Hybrid PySceneDetect + per-frame 12x9 grid RGB change)
  - `flash_frame` (Luminance impulse & highlight saturation)
  - `camera_shake` (High-frequency global optical flow velocity sign reversals)
  - `zoom_punch_transition` (Radial optical flow expansion/contraction)
  - `speed_ramp` (Intra-scene optical flow velocity dynamic envelope)
  - `motion_blur` (Structure-tensor gradient anisotropy + Laplacian sharpness drop)
  - `rgb_split_chromatic_aberration` (Phase correlation R-G / R-B spatial edge offset + chromatic fringe)
  - `glow_bloom` (Annular highlight halo luminance excess)
  - `distortion_displacement` (Non-affine optical flow residual + horizontal scanline tear)
  - `motion_trail_echo` (Lagged edge residual correlation)
  - `masking_reveal` (Progressive partial-grid boundary wipe)
  - `particles_overlay` (Morphological Top-Hat moving high-contrast speckles)
  - `kinetic_typography_candidate` & `camera_3d_parallax`
- **Tách biệt nhận thức luận (Epistemic Separation)**:
  - Phân biệt rõ: `observations` (đo trực tiếp từ frame), `possible_ae_techniques` (kỹ thuật AE khả dĩ), `possible_plugins` (plugin nghi ngờ — `verified: false`, không bao giờ khẳng định chắc chắn tên plugin chỉ từ MP4), và `undetermined_parameters`.

---

## 2. Cài đặt trên Windows

### Yêu cầu hệ thống
- Windows 10/11 (64-bit)
- Python >= 3.11 (đã kiểm thử trên Python 3.14)
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg & FFprobe trong `PATH`

### Các bước cài đặt
```powershell
# 1. Di chuyển vào thư mục dự án
cd F:\code\git\VFXLens

# 2. Khởi tạo môi trường ảo và cài đặt dependencies
uv sync --extra dev

# 3. Kiểm tra môi trường (Python, FFmpeg, GPU RTX 4060, After Effects, Packages)
uv run vfx doctor
```

---

## 3. Hướng dẫn sử dụng CLI (`vfx`)

### 3.1. Kiểm tra chẩn đoán hệ thống
```powershell
uv run vfx doctor
uv run vfx doctor --json
```

### 3.2. Phân tích file project After Effects (`.aep` / `.aepx`)
```powershell
uv run vfx analyze-project "path/to/project.aep" --output outputs/run1
```
Kết quả sinh ra trong `outputs/run1/`:
- `project-analysis.json`: Dữ liệu JSON chuẩn hóa theo schema `ProjectAnalysisResult`.
- `project-report.md`: Báo cáo Markdown chi tiết từng Composition, Layer, Effect Stack, Keyframes, Expressions và Missing Assets.

### 3.3. Phân tích Video VFX (`.mp4` / `.mov`)
```powershell
uv run vfx analyze-video "path/to/video.mp4" --output outputs/run2
```
Kết quả sinh ra trong `outputs/run2/`:
- `video-analysis.json`: Dữ liệu JSON chuẩn hóa theo schema `VideoAnalysisResult`.
- `timeline.json`: Chuỗi tín hiệu đo đạc theo từng frame/timestamp gốc (`FrameSignalEntry`).
- `video-report.md`: Báo cáo Markdown phân tích cảnh, sự kiện VFX, kỹ thuật AE khả dĩ và plugin nghi ngờ.
- `contact-sheet.jpg`: Bảng ảnh tổng hợp các frame tiêu biểu có đánh dấu sự kiện.
- `evidence-frames/`: Thư mục chứa các frame bằng chứng (`frame_00030_1.000s.jpg`, ...).

### 3.4. Phân tích hàng loạt theo thư mục
```powershell
uv run vfx analyze-folder "path/to/folder" --recursive --output outputs/batch1
```
Tự động phân tích toàn bộ `.aep`, `.aepx`, và video trong thư mục, đồng thời tự động bỏ qua an toàn các file `.aex` binary plugin và xuất `batch-summary.json`.

### 3.5. Xem nhanh kết quả phân tích trên Terminal
```powershell
uv run vfx inspect "outputs/run1/project-analysis.json"
uv run vfx inspect "outputs/run2/video-analysis.json"
```

---

## 4. Chạy bộ kiểm thử (Tests)

```powershell
uv run pytest -v
```

---

## 5. Tài liệu chi tiết
- Nghiên cứu & đánh giá 9 GitHub repositories: [`docs/repository-research.md`](docs/repository-research.md)
- Giới hạn kỹ thuật & các kịch bản chưa kiểm thử live: [`docs/limitations.md`](docs/limitations.md)
- Quy tắc dành cho AI Agent: [`AGENTS.md`](AGENTS.md)
