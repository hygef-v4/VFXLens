# Sound effects: vai trò, đồng bộ và mix

## Nhận biết bằng nghe và waveform

| Vai trò đề xuất | Dấu hiệu cần nghe/xem | Dùng thử cho |
| --- | --- | --- |
| Whoosh/flyby | Envelope và chuyển động âm | Quét, xoay, chuyển cảnh có hướng |
| Hit/impact | Transient và phần body/tail | Contact, cut mạnh, từ khóa |
| Reverse/suck/riser | Năng lượng tiến tới điểm kết | Buildup vào hành động |
| Click/typewriter | Độ ngắn, nhịp và sắc thái | Cụm chữ/UI |
| Ambience | Độ liên tục, không gian | Nền cảnh và nối shot |
| Glitch | Cấu trúc nhịp/đứt đoạn | Điểm nhiễu có chủ đích |

Tên file là đầu mối; chỉ đo peak chưa xác nhận âm sắc, chất lượng hoặc đúng loại.

## Chọn và ứng dụng

1. Nghe riêng asset và xác định phần cần dùng; xem waveform để tìm lead-in, transient và tail.
2. Căn sự kiện nghe được với hành động hình ảnh, không mặc định đầu file hoặc sample peak là điểm sync tốt nhất.
3. Trim trên timeline, fade mép cắt và giữ tail phù hợp không gian.
4. Cân với nhạc/thoại, nghe tổng mix và kiểm tra mức đỉnh sau khi cộng lớp.
5. Dùng ít lớp có vai trò khác nhau; tránh thêm một hit cho mọi frame chữ hoặc mọi cut.

## Đo gì và chưa biết gì?

Sample peak, true peak, RMS và LUFS là các đại lượng khác nhau. Báo giá trị phải ghi cách đo, kênh, sample rate và đoạn đo. Peak chạm 0 dBFS cần kiểm tra headroom nhưng tự nó chưa chứng minh clipped; đo một đoạn không kết luận peak toàn file. Sample rate/bit depth cao hơn không đảm bảo âm phù hợp hơn.

Không lưu một gain cố định cho mọi SFX khi chưa nghe trong mix. Đánh dấu rõ trường hợp mới đọc tên hoặc chỉ đo tín hiệu.

**Liên quan:** [lọc âm/reverb](../techniques/sound-design/filters-and-reverb.md), [impact](../styles/impact.md), [AE Notes: ví dụ xử lý âm](../case-studies/ae-notes.md).
