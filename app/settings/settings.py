import copy
import json

from app.detection.gestures import ALL_GESTURES
from app.logic.hotkeys import DEFAULT_HOTKEY
from app.paths import SETTINGS_FILE

# so a fresh install already does something
DEFAULT_SOUNDS = {
    "Thumbs Up": "correct.mp3",
    "Thumbs Down": "booing-crowed.mp3",
    "Peace Sign": "la-peace.mp3",
    "Open Palm": "tada.wav",
    "Fist": "vine_boom.wav",
    "Pointing Up": "gun shot.mp3",
    "Rock On": "airhorn.wav",
    "Mouth Open": "fahhh.mp3",
    "Big Smile": "aww.mp3",
    "Eyebrows Raised": "bruh.mp3",
}

DEFAULT_SETTINGS = {
    "camera_on": True,
    "gestures_on": True,
    "virtual_cam_on": False,
    "virtual_mic_on": False,
    "mic_device": None,
    "mic_volume": 1.0,
    "sounds_volume": 1.0,
    "camera_index": 0,
    "cooldown_seconds": 1.3,
    "hotkey": DEFAULT_HOTKEY,
    "mappings": {name: None for name, _ in ALL_GESTURES} | DEFAULT_SOUNDS,
    "enabled_gestures": {name: True for name, _ in ALL_GESTURES},
}


def load_settings():
    settings = copy.deepcopy(DEFAULT_SETTINGS)
    if SETTINGS_FILE.exists():
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return settings
        settings.update({k: v for k, v in saved.items() if k != "mappings"})
        settings["mappings"].update(saved.get("mappings", {}))
    return settings


def save_settings(settings):
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
