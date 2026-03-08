def build_stylesheet(theme):
    return f"""
    /* ═══════════════════════════════════════════════════════
       GLOBAL BASE
    ═══════════════════════════════════════════════════════ */
    QMainWindow {{
        background-color: {theme['surface']};
    }}
    QWidget {{
        color: {theme['text']};
        font-family: '{theme['body_font']}', 'Segoe UI', sans-serif;
        font-size: {theme['body_size']}px;
        background: transparent;
    }}

    /* ═══════════════════════════════════════════════════════
       TOP BAR
    ═══════════════════════════════════════════════════════ */
    QFrame#TopBar {{
        background-color: {theme['surface']};
        border: none;
        border-bottom: 1px solid {theme['border']};
    }}
    QLabel#AppMono {{
        min-width: 32px;  max-width: 32px;
        min-height: 32px; max-height: 32px;
        border-radius: 8px;
        background-color: {theme['primary']};
        color: {theme['button_text']};
        font-size: 11px;
        font-weight: 800;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
        qproperty-alignment: 'AlignCenter';
    }}
    QLabel#AppTitle {{
        font-size: 30px;
        font-weight: 700;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
        color: {theme['text']};
        letter-spacing: 0.8px;
    }}
    QLabel#AppSubtitle {{
        font-size: 9px;
        color: {theme['text_faint']};
        letter-spacing: 2px;
        font-weight: 600;
    }}
    QLabel#StepIndicator {{
        color: {theme['primary']};
        font-size: {theme['meta_size']}px;
        font-weight: 600;
        background-color: transparent;
        border: 1px solid {theme['primary']};
        border-radius: {theme['button']}px;
        min-width: 138px;
        max-width: 138px;
        min-height: 34px;
        max-height: 34px;
        qproperty-alignment: 'AlignCenter';
        letter-spacing: 0.3px;
    }}

    /* ═══════════════════════════════════════════════════════
       PAGE TYPOGRAPHY
    ═══════════════════════════════════════════════════════ */
    QLabel#PageTitle {{
        color: {theme['text']};
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
        font-size: {theme['page_title_size']}px;
        font-weight: 700;
        letter-spacing: 0.6px;
    }}
    QLabel#PageSubtitle {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-weight: 500;
    }}
    QLabel#SectionLabel {{
        color: {theme['primary']};
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 2px;
    }}
    QFrame#SectionRule {{
        border: none;
        background-color: {theme['border']};
    }}
    QLabel#StreamPrefix {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-weight: 500;
    }}

    /* ═══════════════════════════════════════════════════════
       LOGIN PAGE — GUIDE PANEL
    ═══════════════════════════════════════════════════════ */
    QFrame#GuidePanel {{
        background-color: {theme['surface_alt']};
        border: 1px solid {theme['border']};
        border-radius: {theme['card']}px;
    }}
    QFrame#GuideStepCard {{
        background-color: {theme['surface_soft']};
        border: 1px solid {theme['border_soft']};
        border-radius: 10px;
    }}
    QLabel#GuideStepIndex {{
        color: {theme['primary']};
        background: transparent;
        border: 1.5px solid {theme['primary']};
        border-radius: 10px;
        font-size: 10px;
        font-weight: 800;
        min-width: 20px; max-width: 20px;
        min-height: 20px; max-height: 20px;
        qproperty-alignment: 'AlignCenter';
    }}
    QLabel#GuideStepBody {{
        color: {theme['text_muted']};
        font-size: {theme['body_size']}px;
    }}

    /* ═══════════════════════════════════════════════════════
       LOGIN PAGE — SIGN IN CARD
    ═══════════════════════════════════════════════════════ */
    QFrame#SignInCard {{
        background-color: {theme['panel']};
        border: 1px solid {theme['border']};
        border-top: 2px solid {theme['primary']};
        border-radius: {theme['card']}px;
    }}
    QLabel#FieldLabel {{
        color: {theme['text_faint']};
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.6px;
    }}
    QFrame#LoginDivider {{
        background-color: {theme['border']};
        border: none;
    }}

    /* ═══════════════════════════════════════════════════════
       PANELS / CARDS
    ═══════════════════════════════════════════════════════ */
    QFrame#Panel {{
        background-color: {theme['panel']};
        border: none;
        border-radius: {theme['card']}px;
    }}
    QFrame#SectionPanel {{
        background-color: {theme['panel']};
        border: none;
        border-radius: {theme['card']}px;
    }}
    QFrame#StatCardPrimary {{
        background-color: {theme['panel_alt']};
        border: none;
        border-radius: {theme['card']}px;
    }}
    QFrame#StatCardCompact {{
        background-color: {theme['surface_elevated']};
        border: none;
        border-radius: {theme['card']}px;
    }}
    QFrame#StatCard {{
        background-color: {theme['surface_elevated']};
        border: none;
        border-radius: {theme['card']}px;
    }}

    /* ═══════════════════════════════════════════════════════
       BUTTONS
    ═══════════════════════════════════════════════════════ */
    QPushButton {{
        min-height: 34px;
        padding: 0 {theme['md']}px;
        border-radius: {theme['button']}px;
        border: none;
        background-color: {theme['primary']};
        color: {theme['button_text']};
        font-size: {theme['meta_size']}px;
        font-weight: 700;
        font-family: '{theme['body_font']}', 'Segoe UI', sans-serif;
    }}
    QPushButton:hover {{
        background-color: {theme['primary_hover']};
    }}
    QPushButton:pressed {{
        background-color: {theme['primary_pressed']};
    }}
    QPushButton#PrimaryWide {{
        min-height: 38px;
        border-radius: {theme['button']}px;
        font-size: {theme['body_size']}px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }}
    QPushButton#Secondary {{
        background-color: {theme['surface_soft']};
        color: {theme['text_muted']};
        border: 1px solid {theme['border']};
        border-radius: {theme['button']}px;
    }}
    QPushButton#Secondary:hover {{
        background-color: {theme['surface_elevated']};
        color: {theme['text']};
        border-color: {theme['text_faint']};
    }}
    QPushButton#GhostBtn {{
        background: transparent;
        color: {theme['text_faint']};
        border: 1px solid {theme['border']};
        border-radius: {theme['button']}px;
        font-size: {theme['meta_size']}px;
        font-weight: 600;
    }}
    QPushButton#GhostBtn:hover {{
        color: {theme['text_muted']};
        border-color: {theme['text_faint']};
        background-color: {theme['surface_soft']};
    }}
    QPushButton#Destructive {{
        background-color: {theme['danger']};
        color: #ffffff;
        border-radius: {theme['button']}px;
        border: none;
    }}
    QPushButton#Destructive:hover {{
        background-color: #FF6680;
    }}
    QPushButton#Amber {{
        background-color: {theme['warning']};
        color: {theme['surface']};
        border-radius: {theme['button']}px;
        border: none;
        font-weight: 700;
    }}
    QPushButton#Amber:hover {{
        background-color: #FFB840;
    }}
    QPushButton#FilterBtn {{
        min-height: 30px;
        padding: 0 13px;
        border-radius: {theme['chip']}px;
        border: 1px solid {theme['border']};
        background-color: transparent;
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-weight: 600;
    }}
    QPushButton#FilterBtn:hover {{
        background-color: {theme['surface_soft']};
        color: {theme['text_muted']};
    }}
    QPushButton#FilterBtn:checked {{
        background-color: {theme['primary']};
        color: {theme['button_text']};
        border: 1px solid {theme['primary']};
    }}
    QFrame#SortSegment {{
        background-color: {theme['surface_soft']};
        border: 1px solid {theme['border']};
        border-radius: {theme['chip']}px;
    }}
    QPushButton#SortBtn {{
        min-height: 28px;
        padding: 0 {theme['sm']}px;
        border-radius: {theme['chip']}px;
        border: 1px solid transparent;
        background: transparent;
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-weight: 600;
    }}
    QPushButton#SortBtn:hover {{
        color: {theme['text_muted']};
    }}
    QPushButton#SortBtn:checked {{
        background-color: {theme['primary']};
        color: {theme['button_text']};
        border: 1px solid transparent;
    }}
    QPushButton:disabled {{
        opacity: 0.38;
    }}

    /* ═══════════════════════════════════════════════════════
       INPUTS
    ═══════════════════════════════════════════════════════ */
    QLineEdit, QSpinBox, QComboBox {{
        min-height: 34px;
        padding: 0 {theme['sm']}px;
        border: 1px solid {theme['border']};
        border-radius: {theme['input']}px;
        background-color: {theme['input']};
        color: {theme['text']};
        selection-background-color: {theme['primary']};
        selection-color: {theme['button_text']};
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {theme['primary']};
        background-color: {theme['surface_soft']};
    }}
    QLineEdit#SearchInput {{
        min-height: 32px;
        border-radius: {theme['chip']}px;
        padding-left: 14px;
        background-color: {theme['surface_soft']};
        border: 1px solid {theme['border_soft']};
        color: {theme['text_muted']};
    }}
    QLineEdit#SearchInput:focus {{
        border: 1px solid {theme['primary']};
        color: {theme['text']};
    }}
    QLineEdit#PathInput {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        background-color: {theme['surface_soft']};
        border-color: {theme['border_soft']};
    }}

    QSpinBox {{
        padding-right: 8px;
        background-color: {theme['input']};
        color: {theme['text']};
        border: 1px solid {theme['border']};
        border-radius: {theme['input']}px;
    }}
    QSpinBox:focus {{
        border: 1px solid {theme['primary']};
        background-color: {theme['surface_soft']};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        width: 0; border: none; background: transparent;
    }}
    QSpinBox::up-arrow, QSpinBox::down-arrow {{
        image: none; width: 0; height: 0;
    }}
    QComboBox::drop-down {{
        width: 24px;
        subcontrol-origin: padding;
        subcontrol-position: top right;
        border-left: 1px solid {theme['border']};
        background: transparent;
        border-top-right-radius: {theme['input']}px;
        border-bottom-right-radius: {theme['input']}px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid {theme['text_faint']};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {theme['surface_elevated']};
        color: {theme['text']};
        border: 1px solid {theme['border']};
        outline: none;
        selection-background-color: {theme['primary']};
        selection-color: {theme['button_text']};
        padding: 2px;
    }}
    QComboBox QAbstractItemView::item {{
        min-height: 26px;
        padding: 4px 8px;
        color: {theme['text']};
        background: transparent;
    }}
    QComboBox QAbstractItemView::item:hover {{
        background-color: {theme['surface_soft']};
        color: {theme['text']};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {theme['primary']};
        color: {theme['button_text']};
    }}
    QPushButton#StepperBtn {{
        min-height: 30px;
        min-width: 30px;
        max-height: 30px;
        max-width: 30px;
        padding: 0;
        border: 1px solid {theme['border']};
        border-radius: {theme['button']}px;
        background-color: {theme['surface_soft']};
        color: {theme['text']};
        font-size: 15px;
        font-weight: 700;
    }}
    QPushButton#StepperBtn:hover {{
        border-color: {theme['primary']};
        color: {theme['primary']};
    }}
    QLabel#StepperValue {{
        min-height: 30px;
        max-height: 30px;
        border: 1px solid {theme['border']};
        border-radius: {theme['button']}px;
        background-color: {theme['input']};
        color: {theme['text']};
        font-size: {theme['meta_size']}px;
        font-weight: 700;
        qproperty-alignment: 'AlignCenter';
    }}

    /* ═══════════════════════════════════════════════════════
       CHECKBOX
    ═══════════════════════════════════════════════════════ */
    QCheckBox {{
        color: {theme['text_muted']};
        spacing: {theme['xs']}px;
        font-size: {theme['meta_size']}px;
    }}
    QCheckBox::indicator {{
        width: 15px; height: 15px;
        border: 1.5px solid {theme['border']};
        border-radius: 4px;
        background: transparent;
    }}
    QCheckBox::indicator:checked {{
        background-color: {theme['primary']};
        border: 1.5px solid {theme['primary']};
    }}
    QCheckBox::indicator:hover {{
        border-color: {theme['primary']};
    }}

    /* ═══════════════════════════════════════════════════════
       CHAT LIST
    ═══════════════════════════════════════════════════════ */
    QListWidget#ChatList {{
        background: transparent;
        border: none;
        outline: none;
        padding: 8px 0;
    }}
    QListWidget#ChatList::item {{
        padding: 0;
        margin: 0;
        border: none;
        border-bottom: 1px solid {theme['border']};
        background: transparent;
    }}
    QListWidget#ChatList::item:selected {{
        background: transparent;
    }}
    QLineEdit::placeholder {{
        color: {theme['text_faint']};
    }}
    QFrame#ChatRow {{
        background: transparent;
        border: none;
        border-left: 3px solid transparent;
    }}
    QFrame#ChatRow:hover {{
        background-color: {theme['row_hover']};
        border-left: 3px solid {theme['primary']};
    }}

    QLabel#AvatarBubbleChannel,
    QLabel#AvatarBubbleGroup,
    QLabel#AvatarBubbleDM {{
        min-width: 38px; max-width: 38px;
        min-height: 38px; max-height: 38px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 800;
        qproperty-alignment: 'AlignCenter';
    }}
    QLabel#AvatarBubbleChannel {{
        background-color: #0D2535;
        color: {theme['accent']};
        border: 1px solid rgba(0,194,255,0.2);
    }}
    QLabel#AvatarBubbleGroup {{
        background-color: #0D2519;
        color: {theme['primary']};
        border: 1px solid rgba(0,214,143,0.2);
    }}
    QLabel#AvatarBubbleDM {{
        background-color: {theme['surface_soft']};
        color: {theme['text_faint']};
        border: 1px solid {theme['border_soft']};
    }}
    QLabel#ChatTitle {{
        color: {theme['text']};
        font-size: {theme['body_size']}px;
        font-weight: 600;
    }}
    QLabel#ChatMeta {{
        color: {theme['text_faint']};
        font-size: 10px;
        font-weight: 400;
    }}
    QLabel#TypeBadgeChannel {{
        background-color: rgba(0,194,255,0.10);
        color: {theme['accent']};
        border: 1px solid rgba(0,194,255,0.25);
        border-radius: 5px;
        padding: 2px 7px;
        font-size: 9px;
        font-weight: 700;
    }}
    QLabel#TypeBadgeGroup {{
        background-color: rgba(0,214,143,0.10);
        color: {theme['primary']};
        border: 1px solid rgba(0,214,143,0.25);
        border-radius: 5px;
        padding: 2px 7px;
        font-size: 9px;
        font-weight: 700;
    }}
    QLabel#TypeBadgeDM {{
        background-color: rgba(255,170,44,0.10);
        color: {theme['warning']};
        border: 1px solid rgba(255,170,44,0.25);
        border-radius: 5px;
        padding: 2px 7px;
        font-size: 9px;
        font-weight: 700;
    }}

    /* ═══════════════════════════════════════════════════════
       VIDEO TABLE
    ═══════════════════════════════════════════════════════ */
    QTableWidget {{
        background-color: transparent;
        border: none;
        gridline-color: transparent;
        outline: none;
        selection-background-color: transparent;
        selection-color: {theme['text']};
    }}
    QTableWidget#VideoTable {{
        border-radius: {theme['card']}px;
    }}
    QTableWidget#VideoTable QTableCornerButton::section {{
        background-color: {theme['surface_soft']};
        border: none;
        border-bottom: 1px solid {theme['border']};
        border-right: 1px solid {theme['border_soft']};
        border-top-left-radius: {theme['card']}px;
    }}
    QTableWidget#VideoTable QHeaderView::section:first {{
        border-top-left-radius: {theme['card']}px;
    }}
    QTableWidget#VideoTable QHeaderView::section:last {{
        border-top-right-radius: {theme['card']}px;
    }}
    QTableWidget::item {{
        padding: 0 12px;
        border: none;
        border-bottom: 1px solid {theme['border_soft']};
        color: {theme['text_muted']};
        background: transparent;
    }}
    QTableWidget::item:alternate {{
        background-color: {theme['surface_alt']};
    }}
    QTableWidget::item:hover {{
        background-color: {theme['row_hover']};
        color: {theme['text']};
    }}
    QTableWidget::item:selected {{
        background-color: rgba(0, 214, 143, 0.13);
        color: {theme['text']};
        border-left: 3px solid {theme['primary']};
    }}
    QTableWidget::indicator {{
        width: 16px; height: 16px;
        border: 2px solid {theme['text_faint']};
        border-radius: 4px;
        background-color: {theme['input']};
        margin: 0 8px;
    }}
    QTableWidget::indicator:checked {{
        background-color: {theme['primary']};
        border: 2px solid {theme['primary']};
        image: none;
    }}
    QTableWidget::indicator:hover {{
        border: 2px solid {theme['primary']};
    }}
    QHeaderView {{
        background-color: transparent;
        border: none;
    }}
    QHeaderView::section {{
        background-color: {theme['surface_soft']};
        color: {theme['text_faint']};
        border: none;
        border-bottom: 1px solid {theme['border']};
        border-right: 1px solid {theme['border_soft']};
        padding: 0 10px;
        height: 34px;
        font-weight: 700;
        font-size: {theme['label_size']}px;
        letter-spacing: 1.6px;
    }}
    QHeaderView::section:last {{
        border-right: none;
    }}
    QHeaderView::section:hover {{
        background-color: {theme['surface_elevated']};
        color: {theme['text_muted']};
    }}
    QTableWidget#ActiveStats {{
        background-color: transparent;
        border: none;
        outline: none;
    }}
    QTableWidget#ActiveStats::item {{
        padding: 0 10px;
        border-bottom: 1px solid {theme['border_soft']};
        color: {theme['text_muted']};
        background: transparent;
        font-size: {theme['meta_size']}px;
    }}
    QTableWidget#ActiveStats::item:hover {{
        background-color: {theme['row_hover']};
    }}

    /* ═══════════════════════════════════════════════════════
       DOWNLOAD STATS
    ═══════════════════════════════════════════════════════ */
    QLabel#StatTitle {{
        color: {theme['text_faint']};
        font-size: {theme['label_size']}px;
        font-weight: 700;
        letter-spacing: 1.6px;
    }}
    QLabel#StatValue {{
        color: {theme['text']};
        font-size: 22px;
        font-weight: 700;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
    }}
    QLabel#StatValueCompact {{
        color: {theme['text']};
        font-size: 18px;
        font-weight: 700;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
    }}
    QLabel#StatUnit {{
        color: {theme['text_faint']};
        font-size: 11px;
        font-weight: 500;
    }}
    QFrame#StatSeparator {{
        background-color: {theme['border']};
        border: none;
        min-width: 1px;
        max-width: 1px;
    }}
    QLabel#CountGreen {{
        color: {theme['primary']};
        font-size: {theme['meta_size']}px;
        font-weight: 600;
    }}
    QLabel#CountYellow {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-weight: 600;
    }}
    QLabel#RowProgressPercent {{
        color: {theme['primary']};
        font-size: 11px;
        font-weight: 700;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
    }}

    /* ═══════════════════════════════════════════════════════
       STATUS LABELS
    ═══════════════════════════════════════════════════════ */
    QLabel#StatusInfo    {{ color: {theme['accent']};   font-weight: 600; font-size: {theme['meta_size']}px; }}
    QLabel#StatusOk      {{ color: {theme['primary']};  font-weight: 600; font-size: {theme['meta_size']}px; }}
    QLabel#StatusWarn    {{ color: {theme['warning']};  font-weight: 600; font-size: {theme['meta_size']}px; }}
    QLabel#StatusErr     {{ color: {theme['danger']};   font-weight: 600; font-size: {theme['meta_size']}px; }}
    QLabel#StatusNeutral {{ color: {theme['text_faint']}; font-weight: 500; font-size: {theme['meta_size']}px; }}

    /* ═══════════════════════════════════════════════════════
       FOOTER
    ═══════════════════════════════════════════════════════ */
    QFrame#Footer {{
        background-color: {theme['surface']};
        border: none;
        border-top: 1px solid {theme['border']};
    }}
    QLabel#FooterText {{
        color: {theme['text_muted']};
        font-size: {theme['body_size']}px;
        font-weight: 500;
    }}
    QLabel#FooterPercent {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-weight: 600;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
    }}

    /* ═══════════════════════════════════════════════════════
       SCROLLBARS
    ═══════════════════════════════════════════════════════ */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 5px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background-color: {theme['border']};
        border-radius: 3px;
        min-height: 28px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {theme['text_faint']};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        border: none; background: transparent; height: 0;
    }}

    /* ═══════════════════════════════════════════════════════
       GENERIC LIST
    ═══════════════════════════════════════════════════════ */
    QListWidget {{
        background: transparent;
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        padding: 10px 14px;
        border-bottom: 1px solid {theme['border_soft']};
    }}
    QListWidget::item:hover {{
        background-color: {theme['row_hover']};
    }}
    QListWidget::item:selected {{
        background-color: {theme['row_selected']};
        color: {theme['text']};
        border-left: 2px solid {theme['primary']};
    }}

    /* ═══════════════════════════════════════════════════════
       LOGIN PAGE — RICH LABELS
    ═══════════════════════════════════════════════════════ */
    QWidget#LoginPage {{
        background-color: {theme['surface']};
    }}
    QLabel#GuideHeading {{
        color: {theme['text']};
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
        font-size: 16px;
        font-weight: 700;
    }}
    QLabel#GuideSub {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        line-height: 1.5;
    }}
    QLabel#GuideStepTitle {{
        color: {theme['text']};
        font-size: {theme['meta_size']}px;
        font-weight: 700;
    }}
    QLabel#GuideTip {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-style: italic;
    }}
    QLabel#SignInBadge {{
        min-width: 36px; max-width: 36px;
        min-height: 36px; max-height: 36px;
        border-radius: 9px;
        background-color: {theme['primary']};
        color: {theme['button_text']};
        font-size: 13px;
        font-weight: 800;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
        qproperty-alignment: 'AlignCenter';
    }}
    QLabel#SignInHeading {{
        color: {theme['text']};
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel#SignInSub {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
    }}
    QLabel#SignInIcon {{
        font-size: 32px;
    }}

    /* ═══════════════════════════════════════════════════════
       CHAT PAGE HINT
    ═══════════════════════════════════════════════════════ */
    QLabel#PageHint {{
        color: {theme['text_faint']};
        font-size: {theme['meta_size']}px;
        font-style: italic;
        margin-top: -6px;
    }}

    /* ═══════════════════════════════════════════════════════
       DOWNLOAD PAGE — BATCH PERCENT BADGE
    ═══════════════════════════════════════════════════════ */
    QLabel#BatchPercent {{
        color: {theme['primary']};
        font-size: 15px;
        font-weight: 700;
        font-family: '{theme['heading_font']}', 'Segoe UI', sans-serif;
    }}

    /* ═══════════════════════════════════════════════════════
       TOOLTIP
    ═══════════════════════════════════════════════════════ */
    QToolTip {{
        background-color: {theme['surface_elevated']};
        color: {theme['text_muted']};
        border: 1px solid {theme['border']};
        border-radius: 6px;
        padding: 5px 9px;
        font-size: {theme['meta_size']}px;
    }}

    /* ═══════════════════════════════════════════════════════
       MESSAGE BOX (dark theme for dialogs)
    ═══════════════════════════════════════════════════════ */
    QMessageBox {{
        background-color: {theme['panel']};
    }}
    QMessageBox QLabel {{
        color: {theme['text']};
        font-size: {theme['body_size']}px;
        background: transparent;
    }}
    QMessageBox QPushButton {{
        min-width: 88px;
        min-height: 32px;
        border-radius: {theme['button']}px;
        font-size: {theme['meta_size']}px;
        font-weight: 700;
        background-color: {theme['surface_soft']};
        color: {theme['text_muted']};
        border: 1px solid {theme['border']};
    }}
    QMessageBox QPushButton:hover {{
        background-color: {theme['surface_elevated']};
        color: {theme['text']};
        border-color: {theme['text_faint']};
    }}
    QMessageBox QPushButton:default {{
        background-color: {theme['primary']};
        color: {theme['button_text']};
        border: none;
    }}
    QMessageBox QPushButton:default:hover {{
        background-color: {theme['primary_hover']};
    }}
    """
