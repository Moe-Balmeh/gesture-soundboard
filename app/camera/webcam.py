import cv2


class Webcam:
    def __init__(self, index=0):
        self.index = index
        self._capture = None

    @property
    def is_open(self):
        return self._capture is not None and self._capture.isOpened()

    def open(self):
        self.close()
        self._capture = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        return self.is_open

    def read(self):
        ok, frame = self._capture.read()
        return cv2.flip(frame, 1) if ok else None  # mirror like a selfie cam

    def close(self):
        if self._capture is not None:
            self._capture.release()
            self._capture = None


def to_preview(frame, size):
    # opencv uses BGR, the UI needs RGB
    return cv2.cvtColor(cv2.resize(frame, size), cv2.COLOR_BGR2RGB)
