# Transition bằng chroma, invert và displacement

**Mục đích:** tạo biến dạng và đổi trạng thái màu quanh điểm nối shot. Các bước dưới đây là đề xuất; ví dụ đã đọc tĩnh nằm ở [Takt Op, mục 1](../../case-studies/takt-op.md#1-transition-chroma-invert-và-displacement).

## Cách dựng thử

1. Chọn hướng chuyển cảnh và thời điểm cần khôi phục hình ổn định.
2. Xác định nguồn map, center/trục và cách xử lý biên. Dựng envelope displacement trước.
3. Thử blur để nối hình chuyển động; nếu cần nhấn ngắt, thêm invert ngắn theo timing đã chọn.
4. Kiểm tra màu/sáng cuối cùng và xem riêng từng bước trong stack.

## Điều khiển và dependency

Lượng displacement, map/channel, blur amount, invert luma/chroma, easing và thứ tự effect đều ảnh hưởng kết quả. HOLD đổi trạng thái khác với keyframe liên tục. Plugin chroma và RGB lệch thời gian không phải cùng cơ chế.

## Kiểm chứng và lỗi

Kiểm tra cut, biên đen, hình phản chiếu, vùng mặt/chữ và trạng thái cuối. Không copy lượng displacement theo pixel sang resolution khác mà chưa cân lại. Giữ thứ tự nguồn làm mốc so sánh; thứ tự thử hiệu ứng không tự thay thế thứ tự render.

**Đối chiếu:** [Standard: warp và RGB lệch frame](../../case-studies/standard.md), [AE Notes: nhóm warp/scatter](../../case-studies/ae-notes.md). **Resource:** [overlays](../../resources/overlays.md). **Công cụ:** [render effects](../../tools/render-effects.md).
