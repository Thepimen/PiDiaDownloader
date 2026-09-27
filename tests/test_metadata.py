"""
Unit test for MetadataExtractor structure.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.core.metadata import MetadataExtractor

class TestMetadataExtractor(unittest.TestCase):

    @patch("yt_dlp.YoutubeDL")
    def test_extract_info_mock(self, mock_ydl_class):
        mock_instance = MagicMock()
        mock_ydl_class.return_value.__enter__.return_value = mock_instance
        
        mock_instance.extract_info.return_value = {
            "title": "Test Video Title",
            "uploader": "Test Channel",
            "duration": 180,
            "thumbnail": "https://example.com/thumb.jpg",
            "view_count": 5000,
            "formats": [
                {"vcodec": "avc1", "acodec": "mp4a", "height": 1080},
                {"vcodec": "avc1", "acodec": "mp4a", "height": 720}
            ]
        }

        meta = MetadataExtractor.extract_info("https://www.youtube.com/watch?v=mock123")

        self.assertTrue(meta["success"])
        self.assertEqual(meta["title"], "Test Video Title")
        self.assertEqual(meta["uploader"], "Test Channel")
        self.assertEqual(meta["duration_fmt"], "03:00")
        self.assertIn("1080p", meta["resolutions"])
        self.assertIn("720p", meta["resolutions"])

if __name__ == "__main__":
    unittest.main()
