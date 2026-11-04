# Fonts: chọn dáng chữ và kiểm tra ngôn ngữ

## Nhận biết theo hình dáng

| Dáng | Ứng dụng nên thử | Cần chú ý |
| --- | --- | --- |
| Sans rõ, nét vừa | Caption/lyric và chữ phụ | Độ rộng, khoảng cách và cỡ xuất |
| Condensed cao/hẹp | Tiêu đề ngắn | Dấu và chữ hoa có bị chật không |
| Display rất đậm | Từ khóa impact/sticker | Không gian âm và độ đọc khi blur |
| Serif | Mood editorial/hoài niệm | Chi tiết chân chữ ở cỡ nhỏ |
| Script/brush | Nhấn từ, chữ trang trí | Nét nối, khoảng thở, mapping ký tự |
| Pixel/block | Retro/game | Giữ cấu trúc pixel khi scale |

Đây là hướng lựa chọn mỹ thuật, không phải quy định phong cách. Tên có chữ Glitch không đủ để kết luận hình dáng là nhiễu số.

## Quy trình chọn

1. Render **đúng câu cần dùng**, có dấu, số, punctuation và các chữ hoa/thường cần thiết.
2. Kiểm tra glyph thiếu, ô vuông, dấu sai vị trí hoặc fallback làm lệch style.
3. Xem ở kích thước xuất, trên background thật và trong chuyển động.
4. Kiểm tra line break, tracking, stroke, shadow và khả năng đọc ở peak blur.
5. Kiểm tra phạm vi sử dụng của font trước khi đưa file font vào một bản phân phối.

Bảng Unicode cmap có đủ ký tự là bước lọc, chưa xác nhận shaping, dấu tổ hợp hoặc render trong AE. Không chuyển kết quả của một file/style sang mọi file cùng family. Các glyph logo/demo có thể xuất hiện ở vị trí chữ/số; phải kiểm tra câu thực tế.

**Liên quan:** [typography](../techniques/typography/staggered-text.md), [collage](../styles/collage.md), [công cụ easing/text](../tools/easing-and-typography.md).
