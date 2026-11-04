# White Ferrari — các kỹ thuật edit đọc được

Tài liệu bổ sung cho [sổ tay theo dạng edit](../README.md). Các giá trị dưới đây đọc từ project `white-ferrari.aep`, ngày 2026-11-04. Đây là ví dụ tham chiếu có nguồn, chưa phải preset hoàn chỉnh hoặc render tách effect đã kiểm chứng.

## Nguồn và trạng thái

- Thư mục gốc: `evidence:white-ferrari-01`.
- Dữ liệu: `evidence:white-ferrari-02` và `project-report.md` trong workspace VFXLens.
- Project SHA-256: `a98c718b0e37996e6dd68eedc747cf671571eb91e22eceb61792ecce0eb8fe85`; kiểm tra sau phân tích khớp. Không mở AE hoặc sửa project gốc.
- 82 composition, 816 layer, 73 expression entry; AE lưu phiên bản `25.0x2`, màu 16-bit. Cấu hình CUDA trong project không chứng minh analyzer đang dùng GPU.
- `Main`: 1920×1080, khoảng 23,976 fps, 18,518519 giây, 65 layer.
- Bản render có sẵn `final 2.mp4`: 3840×2160, 24000/1001 fps, 18,5185 giây. Thời lượng/fps gần khớp Main nhưng chưa chứng minh cùng revision hoặc căn chỉnh từng shot.
- Đã phân tích đủ 444 frame của bản render; nguồn giữ nguyên hash. Kết quả tại `evidence:white-ferrari-03`: báo cáo, timeline, contact sheet và ảnh bằng chứng.
- **Giới hạn timestamp:** ffprobe đọc PTS từng frame bị timeout 120 giây; analyzer dùng timestamp dự phòng theo nominal fps. Vì vậy `VFR=False`, jitter=0 và timestamp trong báo cáo không phải kết quả xác minh PTS gốc. JSON warnings hiện không ghi lại lỗi fallback này; log CLI có ghi.
- Contact sheet đã xem cho thấy các khung xanh lạnh, vùng sáng mạnh, hình méo và nét viền sáng, sau đó có ký tự rời trên hình. Đây là mô tả ảnh quan sát được, chưa gán chắc chắn cho plugin/layer nào. Sheet hiện chọn nhiều peak sớm nên tập trung khoảng 0–3,63 giây, không đại diện toàn bộ 18,52 giây.
- 74 asset được báo thiếu tại đường dẫn đã lưu. Tìm trong `(Footage)` có 7 ứng viên trùng basename; chưa xác minh nội dung hoặc relink. Báo cáo collect đi kèm ghi 57 file, khoảng 4,9 GB; không đồng nghĩa đã đủ mọi dependency của toàn bộ project.
- Các mốc dưới đây theo composition được nêu, dùng dấu chấm thập phân. Với precomp, cần lần start/stretch/time remap của parent trước khi suy ra thời gian Main.

## 1. Shake ngắn có xử lý mép hình

**Nguồn:** `Main` → layer 20 `shake 2`, adjustment layer bật; in/out `14.014014–14.597931` giây, effects active.

**Thứ tự bật:** `ADBE Tile` (Motion Tile) → `S_Shake`.

- Motion Tile: Output Width `400`, Output Height `400`, Mirror Edges `1`; Tile Width/Height `100`.
- S_Shake / Amplitude: `14.014014 → 0`, `14.055722 → 0.28`, `14.264264 → 0`; các key có in/out BEZIER.
- Đường bao lên đỉnh sau khoảng một frame, về 0 sau khoảng sáu frame tính từ key đầu tại fps Main. `0.28` là giá trị Amplitude của effect, không phải số pixel.

**Điều rút ra:** tách việc mở rộng mép ảnh và việc tạo rung thành hai bước có thứ tự rõ ràng. Suy luận mục đích Mirror Edges là hỗ trợ che mép trống khi dịch chuyển; chưa render riêng để xác nhận mức cần thiết.

**Trước khi dùng lại:** lấy frequency, trục rung, seed, motion blur và easing speed/influence đầy đủ từ JSON. Không quy mọi shake trong render về layer này.

## 2. Dissolve-shake dài hơn chồng cùng shot

**Nguồn:** `Main` → layer 21 `shake`, adjustment layer bật; in/out `13.596930–14.764765`.

**Thứ tự bật:** Motion Tile → S_Shake → S_DissolveShake. Motion Tile cũng Output Width/Height `400`, Mirror Edges `1`.

S_DissolveShake / Dissolve Percent: `13.596930 → 38`, `14.139139 → 0`, BEZIER ở các key.

**Điều rút ra:** layer 20 và 21 có khoảng hiện chồng nhau, với envelope riêng. Có thể học cách tách một chuyển động nền dài hơn và một nhấn rung ngắn; đó là suy luận từ cấu trúc, chưa đo đóng góp từng layer trong render. Cần kiểm tra phạm vi các adjustment layer và các layer bên dưới trước khi tái dựng.

## 3. Transition bằng lớp một frame

**Nguồn trực tiếp trong `Main`:**

| Layer | In → out, giây | Effect bật theo thứ tự |
| --- | --- | --- |
| 5 `OneFramer for Pre-comp 35` | 14.723056 → 14.764765 | Offset → BCC Directional Blur |
| 11 `1frame` | 14.055722 → 14.097431 | Median → Mosaic Plane |
| 17 `OneFramer for Null 23` | 13.596930 → 13.638639 | OLM Directional Blur → Transform |
| 32 `Adj for Silent Voice Dub.mp4` | 13.555222 → 13.596930 | OLM Directional Blur → Deep Glow (`PEDG`) |

Các layer trên bật, là adjustment layer; độ dài khoảng `0.041709s`, tương đương một frame ở khoảng 23,976 fps. Vì vậy một thay đổi rất ngắn có thể đến từ in/out của layer, không nhất thiết từ cặp keyframe effect.

**Ví dụ blur dẫn vào điểm đổi shot:** `Main`, layer 51 `Adj for Pre-comp 22`, in/out `8.883884–9.134134`; S_BlurDirectional / Blur Amount từ `0` ở `8.883884` lên `120` ở `9.092426`, BEZIER. Cần xem thêm hướng blur và layer kế tiếp để xác nhận cách nối shot.

**Áp dụng suy luận:** dùng lớp một frame làm điểm nhấn rất ngắn, phân biệt với blur có envelope tăng dần. Đây là kỹ thuật theo thời gian, không phải khuyến nghị dùng mọi plugin trong bảng cùng lúc.

## 4. Thay đổi nhịp hình bằng Posterize Time

**Nguồn trong `Main`, adjustment layer và effect đều bật:**

| Layer | Khoảng hiện, giây | Frame Rate trong Posterize Time |
| --- | --- | --- |
| 60 `Adj for Pre-comp 18` | 1.835169–2.335669 | 12 |
| 54 `Adj for Pre-comp 18` | 5.839173–6.798465 | 16 |

**Điều rút ra:** tác giả đặt mức lấy mẫu thời gian riêng cho từng đoạn, dù composition chính vẫn khoảng 23,976 fps. Posterize Time thay đổi nhịp cập nhật hình, không tự chứng minh video bị đổi tốc độ phát.

**Trước khi tái dựng:** kiểm tra độ chồng layer, vị trí adjustment và chuyển động footage. Không đánh đồng Posterize Time, Twixtor và speed ramp.

## 5. VHS/film look bằng expression có biên độ giới hạn

**Đã đọc expression tĩnh, chưa thực thi:**

- `Main` → layer 6 `Adj for Null 27`: in/out `14.347681–14.472806`, Universe VHS bật; Opacity có expression bật `random(0,60)`.
- `Pre-comp 13` → layer 16 `vhs`: in/out `0.208542–0.333667`, Universe VHS bật; Opacity `random(0,50)`.
- `Pre-comp 17` → layer 26 `Pre-comp 4`: Fast Bokeh / Blur Radius `random(0,5)`. Stack bật Motion Tile → FC NITRATE → Curves → Colorista IV → Fast Bokeh.

**Điều rút ra:** mức hiện VHS và blur được điều khiển bằng expression thay vì nhất thiết có keyframe. Giá trị static/pre-expression trong JSON không phải giá trị cuối khi render.

**Cách áp dụng suy luận:** giới hạn khoảng biến thiên của texture/blur để tạo độ bất định có kiểm soát. Chưa xác nhận tần suất cảm nhận, seed, kết quả theo subframe hoặc mức độ giống film thật. Đọc và tái viết expression chỉ trong bài dựng mới được ủy quyền; không chạy expression nhúng của project để khám phá.

## 6. Overlay ánh sáng và khí quyển theo blend mode

| Nguồn | Trạng thái và dữ liệu đã đọc |
| --- | --- |
| `Pre-comp 17`, layer 3 `LENS 25 .mp4` | Bật, SCREEN, in/out 0.041708–1.084418; Opacity expression bật `random(50,65)` |
| `Pre-comp 14`, layer 41 và 42 `1 Fog Atmosphere Side.mp4` | Cả hai bật, ADD, in/out 0–1.042709; Curves bật, Opacity lưu 100 |
| `Pre-comp 13`, layer 12 `D2 Butterflies (1).mp4 Comp 1` | Bật, SCREEN, in/out 0–0.959293; Posterize Time → Curves → Hue/Saturation bật |

**Điều rút ra:** cùng một bài dựng sử dụng overlay footage với nhiều blend mode, có layer điều khiển opacity bằng expression và layer xử lý màu riêng. Không được suy ra mọi overlay đều dùng Screen hoặc mọi bướm đều là particle plugin.

**Còn thiếu:** xem nội dung footage/alpha, transform, parent và layer order đầy đủ để giải thích đóng góp từng bản fog lặp. Chưa xác nhận vì sao tác giả cần cả hai layer.

## 7. Retime và prerender — bằng chứng còn hạn chế

Project có các instance `Twixtor 45`; lần rà tham số trực tiếp của các instance bật chưa tìm được keyframe tốc độ để ghi thành recipe speed ramp.

Thư mục footage và report có các tên chứa `8x-RIFE-RIFE4.0-191.8082fps`, cùng nhiều file `Pre-comp ...` đã render. **Tên file chỉ là dấu vết workflow**, chưa xác minh quá trình tạo, fps thật của từng clip hoặc thiết lập interpolation. Không dùng tên file để kết luận RIFE đã tạo frame chuẩn hay render hiện tại còn cần Twixtor.

**Bài học có thể lưu:** tách việc nghiên cứu prerender/interpolation của footage nguồn khỏi việc nghiên cứu chuyển động/effect trong AE. Muốn có recipe retime đầy đủ phải đọc đúng instance, group con, tham số tĩnh và nguồn clip.

## 8. Tránh học nhầm effect đang tắt

`Main` layer 1 `cc` có nhiều effect bật riêng lẻ nhưng **layer enabled=false**; expression Position `wiggle(6,2)` nằm trên layer này. Không ghi nó là camera shake đang đóng góp vào render hiện tại.

`Main` layer 2 có Posterize Time nhưng layer tắt. Layer 40 `tritione 2` blend Screen cũng tắt, trong khi layer 42 `tritione` bật. Cần kiểm tra đồng thời layer enabled, effects_active, từng effect enabled, in/out và đường đi từ Main tới precomp. Precomp tồn tại không đồng nghĩa đang được render.

## Kiểm chứng tiếp theo

Đối chiếu contact sheet/render với các mốc Main để chọn shot cần học sâu, sau đó đọc đầy đủ dependency của shot. Chỉ ghi nhận một effect gây ra hình ảnh cụ thể khi đã đối chiếu preview trên bản sao an toàn; không tự mở hoặc thay đổi project gốc.

## Đọc nguồn và tái sử dụng

Bài này giữ số đo/tham chiếu từ lần phân tích đã ghi nhận; project, ảnh bằng chứng và báo cáo riêng không được phân phối cùng thư viện. Các mã `evidence:` là định danh nguồn, không phải file cần có để đọc bài. Người giữ nguồn tra chúng trong hồ sơ local; người đóng góp khác phải ghi nguồn và mức kiểm chứng của chính mình. Xem [quy ước bằng chứng](../foundations/evidence-and-validation.md).
