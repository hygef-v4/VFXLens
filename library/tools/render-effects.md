# Render effects: chọn theo vấn đề cần giải quyết

| Vấn đề | Nhóm công cụ tham khảo | Trước khi chọn |
| --- | --- | --- |
| Đổi tốc độ và nội suy chuyển động | [Twixtor](https://revisionfx.com/products/twixtor/) | FPS/cadence, curve, occlusion và artifact |
| Thêm motion blur từ hình ảnh | [RSMB](https://revisionfx.com/products/rsmb/) | Chuyển động nguồn, biên vật thể và thứ tự xử lý |
| Biến dạng bằng map | [Displacer Pro](https://aescripts.com/displacer-pro/) | Map/channel, lượng biến dạng, biên và version |
| Reveal lan trong biên layer | [AutoFill](https://aescripts.com/autofill/) | Alpha/biên nguồn, điểm xuất phát và timing |
| Glow, bokeh, màu, shake | Effect tích hợp hoặc plugin phù hợp | MatchName, đơn vị, effect order và input |

Đây là bản đồ nhiệm vụ, không phải khuyến nghị mua/cài. Twixtor và RSMB xử lý hai vấn đề khác nhau; có retime không tự chứng minh có speed ramp. Nhiều hiệu ứng có cách làm bằng công cụ tích hợp, nhưng chưa bảo đảm kết quả giống một plugin cụ thể.

## Đọc version và matchName

Tên hiển thị, matchName trong project, nhãn folder và version binary là các nguồn khác nhau. Tài liệu sản phẩm hiện tại có thể mô tả chức năng/fix chưa có ở bản cũ. Changelog Displacer Pro có bản sửa scale/anti-aliasing; cần đối chiếu đúng phiên bản trước khi so kết quả, không suy ra từ tên folder.

Không xác nhận plugin từ hình video. Với project, ghi đúng instance, enabled, parameter tree và plugin version nếu đọc được. Classifier chỉ là đầu mối khi chưa xác minh taxonomy.

**Kỹ thuật:** [retime](../techniques/retiming/speed-ramp.md), [displacement](../techniques/transitions/chromatic-displacement.md), [glow/màu/bokeh](../techniques/lighting-and-color/glow-color-bokeh.md). **Nguồn:** [Takt Op](../case-studies/takt-op.md), [White Ferrari](../case-studies/white-ferrari.md).
