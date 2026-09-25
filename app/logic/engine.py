# runs on its own thread so the window doesn't freeze
import threading
import time

from app.camera.virtual_cam import VirtualCam
from app.camera.webcam import Webcam, to_preview
from app.detection.detector import GestureDetector

HOLD_FRAMES = 4  # how many frames a gesture has to be held before it plays
PREVIEW_SIZE = (448, 252)


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
        self.virtual_cam = VirtualCam()
        self._frame_size = (1280, 720)

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
                self._update_virtual_cam()

                if not self.settings["camera_on"]:
                    webcam.close()
                    self._reset_gestures()
                    self.message = "Camera is off"
                    self._send_off_screen()
                    time.sleep(0.1)
                    continue

                if not webcam.is_open:
                    self.message = "Opening camera..."
                    if not webcam.open():
                        self.message = "Camera not found. Is another app using it?"
                        self._send_off_screen()
                        time.sleep(1)
                        continue

                frame = webcam.read()
                if frame is None:
                    self.message = "Lost the camera feed."
                    time.sleep(0.5)
                    continue
                self.message = None

                size = (frame.shape[1], frame.shape[0])
                if size != self._frame_size:
                    # reopens at the webcam's real size on the next loop
                    self._frame_size = size
                    self.virtual_cam.close()

                if self.settings["gestures_on"]:
                    self._play_new_gestures(detector.detect(frame))
                else:
                    self._reset_gestures()

                if self.virtual_cam.is_open:
                    self.virtual_cam.send(frame)

                with self._lock:
                    self._preview = to_preview(frame, PREVIEW_SIZE)
        finally:
            webcam.close()
            self.virtual_cam.close()
            detector.close()

    def _update_virtual_cam(self):
        if not self.settings["virtual_cam_on"]:
            self.virtual_cam.close()
            self.virtual_cam.error = None  # turning it off and on again retries
        elif not self.virtual_cam.is_open and self.virtual_cam.error is None:
            self.virtual_cam.open(*self._frame_size)

    def _send_off_screen(self):
        if self.virtual_cam.is_open:
            self.virtual_cam.send_off_screen()

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
