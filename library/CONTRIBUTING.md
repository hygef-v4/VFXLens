# Bổ sung kiến thức

## Đặt bài đúng nơi

- `foundations`: nguyên lý dùng lại ở nhiều kỹ thuật.
- `techniques`: một nhiệm vụ thực hiện được; liên kết tới bằng chứng thay vì chép bảng nguồn.
- `styles`: đặc điểm và cách phối bài kỹ thuật/resource.
- `resources`: cách nhận biết/chọn/ghép một loại asset, không phụ thuộc pack cá nhân.
- `tools`: công cụ giải quyết nhiệm vụ gì, dependency, version và giới hạn.
- `case-studies`: thông số/vị trí nguồn và điều đã kiểm chứng.

Một chủ đề có một bài chính; dùng liên kết cho các style khác nhau. Chỉ tạo thư mục khi có nội dung. Dùng tên file tiếng Anh dạng `kebab-case`, nội dung tiếng Việt trong giai đoạn hiện tại.

## Một bài có ích phải chứa

Mục đích, dấu hiệu nhận biết/đầu vào, cách thực hiện, điều khiển và đơn vị, dependency, lỗi thường gặp, mức kiểm chứng và nguồn. Chọn [mẫu](templates/README.md) tương ứng. Nếu chưa có render so sánh, ghi quy trình là đề xuất.

## Phần công khai và phần riêng

Giữ đường dẫn máy, inventory, báo cáo gốc và ảnh/media riêng trong vùng local bị Git bỏ qua. Trong bài công khai dùng định danh nguồn và locator comp/layer/property có ý nghĩa; không tạo link bắt người đọc phải có file private. Giữ hash để nhận diện nguồn khi phù hợp, nhưng hash không chứng minh quyền phân phối.

Không đưa plugin, font, preset, project hoặc media của bên thứ ba vào thư viện khi chưa xác nhận quyền chia sẻ. Thư viện hiện không tự cấp giấy phép cho các nguồn đó; giấy phép của phần tài liệu cần được quyết định trước khi phát hành chính thức.

## Kiểm tra trước khi gửi thay đổi

- Đi từ mục lục tới được bài mới, và liên kết file/heading đều hợp lệ.
- Không có đường dẫn máy, inventory hoặc liên kết tới báo cáo private trong phần công khai.
- Giá trị ví dụ có nguồn, đơn vị/timebase và giới hạn; không bị biến thành mặc định chung.
- Phân biệt `observed`, `inferred`, `unavailable`, `unsupported`, `error`.
- Không lặp lại bài đã có; style/tool/resource dẫn tới bài phù hợp.

Không cần chạy analyzer hoặc mở project chỉ để sửa tài liệu. Nếu thay đổi recipe, ghi đúng các bước kiểm chứng thực tế đã làm, bao gồm những gì chưa làm.

[Về thư viện](README.md)
