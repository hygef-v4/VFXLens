# Standard — chữ nảy, sticker và transition nhiều lớp

Bổ sung cho [sổ tay các dạng edit](../README.md), đọc ngày 2026-11-04. Thông số có nguồn từ JSON; mục đích thị giác là suy luận trừ khi được ghi rõ là quan sát ảnh. Chưa render AE tách effect.

## Nguồn và phạm vi

- Project: `evidence:standard-01`.
- Project JSON/report: `evidence:standard-02`.
- SHA-256 project: `8810ab59251ceb7c5c0399b2723ad78e7a34f247695d3d928ce5b4e16fd8f6f1`; sau phân tích khớp. Video nguồn phân tích cũng giữ nguyên hash.
- AE `22.0x111`, màu 8-bit, 17 composition, 137 layer, 5 expression entry được trích xuất.
- `cc2 standard.mp4` trong `(Footage)`: 1650×1080, 24 fps, 6.916667 giây; đã phân tích đủ 166 frame. Kết quả tại `evidence:standard-03`.
- Contact sheet quan sát có nền tím, giấy/ảnh chân dung, ký tự collage, mặt trời, mây, kim cương và icon; có thay đổi bố cục/phóng/xoay giữa các frame. Đây là quan sát prerender, chưa xác định effect riêng gây ra từng thay đổi.
- 50 asset thiếu ở đường dẫn đã lưu; 27 ứng viên trùng basename có trong `(Footage)`. Chưa xác minh nội dung hoặc relink. Report collect cũ ghi một missing item và chỉ collect selected comps; không đồng nghĩa toàn bộ project hiện đủ footage.
- Thời gian bên dưới theo từng comp. Có hai comp cùng tên `bg`: item 18 là 1650×1080/1 layer; item 857 là 1920×1080/4 layer. Tra bằng item_id và cấu trúc khi cần, không gộp theo tên.

## 1. Chữ nảy từng ký tự bằng Expression Selector

**Nguồn:** `trans`, layer 11 `i got ` và `trans 2`, layer 11 `Kool-Aid`. Cả hai text layer bật, Animator 1 có Expression Selector Amount bật.

Expression lưu các hằng số `freq=2.5`, `decay=4`, `duration=0.15`; độ trễ `textIndex * thisComp.frameDuration * 1`. Tính `t = time - (inPoint + retard)`; trước duration, dùng linear từ `[100,100,100]` về `[0,0,0]`; sau đó dùng dao động sin với mẫu số `exp(decay*(t-duration))` và `w=freq*2π`.

**Animator properties đọc được:** Position `[0,41,0]`, Scale `[0,0,100]`, Rotation `12`. Amount điều tiết tổ hợp các thuộc tính animator này; nó không trực tiếp bằng tọa độ hoặc scale cuối của ký tự.

**Điều rút ra:** một expression dùng chung cho nhiều ký tự, lệch một frame mỗi textIndex rồi dao động tắt dần. textIndex bắt đầu từ 1, nên ký tự đầu cũng có một frame delay so với inPoint, không phải zero delay.

Ở 24 fps, một frame khoảng 0.041667 giây. `duration=0.15` là thời gian biểu thức, không phải số frame nguyên. Chưa thực thi source expression, chưa kiểm tra selector mode/combination, easing cảm nhận hoặc font trên máy. Khi tái dựng phải mang cả animator properties và selector, không chỉ copy Amount.

## 2. Viền sticker bằng matte mở rộng và composite lại ảnh

**Nguồn:** `trans`, layer 4 `discord`: layer/effects bật, thứ tự:

`Simple Choker → Fill → CC Composite → S_DropShadow`

| Tham số | Giá trị lưu |
| --- | --- |
| Simple Choker / Choke Matte | -48.5 |
| Fill / Color | [1,1,1,1] |
| Fill / Opacity | 1 |
| CC Composite / Opacity | 100 |
| CC Composite / Composite Original | enum 3, chưa diễn giải tên |
| CC Composite / RGB Only | 1 |

**Suy luận để dựng thử:** dùng matte mở rộng, tô trắng, composite ảnh gốc và thêm shadow để tạo phân lớp. Phải xác nhận alpha và tên chế độ Composite Original trước khi gọi đây là preset viền hoàn chỉnh.

**Biến thể:** `cat cig Comp 1`, layer 2 `saitama`: thứ tự `Fill → Simple Choker → CC Composite`, Choke Matte `-37.2`; không được hoán đổi với stack trên và giả định kết quả giống nhau. `trans` layer 5/6 cũng có stack như layer 4, nhưng không suy ra mọi giá trị giống nhau nếu chưa đọc.

## 3. Transition đầu shot: warp nhanh, blur/mosaic/sáng giảm dần

**Nguồn:** `effects`, 1650×1080, 24 fps, 6.916667 giây. Các layer dưới đây bật và là adjustment layer.

| Layer | Khoảng hiện | Effect và keyframe |
| --- | --- | --- |
| 7 `warp` | 0–0.166667 | Warp Bend: 0 → 45; 0.125 → 0 |
| 6 `blur` | 0–0.291667 | Bokeh Blur Radius: 0 → 20; 0.291667 → 0; Mosaic Pixelate X: 25 → 0 cùng mốc; Brightness: 60 → 0 cùng mốc |
| 3 `blur 2` | 3.458333–3.75 | Cùng ba đường 20/25/60 về 0 ở 3.75 |

Trong dòng layer 6, `0 → 20` nghĩa là tại thời điểm 0 giây giá trị 20, không phải animation từ giá trị 0 lên 20. Mỗi effect có hai key, dùng BEZIER ở in/out.

**Thứ tự layer blur:** Bokeh → BCC Mosaic (`Boris3Pixelate`) → Brightness & Contrast. Motion Tile ở các layer warp tồn tại nhưng **effect disabled**; không đưa nó vào stack đang hoạt động.

**Điều rút ra:** warp hoàn thành khoảng ba frame, còn blur/pixelation/brightness giảm trong khoảng bảy frame. Dùng envelope có thời lượng khác nhau để nối một nhấn méo nhanh với quá trình trở lại rõ hình dài hơn.

**Giới hạn:** key cuối layer 6/3 trùng out_point, không nên nói giá trị 0 đã được hiển thị trọn một frame trước khi layer kết thúc. Cần kiểm tra Warp style/axis và toàn bộ giá trị tĩnh. Prerender `cc2 standard.mp4` ở layer 8 là đầu vào của comp `effects`, vì vậy nhìn video này không kiểm chứng được các effect xử lý phía sau nó.

## 4. RGB lệch thời gian kết hợp threshold, không phải chỉ RGB lệch vị trí

**Nguồn:** `fx`, adjustment layer 7, in/out 0–1.666667; `S_TimeWarpRGB → CC Threshold RGB`, đều bật.

- S_TimeWarpRGB: Red Shift Frames `1`, Green `0`, Blue `-1`.
- CC Threshold RGB: Red/Green/Blue Threshold đều `0.5`.
- Blend w. Original: `0.041667 → 0`, `1.208333 → 1`, BEZIER.
- Layer 2 là biến thể tiếp theo, in/out 1.666667–3.458333; Blend w. Original `1.708333 → 0`, `2.875 → 1`.

**Điều rút ra:** tách kênh theo frame thời gian khác nhau để có thể tạo viền màu phụ thuộc chuyển động; khác dịch R/G/B theo tọa độ ảnh. Chưa xác minh chiều lấy mẫu tương lai/quá khứ theo dấu shift trong plugin và chưa render đóng góp riêng.

**Áp dụng suy luận:** phối hợp mức threshold trở về original với một hiệu ứng màu theo thời gian. Chưa xem `record.mp4` nên không mô tả nội dung đầu vào của đoạn này.

## 5. Wipe đồng hồ cho phần trang trí

**Nguồn:** `trans`, layer 16 `flower`; in/out 2.458333–3.458333, layer và effect bật. Stack `S_WipeClock → S_DropShadow`.

Wipe Percent: `2.666667 → 100`, `3.0 → 0`, BEZIER — khoảng tám frame. Đây là wipe riêng cho một lớp trang trí, không cần chuyển toàn bộ composition. Cần đọc center, direction/reverse và softness để mô tả reveal chính xác.

## 6. Texture và loop theo thời gian — nguồn lưu nhưng phải xét đường render

- `bg` item 857, layer 2 `PYn.gif`: Time Remap expression bật `loopOutDuration(type = "cycle", duration = 0)`.
- Cùng comp, layer 3 `fx`: Roughen Edges / Random Seed có expression bật `time*9`.
- `got standard`, layer 5 `turbulent`: Random Seed expression `time*7` nhưng **layer disabled**. Layer 6 tham chiếu `bg` cũng tắt.

**Điều rút ra:** kiểm tra property expression thay vì chỉ đếm keyframe để tìm loop hoặc texture thay đổi theo thời gian. `time*9` là cách điều khiển seed; không khẳng định nó tương đương một bộ random mới chính xác 9 lần/giây nếu chưa kiểm tra plugin. Không mô tả hai expression trong bg là thành phần đang đóng góp vào bản cuối khi đường parent đang tắt.

## 7. Hai phiên bản collage cùng khung thời gian

`trans` và `trans 2` đều 42 layer, 1650×1080, 24 fps, dài 3.458333 giây. Các vị trí tương ứng có đổi nội dung, ví dụ layer 11 `i got ` ↔ `Kool-Aid`, layer 10 `Standards` ↔ `Jammer`; hai layer 11 dùng cùng expression chữ nảy và animator properties đã đọc ở mục 1.

**Bài học tái sử dụng:** tách khung timing/animation với nội dung chữ/asset để tạo biến thể. Không mặc định cả 42 layer đều có transform/parameter giống nhau chỉ vì cùng số lượng.

**Trạng thái quan trọng:** trong comp `transition`, hai layer tham chiếu `trans` và `trans 2` đều tắt. Trong `effects`, video `cc2 standard.mp4` bật còn layer `transition` tắt. Trong `got standard`, video `got standard  prefinal.mp4` bật, có các adjustment Deep Glow và Sharpen/Unsharp Mask/Looks/Flicker bật phía trên; chưa tìm được video prefinal trong thư mục đã cung cấp. Không xem MP4 6.9 giây đi kèm là bản hoàn chỉnh 18.29 giây của comp này.

## Cách dựng thử tiếp

Chọn một kỹ thuật, lấy đầy đủ source alpha/matte, effect settings, animator/selector hoặc dependency thời gian từ JSON rồi dựng trên project mới được ủy quyền. Các ghi chú là cấu trúc có nguồn và giả thuyết thử nghiệm; chỉ nâng thành công thức đã kiểm chứng sau khi có preview so sánh. Không mở/sửa project gốc hoặc thực thi expression nhúng để khám phá.

## Đọc nguồn và tái sử dụng

Bài này giữ số đo/tham chiếu từ lần phân tích đã ghi nhận; project, ảnh bằng chứng và báo cáo riêng không được phân phối cùng thư viện. Các mã `evidence:` là định danh nguồn, không phải file cần có để đọc bài. Người giữ nguồn tra chúng trong hồ sơ local; người đóng góp khác phải ghi nguồn và mức kiểm chứng của chính mình. Xem [quy ước bằng chứng](../foundations/evidence-and-validation.md).
