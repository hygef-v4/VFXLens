# Chal7z Preset — học từ cấu trúc FFX

Đọc ngày 2026-11-04, bổ sung cho [sổ tay các dạng edit](../README.md). Đây là kiểm kê nhị phân và các ví dụ có nguồn, chưa phải kết quả áp preset/render trong AE.

## Nguồn, phạm vi và độ tin cậy

- Nguồn: `evidence:chal7z-presets-01`.
- SHA-256 archive: `909dc286a54e363f2814dc1f8d446bd7d0dc0bd773f392372b1d6b9a0f758732`.
- Chỉ giải nén FFX vào `evidence:chal7z-presets-02`, giữ nguyên archive gốc; không cài preset, không chạy script/plugin nhúng hoặc mở AE.
- Kiểm kê 673 file, khoảng 130.3 MB giải nén; 654 SHA-256 khác nhau, tức 19 file dư so với số nội dung byte độc nhất. Không coi tên khác nhau là 673 kỹ thuật khác nhau.
- Tất cả 673 file có root `RIFX:FaFX`; quét cấu trúc và đọc 169.848 khối property bằng thư viện `py_aep`, không báo lỗi cấu trúc/property trong lượt này. Điều đó không chứng minh mọi property, opaque payload hoặc kiểu dữ liệu đã được diễn giải đầy đủ và đúng như AE.
- 280 preset có ít nhất một danh sách keyframe đọc được. Đọc được 92 expression source trong 44 preset; chưa xác định tất cả expression có bật hoặc sẽ chạy hợp lệ trong host, và chưa thực thi expression nào.
- **Keyframe time_units chưa đổi sang giây/frame:** host FPS, timebase và cách đặt preset vào playhead chưa được xác lập. Các mốc integer dưới đây là đơn vị lưu, không phải millisecond hoặc số frame.
- **Static storage values không mặc định là AE UI values:** có thể chứa padding, tọa độ chuẩn hóa, enum hoặc quy ước riêng của plugin. Không copy cả mảng vào UI.
- **Property path là tham chiếu:** chưa xác nhận trạng thái bật từng effect hay thứ tự compositing sau khi áp vào layer. Danh sách dưới đây ghi đường tham chiếu theo thứ tự xuất hiện trong file, không khẳng định là stack đang render.

## Bản đồ thư viện

| Nhóm thư mục | Số file FFX |
| --- | ---: |
| General / CC | 139 |
| General / One Frame | 132 |
| General / Shake | 120 |
| General / STYLES | 59 |
| General / Text | 52 |
| General / Distort | 18 |
| General / Optical Flare | 18 |
| General / Particular | 18 |
| General / VFX | 15 |
| General / Audio | 12 |
| General / Fractal Noise | 8 |
| General / Transition&Dissolve | 8 |
| General / Twixtor | 8 |
| General / Flicker | 7 |
| General / Time | 5 |
| General / Vhs - Crt | 5 |
| General / Noise | 3 |
| General / 3d | 2 |
| General / Glitch | 2 |
| General / Pixel | 2 |
| Valorant / !Random, Effects, Extra | 40 |

Nhóm và tên file là nhãn người đóng gói. Tên “One Frame”, “4K”, “Bouncy” hay “Typing” chưa chứng minh thời lượng, khả năng upscale hoặc chuyển động thật.

## 1. Shake giảm biên độ và dissolve-shake

### BEETLX SHAKE 6 BOUNCY

**Nguồn:** `General/Shake/BEETLX SHAKE 6 BOUNCY.FFX`.

Đường tham chiếu `ADBE Effect Parade / S_Shake`. Property `S_Shake-0050`, tên `Amplitude`, có keys:

| Time units lưu | Giá trị đọc được | Nội suy in/out |
| ---: | ---: | --- |
| 0 | 1.7 | BEZIER / BEZIER |
| 22527 | 0 | BEZIER / BEZIER |

**Điều rút ra:** preset lưu đường bao rung giảm về 0. Tên Bouncy chưa đủ chứng minh camera nảy hoặc amplitude overshoot; phải đọc frequency, trục, easing speed/influence và preview.

### D2 DISSOLVE 1

**Nguồn:** `General/Transition&Dissolve/D2 DISSOLVE 1.FFX`.

Tham chiếu `S_DissolveShake`; Amplitude `2` tại time units `7000`, về `0` tại `18000`, BEZIER cả hai phía. Đây là ví dụ tái sử dụng envelope giảm cường độ trong loại effect khác; chưa kết luận Wipe/Dissolve Percent cũng chạy theo đường này.

**Áp dụng suy luận:** tách envelope cường độ khỏi cấu hình rung tĩnh. Cần chọn clip, FPS và thời lượng đích trước khi retime; không gán 22527 hoặc 11000 thành giây/frame.

## 2. Transition sáng và mờ có hai đường đồng bộ

**Nguồn:** `General/Transition&Dissolve/LIGHT BLUR TRANSITION.FFX`.

Các path tham chiếu Bokeh (`CROSSPHERE_Bokeh`) rồi `S_Gamma`.

| Property | Time units 362400 | Time units 369600 | Nội suy |
| --- | ---: | ---: | --- |
| Bokeh / Blur Radius (`-0003`) | 0 | 29 | LINEAR |
| S_Gamma / Gamma (`-0050`) | 1 | 1.5 | LINEAR |

**Điều rút ra:** hai tham số bắt đầu/kết thúc tại cùng mốc lưu, chênh `7200` units. Có thể thử phối hợp một envelope mờ và một envelope gamma để tạo transition, nhưng chưa thấy bằng chứng đây là một chu kỳ “mờ rồi rõ” hoàn chỉnh: hai đường đã đọc chỉ tăng.

**Còn thiếu:** trạng thái effect, định nghĩa plugin/version, timebase, thứ tự áp thực tế và đoạn nối sau đó. Gamma khác Exposure; không đổi tên tham số thành EV hoặc mặc định tương đương flash exposure.

## 3. Chữ smooth: trễ theo giây, dao động cosine tắt dần

**Nguồn:** `General/Text/Text Animation/BEETLX TEXT SMOOTH ANIMATION.FFX`.

Property `ADBE Text Expressible Amount` chứa source:

```javascript
delay = .05;
myDelay = delay*textIndex;
t = (time - inPoint) - myDelay;
if (t >= 0){
  freq = 2;
  amplitude = 80;
  decay = 8.0;
  s = amplitude*Math.cos(freq*t*2*Math.PI)/Math.exp(decay*t);
  [s,s]
}else{
  value
}
```

Đây là **trích source để đọc**, không phải expression đã chạy thử hoặc bảo đảm dán vào mọi selector đều hợp lệ. Property metadata ghi dimensions=3 trong khi nhánh expression trả hai phần tử; cần kiểm tra cách AE chấp nhận/coerce ở selector trước khi tái dùng.

Animator Position có dữ liệu đầu `[0,-56,0]`. Scale đầu `[100,100,100]`, Rotation đầu `0`. Amount điều tiết animator, không trực tiếp là tọa độ/scale cuối.

**Điều rút ra:** delay `.05` là giây cho mỗi textIndex, khác Standard dùng một frame mỗi textIndex. Ở 24 fps, `.05s` tương đương 1.2 khoảng frame; không gọi đây là delay cố định một frame. Theo source, ký tự đầu có delay `.05s` vì textIndex bắt đầu từ 1.

`freq=2`, `amplitude=80`, `decay=8` mô tả cosine giảm dần theo hàm mũ sau mốc trễ. Đây là diễn giải công thức tĩnh, chưa phải đánh giá cảm giác chuyển động.

### Preset Typing: chưa kết luận cơ chế

`BEETLX TEXT TYPING PRESET.FFX` có path Text Document, Text Animator và các control Slider/Checkbox/Color. Bộ đọc hiện không lấy được expression/keyframe trong các property đã quét của file này. Vì vậy chỉ lưu cấu trúc phụ thuộc; không kết luận typing bằng Source Text, selector hay script dựa trên tên file.

## 4. Trail và wide time khác posterize thời gian

### TIMETRAIL

**Nguồn:** `General/Time/TIMETRAIL.FFX`, tham chiếu `S_Trails`.

Các scalar storage đầu: Prev Brightness khoảng `0.9199877929687499`, New Opacity `1`, Blur Amount `2`. Chưa lấy được keyframe ở các property đã đọc của file này.

**Suy luận:** có thể thử trail dựa trên contribution cũ/mới và blur; chưa xác nhận độ dài vệt, cách reset lịch sử, frame sampling, feedback hay artifact ở cut. Không gọi đây là motion blur shutter vật lý.

### SHUTTER_WIDETIME

**Nguồn:** `General/Time/SHUTTER_WIDETIME.FFX`.

Tham chiếu `CC Wide Time`, `ADBE Posterize`, `ADBE Shift Channels`. Dữ liệu scalar đầu:

- Wide Time / Forward Steps `6`, Backward Steps `6`, Native Motion Blur enum `2`.
- Posterize / Level `12`.
- Shift Channels / Take Red From enum `10`, Green `10`, Blue `4`; tên enum chưa giải mã.

**Bài học quan trọng:** `ADBE Posterize` ở đây là effect khác `ADBE Posterize Time`; Level 12 không phải 12 fps. Không suy từ thư mục Time hoặc tên SHUTTER thành cơ chế thực tế.

## 5. One Frame: offset tĩnh không tự tạo thời lượng một frame

**Nguồn:** `General/One Frame/BASIC OFFSET.FFX`.

Tham chiếu `ADBE Offset`. `Shift Center To` có dimensions=2, hai scalar storage đầu `[0.5,1.0018518518518518]`; Blend With Original đầu `0`. Không có keyframe được đọc trong file này.

**Điều rút ra:** folder One Frame có thể là ý định dùng preset trong một layer ngắn, không phải preset tự cắt layer còn một frame. Tọa độ lưu có thể chuẩn hóa theo kích thước layer; không hướng dẫn nhập trực tiếp `0.5 px`/`1.00185 px`.

## 6. Tham chiếu effect và giới hạn tổng hợp

Ví dụ số file có path tham chiếu effect: Curves `91`, PEDG `83`, Looks `74`, S_Shake `71`, S_Flicker `44`, S_DissolveShake `36`, Particular `23`. Đây là số file có tham chiếu, không phải số effect instance đang bật hoặc số máy đã cài plugin.

Chưa học sâu từng preset CC/Particular/Element/Optical Flare hoặc render biến thể; bộ 673 file được **kiểm kê cấu trúc**, còn các recipe trên được xem chi tiết. Opaque/plugin data, script/control dependencies và khả năng render cần kiểm tra theo từng preset được chọn.

## Dữ liệu để học tiếp

Trong `evidence:chal7z-presets-03`:

- `archive-inventory.json`: danh sách archive và hash gốc.
- `preset-catalogue.json`: 673 file, property paths, vị trí byte, scalar storage, raw keyframe time_units, interpolation và expression source đọc được.
- `catalogue-summary.json`: số lượng theo thuộc tính và số file tham chiếu effect.
- `selected-recipes.json`: tám ví dụ đã đọc chi tiết, tên tương đối giúp tìm file.
- `inspect_ffx.py`: bộ kiểm kê local dùng lại thư viện py_aep, có self-check chunk hợp lệ/truncated; không phải tính năng CLI VFXLens được hỗ trợ chính thức.

Các file JSON/media/preset gốc giữ local trong outputs. Khi học thêm, chọn dạng edit và preset cụ thể, xác định dependencies trước rồi mới dựng thử trên bản làm việc mới được ủy quyền. Không khẳng định preview đẹp/đúng khi chưa áp và xem kết quả.

## Đọc nguồn và tái sử dụng

Bài này giữ số đo/tham chiếu từ lần phân tích đã ghi nhận; project, ảnh bằng chứng và báo cáo riêng không được phân phối cùng thư viện. Các mã `evidence:` là định danh nguồn, không phải file cần có để đọc bài. Người giữ nguồn tra chúng trong hồ sơ local; người đóng góp khác phải ghi nguồn và mức kiểm chứng của chính mình. Xem [quy ước bằng chứng](../foundations/evidence-and-validation.md).
