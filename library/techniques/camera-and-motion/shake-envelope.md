# Shake có đường bao giảm dần

**Mục đích:** tạo điểm nhấn rồi đưa hình về ổn định. Hướng dẫn là đề xuất dựa trên envelope đọc được; chưa xác nhận sync với beat trong mọi nguồn.

## Cách dựng thử

1. Chọn điểm nhấn và khoảng cần ổn định trở lại.
2. Đặt amplitude cao quanh điểm nhấn rồi giảm về mức nền mong muốn.
3. Chọn frequency, trục và rotation theo chuyển động shot; kiểm tra easing và seed nếu dùng ngẫu nhiên.
4. Kiểm tra biên khi dịch/xoay/zoom; thêm xử lý biên phù hợp và đánh giá motion blur.
5. Bật/tắt shake để xác định nó làm rõ hành động hay che mất nội dung.

## Đơn vị và dependency

Amplitude chuẩn hóa của plugin không mặc định là pixel. `wiggle` và keyframe phase không có cùng nghĩa với amplitude envelope. Chú ý layer in/out, key ngoài đoạn hiện và shake khác ở precomp cha.

**Bằng chứng:** [Takt Op, mục 2](../../case-studies/takt-op.md#2-shake-giảm-dần-sau-điểm-nhấn) có đường Amplitude giảm; [White Ferrari](../../case-studies/white-ferrari.md) có ví dụ Motion Tile/Mirror Edges; [Chal7z](../../case-studies/chal7z-presets.md) giữ time units FFX chưa quy đổi.

**Dùng trong:** [impact](../../styles/impact.md), [dissolve-shake](../transitions/dissolve-shake.md).
