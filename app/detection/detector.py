import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from app.paths import MODELS_DIR

from .gestures import FACE_EXPRESSIONS, HAND_GESTURES, MIN_HAND_CONFIDENCE

MODEL_URLS = {
    "gesture_recognizer.task": "https://storage.googleapis.com/mediapipe-models/"
    "gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task",
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
}


def download_models():
    MODELS_DIR.mkdir(exist_ok=True)
    for filename, url in MODEL_URLS.items():
        path = MODELS_DIR / filename
        if not path.exists():
            urllib.request.urlretrieve(url, path)


class GestureDetector:
    def __init__(self):
        download_models()
        self.hands = vision.GestureRecognizer.create_from_options(
            vision.GestureRecognizerOptions(
                base_options=mp_python.BaseOptions(
                    model_asset_path=str(MODELS_DIR / "gesture_recognizer.task")
                ),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2,
            )
        )
        self.face = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=mp_python.BaseOptions(
                    model_asset_path=str(MODELS_DIR / "face_landmarker.task")
                ),
                running_mode=vision.RunningMode.VIDEO,
                output_face_blendshapes=True,
                num_faces=1,
            )
        )
        self._start = time.monotonic()
        self._last_timestamp = -1

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # video mode needs timestamps that keep increasing
        timestamp = max(int((time.monotonic() - self._start) * 1000), self._last_timestamp + 1)
        self._last_timestamp = timestamp

        found = set()
        for hand in self.hands.recognize_for_video(image, timestamp).gestures:
            best_guess = hand[0]
            if best_guess.score >= MIN_HAND_CONFIDENCE and best_guess.category_name in HAND_GESTURES:
                found.add(HAND_GESTURES[best_guess.category_name])

        face_result = self.face.detect_for_video(image, timestamp)
        if face_result.face_blendshapes:
            scores = {c.category_name: c.score for c in face_result.face_blendshapes[0]}
            found.update(name for name, rule in FACE_EXPRESSIONS.items() if rule(scores))

        return found

    def close(self):
        self.hands.close()
        self.face.close()
