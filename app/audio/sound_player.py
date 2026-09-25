import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import numpy as np
import pygame

from app.paths import SOUNDS_DIR

from .virtual_mic import VirtualMic

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
        self.virtual_mic = VirtualMic()

    def play(self, name, to_mic=True):
        path = SOUNDS_DIR / name
        if not path.exists():
            return
        if name not in self._loaded:
            self._loaded[name] = pygame.mixer.Sound(str(path))
        sound = self._loaded[name]
        sound.play()
        if to_mic and self.virtual_mic.is_open:
            self.virtual_mic.play(pygame.sndarray.array(sound))

    def set_virtual_mic(self, on):
        if on and not self.virtual_mic.is_open:
            self.virtual_mic.open()
        elif not on:
            self.virtual_mic.close()
            self.virtual_mic.error = None

    def beep(self, rising):
        # two quick tones, going up = on, going down = off
        t = np.arange(int(44100 * 0.07)) / 44100
        fade = np.minimum(1, (0.07 - t) / 0.01)
        freqs = (660, 990) if rising else (990, 660)
        tone = np.concatenate([np.sin(2 * np.pi * f * t) * fade for f in freqs])
        samples = (tone * 0.3 * 32767).astype(np.int16)
        channels = pygame.mixer.get_init()[2]
        pygame.sndarray.make_sound(np.repeat(samples[:, None], channels, axis=1)).play()

    def close(self):
        self.virtual_mic.close()

    def forget_loaded_sounds(self):
        self._loaded.clear()
