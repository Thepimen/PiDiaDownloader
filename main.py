"""
Application Entry Point for πDiaDownloader.
"""

import sys
import os

# Add src to python path for modular imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.gui.app import πDiaDownloaderApp
from src.utils.logger import logger

def main():
    logger.info("Launching πDiaDownloader application...")
    try:
        app = πDiaDownloaderApp()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Unhandled exception during app execution: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

