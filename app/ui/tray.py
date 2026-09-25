import pystray
from PIL import Image, ImageDraw

ON_COLOR = "#8B5CF6"
OFF_COLOR = "#6B6963"

TOGGLES = [("Camera", "camera_on"), ("Gestures", "gestures_on"), ("Virtual camera", "virtual_cam_on")]


def make_icon(on):
    # purple when gestures are on, gray when off
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((2, 2, 62, 62), radius=14, fill=ON_COLOR if on else OFF_COLOR)
    for x, height in ((14, 18), (28, 34), (42, 24)):
        draw.rounded_rectangle((x, 32 - height // 2, x + 8, 32 + height // 2), radius=4, fill="white")
    return image


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
