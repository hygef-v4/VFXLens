# Báo cáo Nghiên cứu & Đánh giá GitHub Repositories (`docs/repository-research.md`)

Tài liệu này tổng hợp kết quả kiểm tra thực tế, phân tích mã nguồn, kiến trúc, giấy phép (license), khả năng tương thích Windows và mức độ hoàn thiện của 9 repository tham khảo đã được clone vào thư mục `references/` (thư mục này được đưa vào `.gitignore` để không trộn lẫn vào source chính).

---

## 1. Bảng Tổng hợp Trạng thái & Chỉ số Repository

| Repository | Phân nhóm | Trạng thái | Ngôn ngữ chính | Stars / Forks | Commits / Contributors (kiểm tra thực tế) | License | Tương thích Windows | Quyết định sử dụng |
|---|---|---|---|---|---|---|---|---|
| [`forticheprod/py-aep`](https://github.com/forticheprod/py-aep) | AEP Parsing | Hoạt động tích cực (cập nhật 11/2026) | Python | 81 ⭐ / 14 🍴 | >50 commits gần nhất / 7+ contributors (Fortiche Production) | **MIT** (có file `LICENSE` đầy đủ) | **Tốt** (OS Independent, pure Python + `struct`, `attrs`, `fonttools`, `uharfbuzz`) | **CHỌN LÀM CORE PACKAGE** (`py-aep` qua PyPI/dependency) cho Offline `.aep` Parser |
| [`ChenxingM/AEP-Tools`](https://github.com/ChenxingM/AEP-Tools) | AEP Parsing | Hoạt động (cập nhật 09/2026) | Python + Rust (`PyO3`/`maturin`) | 7 ⭐ / 0 🍴 | ~50 commits / 1 contributor | Khai báo `license = "MIT"` trong `pyproject.toml` nhưng **thiếu file `LICENSE` gốc** | Trung bình (cần Rust toolchain & `maturin` để build `_core`, có pure-Python fallback) | **KHÔNG SAO CHÉP CODE** (do thiếu file `LICENSE` tường minh); chỉ tham khảo tài liệu đặc tả RIFX/AEPX để tự viết clean-room `.aepx` parser |
| [`boltframe/aftereffects-aep-parser`](https://github.com/boltframe/aftereffects-aep-parser) | AEP Parsing | Ngừng cập nhật (từ 02/2022) | Go + Kaitai Struct | 131 ⭐ / 13 🍴 | 22 commits / 3 contributors | **MIT** (có file `LICENSE`) | Chạy được qua Go runtime | **BỎ QUA TÍCH HỢP TRỰC TIẾP** (viết bằng Go, độ phủ chunk thấp hơn nhiều so với `py-aep`) |
| [`JUNKDOGE-JOE/after-effects-mcp`](https://github.com/JUNKDOGE-JOE/after-effects-mcp) | After Effects MCP | Hoạt động tích cực (v0.11.1, 10/2026) | JS / ExtendScript (`.jsx`) / C++ AEGP | 90 ⭐ / 8 🍴 | 59+ commits / 4 contributors | **MIT** (có file `LICENSE`) | **Tốt** (hỗ trợ Windows x64 + CEP + HTTP `:11488/mcp` + Named Pipe) | **CHỌN HỖ TRỢ ADAPTER** trong `ae_bridge` (kết nối Read-only qua HTTP `:11488/mcp` và học hỏi cơ chế `readonly-worker.jsx` mở bản sao snapshot) |
| [`solomondivyananth/aftereffects-mcp`](https://github.com/solomondivyananth/aftereffects-mcp) | After Effects MCP | Hoạt động (10/2026) | Node.js / ExtendScript (`bridge.jsx`) | 81 ⭐ / 9 🍴 | 19 commits / 1 contributor | **MIT** (có file `LICENSE`) | **Tốt** (CEP panel lắng nghe HTTP `127.0.0.1:7788`, dùng token tại `~/.ae-mcp-bridge.json`) | **CHỌN HỖ TRỢ ADAPTER** trong `ae_bridge` (hỗ trợ giao thức HTTP `:7788/call` Read-only và tham khảo kỹ thuật spill-file JSON trong ExtendScript ES3) |
| [`Breakthrough/PySceneDetect`](https://github.com/Breakthrough/PySceneDetect) | Video Analysis | Rất trưởng thành (v0.7.2, 11/2026) | Python | 5,326 ⭐ / 552 🍴 | >95 commits gần nhất / 18+ contributors | **BSD-3-Clause** (có file `LICENSE`) | **Rất tốt** (hỗ trợ Windows đầy đủ với OpenCV/PyAV + FFmpeg) | **CHỌN LÀM PACKAGE DEPENDENCY** (`scenedetect`) kết hợp với bộ phân tích tín hiệu multi-cue riêng |
| [`pouyashahrdami/mimic-mcp`](https://github.com/pouyashahrdami/mimic-mcp) | Video Analysis | Hoạt động (08/2026) | TypeScript (Node.js + Remotion) | 30 ⭐ / 0 🍴 | 73 commits / 1 contributor | **MIT** (có file `LICENSE`) | Một phần (phần OCR và TTS phụ thuộc macOS Vision/`say`, phần toán học phân tích chạy đa nền tảng) | **THAM KHẢO THUẬT TOÁN** (Adaptive MAD threshold `median + k*MAD`, grid-cell change area để phân biệt full-frame cut vs dissolve vs localized overlay) |
| [`moshspro-dev/video-effect-reel`](https://github.com/moshspro-dev/video-effect-reel) | Video Analysis | Mới (10/2026) | Python | 1 ⭐ / 0 🍴 | 5 commits / 1 contributor | **MIT** (có file `LICENSE`) | Một phần (sử dụng `fcntl` của POSIX và `setup.sh`, dùng fallback `fcntl = None` trên Windows) | **THAM KHẢO CẤU TRÚC CATALOG & CONTACT SHEET** (tổ chức evidence frames, contact sheet grid có gắn timestamp/frame label) |
| [`docsforadobe/after-effects-scripting-guide`](https://github.com/docsforadobe/after-effects-scripting-guide) | Reference Docs | Hoạt động (cập nhật AE 26.5, 09/2026) | Markdown (MkDocs) | 185 ⭐ / 41 🍴 | 93+ commits / 15+ contributors | Tài liệu cộng đồng (Copyright Adobe Systems Inc., mục đích giáo dục/tra cứu) | Độc lập nền tảng (tài liệu) | **DÙNG LÀM TÀI LIỆU TRA CỨU CHÍNH THỨC** cho ExtendScript DOM, Match Names (`ADBE ...`), `KeyframeInterpolationType`, `TrackMatteType`, `BlendingMode` |

---

## 2. Phân tích Chi tiết từng Nhóm Repository

### 2.1. Nhóm AEP Parsing

#### A. `forticheprod/py-aep`
- **Kiến trúc & Source:**
  - Được phát triển bởi studio hoạt hình **Fortiche Production** (tác giả Aurore Delaunay).
  - Tổ chức thành các phân hệ rõ ràng trong `src/py_aep/`:
    - `binary/`: Giải mã cấu trúc container `RIFX` / `RIFF` (`Egg!`), các chunk `Fold`, `Item`, `Layr`, `tdgp`, `tdbs`, `cdat`, `ldat`, `lhd3`, `sspc`, `parT`, `pard`, `btdk`.
    - `parsers/`: Parser chuyên biệt cho `application`, `project`, `composition`, `layer`, `property`, `effect`, `text`, `mask`, `marker`, `essential_graphics`, `render_queue`.
    - `models/`: Mô hình hóa đối tượng sát với ExtendScript API (`Application`, `Project`, `CompItem`, `AVLayer`, `TextLayer`, `ShapeLayer`, `CameraLayer`, `LightLayer`, `PropertyGroup`, `Property`, `Keyframe`).
    - `synthesis/` & `resolvers/`: Tự động tổng hợp (synthesize) các thuộc tính mặc định mà After Effects lược bỏ khỏi file binary khi chưa chỉnh sửa, đồng thời hợp nhất (merge) định nghĩa tham số `parT`/`pard` của cả built-in effect lẫn **third-party plugin** (ví dụ Sapphire `S_BlurDirectional`, `S_Shake`, Deep Glow...).
  - Có bộ script kiểm chứng đối chiếu trực tiếp với After Effects (`scripts/jsx/export_project_json.jsx`) và hàng trăm file `.aep` mẫu từ AE 2018 đến AE 2026 trong `samples/`.
- **Dependencies:** `attrs>=21.3.0`, `PyYAML>=5.1`, `fonttools>=4.38`, `uharfbuzz>=0.39`. Tương thích chính thức tới Python 3.14.
- **Giới hạn kỹ thuật (Limitations):**
  - Không hỗ trợ đánh giá biểu thức (expression evaluation) tại runtime: khi `expression_enabled == True`, `Property.value` trả về giá trị tĩnh/keyframe lưu trong binary trước khi chạy expression (tuy nhiên chuỗi `Property.expression` vẫn đọc được đầy đủ).
  - `Property.expression_error` luôn rỗng khi đọc offline vì AE tính toán lỗi expression lúc runtime.
  - Các thuộc tính thuần runtime (`Application.effects`, `Application.fonts`, `memoryInUse`, trạng thái cửa sổ) không nằm trong file `.aep`.
  - Chỉ đọc trực tiếp định dạng binary `.aep` (`RIFX`/`RIFF`), chưa có hàm đọc trực tiếp `.aepx` (XML).

#### B. `ChenxingM/AEP-Tools`
- **Kiến trúc & Source:**
  - Gồm phần lõi Rust (`rust/lib.rs` dùng `PyO3`) để tăng tốc tách chunk RIFF và phần Python (`python/aep_parser/` và `python/aep_tools/`) để dựng model + GUI PySide6.
  - Điểm đáng chú ý là tài liệu `docs/aep-format.md` mô tả chi tiết cấu trúc byte của `idta`, `cdta`, `ldta`, `tdb4`, `cdat`, `lhd3`, `ldat`, `EfDf`, `parT`, `mkif`, `shph`, `btdk` và cách ánh xạ giữa `.aep` (binary) với `.aepx` (XML).
- **Giới hạn & Lý do không tích hợp code:**
  - Đang ở giai đoạn Alpha (`0.1.0a1`), yêu cầu biên dịch Rust bằng `maturin`.
  - Độ chính xác khi tái tạo property tree, spatial tangents, text animators và third-party effect parameters thấp hơn `py-aep`.
  - **Quan trọng về mặt pháp lý:** Repo khai báo `license = "MIT"` trong `pyproject.toml` nhưng không có file `LICENSE` trong kho mã nguồn. Tuân thủ nghiêm ngặt quy tắc an toàn bản quyền, chúng ta **không sao chép bất kỳ dòng code nào** từ `AEP-Tools`, mà tự xây dựng parser `.aepx` (clean-room implementation) dựa trên định dạng XML/RIFX chuẩn của After Effects.

#### C. `boltframe/aftereffects-aep-parser`
- **Kiến trúc & Source:**
  - Thư viện viết bằng Go (`project.go`, `item.go`, `layer.go`, `property.go`) kèm định nghĩa Kaitai Struct trong README.
- **Giới hạn:**
  - Ngừng phát triển từ tháng 02/2022.
  - Chỉ đọc được một phần rất cơ bản của `idta`, `cdta`, `ldta`, `tdgp`; không giải mã đầy đủ keyframe spatial/temporal ease, text layer COS, shape paths hay cấu trúc `parT` phức tạp của plugin bên thứ ba.

---

### 2.2. Nhóm After Effects MCP & Automation Bridge

#### D. `JUNKDOGE-JOE/after-effects-mcp`
- **Kiến trúc & Source:**
  - Gồm CEP Extension (`plugin/`), Node host lắng nghe Streamable HTTP tại `http://127.0.0.1:11488/mcp`, stdio shim (`clients/ae-mcp-jkdg`) và plugin native AEGP (`native/`).
  - Cung cấp 16 MCP tools (`ae_status`, `ae_read`, `ae_exec`, `ae_previewFrame`, `ae_validateExpressions`, `ae_instances`...).
  - Điểm kiến trúc xuất sắc nhất: **`plugin/jsx/readonly-worker.jsx`** — khi cần đọc/preview mà không ảnh hưởng project gốc của người dùng, hệ thống chỉ mở một bản sao (`snapshot.aep`) trong thư mục tạm riêng biệt, kiểm tra `project.file.fsName`, tắt hộp thoại modal và đóng với `CloseOptions.DO_NOT_SAVE_CHANGES`.
- **Giới hạn:**
  - Đòi hỏi người dùng cài đặt ZXP CEP extension và mở panel `Window > Extensions > ae-mcp` bên trong After Effects đang chạy.

#### E. `solomondivyananth/aftereffects-mcp` (AE MCP Bridge)
- **Kiến trúc & Source:**
  - Kiến trúc gọn nhẹ, zero npm dependencies: `mcp/ae-mcp.js` giao tiếp qua HTTP `127.0.0.1:7788/call` (xác thực bằng header `X-AE-Bridge-Token` đọc từ `~/.ae-mcp-bridge.json`) tới CEP panel chạy `panel/jsx/bridge.jsx` (hơn 3,100 dòng ExtendScript ES3).
  - Xử lý rất tốt các vấn đề thực tế của ExtendScript ES3:
    - Tự cài đặt polyfill `JSON.stringify` / `JSON.parse` vì ExtendScript không có sẵn đối tượng `JSON` chuẩn.
    - Bọc lệnh bằng `app.beginSuppressDialogs()` / `app.endSuppressDialogs(false)` để tránh treo AE khi project thiếu font hoặc thiếu plugin.
    - Cơ chế **Spill File**: khi payload JSON lớn hơn 100 KB, ghi ra file tạm UTF-8 trong `Folder.temp` thay vì trả chuỗi lớn qua `evalScript`.
    - Kiểm tra PNG hoàn chỉnh bằng cách xác nhận chunk `IEND` ở cuối file sau khi gọi `saveFrameToPng`.
- **Giới hạn:**
  - Cũng yêu cầu mở CEP panel `AE MCP Bridge` trong After Effects để dùng qua cổng HTTP `:7788`.

---

### 2.3. Nhóm Video Analysis

#### F. `Breakthrough/PySceneDetect`
- **Kiến trúc & Source:**
  - Thư viện chuẩn công nghiệp trong Python để phát hiện chuyển cảnh (`ContentDetector`, `AdaptiveDetector`, `ThresholdDetector`, `FlashDetector`/`HistogramDetector`).
  - Hỗ trợ cả backend OpenCV (`VideoStreamCv2`) và PyAV, quản lý timecode chính xác theo frame (`FrameTimecode`).
- **Giới hạn đối với Video VFX nhanh (5–15 giây):**
  - Cấu hình mặc định của `ContentDetector` (`threshold=27.0`, `min_scene_len=15`) được thiết kế cho phim dài nên sẽ bỏ sót các flash frame 1–3 frames hoặc các đoạn cắt dồn dập (micro-cuts) mỗi 4–8 frames trong video VFX/Edit ngắn.
  - Do đó, trong `VFX Learning Engine`, chúng ta kết hợp `PySceneDetect` (với `min_scene_len` nhỏ và `AdaptiveDetector` / `ContentDetector`) **cùng với** bộ phân tích tín hiệu từng frame (per-frame timestamped signal analyzer) của riêng chúng ta.

#### G. `pouyashahrdami/mimic-mcp`
- **Kiến trúc & Source:**
  - MCP server viết bằng TypeScript phục vụ phân tích video reel mẫu và dựng lại bằng Remotion.
  - File `src/analysis.ts` chứa nhiều thuật toán thị giác máy tính gọn nhẹ và hiệu quả:
    - Tính độ biến thiên theo kênh màu lớn nhất (`max(|R1-R2|, |G1-G2|, |B1-B2|)`) thay vì chỉ dùng độ chói (luminance), giúp bắt được cả các cú cắt đổi màu có cùng độ sáng.
    - Chia khung hình thành lưới ô (`cols x rows`, ví dụ `12 x 9`) để tính tỷ lệ diện tích thay đổi (`area`): nếu `area` lớn và sụp đổ ngay ở frame kế tiếp thì là **hard cut**; nếu duy trì trên một cửa sổ thời gian thì là **fade/dissolve**; nếu chỉ thay đổi cục bộ (`area < 0.5`) thì là **overlay / text / graphic reveal**.
    - Ngưỡng thích nghi (Adaptive threshold) dựa trên trung vị và độ lệch tuyệt đối trung vị: `max(floor, median + k * MAD)`.
    - Ước lượng chuyển động trong cảnh (pan/zoom) và độ rung (camera shake) từ vector chuyển dịch giữa các frame liên tiếp.
- **Giới hạn:**
  - Viết bằng TypeScript/Node.js, hướng tới dựng reel mạng xã hội bằng Remotion hơn là phân tích chuyên sâu kỹ thuật VFX của After Effects (RGB split, glow/bloom, optical flow speed ramp, radial blur, distortion, particles).

#### H. `moshspro-dev/video-effect-reel`
- **Kiến trúc & Source:**
  - Cung cấp thư viện 123 công thức hiệu ứng (`library/effects.json`) và script `reel_effects.py` tạo contact sheet gắn nhãn thời gian bằng FFmpeg + Pillow.
- **Giới hạn:**
  - Không có bộ detector Computer Vision tự động mà phụ thuộc hoàn toàn vào việc gọi CLI `claude` đọc ảnh contact sheet.
  - Dùng thư viện `fcntl` của POSIX (trên Windows phải fallback `fcntl = None`).

---

### 2.4. Nhóm Reference Documentation

#### I. `docsforadobe/after-effects-scripting-guide`
- Cung cấp tài liệu chuẩn xác cho:
  - Hệ thống phân cấp đối tượng: `app.project` -> `items` (`CompItem`, `FootageItem`, `FolderItem`) -> `layers` (`AVLayer`, `TextLayer`, `ShapeLayer`, `CameraLayer`, `LightLayer`) -> `PropertyGroup` / `Property`.
  - Danh sách **Match Names** (`docs/matchnames/`):
    - Layer Transform (`ADBE Transform Group`, `ADBE Anchor Point`, `ADBE Position`, `ADBE Position_0/1/2`, `ADBE Scale`, `ADBE Orientation`, `ADBE Rotate X/Y/Z`, `ADBE Opacity`).
    - Effects (`ADBE Effect Parade`), Masks (`ADBE Mask Parade`, `ADBE Mask Atom`, `ADBE Mask Shape`, `ADBE Mask Feather`, `ADBE Mask Opacity`, `ADBE Mask Offset`).
    - Text (`ADBE Text Properties`, `ADBE Text Document`, `ADBE Text Animators`, `ADBE Text Animator`, `ADBE Text Selectors`, `ADBE Text Animator Properties`).
    - Shapes (`ADBE Root Vectors Group`, `ADBE Vector Group`, `ADBE Vector Shape - Rect/Ellipse/Star/Group`, `ADBE Vector Filter - Trim/Repeater/...`).
    - 3D Layer, Camera (`ADBE Camera Options Group`), Light (`ADBE Light Options Group`), Material Options (`ADBE Material Options Group`), Time Remapping (`ADBE Time Remapping`), Layer Styles (`ADBE Layer Styles`).

---

## 3. Quyết định Lựa chọn Công nghệ cho `VFX Learning Engine` (Phase 1)

Dựa trên kết quả nghiên cứu thực nghiệm và cấu hình phần cứng mục tiêu (**Windows, NVIDIA GeForce RTX 4060 8GB, Python, FFmpeg 8.1.1, Adobe After Effects 2026**):

1. **Quản lý package & Môi trường:**
   - Sử dụng `pyproject.toml` chuẩn PEP 621 với `uv` / `pip`.
   - Sử dụng **Pydantic v2** (`pydantic>=2.0`) cho toàn bộ data schemas, đảm bảo kiểm kiểu nghiêm ngặt và phân biệt rõ nguồn dữ liệu (`observed`, `inferred`, `unavailable`, `unsupported`, `error`).
   - Sử dụng **Typer** + **Rich** cho CLI (`vfx`) thân thiện, log có cấu trúc rõ ràng.

2. **Module A — After Effects Project Analyzer (`vfx_engine.project_analyzer`):**
   - **Method A (Offline Project Parsing):**
     - Tích hợp package **`py-aep`** (MIT License) làm động cơ chính để phân tích file `.aep` binary. `py-aep` đọc được đầy đủ compositions, precompositions, layer hierarchy, parenting, track matte, blending mode, transforms, masks, shapes, text animators, cameras, lights, **toàn bộ effect stack và tham số của cả plugin bên thứ ba** (nhờ giải mã `parT`/`pard` và `tdgp`), keyframes (giá trị, timing, interpolation, temporal/spatial easing, roving), expressions, time remapping, motion blur, adjustment layers và missing footage/dependencies.
     - Tự triển khai module **Clean-room `.aepx` Parser & Transcoder** (`parsers/aepx_parser.py`): đọc trực tiếp cấu trúc XML `.aepx`, có khả năng chuyển đổi lossless cây XML `.aepx` sang bộ nhớ đệm `RIFX` để tận dụng toàn bộ pipeline giải mã sâu của `py-aep`, đồng thời có fallback XML parser trực tiếp nếu file `.aepx` bị cắt cụt hoặc không chuẩn.
     - Tự triển khai bộ **Third-Party Plugin & Missing Dependency Classifier** (`effect_extractor/`): nhận diện họ plugin (Sapphire `S_*`, Boris FX Continuum `BCC*`, Deep Glow, Trapcode `tc*`/`Particular`/`Form`/`Mir`/`Tao`/`Shine`/`Starglow`, Video Copilot `VIDEOCOPILOT*`/`Element`/`Optical Flares`/`Saber`, RE:Vision `Twixtor*`/`RSMB*`, Red Giant Universe `uni.*`, Rowbyte `Plexus*`, Frischluft, Plugin Everything, v.v.) từ `matchName` và `EfdG` definitions mà **tuyệt đối không thực thi `.aex`**.
   - **Method B (After Effects Read-only Bridge):**
     - Thiết kế `ae_bridge/` hỗ trợ 3 chế độ kết nối **Read-only** an toàn (luôn làm việc trên bản sao tạm thời hoặc chế độ chỉ đọc, không bao giờ ghi đè project gốc):
       1. **JUNKDOGE `ae-mcp` HTTP Adapter** (`http://127.0.0.1:11488/mcp` — công cụ `ae_status`, `ae_read`, `ae_exec`, `ae_previewFrame`).
       2. **Solomon `aftereffects-mcp` HTTP Adapter** (`http://127.0.0.1:7788/call` — xác thực token `~/.ae-mcp-bridge.json`).
       3. **Standalone ExtendScript Read-only Exporter (`ae-scripts/vfx_readonly_extract.jsx`)**: script ES3 độc lập có đầy đủ JSON polyfill, `beginSuppressDialogs()`, đọc toàn bộ cây project/composition/layer/effect/keyframe/expression từ bản sao `.aep` và ghi kết quả ra file JSON.
   - **Normalizer & Comparator (`normalizer/`):**
     - Đưa dữ liệu từ Offline Parser và Live AE Bridge về cùng một Pydantic Schema (`ProjectAnalysisResult`), tự động đối chiếu (`compare_offline_and_live`) để chỉ ra trường nào khớp (`matched`), trường nào chỉ có trên Live AE (`only_in_live`), hoặc khác biệt giá trị (`value_mismatch`, ví dụ `Property.value` khi có expression đang bật).

3. **Module B — Video VFX Analyzer (`vfx_engine.video_analyzer`):**
   - **Decoder & Exact Timestamps (`decoder/`):**
     - Kết hợp **`ffprobe`** (lấy thông tin stream, codec, audio, VFR/CFR và bảng `pkt_pts_time` thực tế của từng frame) và **OpenCV (`cv2.VideoCapture`)** / FFmpeg pipe. Không bao giờ giả định `timestamp = frame_index / fps` đối với video Variable Frame Rate (VFR).
   - **Scene & Flash Detection (`scene_detection/`):**
     - Kết hợp **`PySceneDetect`** (`ContentDetector`, `AdaptiveDetector`) với bộ phân tích **Per-Frame Multi-Channel Change & Grid Area** (lấy cảm hứng từ thuật toán MAD threshold + cell grid của `mimic-mcp`) để bắt chính xác:
       - Hard cuts (kể cả trong video cắt cực nhanh 5–15s).
       - Flash frames (1–5 frames chớp trắng/đen/màu độ chói cao rồi trở lại bình thường).
       - Dissolve / Fade transitions.
       - Localized overlays / Mask reveals / Text pop-ins (thay đổi cục bộ trên một phần diện tích khung hình).
   - **Motion & Optical Flow Analysis (`motion_analysis/`):**
     - Sử dụng **Dense Optical Flow (Farneback)** và **Affine/RANSAC Global Motion Estimation** (`cv2.estimateAffinePartial2D` trên Lucas-Kanade keypoints hoặc grid flow) để tách biệt:
       - **Camera Shake / Impact Shake:** biến thiên tần số cao, đổi dấu liên tục của vector dịch chuyển toàn cục $(dx, dy)$ và góc xoay $d\theta$ trong khoảng thời gian ngắn.
       - **Zoom / Punch-in / Pull-out Transitions:** hệ số divergence (scale factor $s(t)$) tăng/giảm đột biến với đỉnh vận tốc cao.
       - **Speed Ramp / Time Remapping:** biến thiên phi tuyến mạnh (gia tốc/giảm tốc đột ngột) của độ lớn optical flow toàn cảnh giữa các đoạn liên tiếp trong cùng một shot.
       - **3D Camera Motion & Parallax:** sự phân tầng độ lớn vector optical flow theo chiều sâu (foreground vs background flow variance khi camera tịnh tiến).
   - **Visual Effect Signal Detectors (`effect_detection/`):**
     - Đo lường trực tiếp các tín hiệu thị giác có thể kiểm chứng:
       - **RGB Split / Chromatic Aberration:** độ lệch tương quan chéo (cross-correlation shift) và sai khác biên Sobel giữa hai kênh R–B và R–G ở vùng biên độ tương phản cao.
       - **Glow / Bloom:** tỷ lệ vùng sáng bão hòa (highlight saturation ratio) kết hợp với độ lan tỏa hào quang tần số thấp (Gaussian halo energy) quanh vùng sáng.
       - **Motion Blur / Directional Blur:** sự suy giảm năng lượng tần số cao (Laplacian variance drop) đi kèm tính định hướng mạnh của phổ gradient (anisotropy của Sobel gradient tensor) đồng pha với đỉnh vận tốc chuyển động.
       - **Distortion / Displacement / Glitch:** biến dạng cục bộ phi tuyến của trường optical flow (curl/vorticity và high spatial residual so với mô hình affine toàn cục) hoặc dịch chuyển ngang theo dải scanline (block/row tearing).
       - **Motion Trails / Echo:** tương quan cao giữa phần dư khung hình hiện tại $|\Delta I_t|$ với biên của các khung hình trước đó $I_{t-1}, I_{t-2}, \dots$.
       - **Particles / High-frequency Emitters & Kinetic Typography / Masking Candidates:** phát hiện các cụm điểm sáng chuyển động độc lập hoặc vùng biên sắc nét xuất hiện cục bộ, đánh dấu rõ phần nào là tín hiệu đo được (`observed` / `inferred`) và phần nào cần xác nhận ngữ nghĩa qua `VisionAnalyzer`.
   - **Adaptive Frame Sampler & Contact Sheet Generator:**
     - Tự động lấy mẫu toàn bộ frame (full-frame analysis) đối với các đoạn ngắn 5–15 giây và trích xuất dày đặc các frame bằng chứng (`evidence-frames/`) tại các đỉnh sự kiện kèm `contact-sheet.jpg` có đóng dấu `Frame #` và `Timestamp (s)`.

4. **Module C — AI Vision Adapter (`vfx_engine.vision`):**
   - Giao diện trừu tượng `VisionAnalyzer` với các triển khai:
     - `NoOpVisionAnalyzer` (mặc định khi chưa cấu hình API key hoặc chạy offline: giữ nguyên kết quả CV, đánh dấu nhận định ngữ nghĩa nâng cao là `unavailable`, tuyệt đối không bịa kết quả AI và không gọi mạng).
     - `OpenAICompatibleVisionAnalyzer` / `GeminiVisionAnalyzer` (chỉ kích hoạt khi người dùng chủ động cấu hình biến môi trường và truyền cờ `--enable-vision`, hỗ trợ cả local Ollama/LM Studio trên RTX 4060 8GB).
