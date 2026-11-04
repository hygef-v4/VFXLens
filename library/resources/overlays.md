# Overlays: ánh sáng, khí quyển và matte

## Nhận biết

- Ánh sáng, bokeh, điện hoặc particle nền đen: xem nền đen có thật sự sạch và có màu tối cần giữ không.
- Vật thể như bướm, lá, debris: kiểm tra alpha thực; đuôi MOV không chứng minh trong suốt.
- Khói/fog: xem mật độ và vùng phủ qua thời gian; một frame đầu tối không chứng minh asset rỗng.
- Mảng đen trắng lan kín khung: có thể làm matte điều khiển reveal, không chỉ đặt lên hình như lớp trang trí.
- HUD, chữ AV hoặc border có sẵn là một phần asset; kiểm tra trước khi dùng.

## Chọn và ứng dụng

1. Chọn vai trò: điểm sáng, chiều sâu, nhấn hành động hay chuyển cảnh.
2. Kiểm tra alpha, kích thước, fps, duration và một số thời điểm trong clip.
3. Vật thể có alpha: thử Normal. Ánh sáng nền đen: thử Screen/Add. Matte: dùng alpha/luma phù hợp.
4. Đặt điểm phát sáng/origin theo nguồn sáng hoặc action; chọn đoạn phù hợp, không bắt buộc dùng toàn clip.
5. Match màu, scale, độ nét, occlusion và chuyển động với shot; xem cả khi tắt overlay.

## Lỗi thường gặp

Screen vật thể làm mất phần màu tối; fog làm hình bạc; Add quá mạnh làm mất chi tiết; overlay lặp quá rõ; điện/shockwave không bám hành động. Kiểm tra biên alpha trước khi chữa bằng key. Các lựa chọn blend theo nguyên lý [compositing](../foundations/compositing.md), chưa phải preset cố định.

**Liên quan:** [dreamy](../styles/dreamy.md), [impact](../styles/impact.md), [matte reveal](../techniques/transitions/matte-reveal.md). Ví dụ project: [White Ferrari](../case-studies/white-ferrari.md).
