import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageDraw

from . import theme

CLEAR = "#010203"  # painted see-through so the list can have round corners
ROW_HEIGHT = 30
MAX_ROWS = 9  # more than this and the list scrolls


def _arrow(color):
    # drawn big then shrunk so the lines are smooth
    image = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    ImageDraw.Draw(image).line([(12, 18), (24, 30), (36, 18)], fill=color, width=5, joint="curve")
    return image


_arrow_image = None


def arrow_image():
    global _arrow_image
    if _arrow_image is None:
        _arrow_image = ctk.CTkImage(_arrow(theme.TEXT_MUTED[0]), _arrow(theme.TEXT_MUTED[1]), size=(12, 12))
    return _arrow_image


class Dropdown(ctk.CTkFrame):
    # ctk's option menu has a jaggy arrow and opens an old windows menu, so this is our own
    def __init__(self, master, values, command, width):
        super().__init__(master, width=width, height=34, corner_radius=8, fg_color=theme.SURFACE_HOVER)
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._values = list(values)
        self._command = command
        self._value = self._values[0] if self._values else ""
        self._width = width
        self._popup = None

        self._label = ctk.CTkLabel(self, text="", font=theme.font(13), text_color=theme.TEXT, anchor="w")
        self._label.grid(row=0, column=0, sticky="ew", padx=(10, 4))
        arrow = ctk.CTkLabel(self, text="", image=arrow_image(), width=12)
        arrow.grid(row=0, column=1, padx=(0, 10))

        for widget in (self, self._label, arrow):
            widget.bind("<Button-1>", lambda e: self._toggle())
            widget.bind("<Enter>", lambda e: self.configure(fg_color=theme.BORDER))
            widget.bind("<Leave>", lambda e: self.after(20, self._unhover))
            widget.configure(cursor="hand2")

        # clicking or scrolling anywhere else in the window closes the list
        root = self.winfo_toplevel()
        root.bind("<Button-1>", self._click_elsewhere, add="+")
        root.bind("<MouseWheel>", lambda e: self._close(), add="+")
        root.bind("<Unmap>", lambda e: self._close(), add="+")  # e.g. hidden to the tray
        self._show_value()

    def get(self):
        return self._value

    def set(self, value):
        self._value = value
        self._show_value()

    def set_values(self, values):
        self._values = list(values)

    def _show_value(self):
        self._label.configure(text=self._fit(self._value, self._width - 40))

    def _fit(self, text, space):
        # cut long names with ... instead of letting them spill out
        font = theme.font(13)
        if font.measure(text) <= space:
            return text
        while text and font.measure(text + "…") > space:
            text = text[:-1]
        return text + "…"

    def _unhover(self):
        x, y = self.winfo_pointerxy()
        inside = self.winfo_rootx() <= x < self.winfo_rootx() + self.winfo_width() \
            and self.winfo_rooty() <= y < self.winfo_rooty() + self.winfo_height()
        if not inside:
            self.configure(fg_color=theme.SURFACE_HOVER)

    def _click_elsewhere(self, event):
        if not str(event.widget).startswith(str(self)):
            self._close()

    def _toggle(self):
        self._close() if self._popup else self._open()

    def _open(self):
        popup = tk.Toplevel(self, bg=CLEAR)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-transparentcolor", CLEAR)
        popup.bind("<Escape>", lambda e: self._close())

        box = ctk.CTkFrame(
            popup, fg_color=theme.SURFACE, corner_radius=10, border_width=1, border_color=theme.BORDER,
            bg_color=CLEAR,
        )
        box.pack()
        if len(self._values) > MAX_ROWS:
            rows = ctk.CTkScrollableFrame(
                box, fg_color="transparent", width=self._width - 24, height=MAX_ROWS * ROW_HEIGHT,
                scrollbar_button_color=theme.BORDER, scrollbar_button_hover_color=theme.TEXT_MUTED,
            )
        else:
            rows = ctk.CTkFrame(box, fg_color="transparent", width=self._width - 12)
        rows.pack(padx=5, pady=5)

        for value in self._values:
            picked = value == self._value
            ctk.CTkButton(
                rows, text=self._fit(value, self._width - 40), anchor="w", height=ROW_HEIGHT - 2,
                width=self._width - 24, corner_radius=6, font=theme.font(13),
                fg_color=theme.ACCENT_SOFT if picked else "transparent", hover_color=theme.SURFACE_HOVER,
                text_color=theme.ACCENT if picked else theme.TEXT,
                command=lambda v=value: self._pick(v),
            ).pack(fill="x", pady=1)

        # under the box, or above it if there's no room at the bottom of the screen
        popup.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 4
        if y + popup.winfo_reqheight() > self.winfo_screenheight() - 48:
            y = self.winfo_rooty() - popup.winfo_reqheight() - 4
        popup.geometry(f"+{x}+{y}")
        popup.focus_set()
        self._popup = popup

    def _pick(self, value):
        self._close()
        self.set(value)
        self._command(value)

    def _close(self):
        if self._popup:
            self._popup.destroy()
            self._popup = None
