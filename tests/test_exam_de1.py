import copy
import json
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.quiz_engine import QuizEngine


class ExamDe1Tests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "data" / "exam_de1.json"
        self.data = json.loads(path.read_text(encoding="utf-8"))
        self.original = copy.deepcopy(self.data)
        self.engine = QuizEngine(SimpleNamespace(exam_de1_data=self.data))

    def assert_form(self, questions):
        expected = (
            ["single_choice"] * 30 + ["multi_choice"] * 15
            + ["true_false"] * 10 + ["short_answer"] * 4 + ["case_study"]
        )
        self.assertEqual([q["type"] for q in questions], expected)
        self.assertEqual(sum(q["points"] for q in questions), 100)
        self.assertEqual(
            [sum(q["points"] for q in questions if q["type"] == kind)
             for kind in dict.fromkeys(expected)],
            [30, 30, 10, 20, 10],
        )
        self.assertEqual(self.data, self.original)

    def test_shuffle_keeps_sections_and_question_identity(self):
        with patch("core.quiz_engine.random.shuffle", side_effect=lambda items: items.reverse()):
            questions = self.engine.prepare_exam_de1(shuffle_questions=True)
        self.assert_form(questions)
        self.assertNotEqual([q["num"] for q in questions], list(range(1, 61)))
        self.assertEqual(sorted(q["num"] for q in questions), list(range(1, 61)))
        source = {q["num"]: q for q in self.original["questions"]}
        for q in questions:
            for key, value in source[q["num"]].items():
                self.assertEqual(q[key], value)

    def test_original_order_and_score(self):
        questions = self.engine.prepare_exam_de1()
        self.assert_form(questions)
        self.assertEqual([q["num"] for q in questions], list(range(1, 61)))

    def test_option_shuffle_preserves_correct_content(self):
        with patch("core.quiz_engine.random.shuffle", side_effect=lambda items: items.reverse()):
            questions = self.engine.prepare_exam_de1(True, True)
        self.assert_form(questions)
        for q in questions:
            if q["type"] not in ("single_choice", "multi_choice"):
                continue
            def correct_content(options, answer):
                return {re.sub(r"^[A-F][\.\:\s]\s*", "", opt).strip()
                        for opt in options if opt[0] in answer}
            self.assertEqual(
                correct_content(q["options"], q["answer"]),
                correct_content(q["display_options"], q["correct_answer"]),
            )
            self.assertTrue(self.engine.check_answer(q, q["correct_answer"])[0])


if __name__ == "__main__":
    unittest.main()
