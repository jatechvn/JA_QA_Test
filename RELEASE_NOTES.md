TAG=v2.2.2
TITLE=JA_QA_Test v2.2.2 — Nâng Cấp Toàn Diện Hệ Thống Âm Thanh (Sound Engine) CLI & Web Mobile
BODY=
## Ứng Dụng Ôn Thi Tổ Trưởng & Chuyền Trưởng CESBG 2026 — v2.2.2

Bản cập nhật v2.2.2 khắc phục triệt để các lỗi âm thanh trên cả hai nền tảng Terminal CLI và Web Mobile: tổng hợp âm thanh WAV PCM đa âm bất đồng bộ cho CLI và giải mã Web Audio chống crash mượt mà cho Web Mobile.

### 🌟 Điểm Nhấn Chính trong Phiên Bản v2.2.2:
- **🔊 Nâng cấp toàn diện Sound Engine trên Windows Terminal CLI:**
  - Tổng hợp âm thanh WAV PCM đa âm 16-bit 22050Hz trực tiếp trong bộ nhớ.
  - Chạy bất đồng bộ qua luồng ngầm (`daemon thread`), truyền thẳng ra loa ngoài / tai nghe Bluetooth / USB, hoàn toàn không phụ thuộc vào loa còi bo mạch chủ.
  - Cơ chế dự phòng 3 tầng vững chắc: WAV Sound -> winsound.Beep -> MessageBeep.
  - Bổ sung tùy chọn `[5] Phát thử toàn bộ âm thanh (Test Audio)` trong Menu Cài đặt CLI để người dùng thử loa trực tiếp.
- **🌐 Khắc phục triệt để lỗi âm thanh Web Mobile / PC:**
  - Tự động kích hoạt AudioContext (`unlockAudio`) ngay khi người dùng chạm màn hình, không bị chặn bởi chính sách Autoplay của trình duyệt.
  - Sử dụng giải thuật suy giảm tuyến tính (`linearRampToValueAtTime`), loại bỏ 100% tiếng nổ bụp và lỗi DOMException.
  - Bổ sung trọn vẹn 5 hiệu ứng âm thanh: Đúng (Chime), Sai (Buzz), Cắm cờ (Tick), Chuyển câu (Soft tap), Nộp bài đỗ (Triumph).
  - Phân luồng âm thanh chính xác: Chấm điểm tự luận "Đã thuộc" phát chuông đúng, "Cần ôn lại" phát chuông cảnh báo.
  - Tự động lưu trạng thái bật/tắt âm thanh vào `localStorage` (`cesbg_sound`).
- **Đồng bộ tài liệu & hệ thống:** Cập nhật đồng bộ `core/version.py`, `ABOUT.txt`, `README.md`, `CHANGELOG.md`, `USERGUIDE.md`, `RELEASE_NOTES.md`.

### 📦 Cài Đặt & Sử Dụng
- **Cách 1 - Web Mobile (Điện thoại/Máy tính bảng):** Nhấp đúp vào `run_web.bat`, dùng camera điện thoại quét mã QR hiển thị trên màn hình Terminal để học ngay.
- **Cách 2 - Terminal CLI (Máy tính):** Nhấp đúp vào `run.bat` để mở giao diện dòng lệnh ANSI trực quan với ma trận 60 ô và âm thanh hiệu ứng.
