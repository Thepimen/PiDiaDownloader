"""
History Component displaying recent downloads with quick action buttons.
"""

import os
import subprocess
import customtkinter as ctk
from typing import List, Dict, Any
from src.gui.styles import COLORS, Fonts

class HistoryTableWidget(ctk.CTkFrame):
    """
    Scrollable history list showing recent completed downloads.
    """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=12,
            **kwargs
        )
        self.history_items: List[Dict[str, Any]] = []
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Title Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 5))
        header_frame.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="📜 HISTORIAL DE DESCARGAS RECIENTES",
            font=Fonts.TITLE_SMALL,
            text_color=COLORS["accent_primary"]
        ).grid(row=0, column=0, sticky="w")

        clear_btn = ctk.CTkButton(
            header_frame,
            text="Limpiar Historial",
            font=Fonts.CAPTION,
            fg_color=COLORS["surface_border"],
            hover_color=COLORS["danger"],
            width=100,
            height=24,
            corner_radius=6,
            command=self.clear_history
        )
        clear_btn.grid(row=0, column=1, sticky="e")

        # Scrollable Container for Items
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_dark"],
            corner_radius=8
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.scroll_frame.columnconfigure(0, weight=1)

        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Aún no has realizado ninguna descarga.",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.empty_label.pack(pady=40)

    def add_item(self, item: Dict[str, Any]):
        """Add completed download item to history view."""
        self.history_items.append(item)
        
        if self.empty_label and self.empty_label.winfo_exists():
            self.empty_label.pack_forget()

        item_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["surface"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=8
        )
        item_card.pack(fill="x", pady=4, padx=2)
        item_card.columnconfigure(0, weight=1)

        # Info
        file_path = item.get("file_path", "")
        title = item.get("title", os.path.basename(file_path) if file_path else "Media")
        
        lbl = ctk.CTkLabel(
            item_card,
            text=f"✅ {title}",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        lbl.grid(row=0, column=0, sticky="w", padx=10, pady=8)

        # Action Buttons
        btn_frame = ctk.CTkFrame(item_card, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=10)

        if file_path and os.path.exists(file_path):
            ctk.CTkButton(
                btn_frame,
                text="Abrir Archivo",
                font=Fonts.CAPTION,
                fg_color=COLORS["accent_primary"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["text_dark"],
                width=80, height=24,
                command=lambda p=file_path: self._open_file(p)
            ).pack(side="left", padx=2)

    def _open_file(self, path: str):
        if os.path.exists(path):
            os.startfile(path) if hasattr(os, 'startfile') else subprocess.run(['xdg-open', path])

    def clear_history(self):
        self.history_items.clear()
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.empty_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Aún no has realizado ninguna descarga.",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.empty_label.pack(pady=40)
