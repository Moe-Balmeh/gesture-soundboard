import cv2

WIDTH, HEIGHT = 1280, 720


class Webcam:
    def __init__(self, index=0):
        self.index = index
        self._capture = None

    @property
    def is_open(self):
        return self._capture is not None and self._capture.isOpened()

    def open(self):
        self.close()
        # media foundation gets 720p at 30fps, directshow only managed 10fps
        self._capture = cv2.VideoCapture(self.index, cv2.CAP_MSMF)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self._capture.set(cv2.CAP_PROP_FPS, 30)
        return self.is_open

    def read(self):
        ok, frame = self._capture.read()
        return frame if ok else None

    def close(self):
        if self._capture is not None:
            self._capture.release()
            self._capture = None


def to_preview(frame, size):
    # crop to the preview's shape instead of stretching
    h, w = frame.shape[:2]
    crop_w = min(w, round(h * size[0] / size[1]))
    crop_h = min(h, round(w * size[1] / size[0]))
    x, y = (w - crop_w) // 2, (h - crop_h) // 2
    frame = cv2.resize(frame[y:y + crop_h, x:x + crop_w], size)

    # mirrored like a selfie cam, only for our preview (others should see it unflipped)
    # opencv uses BGR, the UI needs RGB
    return cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
