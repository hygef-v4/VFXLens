# Compositing: alpha, blend và matte

**Mục đích:** chọn cách ghép theo dữ liệu của asset và vai trò hình ảnh.

## Ba cơ chế cần phân biệt

- **Alpha** mô tả độ trong suốt. Một file PNG/MOV có thể có hoặc không có alpha; cần kiểm tra channel và pixel.
- **Blend mode** kết hợp màu giữa các layer. Thử Screen/Add cho ánh sáng nền đen; Multiply cho nét tối nền sáng; chọn bằng preview, không theo tên pack.
- **Matte** điều khiển vùng hiện của layer khác. Luma Matte dùng độ sáng, Alpha Matte dùng alpha; dùng đảo matte khi muốn đổi vùng hiện/ẩn.

Alpha straight và premultiplied cần được diễn giải phù hợp. Nếu biên vật thể có viền đen/trắng, kiểm tra Interpret Footage trước khi key hoặc xóa mép. [Adobe: alpha và matte](https://helpx.adobe.com/after-effects/desktop/work-with-transparency-and-compositing/work-with-alpha-channels-and-masks/alpha-channels-masks-mattes.html).

Screen không thay thế alpha cho vật thể màu tối cần giữ nguyên. Add có thể tăng sáng mạnh; kiểm tra highlight và vùng da. Texture nền xám/sáng/tối cần blend khác nhau. [Adobe: blending modes](https://helpx.adobe.com/after-effects/desktop/work-with-layers/work-with-layer-blending-modes/blending-modes-layer-styles.html).

## Thứ tự và biên hình

Transform, effect, matte và precomp tương tác với nhau; ghi lại thứ tự thực tế của ví dụ thay vì chỉ liệt kê tên plugin. Khi shake/zoom/warp, kiểm tra có lộ biên không và mở rộng biên trước bước làm lộ biên nếu phù hợp. Motion Tile/Mirror Edges là một phương án có thể tạo phản chiếu không mong muốn.

**Thực hành kiểm tra:** dùng nền sáng và tối để xem contour; bật/tắt từng lớp; xem cả frame ổn định lẫn đỉnh chuyển động. Không giữ một layer chỉ vì nó có effect nổi tiếng, cũng không xóa layer disabled khi chưa kiểm tra dependency.

**Đọc tiếp:** [overlays](../resources/overlays.md), [cutouts và frame](../resources/cutouts-and-frames.md), [matte transition](../techniques/transitions/matte-reveal.md).
