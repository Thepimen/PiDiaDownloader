"""
Metadata Card component displaying video thumbnail, title, uploader, duration, and platform badge.
"""

import io
import threading
import requests
from PIL import Image
import customtkinter as ctk
from typing import Dict, Any, Optional
from src.gui.styles import COLORS, Fonts

class MetadataCard(ctk.CTkFrame):
    """
    Card component for previewing inspected video/audio metadata.
    Fetches thumbnail asynchronously to keep GUI thread ultra responsive.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=14,
            **kwargs
        )
        self._build_ui()
        self.current_metadata: Optional[Dict[str, Any]] = None

    def _build_ui(self):
        self.columnconfigure(1, weight=1)

        # Left: Widescreen Thumbnail Container (240x135)
        self.thumb_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_dark"],
            width=240,
            height=135,
            corner_radius=10
        )
        self.thumb_frame.grid(row=0, column=0, rowspan=4, padx=15, pady=15, sticky="n")
        self.thumb_frame.grid_propagate(False)
        self.thumb_frame.columnconfigure(0, weight=1)
        self.thumb_frame.rowconfigure(0, weight=1)

        self.thumb_label = ctk.CTkLabel(
            self.thumb_frame,
            text="🎬\nEsperando vídeo",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_secondary"]
        )
        self.thumb_label.grid(row=0, column=0)

        # Right: Info Container
        self.platform_badge = ctk.CTkLabel(
            self,
            text="PLATAFORMA",
            font=Fonts.CAPTION_BOLD,
            fg_color=COLORS["accent_glow"],
            text_color=COLORS["accent_primary"],
            corner_radius=6
        )
        self.platform_badge.grid(row=0, column=1, sticky="w", padx=(0, 15), pady=(15, 4))

        self.title_label = ctk.CTkLabel(
            self,
            text="Pega un enlace arriba para inspeccionar metadatos...",
            font=("Segoe UI", 15, "bold"),
            text_color=COLORS["text_primary"],
            anchor="w",
            wraplength=480,
            justify="left"
        )
        self.title_label.grid(row=1, column=1, sticky="w", padx=(0, 15), pady=2)

        # Sub-info Row (Author & Duration)
        self.info_sub_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_sub_frame.grid(row=2, column=1, sticky="w", padx=(0, 15), pady=4)

        self.author_label = ctk.CTkLabel(
            self.info_sub_frame,
            text="👤 Canal: -",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.author_label.pack(side="left", padx=(0, 20))

        self.duration_label = ctk.CTkLabel(
            self.info_sub_frame,
            text="⏱️ 00:00",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["accent_primary"]
        )
        self.duration_label.pack(side="left")

        # Resolutions Chip Row
        self.res_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.res_frame.grid(row=3, column=1, sticky="w", padx=(0, 15), pady=(4, 15))

        self.res_title = ctk.CTkLabel(
            self.res_frame,
            text="Resoluciones detectadas: -",
            font=Fonts.CAPTION,
            text_color=COLORS["text_secondary"]
        )
        self.res_title.pack(side="left")

    def update_metadata(self, meta: Dict[str, Any]):
        """Update card with extracted metadata object."""
        self.current_metadata = meta
        
        # Title & Details
        self.title_label.configure(text=meta.get("title", "Sin título"))
        self.author_label.configure(text=f"👤 {meta.get('uploader', 'Desconocido')}")
        self.duration_label.configure(text=f"⏱️ {meta.get('duration_fmt', '00:00')}")
        
        # Platform Badge Text
        platform_name = meta.get("platform_name", "Web")
        self.platform_badge.configure(text=f"  {platform_name.upper()}  ")

        # Available Resolutions
        resolutions = meta.get("resolutions", [])
        if resolutions:
            res_str = " | ".join(resolutions[:5])
            self.res_title.configure(text=f"Resoluciones disponibles: {res_str}")
        else:
            self.res_title.configure(text="Resoluciones disponibles: Automático")

        # Load Thumbnail in background thread
        thumb_url = meta.get("thumbnail_url")
        if thumb_url:
            threading.Thread(target=self._load_thumbnail, args=(thumb_url,), daemon=True).start()
        else:
            self._reset_thumbnail()

    def _load_thumbnail(self, url: str):
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                image_data = resp.content
                img = Image.open(io.BytesIO(image_data))
                img = img.resize((240, 135), Image.Resampling.LANCZOS)
                
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 135))
                self.after(0, lambda: self.thumb_label.configure(image=ctk_img, text=""))
        except Exception:
            self.after(0, self._reset_thumbnail)

    def _reset_thumbnail(self):
        self.thumb_label.configure(image=None, text="🎬\nSin miniatura")
