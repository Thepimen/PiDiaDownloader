"""
Core media downloader module using yt-dlp with real-time progress callbacks.
Handles automatic FFmpeg detection and 403 Forbidden prevention.
"""

import os
import re
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import yt_dlp
from src.config import DEFAULT_DOWNLOAD_DIR
from src.core.ffmpeg_check import FFmpegValidator
from src.utils.logger import logger
from src.utils.helpers import format_bytes, format_seconds, sanitize_filename

class MediaDownloader:
    """Manages yt-dlp download execution with real-time progress callbacks and cancel support."""

    def __init__(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.progress_callback = progress_callback
        self._cancel_flag = threading.Event()
        self.current_process: Optional[yt_dlp.YoutubeDL] = None

    def cancel(self):
        """Signal cancellation of current download process."""
        self._cancel_flag.set()
        logger.warning("Download cancel signal issued.")

    def is_cancelled(self) -> bool:
        return self._cancel_flag.is_set()

    def _progress_hook(self, d: Dict[str, Any]):
        """Internal callback invoked by yt-dlp on progress events."""
        if self._cancel_flag.is_set():
            raise Exception("DOWNLOAD_CANCELLED_BY_USER")

        status = d.get('status')
        
        if status == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded_bytes = d.get('downloaded_bytes', 0)
            speed = d.get('speed') or 0
            eta = d.get('eta') or 0
            
            percentage = 0.0
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100.0

            payload = {
                "status": "downloading",
                "percentage": round(percentage, 1),
                "downloaded_str": format_bytes(downloaded_bytes),
                "total_str": format_bytes(total_bytes),
                "speed_str": f"{format_bytes(speed)}/s" if speed else "Calculando...",
                "eta_str": format_seconds(eta) if eta else "--:--",
                "filename": d.get('filename', ''),
                "raw_data": d
            }

            if self.progress_callback:
                self.progress_callback(payload)

        elif status == 'finished':
            payload = {
                "status": "post-processing",
                "percentage": 99.0,
                "downloaded_str": "Completado",
                "total_str": "",
                "speed_str": "Procesando...",
                "eta_str": "Finalizando...",
                "filename": d.get('filename', ''),
                "raw_data": d
            }
            if self.progress_callback:
                self.progress_callback(payload)

    def download(
        self,
        url: str,
        output_dir: str = str(DEFAULT_DOWNLOAD_DIR),
        quality: str = "Mejor Calidad (Automático)",
        container: str = "mp4",
        is_audio_only: bool = False,
        audio_format: str = "mp3",
        audio_bitrate: str = "320 kbps (Estudio)"
    ) -> Dict[str, Any]:
        """
        Execute media download with 403 Forbidden prevention and FFmpeg support.
        Returns result summary dict.
        """
        self._cancel_flag.clear()
        
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        out_tmpl = str(out_path / "%(title)s.%(ext)s")

        # Check FFmpeg availability
        ffmpeg_info = FFmpegValidator.check_ffmpeg()
        has_ffmpeg = ffmpeg_info.get("available", False)
        ffmpeg_location = ffmpeg_info.get("path")

        ydl_opts: Dict[str, Any] = {
            'outtmpl': out_tmpl,
            'progress_hooks': [self._progress_hook],
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
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

        if has_ffmpeg and ffmpeg_location:
            ydl_opts['ffmpeg_location'] = str(Path(ffmpeg_location).parent)

        if is_audio_only:
            if has_ffmpeg:
                bitrate_clean = audio_bitrate.split()[0] if audio_bitrate else "320"
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format.lower(),
                        'preferredquality': bitrate_clean,
                    }],
                })
            else:
                logger.info("FFmpeg not detected. Downloading native audio stream directly.")
                ydl_opts.update({
                    'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best',
                })
        else:
            # Video + Audio Mode
            height_match = re.search(r'(\d+)p', quality)
            target_height = height_match.group(1) if height_match else None

            if "4K" in quality:
                target_height = "2160"
            elif "2K" in quality:
                target_height = "1440"

            if has_ffmpeg:
                if target_height:
                    format_spec = f"bestvideo[height<={target_height}]+bestaudio/bestvideo+bestaudio/b/best"
                else:
                    format_spec = "bestvideo+bestaudio/b/best"

                ydl_opts['format'] = format_spec
                ydl_opts['merge_output_format'] = container.lower()
            else:
                logger.info("FFmpeg not detected. Downloading best single-stream video+audio.")
                if target_height:
                    ydl_opts['format'] = f"b[height<={target_height}]/b/best"
                else:
                    ydl_opts['format'] = 'b/best'

        logger.info(f"Starting download: {url} | AudioOnly={is_audio_only} | HasFFmpeg={has_ffmpeg}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.current_process = ydl
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                if is_audio_only and has_ffmpeg:
                    base, _ = os.path.splitext(filename)
                    filename = f"{base}.{audio_format.lower()}"

            logger.info(f"Download completed successfully: {filename}")
            
            result = {
                "success": True,
                "url": url,
                "file_path": filename,
                "title": info.get('title', 'Media'),
                "cancelled": False,
                "error": None
            }

            if self.progress_callback:
                self.progress_callback({
                    "status": "completed",
                    "percentage": 100.0,
                    "downloaded_str": "Completado",
                    "total_str": "",
                    "speed_str": "Finalizado",
                    "eta_str": "00:00",
                    "filename": filename
                })

            return result

        except Exception as e:
            err_str = str(e)
            if "DOWNLOAD_CANCELLED_BY_USER" in err_str:
                logger.warning("Download was cancelled by user.")
                return {
                    "success": False,
                    "url": url,
                    "file_path": None,
                    "title": None,
                    "cancelled": True,
                    "error": "Descarga cancelada por el usuario."
                }

            logger.error(f"Download failed for {url}: {err_str}")
            
            if self.progress_callback:
                self.progress_callback({
                    "status": "error",
                    "percentage": 0.0,
                    "error_message": err_str
                })

            return {
                "success": False,
                "url": url,
                "file_path": None,
                "title": None,
                "cancelled": False,
                "error": err_str
            }
