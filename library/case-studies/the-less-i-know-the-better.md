# The Less I Know the Better — collage, chữ và camera

Bổ sung cho [sổ tay theo dạng edit](../README.md), đọc ngày 2026-11-04. Tài liệu phân biệt cấu trúc/keyframe lưu trong project với phần đang được dựng qua prerender. Chưa có kiểm chứng đóng góp từng layer bằng render AE.

## Nguồn

- Project: `evidence:the-less-i-know-the-better-01`.
- Kết quả: `evidence:the-less-i-know-the-better-02` và `project-report.md`.
- SHA-256: `a37042c63022661bcdb6d7fd6973f78900310d3b241f40a98b03ed43c8b48f34`; kiểm tra lại sau phân tích khớp. Không sửa file gốc hoặc mở AE.
- Project AE `17.5x40`, 8-bit; 18 composition, 148 layer; không có expression entry được parser trích xuất. Không cần expression để tạo các chuyển động keyframe dưới đây.
- `Comp 1`: 1920×1080, 24 fps, dài 45 giây. Thời lượng composition không chứng minh đã có nội dung hoàn chỉnh đủ 45 giây.
- Parser báo 26 asset thiếu ở đường dẫn lưu; thư mục `(Footage)` có 25 ứng viên trùng basename. Chưa xác minh hash/nội dung, sequence hoặc relink. Report collect năm 2023 ghi một missing item; đó là trạng thái cũ, khác kiểm tra đường dẫn hiện tại.
- Có `Pre-comp 6.mp4` và `Pre-comp 6 p 2.mp4` trong footage. Đây là video nguồn/prerender, không mặc định là bản render hoàn chỉnh của `Comp 1`.
- Đã phân tích `Pre-comp 6.mp4`: 1920×1080, 24 fps, 17.666667 giây, đủ 424 frame; hash nguồn sau phân tích khớp. Báo cáo/timeline/contact sheet tại `evidence:the-less-i-know-the-better-03`.
- Contact sheet đã xem có xoắn ốc trắng trên nền đen, sao/trăng/tên lửa, các chữ rời; tiếp đến bố cục giấy hồng, ảnh mèo đóng khung, trái tim, mây, hành tinh và hoa. Có các bố cục xoay/phóng giữa frame. Đây là quan sát trên prerender, phù hợp về motif với asset/comp lưu trong project nhưng chưa xác nhận đóng góp riêng của camera/effect.
- Các mốc 9.25–12.54 giây in trên contact sheet thuộc MP4, không tự chuyển thành thời gian `Comp 1` hoặc các precomp authoring. Sheet chỉ chọn 25 ảnh và không đại diện toàn bộ video. Chưa phân tích `Pre-comp 6 p 2.mp4` hay bản tham chiếu tải từ mạng.

## 1. Wipe icon xuất hiện lệch nhịp

**Nguồn:** composition `then i saw your face`, layer 6–9. Layer và các effect đều bật. Thứ tự chung `S_DropShadow → S_WipePlasma`.

| Layer | Wipe Percent: giây → giá trị |
| --- | --- |
| 9 `pngegg (5).png` | 0.291667 → 100; 1.125 → 0 |
| 8 `ae` | 0.583333 → 100; 1.083333 → 0 |
| 7 `discord` | 0.833333 → 100; 1.333333 → 0 |
| 6 `spotify` | 1.125 → 100; 1.583333 → 0 |

Các key Wipe Percent có in/out BEZIER. Mốc bắt đầu lệch khoảng 6–7 frame ở 24 fps, nhưng độ dài wipe từng icon không bằng nhau.

**Điều rút ra:** tạo thứ tự xuất hiện bằng cách lệch animation của từng layer, không cần expression chạy theo ký tự. Đây là wipe của icon/ảnh riêng, khác TextEvo selector trong Takt Op.

**Chưa xác nhận:** hình dạng reveal thực tế, hướng wipe và seed plasma. Tên icon không chứng minh file nguồn là logo tương ứng; xem source item/footage khi tái dựng. Composition này còn lưu trong nhánh dựng bên dưới prerender, không mặc định đang render trực tiếp từ layer sống.

## 2. Collage có shadow riêng cho chữ và sticker

**Nguồn:** `then i saw your face`.

| Layer / effect S_DropShadow | Shadow Opacity | Shadow Blur | Shift X | Shift Y |
| --- | --- | --- | --- | --- |
| 2 `Then I Saw  Your Face` | 0.72 | 23 | -9.680008 | 20.319992 |
| 6 `spotify` | 0.79 | 12 | -9.680008 | 40.319992 |
| 9 `pngegg (5).png` | 0.79 | 22 | -9.680008 | 40.319992 |

Shadow Color lưu `[0,0,0,1]`. Các giá trị opacity trên theo thang effect lưu, không phải trực tiếp 0.72%.

**Điều rút ra:** cùng màu shadow nhưng có thể thay độ mờ và độ lệch giữa chữ/ảnh để tạo phân lớp. Đây là cấu trúc gợi ý collage; cảm giác giấy/sticker cụ thể cần xem render và alpha của source.

**Ví dụ tách ảnh chính và lớp tô:** `Pre-comp 2`, layer 1 và 2 cùng tên `cut cat.jpg`, đều bật, cùng in/out 0–2.625 giây; layer 2 nằm dưới và có `Fill → S_DropShadow`, layer 1 không có effect. Chưa kết luận lớp Fill là viền/silhouette: cần xem mask, alpha và transform của hai bản.

## 3. Camera chia chuyển động qua chuỗi Null

**Nguồn:** `3d stroke`, chuỗi parent theo index: `7 → 8 → 9 → 10 → Camera 1 (11)`. Các layer đều bật; có nhiều shape, ảnh và chữ bật 3D.

| Controller | Thuộc tính | Keyframe: giây → giá trị |
| --- | --- | --- |
| Null layer 9 | Position | 0.333333 → [0,0,0]; 0.916667 → [2,-1,188] |
| Null layer 9 | Z Rotation | 0.333333 → 0; 0.916667 → 110 |
| Null layer 10 | Position | -0.041667 → [0,0,10]; 0.5 → [0,0,71] |
| Null layer 10 | Z Rotation | -0.041667 → -219; 0.5 → -10 |

Các key trên có in/out BEZIER. Layer 9 còn có Orientation `[0,0,0] → [0.1,0.1,12]` cùng mốc với Position.

**Điều rút ra:** tách các chặng xoay/tiến camera trên nhiều controller, để chuyển động parent cộng với chuyển động local. Không cộng đơn giản các vector/rotation thành tọa độ thế giới; transform 3D có thứ tự và hệ trục riêng.

**Còn thiếu khi dựng lại:** camera options/point of interest, vị trí các lớp 3D, anchor, easing đầy đủ và map precomp lên timeline cha. Các nhánh này thuộc cấu trúc authoring còn lưu, chưa chứng minh ảnh trong prerender được tạo từ đúng revision đó.

## 4. Reveal hoa và trang trí bằng wipe/scale/opacity

**Nguồn:** `fine without u`.

- Layer 9 `rose`: S_WipeLine bật; Wipe Percent `11.5 → 100`, `12.166667 → 0`, BEZIER.
- Layer 6 `circle`: Wave Warp bật; Scale `12.333333 → [26,26,26]`, `12.791667 → [39,39,39]`, BEZIER. Opacity `12.333333 → 0`, `12.625 → 100`, LINEAR.
- Wave Warp static: Wave Type enum `1` (chưa diễn giải tên enum), Height `9`, Width `38.1`, Direction `98`, Speed `1.15`.

**Điều rút ra:** một lớp trang trí có thể dùng scale để tạo chuyển động, opacity để đưa vào và Wave Warp cho biến dạng bổ sung. Không cần animate tất cả thông số effect.

**Chưa xác nhận:** đường viền/silhouette cuối, hướng wipe và kết quả Wave Warp. Chưa gán các mốc local này cho thời gian trong MP4.

## 5. Wipe tròn và fade để nối prerender

**Nguồn đang bật trong `Comp 1`:**

| Layer | In/out, giây | Dữ liệu chính |
| --- | --- | --- |
| 9 `Pre-comp 6` | 8.958333–17.583333 | S_WipeCircle bật; Wipe Percent tăng từ 0 ở 16.5 tới 97 ở 17.416667 qua 15 key; Opacity 100 ở 17.166667 → 0 ở 17.583333 |
| 12 `Pre-comp 6 p 2.mp4` | 17.541667–25.958333 | S_WipeCircle bật; Wipe Percent từ 0 ở 24.375 tới 97 ở 25.583333 qua 13 key; Opacity 100 ở 25.5 → 0 ở 25.708333 |

Đường Wipe Percent layer 9 dùng BEZIER, layer 12 dùng LINEAR; cả hai opacity fade dùng BEZIER. Layer 9 còn key 0 ở 16.541667; layer 12 còn key 0 ở 24.75 trước khi tăng. Endpoint của wipe là 97, không phải 100.

**Điều rút ra:** đoạn cuối kết hợp wipe và opacity; fade về 0 vẫn loại bỏ layer dù wipe không đi hết 100. Khi tái dựng phải giữ cả hai đường, không rút gọn thành hai key wipe rồi tuyên bố tương đương.

**Giới hạn:** cần lấy center, direction/reverse, softness và các lớp bên dưới để mô tả reveal hay che đi chính xác. Chỉ có cấu trúc nối trong project, chưa có render AE toàn bài để xác nhận.

## 6. 3D Stroke có path, không có bằng chứng animate nét vẽ

**Nguồn:** `3d stroke`, layer 19 `3d stroke`, solid bật với một mask và `tc 3DStrokePath` bật. Static: Path enum `0`, Thickness `1.2`, Start `0`, End `100`; chưa thấy keyframe ở các tham số trực tiếp này.

**Bài học:** tồn tại plugin 3D Stroke không đồng nghĩa có animation vẽ nét bằng Start/End. Camera hoặc geometry có thể tạo chuyển động khác; phải đọc mask/path và các group liên quan trước khi đưa ra recipe draw-on.

## 7. Prerender thay thế nhánh dựng gốc

Trong `Pre-comp 6`, layer 1 `Pre-comp 6.mp4` bật, in/out 0–17.666667 giây; layer 2–19 đều tắt, gồm camera, Null, chữ và `Pre-comp 4`. Vì vậy có thể nghiên cứu những layer tắt như cấu trúc authoring, nhưng không nói chúng đang đóng góp trực tiếp khi render trạng thái hiện tại.

`Comp 1` layer 2 RSMB Pro và layer 3 Deep Glow cũng tắt ở cấp layer dù effect riêng bật. Không đưa blur/glow toàn cục này vào công thức đang hoạt động.

**Bài học mới cho sổ tay:** theo dõi đường render sống và đường authoring lưu trữ riêng. MP4 prerender có thể chứa hiệu ứng đã bake; project hiện tại không đủ chứng minh từng effect còn lưu là nguồn tạo đúng MP4 đó.

## Cách dùng lại

Chọn từng nhóm: icon wipe lệch nhịp, shadow cho collage, camera Null nhiều chặng hoặc circle wipe + fade. Lấy đầy đủ dependency, easing speed/influence, source và parent chain từ JSON trước khi dựng thử trên project mới. Không chạy expression/plugin không tin cậy, không sửa hay relink vào project gốc.

## Đọc nguồn và tái sử dụng

Bài này giữ số đo/tham chiếu từ lần phân tích đã ghi nhận; project, ảnh bằng chứng và báo cáo riêng không được phân phối cùng thư viện. Các mã `evidence:` là định danh nguồn, không phải file cần có để đọc bài. Người giữ nguồn tra chúng trong hồ sơ local; người đóng góp khác phải ghi nguồn và mức kiểm chứng của chính mình. Xem [quy ước bằng chứng](../foundations/evidence-and-validation.md).
