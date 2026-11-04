# Bằng chứng và kiểm chứng

Thư viện ghi cả dữ liệu đọc được và ý tưởng dựng thử. Hai loại có giá trị khác nhau, cần được gắn nhãn rõ.

| Trạng thái | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| `observed` | Đọc/đo trực tiếp | Keyframe Amplitude lưu trong AEP; alpha đo từ ảnh |
| `inferred` | Suy luận có căn cứ | Đề xuất dùng envelope giảm để nhấn beat |
| `unavailable` | Nguồn không cung cấp | Giá trị expression runtime khi chỉ đọc offline |
| `unsupported` | Công cụ chưa hỗ trợ | Channel/payload chưa giải mã được |
| `error` | Thất bại khi đọc | ffprobe timeout; timestamp dự phòng chưa phải PTS gốc |

## Một recipe có nguồn phải ghi gì?

Nguồn và ngày phân tích; comp/layer/property hoặc timestamp/frame; effect order; đơn vị; keyframe/expression/dependency; trạng thái enabled; điều được quan sát; cách áp dụng được đề xuất; kiểm chứng còn thiếu. Hash giúp nhận diện đúng nguồn nhưng không chứng minh chất lượng hoặc quyền phân phối.

Trong case study, các mã `evidence:` nhận diện nguồn riêng mà người phân tích giữ. Thư viện không phân phối các payload đó; chỉ dẫn này không phải xác nhận người đọc đã có quyền truy cập nguồn. Nếu tái lập, ghi locator và bằng chứng của lần thử mới thay vì khẳng định đã kiểm tra lại nguồn cũ.

## Khi nào nâng mức kiểm chứng?

1. Đọc đủ nguồn và dependency, xác định timebase/đường render thực tế.
2. Dựng trên bản làm việc được phép sửa, giữ nguyên nguồn.
3. Bật/tắt hoặc thay đổi riêng bước cần kiểm chứng và so sánh preview.
4. Ghi kết quả, điều kiện, artifact và trường hợp thất bại; đính kèm bằng chứng được phép chia sẻ.

Nhìn video không chứng minh tên plugin hoặc setting. Layer có effect không chứng minh effect đang đóng góp: layer có thể tắt, ngoài in/out, bị matte hoặc được thay bằng prerender. Đọc expression tĩnh không đồng nghĩa đã chạy hợp lệ trong host.

**Đọc tiếp:** [mẫu technique](../templates/technique.md), [mẫu case study](../templates/case-study.md).
