import sys
from pathlib import Path

# as an .exe the assets, models and config.json sit next to the exe
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOUNDS_DIR = PROJECT_ROOT / "assets" / "sounds"
ICON_ICO = PROJECT_ROOT / "assets" / "icon.ico"
ICON_PNG = PROJECT_ROOT / "assets" / "icon.png"
HEADING_FONT_FILE = PROJECT_ROOT / "assets" / "fonts" / "Sora-SemiBold.ttf"
MODELS_DIR = PROJECT_ROOT / "models"
SETTINGS_FILE = PROJECT_ROOT / "config.json"
