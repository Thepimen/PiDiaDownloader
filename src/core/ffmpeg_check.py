"""
FFmpeg binary detector and validator for πDiaDownloader.
Ensures FFmpeg and FFprobe are available for video/audio muxing and encoding.
Includes automatic imageio_ffmpeg binary extraction into a standard ffmpeg.exe executable.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import logger

class FFmpegValidator:
    """Utility class to inspect FFmpeg availability and version information."""

    _cached_info: Optional[Dict[str, Any]] = None

    @classmethod
    def check_ffmpeg(cls, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect FFmpeg binary status.
        Checks custom path, system PATH, and imageio_ffmpeg fallback.
        Returns a dictionary with status, path, and version string.
        """
        if cls._cached_info and not custom_path:
            return cls._cached_info

        executable_name = "ffmpeg.exe" if shutil.which("ffmpeg.exe") or os.name == 'nt' else "ffmpeg"
        target_path = None

        # 1. Check custom path if provided
        if custom_path:
            p = Path(custom_path)
            if p.is_file() and p.name.lower().startswith("ffmpeg"):
                target_path = str(p)
            elif p.is_dir():
                found = p / executable_name
                if found.exists():
                    target_path = str(found)
                    
        # 2. Check system PATH
        if not target_path:
            target_path = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")

        # 3. Check local app bin folder or imageio_ffmpeg fallback
        if not target_path:
            app_bin_dir = Path.home() / ".pidia_downloader" / "bin"
            local_exe = app_bin_dir / executable_name
            
            # Also check legacy path
            legacy_exe = Path.home() / ".pimen_downloader" / "bin" / executable_name
            if not local_exe.exists() and legacy_exe.exists():
                local_exe = legacy_exe
            
            if local_exe.exists():
                target_path = str(local_exe)
            else:
                try:
                    import imageio_ffmpeg
                    img_ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                    if img_ffmpeg_path and Path(img_ffmpeg_path).exists():
                        app_bin_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy(img_ffmpeg_path, local_exe)
                        target_path = str(local_exe)
                        logger.info(f"Extracted imageio_ffmpeg binary to: {target_path}")
                except Exception as e:
                    logger.debug(f"imageio_ffmpeg extraction skipped: {e}")

        if not target_path or not Path(target_path).exists():
            logger.warning("FFmpeg binary not found.")
            info = {
                "available": False,
                "path": None,
                "version": "No instalado",
                "can_mux": False,
                "message": "FFmpeg no detectado."
            }
            cls._cached_info = info
            return info

        # 4. Test execution & version check
        try:
            cmd = [target_path, "-version"]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            first_line = result.stdout.splitlines()[0] if result.stdout else "FFmpeg detectado"
            
            info = {
                "available": True,
                "path": target_path,
                "version": first_line,
                "can_mux": True,
                "message": f"FFmpeg activo ({first_line.split()[2] if len(first_line.split()) > 2 else 'OK'})"
            }
            logger.info(f"FFmpeg validator active: {info['path']}")
            cls._cached_info = info
            return info

        except Exception as e:
            logger.error(f"Error executing FFmpeg binary: {e}")
            info = {
                "available": False,
                "path": target_path,
                "version": "Error de ejecución",
                "can_mux": False,
                "message": f"FFmpeg encontrado en {target_path} pero falló al ejecutarse."
            }
            cls._cached_info = info
            return info

    @classmethod
    def get_ffmpeg_dir(cls) -> Optional[str]:
        """Returns the parent directory of ffmpeg executable if available."""
        info = cls.check_ffmpeg()
        if info["available"] and info["path"]:
            return str(Path(info["path"]).parent)
        return None
