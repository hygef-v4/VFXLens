# Takt Op — phân tích transition, shake và chữ

Case study project/demo, đọc 2026-11-04. Các thông số bên dưới là dữ liệu của nguồn, không phải setting mặc định. [Tra kỹ thuật dùng chung](../techniques/README.md).

Thời gian trong các bảng thuộc composition được ghi tên, không mặc định là thời gian video demo. Khi đối chiếu cần lần start time, stretch, Time Remap và các precomp cha; fps giống nhau không xác lập hai timeline đã căn chỉnh.

## 1. Transition chroma, invert và displacement

**Từ AE Notes:** [warp/scatter và giãn hình](ae-notes.md#3-transition-bằng-méo-hình-giãn-hình-và-scatter), [impact frame/invert](ae-notes.md#5-impact-frame-và-chuỗi-invert); nhiều ví dụ chưa có thời lượng/easing.

**Đối chiếu Standard:** [warp kết hợp blur/mosaic/brightness](standard.md#3-transition-đầu-shot-warp-nhanh-blurmosaicsáng-giảm-dần) và [RGB lệch thời gian từng kênh](standard.md#4-rgb-lệch-thời-gian-kết-hợp-threshold-không-phải-chỉ-rgb-lệch-vị-trí).

**Dạng transition khác:** [circle wipe kết hợp opacity fade](the-less-i-know-the-better.md#5-wipe-tròn-và-fade-để-nối-prerender), có đủ hai đường animation và endpoint wipe không tới 100.

**Đối chiếu White Ferrari:** [transition bằng lớp một frame và blur dẫn vào cut](white-ferrari.md#3-transition-bằng-lớp-một-frame).

**Nguồn:** Takt Op → `Pre-comp 11` → layer 106, `a5e631f4dd4b96f69d91af16d23a40ef.mp4 Comp 1`; in/out 3,35–4,05 giây.

**Đã đọc từ project:** cả bảy effect bật, theo thứ tự:

`S_DistortChroma → S_Invert → Motion Tile → Displacement Map → CC Vector Blur → Exposure → Bokeh`

| Thuộc tính | Keyframe: giây → giá trị | Nội suy |
| --- | --- | --- |
| S_Invert / Invert Luma | 3,65 → 1; 3,70 → 0 | HOLD |
| S_Invert / Invert Chroma | 3,65 → 1; 3,80 → 0 | HOLD |
| Displacement / Max Horizontal Displacement | 3,35 → -323; 3,65 → 57; 4,00 → 57 | LINEAR rồi có tay nắm BEZIER |
| CC Vector Blur / Amount | 3,35 → 0; 3,65 → 136 | LINEAR |
| CC Vector Blur / Angle Offset | 3,35 → 0; 3,65 → 60 | LINEAR |
| Exposure / Exposure | 3,65 → 0; 4,00 → -0,59 | LINEAR |
| Exposure / Offset | 3,65 → 0; 4,00 → -1,26 | LINEAR |

**Điều rút ra:** tác giả xếp nhiều biến đổi trong một layer, dùng HOLD để chuyển trạng thái invert đột ngột và keyframe liên tục cho blur/displacement. Ở 20 fps, hai khoảng invert trên dài tương ứng 1 và 3 khoảng frame.

**Cách thử áp dụng — suy luận:** dựng displacement/blur trước, thêm invert ngắn ở điểm nhấn, sau đó tinh chỉnh màu và bokeh. Giữ thứ tự source làm mốc so sánh; không xem thứ tự thử từng bước là thứ tự render mới.

**Còn thiếu:** nguồn map displacement, các thông số tĩnh còn lại, transform/mask/blend và liên kết precomp. Bảng chưa đủ để trở thành preset độc lập.

## 2. Shake giảm dần sau điểm nhấn

**Từ AE Notes:** [overshoot theo vận tốc và cách đọc wiggle](ae-notes.md#2-chữ-cosine-tắt-dần-và-overshoot-theo-vận-tốc), phân biệt với envelope amplitude của plugin.

**Ví dụ từ preset:** [S_Shake và S_DissolveShake trong Chal7z](chal7z-presets.md#1-shake-giảm-biên-độ-và-dissolve-shake); chưa xác lập timebase của các keyframe FFX.

**Đối chiếu White Ferrari:** [shake có Motion Tile 400% và Mirror Edges](white-ferrari.md#1-shake-ngắn-có-xử-lý-mép-hình).

**Nguồn:** Takt Op → `Pre-comp 11` → layer 19, `Adj for a5e631f4dd4b96f69d91af1`; in/out 5,85–6,70 giây.

**Đã đọc từ project:** layer có `S_Shake` bật. `Amplitude`: 5,85 giây → 1; 6,405566 giây → 0.

**Điều rút ra:** điều khiển độ rung bằng một đường bao giảm về 0 trong khoảng 0,556 giây. Đây là biên độ chuẩn hóa của effect, không có nghĩa là dịch chuyển 1 pixel.

**Cách thử áp dụng — suy luận:** đặt biên độ cao tại điểm nhấn rồi hạ về 0 để cảnh ổn định lại. Cần đọc thêm frequency, trục rung, random seed, motion blur và easing trước khi tái tạo đúng source.

**Chưa xác nhận:** điểm nhấn này có khớp beat nhạc hay vị trí nào trong demo.

## 3. Dissolve kết hợp rung

**Đối chiếu White Ferrari:** [dissolve-shake chồng envelope rung ngắn](white-ferrari.md#2-dissolve-shake-dài-hơn-chồng-cùng-shot).

**Nguồn:** Takt Op → `Pre-comp 3` → layer 1, `ones.`; in/out 0,40–0,95 giây.

**Đã đọc từ project:** `S_DissolveShake` bật.

| Thuộc tính | Keyframe: giây → giá trị |
| --- | --- |
| Dissolve Percent | 0,40 → 33; 0,942188 → 0 |
| Y Phase | 0,40 → 3; 0,535547 → -0,55; 0,738867 → 0,15; 0,942188 → 0 |
| Tilt Phase | 0,40 → -1; 0,535547 → 0,35; 0,738867 → -0,02; 0,942188 → 0 |

**Điều rút ra:** phase đổi dấu với biên độ giảm, đồng thời dissolve về 0. Không chỉ giảm độ rung: tác giả còn điều chỉnh nhịp/pha rung bằng keyframe.

**Cách thử áp dụng — suy luận:** dùng dao động qua lại nhỏ dần để tạo cảm giác nảy trước khi ổn định. Cần lấy đầy đủ easing và các tham số Amplitude/Frequency/X/Y/Tilt từ JSON; ba đường trên không phải toàn bộ preset.

## 4. Glow, màu và bokeh

**Từ AE Notes:** [color remap/Tritone và blend](ae-notes.md#9-colorama-tritone-và-blend), [blur có hướng/DOF](ae-notes.md#6-blur-có-hướng-và-dof).

**Ví dụ từ preset:** [Bokeh phối hợp Gamma](chal7z-presets.md#2-transition-sáng-và-mờ-có-hai-đường-đồng-bộ); chỉ có envelope tăng được đọc, chưa khẳng định toàn bộ chu kỳ transition.

**Đối chiếu White Ferrari:** [film look và Blur Radius điều khiển bằng expression](white-ferrari.md#5-vhsfilm-look-bằng-expression-có-biên-độ-giới-hạn).

**Nguồn ví dụ:** Takt Op → `Pre-comp 11` → layer 26, `a5e631f4dd4b96f69d91af16d23a40ef.mp4 Comp 3`.

**Đã đọc từ project:** thứ tự `PEDG` (Deep Glow theo classifier) → `ADBE Tritone` → `CROSSPHERE_Bokeh`, đều bật. Deep Glow / Exposure có keys 5,85 → 0,26; 6,25 → 1,23; 6,65 → 0,02.

**Lưu ý quan trọng:** layer này chỉ hiện trong khoảng 6,65–6,70 giây. Hai keyframe đầu nằm ngoài khoảng hiện; không được mô tả toàn bộ đường exposure đó như một flash đã hiển thị trên layer này. Cần truy thêm các layer liên quan trước khi kết luận.

**Quan sát demo:** contact sheet có các vùng sáng hồng mạnh và khung hình mờ. Chưa tách được phần nào do Glow, Bokeh, footage nguồn hay lớp compositing khác.

**Cách thử áp dụng — suy luận:** kiểm soát sáng, ánh màu và độ mờ riêng từng bước. Không bê giá trị glow sang footage khác trước khi kiểm tra độ sáng đầu vào, bit depth và thứ tự effect.

## 5. Chữ động trễ từng ký tự

**Ví dụ từ preset:** [delay theo giây và cosine tắt dần](chal7z-presets.md#3-chữ-smooth-trễ-theo-giây-dao-động-cosine-tắt-dần), phân biệt với delay theo frame của Standard.

**Đối chiếu Standard:** [Expression Selector dao động tắt dần](standard.md#1-chữ-nảy-từng-ký-tự-bằng-expression-selector), [viền matte cho sticker](standard.md#2-viền-sticker-bằng-matte-mở-rộng-và-composite-lại-ảnh), và [hai biến thể collage cùng khung timing](standard.md#7-hai-phiên-bản-collage-cùng-khung-thời-gian).

**Dạng dựng khác:** [icon/ảnh wipe lệch nhịp](the-less-i-know-the-better.md#1-wipe-icon-xuất-hiện-lệch-nhịp), [collage có shadow](the-less-i-know-the-better.md#2-collage-có-shadow-riêng-cho-chữ-và-sticker), và [camera qua chuỗi Null](the-less-i-know-the-better.md#3-camera-chia-chuyển-động-qua-chuỗi-null). Đây là keyframe/parenting ở cấp layer, không phải selector từng ký tự.

**Nguồn:** Takt Op → `juice Comp 1` → layer 1, `juice 2` → `Text/Animators/TextEvo/Selectors/textevo/Amount`.

**Đã đọc expression tĩnh:** đọc control `effect("TextEvo")`, tính offset theo `textIndex`, `textTotal`, `thisComp.frameDuration` và lấy giá trị bằng `v.valueAtTime(time - offset)`.

| Chế độ | Công thức offset đọc được |
| --- | --- |
| Mode 1 | `(textIndex - 1) * frameDuration * delay` |
| Mode 2 | `(textTotal - textIndex) * frameDuration * delay` |

Expression còn có các nhánh theo tâm, mép, ký tự được chọn và random; random được seed bằng `textIndex + fx(5)` với tham số timeless bật. Cần đọc đầy đủ từng nhánh khi dùng.

**Điều rút ra:** animate một control chung rồi cho mỗi ký tự lấy mẫu đường animation tại thời điểm trễ khác nhau. Không cần vẽ keyframe riêng cho từng ký tự.

**Cách thử áp dụng — suy luận:** thay đổi chiều chạy và số frame trễ để tạo chữ xuất hiện lần lượt. Control TextEvo, chỉ số tham số và đường animation là dependency bắt buộc; đây chưa phải expression có thể dán độc lập vào project mới. Chưa thực thi expression.

## 6. Retime và speed ramp

**Dạng tích lũy thời gian khác:** [S_Trails / CC Wide Time](chal7z-presets.md#4-trail-và-wide-time-khác-posterize-thời-gian); không đồng nhất trail, posterize màu, posterize thời gian và speed ramp.

**Đối chiếu White Ferrari:** [phân biệt nhịp hình Posterize Time](white-ferrari.md#4-thay-đổi-nhịp-hình-bằng-posterize-time) với [dấu vết prerender/interpolation](white-ferrari.md#7-retime-và-prerender--bằng-chứng-còn-hạn-chế).

**Nguồn:** Takt Op → composition `a5e631f4dd4b96f69d91af16d23a40ef.mp4 Comp 1` → layer 1, footage cùng tên.

**Đã đọc từ project:** `Twixtor 45` bật; layer in/out 3,35–3,70 giây. Lần kiểm tra các tham số trực tiếp của instance này chưa thấy keyframe hoặc expression bật.

**Chưa đủ bằng chứng:** có Twixtor không đồng nghĩa với có speed ramp. Cần kiểm tra tốc độ tĩnh, group con, time remap, stretch, source fps và các instance khác. Detector video có các ứng viên speed ramp nhưng chưa chứng minh chúng đến từ instance này.

**Bài học hiện tại:** chỉ ghi nhận cấu trúc retime; chưa lưu công thức tăng/giảm tốc cụ thể. Không bịa curve hay tỷ lệ tốc độ.

## 7. Overlay và audio visualizer

**Từ AE Notes:** [luma matte chọn vùng flicker](ae-notes.md#4-luma-matte-cho-ánh-sáng-và-flicker-có-chọn-vùng) và [particle/mô phỏng phá vỡ](ae-notes.md#10-particle-và-mô-phỏng-phá-vỡ).

**Đối chiếu White Ferrari:** [overlay lens, fog và bướm theo Screen/Add](white-ferrari.md#6-overlay-ánh-sáng-và-khí-quyển-theo-blend-mode).

**Nguồn:** Takt Op → `Pre-comp 11` → layer 34, `Solid for Adj for Watch Takt Op`; in/out 8,20–10,20 giây.

**Đã đọc từ project:** `BCC_AUDIOVISUALIZER` bật trên layer solid. Kiểm tra tham số trực tiếp chưa thấy keyframe hoặc expression bật.

**Quan sát demo:** có chữ và các đường đồ họa chồng lên nhân vật. Chưa xác nhận đường nào là kết quả của Audio Visualizer hoặc có phản ứng theo âm thanh.

**Còn thiếu trước khi dựng lại:** audio source được tham chiếu, chế độ visualizer, dải tần, thông số hình học và blend/compositing. Chưa có công thức hoàn chỉnh cho dạng này.

## 8. SFX và xử lý âm thanh

[AE Notes: High-Low Pass + Reverb](ae-notes.md#11-sfx-lọc-âm-và-reverb) có thông số screenshot và đề xuất envelope; chưa có bản âm thanh đã nghe/đo để xác nhận hiệu quả. Khi học các project tiếp theo, ghi cả âm nguồn, timing, cutoff, dry/wet, gain và kết quả nghe.

## Nguồn và giới hạn chung

- Project: `evidence:takt-op-01`.
- Project JSON: `evidence:takt-op-02`; báo cáo cùng thư mục `project-report.md`.
- Demo JSON: `evidence:takt-op-03`; timeline, contact sheet và evidence frames cùng thư mục.
- Project có 46 composition, 290 layer và 82 expression entry; 82 entry không có nghĩa là 82 kỹ thuật khác nhau.
- Demo 13,2 giây, 20 fps; `Comp 1` dài 42,8 giây. Chưa căn chỉnh hai timeline.
- 32 asset thiếu tại đường dẫn lưu trong project. Chưa render AE hoặc kiểm chứng riêng đóng góp của từng effect.
- Nhãn plugin từ classifier và nhãn effect từ detector video cần đối chiếu; không dùng chúng làm kết luận mua/cài plugin.

## Đọc nguồn và tái sử dụng

Bài này giữ số đo/tham chiếu từ lần phân tích đã ghi nhận; project, ảnh bằng chứng và báo cáo riêng không được phân phối cùng thư viện. Các mã `evidence:` là định danh nguồn, không phải file cần có để đọc bài. Người giữ nguồn tra chúng trong hồ sơ local; người đóng góp khác phải ghi nguồn và mức kiểm chứng của chính mình. Xem [quy ước bằng chứng](../foundations/evidence-and-validation.md).
