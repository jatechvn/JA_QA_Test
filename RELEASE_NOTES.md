TAG=v2.2.1
TITLE=JA_QA_Test v2.2.1 — Viết Tự Luận Shift+Enter & Điều Hướng Ma Trận Bằng Phím Mũi Tên
BODY=
## Ứng Dụng Ôn Thi Tổ Trưởng & Chuyền Trưởng CESBG 2026 — v2.2.1

Bản cập nhật v2.2.1 tối ưu hóa sâu trải nghiệm tương tác bàn phím: hỗ trợ viết văn tự luận nhiều dòng bằng Shift+Enter, điều hướng ma trận câu hỏi bằng phím mũi tên và xác nhận nhanh bằng Space/Enter.

### 🌟 Điểm Nhấn Chính trong Phiên Bản v2.2.1:
- **📝 Soạn thảo câu tự luận đa dòng (Shift + Enter):**
  - Người học có thể nhấn `[Shift + Enter]` để xuống dòng tự nhiên như đang viết đoạn văn bản trên cả Terminal CLI và Web Mobile.
  - Nhấn `[Enter]` đơn để nộp bài tự luận và lật mở bảng đối soát song song với đáp án mẫu chuẩn.
  - Chuẩn hóa thông báo hướng dẫn: chỉ nhắc nhấn `[Enter]` để lật đáp án, tránh gây nhầm lẫn với phím Space.
- **🎮 Điều hướng Ma trận câu hỏi bằng phím mũi tên (Matrix Arrow Navigation):**
  - Sử dụng các phím mũi tên `[←] [→] [↑] [↓]` (hoặc `W`, `A`, `S`, `D`) để di chuyển con trỏ chọn ô câu hỏi linh hoạt.
  - Nhấn phím `[Space]` hoặc `[Enter]` để xác nhận nhảy ngay đến câu hỏi đã chọn.
  - Hỗ trợ đóng ma trận bằng phím `[Esc]` hoặc `[Q]`.
  - Tự động cuộn ô đang chọn vào tầm nhìn màn hình trên Web Mobile (`scrollIntoView`).
- **Đồng bộ tài liệu & hệ thống:** Cập nhật đồng bộ `core/version.py`, `ABOUT.txt`, `README.md`, `CHANGELOG.md`, `USERGUIDE.md`, `RELEASE_NOTES.md`.

### 📦 Cài Đặt & Sử Dụng
- **Cách 1 - Web Mobile (Điện thoại/Máy tính bảng):** Nhấp đúp vào `run_web.bat`, dùng camera điện thoại quét mã QR hiển thị trên màn hình Terminal để học ngay.
- **Cách 2 - Terminal CLI (Máy tính):** Nhấp đúp vào `run.bat` để mở giao diện dòng lệnh ANSI trực quan với ma trận 60 ô và âm thanh hiệu ứng.
