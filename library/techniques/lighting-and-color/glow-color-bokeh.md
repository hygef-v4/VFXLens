# Glow, màu và bokeh

**Mục đích:** điều khiển độ phát sáng, ánh màu và độ mờ như các thành phần riêng. Chưa có bộ giá trị dùng chung; đọc [Takt Op, mục 4](../../case-studies/takt-op.md#4-glow-màu-và-bokeh) để thấy giới hạn của keyframe nằm ngoài layer in/out.

## Cách dựng thử

1. Đánh giá độ sáng/màu footage đầu vào và vùng cần giữ chi tiết.
2. Thử glow riêng, kiểm tra vùng được chọn, bán kính và lượng sáng theo công cụ đang dùng.
3. Thêm ánh màu/remap và bokeh/blur riêng; so sánh thứ tự nếu hiệu quả khác nhau.
4. Nếu cần pulse theo action, animate envelope có timing rõ rồi kiểm tra nó nằm trong đoạn layer thực sự hiện.
5. Xem trước/sau trên cùng frame, chú ý da, vùng trắng, chữ và contour.

## Phân biệt

Bokeh overlay là asset đặt lên hình; bokeh/DOF effect xử lý hình theo thiết lập của nó. Glow không thay thế exposure, blur không tự tạo depth map. Bit depth/working space và highlight đầu vào có thể thay đổi cảm giác; giữ chúng trong hồ sơ kiểm chứng.

**Đối chiếu:** [White Ferrari](../../case-studies/white-ferrari.md), [Chal7z: bokeh và gamma](../../case-studies/chal7z-presets.md). **Ứng dụng:** [dreamy](../../styles/dreamy.md), [overlays](../../resources/overlays.md). **Công cụ:** [render effects](../../tools/render-effects.md).
