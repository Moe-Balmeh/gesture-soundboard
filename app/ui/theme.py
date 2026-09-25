import customtkinter as ctk

# (light, dark)
BG = ("#F6F4FE", "#262624")
SIDEBAR = ("#ECE7FD", "#1F1E1D")
SURFACE = ("#FFFFFF", "#30302E")
SURFACE_HOVER = ("#F2EFFB", "#3A3A37")
BORDER = ("#E3DDF6", "#44433F")
SWITCH_OFF = ("#D5CEEC", "#44433F")
SIDEBAR_BUTTON = ("#FFFFFF", "#1F1E1D")
CHIP_TRACK = ("#DDD5F8", "#3A3A37")
CHIP_SELECTED = ("#FFFFFF", "#352C4A")

TEXT = ("#1D1A2E", "#F5F4EF")
TEXT_MUTED = ("#67628A", "#A6A39B")

ACCENT = ("#7C3AED", "#8B5CF6")
ACCENT_HOVER = ("#6D28D9", "#7C4DEA")
ACCENT_SOFT = ("#EEE8FF", "#352C4A")
ON_ACCENT = "#FFFFFF"
DANGER = ("#DC2626", "#F87171")

HEADING_FONT = "Bahnschrift SemiBold"
BODY_FONT = "Segoe UI Variable Text"


def font(size, weight="normal", heading=False):
    return ctk.CTkFont(family=HEADING_FONT if heading else BODY_FONT, size=size, weight=weight)
