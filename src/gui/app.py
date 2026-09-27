"""
Main GUI Application window and multi-threaded event orchestration for πDiaDownloader.
"""

import os
import queue
import threading
import customtkinter as ctk
from typing import Dict, Any, Optional

from src.config import APP_NAME, APP_VERSION, THEME_COLORS
from src.core.downloader import MediaDownloader
from src.core.metadata import MetadataExtractor
from src.core.ffmpeg_check import FFmpegValidator
from src.gui.styles import apply_app_theme, COLORS, Fonts
from src.gui.components.dropzone import DropzoneWidget
from src.gui.components.metadata_card import MetadataCard
from src.gui.components.format_selector import FormatSelectorWidget
from src.gui.components.progress_card import ProgressCard
from src.gui.components.history_table import HistoryTableWidget
from src.utils.logger import logger, AppLogger

# Check TkinterDnD support
try:
    from tkinterdnd2 import TkinterDnD
    BaseWindow = TkinterDnD.DnDWrapper
except ImportError:
    BaseWindow = object


class πDiaDownloaderApp(ctk.CTk, BaseWindow):
    """
    Main desktop application class for πDiaDownloader.
    Combines CustomTkinter UI widgets with multi-threaded extraction & download workers.
    """

    def __init__(self):
        if hasattr(BaseWindow, '__init__') and BaseWindow is not object:
            super().__init__()
        else:
            super().__init__()

        apply_app_theme()

        # Window Setup
        self.title(f"{APP_NAME} v{APP_VERSION} — Extractor Multimedia Pro")
        self.geometry("1020x780")
        self.minsize(920, 680)
        self.configure(fg_color=COLORS["bg_dark"])

        # Thread Queue for UI updates
        self.ui_queue = queue.Queue()

        # State Variables
        self.current_url: Optional[str] = None
        self.current_metadata: Optional[Dict[str, Any]] = None
        self.active_downloader: Optional[MediaDownloader] = None
        self.is_downloading = False
        self.is_inspecting = False

        self._build_layout()
        self._check_system_binaries()
        self._setup_logger_callback()

        # Start UI Queue Poller
        self.after(100, self._process_ui_queue)

    def _build_layout(self):
        """Construct application header, tabs, main content, and status bar."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # ----------------------------------------------------
        # TOP HEADER NAVBAR
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            height=65
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.columnconfigure(0, weight=1)

        brand_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=12)

        self.logo_label = ctk.CTkLabel(
            brand_frame,
            text="⚡ PulseDownloader",
            font=Fonts.HERO_TITLE,
            text_color=COLORS["accent_primary"]
        )
        self.logo_label.pack(side="left")

        self.subtitle_tag = ctk.CTkLabel(
            brand_frame,
            text="PRO CREATOR EDITION",
            font=Fonts.CAPTION_BOLD,
            fg_color=COLORS["accent_glow"],
            text_color=COLORS["accent_primary"],
            corner_radius=6
        )
        self.subtitle_tag.pack(side="left", padx=12)

        # FFmpeg Status Indicator Badge
        self.ffmpeg_badge = ctk.CTkLabel(
            self.header_frame,
            text="🟢 FFmpeg: Verificando...",
            font=Fonts.BODY_BOLD,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            corner_radius=8,
            height=32
        )
        self.ffmpeg_badge.pack(side="right", padx=20)

        # ----------------------------------------------------
        # MAIN TABVIEW (DESCARGA / HISTORIAL / LOGS)
        # ----------------------------------------------------
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_dark"],
            segmented_button_fg_color=COLORS["surface"],
            segmented_button_selected_color=COLORS["accent_primary"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["surface"],
            segmented_button_unselected_hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_dark"],
            corner_radius=14
        )
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 10))

        # Add Tabs
        self.tab_download = self.tabview.add("📥 Descarga Directa")
        self.tab_history = self.tabview.add("📜 Historial de Descargas")
        self.tab_logs = self.tabview.add("💻 Consola del Sistema")

        # Configure Tab 1 (Descarga Directa)
        self.tab_download.columnconfigure(0, weight=1)
        
        self.download_scroll = ctk.CTkScrollableFrame(
            self.tab_download,
            fg_color="transparent"
        )
        self.download_scroll.pack(fill="both", expand=True)
        self.download_scroll.columnconfigure(0, weight=1)

        # 1. Dropzone Widget
        self.dropzone = DropzoneWidget(
            self.download_scroll,
            on_url_submitted=self._on_url_submitted
        )
        self.dropzone.pack(fill="x", pady=(0, 12))

        # 2. Metadata Preview Card
        self.metadata_card = MetadataCard(self.download_scroll)
        self.metadata_card.pack(fill="x", pady=(0, 12))

        # 3. Format & Options Selector Widget
        self.format_selector = FormatSelectorWidget(
            self.download_scroll,
            on_start_download=self._start_download_process
        )
        self.format_selector.pack(fill="x", pady=(0, 12))

        # 4. Progress Tracking Card
        self.progress_card = ProgressCard(
            self.download_scroll,
            on_cancel=self._cancel_download
        )
        self.progress_card.pack(fill="x", pady=(0, 12))

        # Configure Tab 2 (Historial)
        self.tab_history.columnconfigure(0, weight=1)
        self.tab_history.rowconfigure(0, weight=1)
        self.history_widget = HistoryTableWidget(self.tab_history)
        self.history_widget.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Configure Tab 3 (Logs Console)
        self.tab_logs.columnconfigure(0, weight=1)
        self.tab_logs.rowconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(
            self.tab_logs,
            font=Fonts.MONO,
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["accent_primary"],
            border_color=COLORS["surface_border"],
            border_width=1,
            corner_radius=8
        )
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # ----------------------------------------------------
        # BOTTOM STATUS BAR
        # ----------------------------------------------------
        self.status_bar = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            height=30
        )
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.columnconfigure(0, weight=1)

        self.status_info_label = ctk.CTkLabel(
            self.status_bar,
            text="Listo. Pega o arrastra un enlace para comenzar.",
            font=Fonts.BODY,
            text_color=COLORS["text_secondary"]
        )
        self.status_info_label.pack(side="left", padx=15)

        self.status_version_label = ctk.CTkLabel(
            self.status_bar,
            text=f"Python 3.11+ | yt-dlp Core | {APP_NAME} v{APP_VERSION}",
            font=Fonts.CAPTION,
            text_color=COLORS["text_secondary"]
        )
        self.status_version_label.pack(side="right", padx=15)

    def _check_system_binaries(self):
        """Check FFmpeg binary asynchronously."""
        def worker():
            info = FFmpegValidator.check_ffmpeg()
            self.ui_queue.put(("ffmpeg_status", info))

        threading.Thread(target=worker, daemon=True).start()

    def _setup_logger_callback(self):
        """Connect application logger to GUI logs tab."""
        def gui_log_cb(msg: str, level: str):
            self.ui_queue.put(("log_message", (msg, level)))
            
        AppLogger.set_gui_callback(gui_log_cb)

    # ----------------------------------------------------
    # EVENT HANDLERS & THREAD WORKERS
    # ----------------------------------------------------
    def _on_url_submitted(self, url: str):
        """Handle URL inspection submission."""
        if self.is_inspecting:
            return

        self.current_url = url
        self.is_inspecting = True
        self.status_info_label.configure(text=f"Inspeccionando metadatos para: {url}...")
        self.dropzone.submit_btn.configure(state="disabled", text="⏳ Analizando...")

        def worker():
            meta = MetadataExtractor.extract_info(url)
            self.ui_queue.put(("metadata_result", meta))

        threading.Thread(target=worker, daemon=True).start()

    def _start_download_process(self):
        """Handle CTA Start Download button click."""
        if not self.current_url:
            self.status_info_label.configure(text="⚠️ Por favor pega o arrastra un enlace primero.", text_color=COLORS["warning"])
            return

        if self.is_downloading:
            return

        self.is_downloading = True
        self.progress_card.reset()
        self.format_selector.download_btn.configure(state="disabled", text="⏳ Iniciando Descarga...")
        self.status_info_label.configure(text="Iniciando motor de descarga...")

        opts = self.format_selector.get_options()
        self.active_downloader = MediaDownloader(
            progress_callback=lambda p: self.ui_queue.put(("progress_update", p))
        )

        def worker():
            result = self.active_downloader.download(
                url=self.current_url,
                output_dir=opts["output_dir"],
                quality=opts["quality"],
                container=opts["container"],
                is_audio_only=opts["is_audio_only"],
                audio_format=opts["audio_format"],
                audio_bitrate=opts["audio_bitrate"]
            )
            self.ui_queue.put(("download_result", result))

        threading.Thread(target=worker, daemon=True).start()

    def _cancel_download(self):
        """Cancel active download."""
        if self.active_downloader and self.is_downloading:
            self.active_downloader.cancel()
            self.status_info_label.configure(text="Cancelando descarga...", text_color=COLORS["warning"])

    # ----------------------------------------------------
    # UI QUEUE DISPATCHER
    # ----------------------------------------------------
    def _process_ui_queue(self):
        """Periodically process messages queued by background threads."""
        try:
            while True:
                msg_type, payload = self.ui_queue.get_nowait()

                if msg_type == "ffmpeg_status":
                    if payload["available"]:
                        self.ffmpeg_badge.configure(
                            text=" 🟢 FFmpeg: Activo ",
                            fg_color="#103820",
                            text_color=COLORS["success"]
                        )
                    else:
                        self.ffmpeg_badge.configure(
                            text=" ⚠️ FFmpeg: Limitado ",
                            fg_color="#382800",
                            text_color=COLORS["warning"]
                        )

                elif msg_type == "metadata_result":
                    self.is_inspecting = False
                    self.dropzone.submit_btn.configure(state="normal", text="⚡ Analizar Enlace")
                    
                    if payload["success"]:
                        self.current_metadata = payload
                        self.metadata_card.update_metadata(payload)
                        self.format_selector.update_available_resolutions(payload.get("resolutions", []))
                        self.status_info_label.configure(
                            text=f"Metadatos listos: '{payload['title']}'",
                            text_color=COLORS["text_primary"]
                        )
                    else:
                        self.status_info_label.configure(
                            text=f"❌ Error al inspeccionar URL: {payload['error']}",
                            text_color=COLORS["danger"]
                        )

                elif msg_type == "progress_update":
                    self.progress_card.update_progress(payload)

                elif msg_type == "download_result":
                    self.is_downloading = False
                    self.format_selector.download_btn.configure(state="normal", text="🚀 DESCARGAR AHORA")
                    
                    if payload["success"]:
                        self.status_info_label.configure(
                            text=f"✅ Descarga completada: {payload.get('file_path')}",
                            text_color=COLORS["success"]
                        )
                        self.history_widget.add_item(payload)
                    elif payload.get("cancelled"):
                        self.status_info_label.configure(
                            text="⚠️ Descarga cancelada por el usuario.",
                            text_color=COLORS["warning"]
                        )
                    else:
                        self.status_info_label.configure(
                            text=f"❌ Fallo en la descarga: {payload.get('error')}",
                            text_color=COLORS["danger"]
                        )

                elif msg_type == "log_message":
                    msg, level = payload
                    self.log_textbox.insert("end", f"{msg}\n")
                    self.log_textbox.see("end")

        except queue.Empty:
            pass
        finally:
            self.after(100, self._process_ui_queue)


# Compatibility aliases
PiDiaDownloaderApp = πDiaDownloaderApp


