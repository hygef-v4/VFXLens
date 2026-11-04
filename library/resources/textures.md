# Textures: chọn chất liệu và cách hòa trộn

## Nhận biết

Giấy, plastic, film grain, xước, bụi và lens dirt có thể là ảnh tĩnh hoặc video. Kiểm tra ảnh thực: tên PAPER không bảo đảm nền trắng; tên Film Burn chưa chứng minh đặc trưng cháy phim. Phân biệt texture toàn bề mặt với dirt chỉ hợp quanh nguồn sáng.

## Chọn và ứng dụng

1. Xác định cần chất liệu, tương phản, độ cũ hay chi tiết foreground.
2. Xem độ phân giải, nền sáng/tối/xám, alpha và scale hạt ở kích thước xuất.
3. Thử Multiply cho nét tối trên nền sáng; Overlay/Soft Light cho tương tác tương phản; Screen cho highlight trên nền đen. So sánh từng phương án.
4. Điều chỉnh mức đóng góp và vùng tác động để giữ da, mắt, chữ dễ đọc.
5. Nếu ảnh tĩnh cần chuyển động, animate có chủ đích; không coi ảnh lớn là một video loop.

## Lỗi thường gặp

Kéo giãn làm hạt/xước méo; blend làm đen hoặc bạc hình; texture vẫn đứng yên khi vật thể cần chuyển động cùng; loop có điểm nối lộ. Không gán cùng opacity hoặc scale cho mọi shot.

**Liên quan:** [compositing](../foundations/compositing.md), [retro/VHS](../styles/retro-vhs.md), [collage](../styles/collage.md). Đối chiếu [Standard](../case-studies/standard.md): layer có texture vẫn cần xét đường render và prerender.
