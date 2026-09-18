#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/quiz_engine.py - Bộ máy điều phối bài thi, trắc nghiệm, xáo trộn đáp án
bảo toàn đáp án chuẩn, sinh đề thi thử ngẫu nhiên chuẩn 100 điểm, và xử lý Flashcard.
"""

import random
import re
from typing import Any, Dict, List, Optional, Tuple


class QuizEngine:
    def __init__(self, storage):
        self.storage = storage

    def prepare_exam_de1(self, shuffle_questions: bool = False, shuffle_options: bool = False) -> List[Dict[str, Any]]:
        """Chuẩn bị Đề 1, giữ cấu trúc từng phần và thang điểm của mẫu."""
        raw_list = [dict(q) for q in self.storage.exam_de1_data.get("questions", [])]
        if shuffle_questions:
            # Chỉ đảo trong cùng loại câu, giữ các vị trí/phần của đề mẫu.
            groups = {}
            for q in raw_list:
                groups.setdefault(q["type"], []).append(q)
            for group in groups.values():
                random.shuffle(group)
            shuffled = {kind: iter(group) for kind, group in groups.items()}
            raw_list = [next(shuffled[q["type"]]) for q in raw_list]

        points_by_type = {
            "single_choice": 1.0,
            "multi_choice": 2.0,
            "true_false": 1.0,
            "short_answer": 5.0,
            "case_study": 10.0,
        }
        for q in raw_list:
            q["points"] = points_by_type.get(q.get("type"), 1.0)
        # Giữ num gốc: StorageManager dùng nó để nhận diện câu trong sổ câu sai.
        return [self._prepare_single_question(q, shuffle_options) for q in raw_list]

    def prepare_topic_questions(self, topic_type: str, shuffle_questions: bool = True, shuffle_options: bool = False) -> List[Dict[str, Any]]:
        """Lấy câu hỏi theo chuyên đề từ Ngân hàng Gốc (201 câu)."""
        bank_questions = self.storage.bank_data.get("questions", [])
        if topic_type == "all":
            filtered = [dict(q) for q in bank_questions]
        else:
            filtered = [dict(q) for q in bank_questions if q.get("type") == topic_type]
            
        if shuffle_questions:
            random.shuffle(filtered)
        return [self._prepare_single_question(q, shuffle_options) for q in filtered]

    def generate_mock_exam(self, shuffle_options: bool = False) -> List[Dict[str, Any]]:
        """
        Sinh đề thi thử ngẫu nhiên từ Ngân hàng Gốc với cấu trúc chuẩn 100 điểm:
        - 30 câu Chọn một đáp án đúng (30 điểm)
        - 15 câu Chọn nhiều đáp án đúng (30 điểm)
        - 10 câu Phán đoán đúng/sai (10 điểm)
        - 4 câu Trả lời ngắn gọn (20 điểm)
        - 1 câu Phân tích tình huống (10 điểm)
        Tổng cộng: 60 câu, thang điểm 100.
        """
        bank_questions = self.storage.bank_data.get("questions", [])
        sc = [dict(q) for q in bank_questions if q.get("type") == "single_choice"]
        mc = [dict(q) for q in bank_questions if q.get("type") == "multi_choice"]
        tf = [dict(q) for q in bank_questions if q.get("type") == "true_false"]
        sa = [dict(q) for q in bank_questions if q.get("type") == "short_answer"]
        cs = [dict(q) for q in bank_questions if q.get("type") == "case_study"]

        selected = (
            random.sample(sc, min(30, len(sc))) +
            random.sample(mc, min(15, len(mc))) +
            random.sample(tf, min(10, len(tf))) +
            random.sample(sa, min(4, len(sa))) +
            random.sample(cs, min(1, len(cs)))
        )

        # Gán số thứ tự và điểm số
        res = []
        for idx, q in enumerate(selected, 1):
            q_copy = dict(q)
            q_copy["num"] = idx
            if q_copy.get("type") == "single_choice":
                q_copy["points"] = 1.0
            elif q_copy.get("type") == "multi_choice":
                q_copy["points"] = 2.0
            elif q_copy.get("type") == "true_false":
                q_copy["points"] = 1.0
            elif q_copy.get("type") == "short_answer":
                q_copy["points"] = 5.0
            elif q_copy.get("type") == "case_study":
                q_copy["points"] = 10.0
            res.append(self._prepare_single_question(q_copy, shuffle_options))
        return res

    def prepare_wrong_questions(self, shuffle_options: bool = False) -> List[Dict[str, Any]]:
        """Lấy danh sách các câu trong Sổ tay câu sai."""
        wrong_list = self.storage.get_wrong_questions()
        random.shuffle(wrong_list)
        return [self._prepare_single_question(q, shuffle_options) for q in wrong_list]

    def _prepare_single_question(self, q: Dict[str, Any], shuffle_options: bool) -> Dict[str, Any]:
        """
        Chuẩn bị một câu hỏi: sao chép, làm sạch và xáo trộn đáp án nếu được bật,
        đồng thời tính toán lại đáp án đúng tương ứng.
        """
        item = dict(q)
        q_type = item.get("type")
        raw_options = item.get("options", [])
        raw_answer = str(item.get("answer", "")).strip().upper()

        if not raw_options or q_type in ("true_false", "short_answer", "case_study") or not shuffle_options:
            item["display_options"] = list(raw_options)
            item["correct_answer"] = raw_answer
            return item

        # Tách phần chữ cái tiền tố và nội dung lựa chọn
        letters = ["A", "B", "C", "D", "E", "F"]
        clean_opts = []
        for opt in raw_options:
            clean = re.sub(r'^[A-F][\.\:\s]\s*', '', opt).strip()
            clean_opts.append(clean)

        # Ánh xạ các đáp án đúng ban đầu sang chỉ số index
        correct_indices = set()
        for char in raw_answer:
            if char in letters:
                idx = letters.index(char)
                if idx < len(clean_opts):
                    correct_indices.add(idx)

        # Tạo danh sách cặp (index_gốc, text) và xáo trộn
        indexed_opts = list(enumerate(clean_opts))
        random.shuffle(indexed_opts)

        # Xây dựng lại options mới và tính đáp án đúng mới
        new_options = []
        new_correct_chars = []
        for new_idx, (orig_idx, opt_text) in enumerate(indexed_opts):
            letter = letters[new_idx]
            new_options.append(f"{letter}. {opt_text}")
            if orig_idx in correct_indices:
                new_correct_chars.append(letter)

        new_correct_chars.sort()
        item["display_options"] = new_options
        item["correct_answer"] = "".join(new_correct_chars)
        return item

    @staticmethod
    def check_answer(question: Dict[str, Any], user_input: str) -> Tuple[bool, str]:
        """
        Kiểm tra tính đúng/sai của câu trả lời người dùng.
        Trả về (is_correct, normalized_user_ans).
        """
        q_type = question.get("type")
        correct_ans = str(question.get("correct_answer", question.get("answer", ""))).strip().upper()
        clean_input = user_input.strip().upper()

        if q_type == "single_choice":
            return (clean_input == correct_ans, clean_input)

        elif q_type == "multi_choice":
            # Chuẩn hóa: lọc các ký tự A-F, sắp xếp theo bảng chữ cái
            user_chars = sorted(list(set(re.findall(r'[A-F]', clean_input))))
            norm_user = "".join(user_chars)
            target_chars = sorted(list(set(re.findall(r'[A-F]', correct_ans))))
            norm_target = "".join(target_chars)
            return (norm_user == norm_target, norm_user)

        elif q_type == "true_false":
            # Chấp nhận: V / X hoặc 1 (Đúng) / 2 (Sai) hoặc T / F
            user_val = ""
            if clean_input in ("V", "1", "T", "D", "Đ"):
                user_val = "V"
            elif clean_input in ("X", "2", "F", "S"):
                user_val = "X"
            else:
                user_val = clean_input
            return (user_val == correct_ans, user_val)

        elif q_type in ("short_answer", "case_study"):
            # Đối với tự luận/tình huống, user tự chấm: 1 = Đạt/Nhớ, 2 = Chưa đạt
            is_ok = clean_input in ("1", "V", "Y", "OK")
            return (is_ok, "Đã thuộc" if is_ok else "Cần ôn lại")

        return (False, clean_input)
