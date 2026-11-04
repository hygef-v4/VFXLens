# Script và preset: dependency và phạm vi tác động

## Phân biệt vai trò

- Plugin render tạo hoặc xử lý hình khi host chạy.
- Script/panel thao tác với project, thiết lập workflow hoặc sinh control/expression.
- Preset FFX lưu cấu hình/animation; không bảo đảm có đủ plugin, footage, font hoặc layer được tham chiếu.
- Công cụ tìm effect/snapshot như [FX Console](https://www.videocopilot.net/blog/2016/10/new-workflow-plug-in-fx-console-is-now-available/) hỗ trợ thao tác, không tự là look nhìn thấy trong video.

## Nhận biết trước khi dùng

1. Kiểm tra host: một panel Adobe có thể dành cho Premiere thay vì AE.
2. Kiểm tra dependency: JSX có thể cần thư mục phương trình, icons, plugin hoặc runtime đi kèm.
3. `.jsx` không đảm bảo mã nguồn đọc được: file có thể chứa marker JSXBIN hoặc payload gọi qua `eval`. Chưa đọc được payload thì ghi chưa xác minh, không suy diễn tính năng/an toàn.
4. Với FFX, kiểm tra effect/control, keyframe, expression và đơn vị lưu; chưa có timebase thì không đổi integer thành giây/frame.
5. Nếu script sửa/xóa cấu trúc, thử trên bản làm việc được phép sửa, không trên nguồn học.

## Bài học từ script dọn layer

Một bản Hidden Layer Cleaner 1.0.0.1 đã đọc tĩnh loại một số parent/matte/effect reference khi chọn layer disabled; nút Delete Selected lại xóa mọi layer đang selected. Mã đã đọc không phân tích tham chiếu expression/cross-comp đầy đủ. Đây là giới hạn của bản nguồn đã xem, không kết luận mọi script dọn layer đều giống vậy.

Layer tắt vẫn có thể là nguồn tham chiếu hoặc giữ cấu trúc trước prerender. Không lấy `enabled == false` làm bằng chứng có thể xóa. Chọn layer và xóa layer là hai thao tác cần kiểm tra riêng.

**Case study:** [Chal7z: cấu trúc FFX, time units và scalar storage](../case-studies/chal7z-presets.md), [White Ferrari: layer disabled](../case-studies/white-ferrari.md). **Quy ước:** [bằng chứng](../foundations/evidence-and-validation.md).
