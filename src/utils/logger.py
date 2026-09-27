"""
Structured logging module for πDiaDownloader.
Provides thread-safe logging with GUI callback listener capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Callable, List, Optional
from datetime import datetime

class GUILogHandler(logging.Handler):
    """Custom logging handler that dispatches log records to GUI callbacks."""
    
    def __init__(self, callback: Optional[Callable[[str, str], None]] = None):
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            level_name = record.levelname
            if self.callback:
                self.callback(msg, level_name)
        except Exception:
            self.handleError(record)

class AppLogger:
    """Central logger instance manager for πDiaDownloader."""
    
    _instance: Optional['AppLogger'] = None
    
    def __init__(self):
        self.logger = logging.getLogger("πDiaDownloader")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console Formatter
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%H:%M:%S"
        )
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File Handler
        try:
            log_dir = Path.home() / ".pidia_downloader" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Could not initialize file log handler: {e}")
            
        self.gui_handler: Optional[GUILogHandler] = None

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._instance is None:
            cls._instance = AppLogger()
        return cls._instance.logger

    @classmethod
    def set_gui_callback(cls, callback: Callable[[str, str], None]) -> None:
        inst = cls.get_instance()
        if inst.gui_handler in inst.logger.handlers:
            inst.logger.removeHandler(inst.gui_handler)
        
        inst.gui_handler = GUILogHandler(callback)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
        inst.gui_handler.setFormatter(formatter)
        inst.logger.addHandler(inst.gui_handler)

    @classmethod
    def get_instance(cls) -> 'AppLogger':
        if cls._instance is None:
            cls._instance = AppLogger()
        return cls._instance

logger = AppLogger.get_logger()
