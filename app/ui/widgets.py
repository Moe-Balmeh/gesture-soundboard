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
        dynamic_resizing=False,  # long file names get cut off instead of stretching the row
    )


class Switch(ctk.CTkSwitch):
    # the border follows the track color so the white knob never blends into a white card
    def __init__(self, master, command):
        super().__init__(
            master, text="", width=44, switch_width=44, switch_height=22, command=command,
            border_width=3, progress_color=theme.ACCENT, fg_color=theme.SWITCH_OFF,
            button_color=theme.ON_ACCENT, button_hover_color=theme.ON_ACCENT,
        )
        self._match_border()

    def toggle(self, event=None):
        super().toggle(event)
        self._match_border()

    def select(self, from_variable_callback=False):
        super().select(from_variable_callback)
        self._match_border()

    def deselect(self, from_variable_callback=False):
        super().deselect(from_variable_callback)
        self._match_border()

    def _match_border(self):
        self.configure(border_color=theme.ACCENT if self.get() else theme.SWITCH_OFF)


def switch(master, command):
    return Switch(master, command)


def outline_button(master, text, command, text_color=theme.TEXT):
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        height=36,
        corner_radius=8,
        font=theme.font(13),
        fg_color=theme.SIDEBAR_BUTTON,
        hover_color=theme.SURFACE_HOVER,
        border_width=1,
        border_color=theme.BORDER,
        text_color=text_color,
    )


class ToggleRow(ctk.CTkFrame):
    def __init__(self, master, title, on_text, off_text, is_on, on_change):
        super().__init__(master, fg_color="transparent")
        self.on_text, self.off_text = on_text, off_text
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text=title, font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=0, sticky="w")
        self.status = ctk.CTkLabel(self, font=theme.font(12), anchor="w", justify="left", wraplength=160)
        self.status.grid(row=1, column=0, sticky="w")

        self.switch = switch(self, lambda: on_change(self.is_on()))
        self.switch.grid(row=0, column=1, rowspan=2)
        if is_on:
            self.switch.select()
        self.show_status()

    def is_on(self):
        return bool(self.switch.get())

    def set_on(self, on):
        self.switch.select() if on else self.switch.deselect()
        self.show_status()

    def show_status(self, error=None):
        if error:
            self.status.configure(text=error, text_color=theme.DANGER)
            return
        on = self.is_on()
        self.status.configure(
            text=self.on_text if on else self.off_text,
            text_color=theme.ACCENT if on else theme.TEXT_MUTED,
        )


class GestureRow(ctk.CTkFrame):
    def __init__(self, master, gesture, sound, sound_names, enabled, on_change, on_play, on_enable):
        super().__init__(master, fg_color="transparent", corner_radius=10)
        self.gesture = gesture
        self.active = False
        self.grid_columnconfigure(1, weight=1)

        self.switch = switch(self, lambda: self._on_switch(on_enable))
        self.switch.grid(row=0, column=0, padx=(10, 10), pady=8)
        if enabled:
            self.switch.select()
        self.name = ctk.CTkLabel(self, text=gesture, font=theme.font(14, "bold"), anchor="w")
        self.name.grid(row=0, column=1, sticky="w")

        self.menu = dropdown(self, [NO_SOUND] + sound_names, lambda v: on_change(gesture, v), 160)
        self.menu.set(sound or NO_SOUND)
        self.menu.grid(row=0, column=2, padx=6)

        ctk.CTkButton(
            self, text="▶", width=34, height=34, corner_radius=8, font=theme.font(12),
            fg_color=theme.ACCENT_SOFT, hover_color=theme.BORDER, text_color=theme.ACCENT,
            command=lambda: on_play(self.menu.get()),
        ).grid(row=0, column=3, padx=(0, 10))
        self._show_enabled()

    def is_enabled(self):
        return bool(self.switch.get())

    def _on_switch(self, on_enable):
        on_enable(self.gesture, self.is_enabled())
        self._show_enabled()

    def _show_enabled(self):
        # switched off gestures get grayed out
        self.name.configure(text_color=theme.TEXT if self.is_enabled() else theme.TEXT_MUTED)

    def set_active(self, active):
        # lights up while the gesture is being seen
        if active != self.active:
            self.active = active
            self.configure(fg_color=theme.ACCENT_SOFT if active else "transparent")

    def set_sound_names(self, names):
        self.menu.configure(values=[NO_SOUND] + names)
