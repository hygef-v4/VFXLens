# Khảo sát skill và công cụ sản xuất video AI

Đây là bản khảo sát ban đầu, trước khi người dùng yêu cầu cài toàn bộ. Cấu hình sau triển khai nằm ở [hướng dẫn yêu cầu](ai-video-requirements.md) và [bản đồ toolchain](full-toolchain.md); các nhận định “chưa cài” bên dưới mô tả thời điểm khảo sát.

Ngày đối chiếu: **15/11/2026**. Phạm vi: đọc hai PDF người dùng cung cấp, đối chiếu README/tài liệu nguồn và các skill đang có; chưa cài thêm công cụ hay thử một lần sản xuất hoàn chỉnh.

## 1. Kết luận để chọn bộ công cụ

Để làm short **nhân vật 2D phẳng trong bối cảnh 3D có ánh sáng**, bộ khởi đầu hợp lý là **Codex + workflow sản xuất đang có + Blender/MCP + Remotion và skill chính thức + FFmpeg/ffprobe + giọng thu thật + Whisper**. LottieFiles motion-design bổ sung nguyên tắc chuyển động; WhisperX và earshot chỉ thêm khi nhu cầu timing và kiểm âm thực tế đòi hỏi. Đây là đề xuất kiến trúc từ tài liệu, chưa phải pipeline đã chạy thành công trên máy này.

Không cần cài cả 20 mục của PDF 2: danh sách gồm engine, thư viện, ứng dụng, mô hình và MCP; **mục Remotion Skills là bộ agent skill được định danh rõ ràng**. Một runtime có tài liệu dành cho AI hoặc có skill đi kèm ở repo khác vẫn cần phân biệt với chính runtime đó. Ví dụ Motion hiện trỏ tới skill riêng ở [motiondivision/ai-kit](https://github.com/motiondivision/ai-kit). [Nguồn Remotion Skills](https://github.com/remotion-dev/skills), [nguồn Motion](https://github.com/motiondivision/motion).

Nhận định “100% free” trong bài đăng không đủ để quyết định chi phí: Remotion có điều kiện miễn phí và giấy phép trả phí; model, asset và dịch vụ bổ sung có điều kiện riêng. Không cần một model Claude cụ thể để áp dụng workflow: README của Remotion Skills và MCP for Blender đều có hỗ trợ Codex. [Remotion license/pricing](https://www.remotion.dev/docs/license/pricing), [Remotion Skills README](https://github.com/remotion-dev/skills), [MCP for Blender README](https://github.com/ahujasid/mcp-for-blender).

## 2. Hai PDF thực sự cung cấp gì

| Tài liệu | Giá trị sử dụng | Giới hạn chứng cứ |
| --- | --- | --- |
| [PDF 1: quy trình short 2.5D](https://www.posttosource.com/files/1794716002010_2zxnvm550.pdf) | Công thức sản xuất: chuyện có nguồn, shot list, set/prop Blender, nhân vật cut-out, diễn xuất, voice, caption và vòng duyệt | Chính tác giả nói không biết pipeline thật của kênh tham chiếu. Đây là cách tái tạo ngôn ngữ hình ảnh được đề xuất, không phải chứng minh công cụ kênh đó đã dùng; chưa xác minh độc lập view count |
| [PDF 2: danh sách 20 repo](https://www.posttosource.com/files/1794716211901_qnhdqdhof.pdf) | Bản đồ các khâu animation, 3D, audio và export | Gọi chung mọi mục là “skills” làm mất khác biệt giữa hướng dẫn cho agent và phần mềm thực thi; không chứng minh chúng tích hợp sẵn hoặc đều cần thiết |

Các thông số của PDF 1 nên coi là **quyết định sáng tạo cho phiên bản mới**: 1080×1920, 30 fps, 55–70 giây, shot khoảng 1,5–3 giây theo từng ý, tái sử dụng 3–5 set, hero prop là 3D; nhân vật vẫn phẳng, có biểu cảm và bóng tiếp xúc. Mốc 150–170 từ áp dụng cho lời dẫn tiếng Anh trong ví dụ. Với tiếng Việt, cần thu thử và dùng thời lượng âm thanh thật để chốt shot. [PDF 1, trang 4–9](https://www.posttosource.com/files/1794716002010_2zxnvm550.pdf).

## 3. Phân loại đủ 20 repo trong PDF 2

Các dòng dưới đây xác nhận **vai trò qua README/tài liệu nguồn**, không xác nhận đã cài hoặc render trên Windows hiện tại. “Chọn” là khuyến nghị cho short 2.5D nêu trên.

| # | Repo / nguồn chính | Bản chất và công dụng | Chọn cho bản đầu |
| --- | --- | --- | --- |
| 01 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Engine tạo video bằng React, có composition, caption, audio và render | **Có**: ghép hình Blender, chữ và âm thanh; kiểm tra điều kiện license |
| 02 | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Bộ agent skill chính thức; router `remotion-best-practices` và hướng dẫn tạo, preview, caption, render | **Có**: hướng dẫn agent dùng engine; không thay engine |
| 03 | [juliangarnier/anime](https://github.com/juliangarnier/anime) | Thư viện JavaScript animate CSS/SVG/DOM/object, có timeline | Để sau: chỉ khi có đoạn HTML/SVG thật sự cần; không thêm để làm việc Remotion đã giải quyết |
| 04 | [motiondivision/motion](https://github.com/motiondivision/motion) | Thư viện animation JavaScript/React/Vue, gesture, spring, layout/scroll transition | Để sau: hợp UI/product demo; README có liên kết tới agent skill riêng |
| 05 | [ManimCommunity/manim](https://github.com/ManimCommunity/manim) | Engine Python cho video giải thích toán và hình học | Chỉ chọn khi nội dung có sơ đồ/công thức cần dựng; xuất clip rồi ghép |
| 06 | [airbnb/lottie-web](https://github.com/airbnb/lottie-web) | Player cho animation JSON xuất từ After Effects/Bodymovin | Chỉ khi đã có asset Lottie phù hợp; không biến mọi hiệu ứng AE thành video |
| 07 | [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender) | MCP server + Blender addon cho agent dựng/chỉnh scene, xem kết quả; dự án cộng đồng, không phải sản phẩm chính thức của Blender | **Có**: điều khiển Blender, cần kết nối addon hoạt động; không phải SKILL.md |
| 08 | [mrdoob/three.js](https://github.com/mrdoob/three.js) | Thư viện 3D JavaScript với renderer WebGL/WebGPU | Nhánh thay thế khi dựng 3D bằng code trong browser; bản đầu dùng Blender để tránh hai scene engine |
| 09 | [gkjohnson/three-gpu-pathtracer](https://github.com/gkjohnson/three-gpu-pathtracer) | Path tracing GPU cho Three.js | Để sau: README hiện cảnh báo WebGPU chưa ổn định và cần khóa phiên bản `three-mesh-bvh`; không cần khi render Blender |
| 10 | [jrouwe/JoltPhysics](https://github.com/jrouwe/JoltPhysics) | Engine mô phỏng va chạm/vật rắn, có soft body và ragdoll; thư viện lõi C++ | Để sau: chỉ khi chọn nhánh mô phỏng riêng; không phải dependency bắt buộc của cảnh Blender |
| 11 | [pmndrs/postprocessing](https://github.com/pmndrs/postprocessing) | Thư viện hậu kỳ cho Three.js, pass/effect như bloom | Để sau: cùng nhánh Three.js; không dùng trực tiếp để hậu kỳ mọi video |
| 12 | [Alchemist0823/three.quarks](https://github.com/Alchemist0823/three.quarks) | Thư viện TypeScript particle/VFX cho Three.js, có editor và tích hợp React Three Fiber | Chỉ khi có particle thực sự cần trong nhánh Three.js |
| 13 | [cocopon/tweakpane](https://github.com/cocopon/tweakpane) | Panel chỉnh tham số và theo dõi giá trị trong ứng dụng web | Để sau: công cụ debug/tinh chỉnh scene, không tạo phim hay quyết định diễn xuất |
| 14 | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Ứng dụng/engine workflow node, API cho tạo hình/video/audio và nhiều model | Tùy chọn: tạo asset khi thiếu. Chọn model theo VRAM và giấy phép; partner/cloud node có thể là dịch vụ trả phí |
| 15 | [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice) | Mô hình và runtime TTS đa ngôn ngữ | Tùy chọn nếu cần giọng tổng hợp. README hiện liệt kê 9 ngôn ngữ, **không có tiếng Việt**; chưa đủ chứng cứ khuyên dùng cho narration tiếng Việt |
| 16 | [librosa/librosa](https://github.com/librosa/librosa) | Thư viện Python xử lý tín hiệu âm thanh/âm nhạc, có phân tích onset/beat | Chỉ thêm khi dựng theo nhạc; không thay kiểm tra tiếng nói và mix bằng tai |
| 17 | [m-bain/whisperX](https://github.com/m-bain/whisperX) | ASR + forced alignment để cải thiện word timing, diarization tùy chọn | Tùy chọn nâng từ Whisper khi timing cần tốt hơn; phải kiểm tra alignment cho ngôn ngữ dùng |
| 18 | [obsproject/obs-studio](https://github.com/obsproject/obs-studio) | Ứng dụng capture/composite/record/stream | Chỉ dùng khi cần ghi màn hình hoặc footage; không cần cho render offline bằng frame |
| 19 | [mifi/lossless-cut](https://github.com/mifi/lossless-cut) | GUI FFmpeg cắt/ghép/remux nhanh, thường tránh encode lại | Tùy chọn xử lý footage; không thay timeline composition có animation/caption |
| 20 | [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | Bộ CLI/thư viện encode, filter, audio/video/subtitle; ffprobe đọc metadata | **Có**: kiểm tra file, contact sheet, mix/encode và delivery |

Với Remotion, animation phải tuân theo frame của composition để kết quả seek/render ổn định. Không tự động mang loop thời gian thực của ví dụ Anime.js, Motion, Three.js hay particle vào timeline mà chưa chuyển sang cơ chế điều khiển theo frame. Đây là khuyến nghị tích hợp; cần kiểm thử seek và render của đoạn thật. [Remotion animations](https://www.remotion.dev/docs/animating-properties).

## 4. Những repo bổ sung trong PDF 1 đáng giữ

| Nguồn | Nhận xét và quyết định |
| --- | --- |
| [LottieFiles/motion-design-skill](https://github.com/LottieFiles/motion-design-skill) | Có `skills/motion-design/SKILL.md`; hữu ích cho timing, easing, staging, choreography. Nhiều chỉ dẫn thiên về UI/micro-interaction, nên dùng bổ trợ, không lấy duration UI làm quy tắc diễn xuất nhân vật |
| [angrypenguinpng/blender-claymation-skill](https://github.com/angrypenguinpng/blender-claymation-skill) | Có skill dựng claymation qua Blender. Hợp nghiên cứu cách tổ chức hướng dẫn Blender, nhưng claymation khác nhân vật cut-out 2.5D; cần xem lại script shell trước khi áp dụng trên Windows |
| [tuzhechen2005/opus-video-skills](https://github.com/tuzhechen2005/opus-video-skills) | Các hướng painted-animation/kinetic-reel dùng cho biến thể 2D hoặc typography; không phải rig Blender 2.5D hoàn chỉnh |
| [JohnHeibel/ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) | Starter animation với p5.js/p5.brush và diễn xuất; tham khảo phong cách vẽ, không coi là agent skill hay rig 3D có sẵn |
| [Leonxlnx/earshot](https://github.com/Leonxlnx/earshot) | CLI/MCP kiểm âm và xử lý âm thanh local trên CPU; đáng thử khi agent cần nghe mix. Vẫn phải nghe bản export thật, không coi báo cáo tự động là bảo đảm chất lượng |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | Skill chính thức cho GSAP; chỉ cần khi chọn animation web/GSAP |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Framework video HTML có đường render local; một lựa chọn thay cho khâu assembly Remotion, không cần cài cả hai. Kiểm tra ranh giới tính năng local và Pro |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | Ví dụ/prompt phong cách phim bằng code; nguồn ý tưởng, không chứng minh một pipeline dựng 2.5D có thể dùng ngay |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | Danh mục khám phá skill; mở repo gốc để đánh giá từng mục. Không phải engine render hay bằng chứng chất lượng cho toàn danh sách |

## 5. Stack tối thiểu và khoảng trống skill

| Khâu | Dùng trước | Chỉ bổ sung khi cần |
| --- | --- | --- |
| Brief, nguồn sự thật, storyboard, cue và delivery | Skill local `motion-design-workflow` | Một skill điều phối 2.5D mỏng nếu sẽ làm nhiều tập |
| Bối cảnh/hero prop/nhân vật cut-out/animation | Blender + MCP for Blender + asset SVG/PNG tự thiết kế | Thư viện rig/asset sau khi thử đúng một cảnh |
| Timeline cuối, caption, âm thanh | Remotion + `remotion-best-practices` | Lottie/GSAP/Manim cho đoạn có nhu cầu riêng |
| Voice và word timing | Giọng người dùng thu + Whisper local | WhisperX nếu alignment cần tốt hơn; TTS sau khi test ngôn ngữ |
| Review và delivery | FFmpeg/ffprobe, contact sheet, xem trên điện thoại, nghe mix | earshot; librosa cho phim dựng theo beat |
| Tạo asset bằng model | Chưa bắt buộc | ComfyUI local sau khi chọn model và kiểm tra VRAM/license |

Đây là **đề xuất lựa chọn**, dựa trên vai trò của các nguồn đã liên kết ở trên. Không thêm thư viện physics, path tracer hoặc particle trước khi một shot cụ thể chứng minh nhu cầu.

Hai skill đáng bổ sung trước có nguồn phát hành rõ: Remotion Skills do nhóm Remotion duy trì (khoảng 824 nghìn lượt cài, 7,1 nghìn GitHub stars); motion-design do LottieFiles phát hành (khoảng 25,5 nghìn lượt cài, 3 nghìn stars). Đây là số gần đúng tại ngày khảo sát, không phải bảo đảm chất lượng. [Trang Remotion skill](https://skills.sh/remotion-dev/skills/remotion-best-practices), [trang LottieFiles skill](https://skills.sh/lottiefiles/motion-design-skill/motion-design).

Lệnh tham khảo để triển khai sau, chạy từ thư mục dự án video riêng; **chưa thực hiện cài đặt**:

```powershell
npx skills add remotion-dev/skills --skill remotion-best-practices
npx skills add LottieFiles/motion-design-skill --skill motion-design
```

Skill local `motion-design-workflow` trong thư mục skill người dùng hiện đã có bộ tài liệu brief/style/assets/storyboard/motion/sound/delivery và hướng dẫn dựng Remotion. Mặc định của nó là 20 giây, 1920×1080, 60 fps: khi dùng cho short trong PDF phải **ghi rõ override 1080×1920, 30 fps, 55–70 giây**. Skill local `ae-edit-recipes` phục vụ học/tái tạo edit từ AE và video phân tích; không thay khâu tạo set, rig và diễn xuất 2.5D. Đây là quan sát từ các skill local được liệt kê/đọc trong phiên.

Khoảng trống phù hợp là một `cartoon-studio` điều phối, **chỉ đề xuất, chưa tạo**. Nó nên gọi workflow và công cụ có sẵn, đồng thời chốt thêm:

- Contract set/prop/nhân vật: nhân vật phẳng, bóng tiếp xúc, biểu cảm thay thế, hướng camera và kiểm tra material/alpha/occlusion ở từng góc.
- Shot list có global frame, mốc âm thanh và mốc từ; quy ước rõ frame bắt đầu từ 0 hay 1 giữa Blender và Remotion.
- Voice thật là chuẩn thời gian, transcript được sửa và kiểm tra bằng nghe; quy tắc chuyển timestamp sang frame thống nhất.
- Dựng block → light → dress; duyệt still và preview một cảnh ngắn trước khi làm cả tập; sửa đúng phạm vi shot.
- Review bằng contact sheet, hình ở kích thước điện thoại, frame liên tiếp gần cut/hit và nghe bản mix; sản xuất phải yêu cầu **export MP4 rõ ràng** vì skill Remotion hiện ưu tiên preview nếu chưa được yêu cầu render.

Tên skill và câu gọi phải thống nhất: PDF đặt `name: cartoon-studio` nhưng kết thúc bằng `/motion-studio`. Không sao chép sự lệch tên này. [PDF 1, trang 11](https://www.posttosource.com/files/1794716002010_2zxnvm550.pdf), [Remotion router hiện tại](https://github.com/remotion-dev/skills/blob/main/skills/remotion-best-practices/SKILL.md).

## 6. Điều cần sửa khi áp dụng công thức PDF

1. **Không suy frame chính xác từ thumbnail thưa.** Trích 2 fps chỉ giúp xem tổng quan; để xác nhận cut cần đọc các frame liên tiếp và PTS gần điểm nghi ngờ. VFR không cho phép mặc định timestamp = frame_index/fps. [ffprobe documentation](https://ffmpeg.org/ffprobe.html).
2. **Word timing là kết quả ước lượng.** Whisper có tùy chọn word timestamps; WhisperX thêm forced alignment nhưng vẫn có giới hạn. Một người kể không cần bật diarization; tính năng này của WhisperX còn cần token/model theo hướng dẫn riêng. Luôn kiểm tra từ bị bỏ, số, tên riêng và điểm chuyển caption. [Whisper transcribe source](https://github.com/openai/whisper/blob/main/whisper/transcribe.py), [WhisperX README](https://github.com/m-bain/whisperX).
3. **Contact sheet không thay preview chuyển động.** `tile=8x9` chứa tối đa 72 ảnh trong một sheet; nếu episode vượt phạm vi lấy mẫu đó phải chia sheet hoặc đổi grid. Sheet không cho thấy đầy đủ mọi frame của cú va chạm, nhấp nháy hay timing âm thanh. [FFmpeg tile filter](https://ffmpeg.org/ffmpeg-filters.html#tile).
4. **Render local không có nghĩa mọi thành phần miễn phí vô điều kiện.** Xem điều kiện Remotion, giấy phép từng model/asset và chỉ bật cloud/API khi được cấu hình rõ. ComfyUI hiện có cả local lẫn partner node/cloud. [Remotion pricing](https://www.remotion.dev/docs/license/pricing), [ComfyUI README](https://github.com/Comfy-Org/ComfyUI).
5. **Học cách trình bày từ video không chứng minh pipeline gốc.** Với VFXLens, giữ `observed` cho metadata/tín hiệu đo được, `inferred` cho diễn giải, `unavailable` cho thông số không thể biết từ video; không ghi tên plugin, rig hoặc thiết lập ánh sáng chính xác nếu không có project/nguồn chứng minh. Nguồn quy định: [AGENTS.md](../AGENTS.md).

## 7. Mức sẵn sàng trong workspace và bước tiếp theo

Quan sát trong phiên: FFmpeg, ffprobe, Python, Node và uv có trong PATH. Không tìm thấy lệnh Blender/Whisper trong PATH **không chứng minh chúng chưa được cài**. Công cụ Blender MCP có trong phiên nhưng kiểm tra trạng thái trả về không kết nối được addon; vì vậy chưa thể khẳng định agent đang điều khiển được Blender. Không cài package/skill, không chạy installer tải về và không gọi cloud trả phí.

Bước thực tế tiếp theo được đề xuất: xác nhận đường dẫn Blender và kết nối addon; thêm Remotion skill nếu người dùng muốn triển khai; thử **một shot 5–10 giây** có một set, một nhân vật phẳng, một prop và một voice ngắn. Chỉ mở rộng thành tập 55–70 giây sau khi shot này chứng minh material, contact shadow, camera, caption timing và export hoạt động. Đây là tiêu chí thử nghiệm đề xuất, chưa phải kết quả đã có.

Nếu triển khai sau khảo sát, dùng thư mục sản xuất mới, bảo toàn nguyên bản `.aep`, `.aepx` và video theo AGENTS.md. Không sửa cấu hình analyzer để biến công cụ phân tích thành studio; tái sử dụng kết quả phân tích/reference như đầu vào tài liệu và review.

Chưa kiểm tra: render end-to-end, chất lượng giọng tiếng Việt, thời gian render/VRAM, tương thích addon thực tế và license của từng asset/model cụ thể. Khảo sát này xác nhận tài liệu và đề xuất lựa chọn, không cam kết chất lượng hay chi phí sản xuất.
