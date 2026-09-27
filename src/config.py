"""
Application configuration constants, color palettes, and settings for πDiaDownloader.
"""

import os
from pathlib import Path

# App Identity
APP_NAME = "πDiaDownloader"
APP_ALIAS = "PiDiaDownloader"
APP_VERSION = "1.1.0"
APP_AUTHOR = "πDiaDownloader Architecture"

# Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_DOWNLOAD_DIR = Path(os.path.expanduser("~/Downloads")) / "πDiaDownloads"
DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Color Palette (Ultra-Sleek Modern Dark Mode with Electric Cyan Accents)
THEME_COLORS = {
    "bg_dark": "#0a0c14",          # Main window background
    "bg_secondary": "#111524",     # Header & nav background
    "surface": "#161b2e",          # Card background
    "surface_hover": "#1f2640",    # Card hover state
    "surface_border": "#262f4d",   # Borders
    
    # Accent Colors
    "accent_primary": "#00f0ff",   # Cyan / Electric Blue primary accent
    "accent_hover": "#00d0e0",     # Hover state for primary buttons
    "accent_glow": "#122838",      # Dark cyan glow background
    "accent_secondary": "#7b2cbf", # Neon purple secondary accent
    
    # Status Colors
    "success": "#00e676",          # Completed / Active (Green)
    "warning": "#ffb300",          # In progress / Warning (Amber)
    "danger": "#ff3838",           # Errors / Cancelled (Red)
    "info": "#29b6f6",             # Information notices (Sky Blue)
    
    # Text Colors
    "text_primary": "#ffffff",     # High contrast pure white text
    "text_secondary": "#94a3b8",   # Soft slate subtitle text
    "text_dark": "#060911",        # Dark text on bright accents
}

# Quality & Format Options
QUALITY_OPTIONS = [
    "Mejor Calidad (Automático)",
    "4K (2160p)",
    "2K (1440p)",
    "Full HD (1080p)",
    "HD (720p)",
    "SD (480p)",
]

CONTAINER_OPTIONS = ["mp4", "mkv", "webm"]
AUDIO_FORMAT_OPTIONS = ["mp3", "wav", "flac", "m4a"]
AUDIO_BITRATE_OPTIONS = ["320 kbps (Estudio)", "256 kbps (Alta)", "192 kbps (Estándar)", "128 kbps (Media)"]

# Supported Platform Matchers
SUPPORTED_PLATFORMS = {
    "youtube": ["youtube.com", "youtu.be"],
    "tiktok": ["tiktok.com"],
    "twitch": ["twitch.tv"],
    "x": ["x.com", "twitter.com"],
    "instagram": ["instagram.com"],
    "vimeo": ["vimeo.com"],
}
