#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py - Điểm khởi chạy Ứng Dụng CLI Ôn Thi Tổ Trưởng CESBG 2026 (Nâng cấp Giai đoạn 1).
Bao gồm:
- Ma trận câu hỏi thi 60 ô vuông (Question Grid Map)
- Cắm cờ câu hỏi phân vân [F]
- Đồng hồ bấm giờ đếm ngược thời gian thực (Live Countdown Timer)
- Điều hướng linh hoạt: [P] Lùi, [N] Tiến, [M] Ma trận, [S] Nộp bài sớm
- Âm thanh tương tác winsound (Ting khi đúng, Bụp khi sai, Cắm cờ, Kết thúc)
- Bảng tổng kết chuẩn box-drawing và Sổ tay câu sai (Spaced Repetition).
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Đảm bảo đường dẫn import tương đối đúng từ thư mục ứng dụng
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from ui.terminal import (
    Color, clear_screen, configure_theme, get_single_key, pause, play_sound
)
from ui.views import (
    display_choice_question, display_flashcard_question,
    display_true_false_question, render_quiz_header, show_exam_summary,
    show_instant_feedback, show_main_menu, show_question_matrix,
    show_search_view, show_settings_view, show_submit_confirmation,
    show_topic_menu
)
from core.storage import StorageManager
from core.quiz_engine import QuizEngine


def ensure_data_extracted(storage: StorageManager):
    """Kiểm tra và tự động trích xuất dữ liệu nếu chưa có tệp JSON."""
    if not storage.bank_data or not storage.exam_de1_data:
        print(f"{Color.YELLOW}[*] Đang khởi tạo và nạp dữ liệu ngân hàng đề thi từ Word...{Color.RESET}")
        from extract_data import main as run_extractor
        run_extractor()
        # Nạp lại dữ liệu
        storage.bank_data = storage._load_json(storage.bank_file)
        storage.exam_de1_data = storage._load_json(storage.exam_de1_file)


def run_quiz_session(
    questions: list,
    exam_title: str,
    storage: StorageManager,
    quiz_engine: QuizEngine,
    is_exam_mode: bool = False,
    time_limit_minutes: int = 60
):
    """
    Điều phối và thực thi phiên luyện tập hoặc thi thử với đầy đủ tính năng Giai đoạn 1:
    Ma trận 60 câu, cắm cờ, nhảy câu linh hoạt, đếm ngược thời gian và âm thanh.
    """
    if not questions:
        print(f"\n{Color.YELLOW}Không có câu hỏi nào trong mục này!{Color.RESET}")
        pause()
        return

    total = len(questions)
    user_answers: Dict[int, str] = {}
    flagged_set: Set[int] = set()
    is_correct_map: Dict[int, bool] = {}

    instant_feedback = False if is_exam_mode else storage.get_setting("instant_feedback", True)
    sound_enabled = storage.get_setting("sound", True)
    time_limit_secs = (time_limit_minutes * 60) if is_exam_mode else None
    start_time = time.time()

    cur_idx = 1
    while 1 <= cur_idx <= total:
        # 1. Kiểm tra đồng hồ đếm ngược
        remain_secs = None
        if time_limit_secs is not None:
            elapsed = int(time.time() - start_time)
            remain_secs = max(0, time_limit_secs - elapsed)
            if remain_secs <= 0:
                clear_screen()
                print(f"\n{Color.BOLD}{Color.BRIGHT_RED}⏰ HẾT GIỜ LÀM BÀI! Đang tự động nộp bài và chấm điểm...{Color.RESET}\n")
                play_sound("finish", sound_enabled)
                time.sleep(2)
                break

        q = questions[cur_idx - 1]
        q_type = q.get("type", "single_choice")
        is_flagged = cur_idx in flagged_set
        prev_ans = user_answers.get(cur_idx, "")
        answered_count = len(user_answers)
        flagged_count = len(flagged_set)

        # Tính điểm tạm thời hiện tại
        current_score = sum(
            questions[i - 1].get("points", 1.0)
            for i in user_answers.keys()
            if is_correct_map.get(i, False)
        )

        # 2. Render Header tiêu đề, đồng hồ và tiến trình
        render_quiz_header(
            exam_title=exam_title,
            current_idx=cur_idx,
            total_count=total,
            answered_count=answered_count,
            flagged_count=flagged_count,
            score=current_score,
            remaining_seconds=remain_secs,
            is_flagged=is_flagged
        )

        # 3. Hiển thị câu hỏi tương ứng
        if q_type in ("single_choice", "multi_choice"):
            user_input = display_choice_question(q, cur_idx, total, is_flagged=is_flagged, cur_ans=prev_ans)
        elif q_type == "true_false":
            user_input = display_true_false_question(q, cur_idx, total, is_flagged=is_flagged, cur_ans=prev_ans)
        elif q_type in ("short_answer", "case_study"):
            user_input = display_flashcard_question(q, cur_idx, total, is_flagged=is_flagged, cur_ans=prev_ans)
        else:
            user_input = display_choice_question(q, cur_idx, total, is_flagged=is_flagged, cur_ans=prev_ans)

        cmd = user_input.upper().strip()

        # 4. Xử lý các phím chức năng điều hướng
        if cmd == "Q":
            confirm = get_single_key(f"\n{Color.YELLOW}Bạn có chắc chắn muốn dừng bài thi sớm? [Y/N]: {Color.RESET}", ["Y", "y", "N", "n"])
            if confirm.upper() == "Y":
                break
            else:
                continue

        elif cmd == "F":
            # Cắm cờ / Bỏ cắm cờ
            if cur_idx in flagged_set:
                flagged_set.remove(cur_idx)
            else:
                flagged_set.add(cur_idx)
                play_sound("flag", sound_enabled)
            continue

        elif cmd == "P":
            # Quay lại câu trước
            if cur_idx > 1:
                cur_idx -= 1
                play_sound("navigate", sound_enabled)
            continue

        elif cmd == "N":
            # Chuyển sang câu tiếp theo
            if cur_idx < total:
                cur_idx += 1
                play_sound("navigate", sound_enabled)
            continue

        elif cmd == "M":
            # Mở bảng ma trận câu hỏi
            jump_to = show_question_matrix(total, user_answers, flagged_set, cur_idx)
            if jump_to is not None:
                cur_idx = jump_to
                play_sound("navigate", sound_enabled)
            continue

        elif cmd == "S":
            # Nộp bài sớm
            confirmed = show_submit_confirmation(total, len(user_answers), len(flagged_set), remain_secs)
            if confirmed:
                break
            else:
                continue

        # 5. Xử lý câu trả lời người dùng
        is_correct, norm_user_ans = quiz_engine.check_answer(q, user_input)
        user_answers[cur_idx] = norm_user_ans
        is_correct_map[cur_idx] = is_correct

        # Lưu vào tiến độ học tập
        storage.record_question_result(q, is_correct, norm_user_ans)

        # Phản hồi tức thì nếu bật (chế độ Luyện nhớ)
        if instant_feedback:
            correct_ans = str(q.get("correct_answer", q.get("answer", ""))).strip().upper()
            show_instant_feedback(is_correct, norm_user_ans, correct_ans, q, sound_enabled)
        else:
            play_sound("navigate", sound_enabled)

        # Tự động chuyển câu tiếp theo
        if cur_idx < total:
            cur_idx += 1
        else:
            # Đã đến câu cuối cùng của bài thi!
            if is_exam_mode:
                confirmed = show_submit_confirmation(total, len(user_answers), len(flagged_set), remain_secs)
                if confirmed:
                    break
                else:
                    # Người dùng muốn kiểm tra lại, mở ma trận
                    jump_to = show_question_matrix(total, user_answers, flagged_set, cur_idx)
                    if jump_to is not None:
                        cur_idx = jump_to
            else:
                break

    # 6. Tính toán kết quả tổng kết
    total_correct = sum(1 for v in is_correct_map.values() if v)
    final_score = sum(
        questions[i - 1].get("points", 1.0)
        for i in range(1, total + 1)
        if is_correct_map.get(i, False)
    )
    wrong_list = [
        questions[i - 1] for i in range(1, total + 1)
        if not is_correct_map.get(i, False)
    ]

    elapsed_seconds = int(time.time() - start_time)
    mins, secs = divmod(elapsed_seconds, 60)
    elapsed_str = f"{mins} phút {secs} giây" if mins > 0 else f"{secs} giây"

    # Ghi nhận lịch sử thi
    storage.record_exam_history(exam_title, total, total_correct, final_score, elapsed_str)

    # Hiển thị bảng tổng kết kết quả
    show_exam_summary(exam_title, total, total_correct, final_score, elapsed_str, wrong_list, sound_enabled)


def main():
    parser = argparse.ArgumentParser(description="CESBG Vietnam - CLI QA Study Tool 2026")
    parser.add_argument("--role", choices=["to_truong", "chuyen_truong"], default="to_truong", help="Chọn vai trò ôn thi (to_truong hoặc chuyen_truong)")
    parser.add_argument("--theme", choices=["dark", "light"], default=None, help="Ép buộc theme dark hoặc light")
    parser.add_argument("--no-color", action="store_true", help="Tắt màu sắc ANSI")
    parser.add_argument("--exam1", action="store_true", help="Khởi chạy ngay Đề 1 chuẩn")
    parser.add_argument("--web", action="store_true", help="Khởi chạy ngay Web Server Mobile")
    args = parser.parse_args()

    # Cấu hình giao diện và màu sắc
    storage = StorageManager(role=args.role)
    saved_theme = storage.get_setting("theme", "dark")
    active_theme = args.theme or saved_theme
    configure_theme(theme=active_theme, no_color=args.no_color)

    # Đảm bảo dữ liệu đã sẵn sàng
    ensure_data_extracted(storage)
    quiz_engine = QuizEngine(storage)

    # Nếu có cờ --web thì khởi động ngay Web Server
    if args.web:
        from web_server import start_server
        start_server(port=8080, open_browser=True)
        return

    # Nếu có cờ --exam1 thì chạy thẳng (đảo ngẫu nhiên câu hỏi như đề thi thử)
    if args.exam1:
        shuffle_opts = storage.get_setting("shuffle_options", False)
        questions = quiz_engine.prepare_exam_de1(shuffle_questions=True, shuffle_options=shuffle_opts)
        run_quiz_session(questions, f"Đề Thi Chuẩn Mẫu Số 1 ({storage.get_role_title()})", storage, quiz_engine, is_exam_mode=False)
        return

    # Vòng lặp chính của Menu
    while True:
        try:
            wrong_count = len(storage.get_wrong_questions())
            stats = storage.progress.get("stats", {})
            settings = storage.progress.get("settings", {})
            role_info = storage.get_role_info()
            bank_total = storage.bank_data.get("total_questions", 201)

            choice = show_main_menu(stats, wrong_count, settings, role_info=role_info, bank_total=bank_total)
            shuffle_opts = storage.get_setting("shuffle_options", False)

            if choice == "1":
                # Luyện tập Đề Thi Mẫu Số 1 (60 câu - Đảo ngẫu nhiên như đề thi thật)
                clear_screen()
                print(f"{Color.BRIGHT_CYAN}{'═' * 74}{Color.RESET}")
                print(f"{Color.BOLD}{Color.BRIGHT_WHITE}   CHỌN CHẾ ĐỘ THI - ĐỀ SỐ 1 (60 CÂU CHUẨN: {storage.get_role_title()}){Color.RESET}")
                print(f"{Color.BRIGHT_CYAN}{'═' * 74}{Color.RESET}\n")
                print(f" [1] {Color.BOLD}Chế độ Luyện Nhớ (Đảo Câu Trong Từng Phần){Color.RESET}: Biết đúng/sai & đối soát ngay từng câu")
                print(f" [2] {Color.BOLD}Chế độ Thi Thử Chuẩn (Đảo Trong Từng Phần - Bấm Giờ 60 Phút){Color.RESET}: Bấm giờ đếm ngược, ma trận 60 câu")
                print(f" [3] {Color.BOLD}Chế độ Theo Thứ Tự Gốc Đề 1 (1 -> 60){Color.RESET}: Giữ nguyên thứ tự câu hỏi mẫu")
                print(f" [0] Quay lại\n")
                
                sub_c = get_single_key(f"{Color.BRIGHT_GREEN}👉 Chọn chế độ [1, 2, 3, 0]: {Color.RESET}", ["1", "2", "3", "0"])
                if sub_c == "1":
                    questions = quiz_engine.prepare_exam_de1(shuffle_questions=True, shuffle_options=shuffle_opts)
                    run_quiz_session(questions, f"Đề Thi Mẫu 1 - {storage.get_role_title()} (Luyện Nhớ)", storage, quiz_engine, is_exam_mode=False)
                elif sub_c == "2":
                    questions = quiz_engine.prepare_exam_de1(shuffle_questions=True, shuffle_options=shuffle_opts)
                    run_quiz_session(questions, f"Đề Thi Thử Số 1 - {storage.get_role_title()} (60 Phút)", storage, quiz_engine, is_exam_mode=True, time_limit_minutes=60)
                elif sub_c == "3":
                    questions = quiz_engine.prepare_exam_de1(shuffle_questions=False, shuffle_options=shuffle_opts)
                    run_quiz_session(questions, f"Đề Thi Mẫu 1 - {storage.get_role_title()} (Thứ Tự Gốc 1-60)", storage, quiz_engine, is_exam_mode=False)

            elif choice == "2":
                # Ôn tập Ngân hàng Đề Gốc theo chuyên đề
                while True:
                    counts = storage.bank_data.get("counts", {})
                    top_choice = show_topic_menu(counts=counts, total=storage.bank_data.get("total_questions", 201))
                    if top_choice == "0":
                        break
                    
                    sc_c = counts.get("single_choice", 0)
                    mc_c = counts.get("multi_choice", 0)
                    tf_c = counts.get("true_false", 0)
                    sa_c = counts.get("short_answer", 0)
                    cs_c = counts.get("case_study", 0)
                    tot_c = storage.bank_data.get("total_questions", 0)

                    topic_map = {
                        "1": ("single_choice", f"Phần I: Trắc Nghiệm 1 Đáp Án ({sc_c} câu)"),
                        "2": ("multi_choice", f"Phần II: Trắc Nghiệm Nhiều Đáp Án ({mc_c} câu)"),
                        "3": ("true_false", f"Phần III: Phán Đoán Đúng/Sai ({tf_c} câu)"),
                        "4": ("short_answer", f"Phần IV: Trả Lời Ngắn Gọn ({sa_c} câu Flashcard)"),
                        "5": ("case_study", f"Phần V: Phân Tích Tình Huống ({cs_c} câu Flashcard)"),
                        "6": ("all", f"Toàn Bộ Ngân Hàng Câu Hỏi Gốc ({tot_c} câu)")
                    }
                    if top_choice in topic_map:
                        t_key, t_title = topic_map[top_choice]
                        questions = quiz_engine.prepare_topic_questions(t_key, shuffle_questions=True, shuffle_options=shuffle_opts)
                        run_quiz_session(questions, t_title, storage, quiz_engine, is_exam_mode=False)

            elif choice == "3":
                # Tạo Đề Thi Thử Ngẫu Nhiên (60 câu / 100 điểm / 60 phút)
                questions = quiz_engine.generate_mock_exam(shuffle_options=shuffle_opts)
                run_quiz_session(questions, f"Đề Thi Thử Ngẫu Nhiên ({storage.get_role_title()} - 100 Điểm)", storage, quiz_engine, is_exam_mode=True, time_limit_minutes=60)

            elif choice == "4":
                # Sổ tay câu hay sai
                wrong_questions = quiz_engine.prepare_wrong_questions(shuffle_options=shuffle_opts)
                if not wrong_questions:
                    clear_screen()
                    print(f"\n{Color.BRIGHT_GREEN}🎉 CHÚC MỪNG! Hiện tại bạn không có câu nào trong Sổ câu sai của {storage.get_role_title()}!{Color.RESET}")
                    print(f"{Color.GRAY}Bạn đã nắm vững hoặc chưa làm sai câu hỏi nào.{Color.RESET}\n")
                    pause()
                else:
                    run_quiz_session(wrong_questions, f"Sổ Tay Ôn Câu Hay Sai ({len(wrong_questions)} câu)", storage, quiz_engine, is_exam_mode=False)

            elif choice == "5":
                # Tra cứu nhanh
                show_search_view(storage)

            elif choice == "6":
                # Cài đặt
                show_settings_view(storage)

            elif choice == "7":
                # Khởi động Web Server Mobile
                clear_screen()
                from web_server import start_server
                print(f"\n{Color.BRIGHT_CYAN}[*] Đang khởi động Web Server phục vụ Mobile...{Color.RESET}\n")
                try:
                    start_server(port=8080, open_browser=True)
                except KeyboardInterrupt:
                    pass
                clear_screen()

            elif choice == "8":
                # Phân tích điểm yếu & Xuất đề thi Word (.docx)
                from ui.views import show_analytics_and_export_view
                weak_key = show_analytics_and_export_view(storage, quiz_engine)
                if weak_key:
                    title_map = {
                        "single_choice": "Luyện Cấp Tốc: Trắc Nghiệm 1 Đáp Án (Phần I)",
                        "multi_choice": "Luyện Cấp Tốc: Trắc Nghiệm Nhiều Đáp Án (Phần II)",
                        "true_false": "Luyện Cấp Tốc: Phán Đoán Đúng/Sai (Phần III)",
                        "short_answer": "Luyện Cấp Tốc: Trả Lời Ngắn Gọn (Phần IV)",
                        "case_study": "Luyện Cấp Tốc: Phân Tích Tình Huống (Phần V)"
                    }
                    w_title = title_map.get(weak_key, "Luyện Cấp Tốc Chuyên Đề Yếu")
                    w_questions = quiz_engine.prepare_topic_questions(weak_key, shuffle_questions=True, shuffle_options=shuffle_opts)
                    run_quiz_session(w_questions, w_title, storage, quiz_engine, is_exam_mode=False)

            elif choice == "9":
                # Đổi vai trò ôn thi: Tổ Trưởng ⇋ Chuyền Trưởng
                target_role = "chuyen_truong" if storage.role == "to_truong" else "to_truong"
                storage.set_role(target_role)
                play_sound("navigate", storage.get_setting("sound", True))
                clear_screen()
                info = storage.get_role_info()
                print(f"\n{Color.BRIGHT_GREEN}✔ ĐÃ CHUYỂN THÀNH CÔNG SANG: {info['icon']} {info['title'].upper()} ({storage.bank_data.get('total_questions', 0)} CÂU HỎI)!{Color.RESET}\n")
                time.sleep(1.2)

            elif choice == "0":
                clear_screen()
                print(f"\n{Color.BRIGHT_CYAN}Cảm ơn bạn đã sử dụng chương trình. Chúc bạn ôn tập tốt và đạt điểm cao trong kỳ thi! 🎉{Color.RESET}\n")
                sys.exit(0)

        except KeyboardInterrupt:
            clear_screen()
            print(f"\n{Color.YELLOW}Đã thoát chương trình an toàn.{Color.RESET}\n")
            sys.exit(0)


if __name__ == '__main__':
    main()
