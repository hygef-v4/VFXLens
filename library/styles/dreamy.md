# Dreamy / atmospheric

**Dấu hiệu định hướng:** ánh sáng mềm, khí quyển, chiều sâu và nhịp chuyển động tạo cảm giác nhẹ. Không bắt buộc dùng glow mạnh hoặc làm mờ toàn khung.

## Chuỗi dựng đề xuất

1. Chọn shot có chủ thể và vùng sáng rõ.
2. Kiểm soát [glow, màu và bokeh](../techniques/lighting-and-color/glow-color-bokeh.md) riêng từng bước.
3. Thêm [leak/fog/particle](../resources/overlays.md) theo nguồn sáng và bố cục.
4. Nếu có vật thể alpha, giữ contour/màu, thêm occlusion hoặc chuyển động theo shot khi cần.
5. Kiểm tra chữ/mắt, highlight và vùng tối; cân SFX/ambience trong ngữ cảnh.

## Lỗi dễ gặp

Fog làm hình bạc, glow mất chi tiết, bokeh che mặt, vật thể alpha quá sắc so với nền, mọi lớp chạy không cùng nhịp. Tắt từng lớp để đánh giá đóng góp; giảm số lớp nếu shot đã truyền đạt đủ.

**Case study:** [White Ferrari](../case-studies/white-ferrari.md) ghi cấu trúc overlay/blur; [Takt Op](../case-studies/takt-op.md) có ví dụ glow nhưng một số key nằm ngoài layer in/out. Chưa dùng các case này để khẳng định toàn bộ video thuộc một style duy nhất.
