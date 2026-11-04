# Công cụ easing và typography

## Chọn theo thao tác

| Nhiệm vụ | Công cụ tham khảo | Dependency/giới hạn cần kiểm tra |
| --- | --- | --- |
| Thiết kế và tái dùng curve easing | [Flow](https://aescripts.com/flow/) | Curve và property đích; phiên bản hỗ trợ |
| Copy easing riêng với giá trị | [EaseCopy](https://aescripts.com/easecopy/) | Keyframe đích và chế độ copy |
| Nội suy bằng expression | [Ease and Wizz](https://aescripts.com/ease-and-wizz/) | File phương trình, keyframe, expression cũ |
| Delay text theo ký tự/từ/dòng | [TextEvo](https://aescripts.com/textevo/) | Control/pseudo-effect và text animator liên kết |
| Tách text thành layer riêng | [TextExploder](https://aescripts.com/textexploder/) | Font/style, bố cục và host/version |

Flow chỉnh curve, EaseCopy sao chép easing, Ease and Wizz gắn expression: chọn theo loại thao tác, không coi là ba preset look tương đương. Có thể dùng keyframe/Graph Editor hoặc text animator của AE nếu đáp ứng mục đích; xem [timing](../foundations/timing-and-easing.md) và [chữ trễ](../techniques/typography/staggered-text.md).

## Điều học từ nguồn script

Một bản Ease and Wizz 2.6.1 đã đọc tĩnh nạp phương trình từ `easingExpressions`, rồi gán expression vào property có ít nhất hai key và cho phép expression. Điều đó cho thấy JSX rời có thể thiếu dependency, và thao tác áp expression có thể thay expression trước đó. Không khẳng định mọi phiên bản đều giống mã đã đọc; chưa thực thi bản nguồn trong lần phân tích.

TextEvo selector và TextExploder layer rời phục vụ hai cấu trúc khác nhau. Nếu chỉ cần thay đổi thời gian lấy mẫu của từng ký tự thì giữ animator/control; nếu cần parent/shadow độc lập từng mảnh thì cân nhắc layer rời.

**Nguồn project:** [Standard](../case-studies/standard.md), [Takt Op](../case-studies/takt-op.md), [AE Notes](../case-studies/ae-notes.md). Các tài liệu hãng liên kết bên trên mô tả sản phẩm, chưa xác thực bộ cài của người đọc.
