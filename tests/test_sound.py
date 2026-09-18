import unittest
import sys
from ui.terminal import play_sound, _build_wav_tone, _init_sound_cache, _SOUND_CACHE

class SoundSystemTests(unittest.TestCase):
    def test_build_wav_tone_valid_structure(self):
        wav = _build_wav_tone([880, 1320], duration_ms=50, volume=0.5)
        self.assertTrue(isinstance(wav, bytes))
        self.assertTrue(len(wav) > 44)
        self.assertEqual(wav[:4], b'RIFF')
        self.assertEqual(wav[8:12], b'WAVE')

    def test_init_sound_cache_has_all_events(self):
        _init_sound_cache()
        expected = ['correct', 'wrong', 'flag', 'navigate', 'finish']
        for key in expected:
            self.assertIn(key, _SOUND_CACHE)
            self.assertTrue(len(_SOUND_CACHE[key]) > 100)

    def test_play_sound_disabled(self):
        # Should return immediately without doing anything
        play_sound('correct', enabled=False)

    def test_play_sound_all_types(self):
        for s_type in ['correct', 'wrong', 'flag', 'navigate', 'finish', 'unknown']:
            play_sound(s_type, enabled=True)

if __name__ == '__main__':
    unittest.main()
