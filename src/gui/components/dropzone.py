"""
Interactive Dropzone component with URL detection, paste button, and Drag & Drop integration.
"""

import customtkinter as ctk
from typing import Callable, Optional
from src.gui.styles import COLORS, Fonts
from src.utils.helpers import is_valid_url

class DropzoneWidget(ctk.CTkFrame):
    """
    Modern Drag & Drop / Input area for media URLs.
    Supports hover highlights, quick paste from clipboard, and text entry callbacks.
    """

    def __init__(
        self,
        master,
        on_url_submitted: Callable[[str], None],
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_color=COLORS["surface_border"],
            border_width=2,
            corner_radius=16,
            **kwargs
        )
        self.on_url_submitted = on_url_submitted
        
        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.container.columnconfigure(0, weight=1)

        # Dropzone Header / Prompt Icon & Text
        self.icon_label = ctk.CTkLabel(
            self.container,
            text="⚡",
            font=("Segoe UI", 36),
            text_color=COLORS["accent_primary"]
        )
        self.icon_label.grid(row=0, column=0, pady=(5, 2))

        self.title_label = ctk.CTkLabel(
            self.container,
            text="Copia, Pega o Arrastra tu Enlace Multimedia aquí",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.grid(row=1, column=0, pady=(0, 2))

        self.subtitle_label = ctk.CTkLabel(
            self.container,
            text="Soporta YouTube, TikTok (sin marca de agua), Twitch clips, X (Twitter), Instagram y +1000 sitios",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.subtitle_label.grid(row=2, column=0, pady=(0, 15))

        # URL Input Bar + Action Buttons
        self.input_frame = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["bg_dark"],
            corner_radius=12,
            border_color=COLORS["surface_border"],
            border_width=1
        )
        self.input_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Pega la URL de tu vídeo o audio aquí (https://...)",
            font=("Segoe UI", 13),
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            placeholder_text_color=COLORS["text_secondary"],
            border_width=0,
            height=50
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(15, 10))
        self.url_entry.bind("<Return>", lambda e: self._submit_url())
        self.url_entry.bind("<KeyRelease>", self._on_key_release)

        # Paste Button
        self.paste_btn = ctk.CTkButton(
            self.input_frame,
            text="📋 Pegar",
            font=Fonts.BODY_BOLD,
            fg_color=COLORS["surface_border"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            width=100,
            height=38,
            corner_radius=8,
            command=self._paste_clipboard
        )
        self.paste_btn.grid(row=0, column=1, padx=5)

        # Inspect / Submit Button
        self.submit_btn = ctk.CTkButton(
            self.input_frame,
            text="⚡ Analizar Enlace",
            font=Fonts.BODY_BOLD,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_dark"],
            width=150,
            height=38,
            corner_radius=8,
            command=self._submit_url
        )
        self.submit_btn.grid(row=0, column=2, padx=(2, 10))

    def _bind_events(self):
        """Bind drag and drop handlers if tkinterdnd2 is enabled on window."""
        self.bind("<Enter>", lambda e: self.configure(border_color=COLORS["accent_primary"]))
        self.bind("<Leave>", lambda e: self.configure(border_color=COLORS["surface_border"]))
        
        try:
            self.drop_target_register("DND_Text", "DND_Files")
            self.dnd_bind("<<Drop>>", self._on_dnd_drop)
        except Exception:
            pass

    def _on_dnd_drop(self, event):
        """Handle Drag and Drop drop event."""
        data = event.data.strip("{}'\"")
        if data:
            self.set_url(data)
            self._submit_url()

    def _on_key_release(self, event):
        url = self.url_entry.get().strip()
        if is_valid_url(url):
            self.configure(border_color=COLORS["accent_primary"])
        else:
            self.configure(border_color=COLORS["surface_border"])

    def _paste_clipboard(self):
        try:
            clipboard_content = self.clipboard_get().strip()
            if clipboard_content:
                self.set_url(clipboard_content)
                self._submit_url()
        except Exception:
            pass

    def _submit_url(self):
        url = self.url_entry.get().strip()
        if url and is_valid_url(url):
            self.on_url_submitted(url)

    def set_url(self, url: str):
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url.strip())

    def clear(self):
        self.url_entry.delete(0, "end")
        self.configure(border_color=COLORS["surface_border"])
