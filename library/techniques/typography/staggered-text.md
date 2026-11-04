# Chữ động trễ từng ký tự

**Mục đích:** cho ký tự/từ/dòng dùng cùng chuyển động ở các thời điểm lệch nhau, thay vì đặt toàn bộ keyframe riêng cho từng chữ. Đây là nguyên lý và quy trình đề xuất; các expression nguồn chưa được chạy để kiểm chứng toàn bộ dependency.

## Cách dựng thử

1. Chọn đơn vị: ký tự, từ hoặc dòng; xác định chiều đi và thứ tự.
2. Dựng chuyển động mẫu của animator/control.
3. Cho mỗi phần tử lấy mẫu animation tại thời điểm trễ theo index. Delay theo giây khác delay theo frame.
4. Nếu thêm dao động tắt dần, kiểm soát amplitude/frequency/decay và thời điểm bắt đầu.
5. Xem chữ đầu, giữa, cuối, khoảng trắng, nhiều dòng và câu tiếng Việt thực tế.

## Ba cách triển khai cần phân biệt

- Text animator/Expression Selector: giữ text editable và hệ selector.
- TextEvo: phụ thuộc control/pseudo-effect và biểu thức liên kết; không copy riêng một dòng expression rồi gọi là recipe đầy đủ.
- TextExploder hoặc cutout: tách thành layer/ảnh riêng để xử lý như collage; không còn cùng cơ chế selector của một text layer.

## Dependency và kiểm chứng

Giữ tên control, chỉ số property, đơn vị delay, dimensions và animator properties. Cosine amplitude cố định khác overshoot lấy vận tốc keyframe. Gán Ease and Wizz có thể thay expression đang có; chọn [công cụ easing/text](../../tools/easing-and-typography.md) theo nhiệm vụ.

**Nguồn:** [Takt Op, mục 5](../../case-studies/takt-op.md#5-chữ-động-trễ-từng-ký-tự), [Standard](../../case-studies/standard.md), [Chal7z](../../case-studies/chal7z-presets.md), [AE Notes](../../case-studies/ae-notes.md). **Resource:** [fonts](../../resources/fonts.md), [cutouts](../../resources/cutouts-and-frames.md).
