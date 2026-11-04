# Dissolve kết hợp rung

**Mục đích:** kết hợp thay đổi độ hiện với dao động giảm dần để nối hoặc đưa một lớp vào hình. Chưa có recipe render độc lập; xem [Takt Op, mục 3](../../case-studies/takt-op.md#3-dissolve-kết-hợp-rung) và [White Ferrari](../../case-studies/white-ferrari.md) cho dữ liệu nguồn.

## Cách dựng thử

1. Xác định lớp đang xuất hiện/biến mất và layer nền cần lộ.
2. Dựng đường dissolve theo semantics của effect; không mặc định giá trị 0 luôn là trong suốt.
3. Tạo dao động qua lại rồi giảm về trạng thái ổn định; phân biệt phase, amplitude và frequency.
4. Nếu chồng thêm shake riêng, xem hai envelope có cộng quá mạnh hoặc kéo dài ngoài đoạn hiện không.

## Dependency và kiểm tra

Ghi layer in/out, alpha, blend, dissolve percent, phase từng trục, amplitude/frequency và easing. Xem cả shot cha và background khi layer thay đổi độ hiện. Keyframe phase đổi dấu là bằng chứng điều khiển phase; chưa đủ để suy ra mọi tham số của preset.

**Đọc tiếp:** [shake envelope](../camera-and-motion/shake-envelope.md), [timing](../../foundations/timing-and-easing.md), [preset/script](../../tools/scripts-and-presets.md).
