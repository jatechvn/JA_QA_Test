#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ui/views.py - Quản lý hiển thị các màn hình giao diện CLI nâng cao:
Menu chính, Giao diện câu hỏi trắc nghiệm, Flashcard tự luận,
Ma trận câu hỏi 60 ô vuông (Grid Map), Cắm cờ câu hỏi phân vân [F],
Đồng hồ đếm ngược thời gian thực, Màn hình xác nhận nộp bài,
Màn hình phản hồi tức thì (kèm âm thanh winsound), Bảng tổng kết kết quả,
Tra cứu nhanh (Cheatsheet) và Cài đặt.
"""

import re
import shutil
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from ui.terminal import (
    Color, clear_screen, display_width, draw_box, get_single_key,
    get_text_input, get_essay_input, get_multi_choice_input, pad_display, pause,
    truncate_display, play_sound, wrap_display
)


def get_terminal_width(fallback: int = 76, max_w: int = 100) -> int:
    """Tự động tính toán độ rộng hiển thị thích ứng khi người dùng phóng lớn cửa sổ Terminal."""
    try:
        cols = shutil.get_terminal_size((80, 24)).columns
        return min(max_w, max(72, cols - 2))
    except Exception:
        return fallback


def render_progress_bar(current: int, total: int, width: int = 24) -> str:
    """Tạo thanh tiến trình Unicode: [████████░░░░░░░░] 50%"""
    if total <= 0:
        return ""
    pct = min(1.0, max(0.0, current / total))
    filled = int(width * pct)
    empty = width - filled
    bar = f"{Color.BRIGHT_GREEN}{'█' * filled}{Color.GRAY}{'░' * empty}{Color.RESET}"
    return f"[{bar}] {int(pct * 100)}%"


def clean_question_title(text: str) -> str:
    """Loại bỏ tiền tố 'Câu X:' và dấu ngoặc trống '( )' ở cuối câu hỏi."""
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r'^Câu\s+\d+[:\.]\s*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'[\(（]\s*[\)）]\s*$', '', t)
    return t.strip()


def show_main_menu(
    stats: Dict[str, Any],
    wrong_count: int,
    settings: Dict[str, Any],
    role_info: Optional[Dict[str, str]] = None,
    bank_total: int = 201
) -> str:
    """Hiển thị màn hình Menu chính hỗ trợ đa vai trò."""
    clear_screen()
    w = get_terminal_width()
    border = "═" * w
    role_title = role_info.get("title", "Tổ Trưởng (周边组长)") if role_info else "Tổ Trưởng (周边组长)"
    role_icon = role_info.get("icon", "👑") if role_info else "👑"

    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   CESBG VIỆT NAM - HỆ THỐNG ÔN THI XÉT THĂNG CHỨC 2026{Color.RESET}")
    print(f"   {Color.BOLD}{Color.BRIGHT_GREEN}[ĐANG ÔN: {role_icon} {role_title.upper()} - {bank_total} CÂU HỎI]{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")

    theme_name = settings.get("theme", "dark").upper()
    shuffle_stat = f"{Color.GREEN}BẬT{Color.RESET}" if settings.get("shuffle_options") else f"{Color.GRAY}TẮT{Color.RESET}"
    instant_stat = f"{Color.GREEN}BẬT{Color.RESET}" if settings.get("instant_feedback") else f"{Color.GRAY}TẮT{Color.RESET}"
    sound_stat = f"{Color.GREEN}BẬT{Color.RESET}" if settings.get("sound", True) else f"{Color.GRAY}TẮT{Color.RESET}"
    wrong_badge = f"{Color.BRIGHT_RED}{wrong_count} câu{Color.RESET}" if wrong_count > 0 else f"{Color.GREEN}0 câu (Tuyệt vời!){Color.RESET}"

    print(f" 📊 {Color.BOLD}Thống kê học tập:{Color.RESET} Đã làm: {Color.BRIGHT_WHITE}{stats.get('total_answered', 0)}{Color.RESET} câu "
          f"| Đúng: {Color.BRIGHT_GREEN}{stats.get('total_correct', 0)}{Color.RESET} "
          f"| Sổ câu sai: {wrong_badge}")
    print(f" ⚙️  {Color.BOLD}Cài đặt hiện tại:{Color.RESET} Theme: {Color.CYAN}{theme_name}{Color.RESET} "
          f"| Đảo đáp án: {shuffle_stat} | Phản hồi tức thì: {instant_stat} | Âm thanh: {sound_stat}")
    print(f"{Color.BRIGHT_CYAN}{'─' * w}{Color.RESET}\n")

    print(f" {Color.BRIGHT_YELLOW}[1]{Color.RESET} {Color.BOLD}Luyện tập Đề Thi Chuẩn Mẫu Số 1{Color.RESET} (60 câu chuẩn theo đề thi thật)")
    print(f" {Color.BRIGHT_YELLOW}[2]{Color.RESET} {Color.BOLD}Ôn tập Ngân Hàng Đề Gốc theo Chuyên Đề{Color.RESET} ({bank_total} câu đầy đủ đáp án)")
    print(f" {Color.BRIGHT_YELLOW}[3]{Color.RESET} {Color.BOLD}Tạo Đề Thi Thử Ngẫu Nhiên Mới{Color.RESET} (Sinh tự động 60 câu / 100 điểm)")
    print(f" {Color.BRIGHT_YELLOW}[4]{Color.RESET} {Color.BOLD}Sổ Tay Luyện Câu Hay Sai (Spaced Repetition){Color.RESET} [{wrong_badge}]")
    print(f" {Color.BRIGHT_YELLOW}[5]{Color.RESET} {Color.BOLD}Tra Cứu Nhanh Ngân Hàng Câu Hỏi & Đáp Án{Color.RESET} (Tìm theo từ khóa)")
    print(f" {Color.BRIGHT_YELLOW}[6]{Color.RESET} {Color.BOLD}Cài Đặt Tùy Chọn (Theme, Âm thanh, Đảo đáp án){Color.RESET}")
    print(f" {Color.BRIGHT_YELLOW}[7]{Color.RESET} {Color.BOLD}Khởi Động Web Server Mobile{Color.RESET} (Quét QR Code học trên Điện Thoại / Wi-Fi)")
    print(f" {Color.BRIGHT_YELLOW}[8]{Color.RESET} {Color.BOLD}Phân Tích Điểm Yếu & Xuất Đề Thi Word (.docx){Color.RESET} (In ấn đề thi giấy)")
    print(f" {Color.BRIGHT_MAGENTA}[9]{Color.RESET} {Color.BOLD}🔄 Đổi Vai Trò Ôn Thi (👑 Tổ Trưởng ⇋ ⚡ Chuyền Trưởng){Color.RESET}")
    print(f" {Color.BRIGHT_RED}[0]{Color.RESET} Thoát chương trình\n")

    valid_choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    return get_single_key(f"{Color.BRIGHT_GREEN}👉 Chọn chức năng [1-9, 0]: {Color.RESET}", valid_choices, default_key="1")


def show_topic_menu(counts: Optional[Dict[str, int]] = None, total: int = 201) -> str:
    """Hiển thị menu chọn chuyên đề ôn tập động theo số lượng câu của vai trò."""
    if not counts:
        counts = {"single_choice": 92, "multi_choice": 57, "true_false": 32, "short_answer": 12, "case_study": 8}
    sc = counts.get("single_choice", 0)
    mc = counts.get("multi_choice", 0)
    tf = counts.get("true_false", 0)
    sa = counts.get("short_answer", 0)
    cs = counts.get("case_study", 0)

    clear_screen()
    border = "═" * 74
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   ÔN TẬP THEO CHUYÊN ĐỀ - NGÂN HÀNG CÂU HỎI GỐC ({total} CÂU){Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

    print(f" {Color.BRIGHT_YELLOW}[1]{Color.RESET} Phần I: Trắc nghiệm một đáp án đúng ({sc} câu)")
    print(f" {Color.BRIGHT_YELLOW}[2]{Color.RESET} Phần II: Trắc nghiệm nhiều đáp án đúng ({mc} câu)")
    print(f" {Color.BRIGHT_YELLOW}[3]{Color.RESET} Phần III: Phán đoán Đúng / Sai ({tf} câu)")
    print(f" {Color.BRIGHT_YELLOW}[4]{Color.RESET} Phần IV: Trả lời ngắn gọn ({sa} câu - Chế độ Tự luận & Flashcard)")
    print(f" {Color.BRIGHT_YELLOW}[5]{Color.RESET} Phần V: Phân tích tình huống ({cs} câu - Xử lý sự cố thực tế)")
    print(f" {Color.BRIGHT_YELLOW}[6]{Color.RESET} Toàn bộ Ngân hàng câu hỏi ngẫu nhiên ({total} câu)")
    print(f" {Color.BRIGHT_RED}[0]{Color.RESET} Quay lại Menu chính\n")

    valid_choices = ["1", "2", "3", "4", "5", "6", "0"]
    return get_single_key(f"{Color.BRIGHT_GREEN}👉 Chọn phần muốn ôn [1-6, 0]: {Color.RESET}", valid_choices, default_key="1")


def render_quiz_header(
    exam_title: str,
    current_idx: int,
    total_count: int,
    answered_count: int,
    flagged_count: int,
    score: float,
    remaining_seconds: Optional[int] = None,
    is_flagged: bool = False
):
    """Hiển thị tiêu đề, đồng hồ đếm ngược, tiến trình và cờ câu hỏi."""
    clear_screen()
    border = "═" * 74
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
    
    # Dòng 1: Tiêu đề + Đồng hồ đếm ngược
    timer_str = ""
    if remaining_seconds is not None:
        rem = max(0, remaining_seconds)
        mins, secs = divmod(rem, 60)
        t_color = Color.BRIGHT_RED if rem < 300 else Color.BRIGHT_YELLOW
        timer_str = f" | {t_color}⏱ Còn lại: {mins:02d}:{secs:02d}{Color.RESET}"
    
    flag_badge = f" {Color.BOLD}{Color.BRIGHT_YELLOW}[⚑ ĐÃ CẮM CỜ]{Color.RESET}" if is_flagged else ""
    print(f"{Color.BOLD}{Color.BRIGHT_WHITE}   {exam_title.upper()}{timer_str}{flag_badge}{Color.RESET}")
    
    # Dòng 2: Thanh tiến trình + thống kê chi tiết
    prog = render_progress_bar(answered_count, total_count)
    info_line = (
        f" Câu {Color.BRIGHT_YELLOW}{current_idx}{Color.RESET}/{Color.BRIGHT_WHITE}{total_count}{Color.RESET} {prog} "
        f"| Đã làm: {Color.BRIGHT_GREEN}{answered_count}{Color.RESET}/{total_count} "
        f"| ⚑ Cờ: {Color.BRIGHT_YELLOW}{flagged_count}{Color.RESET} "
        f"| Điểm: {Color.BRIGHT_CYAN}{score:.1f}{Color.RESET}"
    )
    print(f"   {info_line}")
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")


def show_question_matrix(total_count: int, user_answers: Dict[int, Any], flagged_set: Set[int], current_idx: int) -> Optional[int]:
    """
    Hiển thị bảng ma trận câu hỏi và cho phép nhảy câu:
    - Sử dụng các phím mũi tên [←] [→] [↑] [↓] (hoặc A, D, W, S) để di chuyển ô chọn.
    - Nhấn phím [Space] hoặc [Enter] để xác nhận nhảy tới câu đang chọn.
    - Gõ trực tiếp số câu (1-60) hoặc nhấn [Q] / [Esc] để đóng ma trận.
    """
    selected = current_idx
    w = get_terminal_width()
    cols = 10
    num_buffer = ""

    while True:
        clear_screen()
        border = "═" * w
        print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   MA TRẬN TIẾN ĐỘ BÀI THI ({total_count} CÂU HỎI){Color.RESET}")
        print(f"{Color.GRAY}   Ký hiệu: {Color.BRIGHT_GREEN}[01✔]{Color.GRAY} Đã làm  |  {Color.BRIGHT_YELLOW}[02⚑]{Color.GRAY} Cắm cờ  |  {Color.BOLD}{Color.BG_BLUE}{Color.BRIGHT_WHITE}[>03<]{Color.RESET}{Color.GRAY} Đang chọn  |  {Color.GRAY}[04 ] Chưa làm{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

        for i in range(1, total_count + 1):
            if i == selected:
                cell = f"{Color.BOLD}{Color.BG_BLUE}{Color.BRIGHT_WHITE}[>{i:02d}<]{Color.RESET}"
            elif i == current_idx:
                cell = f"{Color.BOLD}{Color.CYAN}[*{i:02d}*]{Color.RESET}"
            elif i in flagged_set:
                cell = f"{Color.BOLD}{Color.BRIGHT_YELLOW}[{i:02d}⚑]{Color.RESET}"
            elif i in user_answers and user_answers[i] is not None:
                cell = f"{Color.BRIGHT_GREEN}[{i:02d}✔]{Color.RESET}"
            else:
                cell = f"{Color.GRAY}[{i:02d} ]{Color.RESET}"

            print(f" {cell} ", end="")
            if i % cols == 0 or i == total_count:
                print("\n")

        print(f"{Color.BRIGHT_CYAN}{'─' * w}{Color.RESET}")
        print(f" 🎮 {Color.BOLD}Phím di chuyển:{Color.RESET} {Color.CYAN}[←] [→] [↑] [↓]{Color.RESET} (hoặc {Color.CYAN}W, A, S, D{Color.RESET}) để chọn câu hỏi.")
        print(f" ⚡ {Color.BOLD}Xác nhận nhảy câu:{Color.RESET} Nhấn {Color.BRIGHT_GREEN}[Space]{Color.RESET} hoặc {Color.BRIGHT_GREEN}[Enter]{Color.RESET} để nhảy tới {Color.BOLD}{Color.BRIGHT_CYAN}Câu {selected}{Color.RESET}.")
        print(f" 🔢 {Color.GRAY}(Hoặc gõ trực tiếp số 1-{total_count} | Nhấn [Q] / [Esc] để đóng ma trận){Color.RESET}")
        if num_buffer:
            print(f"    {Color.YELLOW}Đang nhập số câu: {num_buffer}_{Color.RESET}")

        if sys.platform == 'win32':
            try:
                import msvcrt
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    arrow = msvcrt.getwch()
                    num_buffer = ""
                    if arrow == 'H':    # Up
                        selected = max(1, selected - cols)
                    elif arrow == 'P':  # Down
                        selected = min(total_count, selected + cols)
                    elif arrow == 'K':  # Left
                        selected = max(1, selected - 1)
                    elif arrow == 'M':  # Right
                        selected = min(total_count, selected + 1)
                    continue

                if ch in (' ', '\r', '\n'):
                    if num_buffer.isdigit():
                        target = int(num_buffer)
                        if 1 <= target <= total_count:
                            return target
                    return selected

                elif ch in ('w', 'W'):
                    num_buffer = ""
                    selected = max(1, selected - cols)
                elif ch in ('s', 'S') and not num_buffer:
                    selected = min(total_count, selected + cols)
                elif ch in ('a', 'A') and not num_buffer:
                    selected = max(1, selected - 1)
                elif ch in ('d', 'D') and not num_buffer:
                    selected = min(total_count, selected + 1)
                elif ch in ('q', 'Q', '\x1b'):
                    return None
                elif ch.isdigit():
                    num_buffer += ch
                    if int(num_buffer) > total_count:
                        num_buffer = ch
                    target = int(num_buffer)
                    if 1 <= target <= total_count:
                        selected = target
                elif ch == '\x08':
                    if num_buffer:
                        num_buffer = num_buffer[:-1]
                        if num_buffer.isdigit() and 1 <= int(num_buffer) <= total_count:
                            selected = int(num_buffer)
            except Exception:
                pass
        else:
            ans = input(f"{Color.BRIGHT_GREEN}👉 Nhập số câu hoặc nhấn Enter (câu {selected}): {Color.RESET}").strip()
            if not ans:
                return selected
            if ans.isdigit() and 1 <= int(ans) <= total_count:
                return int(ans)
            return None


def show_submit_confirmation(total_count: int, answered_count: int, flagged_count: int, remaining_seconds: Optional[int] = None) -> bool:
    """Màn hình kiểm tra và xác nhận nộp bài sớm."""
    clear_screen()
    border = "═" * 74
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}                   KIỂM TRA & XÁC NHẬN NỘP BÀI THI{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

    unanswered = total_count - answered_count
    print(f"  • Tổng số câu hỏi:    {Color.BRIGHT_WHITE}{total_count}{Color.RESET} câu")
    print(f"  • Số câu đã làm:      {Color.BRIGHT_GREEN}{answered_count}{Color.RESET} câu")
    
    if unanswered > 0:
        print(f"  • Số câu CHƯA LÀM:    {Color.BOLD}{Color.BRIGHT_RED}{unanswered}{Color.RESET} câu  ⚠️ {Color.YELLOW}(Các câu chưa làm sẽ bị tính 0 điểm!){Color.RESET}")
    else:
        print(f"  • Số câu CHƯA LÀM:    {Color.BRIGHT_GREEN}0{Color.RESET} câu (Đã hoàn thành 100%!)")
        
    if flagged_count > 0:
        print(f"  • Số câu ĐANG CẮM CỜ: {Color.BRIGHT_YELLOW}{flagged_count}{Color.RESET} câu  ⚑ {Color.GRAY}(Các câu bạn từng phân vân){Color.RESET}")
        
    if remaining_seconds is not None:
        mins, secs = divmod(max(0, remaining_seconds), 60)
        print(f"  • Thời gian còn lại:  {Color.BRIGHT_CYAN}{mins:02d} phút {secs:02d} giây{Color.RESET}")
        
    print(f"\n{Color.BRIGHT_CYAN}{'─' * 74}{Color.RESET}\n")
    print(f"  {Color.BRIGHT_GREEN}[Y]{Color.RESET} Nộp bài ngay và xem kết quả chấm điểm")
    print(f"  {Color.BRIGHT_RED}[N]{Color.RESET} Tiếp tục làm bài (Quay lại câu hỏi)\n")
    
    choice = get_single_key(f"{Color.BRIGHT_GREEN}👉 Bạn có chắc chắn muốn NỘP BÀI? [Y/N]: {Color.RESET}", ["Y", "y", "N", "n"], default_key="N")
    return choice.upper() == "Y"


def display_choice_question(question: Dict[str, Any], current_idx: int, total_count: int, is_flagged: bool = False, cur_ans: str = "") -> str:
    """Hiển thị câu hỏi trắc nghiệm (1 đáp án hoặc nhiều đáp án) kèm thanh điều hướng."""
    q_type = question.get("type")
    q_text = question.get("question", "").strip()
    options = question.get("display_options", question.get("options", []))

    clean_q = clean_question_title(q_text)
    flag_mark = f" {Color.BRIGHT_YELLOW}⚑{Color.RESET}" if is_flagged else ""
    print(wrap_display(f"{Color.BOLD}{Color.BRIGHT_WHITE}Câu {current_idx}:{Color.RESET}{flag_mark} {Color.BOLD}{clean_q}{Color.RESET}\n"))

    valid_letters = []
    for opt in options:
        letter = opt[:1].upper()
        if letter in ("A", "B", "C", "D", "E", "F"):
            valid_letters.append(letter)
        # Highlight nếu câu này đã được trả lời trước đó
        is_selected = letter in cur_ans if cur_ans else False
        prefix = f"{Color.BOLD}{Color.BRIGHT_YELLOW}➔ {Color.RESET}" if is_selected else "  "
        print(wrap_display(f"{prefix}{Color.BRIGHT_CYAN}{opt[:2]}{Color.RESET} {opt[2:].strip()}", subsequent_indent="     "))
    print()

    if cur_ans:
        print(f"  {Color.GRAY}Đã chọn trước đó: {Color.BRIGHT_GREEN}[{cur_ans}]{Color.RESET}\n")

    # Hiển thị thanh điều hướng TUI
    nav_line = (
        f"{Color.GRAY}Phím tắt: {Color.BRIGHT_YELLOW}[F]{Color.GRAY} Cắm cờ ⚑  "
        f"| {Color.CYAN}[P]{Color.GRAY} Lùi  | {Color.CYAN}[N]{Color.GRAY} Kế tiếp  "
        f"| {Color.CYAN}[M]{Color.GRAY} Ma trận  | {Color.BRIGHT_GREEN}[S]{Color.GRAY} Nộp bài  "
        f"| {Color.RED}[Q]{Color.GRAY} Thoát{Color.RESET}"
    )
    print(wrap_display(nav_line))

    if q_type == "single_choice":
        valid_keys = valid_letters + ["F", "f", "P", "p", "N", "n", "M", "m", "S", "s", "Q", "q"]
        prompt = f"{Color.BRIGHT_GREEN}👉 Chọn ({'/'.join(valid_letters)}) hoặc phím tắt: {Color.RESET}"
        ans = get_single_key(prompt, valid_keys, default_key=valid_letters[0] if valid_letters else "A")
        return ans.upper()
    else:
        # Multiple choice: hỗ trợ Space như Enter
        print(f"{Color.YELLOW}💡 Câu hỏi có NHIỀU đáp án đúng. Gõ các chữ cái (ví dụ: ACD) rồi nhấn [Space] hoặc [Enter]{Color.RESET}")
        prompt = f"{Color.BRIGHT_GREEN}👉 Nhập đáp án (hoặc gõ F/P/N/M/S/Q): {Color.RESET}"
        ans = get_multi_choice_input(prompt, valid_letters=valid_letters)
        return ans.upper().strip()


def display_true_false_question(question: Dict[str, Any], current_idx: int, total_count: int, is_flagged: bool = False, cur_ans: str = "") -> str:
    """Hiển thị câu hỏi phán đoán Đúng / Sai kèm thanh điều hướng."""
    q_text = question.get("question", "").strip()
    clean_q = clean_question_title(q_text)
    flag_mark = f" {Color.BRIGHT_YELLOW}⚑{Color.RESET}" if is_flagged else ""
    print(f"{Color.BOLD}{Color.BRIGHT_WHITE}Câu {current_idx}: [Đúng / Sai]{Color.RESET}{flag_mark}\n")
    print(wrap_display(f"  \"{Color.BRIGHT_YELLOW}{clean_q}{Color.RESET}\"\n", subsequent_indent="  "))

    p1 = f"{Color.BOLD}{Color.BRIGHT_YELLOW}➔ {Color.RESET}" if cur_ans == "V" else "  "
    p2 = f"{Color.BOLD}{Color.BRIGHT_YELLOW}➔ {Color.RESET}" if cur_ans == "X" else "  "
    print(f"{p1}{Color.BRIGHT_GREEN}[V]{Color.RESET} Đúng (Quy định đúng / Nhận định chính xác)")
    print(f"{p2}{Color.BRIGHT_RED}[X]{Color.RESET} Sai  (Quy định sai / Nhận định không chính xác)\n")

    if cur_ans:
        ans_lbl = "ĐÚNG" if cur_ans == "V" else "SAI"
        print(f"  {Color.GRAY}Đã chọn trước đó: {Color.BRIGHT_GREEN}[{cur_ans} - {ans_lbl}]{Color.RESET}\n")

    nav_line = (
        f"{Color.GRAY}Phím tắt: {Color.BRIGHT_YELLOW}[F]{Color.GRAY} Cắm cờ ⚑  "
        f"| {Color.CYAN}[P]{Color.GRAY} Lùi  | {Color.CYAN}[N]{Color.GRAY} Kế tiếp  "
        f"| {Color.CYAN}[M]{Color.GRAY} Ma trận  | {Color.BRIGHT_GREEN}[S]{Color.GRAY} Nộp bài  "
        f"| {Color.RED}[Q]{Color.GRAY} Thoát{Color.RESET}"
    )
    print(wrap_display(nav_line))

    valid_keys = ["V", "v", "X", "x", "1", "2", "F", "f", "P", "p", "N", "n", "M", "m", "S", "s", "Q", "q"]
    prompt = f"{Color.BRIGHT_GREEN}👉 Chọn [V/X] hoặc phím tắt: {Color.RESET}"
    ans = get_single_key(prompt, valid_keys, default_key="V")
    if ans in ("1", "V", "v"):
        return "V"
    elif ans in ("2", "X", "x"):
        return "X"
    return ans.upper()


def display_flashcard_question(question: Dict[str, Any], current_idx: int, total_count: int, is_flagged: bool = False, cur_ans: str = "") -> str:
    """Hiển thị câu hỏi tự luận / tình huống, cho phép gõ câu trả lời để đối soát trực tiếp."""
    q_type = question.get("type")
    q_text = question.get("question", "").strip()
    ans_content = question.get("answer", "")

    type_badge = "TRẢ LỜI NGẮN GỌN" if q_type == "short_answer" else "PHÂN TÍCH TÌNH HUỐNG"
    flag_mark = f" {Color.BRIGHT_YELLOW}⚑{Color.RESET}" if is_flagged else ""
    print(f"{Color.BOLD}{Color.BRIGHT_CYAN}[{type_badge}] - Câu {current_idx}:{Color.RESET}{flag_mark}\n")

    clean_lines = [clean_question_title(line) for line in q_text.split("\n") if line.strip()]
    for line in clean_lines:
        print(wrap_display(f"  {Color.BRIGHT_WHITE}{line}{Color.RESET}", subsequent_indent="  "))
    print()

    nav_line = (
        f"{Color.GRAY}Phím tắt nhanh: {Color.BRIGHT_YELLOW}[F]{Color.GRAY} Cắm cờ  "
        f"| {Color.CYAN}[P]{Color.GRAY} Lùi  | {Color.CYAN}[N]{Color.GRAY} Kế tiếp  "
        f"| {Color.CYAN}[M]{Color.GRAY} Ma trận  | {Color.BRIGHT_GREEN}[S]{Color.GRAY} Nộp  "
        f"| {Color.RED}[Q]{Color.GRAY} Thoát{Color.RESET}"
    )
    print(wrap_display(nav_line))
    
    print(f"\n{Color.YELLOW}💡 Bạn có thể gõ câu trả lời của mình bên dưới để đối soát so sánh với đáp án chuẩn.")
    print(f"   (Nhấn [Shift+Enter] để xuống dòng viết đoạn văn, nhấn [Enter] để lật đáp án){Color.RESET}")
    prompt = f"{Color.BRIGHT_GREEN}✍️  Nhập câu trả lời (hoặc gõ F/P/N/M/S/Q): {Color.RESET}"
    user_input = get_essay_input(prompt, default="").strip()
    
    if user_input.upper() in ("F", "P", "N", "M", "S", "Q"):
        return user_input.upper()

    # Hiện bảng đối soát trực quan
    print(f"\n{Color.BRIGHT_CYAN}╔════════════════════════════════════════════════════════════════════════╗{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}║{Color.RESET}{Color.BOLD}{Color.BRIGHT_YELLOW}                    BẢNG ĐỐI SOÁT KẾT QUẢ TỰ LUẬN                       {Color.RESET}{Color.BRIGHT_CYAN}║{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}╠════════════════════════════════════════════════════════════════════════╣{Color.RESET}")
    
    # 1. Câu trả lời của học viên
    print(f"  {Color.BOLD}{Color.BRIGHT_WHITE}✍️  CÂU TRẢ LỜI CỦA BẠN:{Color.RESET}")
    if user_input:
        print(wrap_display(f"     {Color.CYAN}{user_input}{Color.RESET}", subsequent_indent="     "))
    else:
        print(f"     {Color.GRAY}(Bạn đã chọn xem đáp án trực tiếp mà không ghi chú){Color.RESET}")
    print()

    # 2. Đáp án chuẩn tham khảo
    print(f"  {Color.BOLD}{Color.BRIGHT_GREEN}📖  ĐÁP ÁN CHUẨN THAM KHẢO:{Color.RESET}")
    if isinstance(ans_content, list):
        for line in ans_content:
            print(wrap_display(f"     {Color.BRIGHT_YELLOW}•{Color.RESET} {line}", subsequent_indent="       "))
    else:
        print(wrap_display(f"     {ans_content}", subsequent_indent="     "))
    print(f"{Color.BRIGHT_CYAN}╚════════════════════════════════════════════════════════════════════════╝{Color.RESET}\n")

    print(f"  {Color.BRIGHT_GREEN}[1]{Color.RESET} Đã nắm vững / Khớp ý chính (+100% điểm)")
    print(f"  {Color.BRIGHT_RED}[2]{Color.RESET} Chưa khớp / Cần ôn lại thêm (0 điểm, lưu vào sổ câu sai)\n")

    valid_keys = ["1", "2", "F", "f", "P", "p", "N", "n", "M", "m", "S", "s", "Q", "q"]
    ans = get_single_key(f"{Color.BRIGHT_GREEN}👉 Tự đánh giá mức độ chính xác của bạn [1 hoặc 2]: {Color.RESET}", valid_keys, default_key="1")
    return ans.upper()


def show_instant_feedback(is_correct: bool, user_ans: str, correct_ans: str, question: Dict[str, Any], sound_enabled: bool = True):
    """Hiển thị phản hồi tức thì và phát âm thanh tương tác."""
    print()
    if is_correct:
        play_sound("correct", sound_enabled)
        print(f"  {Color.BRIGHT_GREEN}✔ CHÍNH XÁC! Tuyệt vời! 🎉{Color.RESET}")
    else:
        play_sound("wrong", sound_enabled)
        print(f"  {Color.BRIGHT_RED}✖ CHƯA ĐÚNG!{Color.RESET}")
        print(f"  Bạn đã chọn: {Color.RED}[{user_ans}]{Color.RESET}  ➔  Đáp án đúng là: {Color.BOLD}{Color.BRIGHT_GREEN}[{correct_ans}]{Color.RESET}")
        
        options = question.get("display_options", question.get("options", []))
        if options and question.get("type") in ("single_choice", "multi_choice"):
            print(f"  {Color.GRAY}Nội dung đáp án đúng:{Color.RESET}")
            for opt in options:
                letter = opt[:1].upper()
                if letter in correct_ans:
                    print(wrap_display(f"    {Color.BRIGHT_GREEN}✔ {opt}{Color.RESET}", subsequent_indent="      "))

        print(f"  {Color.DIM}{Color.YELLOW}📌 (Câu hỏi này đã được tự động lưu vào 'Sổ tay câu sai' để bạn ôn lại!){Color.RESET}")

    pause("👉 Nhấn phím bất kỳ để chuyển sang câu tiếp theo...")


def show_exam_summary(exam_title: str, total: int, correct: int, score: float, elapsed_time: str, wrong_list: List[Dict[str, Any]], sound_enabled: bool = True):
    """Hiển thị bảng tổng kết kết quả thi/ôn tập đẹp mắt theo chuẩn box-drawing."""
    clear_screen()
    play_sound("finish", sound_enabled)
    border = "═" * 74
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}                   KẾT QUẢ ÔN THI / THI THỬ{Color.RESET}")
    print(f"{Color.GRAY}   Chương trình: {exam_title} | Thời gian làm bài: {elapsed_time}{Color.RESET}")
    print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

    pct = (correct / total * 100) if total > 0 else 0

    if pct >= 90:
        badge = f"{Color.BRIGHT_GREEN}★★★★★ XUẤT SẮC - SẴN SÀNG THI THĂNG CHỨC!{Color.RESET}"
    elif pct >= 75:
        badge = f"{Color.BRIGHT_GREEN}✔ ĐẠT TIÊU CHUẨN TỔ TRƯỞNG CESBG (Điểm an toàn){Color.RESET}"
    elif pct >= 60:
        badge = f"{Color.YELLOW}⚠ ĐẠT MỨC TỐI THIỂU (Nên ôn tập thêm các câu sai){Color.RESET}"
    else:
        badge = f"{Color.BRIGHT_RED}✖ CHƯA ĐẠT (Dưới 60 điểm - Cần luyện kỹ các phần){Color.RESET}"

    w_box = 70
    print(f"{Color.BRIGHT_WHITE}┌{'─' * w_box}┐{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}│{Color.RESET} {pad_display(f'Tổng số câu hỏi: {total}', w_box - 2)} {Color.BRIGHT_WHITE}│{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}│{Color.RESET} {pad_display(f'Số câu trả lời đúng: {Color.BRIGHT_GREEN}{correct}{Color.RESET} câu ({pct:.1f}%)', w_box - 2 + len(Color.BRIGHT_GREEN) + len(Color.RESET))} {Color.BRIGHT_WHITE}│{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}│{Color.RESET} {pad_display(f'Số câu trả lời sai: {Color.BRIGHT_RED}{total - correct}{Color.RESET} câu', w_box - 2 + len(Color.BRIGHT_RED) + len(Color.RESET))} {Color.BRIGHT_WHITE}│{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}│{Color.RESET} {pad_display(f'Tổng điểm đạt được: {Color.BOLD}{Color.BRIGHT_CYAN}{score:.1f}{Color.RESET}/100 điểm', w_box - 2 + len(Color.BOLD) + len(Color.BRIGHT_CYAN) + len(Color.RESET))} {Color.BRIGHT_WHITE}│{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}│{Color.RESET} {pad_display(f'Đánh giá kết quả: {badge}', w_box - 2 + len(badge) - 10)} {Color.BRIGHT_WHITE}│{Color.RESET}")
    print(f"{Color.BRIGHT_WHITE}└{'─' * w_box}┘{Color.RESET}\n")

    if wrong_list:
        print(f"{Color.BOLD}{Color.YELLOW}📋 Danh sách các câu cần lưu ý (Đã thêm vào Sổ câu sai):{Color.RESET}")
        for idx, item in enumerate(wrong_list[:8], 1):
            q_txt = item.get("question", "").replace("\n", " ")
            ans = item.get("correct_answer", item.get("answer", ""))
            print(f"  {idx}. {truncate_display(q_txt, 55)} ➔ Đ/A đúng: {Color.BRIGHT_GREEN}[{ans}]{Color.RESET}")
        if len(wrong_list) > 8:
            print(f"  {Color.GRAY}...và {len(wrong_list) - 8} câu khác trong Sổ tay câu sai.{Color.RESET}")
        print()

    pause("👉 Nhấn phím bất kỳ để trở về Menu chính...")


def show_search_view(storage):
    """Màn hình tra cứu nhanh ngân hàng câu hỏi."""
    while True:
        clear_screen()
        print(f"{Color.BRIGHT_CYAN}{'═' * 74}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   TRA CỨU NHANH NGÂN HÀNG CÂU HỎI & ĐÁP ÁN (CHEATSHEET){Color.RESET}")
        print(f"{Color.GRAY}   Nhập từ khóa bất kỳ (ví dụ: 'chữa cháy', '5why', 'xung đột', 'RBA', 'kỷ luật'){Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{'═' * 74}{Color.RESET}\n")

        kw = get_text_input(f"{Color.BRIGHT_GREEN}🔍 Nhập từ khóa cần tra cứu (hoặc gõ '0' để quay lại): {Color.RESET}")
        if kw == "0" or not kw.strip():
            break

        results = storage.search_questions(kw)
        print(f"\n{Color.BOLD}Tìm thấy {Color.BRIGHT_GREEN}{len(results)}{Color.RESET} kết quả phù hợp với từ khóa '{Color.BRIGHT_YELLOW}{kw}{Color.RESET}':\n")

        for idx, q in enumerate(results[:15], 1):
            q_type = q.get("type", "")
            q_sec = q.get("section", "")
            q_text = clean_question_title(q.get("question", ""))
            ans = q.get("answer", "")

            print(f"{Color.BRIGHT_CYAN}[{idx}] [{q_sec}]{Color.RESET}")
            print(f"  {Color.BOLD}Câu {idx}: {q_text}{Color.RESET}")
            
            if q_type in ("single_choice", "multi_choice"):
                for opt in q.get("options", []):
                    letter = opt[:1].upper()
                    if letter in str(ans):
                        print(f"    {Color.BRIGHT_GREEN}✔ {opt} (ĐÁP ÁN ĐÚNG){Color.RESET}")
                    else:
                        print(f"    {Color.GRAY}  {opt}{Color.RESET}")
            elif q_type == "true_false":
                ans_str = "V (ĐÚNG)" if ans == "V" else "X (SAI)"
                print(f"    ➔ Đáp án: {Color.BRIGHT_GREEN}{ans_str}{Color.RESET}")
            else:
                print(f"    {Color.BRIGHT_GREEN}➔ Đáp án tham khảo:{Color.RESET}")
                if isinstance(ans, list):
                    for a_line in ans[:5]:
                        print(f"      • {a_line}")
                else:
                    print(f"      {ans}")
            print(f"{Color.GRAY}{'─' * 70}{Color.RESET}")

        if len(results) > 15:
            print(f"{Color.YELLOW}⚠ Còn {len(results) - 15} kết quả nữa, vui lòng nhập từ khóa cụ thể hơn để lọc bớt.{Color.RESET}")

        pause("👉 Nhấn phím bất kỳ để tiếp tục tìm kiếm...")


def show_settings_view(storage):
    """Màn hình cấu hình tùy chọn."""
    while True:
        clear_screen()
        w = get_terminal_width()
        border = "═" * w
        print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   CÀI ĐẶT TÙY CHỌN & GIAO DIỆN{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

        cur_theme = storage.get_setting("theme", "dark")
        cur_shuffle = storage.get_setting("shuffle_options", False)
        cur_instant = storage.get_setting("instant_feedback", True)
        cur_sound = storage.get_setting("sound", True)

        theme_badge = f"{Color.BRIGHT_CYAN}Dark (Tối){Color.RESET}" if cur_theme == "dark" else f"{Color.YELLOW}Light (Sáng){Color.RESET}"
        shuffle_badge = f"{Color.BRIGHT_GREEN}ĐANG BẬT{Color.RESET}" if cur_shuffle else f"{Color.GRAY}ĐANG TẮT{Color.RESET}"
        instant_badge = f"{Color.BRIGHT_GREEN}ĐANG BẬT{Color.RESET}" if cur_instant else f"{Color.GRAY}ĐANG TẮT{Color.RESET}"
        sound_badge = f"{Color.BRIGHT_GREEN}ĐANG BẬT{Color.RESET}" if cur_sound else f"{Color.GRAY}ĐANG TẮT{Color.RESET}"
        wrong_count = len(storage.get_wrong_questions())

        print(f" [1] Đổi Theme Terminal: {theme_badge} (Chuyển đổi Dark/Light)")
        print(f" [2] Đảo thứ tự đáp án (Shuffle): {shuffle_badge} (Tránh học vẹt vị trí A/B/C/D)")
        print(f" [3] Phản hồi tức thì (Instant Feedback): {instant_badge} (Hiện đáp án đúng/sai ngay sau mỗi câu)")
        print(f" [4] Âm thanh tương tác (Sound Effects): {sound_badge} (Ting khi đúng, Bụp khi sai)")
        print(f" [5] Xóa sạch Sổ tay câu sai ({Color.BRIGHT_RED}{wrong_count} câu{Color.RESET})")
        print(f" [0] Quay lại Menu chính\n")
        print(f" {Color.GRAY}{'─' * w}{Color.RESET}")
        print(f" 💡 {Color.BRIGHT_CYAN}Mẹo phóng to chữ Terminal:{Color.RESET} Giữ phím {Color.BOLD}Ctrl + Lăn Chuột Lên{Color.RESET} (hoặc {Color.BOLD}Ctrl + Shift + '+'{Color.RESET}) để phóng to/thu nhỏ cỡ chữ tuỳ ý!")
        print(f" 🌐 {Color.BRIGHT_CYAN}Trên Web Mobile/PC:{Color.RESET} Dùng nút {Color.BOLD}[A-] [A+]{Color.RESET} hoặc bật {Color.BOLD}⚡ Tự động phóng lớn theo màn hình{Color.RESET}.\n")

        choice = get_single_key(f"{Color.BRIGHT_GREEN}👉 Chọn mục cần thay đổi [1-5, 0]: {Color.RESET}", ["1", "2", "3", "4", "5", "0"])

        if choice == "1":
            new_theme = "light" if cur_theme == "dark" else "dark"
            storage.set_setting("theme", new_theme)
            from ui.terminal import configure_theme
            configure_theme(new_theme)
        elif choice == "2":
            storage.set_setting("shuffle_options", not cur_shuffle)
        elif choice == "3":
            storage.set_setting("instant_feedback", not cur_instant)
        elif choice == "4":
            new_sound = not cur_sound
            storage.set_setting("sound", new_sound)
            play_sound("correct", new_sound)
        elif choice == "5":
            confirm = get_single_key("Bạn có chắc chắn muốn xóa toàn bộ sổ câu sai? [Y/N]: ", ["Y", "y", "N", "n"])
            if confirm.upper() == "Y":
                storage.clear_wrong_questions()
                print(f"\n{Color.GREEN}✔ Đã làm sạch Sổ tay câu sai!{Color.RESET}")
                time.sleep(1)
        elif choice == "0":
            break


def show_analytics_and_export_view(storage: Any, quiz_engine: Any) -> Optional[str]:
    """
    Giai đoạn 3: Màn hình phân tích năng lực chuyên sâu (Diagnostic Analytics)
    và trung tâm xuất đề thi sang file Word (.docx) chuyên nghiệp.
    Trả về section_key nếu người dùng muốn luyện cấp tốc phần yếu nhất, hoặc None.
    """
    from core.exporter import generate_weakness_report, export_exam_to_docx, get_exports_dir
    import os

    while True:
        clear_screen()
        report = generate_weakness_report(storage)
        border = "═" * 74
        print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}")
        print(f"{Color.BOLD}{Color.BRIGHT_YELLOW}   PHÂN TÍCH ĐIỂM YẾU CHUYÊN SÂU & XUẤT ĐỀ THI WORD (.DOCX){Color.RESET}")
        print(f"{Color.GRAY}   Hệ thống chẩn đoán năng lực học tập và trung tâm in ấn đề thi CESBG 2026.{Color.RESET}")
        print(f"{Color.BRIGHT_CYAN}{border}{Color.RESET}\n")

        # 1. Tổng quan chỉ số
        acc = report['overall_accuracy']
        acc_color = Color.BRIGHT_GREEN if acc >= 80 else (Color.BRIGHT_YELLOW if acc >= 60 else Color.BRIGHT_RED)
        print(f" 📊 {Color.BOLD}Chỉ số tổng quan:{Color.RESET} Đã thi: {Color.BOLD}{report['total_exams']}{Color.RESET} lần "
              f"| Đã làm: {Color.BOLD}{report['total_answered']}{Color.RESET} câu "
              f"| Tỷ lệ đúng: {acc_color}{acc}%{Color.RESET} "
              f"| Sổ câu sai: {Color.BRIGHT_RED}{report['total_wrong_active']}{Color.RESET} câu\n")

        # 2. Phân tích theo từng chuyên đề
        print(f" {Color.BOLD}Mức độ nắm vững theo 5 Chuyên đề:{Color.RESET}")
        for sec_k, sec_data in report['section_breakdown'].items():
            rate = sec_data['mastery_rate']
            lvl = sec_data['level']
            col = Color.BRIGHT_GREEN if sec_data['status_color'] == 'green' else (Color.BRIGHT_YELLOW if sec_data['status_color'] == 'yellow' else Color.BRIGHT_RED)
            
            bar_len = 15
            filled = int(rate / 100 * bar_len)
            bar_str = "█" * filled + "░" * (bar_len - filled)
            
            name = sec_data['name'].ljust(38)
            print(f"   • {name} [{col}{bar_str}{Color.RESET}] {col}{rate:5.1f}%{Color.RESET}  [{col}{lvl}{Color.RESET}]")

        # Cảnh báo điểm yếu
        weak_name = report['weakest_section_name']
        print(f"\n ⚠️  {Color.BOLD}Cảnh báo mảng kiến thức yếu nhất:{Color.RESET} {Color.BRIGHT_RED}{weak_name}{Color.RESET}")
        print(f"     {Color.GRAY}Khuyên bạn nên tập trung ôn chuyên đề này trước khi thi thật.{Color.RESET}\n")

        # 3. Menu thao tác
        print(f"{Color.BRIGHT_CYAN}{'─' * 74}{Color.RESET}")
        print(f" {Color.BRIGHT_YELLOW}[1]{Color.RESET} {Color.BOLD}Luyện cấp tốc chuyên đề yếu nhất ngay{Color.RESET} ({weak_name})")
        print(f" {Color.BRIGHT_YELLOW}[2]{Color.RESET} {Color.BOLD}Xuất Đề Thi Chuẩn Mẫu Số 1 ra Word (.docx){Color.RESET} (60 câu kèm Answer Key)")
        print(f" {Color.BRIGHT_YELLOW}[3]{Color.RESET} {Color.BOLD}Sinh Đề Thi Thử Ngẫu Nhiên Mới và Xuất Word (.docx){Color.RESET} (100 điểm chuẩn)")
        print(f" {Color.BRIGHT_YELLOW}[4]{Color.RESET} {Color.BOLD}Mở thư mục chứa file Word đã xuất (exports/){Color.RESET}")
        print(f" {Color.BRIGHT_RED}[0]{Color.RESET} Quay lại Menu chính\n")

        ch = get_single_key(f"{Color.BRIGHT_GREEN}👉 Chọn thao tác [1-4, 0]: {Color.RESET}", ["1", "2", "3", "4", "0"])

        if ch == "1":
            return report['weakest_section_key']

        elif ch == "2":
            print(f"\n{Color.CYAN}[*] Đang xuất Đề Thi Chuẩn Mẫu Số 1 sang định dạng Word (.docx)...{Color.RESET}")
            shuffle_opts = storage.get_setting("shuffle_options", False)
            questions = quiz_engine.prepare_exam_de1(shuffle_questions=True, shuffle_options=shuffle_opts)
            file_path = export_exam_to_docx(questions, "Đề Thi Chuẩn Mẫu Số 1 (Đảo Ngẫu Nhiên)")
            print(f"{Color.BRIGHT_GREEN}🎉 Xuất đề thi thành công!{Color.RESET}")
            print(f"   📁 Tệp Word: {Color.BOLD}{file_path.name}{Color.RESET}")
            print(f"   📂 Đường dẫn: {Color.GRAY}{file_path}{Color.RESET}\n")
            pause()

        elif ch == "3":
            print(f"\n{Color.CYAN}[*] Đang sinh đề thi thử ngẫu nhiên và xuất sang Word (.docx)...{Color.RESET}")
            shuffle_opts = storage.get_setting("shuffle_options", False)
            questions = quiz_engine.generate_mock_exam(shuffle_options=shuffle_opts)
            file_path = export_exam_to_docx(questions, "Đề Thi Thử Ngẫu Nhiên Mới (Chuẩn 100 Điểm)")
            print(f"{Color.BRIGHT_GREEN}🎉 Xuất đề thi thử thành công!{Color.RESET}")
            print(f"   📁 Tệp Word: {Color.BOLD}{file_path.name}{Color.RESET}")
            print(f"   📂 Đường dẫn: {Color.GRAY}{file_path}{Color.RESET}\n")
            pause()

        elif ch == "4":
            exp_dir = get_exports_dir()
            try:
                os.startfile(str(exp_dir))
                print(f"\n{Color.GREEN}✔ Đã mở thư mục: {exp_dir}{Color.RESET}")
            except Exception:
                print(f"\n{Color.YELLOW}Thư mục xuất file tại: {exp_dir}{Color.RESET}")
            time.sleep(1)

        elif ch == "0":
            return None
