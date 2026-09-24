import customtkinter as ctk

from . import theme

NO_SOUND = "No sound"


def card(master, radius=12):
    return ctk.CTkFrame(
        master, fg_color=theme.SURFACE, corner_radius=radius, border_width=1, border_color=theme.BORDER
    )


def dropdown(master, values, command, width):
    return ctk.CTkOptionMenu(
        master,
        values=values,
        command=command,
        width=width,
        height=34,
        corner_radius=8,
        font=theme.font(13),
        dropdown_font=theme.font(13),
        fg_color=theme.SURFACE_HOVER,
        button_color=theme.SURFACE_HOVER,
        button_hover_color=theme.BORDER,
        text_color=theme.TEXT,
        dropdown_fg_color=theme.SURFACE,
        dropdown_hover_color=theme.ACCENT_SOFT,
        dropdown_text_color=theme.TEXT,
    )


def outline_button(master, text, command):
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        height=36,
        corner_radius=8,
        font=theme.font(13),
        fg_color="transparent",
        hover_color=theme.SURFACE_HOVER,
        border_width=1,
        border_color=theme.BORDER,
        text_color=theme.TEXT,
    )


class ToggleRow(ctk.CTkFrame):
    def __init__(self, master, title, on_text, off_text, is_on, on_change):
        super().__init__(master, fg_color="transparent")
        self.on_text, self.off_text = on_text, off_text
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text=title, font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        self.status = ctk.CTkLabel(self, font=theme.font(12), anchor="w")
        self.status.grid(row=1, column=0, sticky="w")

        self.switch = ctk.CTkSwitch(
            self, text="", width=44, switch_width=44, switch_height=22,
            command=lambda: on_change(self.is_on()),
            border_width=3, border_color=theme.BORDER,  # so the knob shows on white
            progress_color=theme.ACCENT, fg_color=theme.BORDER,
            button_color=theme.ON_ACCENT, button_hover_color=theme.ON_ACCENT,
        )
        self.switch.grid(row=0, column=1, rowspan=2)
        if is_on:
            self.switch.select()
        self.show_status()

    def is_on(self):
        return bool(self.switch.get())

    def show_status(self):
        on = self.is_on()
        self.status.configure(
            text=self.on_text if on else self.off_text,
            text_color=theme.ACCENT if on else theme.TEXT_MUTED,
        )


class GestureRow(ctk.CTkFrame):
    def __init__(self, master, gesture, kind, sound, sound_names, on_change, on_play):
        super().__init__(
            master, fg_color=theme.SURFACE, corner_radius=12, border_width=1, border_color=theme.BORDER
        )
        self.gesture = gesture
        self.active = False
        self.grid_columnconfigure(1, weight=1)

        self.dot = ctk.CTkLabel(self, text="●", width=14, font=theme.font(15), text_color=theme.BORDER)
        self.dot.grid(row=0, column=0, rowspan=2, padx=(16, 8))
        ctk.CTkLabel(
            self, text=gesture, font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=1, sticky="sw", pady=(10, 0))
        ctk.CTkLabel(
            self, text=kind, font=theme.font(12), text_color=theme.TEXT_MUTED, anchor="w"
        ).grid(row=1, column=1, sticky="nw", pady=(0, 10))

        self.menu = dropdown(self, [NO_SOUND] + sound_names, lambda v: on_change(gesture, v), 170)
        self.menu.set(sound or NO_SOUND)
        self.menu.grid(row=0, column=2, rowspan=2, padx=6)

        ctk.CTkButton(
            self, text="▶", width=34, height=34, corner_radius=8, font=theme.font(12),
            fg_color=theme.ACCENT_SOFT, hover_color=theme.BORDER, text_color=theme.ACCENT,
            command=lambda: on_play(self.menu.get()),
        ).grid(row=0, column=3, rowspan=2, padx=(0, 14))

    def set_active(self, active):
        if active != self.active:
            self.active = active
            color = theme.ACCENT if active else theme.BORDER
            self.dot.configure(text_color=color)
            self.configure(border_color=color)

    def set_sound_names(self, names):
        self.menu.configure(values=[NO_SOUND] + names)
