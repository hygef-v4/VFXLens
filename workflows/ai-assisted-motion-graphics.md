# Làm explainer bằng AI-assisted motion graphics

Đọc sau [workflow sản xuất chung](create-video.md) khi yêu cầu là motion graphics có AI hỗ trợ, explainer bằng sơ đồ, isometric/2.5D hoặc cartoon có nhân vật. Đây là workflow để tạo một video mới; chưa phải một lệnh tự động sinh trọn video.

## Phân loại và phạm vi

**Motion graphics/animation → explainer → chọn nhánh hình ảnh phù hợp.** Phương pháp sản xuất đề xuất: **AI-assisted, code-driven**. AI viết kịch bản, chuẩn bị dữ liệu cảnh/asset, lập trình chuyển động, chạy render và kiểm tra kết quả. Chọn từng khả năng theo công cụ và đầu vào thực tế.

| Nhánh | Đặc trưng và tài liệu |
| --- | --- |
| Isometric/2.5D infographic | [Style guide](../library/styles/isometric-explainer.md), [case Internet Global](../library/case-studies/internet-global-explainer.md): đạo cụ không gian, diagram, thẻ nguồn/trạng thái và recap |
| Cartoon 2D có nhân vật | [Style guide](../library/styles/cartoon-explainer.md), [case Nvidia Chips](../library/case-studies/nvidia-chips-cartoon-explainer.md): biểu cảm, đạo cụ dẫn chuyện, bối cảnh phân lớp, ánh sáng cục bộ và đối thoại/câu hỏi |

Ghi cách sản xuất từng loại tài sản: shape/SVG viết bằng code, cảnh 3D dựng bằng code, ảnh AI sinh, giọng tổng hợp hoặc tư liệu nguồn. “Có AI hỗ trợ” không tự chứng minh mọi tài sản của video tham chiếu do AI sinh ra. Công cụ gốc và mức độ dùng AI của nguồn vẫn chưa xác minh.

Các đặc trưng và tiêu chí hình ảnh nằm ở style guide tương ứng; bằng chứng và mốc đo nằm ở case study. Những lựa chọn cho video mới được ghi là quyết định sáng tạo.

## Bộ công cụ theo nhiệm vụ

| Việc | Lựa chọn trong project | Điều cần xác nhận |
| --- | --- | --- |
| Brief, kịch bản, shot list, code, kiểm tra | Claude/Codex qua skill VFXLens | Dùng chung checkpoint sản xuất; kiểm chứng các phát biểu cần nguồn |
| Nhãn, thẻ thông tin, UI, timeline, stamp, lắp dựng | Remotion + React + SVG | Animation phụ thuộc frame; đọc skill Remotion của studio |
| Minh họa isometric góc cố định | SVG/shape nhiều lớp; Three.js/R3F khi cần hình học 3D | Chọn cách đơn giản đáp ứng shot; chữ ưu tiên lớp 2D dễ đọc |
| Camera, che khuất hoặc ánh sáng 3D | Three.js qua `@remotion/three`, hoặc Blender + MCP | Kiểm tra shot thật; giữ nguyên scene người dùng đang làm |
| Giọng đọc tiếng Việt | Bản thu được cung cấp; `edge-tts` đã cài là một nhánh tổng hợp online | Online cần được cho phép; kiểm tra giọng khả dụng và phát âm trước khi làm dài |
| ASR/phụ đề/cue lời | Whisper/faster-whisper; WhisperX khi cần căn chỉnh | Có model phù hợp; sửa chữ/tên riêng và kiểm nghe mốc thời gian |
| Âm nhấn và phối âm | earshot + FFmpeg; librosa hỗ trợ đo tín hiệu | Nghe xác nhận cue, không coi onset lời nói là beat nhạc |
| Xuất và kiểm tra tệp | Remotion + FFmpeg/ffprobe | Đúng contract hình/âm thanh và không có lỗi giải mã |

Tra [toolchain](../docs/full-toolchain.md) và hướng dẫn từng môi trường trước khi chạy. ComfyUI, CosyVoice và Kokoro là các nhánh bổ sung; việc cài package không đồng nghĩa đã có model, giọng Việt hoặc chất lượng phù hợp. Không phát sinh cloud call, tải model lớn hay thay dependency chỉ vì tài liệu nhắc tới chúng.

## Các bước thực hiện

### 1. Chốt contract và lập luận

Tra [Content Writing](../library/content-writing/README.md) để chọn hook, cấu trúc giải thích và cách chuyển lời dẫn thành ý hình; áp dụng vào kịch bản của production hiện tại.

Tạo hoặc cập nhật một `local/productions/<slug>/production.md` theo workflow chung. Ghi thông điệp, người xem, thời lượng, kích thước/fps, composition ID, nguồn, nơi xuất và những đầu vào còn thiếu. Thông số 1920×1080, 30 fps của case study là dữ liệu tham chiếu; chỉ dùng cho video mới khi được chọn rõ.

Chọn cấu trúc theo câu hỏi video và bài học trong Content Writing; các nhánh kể theo vật thể hoặc phân loại bằng chứng có thể cần dàn ý khác nhau. Với mỗi phát biểu, lưu nguồn và trạng thái quan sát/suy luận/chưa biết. Ảnh minh họa không đóng vai bằng chứng tư liệu thật.

**Xong khi:** contract rõ và mỗi ý chính có nguồn/trạng thái hoặc được ghi là thiếu dữ liệu.

### 2. Chuẩn bị lời và storyboard theo cue

Nếu có lời dẫn, chuẩn bị bản thu hoặc thử một đoạn TTS ngắn được phép dùng trước. Đo bản audio thực rồi đặt cue hình; nếu chưa có audio, ghi thời gian là ước tính và giữ việc căn chỉnh cuối ở trạng thái chưa xong.

Mỗi shot trong checkpoint có các trường:

| Trường | Nội dung |
| --- | --- |
| ID và `[start, end)` | Mốc frame trên timeline sản xuất |
| Ý/lời dẫn và nguồn | Một ý chính, phần chưa xác minh ghi rõ |
| Bố cục/asset | Chủ thể, nhãn, diagram và nơi lấy tài sản |
| Trạng thái hình | Vào → hạ xuống/ổn định → giữ → nhấn/thay đổi → ra |
| Cue chung | ID và frame cho hình, lời, SFX hoặc điểm cần nghe lại |
| Kiểm tra | Thời gian đọc, chữ nhỏ, quyền asset và vấn đề còn mở |

**Xong khi:** mỗi shot có mục đích và thứ tự đọc; các mốc chưa có audio được đánh dấu ước tính.

### 3. Dựng một hệ component và một shot mẫu

Chọn palette theo nhóm ý/trạng thái, font hỗ trợ tiếng Việt và cách vẽ viền/bóng. Với nhánh isometric, giữ góc nhìn nhất quán; bộ component gợi ý gồm `IsometricPlatform`, `EntityLabel`, `ClaimCard`, `SourceFooter`, `StatusStamp`, `Timeline`, `RecapBoard`. Đây là thiết kế đề xuất, chưa phải các component đã triển khai sẵn trong studio.

Với nhánh cartoon, giữ một character sheet về tỷ lệ, silhouette, biểu cảm, pose và điểm gắn đạo cụ. Thay bộ đế/recap bằng các vai trò `CharacterRig`, `ExpressionState`, `Prop`, `BackgroundLayers`, `LightPool`, `Intertitle`, `RouteMap` khi phù hợp. Các lớp gradient/mask, bóng tiếp xúc và nền ít tương phản là cách tái dựng ánh sáng 2D đề xuất; chưa chứng minh source dùng rig hoặc ánh sáng thật. Lấy hook, câu hỏi, ẩn dụ và chuỗi nhân quả từ transcript đã ghi giới hạn nhận dạng; tách đoạn quảng bá khỏi mạch nội dung chính.

Dựng một shot đại diện đủ chứa đạo cụ, chữ và trạng thái. Dùng SVG/shape cho bố cục cố định; thêm 3D ở nơi cần thay đổi không gian. Render still trước, rồi bản chuyển động ngắn. Với video dài, kiểm tra shot mẫu trước khi nhân rộng scene.

**Xong khi:** shot mẫu đã render và được xem; chữ, hướng đọc, góc nhìn và tương phản hoạt động ở kích thước xem mục tiêu.

### 4. Triển khai chuyển động và ghép cảnh

AI viết code tái dùng trong `studio/src/`, dữ liệu/tài sản riêng theo workspace trong workflow chung. Reveal node/đường nối theo lời giải thích; đổi trạng thái của cùng đạo cụ thay vì liên tục đổi toàn cảnh. Dùng bảng recap để quay lại các nhóm thông tin và đổi palette ở ranh giới chương.

Mốc stamp khoảng chín frame trong case study chỉ là ví dụ đã đo. Chọn thời gian vào, scale, góc nghiêng, easing và khoảng giữ cho bố cục/lời mới; không gọi đó là keyframe gốc. Chữ đã hạ xuống nên giữ ổn định đủ lâu để đọc. Glitch là một lựa chọn nhấn ranh giới, không phải yêu cầu cho mọi lần chuyển cảnh.

**Xong khi:** các shot chạy đúng frame, chuyển cảnh giữ được ý, timeline/cue khớp bản audio đang dùng và không còn timing ước tính bị trình bày như đã căn chỉnh.

### 5. Âm thanh, render và bàn giao

Phối lời, nền và SFX theo cue chung; nghe lại mức âm, chỗ bị che và đuôi chuyển cảnh. Thông số loudness/khoảng nghỉ của nguồn là số đo tham khảo, không phải target bắt buộc. Onset từ phân tích âm thanh chỉ là ứng viên cue.

Thực hiện phần **Review, render and hand off** trong [workflow chung](create-video.md): typecheck, still/moving preview, render MP4, ffprobe, kiểm tra giải mã, xem frame đã encode và nghe mix. Sửa lỗi quan sát được, ghi riêng các kiểm tra chưa làm.

**Xong khi:** yêu cầu xuất MP4 có tệp thực, đúng contract và kết quả kiểm tra; checkpoint chứa nguồn chỉnh sửa, asset, lệnh render, kết quả, vấn đề còn lại và bước tiếp theo. Yêu cầu chỉ viết tài liệu kết thúc ở tài liệu có quyết định và workflow cụ thể, không tự mở rộng sang sản xuất video.

## Giới hạn đã biết

Case study đã có ảnh mẫu xuyên suốt nguồn, hai cửa sổ VFX được phân tích đầy đủ, một chuỗi frame đo dấu đỏ và ASR/audio measurement. Chưa có project gốc, kiểm nghe toàn bộ hoặc bản dựng so sánh hoàn chỉnh. Vì vậy đây là **workflow tái dựng đề xuất**, chưa phải pipeline đã chứng minh tạo được bản sao của nguồn.
