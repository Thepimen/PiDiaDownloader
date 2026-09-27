"""
Format Selector & Options Component for quality, audio extraction, container, and target folder selection.
"""

import os
import subprocess
import customtkinter as ctk
from typing import Dict, Any, Callable
from src.config import (
    QUALITY_OPTIONS,
    CONTAINER_OPTIONS,
    AUDIO_FORMAT_OPTIONS,
    AUDIO_BITRATE_OPTIONS,
    DEFAULT_DOWNLOAD_DIR
)
from src.gui.styles import COLORS, Fonts

class FormatSelectorWidget(ctk.CTkFrame):
    """
    Options panel for quality selection, mode toggling (Video vs Audio), and destination directory.
    """

    def __init__(self, master, on_start_download: Callable[[], None], **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=16,
            **kwargs
        )
        self.on_start_download = on_start_download
        self.download_folder = str(DEFAULT_DOWNLOAD_DIR)
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Header Row
        header_lbl = ctk.CTkLabel(
            self,
            text="⚙️ OPCIONES Y CONFIGURACIÓN DE DESCARGA",
            font=Fonts.TITLE_SMALL,
            text_color=COLORS["accent_primary"]
        )
        header_lbl.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(16, 10))

        # Mode Selection (Segmented Button: Video vs Audio)
        self.mode_var = ctk.StringVar(value="🎬 Vídeo (MP4/MKV)")
        self.mode_segmented = ctk.CTkSegmentedButton(
            self,
            values=["🎬 Vídeo (MP4/MKV)", "🎵 Solo Audio (MP3/WAV)"],
            variable=self.mode_var,
            command=self._on_mode_change,
            selected_color=COLORS["accent_primary"],
            selected_hover_color=COLORS["accent_hover"],
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_dark"],
            height=42
        )
        self.mode_segmented.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))

        # ----------------------------------------------------
        # 1. Video Options Frame (Shown by default)
        # ----------------------------------------------------
        self.video_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.video_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        self.video_frame.columnconfigure(0, weight=1)
        self.video_frame.columnconfigure(1, weight=1)

        # Quality Dropdown
        ctk.CTkLabel(
            self.video_frame,
            text="Resolución / Calidad de Vídeo:",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.quality_combo = ctk.CTkOptionMenu(
            self.video_frame,
            values=QUALITY_OPTIONS,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["surface_border"],
            button_hover_color=COLORS["accent_primary"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            font=Fonts.BODY,
            height=38
        )
        self.quality_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Container Dropdown
        ctk.CTkLabel(
            self.video_frame,
            text="Formato contenedor:",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))

        self.container_combo = ctk.CTkOptionMenu(
            self.video_frame,
            values=CONTAINER_OPTIONS,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["surface_border"],
            button_hover_color=COLORS["accent_primary"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            font=Fonts.BODY,
            height=38
        )
        self.container_combo.grid(row=1, column=1, sticky="ew")

        # ----------------------------------------------------
        # 2. Audio Options Frame (Hidden initially)
        # ----------------------------------------------------
        self.audio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.audio_frame.columnconfigure(0, weight=1)
        self.audio_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.audio_frame,
            text="Formato de audio de salida:",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.audio_fmt_combo = ctk.CTkOptionMenu(
            self.audio_frame,
            values=AUDIO_FORMAT_OPTIONS,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["surface_border"],
            button_hover_color=COLORS["accent_primary"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            font=Fonts.BODY,
            height=38
        )
        self.audio_fmt_combo.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkLabel(
            self.audio_frame,
            text="Tasa de bits (Bitrate de Audio):",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["text_primary"]
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))

        self.audio_bitrate_combo = ctk.CTkOptionMenu(
            self.audio_frame,
            values=AUDIO_BITRATE_OPTIONS,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["surface_border"],
            button_hover_color=COLORS["accent_primary"],
            dropdown_fg_color=COLORS["surface"],
            dropdown_hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            font=Fonts.BODY,
            height=38
        )
        self.audio_bitrate_combo.grid(row=1, column=1, sticky="ew")

        # ----------------------------------------------------
        # Destination Folder Selector Row
        # ----------------------------------------------------
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 10))
        folder_frame.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            folder_frame,
            text="📁 Carpeta de destino:",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["text_secondary"]
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.folder_label = ctk.CTkLabel(
            folder_frame,
            text=self.download_folder,
            font=Fonts.BODY,
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self.folder_label.grid(row=0, column=1, sticky="ew")

        self.browse_btn = ctk.CTkButton(
            folder_frame,
            text="📁 Cambiar...",
            font=Fonts.BODY_BOLD,
            fg_color=COLORS["surface_border"],
            hover_color=COLORS["surface_hover"],
            width=110,
            height=34,
            corner_radius=8,
            command=self._browse_folder
        )
        self.browse_btn.grid(row=0, column=2, padx=5)

        self.open_folder_btn = ctk.CTkButton(
            folder_frame,
            text="📂 Abrir",
            font=Fonts.BODY_BOLD,
            fg_color=COLORS["surface_border"],
            hover_color=COLORS["surface_hover"],
            width=90,
            height=34,
            corner_radius=8,
            command=self._open_folder
        )
        self.open_folder_btn.grid(row=0, column=3)

        # ----------------------------------------------------
        # Prominent CTA Start Download Button
        # ----------------------------------------------------
        self.download_btn = ctk.CTkButton(
            self,
            text="🚀 DESCARGAR AHORA",
            font=("Segoe UI", 16, "bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_dark"],
            height=52,
            corner_radius=12,
            command=self.on_start_download
        )
        self.download_btn.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=20)

    def _on_mode_change(self, value: str):
        """Toggle options panel view based on user selection."""
        if "Solo Audio" in value:
            self.video_frame.grid_forget()
            self.audio_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=5)
        else:
            self.audio_frame.grid_forget()
            self.video_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=5)

    def update_available_resolutions(self, resolutions: list):
        """Dynamically populate available video resolutions if extracted."""
        if resolutions:
            new_opts = [f"Mejor Calidad ({resolutions[0]})"] + resolutions
            self.quality_combo.configure(values=new_opts)
            self.quality_combo.set(new_opts[0])

    def _browse_folder(self):
        folder = ctk.filedialog.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_label.configure(text=folder)

    def _open_folder(self):
        if os.path.exists(self.download_folder):
            os.startfile(self.download_folder) if hasattr(os, 'startfile') else subprocess.run(['xdg-open', self.download_folder])

    def get_options(self) -> Dict[str, Any]:
        """Collect current user option selections into a dictionary."""
        is_audio = "Solo Audio" in self.mode_var.get()
        return {
            "output_dir": self.download_folder,
            "quality": self.quality_combo.get(),
            "container": self.container_combo.get(),
            "is_audio_only": is_audio,
            "audio_format": self.audio_fmt_combo.get(),
            "audio_bitrate": self.audio_bitrate_combo.get(),
        }
