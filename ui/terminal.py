#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ui/terminal.py - Thư viện hỗ trợ hiển thị giao diện Terminal đẹp mắt,
chuẩn ANSI, thích ứng nền Dark/Light, bắt phím bấm 1-chạm không cần Enter.
Thừa hưởng và tối ưu từ framework _py_sample/cli_app_template.py.
"""

import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# 1. Kích hoạt ANSI escape sequence và UTF-8 trên Windows console
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
            sys.stdin.reconfigure(encoding='utf-8')
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # ENABLE_PROCESSED_OUTPUT (1) | ENABLE_WRAP_AT_EOL_OUTPUT (2) | ENABLE_VIRTUAL_TERMINAL_PROCESSING (4)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


# 2. Bảng mã màu thích ứng (Adaptive Color Palette)
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    BRIGHT_RED = "\033[1;91m"
    BRIGHT_GREEN = "\033[1;92m"
    BRIGHT_YELLOW = "\033[1;93m"
    BRIGHT_BLUE = "\033[1;94m"
    BRIGHT_MAGENTA = "\033[1;95m"
    BRIGHT_CYAN = "\033[1;96m"
    BRIGHT_WHITE = "\033[1;97m"

    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"
    BG_DARK = "\033[48;5;236m"


_STYLE_CODES = {
    "RESET": "\033[0m", "BOLD": "\033[1m", "DIM": "\033[2m", "UNDERLINE": "\033[4m",
    "BG_BLUE": "\033[44m", "BG_GREEN": "\033[42m", "BG_RED": "\033[41m", "BG_DARK": "\033[48;5;236m"
}

_PALETTES = {
    "dark": {
        "BLACK": "\033[30m",
        "RED": "\033[91m", "GREEN": "\033[92m", "YELLOW": "\033[93m",
        "BLUE": "\033[94m", "MAGENTA": "\033[95m", "CYAN": "\033[96m", "WHITE": "\033[97m",
        "GRAY": "\033[90m",
        "BRIGHT_RED": "\033[1;91m", "BRIGHT_GREEN": "\033[1;92m", "BRIGHT_YELLOW": "\033[1;93m",
        "BRIGHT_BLUE": "\033[1;94m", "BRIGHT_MAGENTA": "\033[1;95m", "BRIGHT_CYAN": "\033[1;96m",
        "BRIGHT_WHITE": "\033[1;97m",
    },
    "light": {
        "BLACK": "\033[30m",
        "RED": "\033[31m", "GREEN": "\033[32m",
        "YELLOW": "\033[35m",
        "BLUE": "\033[34m", "MAGENTA": "\033[35m", "CYAN": "\033[36m", "WHITE": "\033[30m",
        "GRAY": "\033[90m",
        "BRIGHT_RED": "\033[1;31m", "BRIGHT_GREEN": "\033[1;32m",
        "BRIGHT_YELLOW": "\033[1;35m",
        "BRIGHT_BLUE": "\033[1;34m", "BRIGHT_MAGENTA": "\033[1;35m", "BRIGHT_CYAN": "\033[1;36m",
        "BRIGHT_WHITE": "\033[1;30m",
    },
}
_NO_COLOR_PALETTE = {name: "" for name in list(_PALETTES["dark"]) + list(_STYLE_CODES)}


def _detect_theme() -> str:
    val = os.environ.get("COLORFGBG")
    if val:
        try:
            bg = int(val.split(";")[-1])
            return "light" if bg in (7, 15) else "dark"
        except (ValueError, IndexError):
            pass
    return "dark"


def configure_theme(theme: Optional[str] = None, no_color: bool = False) -> str:
    if no_color or os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        palette, resolved = _NO_COLOR_PALETTE, "none"
    else:
        resolved = theme if theme in ("dark", "light") else _detect_theme()
        palette = dict(_STYLE_CODES)
        palette.update(_PALETTES[resolved])

    for name, code in palette.items():
        setattr(Color, name, code)
    return resolved


# 3. Thước đo độ rộng ký tự hiển thị (CJK, Emoji, Ký hiệu 2-cell)
_WIDE_RANGES = (
    (0x1100, 0x115F),
    (0x2600, 0x27BF),
    (0x2E80, 0xA4CF),
    (0xAC00, 0xD7A3),
    (0xF900, 0xFAFF),
    (0xFF00, 0xFF60),
    (0xFFE0, 0xFFE6),
    (0x1F300, 0x1FAFF),
)

_ANSI_RE = re.compile(r'\033\[[0-9;]*m')


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub('', text)


def display_width(text: str) -> int:
    clean = strip_ansi(text)
    width = 0
    for ch in clean:
        if unicodedata.combining(ch) or ch in ('\ufe0f', '\u200d'):
            continue
        code = ord(ch)
        width += 2 if any(lo <= code <= hi for lo, hi in _WIDE_RANGES) else 1
    return width


def wrap_display(text: str, width: Optional[int] = None, subsequent_indent: str = "") -> str:
    """Ngắt tại khoảng trắng, giữ màu ANSI và nguyên từ tiếng Việt."""
    if width is None:
        width = max(1, shutil.get_terminal_size(fallback=(80, 24)).columns - 1)
    width = max(1, width)
    result = []
    for paragraph in text.split('\n'):
        line = ""
        pending = ""
        for token in re.findall(r'\s+|\S+', paragraph):
            if token.isspace():
                pending += token
                continue
            if (display_width(line) > 0
                    and display_width(line + pending + token) > width):
                result.append(line)
                line = subsequent_indent + token
            else:
                line += pending + token
            pending = ""
        result.append(line + pending)
    return '\n'.join(result)


def pad_display(text: str, width: int) -> str:
    current_w = display_width(text)
    return text + " " * max(0, width - current_w)


def truncate_display(text: str, width: int, keep_tail: bool = False) -> str:
    if display_width(text) <= width:
        return text
    budget = max(0, width - 3)
    if keep_tail:
        out = ""
        for ch in reversed(text):
            if display_width(ch + out) > budget:
                break
            out = ch + out
        return "..." + out
    out = ""
    for ch in text:
        if display_width(out + ch) > budget:
            break
        out += ch
    return out + "..."


# 4. Nhập liệu 1 chạm tức thì (Instant Single Key Selection)
def get_single_key(prompt_text: str, valid_keys: Sequence[str], default_key: str = "1") -> str:
    """
    Bắt phím bấm đơn lập tức mà không cần nhấn Enter.
    Hỗ trợ Windows qua msvcrt.getwch().
    """
    print(wrap_display(prompt_text), end="", flush=True)
    valid_lower = [k.lower() for k in valid_keys]

    if sys.platform == 'win32':
        try:
            import msvcrt
            while True:
                ch = msvcrt.getwch()
                if ch in ('\r', '\n'):
                    print(f"{default_key}")
                    return default_key
                elif ch.lower() in valid_lower:
                    # Tìm key gốc đúng hoa/thường
                    idx = valid_lower.index(ch.lower())
                    res = valid_keys[idx]
                    print(f"{res}")
                    return res
                elif ch == '\x03':  # Ctrl+C
                    print()
                    raise KeyboardInterrupt
        except Exception:
            pass

    # Fallback cho terminal thông thường
    try:
        inp = input().strip()
        if not inp:
            return default_key
        for k in valid_keys:
            if inp.lower() == k.lower():
                return k
        return default_key
    except KeyboardInterrupt:
        print()
        raise


def get_text_input(prompt_text: str, default: str = "") -> str:
    """Nhập chuỗi văn bản (dùng cho tìm kiếm hoặc nhập câu trả lời tự luận)."""
    try:
        val = input(wrap_display(prompt_text)).strip()
        return val if val else default
    except KeyboardInterrupt:
        print()
        raise


def get_multi_choice_input(prompt_text: str, valid_letters: Optional[List[str]] = None) -> str:
    """
    Nhập các đáp án cho câu hỏi nhiều lựa chọn (ví dụ: ACD).
    Hỗ trợ:
    - Gõ trực tiếp các chữ cái (A, B, C, D, E).
    - Phím [Space] (phím cách) hoặc [Enter] đều có chức năng XÁC NHẬN / NỘP đáp án.
    - Phím [Backspace] để xóa ký tự vừa nhập.
    - Phím tắt điều hướng nhanh (F, P, N, M, S, Q) khi buffer rỗng.
    """
    if valid_letters is None:
        valid_letters = ["A", "B", "C", "D", "E"]
    valid_letters_upper = [x.upper() for x in valid_letters]
    nav_keys = ["F", "P", "N", "M", "S", "Q"]

    print(wrap_display(prompt_text), end="", flush=True)

    if sys.platform == 'win32':
        try:
            import msvcrt
            buffer = []
            while True:
                ch = msvcrt.getwch()
                # 1. Phím Space (' ') hoặc Enter ('\r', '\n') -> Xác nhận nộp bài
                if ch in ('\r', '\n', ' '):
                    print()
                    return "".join(buffer)
                # 2. Phím Backspace
                elif ch in ('\x08', '\x7f'):
                    if buffer:
                        buffer.pop()
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                # 3. Ctrl+C
                elif ch == '\x03':
                    print()
                    raise KeyboardInterrupt
                else:
                    ch_upper = ch.upper()
                    # Phím điều hướng khi chưa nhập đáp án nào (F/P/N/M/S/Q)
                    if not buffer and ch_upper in nav_keys and ch_upper not in valid_letters_upper:
                        print(ch_upper)
                        return ch_upper
                    # Thêm ký tự đáp án hợp lệ
                    if ch_upper in valid_letters_upper:
                        if ch_upper not in buffer:
                            buffer.append(ch_upper)
                            buffer.sort()
                            # Xóa ký tự cũ đã hiển thị và in lại buffer đã sắp xếp
                            sys.stdout.write('\b' * (len(buffer) - 1))
                            sys.stdout.write("".join(buffer))
                            sys.stdout.flush()
        except Exception:
            pass

    # Fallback cho terminal khác: dùng input thông thường
    try:
        val = input().strip()
        return val
    except KeyboardInterrupt:
        print()
        raise


def clear_screen():
    """Xóa màn hình console."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pause(message: str = "Nhấn phím bất kỳ để tiếp tục..."):
    """Dừng màn hình chờ người dùng nhấn phím."""
    print(f"\n{Color.GRAY}{message}{Color.RESET}", end="", flush=True)
    if sys.platform == 'win32':
        try:
            import msvcrt
            msvcrt.getwch()
            print()
            return
        except Exception:
            pass
    try:
        input()
    except Exception:
        pass


def draw_box(lines: List[str], title: str = "", border_color: str = Color.BRIGHT_CYAN, max_width: int = 76) -> str:
    """Vẽ một hộp khung chữ nhật Unicode bao quanh các dòng văn bản."""
    clean_lines = [line for line in lines]
    max_len = max([display_width(l) for l in clean_lines] + [display_width(title) + 4, 40])
    box_w = min(max(max_len + 4, 50), max_width)

    top_border = "─" * (box_w - 2)
    if title:
        title_str = f" {title} "
        t_len = display_width(title_str)
        if t_len < box_w - 4:
            rem = box_w - 2 - t_len
            left_p = rem // 2
            right_p = rem - left_p
            top_line = f"{border_color}┌{'─' * left_p}{Color.BOLD}{Color.BRIGHT_WHITE}{title_str}{Color.RESET}{border_color}{'─' * right_p}┐{Color.RESET}"
        else:
            top_line = f"{border_color}┌─{Color.BOLD}{Color.BRIGHT_WHITE}{title_str[:box_w-6]}{Color.RESET}{border_color}─┐{Color.RESET}"
    else:
        top_line = f"{border_color}┌{top_border}┐{Color.RESET}"

    bot_line = f"{border_color}└{'─' * (box_w - 2)}┘{Color.RESET}"

    res = [top_line]
    for line in clean_lines:
        content_w = box_w - 4
        # Tự động ngắt dòng nếu dòng dài hơn khung
        words = line.split(" ")
        cur_line = ""
        for word in words:
            if display_width(cur_line + " " + word) if cur_line else display_width(word) <= content_w:
                cur_line = f"{cur_line} {word}" if cur_line else word
            else:
                padded = pad_display(cur_line, content_w)
                res.append(f"{border_color}│{Color.RESET} {padded} {border_color}│{Color.RESET}")
                cur_line = word
        if cur_line:
            padded = pad_display(cur_line, content_w)
            res.append(f"{border_color}│{Color.RESET} {padded} {border_color}│{Color.RESET}")

    res.append(bot_line)
    return "\n".join(res)


def play_sound(sound_type: str = "correct", enabled: bool = True):
    """Phát âm thanh phản hồi tương tác qua winsound trên Windows."""
    if not enabled or sys.platform != 'win32':
        return
    try:
        import winsound
        if sound_type == "correct":
            winsound.Beep(1200, 80)
            winsound.Beep(1800, 100)
        elif sound_type == "wrong":
            winsound.Beep(350, 180)
        elif sound_type == "flag":
            winsound.Beep(850, 90)
        elif sound_type == "navigate":
            winsound.Beep(650, 50)
        elif sound_type == "finish":
            winsound.Beep(1000, 80)
            winsound.Beep(1500, 100)
            winsound.Beep(2000, 150)
    except Exception:
        pass
