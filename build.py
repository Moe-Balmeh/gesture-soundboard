# builds dist/Gesture Soundboard/ and a zip of it for the github release
# run: .venv\Scripts\python.exe build.py
import shutil
from pathlib import Path

import PyInstaller.__main__

from app.detection.detector import download_models

VERSION = "1.0.0"
NAME = "Gesture Soundboard"
ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
APP_DIR = DIST / NAME

PyInstaller.__main__.run([
    "main.py",
    "--name", NAME,
    "--icon", "assets/icon.ico",
    "--windowed",  # no console window
    "--noconfirm",
    "--clean",
    "--collect-data", "customtkinter",
    "--collect-all", "mediapipe",
    "--collect-all", "pyvirtualcam",
    # these pick the windows backend at runtime so pyinstaller can't see them
    "--hidden-import", "pystray._win32",
    "--hidden-import", "pynput.keyboard._win32",
    "--hidden-import", "pynput.mouse._win32",
])

# opencv's ffmpeg part is only for video files, we read the webcam through media foundation
for dll in (APP_DIR / "_internal" / "cv2").glob("opencv_videoio_ffmpeg*.dll"):
    dll.unlink()

# sounds, icon, font and the ai models go next to the exe so people can add their own sounds
download_models()
shutil.copytree(ROOT / "assets", APP_DIR / "assets", ignore=shutil.ignore_patterns("*.gif"))
shutil.copytree(ROOT / "models", APP_DIR / "models")

zip_path = shutil.make_archive(str(DIST / f"GestureSoundboard-v{VERSION}-windows"), "zip", DIST, NAME)
print("built", zip_path)
