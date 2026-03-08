SPACING = {
    "xxs": 4,
    "xs": 8,
    "sm": 11,
    "md": 18,
    "lg": 26,
    "xl": 34,
    "xxl": 48,
    "page_h": 32,
    "page_v": 24,
    "section": 18,
    "item": 12,
}

RADII = {
    "card": 14,
    "input": 8,
    "button": 8,
    "chip": 999,
}

TYPOGRAPHY = {
    "heading_font": "DM Sans",
    "body_font": "DM Sans",
    "title_size": 20,
    "page_title_size": 13,
    "body_size": 13,
    "meta_size": 11,
    "label_size": 9,
    "line_height": 1.55,
}

THEMES = {
    "light": {
        # Base surfaces — deep charcoal, not navy
        "surface":          "#0E0F11",
        "surface_alt":      "#131416",
        "surface_soft":     "#1A1C1F",
        "surface_elevated": "#1E2024",

        # Panels / cards
        "panel":            "#181A1D",
        "panel_alt":        "#1C1E22",

        # Inputs
        "input":            "#16181B",

        # Borders — subtle, glass-like
        "border":           "#2C2E33",
        "border_soft":      "#222428",

        # Primary — electric emerald
        "primary":          "#00D68F",
        "primary_hover":    "#00F0A0",
        "primary_pressed":  "#00B87A",

        # Accent — crisp cyan
        "accent":           "#00C2FF",
        "accent_hover":     "#33CEFF",

        # Semantic
        "success":          "#00D68F",
        "warning":          "#FFAA2C",
        "danger":           "#FF4D6A",
        "info":             "#00C2FF",

        # Text
        "text":             "#F0F2F5",
        "text_muted":       "#9DA3AD",
        "text_faint":       "#5A6070",

        # Interactive states
        "row_hover":        "#1F2125",
        "row_selected":     "#1A2B24",

        # Misc
        "terminal_bg":      "#0B0C0E",
        "overlay":          "#000000",
        "overlay_alpha":    180,
        "scanline_alpha":   0,
        "footer_bg":        "#0E0F11",
        "button_text":      "#0E0F11",
        "topbar_bg":        "#0E0F11",
        "topbar_border":    "#00D68F",
        "header_bg":        "#0E0F11",
    },
}

for mode in THEMES.values():
    mode.update(SPACING)
    mode.update(RADII)
    mode.update(TYPOGRAPHY)
    mode["accent_text"] = mode["button_text"]


def normalize_theme_mode(mode):
    return "light"


def resolve_theme_mode(saved_mode, app):
    return "light"


def get_theme(mode):
    return THEMES[normalize_theme_mode(mode)]
