# mediapipe name -> name shown in the app
HAND_GESTURES = {
    "Thumb_Up": "Thumbs Up",
    "Thumb_Down": "Thumbs Down",
    "Victory": "Peace Sign",
    "Open_Palm": "Open Palm",
    "Closed_Fist": "Fist",
    "Pointing_Up": "Pointing Up",
    "ILoveYou": "Rock On",
}

# ignore hand guesses below this confidence
MIN_HAND_CONFIDENCE = 0.6

# face scores go from 0 to 1 (jawOpen 0.9 = mouth wide open)
FACE_EXPRESSIONS = {
    "Mouth Open": lambda s: s["jawOpen"] > 0.5,
    "Big Smile": lambda s: (s["mouthSmileLeft"] + s["mouthSmileRight"]) / 2 > 0.6,
    "Eyebrows Raised": lambda s: s["browInnerUp"] > 0.5,
}

ALL_GESTURES = [(name, "Hand gesture") for name in HAND_GESTURES.values()] + [
    (name, "Face expression") for name in FACE_EXPRESSIONS
]
