"""
Unit tests for FFmpeg detection validator.
"""

import unittest
from src.core.ffmpeg_check import FFmpegValidator

class TestFFmpegValidator(unittest.TestCase):

    def test_ffmpeg_check_returns_dict(self):
        result = FFmpegValidator.check_ffmpeg()
        self.assertIsInstance(result, dict)
        self.assertIn("available", result)
        self.assertIn("version", result)
        self.assertIn("can_mux", result)

if __name__ == "__main__":
    unittest.main()
