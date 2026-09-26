import customtkinter as ctk

from app.paths import HEADING_FONT_FILE

# (light, dark), light uses warm grays so it's not too bright
BG = ("#ECEAE4", "#262624")
SIDEBAR = ("#E2DFD7", "#1F1E1D")
SURFACE = ("#F6F5F1", "#30302E")
SURFACE_HOVER = ("#E9E6DF", "#3A3A37")
BORDER = ("#D5D1C7", "#44433F")
SWITCH_OFF = ("#B8B2A5", "#4A4945")
SIDEBAR_BUTTON = ("#F6F5F1", "#1F1E1D")
CHIP_TRACK = ("#D6D2C8", "#3A3A37")
CHIP_SELECTED = ("#F6F5F1", "#352C4A")

TEXT = ("#2A2825", "#F5F4EF")
TEXT_MUTED = ("#6E6A62", "#A6A39B")

ACCENT = ("#6A4FD3", "#8B5CF6")
ACCENT_HOVER = ("#5A40BF", "#7C4DEA")
ACCENT_SOFT = ("#E3DDF3", "#352C4A")
ON_ACCENT = "#FFFFFF"
DANGER = ("#C43D32", "#F87171")

# sora ships with the app so it looks the same on every pc (free font, see assets/fonts/OFL.txt)
ctk.FontManager.load_font(str(HEADING_FONT_FILE))
HEADING_FONT = "Sora SemiBold"
BODY_FONT = "Segoe UI Variable Text"


def font(size, weight="normal", heading=False):
    return ctk.CTkFont(family=HEADING_FONT if heading else BODY_FONT, size=size, weight=weight)
