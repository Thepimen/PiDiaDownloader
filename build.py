"""
Automated packaging script for πDiaDownloader using PyInstaller.
Generates standalone executable (.exe for Windows / binary for Linux & macOS).
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

# Safe stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
ASSETS_DIR = BASE_DIR / "assets"
MAIN_FILE = BASE_DIR / "main.py"

def clean_build():
    """Remove previous build artifacts."""
    print("[*] Clearing previous build directories...")
    if DIST_DIR.exists():
        try:
            shutil.rmtree(DIST_DIR)
        except Exception as e:
            print(f"Warning: could not remove dist directory: {e}")
    if BUILD_DIR.exists():
        try:
            shutil.rmtree(BUILD_DIR)
        except Exception as e:
            print(f"Warning: could not remove build directory: {e}")

def build_executable():
    """Execute PyInstaller build command."""
    clean_build()
    
    print("[*] Starting PyInstaller build process for πDiaDownloader...")

    # Discover CustomTkinter assets path
    try:
        import customtkinter
        ctk_path = Path(customtkinter.__file__).parent
        ctk_data = f"{ctk_path}{os.pathsep}customtkinter"
    except ImportError:
        print("[!] Error: customtkinter is not installed.")
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",  # Hide background terminal window
        "--name=πDiaDownloader",
        f"--add-data={ctk_data}",
    ]

    # Add assets if exists
    if ASSETS_DIR.exists() and any(ASSETS_DIR.iterdir()):
        cmd.append(f"--add-data={ASSETS_DIR}{os.pathsep}assets")

    # Entry point
    cmd.append(str(MAIN_FILE))

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n[+] BUILD SUCCESSFUL!")
        print(f"[+] Executable located at: {DIST_DIR / 'πDiaDownloader' / 'πDiaDownloader.exe'}")
    else:
        print("\n[!] BUILD FAILED! Check error log above.")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
