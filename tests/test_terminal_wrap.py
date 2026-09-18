import io
import os
import unicodedata
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from ui.terminal import display_width, strip_ansi, wrap_display
from ui.views import display_choice_question


class TerminalWrapTests(unittest.TestCase):
    def test_vietnamese_words_and_ansi_are_preserved(self):
        text = '\033[96mA.\033[0m Trong trường hợp có sự cố khẩn cấp được ký duyệt đầy đủ'
        for width in (20, 40, 60, 100):
            wrapped = wrap_display(text, width, subsequent_indent='     ')
            self.assertEqual(strip_ansi(wrapped).split(), strip_ansi(text).split())
            self.assertTrue(all(display_width(line) <= width for line in wrapped.splitlines()))
            self.assertIn('\033[96mA.\033[0m', wrapped)
            for line in wrapped.splitlines()[1:]:
                self.assertTrue(line.startswith('     '))

    def test_existing_newlines_and_combining_accents(self):
        text = unicodedata.normalize('NFD', 'đầy đủ')
        self.assertEqual(display_width(text), 6)
        self.assertEqual(wrap_display(text, 4), text.replace(' ', '\n'))
        self.assertEqual(wrap_display('Một\n\nHai\n', 20), 'Một\n\nHai\n')

    def test_current_terminal_width_is_read_each_time(self):
        text = 'một hai ba bốn năm sáu'
        with patch('ui.terminal.shutil.get_terminal_size', side_effect=[
            os.terminal_size((12, 24)), os.terminal_size((80, 24))
        ]):
            self.assertIn('\n', wrap_display(text))
            self.assertEqual(wrap_display(text), text)

    def test_choice_view_wraps_complete_option_words(self):
        option = 'A. Trong trường hợp có sự cố khẩn cấp như cháy nổ, tai nạn lao động, được ký duyệt đầy đủ'
        question = {'type': 'single_choice', 'question': 'Trường hợp nào được phép mở cửa?', 'options': [option]}
        output = io.StringIO()
        with patch('ui.terminal.shutil.get_terminal_size', return_value=os.terminal_size((40, 24))), \
                patch('ui.views.get_single_key', return_value='A'), redirect_stdout(output):
            self.assertEqual(display_choice_question(question, 13, 60), 'A')
        lines = strip_ansi(output.getvalue()).splitlines()
        self.assertTrue(all(display_width(line) <= 39 for line in lines))
        start = next(i for i, line in enumerate(lines) if line.startswith('  A.'))
        end = next(i for i in range(start, len(lines)) if not lines[i])
        self.assertEqual(' '.join(lines[start:end]).split(), option.split())


if __name__ == '__main__':
    unittest.main()
