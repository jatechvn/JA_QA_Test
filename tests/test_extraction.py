import copy
import json
from pathlib import Path
import unittest

from extract_data import extract_goc, extract_exam1, validate_data
from core.storage import StorageManager


ROOT = Path(__file__).resolve().parents[1]


class ExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = extract_goc(str(next(ROOT.glob('*Gốc.docx'))))
        cls.exam = extract_exam1(str(next(ROOT.glob('* 1.docx'))), cls.bank)

    def test_all_questions_valid_and_generated_files_current(self):
        validate_data(self.bank, self.exam)
        self.assertEqual(len(self.bank['questions']), 201)
        self.assertEqual(len(self.exam['questions']), 60)
        for name, data in [('question_bank.json', self.bank), ('exam_de1.json', self.exam)]:
            self.assertEqual(json.loads((ROOT / 'data' / name).read_text(encoding='utf-8')), data)

    def test_brainstorming_matches_source(self):
        q = self.exam['questions'][40]
        self.assertEqual(q['matched_id'], 'MC_032')
        self.assertEqual(q['answer'], 'BCE')
        self.assertEqual(q['options'], [
            'A. Trong cuộc họp, kịp thời phê bình và đánh giá ý kiến của người khác',
            'B. Theo đuổi số lượng ý tưởng',
            'C. Khuyến khích những ý tưởng sáng tạo bay bổng, không giới hạn',
            'D. Chỉ người quản lý được phát biểu',
            'E. Kết hợp và cải tiến ý tưởng của người khác',
        ])

    def test_similar_prefix_does_not_match_wrong_question(self):
        self.assertEqual(self.exam['questions'][14]['matched_id'], 'SC_029')

    def test_separate_answer_paragraphs_keep_question_titles(self):
        bank = {q['id']: q for q in self.bank['questions']}
        for number in (26, 29, 31, 38, 43, 48):
            self.assertTrue(bank[f'MC_{number:03}']['question'])
        self.assertEqual(len(bank['MC_047']['options']), 4)
        self.assertTrue(bank['MC_048']['question'].startswith('Khi nhân viên gặp vấn đề'))

    def test_empty_or_ambiguous_bank_match_is_rejected(self):
        bank = copy.deepcopy(self.bank)
        bank['questions'].insert(0, {'id': 'EMPTY', 'type': 'multi_choice', 'question': '', 'answer': 'ABCD', 'options': []})
        bank['questions'].append(copy.deepcopy(bank['questions'][1]))
        exam = extract_exam1(str(next(ROOT.glob('* 1.docx'))), bank)
        self.assertFalse(any(q['matched_id'] == 'EMPTY' for q in exam['questions']))
        with self.assertRaises(ValueError):
            validate_data(bank, exam)

    def test_wrong_notebook_uses_current_content_without_mutating_history(self):
        storage = StorageManager.__new__(StorageManager)
        storage.bank_data = self.bank
        storage.exam_de1_data = self.exam
        storage.progress = {'wrong_questions': {'41': {'question_data': {
            'num': 41, 'question': 'stale', 'options': ['wrong'], 'answer': 'ABCD'
        }, 'fail_count': 2}}}
        original = copy.deepcopy(storage.progress)
        self.assertEqual(storage.get_wrong_questions()[0], self.exam['questions'][40])
        self.assertEqual(storage.progress, original)


if __name__ == '__main__':
    unittest.main()
