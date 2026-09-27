"""
GUI Styling system and visual theme configurations for CustomTkinter.
"""

import customtkinter as ctk
from src.config import THEME_COLORS

def apply_app_theme():
    """Configure CustomTkinter global theme options."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

class Fonts:
    """Font family specifications and sizing."""
    FAMILY = "Segoe UI"
    
    HERO_TITLE = (FAMILY, 24, "bold")
    TITLE_LARGE = (FAMILY, 20, "bold")
    TITLE_MEDIUM = (FAMILY, 16, "bold")
    TITLE_SMALL = (FAMILY, 13, "bold")
    
    BODY = (FAMILY, 12, "normal")
    BODY_BOLD = (FAMILY, 12, "bold")
    CAPTION = (FAMILY, 10, "normal")
    CAPTION_BOLD = (FAMILY, 10, "bold")
    MONO = ("Consolas", 11, "normal")

COLORS = THEME_COLORS
