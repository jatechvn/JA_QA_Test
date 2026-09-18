# Ứng Dụng CLI & Web Mobile Ôn Thi Tổ Trưởng & Chuyền Trưởng CESBG 2026

![Version](https://img.shields.io/badge/version-2.2.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-CLI%20%7C%20Web%20Mobile-orange.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)

Hệ thống ôn thi trắc nghiệm & tình huống chuẩn mực 2-trong-1, chuyên nghiệp và trực quan, hỗ trợ học viên ôn luyện và ghi nhớ nhanh nhất toàn bộ kiến thức kỳ thi thăng chức **Tổ Trưởng (周边组长)** và **Chuyền Trưởng (线长)** CESBG Việt Nam (2026).

---

## 🌟 Tính Năng Nổi Bật Mới Nhất

### 1. 🔄 Nền Tảng Đa Vai Trò 2-trong-1 (Multi-Role Platform)
- **Hỗ trợ đầy đủ 2 ngân hàng câu hỏi chính thức**:
  - 👑 **Tổ Trưởng (周边组长)**: 201 câu hỏi (92 Trắc nghiệm 1 đáp án, 57 Nhiều đáp án, 32 Đúng/Sai, 12 Tự luận, 8 Tình huống).
  - ⚡ **Chuyền Trưởng (线长)**: 255 câu hỏi (116 Trắc nghiệm 1 đáp án, 69 Nhiều đáp án, 43 Đúng/Sai, 16 Tự luận, 11 Tình huống).
- **Chuyển đổi vai trò tức thì**:
  - Trên **Terminal CLI**: Nhấn phím **`[9]`** tại Menu chính để chuyển đổi vai trò ôn thi.
  - Trên **Web Mobile**: Chạm vào tab **`[ 👑 Tổ Trưởng ]`** hoặc **`[ ⚡ Chuyền Trưởng ]`** ngay trên đầu màn hình.
- **Dữ liệu độc lập tuyệt đối**: Lịch sử thi cử, tiến độ và Sổ tay câu làm sai của Tổ Trưởng và Chuyền Trưởng được lưu trữ ở hai thư mục riêng biệt (`data/to_truong/` và `data/chuyen_truong/`), không gây nhầm lẫn hay ghi đè.

### 2. 📝 Soạn Thảo Đoạn Văn Tự Luận (Shift + Enter) & Đối Soát Trực Quan
- Ở phần Tự luận (Phần IV) và Tình huống (Phần V):
  - Hỗ trợ nhấn **`[Shift + Enter]`** để xuống dòng tự nhiên như viết đoạn văn trên cả Terminal và Web.
  - Nhấn **`[Enter]`** đơn để gửi bài làm và lật mở bảng đối soát song song giữa "Câu trả lời của bạn" và "Đáp án mẫu chuẩn".

### 3. 🎮 Ma Trận Câu Hỏi Điều Hướng Thông Minh (Matrix Navigation)
- Dùng **phím mũi tên `[←] [→] [↑] [↓]`** hoặc **`[W] [A] [S] [D]`** để di chuyển con trỏ chọn câu trong ma trận câu hỏi.
- Nhấn phím **`[Space]`** hoặc **`[Enter]`** để xác nhận nhảy ngay đến câu hỏi đang chọn.
- Nhấn **`[Esc]`** hoặc **`[Q]`** để đóng ma trận nhanh chóng.

### 4. ⌨️ Hỗ Trợ Phím Space Cho Câu Hỏi Nhiều Đáp Án
- Ở các câu trắc nghiệm nhiều đáp án (Phần II), bạn có thể nhập các lựa chọn (ví dụ: `ABD` hoặc `A B D`) và nhấn phím **`[Space]`** (phím cách) hoặc **`[Enter]`** đều được chấp nhận để xác nhận câu trả lời.
- Hoạt động mượt mà trên cả giao diện Terminal CLI lẫn Web Mobile.

### 5. 🔤 Tự Động Phóng Lớn & Điều Chỉnh Cỡ Chữ Linh Hoạt
- **Tự động thích ứng (Auto-Scale)**: Khi phóng to cửa sổ trình duyệt, xoay ngang điện thoại hoặc học trên iPad/máy tính, cỡ chữ và khung câu hỏi tự động mở rộng mượt mà theo tỷ lệ màn hình (Fluid Typography) giúp mắt không bị mỏi.
- **Tùy chỉnh thủ công (Manual Controls)**:
  - **Trên Web Mobile / Desktop**: Cụm nút bấm nhanh `[A-] [100%] [A+]` ngay trên thanh tiêu đề cho phép tăng/giảm nhanh cỡ chữ (80% đến 160%), chọn các mức chuẩn (`Nhỏ 85%`, `Chuẩn 100%`, `Lớn 115%`, `Rất Lớn 130%`, `Cực Đại 150%`), hoặc dùng phím tắt `Ctrl + +` / `Ctrl + -`.
  - **Trên Terminal CLI**: Tự động co giãn độ rộng khung viền theo độ phóng to của cửa sổ PowerShell/CMD, hỗ trợ phóng to chữ tức thì bằng `Ctrl + Lăn Chuột Lên`.

---

## 📱 Hai Nền Tảng Trải Nghiệm Linh Hoạt

- **Terminal TUI Đẳng Cấp (PC/Laptop)**: Ma trận câu hỏi 60 ô, cắm cờ `[F]`, đồng hồ đếm ngược, âm thanh `winsound`, điều hướng 1-chạm cực nhanh.
- **Web Mobile Siêu Tốc (Smartphone/Tablet)**: Quét mã QR Code trực tiếp từ Terminal bằng camera điện thoại để làm bài trên smartphone qua mạng Wi-Fi/LAN, Zero-Dependency.

---

## 🚀 Hướng Dẫn Khởi Động

### 1. Dùng trên Điện Thoại (Web Mobile)
- **Cách 1**: Nhấp đúp chuột vào file **`run_web.bat`**.
- **Cách 2**: Chạy lệnh từ Terminal:
  ```bash
  python -X utf8 web_server.py
  ```
- **Cách 3**: Mở `app.py` và chọn phím **`[7]`** (Khởi Động Web Server Mobile).
👉 Dùng camera điện thoại (cùng kết nối Wi-Fi) quét mã QR hiển thị trên màn hình để bắt đầu học!

### 2. Dùng trên Máy Tính (Terminal CLI)
- **Cách 1**: Nhấp đúp chuột vào file **`run.bat`**.
- **Cách 2**: Chạy lệnh:
  ```bash
  python -X utf8 app.py
  ```
  *(Có thể truyền trực tiếp vai trò khởi động: `python -X utf8 app.py --role chuyen_truong`)*

---

## 🎮 Hệ Thống Phím Tắt Terminal

Khi đang trong bài thi hoặc luyện tập trên Terminal:

| Phím tắt | Chức năng | Mô tả |
|---|---|---|
| **`A` / `B` / `C` / `D`** | **Chọn đáp án** | Chọn đáp án trắc nghiệm đơn và tự động chuyển câu tiếp theo. |
| **`A B C...` + `Enter`/`Space`** | **Nhiều đáp án** | Chọn nhiều đáp án, bấm **Enter** hoặc **Space** để nộp. |
| **`V` / `X`** | **Đúng / Sai** | Chọn Đúng (V) hoặc Sai (X) ở phần Phán đoán. |
| **`F`** | **Cắm cờ / Bỏ cắm cờ ⚑** | Đánh dấu câu hỏi cần phân vân suy nghĩ lại. |
| **`P`** | **Quay lại (Previous)** | Lùi về câu hỏi phía trước để xem hoặc sửa đáp án. |
| **`N`** | **Kế tiếp (Next)** | Chuyển nhanh sang câu hỏi tiếp theo. |
| **`M`** | **Mở Ma Trận 60 câu** | Xem bảng lưới tổng quan toàn bộ đề thi & nhập số câu để nhảy nhanh. |
| **`S`** | **Nộp bài sớm (Submit)** | Mở màn hình kiểm tra tổng kết câu đã làm / câu chưa làm và xác nhận nộp bài. |
| **`Q`** | **Thoát (Quit)** | Dừng bài thi sớm và quay về Menu chính. |

---

## 🎯 Danh Mục Chức Năng Ôn Luyện (Menu Chính)

| Mục | Chức năng | Mô tả chi tiết |
|---|---|---|
| **[1]** | **Luyện tập Đề Thi Mẫu 1 (60 câu)** | Chuẩn cơ cấu thi 100 điểm: 30 câu đơn (30đ) + 15 câu đa (30đ) + 10 đúng/sai (10đ) + 4 tự luận (20đ) + 1 tình huống (10đ). Tùy chọn giữ nguyên thứ tự gốc hoặc đảo ngẫu nhiên; gồm **Luyện Nhớ** và **Thi Thử Bấm Giờ 60 Phút**. |
| **[2]** | **Ôn tập Ngân Hàng Gốc theo Chuyên Đề** | Luyện riêng theo từng phần: Trắc nghiệm 1 đáp án, Nhiều đáp án, Đúng/Sai, Tự luận ngắn, Tình huống thực tế. |
| **[3]** | **Tạo Đề Thi Thử Ngẫu Nhiên (100 điểm)** | Tự động rút ngẫu nhiên 60 câu chuẩn cơ cấu điểm số theo vai trò đang chọn. |
| **[4]** | **Sổ Tay Câu Hay Sai (Spaced Repetition)** | Mọi câu làm sai sẽ tự động được lưu vào đây để ôn luyện lại cho đến khi thành thạo. |
| **[5]** | **Tra Cứu Nhanh (Cheatsheet)** | Tìm kiếm thông minh (hỗ trợ cả gõ có dấu và không dấu: `an toan`, `xung dot`, `5S`, `chua chay`) để tìm câu hỏi và đáp án đúng. |
| **[6]** | **Cài Đặt Tùy Chọn** | Đổi theme Dark/Light, Bật/Tắt âm thanh (winsound / Web Audio), Đảo vị trí đáp án A/B/C/D chống học vẹt, Xóa dữ liệu ôn tập. |
| **[7]** | **Khởi Động Web Server Mobile** | Kích hoạt máy chủ đa luồng cục bộ, in mã QR Code để ôn tập trên smartphone mọi lúc mọi nơi. |
| **[8]** | **Phân Tích Điểm Yếu & Xuất Đề Word (.docx)** | Chẩn đoán năng lực 5 chuyên đề, xác định mảng kiến thức yếu nhất để luyện cấp tốc, và xuất đề thi giấy chuẩn sang file Word `.docx` kèm Answer Key. |
| **[9]** | **🔄 Đổi Vai Trò Ôn Thi** | Chuyển đổi linh hoạt giữa **👑 Tổ Trưởng (周边组长)** và **⚡ Chuyền Trưởng (线长)**. |

---

## 🧠 Lộ Trình Ôn Thi Đạt 90 - 100 Điểm

1. **Bước 1**: Chọn vai trò ôn thi phù hợp (**Mục [9]** hoặc đổi trên Web).
2. **Bước 2**: Mở **Mục [2]** luyện từng chuyên đề với chế độ **Phản hồi tức thì** để nắm vững lý thuyết.
3. **Bước 3**: Luyện các câu Tự luận & Tình huống, chủ động **tự gõ câu trả lời** để đối soát với đáp án chuẩn.
4. **Bước 4**: Quét mã QR bằng điện thoại qua **Mục [7]** hoặc `run_web.bat` để luyện tập tranh thủ giờ nghỉ giải lao.
5. **Bước 5**: Mở **Mục [8]** xem Báo cáo chẩn đoán điểm yếu và luyện cấp tốc chuyên đề cần cải thiện.
6. **Bước 6**: Làm bài thi thử bấm giờ 60 phút ở **Mục [1]** hoặc **Mục [3]**, rèn luyện tốc độ làm bài và làm chủ kỳ thi!
