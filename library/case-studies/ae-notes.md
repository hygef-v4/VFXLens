# AE Notes — kỹ thuật theo dạng edit

Tổng hợp từ `evidence:ae-notes-01`, đọc ngày 2026-11-04, bổ sung cho [sổ tay chính](../README.md). Nguồn là ghi chú và ảnh minh họa của người dùng; không phải project có keyframe đã được parser đo hoặc công thức đã render kiểm chứng.

## Nguồn và cách tra

- SHA-256 DOCX: `09fb93d63e664d97d895e976595cd1934bd0ed697e12ed5a02dec5b78fc7b16c`.
- Đã trích 472 đoạn trực tiếp trong body, 105 ảnh PNG, không có bảng Word; có 32 đoạn chứa link YouTube. Đã đọc chữ, xem cả năm bảng ảnh và mở riêng bảy ảnh thông số/impact để đọc rõ; chưa xem video tutorial.
- `P...` dưới đây là số đoạn trong bản trích, **không phải số trang Word**. Bản trích nguyên văn, image relationship và ảnh nằm ở `evidence:ae-notes-02`.
- `extracted-text.txt` giữ nội dung và vị trí ảnh; `extracted-notes.json` giữ các relation/hyperlink; thư mục `media/` giữ đủ 105 ảnh. Năm `image-index-*.jpg` chỉ để tra nhanh, không thay thế ảnh gốc khi đọc số.
- Một số mũi tên/dấu tiếng Anh trong nguồn đã là ký tự lỗi `[ký tự lỗi trong nguồn]`; không tự khôi phục thành lệnh hoặc thông số chắc chắn. Giữ file DOCX nguyên trạng.
- Phân biệt: **nguồn ghi** là nội dung tài liệu; **đọc từ ảnh** là screenshot tĩnh; **suy luận/đề xuất thử** chưa được chạy trên clip. Chưa thực thi expression nhúng hoặc cài/chạy plugin.

## 1. Giả độ dày bằng xếp nhiều lớp 3D

**Nguồn P2–6.** Expression Position cộng offset X/Y theo `index` và Slider `x - offset`, `y - offset`; Z được tạo từ `index + index*z_offset/10`. Nó tham chiếu cứng `comp("Comp 1").layer("Shape Layer 2 controller")`.

**Bài học:** xếp nhiều bản layer 3D với khoảng cách điều khiển chung để gợi độ dày; đây không phải biến ảnh 2D thành mesh 3D có geometry/bề mặt thật.

**Trước khi dùng:** phải có đúng controller/effect names, xác định dùng layer switch 3D thay vì hiểu thành yêu cầu import model 3D. Công thức Z trong nguồn không cộng Z gốc. Dùng `index` tuyệt đối khiến việc chèn layer hoặc thay thứ tự thay đổi hình; khi dựng mới cần chủ động chọn chỉ số tương đối và giữ vị trí nền mong muốn. Chưa kiểm chứng với AE.

## 2. Chữ cosine tắt dần và overshoot theo vận tốc

### Chữ trễ từng ký tự

**Nguồn P9–22.** Expression Selector: delay `.05`, freq `2`, amplitude `100`, decay `8`; offset theo `textIndex`, hàm `cos(2π*freq*t)/exp(decay*t)`, trả `[s,s]` khi t không âm, trước đó trả `value`.

**Đối chiếu:** cùng cấu trúc preset [Chal7z smooth text](chal7z-presets.md#3-chữ-smooth-trễ-theo-giây-dao-động-cosine-tắt-dần) nhưng amplitude trong Notes là **100**, preset là **80**. Không hợp nhất thành một giá trị “chuẩn”. Phải mang cả selector và animator properties; hai phần tử trả về chưa chứng minh phù hợp mọi property ba chiều.

### Overshoot từ vận tốc keyframe

**Nguồn P32–53.** Tìm key gần nhất phía trước thời điểm hiện tại; lấy `velocityAtTime(keyTime - frameDuration/10)`, nhân Slider amplitude và `sin(2π*freq*t)/exp(decay*t)`, cộng vào `value`.

**Bài học:** biên độ dao động phụ thuộc vận tốc đi vào key, khác hẳn cosine với amplitude cố định. Không chỉ chạy sau key cuối: logic nguồn chọn key phía trước hiện tại. Cần có keyframe, ba Slider đúng tên `Position amplitude`, `Position frequency`, `Position decay`; nếu vận tốc đi vào bằng 0 thì thành phần dao động theo công thức cũng bằng 0.

**Chưa kiểm chứng:** behavior khi có nhiều key, dimensions, key easing và giá trị controller. Không áp công thức như preset độc lập.

### Wiggle và liên kết property

**Nguồn P25–30, P54–56.** Notes có `position+value`, `wiggle(frequency, amplitude)` và một ví dụ viết `Wiggle(1,10,2,.25)`.

Khi viết expression dùng tên API `wiggle` chữ thường theo [Adobe Expression Language Reference](https://helpx.adobe.com/after-effects/desktop/work-with-expressions/expression-language-reference/expression-language-reference.html). Frequency theo giây; amplitude theo đơn vị property. Không sao chép nguyên ví dụ viết hoa và không xem lời ghi “tối đa ±50 px” là một giới hạn đã được kiểm chứng trong phiên này.

`position+value` phải xác định expression đặt ở property nào và tham chiếu nào cùng hệ tọa độ; đặt lên chính Position không phải ví dụ liên kết chung có thể áp mù quáng.

## 3. Transition bằng méo hình, giãn hình và scatter

**Nguồn P61–85, P164–216.** Nhóm effect được gợi ý: S_DissolveLuma, S_WipeBlobs, BCC 2D Particles/scatter, S_WarpVortex, Minimax, BCC Scatterize, S_Diffuse, RetroGrade Transition; các warp như FishEye, Magnify, Bubble, Chroma, HeatDistortion, Polar, Puddle, Wave Warp và Warp.

Các ví dụ có số cần giữ bối cảnh:

- P71–75 ghi vortex `0` tới `-20`, nhưng chưa ghi rõ tên property/timing; không đủ dựng curve chính xác.
- P77–81 ghi chuỗi Minimax `0`, `500`, `0` với dấu nối bị lỗi mã. Ảnh `image8.png` cho thấy Operation Maximum, Radius 500, Channel Color, Direction Just Horizontal. Đây là một mẫu giãn theo trục, không mặc định mọi clip dùng Radius 500.
- P177–180: FishEye Amount `-1.5` tới `0`; `image41.png` xác nhận tại ảnh Amount `-1.50`, Wrap X/Y Reflect, center `[960,540]`. Chưa có thời lượng hoặc easing.
- P165 ghi Scale Wipe “same as CC Smear”: giữ như liên tưởng thị giác của người ghi; không coi hai effect là tương đương tham số hoặc thuật toán.

**Cách học tiếp:** chọn clip, xác định trục/center/edge handling, rồi mới dựng envelope theo nhịp. Đừng suy từ ví dụ screenshot 1920×1080 rằng center `[960,540]` dùng cho mọi resolution.

## 4. Luma matte cho ánh sáng và flicker có chọn vùng

**Nguồn P92–124.** Hai ý tưởng riêng:

1. Chuẩn bị luma của nhân vật bằng Black & White/Levels/Blur; dùng chuyển động/texture ở layer khác và Luma Matte để giới hạn vùng hiện. Ảnh P97 cho thấy chuỗi Black & White → Levels → Gaussian Blur (Blurriness 6.9), không đủ chứng minh toàn bộ setup.
2. Tạo shape ngẫu nhiên, thêm blur, chỉnh Levels, dùng Luma Inverted Matte với cảnh chính để tạo flicker theo vùng (P117–124).

**Bài học:** flicker không nhất thiết là tăng/giảm Exposure toàn màn hình; matte có thể chọn vùng hoặc hình dạng. Chưa rõ role từng layer, invert, blend và layer order trong ví dụ nên chưa đưa ra preset hoàn chỉnh.

CC Blobbylize đi cùng một ghi chú tên blend viết không rõ ở P110–116; ảnh có texture màu và cảnh mẫu. Giữ ý tưởng texture-driven overlay, chưa chuẩn hóa tên blend từ câu mơ hồ đó.

## 5. Impact frame và chuỗi invert

**Nguồn P318–342.** Notes mô tả frame 1 dùng Invert, frame 2 dùng S_Invert tắt chroma. Ảnh P321/P324 cho hai kiểu màu khác nhau với chữ ERROR.

Ảnh `image93.png` (P326) xác nhận trạng thái screenshot: **Invert Luma bật**, Invert Chroma và các Invert Red/Green/Blue/Alpha tắt; Scale Lights 1, Offset Darks 0, Saturation 1. Không có timeline gốc để xác nhận hai ảnh thật sự là hai frame liên tiếp hoặc tổng thời lượng bao nhiêu.

P328–334 gợi ý chèn một frame năng lượng trước frame hành động. Đây là ý đồ timing để thử, chưa phải quy luật bắt buộc hoặc dự đoán được tác động hình ảnh từ một screenshot.

P336–342 gợi ý AE Pixel Sorter 2 với Sort by XOR. Ảnh minh họa có kéo vệt màu; cần giới hạn vùng/threshold và đọc đúng plugin version. Không gọi mọi vệt kéo là datamosh.

## 6. Blur có hướng và DOF

**Nguồn P226–245.** Có OLM DirectionalBlur, BCC Fast Lens Blur, Radial Blur, FL Depth of Field kèm ý tưởng depth scanner.

Ảnh `image61.png` tại P236 đọc rõ OLM DirectionalBlur:

| Tham số tại screenshot | Giá trị |
| --- | ---: |
| Angle | 35° |
| Brightness Gain | 1 |
| Front Blur Strength | 155 |
| Back Blur Strength | 75 |
| Front/Back Alpha Fade | 0 |
| Front/Back Sharp Tail | 0% |
| Noise Variation | 0% |
| Thickness | 10 |

**Bài học:** front/back blur có thể có độ mạnh khác nhau. Chưa có keyframe góc hoặc strength, nên không khẳng định các giá trị này đúng với chuyển động của mọi shot.

**Nguồn P346–348:** screenshot Camera Options (`image98.png`) có Depth of Field On, Focus Distance 1309 px, Aperture 262.3 px, Blur Level 100%, Zoom 2000 px. Đây là camera/scene cụ thể; cần camera distance, layer depth và comp size để tái dùng. Không đồng nhất camera DOF với blur 2D hoặc depth-map plugin.

## 7. Texture, sketch, halftone và pixel

**Nguồn P88–163, P217–225, P246–280.** Lưu như bản đồ lựa chọn, chưa gán mọi screenshot cho recipe hoàn chỉnh:

| Ý định ghi trong tài liệu | Effect/nhóm được nêu |
| --- | --- |
| Chất lượng nén/hỏng số | S_JpegDamage, S_DigitalDamage, JPEG Glitch |
| Scanline/TV/analog | BCC Damaged TV/Dissolve, Bad TV, Signal, uni.VHS Transition |
| Đồ họa/phong cách vẽ | BCC Pencil Sketch, S_AutoPaint, S_Cartoon, S_CartoonPaint |
| Chấm/pixel/hiển thị | BCC Halftone, BCC Tile Mosaic, BCC LED |
| Texture/vật liệu | BCC Grunge, Noise HLS, S_FilmDamage |
| Chia/kéo pixel | AE Pixel Sorter, Pixel Melt, Pixel Stretch, Pixelocybe |

Ảnh cùng scene với các xử lý khác nhau hữu ích để chọn hướng thị giác, nhưng chưa có render A/B giữ nguyên mọi tham số khác. Mức noise/chroma/edge cần thử theo footage, không mặc định “càng nhiều càng đẹp”.

## 8. Thời gian và màu theo thời gian

**Nguồn P282–304.** Notes mô tả S_TimeWarpRGB lệch R/G/B theo thời gian, phù hợp về cơ chế với các tham số frame shift đã đọc trong [Standard](standard.md#4-rgb-lệch-thời-gian-kết-hợp-threshold-không-phải-chỉ-rgb-lệch-vị-trí).

Các hướng thử khác: S_TimeSlice (ghi animate số slice nhưng chưa có tên property chuẩn), S_Trails, S_GetFrame/freeze, CC Wide Time, S_JitterFrames, S_MotionDetect, S_RandomEdits và Posterize Time.

**Phân biệt khi dùng:** freeze giữ frame, trail tích lũy lịch sử, RGB time-shift đổi nguồn thời gian từng kênh, Posterize Time giảm nhịp cập nhật hình. Chưa xem plugin/version và setting nên không xem tất cả tương đương retime hoặc speed ramp.

## 9. Colorama, Tritone và blend

**Nguồn P105–109:** Colorama và gợi ý blend Hue; ảnh cho thấy remap màu mạnh. Chưa ghi đủ Input Phase/Output Cycle để tái tạo.

**Nguồn P393–395:** làm tối midtone bằng Tritone, thêm Deep Glow/Curves/Levels, đặt blend Screen để gợi ý làm chủ thể nổi bật. Đây là hướng compositing cần mask/matte hoặc layer tách chủ thể; không khẳng định nó tự nhận biết chủ thể hay tương đương mọi lần gặp Tritone + Glow trong project.

**Đối chiếu bằng chứng:** White Ferrari có layer Screen chứa Tritone + PEDG nhưng có cả bản bật và tắt. Có chung nhóm công cụ không chứng minh dùng đúng recipe Notes.

## 10. Particle và mô phỏng phá vỡ

**Nguồn P352–364:** Particular, chọn emitter type, Particles/sec, Emitter Size XYZ Individual, direction/spread, velocity. Nguồn gợi Box, Uniform/Disc và spread khoảng 25–40; lưu như điểm bắt đầu thử, không phải thông số bắt buộc hoặc mọi loại emitter đều dùng được cùng chế độ.

**Nguồn P307–317:** CC Pixel Polly, CC Cylinder và BCC 3D Image Shatter; các ảnh có mảnh vỡ hoặc uốn mặt giấy. Chưa có source geometry, alpha, force/easing hoặc camera. Không gọi Cylinder là mô phỏng nếp gấp giấy vật lý chỉ từ tên ví dụ.

## 11. SFX lọc âm và reverb

**Nguồn P365–390.** Ý tưởng làm âm nghẹt trước điểm nhấn bằng High-Low Pass, kết hợp Reverb và audio level. Ghi chú có chuỗi cutoff `4000`, `800`, `4000` với dấu lỗi mã, không có timestamp/easing; giữ là đề xuất thử chứ không là envelope đã đo.

Ảnh `image104.png` tại P370 đọc rõ:

| Effect / tham số | Giá trị tại screenshot |
| --- | --- |
| High-Low Pass / Filter Options | Low Pass |
| Cutoff Frequency | 2400 |
| High-Low Pass Dry/Wet Out | 0% / 100% |
| Reverb Time | 100 ms |
| Diffusion / Decay / Brightness | 75% / 25% / 10% |
| Reverb Dry/Wet Out | 86% / 16% |

Đây là trạng thái tại một thời điểm, khác chuỗi cutoff trong câu ghi chú; không sửa hai nguồn thành cùng một giá trị.

Theo [Adobe Audio Effects](https://helpx.adobe.com/after-effects/desktop/apply-effects-and-animation-presets/list-of-effects/audio-effects.html), Dry/Wet điều khiển phần gốc và phần xử lý; 0% dry/100% wet là cấu hình thường dùng khi lọc bỏ tần số. Không áp câu “always decrease dryout” trong Notes thành quy tắc trộn âm phổ quát; cần nghe, kiểm tra gain và tránh clipping. Chưa nghe âm mẫu hoặc dựng SFX.

## 12. Tutorial và cách học tiếp

32 đoạn chứa link YouTube vẫn giữ trong `extracted-text.txt` (P397–470), gồm title card, 3D VHS text, vector blur, dissolve, print copy, shockwave, glitch/VHS, DOF, smoke, 3D, audio và pacing/scene selection. **Chưa mở hoặc xem các tutorial**, nên không ghi nội dung video thành kiến thức đã kiểm chứng.

Khi dùng một mục: lấy đúng ảnh/source, xác định property, đơn vị, layer order, controls và plugin version; thử trên project mới được ủy quyền, xem hoặc nghe kết quả rồi ghi lại recipe có thời gian/easing/điều kiện áp dụng. Chưa thay đổi DOCX gốc.

## Đọc nguồn và tái sử dụng

Bài này giữ số đo/tham chiếu từ lần phân tích đã ghi nhận; project, ảnh bằng chứng và báo cáo riêng không được phân phối cùng thư viện. Các mã `evidence:` là định danh nguồn, không phải file cần có để đọc bài. Người giữ nguồn tra chúng trong hồ sơ local; người đóng góp khác phải ghi nguồn và mức kiểm chứng của chính mình. Xem [quy ước bằng chứng](../foundations/evidence-and-validation.md).
