import pystray
from PIL import Image, ImageOps

from app.paths import ICON_PNG

TOGGLES = [
    ("Camera", "camera_on"), ("Gestures", "gestures_on"), ("Virtual camera", "virtual_cam_on"),
    ("Virtual mic", "virtual_mic_on"),
]


def make_icon(on):
    # the app icon when gestures are on, a gray copy when off
    icon = Image.open(ICON_PNG).convert("RGBA")
    if on:
        return icon
    gray = ImageOps.grayscale(icon).convert("RGBA")
    gray.putalpha(icon.getchannel("A"))
    return gray


class Tray:
    # pystray runs on its own thread, so menu clicks just call send()
    # and the window handles them on its own thread
    def __init__(self, settings, send):
        self.settings = settings

        def toggle_item(label, key):
            return pystray.MenuItem(
                label, lambda: send(("toggle", key)), checked=lambda _: self.settings[key]
            )

        menu = pystray.Menu(
            pystray.MenuItem("Show window", lambda: send(("show",)), default=True),
            pystray.Menu.SEPARATOR,
            *[toggle_item(label, key) for label, key in TOGGLES],
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: send(("quit",))),
        )
        self.icon = pystray.Icon("gesture-soundboard", make_icon(True), "Gesture Soundboard", menu)
        self.refresh()

    def start(self):
        self.icon.run_detached()

    def refresh(self):
        # camera off also means no sounds, so gray for that too
        on = self.settings["camera_on"] and self.settings["gestures_on"]
        self.icon.icon = make_icon(on)
        self.icon.title = f"Gesture Soundboard · {'listening' if on else 'paused'}"
        self.icon.update_menu()

    def notify(self, text):
        self.icon.notify(text, "Gesture Soundboard")

    def stop(self):
        self.icon.stop()
