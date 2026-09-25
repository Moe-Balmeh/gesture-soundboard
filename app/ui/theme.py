import customtkinter as ctk

# (light, dark)
BG = ("#FAF9F5", "#262624")
SIDEBAR = ("#F3F1EA", "#1F1E1D")
SURFACE = ("#FFFFFF", "#30302E")
SURFACE_HOVER = ("#F5F3EC", "#3A3A37")
BORDER = ("#E3E0D6", "#44433F")

TEXT = ("#1F1E1D", "#F5F4EF")
TEXT_MUTED = ("#6B6963", "#A6A39B")

ACCENT = ("#7446D8", "#8B5CF6")
ACCENT_HOVER = ("#6236C4", "#7C4DEA")
ACCENT_SOFT = ("#EEE7FB", "#352C4A")
ON_ACCENT = "#FFFFFF"
DANGER = ("#C0392B", "#F87171")

HEADING_FONT = "Bahnschrift SemiBold"
BODY_FONT = "Segoe UI Variable Text"


def font(size, weight="normal", heading=False):
    return ctk.CTkFont(family=HEADING_FONT if heading else BODY_FONT, size=size, weight=weight)
