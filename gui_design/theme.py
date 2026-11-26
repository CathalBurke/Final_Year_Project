"""Colours and stylesheet loading for the Vision Inspection app."""
import os

#COLOURS - ISA-101 GREYS, GREEN AND RED ONLY FOR PASS AND FAIL
PALETTE = {
    "ground": "#DDE1E4",
    "panel": "#F1F3F4",
    "border": "#B9BFC5",
    "header": "#2E353B",
    "header_hover": "#3A4148",
    "header_text": "#F2F4F5",
    "header_muted": "#C3CAD0",
    "text": "#1E2327",
    "text_disabled": "#8A939B",
    "button": "#FFFFFF",
    "button_border": "#8A939B",
    "button_hover": "#EEF0F2",
    "button_pressed": "#D5D9DD",
    "hover": "#E4E7EA",
    "track": "#D5D9DD",
    "muted_fill": "#5B646C",
    "feed": "#1C2124",
    "status": "#C9CED3",
    "pass": "#1E7A3C",
    "fail": "#B42318",
    "header_dark": "#1F2529",
    "section": "#5F6870",
}

def load_style():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.qss")
    with open(path, encoding="utf-8") as f:
        qss = f.read()
    for key in sorted(PALETTE, key=len, reverse=True):    # longest names first
        qss = qss.replace("@" + key, PALETTE[key])
    return qss