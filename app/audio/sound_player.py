import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from app.paths import SOUNDS_DIR

SOUND_EXTENSIONS = {".wav", ".mp3", ".ogg"}


def list_sounds():
    if not SOUNDS_DIR.exists():
        return []
    return sorted(p.name for p in SOUNDS_DIR.iterdir() if p.suffix.lower() in SOUND_EXTENSIONS)


class SoundPlayer:
    def __init__(self):
        pygame.mixer.init(frequency=44100)
        pygame.mixer.set_num_channels(16)  # so sounds can overlap
        self._loaded = {}

    def play(self, name):
        path = SOUNDS_DIR / name
        if not path.exists():
            return
        if name not in self._loaded:
            self._loaded[name] = pygame.mixer.Sound(str(path))
        self._loaded[name].play()

    def forget_loaded_sounds(self):
        self._loaded.clear()
