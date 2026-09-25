import os

import customtkinter as ctk
from PIL import Image

from app.audio.sound_player import SoundPlayer, list_sounds
from app.detection.gestures import ALL_GESTURES
from app.logic.engine import PREVIEW_SIZE, Engine
from app.paths import SOUNDS_DIR
from app.settings.settings import load_settings, save_settings

from . import theme
from .widgets import NO_SOUND, GestureRow, ToggleRow, card, outline_button

REFRESH_MS = 33  # ~30 fps


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=theme.BG)
        self.title("Gesture Soundboard")
        self.geometry("1280x720")
        self.minsize(1200, 640)

        self.settings = load_settings()
        self.player = SoundPlayer()
        self.engine = Engine(self.settings, self.player)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main_area()

        self.engine.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._refresh_id = self.after(REFRESH_MS, self._refresh)

    # layout

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=theme.SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            sidebar, text="Gesture\nSoundboard", justify="left", anchor="w",
            font=theme.font(26, heading=True), text_color=theme.TEXT,
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(28, 4))
        ctk.CTkLabel(
            sidebar, text="Meme sounds on cue for\nyour calls and streams.", justify="left",
            anchor="w", font=theme.font(13), text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=24)

        controls = card(sidebar)
        controls.grid(row=2, column=0, sticky="ew", padx=16, pady=(28, 0))
        controls.grid_columnconfigure(0, weight=1)
        self.camera_toggle = ToggleRow(
            controls, "Camera", "On · live", "Off · free for other apps",
            self.settings["camera_on"], self._on_camera_toggle,
        )
        self.camera_toggle.grid(row=0, column=0, sticky="ew", padx=(16, 10), pady=(14, 10))
        ctk.CTkFrame(controls, height=1, fg_color=theme.BORDER).grid(row=1, column=0, sticky="ew", padx=16)
        self.gestures_toggle = ToggleRow(
            controls, "Gestures", "On · listening", "Off · paused",
            self.settings["gestures_on"], self._on_gestures_toggle,
        )
        self.gestures_toggle.grid(row=2, column=0, sticky="ew", padx=(16, 10), pady=10)
        ctk.CTkFrame(controls, height=1, fg_color=theme.BORDER).grid(row=3, column=0, sticky="ew", padx=16)
        self.virtual_cam_toggle = ToggleRow(
            controls, "Virtual camera", "On · pick \"OBS Virtual Camera\" in Zoom/Meet", "Off",
            self.settings["virtual_cam_on"], self._on_virtual_cam_toggle,
        )
        self.virtual_cam_toggle.grid(row=4, column=0, sticky="ew", padx=(16, 10), pady=(10, 14))
        self._shown_vcam_error = None

        self.last_played_label = ctk.CTkLabel(
            sidebar, text="", justify="left", anchor="w", wraplength=220,
            font=theme.font(13), text_color=theme.TEXT_MUTED,
        )
        self.last_played_label.grid(row=3, column=0, sticky="w", padx=24, pady=(16, 0))

        outline_button(sidebar, "Open sounds folder", lambda: os.startfile(SOUNDS_DIR)).grid(
            row=5, column=0, sticky="ew", padx=16, pady=(0, 8)
        )
        outline_button(sidebar, "Reload sounds", self._reload_sounds).grid(
            row=6, column=0, sticky="ew", padx=16, pady=(0, 16)
        )
        appearance = ctk.CTkSegmentedButton(
            sidebar, values=["System", "Light", "Dark"], command=self._on_appearance,
            font=theme.font(12), height=30, corner_radius=8,
            fg_color=theme.SURFACE_HOVER, unselected_color=theme.SURFACE_HOVER,
            unselected_hover_color=theme.BORDER, selected_color=theme.ACCENT_SOFT,
            selected_hover_color=theme.ACCENT_SOFT, text_color=theme.TEXT,
        )
        appearance.set("System")
        appearance.grid(row=7, column=0, sticky="ew", padx=16, pady=(0, 24))

    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=32, pady=28)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            main, text="Gestures", font=theme.font(32, heading=True), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(
            main, text="Pick a sound for each gesture. Hold the gesture for a moment to play it.",
            font=theme.font(14), text_color=theme.TEXT_MUTED, anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 20))

        # video and placeholder sit in the same spot, only one is shown
        camera_card = card(main, radius=16)
        camera_card.grid(row=2, column=0, sticky="n", padx=(0, 20))
        self.preview_image = ctk.CTkImage(Image.new("RGB", PREVIEW_SIZE), size=PREVIEW_SIZE)
        self.video = ctk.CTkLabel(camera_card, text="", image=self.preview_image)
        self.video.grid(row=0, column=0, padx=10, pady=10)
        self.placeholder = ctk.CTkLabel(
            camera_card, text="", width=PREVIEW_SIZE[0], height=PREVIEW_SIZE[1],
            corner_radius=12, fg_color=theme.SURFACE_HOVER, font=theme.font(14),
            text_color=theme.TEXT_MUTED, wraplength=PREVIEW_SIZE[0] - 40,
        )
        self.placeholder.grid(row=0, column=0, padx=10, pady=10)
        self.video.grid_remove()

        gesture_list = ctk.CTkScrollableFrame(
            main, fg_color="transparent", scrollbar_button_color=theme.BORDER,
            scrollbar_button_hover_color=theme.TEXT_MUTED,
        )
        gesture_list.grid(row=2, column=1, sticky="nsew")
        gesture_list.grid_columnconfigure(0, weight=1)

        sound_names = list_sounds()
        self.rows = []
        for i, (gesture, kind) in enumerate(ALL_GESTURES):
            row = GestureRow(
                gesture_list, gesture, kind, self.settings["mappings"].get(gesture),
                sound_names, self._on_sound_picked, self._play_sound,
            )
            row.grid(row=i, column=0, sticky="ew", pady=(0, 10), padx=(0, 8))
            self.rows.append(row)

    # actions

    def _on_camera_toggle(self, on):
        self.settings["camera_on"] = on
        self.camera_toggle.show_status()
        save_settings(self.settings)

    def _on_gestures_toggle(self, on):
        self.settings["gestures_on"] = on
        self.gestures_toggle.show_status()
        save_settings(self.settings)

    def _on_virtual_cam_toggle(self, on):
        self.settings["virtual_cam_on"] = on
        self.virtual_cam_toggle.show_status()
        self._shown_vcam_error = None
        save_settings(self.settings)

    def _on_sound_picked(self, gesture, sound):
        self.settings["mappings"][gesture] = None if sound == NO_SOUND else sound
        save_settings(self.settings)

    def _play_sound(self, sound):
        if sound != NO_SOUND:
            self.player.play(sound)

    def _reload_sounds(self):
        self.player.forget_loaded_sounds()
        names = list_sounds()
        for row in self.rows:
            row.set_sound_names(names)

    def _on_appearance(self, mode):
        ctk.set_appearance_mode(mode.lower())

    def _on_close(self):
        self.after_cancel(self._refresh_id)
        self.engine.stop()
        self.destroy()

    # live updates

    def _refresh(self):
        frame = self.engine.take_preview()
        if self.engine.message:
            self.placeholder.configure(text=self.engine.message)
            self.video.grid_remove()
            self.placeholder.grid()
        elif frame is not None:
            image = Image.fromarray(frame)
            self.preview_image.configure(light_image=image, dark_image=image)
            self.placeholder.grid_remove()
            self.video.grid()

        for row in self.rows:
            row.set_active(row.gesture in self.engine.active_gestures)

        error = self.engine.virtual_cam.error
        if error != self._shown_vcam_error:
            self._shown_vcam_error = error
            self.virtual_cam_toggle.show_status(error)

        if self.engine.last_played:
            gesture, sound = self.engine.last_played
            self.last_played_label.configure(text=f"Last played\n{sound}  ·  {gesture}")

        self._refresh_id = self.after(REFRESH_MS, self._refresh)


def run():
    ctk.set_appearance_mode("system")
    MainWindow().mainloop()
