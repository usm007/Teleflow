THEMES = {
    "dark": {
        "surface": "#0b1020",
        "surface_alt": "#111a2e",
        "surface_soft": "#16213a",
        "surface_elevated": "#1b2744",
        "panel": "#131d34",
        "panel_alt": "#1a2746",
        "border": "#2a3d63",
        "border_soft": "#203153",
        "text": "#e7edf9",
        "text_muted": "#9cb0d6",
        "text_faint": "#7f93b8",
        "accent": "#4f8cff",
        "accent_hover": "#6ba0ff",
        "accent_pressed": "#3d77e8",
        "success": "#2bc48a",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "row_hover": "#1d2d52",
        "row_selected": "#243861",
        "terminal_bg": "#090f1d",
        "overlay": "#050914",
        "overlay_alpha": 220,
        "scanline_alpha": 26,
        "footer_bg": "#0a1224",
        "button_text": "#ffffff",
    },
    "light": {
        "surface": "#f4f7fc",
        "surface_alt": "#eef3fb",
        "surface_soft": "#e7edf8",
        "surface_elevated": "#ffffff",
        "panel": "#ffffff",
        "panel_alt": "#f8fafe",
        "border": "#cfdbf2",
        "border_soft": "#dde6f7",
        "text": "#0f1a2f",
        "text_muted": "#4f6285",
        "text_faint": "#6f81a5",
        "accent": "#2f6ef3",
        "accent_hover": "#4b83f5",
        "accent_pressed": "#2558c6",
        "success": "#0f9f68",
        "warning": "#c97f00",
        "danger": "#cf3030",
        "row_hover": "#e8effd",
        "row_selected": "#dce8ff",
        "terminal_bg": "#f3f7ff",
        "overlay": "#0f172a",
        "overlay_alpha": 150,
        "scanline_alpha": 20,
        "footer_bg": "#edf2fb",
        "button_text": "#ffffff",
    },
}


def normalize_theme_mode(mode):
    if mode in ("dark", "light"):
        return mode
    return "dark"


def resolve_theme_mode(saved_mode, app):
    if saved_mode in ("dark", "light"):
        return saved_mode

    try:
        color_scheme = app.styleHints().colorScheme()
        if str(color_scheme).lower().endswith("light"):
            return "light"
    except Exception:
        pass
    return "dark"


def get_theme(mode):
    return THEMES[normalize_theme_mode(mode)]
