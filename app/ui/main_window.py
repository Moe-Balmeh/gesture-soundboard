import os
import queue

import customtkinter as ctk
from PIL import Image

from app.audio.sound_player import SoundPlayer, list_sounds
from app.audio.virtual_mic import list_mics
from app.detection.gestures import FACE_EXPRESSIONS, HAND_GESTURES
from app.logic.engine import PREVIEW_SIZE, Engine
from app.logic.hotkeys import HotkeyListener
from app.logic.single_instance import listen_for_show
from app.paths import SOUNDS_DIR
from app.settings.settings import load_settings, save_settings

from . import theme
from .help_button import HelpButton
from .hotkey_card import HotkeyCard
from .sound_card import SoundCard
from .tray import Tray
from .widgets import NO_SOUND, GestureRow, ToggleRow, card, outline_button

REFRESH_MS = 33  # ~30 fps


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=theme.BG)
        self.title("Gesture Soundboard")
        self.geometry("1280x720")
        self.minsize(1200, 700)

        self.settings = load_settings()
        self.player = SoundPlayer()
        mic = self.player.virtual_mic
        mic.mic_name = self.settings["mic_device"]
        mic.mic_volume = self.settings["mic_volume"]
        mic.sounds_volume = self.settings["sounds_volume"]
        self.engine = Engine(self.settings, self.player)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main_area()
        self._update_virtual_mic()

        # the tray and the hotkey run on their own threads, they send actions here
        self.actions = queue.Queue()
        self.tray = Tray(self.settings, self.actions.put)
        self.hotkeys = HotkeyListener(self.settings, lambda: self.actions.put(("hotkey",)))
        self._told_about_tray = False

        listen_for_show(lambda: self.actions.put(("show",)))
        self.engine.start()
        self.tray.start()
        self.hotkeys.start()
        self.protocol("WM_DELETE_WINDOW", self._hide_to_tray)
        self._refresh_id = self.after(REFRESH_MS, self._refresh)

    # layout

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=theme.SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(4, weight=1)

        title = ctk.CTkFrame(sidebar, fg_color="transparent")
        title.grid(row=0, column=0, sticky="w", padx=24, pady=(28, 4))
        ctk.CTkLabel(
            title, text="Gesture", font=theme.font(26, heading=True), text_color=theme.TEXT, anchor="w", height=30
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            title, text="Soundboard", font=theme.font(26, heading=True), text_color=theme.ACCENT, anchor="w", height=30
        ).grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(
            sidebar, text="Meme sounds on cue for\nyour calls and streams.", justify="left",
            anchor="w", font=theme.font(13), text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=24)

        controls = card(sidebar)
        controls.grid(row=2, column=0, sticky="ew", padx=16, pady=(20, 0))
        controls.grid_columnconfigure(0, weight=1)
        self.toggles = {}
        toggle_rows = [
            ("camera_on", "Camera", "On · live", "Off · free for other apps"),
            ("gestures_on", "Gestures", "On · listening", "Off · paused"),
            ("virtual_cam_on", "Virtual camera", "On · pick \"OBS Virtual Camera\" in Zoom/Meet", "Off"),
            ("virtual_mic_on", "Virtual mic", "On · pick \"CABLE Output\" in Zoom/Meet", "Off"),
        ]
        for i, (key, title, on_text, off_text) in enumerate(toggle_rows):
            if i > 0:
                ctk.CTkFrame(controls, height=1, fg_color=theme.BORDER).grid(
                    row=i * 2 - 1, column=0, sticky="ew", padx=16
                )
            row = ToggleRow(
                controls, title, on_text, off_text, self.settings[key],
                lambda on, key=key: self._set_toggle(key, on),
            )
            first, last = i == 0, i == len(toggle_rows) - 1
            row.grid(row=i * 2, column=0, sticky="ew", padx=(16, 10), pady=(12 if first else 7, 12 if last else 7))
            self.toggles[key] = row
        self._shown_vcam_error = None

        self.last_played_label = ctk.CTkLabel(
            sidebar, text="", justify="left", anchor="w", wraplength=220,
            font=theme.font(13), text_color=theme.TEXT_MUTED,
        )
        self.last_played_label.grid(row=3, column=0, sticky="w", padx=24, pady=(12, 8))

        outline_button(sidebar, "Open sounds folder", lambda: os.startfile(SOUNDS_DIR)).grid(
            row=5, column=0, sticky="ew", padx=16, pady=(0, 8)
        )
        outline_button(sidebar, "Reload sounds", self._reload_sounds).grid(
            row=6, column=0, sticky="ew", padx=16, pady=(0, 16)
        )
        appearance = ctk.CTkSegmentedButton(
            sidebar, values=["System", "Light", "Dark"], command=self._on_appearance,
            font=theme.font(12), height=30, corner_radius=8,
            fg_color=theme.CHIP_TRACK, unselected_color=theme.CHIP_TRACK,
            unselected_hover_color=theme.SURFACE_HOVER, selected_color=theme.CHIP_SELECTED,
            selected_hover_color=theme.CHIP_SELECTED, text_color=theme.TEXT,
        )
        appearance.set("System")
        appearance.grid(row=7, column=0, sticky="ew", padx=16, pady=(0, 16))
        # the X button only hides to the tray, this one really closes
        outline_button(sidebar, "Quit app", self._quit, text_color=theme.DANGER).grid(
            row=8, column=0, sticky="ew", padx=16, pady=(0, 16)
        )

    def _build_main_area(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=32, pady=28)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            main, text="Gestures", font=theme.font(32, heading=True), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        HelpButton(main).grid(row=0, column=1, sticky="e", padx=(0, 8))
        ctk.CTkLabel(
            main, text="Pick a sound for each gesture. Hold the gesture for a moment to play it.",
            font=theme.font(14), text_color=theme.TEXT_MUTED, anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 20))

        # video and placeholder sit in the same spot, only one is shown
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.grid(row=2, column=0, sticky="n", padx=(0, 20))
        camera_card = card(left, radius=16)
        camera_card.grid(row=0, column=0, sticky="ew")
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

        HotkeyCard(left, self.settings["hotkey"], self._on_hotkey_changed, self._on_hotkey_recording).grid(
            row=1, column=0, sticky="ew", pady=(16, 0)
        )
        self.sound_card = SoundCard(
            left, list_mics(), self.settings["mic_device"], self.settings["mic_volume"],
            self.settings["sounds_volume"], self._on_mic_picked, self._on_volume,
        )
        self.sound_card.grid(row=2, column=0, sticky="ew", pady=(16, 0))

        gesture_list = ctk.CTkScrollableFrame(
            main, fg_color="transparent", scrollbar_button_color=theme.BORDER,
            scrollbar_button_hover_color=theme.TEXT_MUTED,
        )
        gesture_list.grid(row=2, column=1, sticky="nsew")
        gesture_list.grid_columnconfigure(0, weight=1)

        sound_names = list_sounds()
        enabled = self.settings["enabled_gestures"]
        self.rows = []
        groups = [("Hand gestures", list(HAND_GESTURES.values())), ("Face expressions", list(FACE_EXPRESSIONS))]
        for i, (title, gestures) in enumerate(groups):
            group = card(gesture_list, radius=16)
            group.grid(row=i, column=0, sticky="ew", pady=(0, 16), padx=(0, 8))
            group.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                group, text=title, font=theme.font(16, heading=True), text_color=theme.TEXT, anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

            for j, gesture in enumerate(gestures):
                if j > 0:
                    ctk.CTkFrame(group, height=1, fg_color=theme.BORDER).grid(
                        row=j * 2, column=0, sticky="ew", padx=16
                    )
                row = GestureRow(
                    group, gesture, self.settings["mappings"].get(gesture), sound_names,
                    enabled.get(gesture, True), self._on_sound_picked, self._play_sound, self._on_gesture_enabled,
                )
                last = j == len(gestures) - 1
                row.grid(row=j * 2 + 1, column=0, sticky="ew", padx=6, pady=(2, 8 if last else 2))
                self.rows.append(row)

    # actions

    def _set_toggle(self, key, on):
        # same path for the sidebar switches and the tray menu
        self.settings[key] = on
        self.toggles[key].set_on(on)
        if key == "virtual_cam_on":
            self._shown_vcam_error = None
        elif key == "virtual_mic_on":
            self._update_virtual_mic()
        save_settings(self.settings)
        self.tray.refresh()

    def _update_virtual_mic(self):
        self.player.set_virtual_mic(self.settings["virtual_mic_on"])
        self.toggles["virtual_mic_on"].show_status(self.player.virtual_mic.error)
        self.sound_card.show_error(self.player.virtual_mic.mic_error)

    def _on_mic_picked(self, name):
        self.settings["mic_device"] = name
        self.player.virtual_mic.set_mic(name)
        self.sound_card.show_error(self.player.virtual_mic.mic_error)
        save_settings(self.settings)

    def _on_volume(self, key, value):
        self.settings[key] = value
        setattr(self.player.virtual_mic, key, value)
        save_settings(self.settings)

    def _on_hotkey_changed(self, hotkey):
        self.settings["hotkey"] = hotkey
        save_settings(self.settings)

    def _on_hotkey_recording(self, recording):
        self.hotkeys.paused = recording

    def _on_sound_picked(self, gesture, sound):
        self.settings["mappings"][gesture] = None if sound == NO_SOUND else sound
        save_settings(self.settings)

    def _on_gesture_enabled(self, gesture, on):
        self.settings["enabled_gestures"][gesture] = on
        save_settings(self.settings)

    def _play_sound(self, sound):
        if sound != NO_SOUND:
            self.player.play(sound, to_mic=False)  # previews only go to your speakers

    def _reload_sounds(self):
        self.player.forget_loaded_sounds()
        names = list_sounds()
        for row in self.rows:
            row.set_sound_names(names)

    def _on_appearance(self, mode):
        ctk.set_appearance_mode(mode.lower())

    def _hide_to_tray(self):
        self.withdraw()
        if not self._told_about_tray:
            self._told_about_tray = True
            self.tray.notify("Still running in the tray. Right-click the icon to quit.")

    def _show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit(self):
        self.after_cancel(self._refresh_id)
        self.tray.stop()
        self.hotkeys.stop()
        self.engine.stop()
        self.player.close()
        self.destroy()

    def _handle_actions(self):
        while not self.actions.empty():
            action, *args = self.actions.get()
            if action == "hotkey":
                on = not self.settings["gestures_on"]
                self._set_toggle("gestures_on", on)
                self.player.beep(rising=on)
            elif action == "show":
                self._show()
            elif action == "toggle":
                key = args[0]
                self._set_toggle(key, not self.settings[key])
            elif action == "quit":
                self._quit()
                return True
        return False

    # live updates

    def _refresh(self):
        if self._handle_actions():
            return  # app is closing

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
            self.toggles["virtual_cam_on"].show_status(error)

        if self.engine.last_played:
            gesture, sound = self.engine.last_played
            self.last_played_label.configure(text=f"Last played\n{sound}  ·  {gesture}")

        self._refresh_id = self.after(REFRESH_MS, self._refresh)


def run():
    ctk.set_appearance_mode("system")
    MainWindow().mainloop()
