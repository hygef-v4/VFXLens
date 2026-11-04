# Lọc âm và reverb theo chuyển động

**Mục đích:** dùng lọc tần số và không gian âm để hỗ trợ nhịp hình, không che transient hoặc làm đục mix. Đây là đề xuất thực hành; chưa có so sánh nghe/đo xác nhận cho ví dụ nguồn.

## Cách dựng thử

1. Chọn SFX bằng nghe trong ngữ cảnh, xác định transient và tail cần giữ.
2. Thử High/Low Pass theo mục đích: giảm dải không cần hoặc tạo thay đổi âm sắc có chủ đích.
3. Nếu cần chuyển động âm, animate cutoff/envelope theo action thay vì áp giá trị screenshot lên mọi file.
4. Thêm reverb theo không gian mong muốn, kiểm tra dry/wet, tail và gain.
5. Nghe tổng mix, so sánh khi bypass và kiểm tra khoảng nối/cắt.

## Dependency và giới hạn

Ghi nguồn âm, timing, cutoff, dry/wet và gain. Chỉ đo peak chưa đánh giá được âm sắc; sample peak không thay LUFS/true peak. Không gọi thông số screenshot là recipe đã nghe thử.

**Nguồn:** [AE Notes: SFX](../../case-studies/ae-notes.md). **Đọc tiếp:** [resource SFX](../../resources/sound-effects.md), [impact](../../styles/impact.md).
