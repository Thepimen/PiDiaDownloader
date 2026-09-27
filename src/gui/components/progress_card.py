"""
Real-time progress monitoring card with progress bar, download speed, ETA, and cancel support.
"""

import os
import subprocess
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any
from src.gui.styles import COLORS, Fonts

class ProgressCard(ctk.CTkFrame):
    """
    Progress widget showing downloading progress, transfer rate, ETA, and cancel action.
    """

    def __init__(self, master, on_cancel: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["surface"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=14,
            **kwargs
        )
        self.on_cancel = on_cancel
        self.last_completed_path: Optional[str] = None
        self._build_ui()
        self.reset()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Header status row
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        status_frame.columnconfigure(0, weight=1)

        self.status_title = ctk.CTkLabel(
            status_frame,
            text="⏳ Estado: Listo para descargar",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["text_secondary"]
        )
        self.status_title.grid(row=0, column=0, sticky="w")

        self.percent_label = ctk.CTkLabel(
            status_frame,
            text="0.0%",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.percent_label.grid(row=0, column=1, sticky="e")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            fg_color=COLORS["bg_dark"],
            progress_color=COLORS["accent_primary"],
            height=16,
            corner_radius=8
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=8)
        self.progress_bar.set(0.0)

        # Details Metrics Row (Downloaded size, Speed, ETA)
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 10))
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)

        self.size_label = ctk.CTkLabel(
            metrics_frame,
            text="Descargado: 0 B",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.size_label.grid(row=0, column=0, sticky="w")

        self.speed_label = ctk.CTkLabel(
            metrics_frame,
            text="Velocidad: 0 KB/s",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.speed_label.grid(row=0, column=1, sticky="w")

        self.eta_label = ctk.CTkLabel(
            metrics_frame,
            text="ETA: --:--",
            font=Fonts.BODY_BOLD,
            text_color=COLORS["warning"]
        )
        self.eta_label.grid(row=0, column=2, sticky="e")

        # Action Buttons Container
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.action_frame.columnconfigure(0, weight=1)

        if self.on_cancel:
            self.cancel_btn = ctk.CTkButton(
                self.action_frame,
                text="❌ Cancelar Descarga",
                font=Fonts.BODY_BOLD,
                fg_color=COLORS["danger"],
                hover_color="#d63031",
                text_color=COLORS["text_primary"],
                height=34,
                width=160,
                corner_radius=8,
                command=self.on_cancel
            )
            self.cancel_btn.pack(side="right")

        self.open_file_btn = ctk.CTkButton(
            self.action_frame,
            text="▶️ Abrir Archivo Descargado",
            font=Fonts.BODY_BOLD,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_dark"],
            height=34,
            corner_radius=8,
            command=self._open_completed_file
        )

    def update_progress(self, data: Dict[str, Any]):
        """Update metrics UI safely."""
        status = data.get("status")
        
        if status == "downloading":
            self.open_file_btn.pack_forget()
            if self.on_cancel:
                self.cancel_btn.pack(side="right")

            pct = data.get("percentage", 0.0)
            self.progress_bar.configure(progress_color=COLORS["accent_primary"])
            self.progress_bar.set(pct / 100.0)
            self.percent_label.configure(text=f"{pct:.1f}%")
            
            d_str = data.get("downloaded_str", "0 B")
            t_str = data.get("total_str", "")
            size_txt = f"Descargado: {d_str} / {t_str}" if t_str else f"Descargado: {d_str}"
            self.size_label.configure(text=size_txt)
            
            self.speed_label.configure(text=f"Velocidad: {data.get('speed_str', '0 B/s')}")
            self.eta_label.configure(text=f"ETA: {data.get('eta_str', '--:--')}")
            self.status_title.configure(text="⚡ Descargando contenido multimedia...", text_color=COLORS["accent_primary"])

        elif status == "post-processing":
            self.progress_bar.set(0.99)
            self.percent_label.configure(text="99%")
            self.status_title.configure(text="🔄 Procesando / Guardando archivo...", text_color=COLORS["warning"])
            self.eta_label.configure(text="Un momento...")

        elif status == "completed":
            self.progress_bar.configure(progress_color=COLORS["success"])
            self.progress_bar.set(1.0)
            self.percent_label.configure(text="100%")
            self.status_title.configure(text="✅ Descarga completada con éxito", text_color=COLORS["success"])
            self.eta_label.configure(text="Finalizado")
            
            file_path = data.get("filename")
            if file_path:
                self.last_completed_path = file_path
                if self.on_cancel:
                    self.cancel_btn.pack_forget()
                self.open_file_btn.pack(side="right")

        elif status == "error":
            self.progress_bar.configure(progress_color=COLORS["danger"])
            self.status_title.configure(text="❌ Error en la descarga", text_color=COLORS["danger"])
            self.eta_label.configure(text="Falló")
            if self.on_cancel:
                self.cancel_btn.pack_forget()

    def _open_completed_file(self):
        if self.last_completed_path and os.path.exists(self.last_completed_path):
            os.startfile(self.last_completed_path) if hasattr(os, 'startfile') else subprocess.run(['xdg-open', self.last_completed_path])

    def reset(self):
        self.progress_bar.configure(progress_color=COLORS["accent_primary"])
        self.progress_bar.set(0.0)
        self.percent_label.configure(text="0.0%")
        self.size_label.configure(text="Descargado: 0 B")
        self.speed_label.configure(text="Velocidad: 0 KB/s")
        self.eta_label.configure(text="ETA: --:--")
        self.status_title.configure(text="⏳ Listo para descargar", text_color=COLORS["text_secondary"])
        self.open_file_btn.pack_forget()
        if self.on_cancel:
            self.cancel_btn.pack_forget()
