# Footage: chọn shot và kiểm tra dữ liệu

## Nhận biết

Phân biệt footage nguồn, flow pack đã xử lý, prerender, bản demo và render cuối. Một clip có cùng nhân vật hoặc fps chưa chứng minh là asset gốc của project. Tên 4K không thay thế metadata kích thước; fps khai báo chưa chứng minh mọi frame có hình khác nhau.

## Chọn và ứng dụng

1. Chọn shot theo hành động, hướng chuyển động, vùng đặt chữ và cảm xúc cần truyền tải.
2. Đọc kích thước, aspect ratio, fps/timestamp, duration và audio track.
3. Xem clip có cut, duplicate frame, retime, LUT/grade, watermark, HUD hoặc text sẵn không.
4. Xem cả vùng trước/sau action để chọn in/out; giữ hướng chuyển động liên tục nếu đó là mục tiêu nối shot.
5. Kiểm tra cadence trước khi slow motion; kiểm tra nguồn âm trước khi đưa vào mix.
6. Crop/reframe có chủ đích, không tự kết luận scale lớn hơn sẽ phục hồi chi tiết đã mất.

## Lỗi thường gặp

Relink theo basename/hình giống nhau mà không kiểm tra nội dung; dùng prerender để kết luận mọi layer authoring đang render; chuyển thời gian demo sang comp chỉ vì duration gần nhau. Giữ metadata và nhận xét quan sát riêng với suy luận.

**Liên quan:** [timing](../foundations/timing-and-easing.md), [retime](../techniques/retiming/speed-ramp.md), [case study Takt Op](../case-studies/takt-op.md).
