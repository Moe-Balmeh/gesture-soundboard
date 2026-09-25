import tkinter as tk
import webbrowser

import customtkinter as ctk

from . import theme

WIDTH = 360
CLEAR = "#010203"  # painted see-through so the popup can have round corners

DOWNLOADS = [
    ("OBS Studio", "needed for Virtual camera", "https://obsproject.com/"),
    ("VB-Audio Virtual Cable", "needed for Virtual mic, restart your PC after", "https://vb-audio.com/Cable/"),
]
STEPS = [
    "Pick a sound for each gesture on the right.",
    "Hold the gesture for a moment to play it.",
    "Use the keyboard shortcut to pause gestures from any app.",
]
CALL_STEPS = [
    'Camera: pick "OBS Virtual Camera".',
    'Mic: pick "CABLE Output", and choose your real mic under Call audio.',
    "Discord: set Noise Suppression to None or it cuts out the sounds.",
]


class HelpButton(ctk.CTkButton):
    # hover to open, the popup stays while the mouse is on it so the links can be clicked
    def __init__(self, master):
        super().__init__(
            master, text="?  Help", width=84, height=32, corner_radius=16, font=theme.font(13, "bold"),
            fg_color=theme.ACCENT_SOFT, hover_color=theme.BORDER, text_color=theme.ACCENT,
            command=self._toggle,
        )
        self._popup = None
        self._hide_id = None
        self.bind("<Enter>", lambda e: self._show(), add="+")
        self.bind("<Leave>", lambda e: self._hide_soon(), add="+")

    def _toggle(self):
        self._close() if self._popup else self._show()

    def _show(self):
        if self._hide_id:
            self.after_cancel(self._hide_id)
            self._hide_id = None
        if self._popup:
            return
        popup = tk.Toplevel(self, bg=CLEAR)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-transparentcolor", CLEAR)
        self._build(popup)
        popup.bind("<Enter>", lambda e: self._show())
        popup.bind("<Leave>", lambda e: self._hide_soon())

        # right edge lines up with the button, just under it
        popup.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() - popup.winfo_reqwidth()
        y = self.winfo_rooty() + self.winfo_height() + 6
        popup.geometry(f"+{x}+{y}")
        self._popup = popup

    def _hide_soon(self):
        # small delay so moving from the button to the popup doesn't close it
        if self._hide_id:
            self.after_cancel(self._hide_id)
        self._hide_id = self.after(250, self._hide_if_away)

    def _hide_if_away(self):
        self._hide_id = None
        x, y = self.winfo_pointerxy()
        for widget in (self, self._popup):
            if widget and widget.winfo_rootx() <= x < widget.winfo_rootx() + widget.winfo_width() \
                    and widget.winfo_rooty() <= y < widget.winfo_rooty() + widget.winfo_height():
                return
        self._close()

    def _close(self):
        if self._popup:
            self._popup.destroy()
            self._popup = None

    def _build(self, popup):
        box = ctk.CTkFrame(
            popup, fg_color=theme.SURFACE, corner_radius=14, border_width=1, border_color=theme.BORDER,
            bg_color=CLEAR,
        )
        box.pack()
        box.grid_columnconfigure(0, minsize=WIDTH)

        rows = [self._title(box, "Free apps to install first")]
        for name, why, url in DOWNLOADS:
            rows.append(self._url(box, name, url))
            rows.append(self._line(box, why, muted=True, pad=(0, 4)))
        rows.append(self._title(box, "How to use"))
        rows += [self._line(box, f"{i}.  {step}") for i, step in enumerate(STEPS, 1)]
        rows.append(self._title(box, "In Zoom / Meet / Discord"))
        rows += [self._line(box, f"•  {step}") for step in CALL_STEPS]

        for i, (widget, pady) in enumerate(rows):
            last = i == len(rows) - 1
            widget.grid(row=i, column=0, sticky="w", padx=16, pady=(pady[0], 14 if last else pady[1]))
            widget.bind("<Enter>", lambda e: self._show(), add="+")

    def _title(self, master, text):
        label = ctk.CTkLabel(master, text=text, font=theme.font(13, "bold"), text_color=theme.TEXT, anchor="w")
        return label, (12, 2)

    def _line(self, master, text, muted=False, pad=(1, 1)):
        label = ctk.CTkLabel(
            master, text=text, font=theme.font(12), anchor="w", justify="left", wraplength=WIDTH - 32,
            text_color=theme.TEXT_MUTED if muted else theme.TEXT,
        )
        return label, pad

    def _url(self, master, text, url):
        label = ctk.CTkLabel(
            master, text=f"{text}  ↗", font=ctk.CTkFont(family=theme.BODY_FONT, size=13, underline=True),
            text_color=theme.ACCENT, anchor="w", cursor="hand2",
        )
        label.bind("<Button-1>", lambda e: webbrowser.open(url))
        return label, (2, 0)
