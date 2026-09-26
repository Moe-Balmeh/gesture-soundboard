import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter

from . import theme
from .dropdown import Dropdown

NO_SOUND = "No sound"


def card(master, radius=12):
    return ctk.CTkFrame(
        master, fg_color=theme.SURFACE, corner_radius=radius, border_width=1, border_color=theme.BORDER
    )


def dropdown(master, values, command, width):
    return Dropdown(master, values, command, width)


SWITCH_SIZE = (44, 24)


def _switch_image(on, mode):
    # drawn 4x bigger then shrunk so the edges come out smooth
    scale = 4
    w, h = SWITCH_SIZE[0] * scale, SWITCH_SIZE[1] * scale
    track = (theme.ACCENT if on else theme.SWITCH_OFF)[mode]
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=track)

    pad = 3 * scale
    size = h - 2 * pad
    x = w - pad - size if on else pad
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((x - scale, pad - scale, x + size + scale, pad + size + scale), fill=(0, 0, 0, 50))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(scale)))  # soft even shadow all around
    draw.ellipse((x, pad, x + size, pad + size), fill=theme.ON_ACCENT)
    return image.resize((SWITCH_SIZE[0] * 2, SWITCH_SIZE[1] * 2), Image.LANCZOS)


_switch_images = {}


def switch_image(on):
    if on not in _switch_images:
        _switch_images[on] = ctk.CTkImage(_switch_image(on, 0), _switch_image(on, 1), size=SWITCH_SIZE)
    return _switch_images[on]


class Switch(ctk.CTkLabel):
    # ctk's own switch has a seam around the knob, this one is just two pictures
    def __init__(self, master, command):
        self._is_on = False
        self._on_click = command
        super().__init__(master, text="", image=switch_image(False), cursor="hand2")
        self.bind("<Button-1>", self.toggle)

    def get(self):
        return int(self._is_on)

    def toggle(self, event=None):
        self._set(not self._is_on)
        self._on_click()

    def select(self):
        self._set(True)

    def deselect(self):
        self._set(False)

    def _set(self, on):
        self._is_on = on
        self.configure(image=switch_image(on))


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
        self.menu.set_values([NO_SOUND] + names)
