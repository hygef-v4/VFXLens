# AGENTS.md — VFX Learning Engine (Phase 1)

## 1. Mục tiêu Hệ thống
`VFX Learning Engine` là hệ thống phân tích kỹ thuật VFX và Motion Graphics chuyên nghiệp gồm hai phân hệ cốt lõi trong Phase 1:
1. **After Effects Project Analyzer (`vfx_engine.project_analyzer`)**: Đọc file `.aep` (binary RIFX/RIFF) và `.aepx` (XML) ở chế độ Offline (dựa trên `py-aep` + clean-room `.aepx` transcoder/parser) hoặc qua Read-only AE Bridge (MCP HTTP / ExtendScript `.jsx` trên bản sao tạm).
2. **Video VFX Analyzer (`vfx_engine.video_analyzer`)**: Phân tích video tốc độ cao (5–15s hoặc dài hơn) theo từng frame và timestamp gốc (`ffprobe` + OpenCV + `PySceneDetect` + Optical Flow + Multi-cue Signal Detectors + AI Vision Adapter tùy chọn).

## 2. Quy tắc An toàn & Bảo mật Dữ liệu (BẮT BUỘC)
- **Read-only tuyệt đối với dữ liệu người dùng:** Không bao giờ ghi đè, xóa, đổi tên hoặc di chuyển file `.aep`, `.aepx` hay video gốc của người dùng.
- **Mở qua After Effects:** Nếu sử dụng Live AE Bridge hoặc ExtendScript, bắt buộc copy file `.aep` sang thư mục tạm độc lập trước khi mở và đóng với `CloseOptions.DO_NOT_SAVE_CHANGES`.
- **Không thực thi mã không tin cậy:** Không bao giờ nạp hoặc thực thi binary plugin `.aex`, không tự chạy script nhúng trong project người dùng.
- **Không tự gọi dịch vụ đám mây trả phí:** Mọi bước xử lý mặc định diễn ra hoàn toàn local. `VisionAnalyzer` mặc định ở chế độ `noop` (offline) trừ khi người dùng chủ động cấu hình provider hợp lệ.
- **Phân biệt rõ trạng thái dữ liệu (`DataAvailabilityStatus`):**
  - `observed`: Đọc hoặc đo được trực tiếp từ binary/XML/frame.
  - `inferred`: Suy luận có căn cứ từ tín hiệu đo được hoặc từ heuristic.
  - `unavailable`: Không có mặt trong nguồn dữ liệu tĩnh (ví dụ giá trị sau khi chạy expression khi phân tích offline, hoặc thông số plugin từ video MP4).
  - `unsupported`: Định dạng hoặc trường dữ liệu chưa được parser hỗ trợ.
  - `error`: Lỗi xảy ra trong quá trình đọc/trích xuất.

## 3. Lệnh CLI Chính
```powershell
uv run vfx doctor
uv run vfx analyze-project "path/to/project.aep"
uv run vfx analyze-video "path/to/video.mp4"
uv run vfx analyze-folder "path/to/folder" --recursive
uv run vfx inspect "outputs/<analysis-id>"
```

## 4. Kiểm thử
```powershell
uv run pytest
```
