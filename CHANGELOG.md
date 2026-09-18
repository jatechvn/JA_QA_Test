# Nhật Ký Thay Đổi (Changelog) - JA_QA_Test

Tất cả các thay đổi quan trọng của dự án Ứng dụng Ôn thi Tổ Trưởng & Chuyền Trưởng CESBG 2026 sẽ được ghi lại trong tài liệu này.

---

## [v2.2.1] - 2026-09-18

### 🚀 Nâng cấp & Tính năng mới
- **Soạn thảo câu tự luận đa dòng (Shift + Enter):**
  - Hỗ trợ nhấn `[Shift + Enter]` để xuống dòng tự nhiên như viết đoạn văn trên cả Terminal CLI (`msvcrt` + Win32 API `GetAsyncKeyState`) và Web Mobile / PC (`textarea keydown`).
  - Nhấn `[Enter]` đơn để hoàn tất bài làm và lật mở đáp án chuẩn đối soát.
  - Chuẩn hóa câu hướng dẫn thành `nhấn [Enter] để lật đáp án` (không còn hiển thị nhầm phím Space ở phần tự luận).
- **Ma trận câu hỏi tương tác thông minh (Question Matrix Navigation):**
  - Hỗ trợ đầy đủ phím mũi tên `[←] [→] [↑] [↓]` (hoặc `W`, `A`, `S`, `D`) để di chuyển con trỏ chọn câu trong ma trận câu hỏi.
  - Hỗ trợ nhấn `[Space]` (phím cách) hoặc `[Enter]` để xác nhận nhảy ngay đến câu đã chọn.
  - Tự động cuộn ô đang chọn vào tầm nhìn trên Web Mobile (`scrollIntoView`).
  - Hỗ trợ đóng ma trận bằng phím `[Esc]` hoặc `[Q]`.

### 📦 Phát hành
- Đồng bộ version `v2.2.1+6` trong `core/version.py`, `ABOUT.txt`, `README.md`, `CHANGELOG.md`, `USERGUIDE.md`, `RELEASE_NOTES.md`.

---

## [v2.2.0] - 2026-09-18

### 🚀 Nâng cấp & Tính năng mới
- **Nền tảng Đa Vai Trò 2-trong-1 (Multi-Role Platform):**
  - Tích hợp trọn vẹn 2 ngân hàng câu hỏi chính thức: **Tổ Trưởng (周边组长 - 201 câu)** và **Chuyền Trưởng (线长 - 255 câu)**.
  - Hỗ trợ chuyển đổi vai trò linh hoạt tức thì qua phím `[9]` trên Terminal CLI hoặc tab chuyển đổi ở đầu trang Web Mobile.
  - Phân vùng dữ liệu độc lập: `data/to_truong/` và `data/chuyen_truong/`, bảo toàn lịch sử thi cử và Sổ tay câu sai riêng biệt.
- **Hỗ trợ phím Space cho câu nhiều đáp án:**
  - Cho phép thí sinh nhập các đáp án (ví dụ: `ABD`) và nhấn phím `[Space]` (phím cách) với chức năng tương tự phím `[Enter]` để xác nhận câu trả lời trên cả Terminal và Web Mobile.
- **Tự viết câu trả lời tự luận & Đối soát trực quan:**
  - Cung cấp khung nhập liệu cho phép thí sinh tự gõ câu trả lời của mình ở phần Tự luận (Phần IV) và Tình huống (Phần V).
  - Tự động hiển thị bảng so sánh đối soát song song giữa "Câu trả lời của bạn" và "Đáp án mẫu chuẩn" trước khi tự chấm điểm.
- **Tự động phóng lớn cỡ chữ theo màn hình (Fluid Typography):**
  - Mở khóa cử chỉ chụm/mở (`pinch-to-zoom`) trên thiết bị di động lên tới 500%.
  - Áp dụng công thức CSS `clamp()` kết hợp biến động `--font-scale` tự động phóng to chữ từ 1.0x (điện thoại) lên đến 1.25x (màn hình máy tính lớn / khi phóng to trình duyệt).
  - Mở rộng chiều rộng khung nội dung tối đa từ 640px lên đến 860px trên máy tính.
- **Bảng điều khiển cỡ chữ thủ công:**
  - Cụm nút nhanh `[A-] [100%] [A+]` trên thanh Header của Web Mobile / PC.
  - Bảng cài đặt cỡ chữ chuyên sâu với 5 mức chọn nhanh (`85%`, `100%`, `115%`, `130%`, `150%`), thanh trượt tinh chỉnh (80% - 160%), công tắc bật/tắt tự động phóng lớn và ô xem trước thực tế.
  - Phím tắt bàn phím tiện lợi: `Ctrl + +`, `Ctrl + -`, `Ctrl + 0`.

### 🐛 Sửa lỗi & Tối ưu hóa
- Tối ưu hóa bộ bóc tách PDF PyMuPDF (`fitz`), xử lý chuẩn xác 100% các ký hiệu Đúng/Sai (`V`, `X`, `√`, `×`).
- Co giãn linh hoạt khung viền Terminal CLI theo kích thước thực tế của cửa sổ (`get_terminal_width()`).
- Bổ sung mẹo phóng to chữ Terminal trực tiếp trong menu Cài đặt (`Ctrl + Lăn Chuột Lên`).

### 📦 Phát hành
- Đồng bộ version `v2.2.0+5` trong `core/version.py`, `ABOUT.txt`, `README.md`, `CHANGELOG.md`, `USERGUIDE.md`, `RELEASE_NOTES.md`.

---

## [v2.1.0] - 2026-09-17

### 🚀 Nâng cấp & Tính năng mới
- **Chẩn đoán điểm yếu (Diagnostic Analytics):**
  - Báo cáo phân tích tỷ lệ nắm vững theo 5 mảng kiến thức, tìm ra phần có tỷ lệ sai nhiều nhất.
  - Tính năng "Luyện cấp tốc chuyên đề yếu nhất" giúp nâng điểm nhanh chóng.
- **Xuất đề thi Word (.docx) chuyên nghiệp:**
  - Xuất trọn vẹn 60 câu hỏi chuẩn sang file Word phục vụ in ấn nội bộ Foxconn/CESBG.
  - Tùy chọn kèm Answer Key chi tiết và bảng chấm điểm cho ban giám khảo.

---

## [v2.0.0] - 2026-09-16

### 🚀 Nâng cấp & Tính năng mới
- **Web Server Mobile & Quét mã QR Code:**
  - Tích hợp máy chủ HTTP đa luồng `ThreadingHTTPServer` siêu nhẹ (Zero-dependency).
  - Tự động dò tìm địa chỉ IP mạng LAN/Wi-Fi và in mã QR Code dạng ASCII Art trực tiếp lên màn hình Terminal.
  - Giao diện Web tối ưu Mobile-First, hỗ trợ Dark/Light Theme và âm thanh Web Audio API.

---

## [v1.0.0] - 2026-09-15

### 🚀 Nâng cấp & Tính năng mới
- Khởi tạo hệ thống thi trắc nghiệm trên nền tảng Terminal CLI TUI.
- Bộ đề thi chuẩn 60 câu / 100 điểm cho Tổ Trưởng CESBG.
- Ma trận 60 ô vuông, cắm cờ câu hỏi phân vân `[F]`, đồng hồ đếm ngược 60 phút, sổ câu hay sai Spaced Repetition và tra cứu nhanh Cheatsheet.
