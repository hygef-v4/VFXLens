# Retime và speed ramp

**Mục đích:** điều khiển tốc độ hành động theo thời gian. Chưa có curve speed ramp hoàn chỉnh được xác minh từ các nguồn hiện tại; đây là quy trình kiểm tra và dựng thử.

## Phân biệt trước khi dựng

| Cơ chế | Điều nó thay đổi |
| --- | --- |
| Stretch/Time Remap/retime | Quan hệ thời gian nguồn và timeline |
| Speed ramp | Tốc độ thay đổi theo thời gian |
| Posterize Time | Nhịp lấy/giữ hình |
| Trail/echo/wide time | Tích lũy hoặc phối hình từ nhiều thời điểm |
| Motion blur | Độ nhòe chuyển động, chưa chứng minh retime |

## Cách dựng thử

1. Kiểm tra source fps, timestamp/cadence và cut trong clip.
2. Xác định action frame cần nhấn và các đoạn tăng/giảm tốc.
3. Dựng curve tốc độ, xem thời gian nguồn có đi đúng action không.
4. Đánh giá interpolation ở tóc, biên tay, occlusion và vùng qua cut.
5. Chỉ thêm motion blur sau khi đã xem chuyển động ở tốc độ mục tiêu; kiểm tra thứ tự xử lý thực tế.

Sự có mặt của Twixtor không đủ để khẳng định có ramp; cần đọc tốc độ, keyframe, Time Remap, stretch và các precomp. Twixtor retime khác nhiệm vụ RSMB motion blur. Xem [công cụ render](../../tools/render-effects.md).

**Nguồn và giới hạn:** [Takt Op, mục 6](../../case-studies/takt-op.md#6-retime-và-speed-ramp), [White Ferrari](../../case-studies/white-ferrari.md), [Chal7z: trail/wide time](../../case-studies/chal7z-presets.md). **Resource:** [footage](../../resources/footage.md).
