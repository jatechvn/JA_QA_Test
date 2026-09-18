TAG=v2.2.0
TITLE=JA_QA_Test v2.2.0 — Nền Tảng Đa Vai Trò (Tổ Trưởng ⇋ Chuyền Trưởng) & Cỡ Chữ Thích Ứng
BODY=
## Ứng Dụng Ôn Thi Tổ Trưởng & Chuyền Trưởng CESBG 2026 — v2.2.0

Bản phát hành lớn v2.2.0 mở rộng ứng dụng thành nền tảng thi cử 2-trong-1 toàn diện, nâng cấp trải nghiệm tương tác với phím Space cho câu đa đáp án, nhập câu trả lời tự luận đối soát trực tiếp, và hệ thống tự động phóng lớn cỡ chữ thích ứng màn hình (Fluid Typography).

### 🌟 Điểm Nhấn Chính trong Phiên Bản v2.2.0:
- **👑⚡ Nền tảng Đa Vai Trò 2-trong-1:**
  - Hỗ trợ trọn vẹn 2 ngân hàng câu hỏi chính thức CESBG 2026: **Tổ Trưởng (周边组长 - 201 câu)** và **Chuyền Trưởng (线长 - 255 câu)**.
  - Đề thi chuẩn mẫu số 1 và Đề thi thử ngẫu nhiên 60 câu / 100 điểm độc lập cho từng vai trò.
  - Chuyển đổi vai trò tức thì chỉ với 1 nút bấm (phím `[9]` trên Terminal hoặc chạm tab trên Web Mobile).
  - Tách biệt hoàn toàn tiến độ học tập, lịch sử điểm và Sổ tay câu sai giữa 2 vai trò.
- **⌨️ Phím Space cho câu nhiều lựa chọn:** Nhập các đáp án (vd: `ABD`) và bấm phím `[Space]` (phím cách) hoặc `[Enter]` đều được chấp nhận để xác nhận câu trả lời.
- **✍️ Tự viết câu trả lời tự luận & Đối soát trực quan:** Khung nhập văn bản cho phép người học tự soạn câu trả lời trước khi xem đáp án, sau đó hiển thị bảng đối soát chi tiết giữa câu trả lời của bạn và đáp án chuẩn.
- **🔤 Tự động phóng lớn theo màn hình & Điều chỉnh cỡ chữ linh hoạt:**
  - Áp dụng công thức CSS `clamp()` kết hợp biến `--font-scale` tự động phóng to chữ từ 1.0x (điện thoại) đến 1.25x (màn hình máy tính lớn / khi phóng to trình duyệt).
  - Mở khóa cử chỉ hai ngón tay chụm/mở (`pinch-to-zoom`) trên điện thoại lên tới 500%.
  - Cụm nút nhanh `[A-] [100%] [A+]` trên Header Web, bảng cài đặt cỡ chữ chuyên sâu (80% - 160%), công tắc bật/tắt tự động thích ứng và phím tắt `Ctrl + +` / `Ctrl + -`.
  - Terminal CLI tự động co giãn độ rộng theo cửa sổ PowerShell/CMD.
- **📄 Xuất đề thi Word (.docx) & Chẩn đoán điểm yếu:** Hệ thống phân tích 5 chuyên đề kiến thức và xuất đề thi giấy chuẩn in ấn kèm Answer Key.

### 📦 Cài Đặt & Sử Dụng
- **Cách 1 - Web Mobile (Điện thoại/Máy tính bảng):** Nhấp đúp vào `run_web.bat`, dùng camera điện thoại quét mã QR hiển thị trên màn hình Terminal để học ngay.
- **Cách 2 - Terminal CLI (Máy tính):** Nhấp đúp vào `run.bat` để mở giao diện dòng lệnh ANSI trực quan với ma trận 60 ô và âm thanh hiệu ứng.
