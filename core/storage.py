#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/storage.py - Quản lý nạp dữ liệu ngân hàng đề thi và lưu trữ tiến độ học tập,
sổ tay câu hỏi sai (Spaced Repetition), lịch sử thi và cài đặt cá nhân.
"""

import json
import os
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def strip_accents(s: str) -> str:
    """Loại bỏ dấu tiếng Việt để tìm kiếm không dấu linh hoạt."""
    if not s:
        return ""
    nfkd = unicodedata.normalize('NFD', s)
    no_marks = "".join(c for c in nfkd if not unicodedata.combining(c))
    return no_marks.replace('đ', 'd').replace('Đ', 'D').lower()


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    d = get_base_dir() / "data"
    d.mkdir(exist_ok=True)
    return d


ROLES = {
    "to_truong": {
        "title": "Tổ Trưởng (周边组长)",
        "short_title": "Tổ Trưởng",
        "icon": "👑"
    },
    "chuyen_truong": {
        "title": "Chuyền Trưởng (线长)",
        "short_title": "Chuyền Trưởng",
        "icon": "⚡"
    }
}


class StorageManager:
    def __init__(self, role: str = "to_truong"):
        self.data_dir = get_data_dir()
        self.role = role if role in ROLES else "to_truong"
        self._init_paths_for_role()
        self.bank_data = self._load_json(self.bank_file)
        self.exam_de1_data = self._load_json(self.exam_de1_file)
        self.progress = self._load_progress()

    def _init_paths_for_role(self):
        role_dir = self.data_dir / self.role
        role_dir.mkdir(exist_ok=True)
        
        bank_p = role_dir / "question_bank.json"
        if not bank_p.exists():
            bank_p = self.data_dir / "question_bank.json"
        
        exam_p = role_dir / "exam_de1.json"
        if not exam_p.exists():
            exam_p = self.data_dir / "exam_de1.json"

        self.bank_file = bank_p
        self.exam_de1_file = exam_p
        self.progress_file = role_dir / "user_progress.json"

    def set_role(self, role: str):
        """Chuyển đổi vai trò ôn thi (to_truong hoặc chuyen_truong)."""
        if role not in ROLES:
            role = "to_truong"
        if self.role == role:
            return

        common_settings = self.progress.get("settings", {}) if hasattr(self, "progress") else {}
        self.role = role
        self._init_paths_for_role()
        self.bank_data = self._load_json(self.bank_file)
        self.exam_de1_data = self._load_json(self.exam_de1_file)
        self.progress = self._load_progress()
        
        # Đồng bộ các cài đặt chung (Theme, Sound, Feedback, Shuffle)
        if common_settings:
            for k in ["theme", "sound", "instant_feedback", "shuffle_options"]:
                if k in common_settings:
                    self.progress.setdefault("settings", {})[k] = common_settings[k]

    def get_role_info(self) -> Dict[str, str]:
        return ROLES.get(self.role, ROLES["to_truong"])

    def get_role_title(self) -> str:
        return self.get_role_info()["title"]

    def _load_json(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_progress(self) -> Dict[str, Any]:
        default_progress = {
            "settings": {
                "shuffle_options": False,  # Mặc định không đảo để quen mặt chữ theo đề gốc
                "theme": "dark",
                "instant_feedback": True,  # Chế độ luyện nhớ: hiện đáp án ngay sau mỗi câu
                "sound": True              # Âm thanh hiệu ứng tương tác (winsound)
            },
            "wrong_questions": {},  # id -> {question_dict, count, last_attempt}
            "history": [],
            "stats": {
                "total_answered": 0,
                "total_correct": 0,
                "exams_taken": 0
            }
        }
        if not self.progress_file.exists():
            return default_progress
        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Đảm bảo có đủ các key
                for k, v in default_progress.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            return default_progress

    def save_progress(self):
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi lưu tiến độ: {e}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.progress.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any):
        if "settings" not in self.progress:
            self.progress["settings"] = {}
        self.progress["settings"][key] = value
        self.save_progress()

    def record_question_result(self, question: Dict[str, Any], is_correct: bool, user_ans: str):
        q_id = question.get("id") or str(question.get("num") or question.get("question")[:30])
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.progress["stats"]["total_answered"] += 1
        if is_correct:
            self.progress["stats"]["total_correct"] += 1
            # Nếu câu này từng làm sai và nay đã trả lời đúng -> gỡ khỏi sổ câu sai
            if q_id in self.progress["wrong_questions"]:
                del self.progress["wrong_questions"][q_id]
        else:
            # Ghi nhận vào sổ câu sai
            if q_id not in self.progress["wrong_questions"]:
                self.progress["wrong_questions"][q_id] = {
                    "question_data": question,
                    "fail_count": 1,
                    "last_wrong_ans": user_ans,
                    "last_attempt": now_str
                }
            else:
                self.progress["wrong_questions"][q_id]["fail_count"] += 1
                self.progress["wrong_questions"][q_id]["last_wrong_ans"] = user_ans
                self.progress["wrong_questions"][q_id]["last_attempt"] = now_str
                self.progress["wrong_questions"][q_id]["question_data"] = question

        self.save_progress()

    def record_exam_history(self, exam_title: str, total: int, correct: int, score: float, time_str: str):
        self.progress["stats"]["exams_taken"] += 1
        history_item = {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "title": exam_title,
            "total": total,
            "correct": correct,
            "score": round(score, 1),
            "passed": score >= 60.0,
            "duration": time_str
        }
        self.progress["history"].insert(0, history_item)
        # Giữ tối đa 30 lượt thi gần nhất
        self.progress["history"] = self.progress["history"][:30]
        self.save_progress()

    def get_wrong_questions(self) -> List[Dict[str, Any]]:
        """Dùng nội dung hiện tại, tránh ôn lại bản dữ liệu cũ ghép sai."""
        bank = {q["id"]: q for q in self.bank_data.get("questions", [])}
        exam = {q["num"]: q for q in self.exam_de1_data.get("questions", [])}
        result = []
        for entry in self.progress.get("wrong_questions", {}).values():
            saved = entry["question_data"]
            current = (bank.get(saved["id"]) if saved.get("id")
                       else exam.get(saved.get("num")))
            result.append(dict(current if current is not None else saved))
        return result

    def clear_wrong_questions(self):
        self.progress["wrong_questions"] = {}
        self.save_progress()

    def search_questions(self, keyword: str) -> List[Dict[str, Any]]:
        """Tìm kiếm câu hỏi trong ngân hàng theo từ khóa (hỗ trợ cả có dấu và không dấu)."""
        raw_kw = keyword.lower().strip()
        clean_kw = strip_accents(keyword)
        if not clean_kw:
            return []
        res = []
        for q in self.bank_data.get("questions", []):
            q_txt = q.get("question", "")
            ans_txt = str(q.get("answer", ""))
            opts_txt = " ".join(q.get("options", []))
            full_raw = f"{q_txt} {ans_txt} {opts_txt}".lower()
            full_clean = strip_accents(full_raw)
            if raw_kw in full_raw or clean_kw in full_clean:
                res.append(q)
        return res
