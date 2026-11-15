# Đề xuất dùng VFXLens làm skill và workflow sản xuất video

Ngày: 15/11/2026. Đây là **đề xuất ban đầu đã được chấp thuận**, lưu lại trước khi triển khai. Người dùng sau đó yêu cầu cài toàn bộ; xem [hướng dẫn hiện tại](ai-video-requirements.md) và [bản đồ toolchain](full-toolchain.md) để biết cấu hình, kiểm tra và giới hạn sau cài đặt.

## 1. Lựa chọn kiến trúc

Theo yêu cầu dùng chính dự án này, giữ VFXLens làm nguồn chung cho Claude Code và Codex: thư viện kiến thức, công cụ phân tích và workflow tạo video. Không cần repo studio thứ hai ở giai đoạn đầu.

Hai cách tổ chức đã cân nhắc:

| Cách | Đánh đổi | Đề xuất |
| --- | --- | --- |
| Một repo VFXLens, tách môi trường phân tích và sản xuất | Chia sẻ kiến thức và workflow trực tiếp; phải giữ ranh giới dependency và dữ liệu rõ ràng | **Chọn cho đề xuất này**, phù hợp yêu cầu hiện tại |
| Repo studio riêng, VFXLens chỉ cung cấp phân tích | Độc lập vòng phát hành, nhưng cần đồng bộ kiến thức và đường dẫn giữa hai repo | Chỉ xem lại khi studio cần phát hành độc lập |

Đây là lựa chọn đề xuất của người thực hiện, chưa phải xác nhận rằng các thành phần đã tích hợp hoặc chạy được.

## 2. Cấu trúc nên bổ sung

```text
VFXLens/
  AGENTS.md                    Quy tắc chung và bảo vệ dữ liệu gốc
  CLAUDE.md                    Chỉ dẫn ngắn tới quy tắc và skill chung
  skills/
    vfxlens/
      SKILL.md                 Cửa vào: học, phân tích, tạo video
  workflows/
    study-reference.md         Đọc tài liệu/reference, ghi nguồn và giới hạn
    create-video.md            Brief -> storyboard -> sản xuất -> review -> MP4
  library/                     Kiến thức chuẩn; dùng cấu trúc đang có
  src/vfx_engine/               CLI phân tích đang có
  studio/                      Dự án Remotion, package.json và lockfile riêng
  local/productions/<slug>/     Tài liệu từng video, asset riêng, .blend và bản render
  outputs/                     Kết quả phân tích đang có
```

`skills/vfxlens/` là bản nguồn do repo quản lý, nằm ngoài thư mục khám phá tự động để tránh đăng ký cùng một skill cả ở cấp repo và cấp tài khoản. Liên kết skill này vào hai thư mục cá nhân:

- Codex: `~/.agents/skills/vfxlens/`.
- Claude Code: `~/.claude/skills/vfxlens/`.

Cả hai đọc cùng một bản. Skill phải xác định repo từ vị trí thật của chính nó sau khi giải liên kết, không giả định thư mục làm việc hiện tại là VFXLens. Nếu Windows không tạo được liên kết, dùng bản sao được đồng bộ từ nguồn repo và kiểm tra phiên bản khi cập nhật; không sửa độc lập hai bản.

Khi gọi skill từ một dự án khác, entrypoint phải chỉ rõ nơi đọc workflow và hướng dẫn Remotion trong `studio/`; không trông chờ agent tự khám phá skill của một repo nằm ngoài thư mục làm việc. Đầu ra vẫn đi vào thư mục sản xuất đã chỉ định cho yêu cầu hiện tại.

Các đường dẫn trên dành cho agent chạy local. Chạy trên cloud/máy khác cần clone và cài lại; liên kết tới ổ F của máy này không tự hoạt động ở môi trường khác. Nguồn: [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills), [Claude Code skill locations và symlink](https://code.claude.com/docs/en/skills#choose-where-skills-load).

`CLAUDE.md` chỉ dẫn tới `AGENTS.md` và skill chung; không chép lại toàn bộ quy tắc. Cần bổ sung mô tả phạm vi tạo video vào hướng dẫn repo khi triển khai. Quy tắc read-only vẫn áp dụng với dữ liệu gốc; mã, scene và video mới được tạo trong thư mục sản xuất riêng.

## 3. Một skill, ba công việc

| Người dùng yêu cầu | Skill thực hiện | Kết quả cần có |
| --- | --- | --- |
| Đọc PDF, bài viết, tài liệu hướng dẫn | Đọc nội dung và hình liên quan, đối chiếu nguồn chính, rút ra kỹ thuật áp dụng được | Ghi chú có nguồn và giới hạn; chỉ đưa kiến thức tái sử dụng vào đúng mục `library/` |
| Học một video hoặc project AE | Gọi CLI `analyze-video` / `analyze-project` đang có, đọc báo cáo, xem frame và liên hệ thư viện | Reference breakdown, bằng chứng đo được, suy luận và dữ liệu còn thiếu |
| Tạo video từ brief hoặc bài học | Chọn công cụ theo nội dung, lập storyboard theo voice và frame, tạo asset/scene/code, preview, sửa, xuất khi người dùng yêu cầu | Nguồn chỉnh sửa được, tài liệu sản xuất và MP4 đã kiểm tra nếu được yêu cầu xuất |

Không thêm ngay một CLI dựng video mới. Agent điều phối các công cụ hiện có theo workflow. `uv run vfx ...` tiếp tục chỉ cung cấp các lệnh phân tích hiện tại.

Tái sử dụng nội dung phù hợp của skill cá nhân `motion-design-workflow` và `ae-edit-recipes`: đưa phần cần dùng độc lập vào nguồn repo khi triển khai, giữ một bản chuẩn và thay các bản cũ bằng chỉ dẫn/liên kết sau khi kiểm tra caller. Không làm skill mới phụ thuộc ngầm vào đường dẫn cá nhân trên máy hiện tại. Bộ tài liệu brief/style/assets/storyboard/motion/sound/delivery được giữ khi công việc thực sự cần, không sinh mẫu trống để coi như đã hoàn tất.

## 4. Bộ cài tối thiểu

| Thành phần | Vị trí / cách dùng | Khi triển khai |
| --- | --- | --- |
| VFXLens analyzer | `.venv` gốc, `pyproject.toml` và `uv.lock` hiện có | Dùng lại; chạy doctor và kiểm tra CLI |
| Skill `vfxlens` | Bản nguồn trong repo, hai liên kết cá nhân cho Claude/Codex | Thêm mới; kiểm tra phát hiện từ cả trong repo và một thư mục khác |
| Remotion Skills | Skill của dự án `studio/`, chọn cả hai agent qua Skills CLI | Cài theo dự án, dùng liên kết, lưu lockfile skill; không cài trùng global cùng tên |
| Remotion runtime | `studio/node_modules/`, phiên bản khóa trong lockfile Node | Cài khi triển khai video; xác nhận phiên bản Node được hỗ trợ |
| Blender + MCP | Blender cài một lần trên máy; mỗi client cấu hình kết nối tới addon | Xác minh bản cài trước; hiện kiểm tra MCP chưa kết nối được |
| Whisper local | Môi trường Python riêng của phần voice, tách khỏi `.venv` analyzer | Chỉ cài khi cần caption theo voice; chọn Python tương thích PyTorch/Whisper |
| FFmpeg / ffprobe | Dùng bản đang có trong PATH | Kiểm tra encode, metadata và xuất contact sheet |
| LottieFiles motion-design | Tùy chọn theo dự án nếu cần bổ sung motion principles | Bổ trợ, không phải engine diễn hoạt nhân vật |

Từ thư mục `studio/`, lệnh tham khảo để cài skill cho cả hai agent là:

```powershell
npx skills add remotion-dev/skills --skill remotion-best-practices -a codex -a claude-code
```

Lệnh này chỉ cài hướng dẫn cho agent, chưa cài Remotion runtime. Khi cài, kiểm tra đường dẫn đích và chọn phương thức liên kết. Nếu nguồn repo và thư mục đích trùng nhau thì không tiếp tục ghi đè. Nguồn: [Skills CLI scopes, agents và installation methods](https://github.com/vercel-labs/skills/blob/main/docs/commands.md), [Remotion Skills](https://github.com/remotion-dev/skills).

Chưa cần cài Three.js, Jolt, path tracer, particles, ComfyUI, earshot hay TTS ở lượt đầu. Chỉ thêm khi một shot cụ thể cần. Với phim 2D/motion graphic, Remotion là đường đầu tiên; với nhân vật phẳng trong set 3D như PDF, bổ sung Blender. Giọng người dùng thu là đầu vào mặc định cho narration; TTS tiếng Việt cần được chọn và thử riêng.

Không coi mọi thứ là miễn phí vô điều kiện: xem [Remotion license/pricing](https://www.remotion.dev/docs/license/pricing). Không tự gọi dịch vụ trả phí hoặc tải model nặng trước khi thực sự cần và được cấu hình phù hợp.

## 5. Workflow thực hiện video

1. Nhận brief, tài liệu và asset; kiểm kê nguồn thật và đầu vào còn thiếu.
2. Đọc hoặc phân tích reference. Giữ `observed`, `inferred`, `unavailable`, `unsupported`, `error` đúng nghĩa của repo; quyết định sáng tạo được ghi là quyết định cho bản mới.
3. Chốt định dạng, nội dung, storyboard và voice. Chốt thời điểm từ bản voice thật; không áp số từ tiếng Anh vào tiếng Việt.
4. Làm still và một đoạn chuyển động ngắn. Nếu 2.5D: block set, light, dress, nhân vật phẳng, contact shadow, biểu cảm và camera theo shot.
5. Ghép video, caption và mix; dùng chung event/frame giữa hình và âm thanh. Chốt quy ước frame giữa Blender và Remotion.
6. Xem contact sheet, preview có chuyển động, chữ ở kích thước điện thoại và nghe bản mix; sửa lỗi theo shot.
7. Khi yêu cầu bao gồm MP4, xuất và kiểm tra file thật bằng ffprobe, frame quanh cut/hit và nghe âm thanh; ghi rõ phần nào chưa kiểm tra được.

Tài liệu riêng của tập được lưu trong `local/productions/<slug>/`. Dùng lại `studio/` để render, không tạo một bộ dependency cho mỗi AI hoặc mỗi lần sửa. Asset được đưa vào vùng media được ignore khi renderer cần truy cập; không commit media riêng tư, model hoặc cache vào Git. Cần mở rộng `.gitignore` cho `node_modules`, vùng media và render cache khi triển khai. Mã và lockfile của studio được quản lý bằng Git.

## 6. Thứ tự triển khai và tiêu chí hoàn tất

1. **Skill và tài liệu:** thêm skill, hai workflow, hướng dẫn cài và liên kết hai agent; cập nhật README và chỉ dẫn repo. Đọc và kiểm tra lại mô tả trigger để không kích hoạt khi người dùng yêu cầu việc không liên quan.
2. **Môi trường tạo video:** thêm studio Remotion, kiểm tra Blender/MCP nếu chọn 2.5D, giữ môi trường analyzer độc lập. Chỉ tạo môi trường voice khi cần.
3. **Kiểm chứng:** dùng cùng skill từ Claude và Codex để đọc một tài liệu; chạy một phân tích reference; tạo và xuất một đoạn 5–10 giây với caption và âm thanh. Một agent bàn giao được cho agent kia qua tài liệu, file nguồn và lệnh đã ghi.

Hoàn tất chỉ khi skill được hai agent phát hiện, nguồn gốc không bị sửa, analyzer vẫn chạy được, bản export có đúng định dạng và chất lượng được quan sát. Kiểm tra frontmatter hay một lệnh render thành công riêng lẻ chưa chứng minh toàn bộ workflow hoạt động.

Hiện đã quan sát: CLI Claude, Codex, Node, uv, FFmpeg và ffprobe có trong PATH; chưa có thư mục skill `vfxlens` hoặc `studio/`. Không tìm thấy Blender trên PATH và thư mục mặc định đã kiểm tra không chứng minh Blender chưa được cài. Chưa chạy lại doctor, chưa cài skill/thư viện, chưa render end-to-end. Đề xuất này không thay đổi cấu hình hiện tại.
