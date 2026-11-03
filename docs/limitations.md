# Technical Limitations & Untested Scenarios — VFX Learning Engine (Phase 1)

Tài liệu này liệt kê trung thực và đầy đủ các giới hạn kỹ thuật của **VFX Learning Engine (Phase 1)** cùng các tính năng đã được thiết kế adapter nhưng chưa thể kiểm thử trực tiếp với phần mềm đang chạy trong phiên làm việc hiện tại.

---

## 1. Giới hạn của After Effects Project Analyzer (`project_analyzer`)

### 1.1. Offline Binary/XML Parsing (`offline_py_aep` & `offline_aepx`)
1. **Không đánh giá biểu thức (Expressions) tại thời điểm chạy**:
   - Offline parser trích xuất **đầy đủ mã nguồn** JavaScript/ExtendScript expression (ví dụ: `wiggle(8, 35)`, `time * 150`, `valueAtTime(...)`) và trạng thái bật/tắt (`expression_enabled`), nhưng **không thực thi** bộ máy JavaScript của After Effects.
   - Do đó, giá trị thực tế sau khi biểu thức được tính toán tại từng frame (`expression_evaluated_value_status`) được đánh dấu rõ là `unavailable` trong chế độ offline.
2. **Thông số nội bộ dạng Opaque Binary (`ARBITRARY_DATA` / `NO_VALUE`) của Plugin bên thứ ba**:
   - Đối với các thông số tiêu chuẩn của plugin bên thứ ba (Slider, Angle, Point 2D/3D, Color, Checkbox, Popup/Dropdown) thuộc **Sapphire (`S_*`)**, **Deep Glow**, **BCC**, **Trapcode**, **Twixtor**, After Effects lưu cấu trúc định nghĩa tham số (`LIST:parT` -> `tdmn`, `pard`, `pdnm`) và giá trị/keyframe (`LIST:tdgp` -> `cdat`, `ldat`) ngay trong file `.aep`. Offline parser đọc được đầy đủ tên, `matchName`, giá trị và keyframe của các tham số này.
   - Tuy nhiên, một số plugin lưu dữ liệu cảnh 3D hoặc đường cong tùy chỉnh dưới dạng blob nhị phân độc quyền (`PropertyControlType.UNKNOWN` / `PropertyValueType.NO_VALUE` hoặc custom `bdata`, ví dụ: cấu trúc scene 3D nội bộ của **Video Copilot Element 3D (`VIDEOCOPILOT 3DArray`)** hoặc custom curves). Các tham số này được trích xuất tên/`matchName`/keyframe timing nhưng phần payload nhị phân độc quyền được đánh dấu `unsupported` thay vì đoán mò.
3. **Giá trị mặc định của các thông số chưa chỉnh sửa trong `.aepx` fallback**:
   - Khi phân tích file `.aepx` bằng nhánh transcode XML-sang-RIFX (`aepx_transcoded_py_aep`), toàn bộ cây thuộc tính được giải mã giống hệt `.aep`.
   - Nếu một file `.aepx` bị cắt cụt hoặc chứa thẻ XML phi chuẩn buộc phải chuyển sang nhánh `offline_aepx_xml_fallback`, chỉ những chunk được lưu tường minh trong XML mới hiển thị; các trường ẩn được đánh dấu `unavailable`.
4. **Không đọc hoặc thực thi file nhị phân `.aex`**:
   - File `.aex` là thư viện liên kết động (PE/DLL) chứa mã máy của plugin trên Windows. Theo nguyên tắc an toàn, hệ thống **từ chối mở hoặc thực thi `.aex`** (`UnsafeFileError`). Hệ thống chỉ nhận diện các plugin được tham chiếu bên trong project `.aep`/`.aepx` thông qua `matchName` và bảng `PluginRegistry`.

### 1.2. After Effects Read-Only Live Bridge (`ae_bridge`)
1. **Trạng thái kiểm thử thực tế (`live_bridge_tested = false`)**:
   - Trên máy hiện tại có cài đặt **Adobe After Effects 2026** (`C:\Program Files\Adobe\Adobe After Effects 2026\Support Files\AfterFX.exe`), nhưng **After Effects không mở sẵn và chưa cài/bật CEP MCP Extension** lắng nghe trên cổng `11488` (JUNKDOGE `after-effects-mcp`) hoặc `7788` (Solomon `aftereffects-mcp`).
   - Do đó, `live_bridge_tested` được ghi nhận trung thực là `false` trong toàn bộ kết quả thực thi.
   - Hệ thống đã cung cấp đầy đủ:
     - `ae-scripts/vfx_readonly_extract.jsx`: ExtendScript hoàn toàn chỉ đọc (không gọi `app.open()`, không sửa thuộc tính, không gọi `app.project.save()`).
     - `AfterEffectsReadOnlyBridge`: HTTP/JSON-RPC adapter cho cả 2 chuẩn MCP (`11488` và `7788`) kèm danh sách từ khóa cấm (`FORBIDDEN_JSX_PATTERNS`) để chặn tuyệt đối mọi thao tác ghi/chỉnh sửa project.
     - `compare_offline_and_live()`: Bộ đối chiếu tự động giữa kết quả offline parser và live AE bridge.

---

## 2. Giới hạn của Video VFX Analyzer (`video_analyzer`)

1. **Không thể đảo ngược duy nhất (Non-invertible) từ pixel MP4/MOV sang cấu trúc After Effects**:
   - Từ một video đã render (đặc biệt sau khi nén H.264/HEVC 8-bit), **không thể xác định chắc chắn 100%** tên plugin đã dùng. Ví dụ: hiệu ứng sáng rực quanh vùng highlight có thể được tạo bởi **Deep Glow**, **Sapphire `S_Glow`**, hoặc **3 lớp `ADBE Glo2` (Built-in Glow) xếp chồng ở chế độ 32-bpc**.
   - Vì vậy, mọi sự kiện trong `video-analysis.json` đều tách bạch 4 trường độc lập:
     - `observations` (quan sát tín hiệu đo trực tiếp từ frame),
     - `possible_ae_techniques` (kỹ thuật AE khả dĩ),
     - `possible_plugins` (plugin nghi ngờ — luôn đi kèm `verified: false`),
     - `undetermined_parameters` (thông số không thể suy ra từ video).
2. **Giới hạn của Computer Vision Heuristics & Optical Flow**:
   - **Motion Blur vs. Defocus Blur**: Bộ phát hiện sử dụng độ sụt giảm phương sai Laplacian kết hợp với tính dị hướng của tensor cấu trúc (`gradient_anisotropy`) và vận tốc Optical Flow để phân biệt Directional Motion Blur với Out-of-Focus Blur đẳng hướng. Tuy nhiên, nếu cảnh quay có sẵn các sọc nền định hướng mạnh kèm defocus, độ tin cậy có thể bị ảnh hưởng.
   - **Speed Ramp vs. Chuyển động vật lý nhanh**: Optical Flow đo vận tốc biểu kiến trên mặt phẳng ảnh (px/frame). Một cú vung tay/camera thật tăng tốc đột ngột và một đoạn Time Remapping / Twixtor tạo ra trường vận tốc tương tự nhau.
   - **Kinetic Typography & Semantic Compositing**: Khi không cấu hình AI Vision (`VFX_VISION_PROVIDER=none`), bộ phát hiện chỉ tìm ra ứng viên (`kinetic_typography_candidate`) dựa trên mật độ cạnh sắc nét tương phản cao xuất hiện cục bộ; việc đọc nội dung chữ hoặc hiểu ngữ nghĩa 3D object được đánh dấu `unavailable`.
3. **AI Vision Provider (`VisionAnalyzer`)**:
   - Mặc định hệ thống chạy `NoOpVisionAnalyzer` (100% cục bộ, không gọi API trả phí, không tự bịa kết quả AI).
   - Hệ thống xuất đầy đủ `contact-sheet.jpg` và thư mục `evidence-frames/` với timestamp chính xác để sẵn sàng đưa vào model Vision khi người dùng cấu hình.
