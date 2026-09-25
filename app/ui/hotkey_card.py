import customtkinter as ctk

from app.logic.hotkeys import hotkey_label, is_allowed_key, is_function_key

from . import theme

MODIFIER_KEYSYMS = {
    "Control_L": "ctrl", "Control_R": "ctrl",
    "Shift_L": "shift", "Shift_R": "shift",
    "Alt_L": "alt", "Alt_R": "alt",
}
HINT = "Turns gestures on/off from any app. Click to change."


class HotkeyCard(ctk.CTkFrame):
    def __init__(self, master, hotkey, on_change, on_recording):
        super().__init__(
            master, fg_color=theme.SURFACE, corner_radius=16, border_width=1, border_color=theme.BORDER
        )
        self.hotkey = hotkey
        self.on_change = on_change
        self.on_recording = on_recording  # tells the app to ignore the old shortcut meanwhile
        self._recording = False
        self._modifiers = set()
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text="Keyboard shortcut", font=theme.font(14, "bold"), text_color=theme.TEXT, anchor="w"
        ).grid(row=0, column=0, sticky="sw", padx=16, pady=(12, 0))
        self.hint = ctk.CTkLabel(
            self, text=HINT, font=theme.font(12), text_color=theme.TEXT_MUTED, anchor="w",
            justify="left", wraplength=260,
        )
        self.hint.grid(row=1, column=0, sticky="nw", padx=16, pady=(0, 12))

        self.key_button = ctk.CTkButton(
            self, text=hotkey_label(hotkey), command=self._start_recording, width=140, height=34,
            corner_radius=8, font=theme.font(13, "bold"), fg_color=theme.ACCENT_SOFT,
            hover_color=theme.BORDER, text_color=theme.ACCENT,
        )
        self.key_button.grid(row=0, column=1, rowspan=2, padx=16, pady=12)

    def _start_recording(self):
        if self._recording:
            return
        self._recording = True
        self._modifiers.clear()
        self.on_recording(True)
        self.key_button.configure(text="Press keys...", fg_color=theme.ACCENT, text_color=theme.ON_ACCENT)
        self._show_hint("Hold Ctrl, Alt or Shift and press a key. Esc cancels.")
        root = self.winfo_toplevel()
        root.bind("<KeyPress>", self._on_key_press)
        root.bind("<KeyRelease>", self._on_key_release)
        root.focus_force()

    def _stop_recording(self):
        self._recording = False
        root = self.winfo_toplevel()
        root.unbind("<KeyPress>")
        root.unbind("<KeyRelease>")
        self.key_button.configure(
            text=hotkey_label(self.hotkey), fg_color=theme.ACCENT_SOFT, text_color=theme.ACCENT
        )
        self.on_recording(False)

    def _on_key_press(self, event):
        if event.keysym in MODIFIER_KEYSYMS:
            self._modifiers.add(MODIFIER_KEYSYMS[event.keysym])
            return "break"
        if event.keysym == "Escape":
            self._stop_recording()
            self._show_hint(HINT)
            return "break"

        vk = event.keycode  # on windows this is the same key code pynput uses
        if not is_allowed_key(vk):
            self._show_hint("Use a letter, number or F-key.", error=True)
        elif not self._modifiers and not is_function_key(vk):
            self._show_hint("Add Ctrl, Alt or Shift (F-keys work alone).", error=True)
        else:
            self.hotkey = {"modifiers": sorted(self._modifiers), "vk": vk}
            self._stop_recording()
            self._show_hint(HINT)
            self.on_change(self.hotkey)
        return "break"

    def _on_key_release(self, event):
        self._modifiers.discard(MODIFIER_KEYSYMS.get(event.keysym))
        return "break"

    def _show_hint(self, text, error=False):
        self.hint.configure(text=text, text_color=theme.DANGER if error else theme.TEXT_MUTED)
