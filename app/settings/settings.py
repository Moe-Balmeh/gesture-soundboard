import copy
import json

from app.detection.gestures import ALL_GESTURES
from app.paths import SETTINGS_FILE

DEFAULT_SETTINGS = {
    "camera_on": True,
    "gestures_on": True,
    "camera_index": 0,
    "cooldown_seconds": 1.3,
    "mappings": {name: None for name, _ in ALL_GESTURES},
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
