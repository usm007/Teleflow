def build_stylesheet(theme):
    return f"""
    QMainWindow {{ background-color: {theme['surface']}; }}
    QWidget {{
        color: {theme['text']};
        font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
        font-size: 13px;
    }}

    QFrame#TopBar {{
        background-color: {theme['surface_alt']};
        border-bottom: 1px solid {theme['border']};
    }}
    QLabel#AppTitle {{
        font-size: 18px;
        font-weight: 700;
        color: {theme['text']};
    }}
    QLabel#AppSubtitle {{
        font-size: 11px;
        color: {theme['text_faint']};
        letter-spacing: 0.4px;
    }}

    QFrame#Panel {{
        background-color: {theme['panel']};
        border: 1px solid {theme['border']};
        border-radius: 12px;
    }}
    QFrame#SectionPanel {{
        background-color: {theme['panel_alt']};
        border: 1px solid {theme['border_soft']};
        border-radius: 12px;
    }}
    QFrame#Footer {{
        background-color: {theme['footer_bg']};
        border-top: 1px solid {theme['border']};
    }}

    QLabel#GuideHeader {{
        color: {theme['text']};
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    QLabel#GuideStep {{
        color: {theme['text_muted']};
        font-size: 13px;
        line-height: 1.6;
    }}

    QLineEdit, QSpinBox, QComboBox {{
        background-color: {theme['surface_elevated']};
        border: 1px solid {theme['border']};
        border-radius: 8px;
        padding: 10px 12px;
        color: {theme['text']};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {theme['accent']};
    }}

    QPushButton {{
        background-color: {theme['accent']};
        color: {theme['button_text']};
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: {theme['accent_hover']};
    }}
    QPushButton:pressed {{
        background-color: {theme['accent_pressed']};
    }}

    QPushButton#Secondary {{
        background-color: {theme['surface_soft']};
        color: {theme['text']};
        border: 1px solid {theme['border']};
    }}
    QPushButton#Destructive {{
        background-color: {theme['danger']};
        color: #ffffff;
    }}
    QPushButton#Amber {{
        background-color: {theme['warning']};
        color: #111111;
    }}
    QPushButton#FilterBtn {{
        background-color: {theme['surface_elevated']};
        color: {theme['text_faint']};
        border: 1px solid {theme['border']};
        font-size: 11px;
    }}
    QPushButton#FilterBtn:checked {{
        background-color: {theme['row_selected']};
        color: {theme['accent']};
        border: 1px solid {theme['accent']};
    }}

    QListWidget {{
        background-color: {theme['surface_elevated']};
        border: 1px solid {theme['border']};
        border-radius: 10px;
        color: {theme['text']};
        outline: none;
    }}
    QListWidget::item {{
        padding: 11px;
        border-bottom: 1px solid {theme['border_soft']};
    }}
    QListWidget::item:selected {{
        background-color: {theme['row_selected']};
        border-left: 3px solid {theme['accent']};
        color: {theme['text']};
    }}

    QTableWidget {{
        background-color: {theme['surface_elevated']};
        border: 1px solid {theme['border_soft']};
        border-radius: 10px;
        gridline-color: transparent;
        color: {theme['text_muted']};
        selection-background-color: transparent;
        selection-color: {theme['text']};
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {theme['border_soft']};
    }}
    QTableWidget::item:hover {{
        background-color: {theme['row_hover']};
        color: {theme['text']};
    }}
    QTableWidget::item:selected {{
        background-color: {theme['row_selected']};
        color: {theme['text']};
    }}
    QTableWidget::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {theme['border']};
        border-radius: 3px;
        background: transparent;
    }}
    QTableWidget::indicator:checked {{
        background-color: {theme['accent']};
        border: 1px solid {theme['accent']};
    }}

    QTableWidget#ActiveStats {{
        background-color: {theme['surface_elevated']};
        border: 1px solid {theme['border_soft']};
        font-family: 'Consolas', monospace;
        font-size: 13px;
        font-weight: 700;
    }}
    QTableWidget#ActiveStats::item {{
        color: {theme['text']};
        border-bottom: 1px solid {theme['border_soft']};
    }}

    QHeaderView::section {{
        background-color: {theme['surface_alt']};
        color: {theme['text_faint']};
        border: none;
        border-bottom: 1px solid {theme['border']};
        padding: 10px;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 10px;
    }}

    QCheckBox {{
        color: {theme['text_muted']};
        font-weight: 600;
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {theme['border']};
        border-radius: 4px;
        background: {theme['surface_elevated']};
    }}
    QCheckBox::indicator:checked {{
        background: {theme['accent']};
        border: 1px solid {theme['accent']};
    }}

    QLabel#StatTitle {{
        color: {theme['text_faint']};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.4px;
    }}
    QLabel#StatValue {{
        color: {theme['text']};
        font-family: 'Consolas', monospace;
        font-size: 12px;
    }}
    QLabel#StatValueGreen {{
        color: {theme['success']};
        font-family: 'Consolas', monospace;
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#CountGreen {{
        color: {theme['success']};
        font-family: 'Consolas', monospace;
        font-size: 15px;
        font-weight: 800;
    }}
    QLabel#CountYellow {{
        color: {theme['warning']};
        font-family: 'Consolas', monospace;
        font-size: 15px;
        font-weight: 800;
    }}
    QLabel#MetaBadge {{
        color: {theme['text_faint']};
        font-size: 11px;
        font-weight: 700;
    }}

    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
    }}
    QScrollBar::handle:vertical {{
        background: {theme['border']};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
