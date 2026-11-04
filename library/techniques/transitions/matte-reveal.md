# Reveal và transition bằng matte

**Mục đích:** dùng hình hoặc độ trong suốt của một layer để điều khiển vùng hiện của layer khác. Có thể dùng cho wipe, ink, noise và khung đồ họa; đây là quy trình dựng thử.

## Cách dựng thử

1. Đặt shot A làm nền và shot B cần reveal ở trên.
2. Chọn matte: alpha nếu có vùng trong suốt đúng ý, luma nếu dùng độ sáng.
3. Với Luma Matte, trắng hiện B và đen ẩn B; đảo matte khi cần hướng ngược lại.
4. Trim/retime matte theo nhịp, kiểm tra vùng che tại đầu/cuối và điểm nối.
5. Xem mép và phần xám trung gian trước khi tăng contrast hoặc threshold.

Theo [Adobe: track mattes](https://helpx.adobe.com/after-effects/desktop/work-with-transparency-and-compositing/work-with-track-mattes-and-traveling-mattes/track-mattes-and-traveling-mattes.html), alpha và luma là hai nguồn điều khiển khác nhau. Video trắng đen có thể opaque hoàn toàn nên dùng Alpha Matte sẽ không tạo vùng reveal mong muốn.

## Lỗi thường gặp

Chọn nhầm loại/chiều matte; matte không phủ kín; source quá nhỏ làm vỡ biên; thay đổi timing matte nhưng quên hai shot. Effect wipe trực tiếp trong case study là một cách triển khai khác, không phải bằng chứng đã dùng footage matte.

**Đọc tiếp:** [overlays](../../resources/overlays.md), [compositing](../../foundations/compositing.md), [The Less I Know: các wipe có keyframe](../../case-studies/the-less-i-know-the-better.md).
