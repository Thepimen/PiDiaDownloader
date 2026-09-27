"""
Utility helper functions for formatting, URL validation, and string sanitization.
"""

import re
import urllib.parse
from typing import Tuple
from src.config import SUPPORTED_PLATFORMS

URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE
)

def is_valid_url(url: str) -> bool:
    """Check if the provided string is a valid HTTP/HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return bool(URL_REGEX.match(url))

def detect_platform(url: str) -> Tuple[str, str]:
    """
    Detect media platform name and brand accent color from URL.
    Returns (platform_key, display_name).
    """
    if not url:
        return "generic", "Desconocido"
    
    url_lower = url.lower()
    for platform_key, domains in SUPPORTED_PLATFORMS.items():
        for domain in domains:
            if domain in url_lower:
                name_map = {
                    "youtube": "YouTube",
                    "tiktok": "TikTok",
                    "twitch": "Twitch",
                    "x": "X (Twitter)",
                    "instagram": "Instagram",
                    "vimeo": "Vimeo"
                }
                return platform_key, name_map.get(platform_key, platform_key.capitalize())
                
    return "generic", "Web Content"

def format_bytes(bytes_count: float) -> str:
    """Format bytes integer/float to human readable string (e.g. 15.4 MB)."""
    if not bytes_count or bytes_count <= 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(bytes_count)
    
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
        
    return f"{size:.2f} {units[unit_index]}"

def format_seconds(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    if not seconds or seconds < 0:
        return "00:00"
    
    tot_sec = int(seconds)
    hours = tot_sec // 3600
    minutes = (tot_sec % 3600) // 60
    secs = tot_sec % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent invalid characters on Windows, Linux, and macOS."""
    if not filename:
        return "downloaded_media"
    
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Strip whitespace and trailing dots
    sanitized = sanitized.strip().strip(".")
    return sanitized if sanitized else "downloaded_media"
