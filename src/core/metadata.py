"""
Metadata extractor module utilizing yt-dlp to inspect URLs without downloading.
"""

from typing import Dict, Any, Optional
import yt_dlp
from src.utils.logger import logger
from src.utils.helpers import detect_platform, format_seconds

class MetadataExtractor:
    """Extracts media metadata (title, uploader, thumbnail, formats) via yt-dlp."""

    @staticmethod
    def extract_info(url: str) -> Dict[str, Any]:
        """
        Fetch video/audio metadata without downloading content.
        Returns normalized dictionary with thumbnail, title, author, duration, etc.
        """
        logger.info(f"Extracting metadata for URL: {url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'socket_timeout': 15,
            'nocheckcertificate': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            if not info:
                raise ValueError("No metadata returned from extractor.")

            # If playlist, pick first entry for quick preview
            if 'entries' in info and info['entries']:
                is_playlist = True
                playlist_title = info.get('title', 'Lista de reproducción')
                info = info['entries'][0]
            else:
                is_playlist = False
                playlist_title = None

            platform_key, platform_name = detect_platform(url)
            
            # Select best thumbnail
            thumbnail_url = info.get('thumbnail')
            thumbnails = info.get('thumbnails', [])
            if thumbnails and isinstance(thumbnails, list):
                valid_thumbs = [t for t in thumbnails if isinstance(t, dict) and t.get('url')]
                if valid_thumbs:
                    thumbnail_url = valid_thumbs[-1].get('url')

            # Parse available formats for user selection
            raw_formats = info.get('formats', [])
            res_set = set()
            has_audio = False

            for fmt in raw_formats:
                if not isinstance(fmt, dict):
                    continue
                vcodec = fmt.get('vcodec', 'none')
                acodec = fmt.get('acodec', 'none')
                height = fmt.get('height')

                if vcodec != 'none' and height:
                    res_set.add(f"{height}p")
                if acodec != 'none':
                    has_audio = True

            sorted_res = sorted(
                list(res_set), 
                key=lambda x: int(x.replace("p", "")) if x.replace("p", "").isdigit() else 0,
                reverse=True
            )

            duration_sec = info.get('duration', 0) or 0
            
            normalized_meta = {
                "success": True,
                "url": url,
                "title": info.get('title', 'Sin título'),
                "uploader": info.get('uploader') or info.get('channel') or info.get('creator') or 'Desconocido',
                "duration_raw": duration_sec,
                "duration_fmt": format_seconds(duration_sec),
                "thumbnail_url": thumbnail_url,
                "platform_key": platform_key,
                "platform_name": platform_name,
                "view_count": info.get('view_count', 0),
                "like_count": info.get('like_count', 0),
                "resolutions": sorted_res,
                "has_audio": has_audio,
                "is_playlist": is_playlist,
                "playlist_title": playlist_title,
                "error": None
            }
            
            logger.info(f"Metadata extracted successfully: '{normalized_meta['title']}' ({normalized_meta['platform_name']})")
            return normalized_meta

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Metadata extraction failed for {url}: {err_msg}")
            return {
                "success": False,
                "url": url,
                "title": "No se pudieron obtener los datos",
                "uploader": "-",
                "duration_raw": 0,
                "duration_fmt": "00:00",
                "thumbnail_url": None,
                "platform_key": "generic",
                "platform_name": "Error",
                "resolutions": [],
                "error": err_msg
            }
