# Overlay và audio visualizer

**Mục đích:** phối các lớp phụ với nội dung chính; với visualizer, xác định quan hệ giữa hình và nguồn âm thay vì chỉ đoán từ hình dáng.

## Quy trình dựng thử

1. Chọn vai trò của layer: foreground, ánh sáng, không gian, graphic hoặc biểu diễn âm thanh.
2. Với asset có sẵn, kiểm tra alpha/nền, timing và blend theo [overlays](../../resources/overlays.md).
3. Với audio visualizer, xác định audio source, dải tần/chế độ, hình học, gain và cách composite.
4. Xem khi thay đổi nguồn âm hoặc tắt layer để kiểm chứng đóng góp.
5. Kiểm tra ưu tiên thị giác: mặt, chữ và action có còn đọc được không?

## Mức bằng chứng hiện có

[Takt Op, mục 7](../../case-studies/takt-op.md#7-overlay-và-audio-visualizer) ghi một instance `BCC_AUDIOVISUALIZER`, nhưng chưa xác minh đường đồ họa nào trong demo đến từ effect đó hoặc có phản ứng âm thanh. Đây chưa phải recipe visualizer hoàn chỉnh.

**Ứng dụng:** [dreamy](../../styles/dreamy.md) và [collage](../../styles/collage.md). **Nền tảng:** [compositing](../../foundations/compositing.md).
