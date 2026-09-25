import cv2
import numpy as np
import pyvirtualcam

OFF_SCREEN_COLOR = (36, 38, 38)  # BGR


class VirtualCam:
    def __init__(self):
        self._cam = None
        self.error = None

    @property
    def is_open(self):
        return self._cam is not None

    def open(self, width, height):
        try:
            # uses the driver that comes with OBS
            self._cam = pyvirtualcam.Camera(width, height, 30, fmt=pyvirtualcam.PixelFormat.BGR)
            self.error = None
        except RuntimeError:
            self._cam = None
            self.error = "Couldn't start. Is OBS's own virtual camera running?"
        return self.is_open

    def send(self, frame):
        if (frame.shape[1], frame.shape[0]) != (self._cam.width, self._cam.height):
            frame = cv2.resize(frame, (self._cam.width, self._cam.height))
        self._cam.send(frame)

    def send_off_screen(self):
        # so zoom/meet show "camera off" instead of a frozen frame
        frame = np.full((self._cam.height, self._cam.width, 3), OFF_SCREEN_COLOR, np.uint8)
        text = "Camera off"
        font = cv2.FONT_HERSHEY_SIMPLEX
        (w, h), _ = cv2.getTextSize(text, font, 1, 2)
        position = ((frame.shape[1] - w) // 2, (frame.shape[0] + h) // 2)
        cv2.putText(frame, text, position, font, 1, (160, 163, 166), 2, cv2.LINE_AA)
        self._cam.send(frame)

    def close(self):
        if self._cam is not None:
            self._cam.close()
            self._cam = None
