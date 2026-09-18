# Hướng Dẫn Sử Dụng Hệ Thống Ôn Thi Tổ Trưởng & Chuyền Trưởng CESBG 2026 (v2.2.0)

Chào mừng bạn đến với **Hệ Thống Ôn Thi Xét Thăng Chức Tổ Trưởng (周边组长) & Chuyền Trưởng (线长) CESBG Việt Nam (2026)**.

---

## 🎯 Mục Lục
1. [Giới Thiệu Tổng Quan](#1-giới-thiệu-tổng-quan)
2. [Hướng Dẫn Khởi Động Nhanh](#2-hướng-dẫn-khởi-động-nhanh)
3. [Nền Tảng Đa Vai Trò (Tổ Trưởng ⇋ Chuyền Trưởng)](#3-nền-tảng-đa-vai-trò-tổ-trưởng--chuyền-trưởng)
4. [Hướng Dẫn Sử Dụng Web Mobile (Điện Thoại / Tablet)](#4-hướng-dẫn-sử-dụng-web-mobile-điện-thoại--tablet)
5. [Hướng Dẫn Sử Dụng Terminal CLI (Máy Tính)](#5-hướng-dẫn-sử-dụng-terminal-cli-máy-tính)
6. [Các Tính Năng Đặc Biệt Vừa Nâng Cấp](#6-các-tính-năng-đặc-biệt-vừa-nâng-cấp)
7. [Chẩn Đoán Điểm Yếu & Xuất Đề Thi Word (.docx)](#7-chẩn-đoán-điểm-yếu--xuất-đề-thi-word-docx)
8. [Các Câu Hỏi Thường Gặp (FAQ)](#8-các-câu-hỏi-thường-gặp-faq)

---

## 1. Giới Thiệu Tổng Quan
Hệ thống ôn thi CESBG 2026 là nền tảng 2-trong-1 chuyên nghiệp, số hóa toàn bộ dữ liệu kỳ thi thăng chức:
- **Tổ Trưởng (周边组长)**: Ngân hàng **201 câu hỏi** chính thức từ file Word gốc.
- **Chuyền Trưởng (线长)**: Ngân hàng **255 câu hỏi** chính thức từ file PDF gốc 15 trang.
- Đề thi mẫu chuẩn số 1 gồm **60 câu / 100 điểm** theo đúng ma trận đề thi thực tế tại nhà máy Foxconn/CESBG.

---

## 2. Hướng Dẫn Khởi Động Nhanh

### 📱 Cách 1: Sử dụng trên Điện Thoại (Web Mobile) — Tiện Lợi Nhất
1. Máy tính và điện thoại cùng kết nối vào một mạng Wi-Fi (hoặc chia sẻ 4G từ điện thoại).
2. Trên máy tính, nhấp đúp chuột vào file **`run_web.bat`**.
3. Màn hình Terminal sẽ hiển thị một **Mã QR Code** cùng địa chỉ IP (ví dụ: `http://192.168.1.15:8080`).
4. Mở camera trên điện thoại, quét mã QR và chạm vào đường link để vào thi ngay!

### 💻 Cách 2: Sử dụng trên Máy Tính (Terminal CLI) — Thao Tác Siêu Tốc
1. Nhấp đúp chuột vào file **`run.bat`**.
2. Giao diện dòng lệnh chuyên nghiệp sẽ mở ra với đầy đủ âm thanh, màu sắc và điều hướng 1-chạm.

---

## 3. Nền Tảng Đa Vai Trò (Tổ Trưởng ⇋ Chuyền Trưởng)

Ứng dụng cho phép bạn ôn luyện song song cả hai bộ đề thi mà không cần cài đặt hai phần mềm riêng biệt:
- **Trên Web Mobile**: Nhấp vào tab **`[ 👑 Tổ Trưởng ]`** hoặc **`[ ⚡ Chuyền Trưởng ]`** ngay trên thanh đầu trang. Toàn bộ câu hỏi, đề thi, số liệu thống kê sẽ lập tức chuyển đổi tương ứng.
- **Trên Terminal CLI**: Bấm phím **`[9]`** tại Menu chính để chuyển đổi qua lại tức thì. Bạn cũng có thể mở trực tiếp bằng lệnh:
  ```powershell
  python -X utf8 app.py --role chuyen_truong
  ```
- **Lưu ý quan trọng**: Sổ tay câu làm sai và lịch sử điểm số của Tổ Trưởng và Chuyền Trưởng được lưu độc lập tại `data/to_truong/` và `data/chuyen_truong/`, hoàn toàn không gây xáo trộn.

---

## 4. Hướng Dẫn Sử Dụng Web Mobile (Điện Thoại / Tablet)

- **Luyện Nhớ (Đề 1)**: Chọn đáp án và biết ngay kết quả Đúng (ting) / Sai (buzz) kèm giải thích chi tiết.
- **Thi Thử Bấm Giờ (60 Phút)**: Đồng hồ đếm ngược thời gian thực, ma trận 60 câu hỏi kéo mở mượt mà (Drawer Sheet), chấm điểm tự động và xếp loại cuối giờ.
- **Tự Động & Thủ Công Điều Chỉnh Cỡ Chữ**:
  - Cụm nút **`[ A- ] [ 100% ] [ A+ ]`** trên thanh Header: Bấm `A+` để chữ to hơn, `A-` để chữ nhỏ đi.
  - Bấm vào số `%` để mở **Bảng Tùy Chỉnh Cỡ Chữ**: chọn nhanh các mức từ 85% đến 150%, hoặc kéo thanh trượt tinh chỉnh.
  - Tự động phóng to theo màn hình: Khi xem trên iPad, laptop hoặc phóng to cửa sổ, chữ tự động to lên cho dễ đọc.
- **Ma trận 60 câu**: Chạm vào nút **`⚏ Ma Trận`** ở thanh đáy để xem tổng quan danh sách câu hỏi: câu màu xanh là đã làm, câu cắm cờ màu vàng, chạm vào ô bất kỳ để nhảy tức thì tới câu đó.

---

## 5. Hướng Dẫn Sử Dụng Terminal CLI (Máy Tính)

Hệ thống hỗ trợ bắt phím bấm tức thì (không cần nhấn Enter):

| Phím bấm | Tác vụ | Chi tiết |
|---|---|---|
| **`A` / `B` / `C` / `D`** | Chọn đáp án đơn | Chọn và tự động chuyển câu hỏi tiếp theo |
| **`A B C...` + `Enter`/`Space`** | Chọn nhiều đáp án | Nhập các ký tự đáp án, bấm **Enter** hoặc **Space** để nộp |
| **`V` / `X`** | Đúng / Sai | V = Đúng, X = Sai |
| **`F`** | Cắm cờ `⚑` | Đánh dấu câu hỏi cần xem lại trước khi nộp bài |
| **`P` / `N`** | Lùi / Tiến | Di chuyển qua lại giữa các câu hỏi |
| **`M`** | Mở Ma Trận 60 ô | Hiển thị bảng lưới toàn bộ bài thi |
| **`S`** | Nộp bài sớm | Kiểm tra số câu chưa làm và xác nhận kết thúc |
| **`Q`** | Thoát | Hủy bài thi quay về menu |

---

## 6. Các Tính Năng Đặc Biệt Vừa Nâng Cấp

### ⌨️ Phím Space Cho Câu Nhiều Đáp Án
- Tại các câu hỏi Phần II (chọn nhiều đáp án đúng), bạn có thể gõ các lựa chọn như `ABD` hoặc `A B D` rồi nhấn phím **`[Space]`** (phím cách) hoặc **`[Enter]`** đều được hệ thống ghi nhận.

### ✍️ Tự Viết Câu Trả Lời Tự Luận & Đối Soát Trực Quan
- Ở Phần IV (Trả lời ngắn gọn) và Phần V (Phân tích tình huống), ứng dụng hiển thị khung văn bản để bạn **tự gõ câu trả lời của mình**.
- Sau khi gõ xong và gửi, màn hình sẽ hiển thị bảng so sánh song song giữa **"Câu trả lời của bạn"** và **"Đáp án chuẩn của Foxconn/CESBG"** để bạn tự đánh giá độ chính xác và mức độ ghi nhớ.

---

## 7. Chẩn Đoán Điểm Yếu & Xuất Đề Thi Word (.docx)

- **Báo Cáo Điểm Yếu (Menu [8])**: Hệ thống tự động phân tích tỷ lệ nắm vững của 5 chuyên đề kiến thức, đánh dấu mức độ (Vững vàng / Trung bình / Cần cải thiện gấp) và đề xuất luyện cấp tốc phần yếu nhất.
- **Xuất Đề Thi Ra File Word (.docx)**:
  - Chọn mục xuất Word trên Terminal hoặc bấm nút **`📄 Xuất Đề Thi Ra File Word`** trên Web.
  - File Word sẽ được tạo tự động tại thư mục `exports/`, có định dạng bảng biểu in ấn đẹp mắt kèm theo Answer Key chi tiết ở cuối trang để in ra giấy cho toàn chuyền/tổ cùng làm bài.

---

## 8. Các Câu Hỏi Thường Gặp (FAQ)

1. **Tôi đổi điện thoại khác thì tiến độ có còn không?**
   - Dữ liệu làm bài được lưu trữ tập trung trên máy tính chạy Web Server. Khi bạn kết nối điện thoại mới, hệ thống tự động tải dữ liệu từ máy tính sang.
2. **Làm sao để xóa các câu trong Sổ câu sai khi đã thuộc?**
   - Vào mục **[6] Cài đặt** trên Terminal CLI và chọn **[5] Xóa sạch Sổ tay câu sai**.
3. **Phóng to chữ trên máy tính bằng cách nào nhanh nhất?**
   - Trên Terminal: Giữ phím **`Ctrl`** và **lăn chuột lên** (hoặc nhấn `Ctrl + Shift + '+'`).
   - Trên Web: Bấm nút **`[A+]`** trên góc phải màn hình hoặc nhấn phím tắt `Ctrl` + `+`.
