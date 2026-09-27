"""
Unit tests for helper utilities.
"""

import unittest
from src.utils.helpers import (
    is_valid_url,
    detect_platform,
    format_bytes,
    format_seconds,
    sanitize_filename
)

class TestHelperUtilities(unittest.TestCase):

    def test_is_valid_url(self):
        self.assertTrue(is_valid_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
        self.assertTrue(is_valid_url("https://tiktok.com/@user/video/123456789"))
        self.assertTrue(is_valid_url("http://twitch.tv/streamer"))
        self.assertFalse(is_valid_url("not_a_url"))
        self.assertFalse(is_valid_url(""))

    def test_detect_platform(self):
        key, name = detect_platform("https://www.youtube.com/watch?v=abc")
        self.assertEqual(key, "youtube")
        self.assertEqual(name, "YouTube")

        key, name = detect_platform("https://www.tiktok.com/@creator/video/111")
        self.assertEqual(key, "tiktok")
        self.assertEqual(name, "TikTok")

        key, name = detect_platform("https://x.com/status/123456")
        self.assertEqual(key, "x")
        self.assertEqual(name, "X (Twitter)")

        key, name = detect_platform("https://unknown-domain.com/video")
        self.assertEqual(key, "generic")
        self.assertEqual(name, "Web Content")

    def test_format_bytes(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(512), "512.00 B")
        self.assertEqual(format_bytes(1048576), "1.00 MB")
        self.assertEqual(format_bytes(1073741824), "1.00 GB")

    def test_format_seconds(self):
        self.assertEqual(format_seconds(0), "00:00")
        self.assertEqual(format_seconds(65), "01:05")
        self.assertEqual(format_seconds(3665), "01:01:05")

    def test_sanitize_filename(self):
        dirty = 'My Video: Title / Test * Invalid?'
        clean = sanitize_filename(dirty)
        self.assertEqual(clean, "My Video Title  Test  Invalid")

if __name__ == "__main__":
    unittest.main()
