# Timing và easing

**Mục đích:** đặt chuyển động vào đúng hành động/nhịp, đồng thời giữ đơn vị thời gian rõ ràng. Đây là hướng dẫn tổng quát; các con số trong case study chỉ thuộc nguồn được ghi tên.

## Phân biệt các đồng hồ

- Video có timestamp/fps riêng; composition và precomp có thể khác fps, start time, stretch hoặc Time Remap.
- Khoảng dài `n` frame ở fps `f` tương ứng `n/f` giây khi dùng timebase đó. Không chuyển thời gian precomp sang demo bằng fps giống nhau.
- Still image không mang thời lượng dựng. Image sequence cần fps diễn giải; dữ liệu preset có thể chỉ chứa time units chưa xác định.
- Các frame được mã hóa ở fps cao có thể lặp hình. Chưa đo cadence thì chưa khẳng định có thêm chuyển động để slow motion.

## Thiết kế đường chuyển động

1. Chọn điểm hành động: bắt đầu, điểm nhấn, kết thúc ổn định.
2. Đặt giá trị ở các mốc, xem chuyển động ở tốc độ phát thực.
3. Chỉnh easing để điều khiển cách vào/ra; dùng HOLD cho đổi trạng thái có chủ đích.
4. Nếu thêm overshoot/shake, kiểm tra envelope giảm và trạng thái cuối thay vì chỉ tăng cường độ.
5. Với nhiều layer/ký tự, phân biệt độ trễ bắt đầu với độ dài và easing của từng animation.

## Cách kiểm tra

Xem riêng đường keyframe và kết quả trong comp cha; kiểm tra motion blur, frame trước/sau cut và dependency của expression. Không kết luận có speed ramp chỉ vì thấy Twixtor. [Retime](../techniques/retiming/speed-ramp.md) và [chữ trễ](../techniques/typography/staggered-text.md) có quy trình chi tiết.

**Đối chiếu:** [White Ferrari: Posterize Time và prerender](../case-studies/white-ferrari.md), [Chal7z: time units của FFX](../case-studies/chal7z-presets.md).
