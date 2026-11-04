# Collage

**Dấu hiệu để nhận biết:** nhiều mảnh ảnh/chữ/icon có biên riêng, sự chồng lớp, khung, chất liệu và bố cục thay đổi. Đây là mô tả định hướng, không phải mọi collage đều cần mọi yếu tố.

## Chuỗi dựng đề xuất

1. Chọn bố cục và thứ tự đọc, đặt background và chủ thể chính.
2. Thêm [cutout/khung](../resources/cutouts-and-frames.md), giữ tỉ lệ và khoảng trống cho chữ.
3. Chọn [font](../resources/fonts.md) hoặc ảnh chữ cắt giấy; thống nhất viền và shadow.
4. Dựng chuyển động nhóm qua Null/camera hoặc transform, rồi thêm [độ trễ chữ](../techniques/typography/staggered-text.md) nếu cần.
5. Thêm [texture](../resources/textures.md) và SFX vừa đủ; kiểm tra ở tốc độ phát.

## Kiểm tra

Thứ tự lớp, alpha, hướng shadow, độ đọc và mép khung; các mảnh có chuyển động theo cùng hệ tọa độ không? Dùng camera không tự tạo chiều sâu nếu mọi lớp vẫn cùng mặt phẳng. Tránh keyframe tất cả mảnh khi một nhóm điều khiển đã đủ.

**Case study:** [The Less I Know](../case-studies/the-less-i-know-the-better.md) có camera/Null và shadow; [Standard](../case-studies/standard.md) có chữ/sticker và hai bố cục. Đây là ví dụ từng kỹ thuật, chưa phải xác nhận mọi lớp đang hiện trong bản prerender.
