import customtkinter as ctk

from . import theme
from .widgets import dropdown

NO_MIC = "No mic (sounds only)"
HINT = "Your voice + the sounds, sent to the virtual mic."


class SoundCard(ctk.CTkFrame):
    def __init__(self, master, mic_names, mic, mic_volume, sounds_volume, on_mic, on_volume):
        super().__init__(
            master, fg_color=theme.SURFACE, corner_radius=16, border_width=1, border_color=theme.BORDER
        )
        self.grid_columnconfigure((0, 1), weight=1, uniform="half")

        ctk.CTkLabel(
            self, text="Call audio", font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=0, sticky="sw", padx=16, pady=(12, 0))
        self.hint = ctk.CTkLabel(
            self, text=HINT, font=theme.font(12), text_color=theme.TEXT_MUTED, anchor="w",
            justify="left", wraplength=200,
        )
        self.hint.grid(row=1, column=0, sticky="nw", padx=16)

        # keep a saved mic in the list even if it's unplugged right now
        names = mic_names if not mic or mic in mic_names else mic_names + [mic]
        self.mic_menu = dropdown(
            self, [NO_MIC] + names, lambda v: on_mic(None if v == NO_MIC else v), 200
        )
        self.mic_menu.set(mic or NO_MIC)
        self.mic_menu.grid(row=0, column=1, rowspan=2, sticky="e", padx=16, pady=(12, 0))

        self._slider("Voice", mic_volume, lambda v: on_volume("mic_volume", v)).grid(
            row=2, column=0, sticky="ew", padx=(16, 8), pady=(8, 12)
        )
        self._slider("Sounds", sounds_volume, lambda v: on_volume("sounds_volume", v)).grid(
            row=2, column=1, sticky="ew", padx=(8, 16), pady=(8, 12)
        )

    def _slider(self, text, value, on_change):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=text, font=theme.font(13), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, padx=(0, 8)
        )
        percent = ctk.CTkLabel(
            row, text=f"{round(value * 100)}%", font=theme.font(12), text_color=theme.TEXT_MUTED,
            width=36, anchor="e",
        )
        percent.grid(row=0, column=2)

        def changed(v):
            percent.configure(text=f"{round(v)}%")
            on_change(v / 100)

        # goes past 100% for quiet mics
        slider = ctk.CTkSlider(
            row, from_=0, to=150, number_of_steps=30, command=changed, width=80, height=16,
            fg_color=theme.SWITCH_OFF, progress_color=theme.ACCENT, button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_HOVER,
        )
        slider.set(value * 100)
        slider.grid(row=0, column=1, sticky="ew", padx=(0, 4))
        return row

    def show_error(self, error):
        self.hint.configure(text=error or HINT, text_color=theme.DANGER if error else theme.TEXT_MUTED)
