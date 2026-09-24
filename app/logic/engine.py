# runs on its own thread so the window doesn't freeze
import threading
import time

from app.camera.webcam import Webcam, to_preview
from app.detection.detector import GestureDetector

HOLD_FRAMES = 4  # how many frames a gesture has to be held before it plays
PREVIEW_SIZE = (420, 315)


class Engine:
    def __init__(self, settings, player):
        self.settings = settings
        self.player = player
        self.active_gestures = frozenset()
        self.last_played = None  # (gesture, sound)
        self.message = "Starting..."  # None when the video is showing
        self._preview = None
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._held = {}  # gesture -> frames held
        self._last_fired = {}  # gesture -> last time it played

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def take_preview(self):
        with self._lock:
            frame, self._preview = self._preview, None
        return frame

    def _run(self):
        self.message = "Loading models..."
        try:
            detector = GestureDetector()
        except Exception as error:
            self.message = f"Could not load models: {error}"
            return

        webcam = Webcam(self.settings.get("camera_index", 0))
        try:
            while self._running:
                if not self.settings["camera_on"]:
                    webcam.close()
                    self._reset_gestures()
                    self.message = "Camera is off"
                    time.sleep(0.1)
                    continue

                if not webcam.is_open:
                    self.message = "Opening camera..."
                    if not webcam.open():
                        self.message = "Camera not found. Is another app using it?"
                        time.sleep(1)
                        continue

                frame = webcam.read()
                if frame is None:
                    self.message = "Lost the camera feed."
                    time.sleep(0.5)
                    continue
                self.message = None

                if self.settings["gestures_on"]:
                    self._play_new_gestures(detector.detect(frame))
                else:
                    self._reset_gestures()

                with self._lock:
                    self._preview = to_preview(frame, PREVIEW_SIZE)
        finally:
            webcam.close()
            detector.close()

    def _play_new_gestures(self, found):
        self.active_gestures = frozenset(found)
        self._held = {g: self._held.get(g, 0) + 1 for g in found}

        now = time.monotonic()
        cooldown = self.settings["cooldown_seconds"]
        for gesture, frames in self._held.items():
            # == so holding a gesture only plays once
            if frames != HOLD_FRAMES or now - self._last_fired.get(gesture, -cooldown) < cooldown:
                continue
            sound = self.settings["mappings"].get(gesture)
            if sound:
                self.player.play(sound)
                self._last_fired[gesture] = now
                self.last_played = (gesture, sound)

    def _reset_gestures(self):
        self.active_gestures = frozenset()
        self._held = {}
