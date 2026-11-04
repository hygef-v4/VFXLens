# Cutouts, sticker và frame

## Nhận biết

Cutout tách vật thể khỏi nền; sticker có thể kèm viền/shadow; khung có vùng che và vùng trong suốt; ảnh chữ cắt sẵn không phải text editable. Kiểm tra alpha của cả ảnh palette, không chỉ ảnh RGBA. Nền caro in sẵn khác với alpha thật.

## Chọn và ứng dụng

1. Xem biên trên nền sáng/tối và kiểm tra kích thước dùng cuối, nhất là chữ cắt giấy nhỏ.
2. Đặt anchor theo cách vật thể cần xoay/scale; giữ đúng tỉ lệ hình.
3. Dùng Normal để giữ màu và alpha khi thích hợp. Nếu cần viền/shadow, kiểm tra độ dày và hướng sáng nhất quán.
4. Với collage, animate các mảnh theo nhóm hoặc Null rồi thêm độ trễ có chủ đích.
5. Với split screen, đặt clip dưới vùng lỗ và mask từng clip để không tràn sang ô khác.
6. Kiểm tra vị trí mặt/chữ sau khi đặt border; tên Cinemascope không đảm bảo mọi frame đều có thanh đen trên/dưới.

## Lỗi thường gặp

Phóng ảnh nhỏ quá mức; dùng Screen làm mất nét tối; shadow khác hướng giữa các mảnh; nhầm ba lỗ trong PNG với ba vùng footage tự động; áp TextEvo vào ảnh chữ raster.

**Liên quan:** [collage](../styles/collage.md), [chữ động trễ](../techniques/typography/staggered-text.md), [Standard: viền matte](../case-studies/standard.md), [The Less I Know: shadow/camera](../case-studies/the-less-i-know-the-better.md).
