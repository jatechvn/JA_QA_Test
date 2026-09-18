#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_server.py - Máy chủ Web Server ôn thi Tổ Trưởng CESBG 2026 (Giai đoạn 2).
Sử dụng ThreadingHTTPServer tích hợp sẵn trong Python (Zero-dependency),
hỗ trợ học viên luyện đề trực tiếp trên Smartphone / Máy tính bảng / PC.
Tự động phát hiện IP mạng LAN/Wi-Fi và in mã QR Code trực tiếp ra Terminal.
"""

import json
import os
import re
import socket
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.storage import StorageManager
from core.quiz_engine import QuizEngine
from ui.terminal import Color

STORAGE = StorageManager()
QUIZ_ENGINE = QuizEngine(STORAGE)


def get_local_ip() -> str:
    """Tự động phát hiện địa chỉ IP nội bộ của máy tính trong mạng Wi-Fi/LAN."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def print_qr_code(url: str):
    """In mã QR Code ra Terminal để học viên dùng điện thoại quét nhanh."""
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.print_ascii(invert=True)
    except Exception:
        pass


class QAWebHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler phục vụ REST API và Web App tĩnh."""

    def log_message(self, format, *args):
        # Giảm bớt log terminal để giao diện luôn sạch
        if "404" in str(args) or "500" in str(args):
            super().log_message(format, *args)

    def _send_json(self, data: Any, status: int = HTTPStatus.OK):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # Hỗ trợ tham số vai trò: ?role=to_truong hoặc ?role=chuyen_truong
        req_role = params.get("role", [None])[0]
        if req_role in ("to_truong", "chuyen_truong"):
            STORAGE.set_role(req_role)

        # 1. API: Thống kê & Trạng thái
        if path == '/api/info':
            STORAGE.progress = STORAGE._load_progress()
            data = {
                "role": STORAGE.role,
                "role_info": STORAGE.get_role_info(),
                "total_bank": STORAGE.bank_data.get("total_questions", 0),
                "counts": STORAGE.bank_data.get("counts", {}),
                "total_exam1": STORAGE.exam_de1_data.get("total_questions", 0),
                "wrong_count": len(STORAGE.get_wrong_questions()),
                "stats": STORAGE.progress.get("stats", {}),
                "settings": STORAGE.progress.get("settings", {})
            }
            self._send_json(data)
            return

        # 2. API: Lấy Đề 1 (60 câu - mặc định đảo ngẫu nhiên theo yêu cầu)
        elif path == '/api/exam1':
            shuffle_opts = STORAGE.get_setting("shuffle_options", False)
            shuffle_q = params.get("shuffle", ["true"])[0].lower() in ("true", "1")
            questions = QUIZ_ENGINE.prepare_exam_de1(shuffle_questions=shuffle_q, shuffle_options=shuffle_opts)
            role_label = STORAGE.get_role_title()
            self._send_json({
                "title": f"Đề Thi Chuẩn Mẫu Số 1 - {role_label} (Đảo Ngẫu Nhiên)" if shuffle_q else f"Đề Thi Chuẩn Mẫu Số 1 - {role_label}",
                "total": len(questions),
                "questions": questions
            })
            return

        # 3. API: Lấy câu hỏi theo chuyên đề
        elif path == '/api/topic':
            topic_type = params.get("type", ["single_choice"])[0]
            shuffle_opts = STORAGE.get_setting("shuffle_options", False)
            questions = QUIZ_ENGINE.prepare_topic_questions(topic_type, shuffle_questions=True, shuffle_options=shuffle_opts)
            title_map = {
                "single_choice": "Phần I: Trắc Nghiệm 1 Đáp Án",
                "multi_choice": "Phần II: Trắc Nghiệm Nhiều Đáp Án",
                "true_false": "Phần III: Phán Đoán Đúng / Sai",
                "short_answer": "Phần IV: Trả Lời Ngắn Gọn (Tự Luận)",
                "case_study": "Phần V: Phân Tích Tình Huống (Thực Tế)",
                "all": f"Toàn Bộ Ngân Hàng Câu Hỏi Gốc ({STORAGE.bank_data.get('total_questions', 0)} câu)"
            }
            self._send_json({
                "title": title_map.get(topic_type, "Ôn Tập Chuyên Đề"),
                "total": len(questions),
                "questions": questions
            })
            return

        # 4. API: Sinh đề thi thử ngẫu nhiên 100 điểm
        elif path == '/api/mock':
            shuffle_opts = STORAGE.get_setting("shuffle_options", False)
            questions = QUIZ_ENGINE.generate_mock_exam(shuffle_options=shuffle_opts)
            self._send_json({
                "title": f"Đề Thi Thử Ngẫu Nhiên ({STORAGE.get_role_title()} - 100 Điểm)",
                "total": len(questions),
                "questions": questions
            })
            return

        # 5. API: Sổ tay câu hỏi sai
        elif path == '/api/wrong':
            shuffle_opts = STORAGE.get_setting("shuffle_options", False)
            questions = QUIZ_ENGINE.prepare_wrong_questions(shuffle_options=shuffle_opts)
            self._send_json({
                "title": "Sổ Tay Ôn Câu Hay Sai",
                "total": len(questions),
                "questions": questions
            })
            return

        # 6. API: Tra cứu từ khóa (Cheatsheet)
        elif path == '/api/search':
            kw = params.get("q", [""])[0]
            results = STORAGE.search_questions(kw)
            self._send_json({
                "query": kw,
                "total": len(results),
                "results": results[:50]
            })
            return

        # 7. API: Báo cáo phân tích điểm yếu (Giai đoạn 3)
        elif path == '/api/analytics':
            from core.exporter import generate_weakness_report
            data = generate_weakness_report(STORAGE)
            self._send_json(data)
            return

        # 8. API: Xuất đề thi sang file Word (.docx) (Giai đoạn 3)
        elif path == '/api/export_docx':
            from core.exporter import export_exam_to_docx
            exam_type = params.get("type", ["exam1"])[0]
            shuffle_opts = STORAGE.get_setting("shuffle_options", False)
            if exam_type == "mock":
                questions = QUIZ_ENGINE.generate_mock_exam(shuffle_options=shuffle_opts)
                title = "Đề Thi Thử Ngẫu Nhiên Mới (Chuẩn 100 Điểm)"
            else:
                questions = QUIZ_ENGINE.prepare_exam_de1(shuffle_questions=True, shuffle_options=shuffle_opts)
                title = "Đề Thi Chuẩn Mẫu Số 1 (Đảo Ngẫu Nhiên)"
            
            file_path = export_exam_to_docx(questions, title)
            self._send_json({
                "status": "ok",
                "filename": file_path.name,
                "path": str(file_path),
                "message": f"Đã xuất file Word thành công tại {file_path.name}"
            })
            return

        # 7. Phục vụ Web App tĩnh (HTML/CSS/JS)
        if path in ('/', '/index.html'):
            html_file = BASE_DIR / "web" / "index.html"
            if html_file.exists():
                content = html_file.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_error(HTTPStatus.NOT_FOUND, "Không tìm thấy trang yêu cầu.")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # Nếu payload có chỉ định vai trò
        req_role = payload.get("role")
        if req_role in ("to_truong", "chuyen_truong"):
            STORAGE.set_role(req_role)

        # 0. API: Đổi vai trò
        if path == '/api/set_role':
            new_role = payload.get("role", "to_truong")
            STORAGE.set_role(new_role)
            self._send_json({
                "status": "ok",
                "role": STORAGE.role,
                "role_info": STORAGE.get_role_info(),
                "total_bank": STORAGE.bank_data.get("total_questions", 0),
                "counts": STORAGE.bank_data.get("counts", {}),
                "total_exam1": STORAGE.exam_de1_data.get("total_questions", 0),
                "wrong_count": len(STORAGE.get_wrong_questions()),
                "stats": STORAGE.progress.get("stats", {})
            })
            return

        # 1. Ghi nhận kết quả 1 câu hỏi
        elif path == '/api/record':
            q_data = payload.get("question", {})
            is_correct = bool(payload.get("is_correct", False))
            user_ans = str(payload.get("user_ans", ""))
            if q_data:
                STORAGE.record_question_result(q_data, is_correct, user_ans)
            self._send_json({"status": "ok", "wrong_count": len(STORAGE.get_wrong_questions())})
            return

        # 2. Ghi nhận lịch sử nộp bài thi
        elif path == '/api/history':
            title = payload.get("title", "Bài thi")
            total = int(payload.get("total", 0))
            correct = int(payload.get("correct", 0))
            score = float(payload.get("score", 0.0))
            duration = payload.get("duration", "0 giây")
            STORAGE.record_exam_history(title, total, correct, score, duration)
            self._send_json({"status": "ok"})
            return

        # 3. Cập nhật cài đặt
        elif path == '/api/settings':
            for k, v in payload.items():
                STORAGE.set_setting(k, v)
            self._send_json({"status": "ok", "settings": STORAGE.progress.get("settings", {})})
            return

        # 4. Xóa sạch sổ câu sai
        elif path == '/api/clear_wrong':
            STORAGE.clear_wrong_questions()
            self._send_json({"status": "ok", "wrong_count": 0})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Endpoint không tồn tại.")

def find_available_port(start_port: int = 8080, max_attempts: int = 20) -> int:
    """Tìm cổng mạng khả dụng, tránh xung đột nếu cổng 8080 đang bị chiếm dụng."""
    for p in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(('0.0.0.0', p))
                return p
            except OSError:
                continue
    return start_port


def start_server(port: int = 8080, open_browser: bool = False):
    """Khởi động máy chủ HTTP đa luồng và in mã QR ra Terminal."""
    port = find_available_port(port)
    local_ip = get_local_ip()
    local_url = f"http://localhost:{port}"
    mobile_url = f"http://{local_ip}:{port}"

    border = "═" * 74
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   CESBG VIỆT NAM - MÁY CHỦ WEB MOBILE ÔN THI TRÊN ĐIỆN THOẠI{Color.RESET}")
    print(f"{Color.GRAY}   Hệ thống máy chủ Zero-Dependency phục vụ ôn thi mọi lúc mọi nơi.{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

    print(f" 💻 {Color.BOLD}Truy cập trên Máy Tính:{Color.RESET} {Color.BRIGHT_GREEN}{local_url}{Color.RESET}")
    print(f" 📱 {Color.BOLD}Truy cập trên Điện Thoại (Cùng Wi-Fi):{Color.RESET} {Color.BOLD}{Color.BRIGHT_YELLOW}{mobile_url}{Color.RESET}\n")

    print(f"{Color.CYAN}👉 QUÉT MÃ QR DƯỚI ĐÂY BẰNG CAMERA ĐIỆN THOẠI ĐỂ MỞ NGAY:{Color.RESET}")
    print_qr_code(mobile_url)
    print(f"\n{Color.GRAY}Nhấn Ctrl+C để dừng máy chủ bất cứ lúc nào.{Color.RESET}\n")

    if open_browser:
        try:
            import webbrowser
            webbrowser.open(local_url)
        except Exception:
            pass

    server_address = ('0.0.0.0', port)
    httpd = ThreadingHTTPServer(server_address, QAWebHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}[*] Đang dừng Web Server...{Color.RESET}")
        httpd.shutdown()
        print(f"{Color.GREEN}[✔] Máy chủ đã tắt an toàn.{Color.RESET}\n")


if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    start_server(port, open_browser=False)

