from pynput import keyboard

# keys are saved as windows key codes, e.g. ctrl + shift + G
DEFAULT_HOTKEY = {"modifiers": ["ctrl", "shift"], "vk": 71}

K = keyboard.Key
MODIFIER_KEYS = {
    K.ctrl: "ctrl", K.ctrl_l: "ctrl", K.ctrl_r: "ctrl",
    K.shift: "shift", K.shift_l: "shift", K.shift_r: "shift",
    K.alt: "alt", K.alt_l: "alt", K.alt_r: "alt", K.alt_gr: "alt",
}


def is_function_key(vk):
    return 112 <= vk <= 123  # F1 - F12


def is_allowed_key(vk):
    return 65 <= vk <= 90 or 48 <= vk <= 57 or is_function_key(vk)  # letters, numbers, F-keys


def hotkey_label(hotkey):
    names = [name.title() for name in ("ctrl", "alt", "shift") if name in hotkey["modifiers"]]
    vk = hotkey["vk"]
    names.append(f"F{vk - 111}" if is_function_key(vk) else chr(vk))
    return " + ".join(names)


class HotkeyListener:
    # listens to the keyboard everywhere, not just when our window is focused
    def __init__(self, settings, on_hotkey):
        self.settings = settings
        self.on_hotkey = on_hotkey
        self.paused = False  # while the user is picking a new shortcut
        self._held_modifiers = set()
        self._key_down = False
        self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)

    def start(self):
        self._listener.start()

    def stop(self):
        self._listener.stop()

    def _on_press(self, key):
        if key in MODIFIER_KEYS:
            self._held_modifiers.add(MODIFIER_KEYS[key])
            return
        hotkey = self.settings["hotkey"]
        matches = key_code(key) == hotkey["vk"] and self._held_modifiers == set(hotkey["modifiers"])
        # _key_down so holding the keys doesn't keep toggling
        if matches and not self._key_down and not self.paused:
            self._key_down = True
            self.on_hotkey()

    def _on_release(self, key):
        if key in MODIFIER_KEYS:
            self._held_modifiers.discard(MODIFIER_KEYS[key])
        elif key_code(key) == self.settings["hotkey"]["vk"]:
            self._key_down = False


def key_code(key):
    # letters come as KeyCode(vk=...), F-keys as Key.f1 etc.
    if isinstance(key, keyboard.Key):
        return key.value.vk
    return key.vk
