# Image sequences: nhập đúng frame, fps và channel

## Nhận biết

Sequence là một dãy frame có quy tắc tên; PNG/EXR cũng có thể chỉ là ảnh rời. Gom theo thư mục, prefix, số frame, suffix và extension trước khi kết luận một bộ có bao nhiêu animation.

## Kiểm tra trước khi nhập

- Khoảng số có liên tục không; có duplicate số hoặc frame bị đổi hậu tố bản sao không?
- PNG và EXR có cùng số frame/kích thước không? Không mặc định chúng là hai bản tương đương.
- FPS xuất là bao nhiêu? Tên số frame và ảnh tĩnh thường không đủ xác định.
- Có alpha thật không? PNG không bảo đảm alpha, EXR không bảo đảm chỉ có RGB/A chuẩn.
- Channel, bit depth và metadata màu có được host diễn giải đúng không?

## Ứng dụng

Chọn frame đầu và nhập như sequence; xem số frame/thứ tự mà host thực sự nhận. Dùng Interpret Footage theo fps nguồn đã xác minh. Kiểm tra đầu/cuối, alpha và tốc độ trước khi composite. Nếu thiếu fps nguồn, ghi chưa biết thay vì chọn một giá trị rồi gọi đó là tốc độ gốc. [Adobe: image sequence](https://helpx.adobe.com/after-effects/desktop/import-files/import-still-images/preparing-importing-still-images.html).

EXR có thể có nhiều channel đặt tên riêng, như beauty hoặc alpha nằm trong nhóm. Kiểm tra mapping/trích channel khi host không tự nhận; không đổi tên channel hoặc sửa nguồn chỉ để thử. Header có kiểu half/float không tự chứng minh không gian màu hoặc việc decode pixel thành công. [OpenEXR: cấu trúc và channel](https://openexr.com/en/latest/TechnicalIntroduction.html).

## Lỗi thường gặp

Import từng frame thành still rời; tên lẫn suffix làm host bỏ một đoạn; tự bù frame thiếu; lấy fps của preview khác làm fps chắc chắn của sequence; dùng blend để che lỗi channel. Thử trên bản làm việc và ghi rõ điều đã xác minh.

**Liên quan:** [compositing](../foundations/compositing.md), [timing](../foundations/timing-and-easing.md), [overlays](overlays.md).
