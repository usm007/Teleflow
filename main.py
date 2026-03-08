import sys
import os
import asyncio
import qasync
import webbrowser
import ctypes
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import re

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QListWidget, QTableWidget, QTableWidgetItem, QProgressBar, 
    QFrame, QHeaderView, QLineEdit, QPushButton, QStackedWidget, 
    QAbstractItemView, QListWidgetItem, QGridLayout, QSizePolicy,
    QCheckBox, QFileDialog, QMessageBox, QComboBox, QStyle, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, QSettings, QSize
from PySide6.QtGui import QCursor, QIcon, QColor, QBrush, QFont, QFontMetrics
from core import TelegramWorker, BASE_DIR
from themes import get_theme
from stylesheet_builder import build_stylesheet
from assets import (
    DecryptLabel,
    HackerProgressBar,
    MatrixLoader,
    CyberLoadingOverlay,
)


def configure_logging():
    os.makedirs(BASE_DIR, exist_ok=True)
    log_path = os.path.join(BASE_DIR, "teleflow.log")
    logger = logging.getLogger("teleflow")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(log_path, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = configure_logging()

try:
    myappid = u'teleflow.downloader.pro.v4'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    logger.debug("Could not set AppUserModelID", exc_info=True)


class SelectableVideoTable(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)
        self.last_row = None
        self.range_toggle_callback = None

    def mousePressEvent(self, event):
        index = self.indexAt(event.position().toPoint())
        if index.isValid() and event.button() == Qt.LeftButton:
            row = index.row()
            col = index.column()
            if event.modifiers() & Qt.ShiftModifier and self.last_row is not None:
                clicked_item = self.item(row, 0)
                target_state = Qt.Checked
                if clicked_item and col == 0 and clicked_item.checkState() == Qt.Checked:
                    target_state = Qt.Unchecked
                start, end = sorted((self.last_row, row))
                self.blockSignals(True)
                for r in range(start, end + 1):
                    check_item = self.item(r, 0)
                    if check_item:
                        check_item.setCheckState(target_state)
                self.blockSignals(False)
                if self.range_toggle_callback:
                    self.range_toggle_callback()
                self.last_row = row
                event.accept()
                return

            self.last_row = row
        super().mousePressEvent(event)


class RoundedCardFrame(QFrame):
    """Styled rounded card container without pixel mask clipping."""

    def __init__(self, radius=14, parent=None):
        super().__init__(parent)
        self._radius = radius
        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_radius(self, radius):
        self._radius = max(0, int(radius))

class MainWindow(QMainWindow):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.decrypt_labels = []
        self.setWindowIcon(QIcon(resource_path("icon.ico"))) 
        self.setWindowTitle("Teleflow v4")
        self.resize(1000, 700) 
        self.setMinimumSize(920, 640)
        
        # Load Settings (Last Download Path)
        self.settings = QSettings("Teleflow", "Downloader")
        default_dl = os.path.join(os.path.expanduser("~"), "Downloads", "Teleflow")
        saved_download_path = self.settings.value("download_path", default_dl)
        self.download_path = str(saved_download_path) if saved_download_path else default_dl
        try:
            os.makedirs(self.download_path, exist_ok=True)
        except Exception:
            logger.exception("Failed to ensure download folder exists: %s", self.download_path)
        self.theme_preference = "light"
        self.theme_mode = "light"
        self.theme = get_theme(self.theme_mode)
        self._active_filter = "all"
        self._auto_connect_attempted = False
        self.depth_effects = []
        self.queue_paused = False
        self.concurrent_limit = 3
        self._scan_in_progress = False
        self._new_video_anim_state = {}
        self._new_video_anim_frames = [".", "..", "..."]
        
        center = QApplication.primaryScreen().availableGeometry().center()
        frame_geo = self.frameGeometry()
        frame_geo.moveCenter(center)
        self.move(frame_geo.topLeft())
        
        self.central_container = QWidget(); self.setCentralWidget(self.central_container)
        self.global_layout = QVBoxLayout(self.central_container)
        self.global_layout.setContentsMargins(0, 0, 0, 0)
        self.global_layout.setSpacing(0)

        self.top_bar = self.init_top_bar()
        self.global_layout.addWidget(self.top_bar)

        self.stack = QStackedWidget(); self.global_layout.addWidget(self.stack)

        self.init_footer(); self.init_login_page(); self.init_chat_page(); self.init_video_page(); self.init_download_page()
        self.is_downloading = False; self.all_chats = []; self.current_videos = []; self.sort_reverse = False

        self.video_filter_timer = QTimer(self)
        self.video_filter_timer.setSingleShot(True)
        self.video_filter_timer.setInterval(200)
        self.video_filter_timer.timeout.connect(self.refresh_video_table)

        self.new_video_anim_timer = QTimer(self)
        self.new_video_anim_timer.setInterval(180)
        self.new_video_anim_timer.timeout.connect(self._tick_new_video_animation)
        
        # --- LOADING OVERLAY ---
        self.loader = CyberLoadingOverlay(self.central_container, theme=self.theme)
        self.loader.raise_()
        
        self.worker.saved_creds_found.connect(self.on_creds_found)
        self.worker.request_creds.connect(lambda: self.stack.setCurrentIndex(0))
        self.worker.login_success.connect(self.on_login_success)
        self.worker.chats_loaded.connect(self.store_and_populate_chats)
        self.worker.videos_loaded.connect(self.populate_videos)
        self.worker.scan_progress.connect(self.update_scan_progress)
        self.worker.scan_cache_loaded.connect(self.on_scan_cache_loaded)
        self.worker.scan_finished.connect(self.on_scan_finished)
        self.worker.download_started.connect(self.on_dl_start)
        self.worker.download_progress.connect(self.on_dl_progress)
        self.worker.individual_progress.connect(self.update_individual_row)
        self.worker.queue_finished.connect(self.on_queue_finished)
        self.worker.auth_status.connect(self.update_status)
        self.worker.request_otp.connect(self.on_request_otp)
        self.worker.request_password.connect(self.on_request_pwd)
        self.worker.session_corrupted.connect(self.on_session_corrupted)
        self.worker.operation_aborted.connect(self.on_operation_aborted)
        self.stack.currentChanged.connect(self.on_page_changed)

        self.row_map = {} 
        self.cnt_down = 0
        self.cnt_queue = 0

        self.apply_theme("light")
        self.apply_interaction_cues()
        self.update_window_title()

    def resizeEvent(self, event): 
        self.loader.setGeometry(self.rect()) # KEEP OVERLAY FULL SIZE
        self._update_global_stream_elide()
        # Re-elide video names when the filename column changes with window size.
        if (
            hasattr(self, "video_table")
            and hasattr(self, "list_stack")
            and self.stack.currentIndex() == 2
            and self.list_stack.currentIndex() == 0
            and self.current_videos
        ):
            self.schedule_video_filter_refresh()
        super().resizeEvent(event)

    def init_top_bar(self):
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(60)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 6, 18, 6)
        layout.setSpacing(12)

        mono = QLabel("TF")
        mono.setObjectName("AppMono")
        layout.addWidget(mono)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("TELEFLOW")
        title.setObjectName("AppTitle")
        title_box.addWidget(title)

        layout.addLayout(title_box)
        layout.addStretch()

        self.lbl_step = QLabel("Log In")
        self.lbl_step.setObjectName("StepIndicator")
        layout.addWidget(self.lbl_step)
        layout.addStretch()

        self.btn_switch_account = QPushButton("Switch Account")
        self.btn_switch_account.setObjectName("GhostBtn")
        self.btn_switch_account.setFixedWidth(138)
        self.btn_switch_account.clicked.connect(self.switch_account)
        layout.addWidget(self.btn_switch_account)
        self._apply_depth_effect(bar, blur=12, y_offset=2)
        return bar

    def add_section_header(self, parent_layout, text):
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        parent_layout.addWidget(label)
        rule = QFrame()
        rule.setObjectName("SectionRule")
        rule.setFixedHeight(1)
        parent_layout.addWidget(rule)

    def make_decrypt_label(self, text, size):
        label = DecryptLabel(text, size=size, theme=self.theme)
        self.decrypt_labels.append(label)
        return label

    def _sync_theme_controls(self):
        return

    def set_theme_preference(self, mode):
        self.theme_preference = "light"
        self.settings.setValue("theme_preference", "light")
        self.settings.sync()
        self.theme_mode = "light"
        self.apply_theme("light")

    def toggle_theme(self):
        self.set_theme_preference("light")

    def apply_theme(self, mode):
        self.theme_mode = mode
        self.theme = get_theme(mode)
        self.setStyleSheet(build_stylesheet(self.theme))

        for label in self.decrypt_labels:
            label.set_theme(self.theme)

        for widget_name in ["loader", "dl_bar", "matrix_loader", "graph"]:
            widget = getattr(self, widget_name, None)
            if widget and hasattr(widget, "set_theme"):
                widget.set_theme(self.theme)

        self._refresh_login_status_style(self.lbl_login_status.text() if hasattr(self, "lbl_login_status") else "")
        self._refresh_depth_effects()

        if hasattr(self, "active_table"):
            for row in range(self.active_table.rowCount()):
                widget = self.active_table.cellWidget(row, 0)
                if isinstance(widget, QLabel):
                    widget.setText(self._format_file_name_html(widget.toolTip() or widget.text()))

        self._update_global_stream_elide()

        self._sync_theme_controls()

    def _apply_depth_effect(self, widget, blur=12, y_offset=2):
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(blur)
        effect.setOffset(0, y_offset)
        widget.setGraphicsEffect(effect)
        self.depth_effects.append(effect)

    def _make_card_frame(self, object_name):
        frame = RoundedCardFrame(radius=self.theme.get("card", 14))
        frame.setObjectName(object_name)
        return frame

    def _refresh_depth_effects(self):
        glow = QColor(self.theme.get("primary", "#00D68F"))
        glow.setAlpha(24)
        for effect in self.depth_effects:
            effect.setColor(glow)

    def apply_interaction_cues(self):
        for button in self.findChildren(QPushButton):
            button.setCursor(Qt.PointingHandCursor)
        if hasattr(self, "chat_list"):
            self.chat_list.setMouseTracking(True)
            self.chat_list.viewport().setMouseTracking(True)

    # --- PAGES ---
    def init_login_page(self):
        p = QWidget()
        p.setObjectName("LoginPage")
        outer = QVBoxLayout(p)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addStretch(1)

        layout = QHBoxLayout()
        layout.setContentsMargins(self.theme["page_h"], 0, self.theme["page_h"], 0)
        layout.setSpacing(28)
        layout.addStretch(1)

        # ── Guide panel ────────────────────────────────────────
        guide_pan = self._make_card_frame("GuidePanel")
        guide_pan.setMinimumSize(420, 500)
        guide_pan.setMaximumSize(460, 560)
        self._apply_depth_effect(guide_pan)

        g_ly = QVBoxLayout(guide_pan)
        g_ly.setContentsMargins(28, 32, 28, 28)
        g_ly.setSpacing(0)

        guide_heading = QLabel("Getting Started")
        guide_heading.setObjectName("GuideHeading")
        g_ly.addWidget(guide_heading)
        g_ly.addSpacing(4)
        guide_sub = QLabel("You need a free Telegram API key to use Teleflow.")
        guide_sub.setObjectName("GuideSub")
        guide_sub.setWordWrap(True)
        g_ly.addWidget(guide_sub)
        g_ly.addSpacing(20)

        steps = [
            ("Visit", 'Go to <a href="https://my.telegram.org">my.telegram.org</a> and log in.'),
            ("API Tools", "Open <b>API Development Tools</b> in the menu."),
            ("Create App", "Fill in any app name and submit to get your credentials."),
            ("Connect", "Paste your API ID, API Hash, and phone number below."),
        ]
        for index, (short, detail) in enumerate(steps, start=1):
            row = QFrame(objectName="GuideStepCard")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(10, 10, 12, 10)
            row_layout.setSpacing(12)
            idx = QLabel(str(index), objectName="GuideStepIndex")
            body = QVBoxLayout()
            body.setSpacing(1)
            lbl_short = QLabel(short, objectName="GuideStepTitle")
            lbl_detail = QLabel(detail, objectName="GuideStepBody")
            lbl_detail.setOpenExternalLinks(True)
            lbl_detail.setWordWrap(True)
            body.addWidget(lbl_short)
            body.addWidget(lbl_detail)
            row_layout.addWidget(idx, 0, Qt.AlignTop)
            row_layout.addLayout(body, 1)
            g_ly.addWidget(row)
            if index < len(steps):
                g_ly.addSpacing(8)

        g_ly.addStretch()
        divider = QFrame(objectName="SectionRule")
        divider.setFixedHeight(1)
        g_ly.addWidget(divider)
        g_ly.addSpacing(12)
        tip = QLabel("💡  Your credentials are stored locally and never shared.")
        tip.setObjectName("GuideTip")
        tip.setWordWrap(True)
        g_ly.addWidget(tip)

        layout.addWidget(guide_pan, 0, Qt.AlignVCenter)
        login_pan = self._make_card_frame("SignInCard")
        login_pan.setMinimumSize(420, 500)
        login_pan.setMaximumSize(460, 560)
        self._apply_depth_effect(login_pan)

        self.login_stack = QStackedWidget(login_pan)
        pl = QVBoxLayout(login_pan)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.addWidget(self.login_stack)

        # Page 0 — Credentials
        pg0 = QWidget()
        p0l = QVBoxLayout(pg0)
        p0l.setSpacing(0)
        p0l.setContentsMargins(32, 32, 32, 28)

        app_badge = QLabel("TF")
        app_badge.setObjectName("SignInBadge")
        p0l.addWidget(app_badge, 0, Qt.AlignLeft)
        p0l.addSpacing(14)

        heading = self.make_decrypt_label("Welcome back", size=18)
        heading.setObjectName("SignInHeading")
        p0l.addWidget(heading)
        p0l.addSpacing(4)
        sign_sub = QLabel("Enter your Telegram API credentials to continue.")
        sign_sub.setObjectName("SignInSub")
        sign_sub.setWordWrap(True)
        p0l.addWidget(sign_sub)
        p0l.addSpacing(24)

        p0l.addWidget(QLabel("API ID", objectName="FieldLabel"))
        p0l.addSpacing(5)
        self.inp_api = QLineEdit(placeholderText="e.g. 12345678")
        p0l.addWidget(self.inp_api)
        p0l.addSpacing(14)

        p0l.addWidget(QLabel("API Hash", objectName="FieldLabel"))
        p0l.addSpacing(5)
        hash_row = QHBoxLayout()
        hash_row.setSpacing(8)
        self.inp_hash = QLineEdit(placeholderText="32-character hash")
        self.inp_hash.setEchoMode(QLineEdit.Password)
        hash_row.addWidget(self.inp_hash, 1)
        self.btn_toggle_hash = QPushButton("Show")
        self.btn_toggle_hash.setObjectName("Secondary")
        self.btn_toggle_hash.setFixedSize(64, 34)
        self.btn_toggle_hash.clicked.connect(self.toggle_hash_visibility)
        hash_row.addWidget(self.btn_toggle_hash)
        p0l.addLayout(hash_row)
        p0l.addSpacing(14)

        p0l.addWidget(QLabel("Phone Number", objectName="FieldLabel"))
        p0l.addSpacing(5)
        self.inp_phone = QLineEdit(placeholderText="+1 555 000 0000")
        self.inp_phone.returnPressed.connect(self.do_connect)
        p0l.addWidget(self.inp_phone)
        p0l.addSpacing(20)

        btn_con = QPushButton("Connect to Telegram")
        btn_con.setObjectName("PrimaryWide")
        btn_con.clicked.connect(self.do_connect)
        p0l.addWidget(btn_con)
        p0l.addSpacing(10)

        self.lbl_login_status = QLabel("", alignment=Qt.AlignCenter)
        self.lbl_login_status.setObjectName("StatusInfo")
        p0l.addWidget(self.lbl_login_status)
        self.login_stack.addWidget(pg0)

        # Page 1 — OTP
        pg1 = QWidget()
        p1l = QVBoxLayout(pg1)
        p1l.setSpacing(0)
        p1l.setContentsMargins(32, 40, 32, 28)
        otp_icon = QLabel("📱")
        otp_icon.setObjectName("SignInIcon")
        p1l.addWidget(otp_icon, 0, Qt.AlignCenter)
        p1l.addSpacing(12)
        otp_title = self.make_decrypt_label("Check your phone", size=16)
        otp_title.setObjectName("SignInHeading")
        p1l.addWidget(otp_title, 0, Qt.AlignCenter)
        p1l.addSpacing(6)
        otp_sub = QLabel("Telegram sent a verification code to your device.")
        otp_sub.setObjectName("SignInSub")
        otp_sub.setAlignment(Qt.AlignCenter)
        otp_sub.setWordWrap(True)
        p1l.addWidget(otp_sub)
        p1l.addSpacing(28)
        p1l.addWidget(QLabel("Verification Code", objectName="FieldLabel"))
        p1l.addSpacing(5)
        self.inp_otp = QLineEdit(placeholderText="e.g. 12345")
        self.inp_otp.returnPressed.connect(self.do_verify_otp)
        p1l.addWidget(self.inp_otp)
        p1l.addSpacing(16)
        btn_otp = QPushButton("Verify Code")
        btn_otp.setObjectName("PrimaryWide")
        btn_otp.clicked.connect(self.do_verify_otp)
        p1l.addWidget(btn_otp)
        p1l.addStretch()
        self.login_stack.addWidget(pg1)

        # Page 2 — 2FA
        pg2 = QWidget()
        p2l = QVBoxLayout(pg2)
        p2l.setSpacing(0)
        p2l.setContentsMargins(32, 40, 32, 28)
        lock_icon = QLabel("🔒")
        lock_icon.setObjectName("SignInIcon")
        p2l.addWidget(lock_icon, 0, Qt.AlignCenter)
        p2l.addSpacing(12)
        pwd_title = self.make_decrypt_label("Two-step verification", size=16)
        pwd_title.setObjectName("SignInHeading")
        p2l.addWidget(pwd_title, 0, Qt.AlignCenter)
        p2l.addSpacing(6)
        pwd_sub = QLabel("Your account has an additional password set.")
        pwd_sub.setObjectName("SignInSub")
        pwd_sub.setAlignment(Qt.AlignCenter)
        pwd_sub.setWordWrap(True)
        p2l.addWidget(pwd_sub)
        p2l.addSpacing(28)
        p2l.addWidget(QLabel("Password", objectName="FieldLabel"))
        p2l.addSpacing(5)
        self.inp_2fa = QLineEdit(placeholderText="Your 2FA password")
        self.inp_2fa.setEchoMode(QLineEdit.Password)
        self.inp_2fa.returnPressed.connect(self.do_verify_pwd)
        p2l.addWidget(self.inp_2fa)
        p2l.addSpacing(16)
        btn_2fa = QPushButton("Continue")
        btn_2fa.setObjectName("PrimaryWide")
        btn_2fa.clicked.connect(self.do_verify_pwd)
        p2l.addWidget(btn_2fa)
        p2l.addStretch()
        self.login_stack.addWidget(pg2)

        layout.addWidget(login_pan, 0, Qt.AlignVCenter)
        layout.addStretch(1)
        outer.addLayout(layout)
        outer.addStretch(1)
        self.stack.addWidget(p)

    def init_chat_page(self):
        p = QWidget()
        layout = QVBoxLayout(p)
        layout.setContentsMargins(self.theme["page_h"], 12, self.theme["page_h"], self.theme["page_v"])
        layout.setSpacing(12)

        f_bar = QHBoxLayout()
        f_bar.setSpacing(8)
        self.search_chats = QLineEdit(placeholderText="Search chats...")
        self.search_chats.setObjectName("SearchInput")
        self.search_chats.setMaximumWidth(360)
        self.search_chats.setMinimumWidth(240)
        self.search_chats.textChanged.connect(self.apply_chat_filter)
        f_bar.addWidget(self.search_chats)
        f_bar.addSpacing(12)

        self.btn_all = QPushButton("All")
        self.btn_ch  = QPushButton("Channels")
        self.btn_gr  = QPushButton("Groups")
        self.btn_dm  = QPushButton("DMs")
        for b in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]:
            b.setCheckable(True)
            b.setObjectName("FilterBtn")
            b.clicked.connect(self.apply_chat_filter)
            f_bar.addWidget(b)
        self.btn_all.setChecked(True)
        f_bar.addStretch()
        layout.addLayout(f_bar)

        chat_card = self._make_card_frame("SectionPanel")
        self._apply_depth_effect(chat_card)
        chat_card_layout = QVBoxLayout(chat_card)
        chat_card_layout.setContentsMargins(0, 0, 0, 0)
        chat_card_layout.setSpacing(0)
        self.chat_list = QListWidget()
        self.chat_list.setObjectName("ChatList")
        self.chat_list.itemDoubleClicked.connect(self.start_chat_scan)
        chat_card_layout.addWidget(self.chat_list)
        layout.addWidget(chat_card)
        self.stack.addWidget(p)

    def start_chat_scan(self, item):
        self.worker.cancel_scan()
        self._scan_in_progress = True
        self._new_video_anim_state = {}
        self.new_video_anim_timer.stop()
        self.current_videos = []
        self.video_table.setRowCount(0)
        self.update_selected_summary()
        if hasattr(self, "lbl_video_cache_status"):
            self.lbl_video_cache_status.setObjectName("StatusNeutral")
            self.lbl_video_cache_status.setText("")
            self.lbl_video_cache_status.style().unpolish(self.lbl_video_cache_status)
            self.lbl_video_cache_status.style().polish(self.lbl_video_cache_status)
        if hasattr(self, "lbl_scan_progress"):
            self.lbl_scan_progress.setObjectName("StatusInfo")
            self.lbl_scan_progress.setText("Scan progress: 0 / ? (0%)")
            self.lbl_scan_progress.style().unpolish(self.lbl_scan_progress)
            self.lbl_scan_progress.style().polish(self.lbl_scan_progress)
        self.stack.setCurrentIndex(2)
        # Keep table visible during scan; no full-screen scanning animation.
        self.list_stack.setCurrentIndex(0)
        asyncio.create_task(self.worker.scan_chat(item.data(Qt.UserRole)))

    def update_scan_progress(self, count, total):
        if not hasattr(self, "lbl_scan_progress"):
            return
        if total and total > 0:
            pct = int(round(max(0.0, min(1.0, count / float(total))) * 100))
            text = f"Scan progress: {count} / {total} ({pct}%)"
        else:
            text = f"Scan progress: {count} files discovered"
        self.lbl_scan_progress.setObjectName("StatusInfo")
        self.lbl_scan_progress.setText(text)
        self.lbl_scan_progress.style().unpolish(self.lbl_scan_progress)
        self.lbl_scan_progress.style().polish(self.lbl_scan_progress)

    def on_scan_cache_loaded(self, count):
        if not hasattr(self, "lbl_video_cache_status"):
            return
        self.lbl_video_cache_status.setObjectName("StatusInfo")
        self.lbl_video_cache_status.setText(f"Loaded {count} cached videos. Refreshing...")
        self.lbl_video_cache_status.style().unpolish(self.lbl_video_cache_status)
        self.lbl_video_cache_status.style().polish(self.lbl_video_cache_status)

    def on_scan_finished(self):
        self._scan_in_progress = False
        self.new_video_anim_timer.stop()
        self._new_video_anim_state = {}
        if not hasattr(self, "lbl_video_cache_status"):
            return
        if hasattr(self, "lbl_scan_progress") and self.current_videos:
            self.lbl_scan_progress.setObjectName("StatusOk")
            self.lbl_scan_progress.setText(f"Scan complete: {len(self.current_videos)} files")
            self.lbl_scan_progress.style().unpolish(self.lbl_scan_progress)
            self.lbl_scan_progress.style().polish(self.lbl_scan_progress)
        self.list_stack.setCurrentIndex(0)
        if not self.lbl_video_cache_status.text():
            return
        self.lbl_video_cache_status.setObjectName("StatusOk")
        self.lbl_video_cache_status.setText("Scan refreshed")
        self.lbl_video_cache_status.style().unpolish(self.lbl_video_cache_status)
        self.lbl_video_cache_status.style().polish(self.lbl_video_cache_status)

        def _clear_status():
            if hasattr(self, "lbl_video_cache_status") and self.lbl_video_cache_status.text() == "Scan refreshed":
                self.lbl_video_cache_status.setObjectName("StatusNeutral")
                self.lbl_video_cache_status.setText("")
                self.lbl_video_cache_status.style().unpolish(self.lbl_video_cache_status)
                self.lbl_video_cache_status.style().polish(self.lbl_video_cache_status)

        QTimer.singleShot(1800, _clear_status)

    def init_video_page(self):
        p = QWidget()
        layout = QVBoxLayout(p)
        layout.setContentsMargins(self.theme["page_h"], 12, self.theme["page_h"], self.theme["page_v"])
        layout.setSpacing(12)

        controls_card = self._make_card_frame("SectionPanel")
        self._apply_depth_effect(controls_card)
        sl = QHBoxLayout(controls_card)
        sl.setContentsMargins(14, 10, 14, 10)
        sl.setSpacing(12)
        self.btn_back_video = QPushButton("Back")
        self.btn_back_video.setObjectName("Secondary")
        self.btn_back_video.clicked.connect(self.back_to_chat_from_video)
        sl.addWidget(self.btn_back_video)

        self.btn_sel_all = QPushButton("Select All")
        self.btn_sel_all.setObjectName("Secondary")
        self.btn_sel_all.clicked.connect(self.toggle_select_all)
        sl.addWidget(self.btn_sel_all)

        self.btn_sort_new = QPushButton("Newest")
        self.btn_sort_new.setObjectName("SortBtn")
        self.btn_sort_new.setCheckable(True)
        self.btn_sort_new.setChecked(True)
        self.btn_sort_new.clicked.connect(lambda: self.toggle_sort(True))
        self.btn_sort_old = QPushButton("Oldest")
        self.btn_sort_old.setObjectName("SortBtn")
        self.btn_sort_old.setCheckable(True)
        self.btn_sort_old.clicked.connect(lambda: self.toggle_sort(False))
        sort_group = QFrame()
        sort_group.setObjectName("SortSegment")
        sg_layout = QHBoxLayout(sort_group)
        sg_layout.setContentsMargins(3, 3, 3, 3)
        sg_layout.setSpacing(4)
        sg_layout.addWidget(self.btn_sort_new)
        sg_layout.addWidget(self.btn_sort_old)
        sl.addWidget(sort_group)

        self.search_videos = QLineEdit(placeholderText="Search files...")
        self.search_videos.setObjectName("SearchInput")
        self.search_videos.textChanged.connect(self.schedule_video_filter_refresh)
        self.search_videos.setMinimumWidth(260)
        self.search_videos.setMaximumWidth(460)
        self.search_videos.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sl.addWidget(self.search_videos)

        sl.addStretch(1)

        self.chk_show_caption = QCheckBox("Show Captions")
        self.chk_show_caption.setCursor(Qt.PointingHandCursor)
        self.chk_show_caption.stateChanged.connect(self.schedule_video_filter_refresh)
        sl.addWidget(self.chk_show_caption)
        layout.addWidget(controls_card)

        scan_status_row = QHBoxLayout()
        scan_status_row.setSpacing(16)
        self.lbl_video_cache_status = QLabel("")
        self.lbl_video_cache_status.setObjectName("StatusNeutral")
        scan_status_row.addWidget(self.lbl_video_cache_status, 0, Qt.AlignLeft)
        scan_status_row.addStretch(1)
        self.lbl_scan_progress = QLabel("")
        self.lbl_scan_progress.setObjectName("StatusNeutral")
        scan_status_row.addWidget(self.lbl_scan_progress, 0, Qt.AlignRight)
        layout.addLayout(scan_status_row)

        self.list_stack = QStackedWidget()

        self.video_table = SelectableVideoTable(0, 4)
        self.video_table.setObjectName("VideoTable")
        self.video_table.range_toggle_callback = self.update_selected_summary
        self.video_table.setHorizontalHeaderLabels(["✓", "File name", "Date Added", "Size"])
        self.video_table.setAlternatingRowColors(True)
        self.video_table.setShowGrid(False)
        self.video_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.video_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.video_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.video_table.setFocusPolicy(Qt.NoFocus)
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.verticalHeader().setDefaultSectionSize(48)
        self.video_table.setWordWrap(True)
        self.video_table.setMouseTracking(True)
        self.video_table.viewport().setMouseTracking(True)
        self.video_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.video_table.setColumnWidth(0, 64)
        self.video_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.video_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.video_table.setColumnWidth(2, 156)
        self.video_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.video_table.setColumnWidth(3, 96)
        h0 = self.video_table.horizontalHeaderItem(0)
        if h0:
            h0.setTextAlignment(Qt.AlignCenter)
        self.video_table.cellDoubleClicked.connect(self.on_video_cell_double_click)
        self.video_table.itemChanged.connect(self.on_video_item_changed)
        self.list_stack.addWidget(self.video_table)

        self.matrix_loader = MatrixLoader(theme=self.theme)
        self.list_stack.addWidget(self.matrix_loader)

        table_card = self._make_card_frame("SectionPanel")
        self._apply_depth_effect(table_card)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        table_layout.addWidget(self.list_stack)
        layout.addWidget(table_card, 1)

        footer_shell = self._make_card_frame("SectionPanel")
        self._apply_depth_effect(footer_shell)
        footer_layout = QVBoxLayout(footer_shell)
        footer_layout.setContentsMargins(18, 12, 18, 12)
        footer_layout.setSpacing(6)

        self.lbl_selected_summary = QLabel("Selected: 0 files (0.0 MB)")
        self.lbl_selected_summary.setObjectName("PageSubtitle")

        bl = QHBoxLayout()
        bl.setSpacing(10)

        self.lbl_save_location = QLabel("Save to:")
        self.lbl_save_location.setObjectName("FieldLabel")
        self.txt_path = QLineEdit(self.download_path)
        self.txt_path.setObjectName("PathInput")
        self.txt_path.setReadOnly(True)
        self.txt_path.setMaximumWidth(320)
        btn_browse = QPushButton("Browse…")
        btn_browse.setFixedHeight(34)
        btn_browse.setObjectName("Secondary")
        btn_browse.clicked.connect(self.browse_folder)
        dl = QPushButton("⬇  Download Selected")
        dl.clicked.connect(self.start_download_batch)
        bl.addWidget(self.lbl_selected_summary)
        bl.addStretch()
        bl.addWidget(self.lbl_save_location)
        bl.addWidget(self.txt_path)
        bl.addWidget(btn_browse)
        self.lbl_threads = QLabel("Downloads at once:")
        self.lbl_threads.setObjectName("FieldLabel")
        bl.addWidget(self.lbl_threads)
        self.btn_conc_down = QPushButton("-")
        self.btn_conc_down.setObjectName("StepperBtn")
        self.btn_conc_down.setFixedSize(30, 30)
        self.btn_conc_down.clicked.connect(self.decrease_concurrency)
        bl.addWidget(self.btn_conc_down)
        self.lbl_concurrency_value = QLabel(str(self.concurrent_limit))
        self.lbl_concurrency_value.setObjectName("StepperValue")
        self.lbl_concurrency_value.setFixedWidth(30)
        self.lbl_concurrency_value.setAlignment(Qt.AlignCenter)
        bl.addWidget(self.lbl_concurrency_value)
        self.btn_conc_up = QPushButton("+")
        self.btn_conc_up.setObjectName("StepperBtn")
        self.btn_conc_up.setFixedSize(30, 30)
        self.btn_conc_up.clicked.connect(self.increase_concurrency)
        bl.addWidget(self.btn_conc_up)
        bl.addWidget(dl)
        footer_layout.addLayout(bl)
        layout.addWidget(footer_shell)
        self.stack.addWidget(p)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_path)
        if folder:
            self.download_path = folder
            self.txt_path.setText(folder)
            self.settings.setValue("download_path", folder)

    def init_download_page(self):
        p = QWidget()
        layout = QVBoxLayout(p)
        layout.setContentsMargins(self.theme["page_h"], self.theme["page_v"], self.theme["page_h"], self.theme["page_v"])
        layout.setSpacing(self.theme["section"])

        header_row = QHBoxLayout()
        self.dl_header = self.make_decrypt_label("Download", size=13)
        self.dl_header.setObjectName("PageTitle")
        header_row.addWidget(self.dl_header)
        header_row.addSpacing(18)
        header_row.addStretch()
        layout.addLayout(header_row)
        header_rule = QFrame()
        header_rule.setObjectName("SectionRule")
        header_rule.setFixedHeight(1)
        layout.addWidget(header_rule)

        self.add_section_header(layout, "Batch Progress")

        prog_frame = self._make_card_frame("StatCardPrimary")
        self.batch_progress_card = prog_frame
        self._apply_depth_effect(prog_frame)
        prog_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        pf_layout = QVBoxLayout(prog_frame)
        pf_layout.setContentsMargins(self.theme["md"], self.theme["section"], self.theme["md"], self.theme["section"])
        pf_layout.setSpacing(self.theme["item"])
        stream_row = QHBoxLayout()
        stream_row.setContentsMargins(0, 0, 0, 0)
        stream_row.setSpacing(6)
        self.lbl_global_prefix = QLabel("Downloading:")
        self.lbl_global_prefix.setObjectName("StreamPrefix")
        stream_row.addWidget(self.lbl_global_prefix, 0, Qt.AlignLeft)
        self.lbl_global_stream = QLabel("Waiting for queue")
        self.lbl_global_stream.setObjectName("StatusInfo")
        stream_row.addWidget(self.lbl_global_stream, 0, Qt.AlignLeft)
        stream_row.addStretch(1)
        self.lbl_batch_percent = QLabel("0%")
        self.lbl_batch_percent.setObjectName("BatchPercent")
        stream_row.addWidget(self.lbl_batch_percent, 0, Qt.AlignRight)
        pf_layout.addLayout(stream_row)
        self.dl_bar = HackerProgressBar(theme=self.theme)
        self.dl_bar.setFixedHeight(8)
        pf_layout.addWidget(self.dl_bar)

        stat_row = QHBoxLayout()
        stat_row.setSpacing(12)

        col_downloaded = QVBoxLayout()
        self.lbl_size = QLabel("0.0 / 0.0 MB", objectName="StatValueCompact")
        lbl_downloaded_meta = QLabel("DOWNLOADED", objectName="StatTitle")
        col_downloaded.addWidget(self.lbl_size)
        col_downloaded.addWidget(lbl_downloaded_meta)

        col_speed = QVBoxLayout()
        speed_wrap = QHBoxLayout()
        speed_wrap.setSpacing(4)
        self.lbl_speed = QLabel("0.00")
        self.lbl_speed.setObjectName("StatValueCompact")
        self.lbl_speed_unit = QLabel("MB/s")
        self.lbl_speed_unit.setObjectName("StatUnit")
        speed_wrap.addWidget(self.lbl_speed)
        speed_wrap.addWidget(self.lbl_speed_unit, 0, Qt.AlignBottom)
        speed_widget = QWidget()
        speed_widget.setLayout(speed_wrap)
        lbl_speed_meta = QLabel("SPEED", objectName="StatTitle")
        col_speed.addWidget(speed_widget)
        col_speed.addWidget(lbl_speed_meta)

        col_eta = QVBoxLayout()
        self.lbl_eta = QLabel("00:00", objectName="StatValueCompact")
        lbl_eta_meta = QLabel("ETA", objectName="StatTitle")
        col_eta.addWidget(self.lbl_eta)
        col_eta.addWidget(lbl_eta_meta)

        stat_row.addLayout(col_downloaded, 1)
        sep1 = QFrame()
        sep1.setObjectName("StatSeparator")
        sep1.setFrameShape(QFrame.VLine)
        stat_row.addWidget(sep1)
        stat_row.addLayout(col_speed, 1)
        sep2 = QFrame()
        sep2.setObjectName("StatSeparator")
        sep2.setFrameShape(QFrame.VLine)
        stat_row.addWidget(sep2)
        stat_row.addLayout(col_eta, 1)
        pf_layout.addLayout(stat_row)

        self.lbl_selected = QLabel("Selected: 0 files", objectName="PageSubtitle")
        pf_layout.addWidget(self.lbl_selected)
        layout.addWidget(prog_frame)

        self.add_section_header(layout, "Active Downloads")

        active_frame = self._make_card_frame("SectionPanel")
        self._apply_depth_effect(active_frame)
        af_lay = QVBoxLayout(active_frame)
        af_lay.setContentsMargins(self.theme["md"], self.theme["section"], self.theme["md"], self.theme["section"])
        af_lay.setSpacing(self.theme["item"])

        hud_layout = QHBoxLayout()
        self.lbl_manifest = QLabel("Live Download List")
        self.lbl_manifest.setObjectName("PageSubtitle")
        hud_layout.addWidget(self.lbl_manifest)
        hud_layout.addStretch()
        self.lbl_active_count = QLabel("Active: 0", objectName="CountGreen")
        self.lbl_queue_count = QLabel("Queued: 0", objectName="CountYellow")
        hud_layout.addWidget(self.lbl_active_count)
        hud_layout.addSpacing(18)
        hud_layout.addWidget(self.lbl_queue_count)
        af_lay.addLayout(hud_layout)

        self.lbl_download_status = QLabel("Ready — select files and press Download", objectName="StatusNeutral")
        af_lay.addWidget(self.lbl_download_status)

        col_hdr = QHBoxLayout()
        col_hdr.setContentsMargins(6, 2, 6, 2)
        for text, stretch, align in [
            ("FILE", 4, Qt.AlignLeft),
            ("%", 2, Qt.AlignLeft),
            ("SIZE", 2, Qt.AlignLeft),
            ("SPEED", 2, Qt.AlignLeft),
            ("ETA", 1, Qt.AlignLeft),
        ]:
            label = QLabel(text)
            label.setObjectName("StatTitle")
            col_hdr.addWidget(label, stretch, align)
        af_lay.addLayout(col_hdr)

        self.active_table = QTableWidget(0, 5)
        self.active_table.setObjectName("ActiveStats")
        self.active_table.verticalHeader().setVisible(False)
        self.active_table.verticalHeader().setDefaultSectionSize(56)
        self.active_table.horizontalHeader().setVisible(False)
        self.active_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.active_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.active_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.active_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.active_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.active_table.setColumnWidth(1, 180)
        self.active_table.setColumnWidth(2, 140)
        self.active_table.setColumnWidth(3, 120)
        self.active_table.setColumnWidth(4, 100)
        self.active_table.setShowGrid(False)
        self.active_table.setFocusPolicy(Qt.NoFocus)
        self.active_table.setSelectionMode(QAbstractItemView.NoSelection)
        af_lay.addWidget(self.active_table)
        layout.addWidget(active_frame)

        btn_l = QHBoxLayout()
        btn_bk = QPushButton("Back")
        btn_bk.setObjectName("Secondary")
        btn_bk.clicked.connect(self.go_back_keep_downloading)
        self.btn_pause = QPushButton("Pause Queue")
        self.btn_pause.setObjectName("Amber")
        self.btn_pause.setFixedHeight(36)
        self.btn_pause.setMinimumWidth(120)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_st = QPushButton("Stop")
        self.btn_st.setObjectName("Destructive")
        self.btn_st.setFixedHeight(36)
        self.btn_st.setMinimumWidth(72)
        self.btn_st.clicked.connect(self.stop_download)
        self.chk_shutdown = QCheckBox("Auto shutdown")
        self.chk_shutdown.setCursor(Qt.PointingHandCursor)
        btn_l.addWidget(btn_bk)
        btn_l.addWidget(self.btn_pause)
        btn_l.addWidget(self.btn_st)
        btn_l.addStretch()
        btn_l.addWidget(self.chk_shutdown)
        layout.addLayout(btn_l)
        self._set_global_stream_text("Waiting for queue")
        self.stack.addWidget(p)

    def init_footer(self):
        self.footer = QFrame()
        self.footer.setObjectName("Footer")
        self.footer.setFixedHeight(78)
        self.footer.hide()

        layout = QHBoxLayout(self.footer)
        layout.setContentsMargins(28, 12, 28, 12)
        layout.setSpacing(10)

        self.foot_lbl_name = QLabel("...")
        self.foot_lbl_name.setObjectName("FooterText")
        layout.addWidget(self.foot_lbl_name, 1)

        self.foot_lbl_stat = QLabel("0%")
        self.foot_lbl_stat.setObjectName("FooterPercent")
        layout.addWidget(self.foot_lbl_stat)

        self.foot_btn_pause = QPushButton("Pause Queue")
        self.foot_btn_pause.setObjectName("Amber")
        self.foot_btn_pause.setFixedSize(128, 36)
        self.foot_btn_pause.clicked.connect(self.toggle_pause)
        layout.addWidget(self.foot_btn_pause)

        btn_st = QPushButton("Stop")
        btn_st.setObjectName("Destructive")
        btn_st.setFixedSize(82, 36)
        btn_st.clicked.connect(self.stop_download)
        layout.addWidget(btn_st)

        btn_ex = QPushButton("Open")
        btn_ex.setFixedSize(90, 36)
        btn_ex.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        layout.addWidget(btn_ex)

        self.global_layout.addWidget(self.footer)

    def go_back_keep_downloading(self): self.stack.setCurrentIndex(2); self.check_footer_visibility()
    def toggle_pause(self):
        self.queue_paused = not self.queue_paused
        self.btn_pause.setText("Resume Queue" if self.queue_paused else "Pause Queue")
        self.foot_btn_pause.setText("Resume Queue" if self.queue_paused else "Pause Queue")
        self.worker.set_pause(self.queue_paused)
        self.set_download_status("Queue paused" if self.queue_paused else "Queue resumed", "warn")

    def stop_download(self):
        self.worker.stop_task()
        self.set_download_status("Stopping downloads...", "warn")
    
    def toggle_sleep_prevention(self, enable):
        try:
            if enable:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
            else:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except Exception:
            logger.debug("Sleep prevention toggle failed", exc_info=True)

    def update_header_counts(self):
        self.lbl_active_count.setText(f"Active: {self.cnt_down}")
        self.lbl_queue_count.setText(f"Queued: {self.cnt_queue}")
        self.lbl_active_count.setObjectName("CountGreen" if self.cnt_down > 0 else "CountYellow")
        self.lbl_active_count.style().unpolish(self.lbl_active_count)
        self.lbl_active_count.style().polish(self.lbl_active_count)
        if hasattr(self, "lbl_active"):
            self.lbl_active.setText(str(self.cnt_down))
        if hasattr(self, "lbl_queued"):
            self.lbl_queued.setText(str(self.cnt_queue))

    def start_download_batch(self):
        # 1. Show Loader
        self.loader.start("Preparing download queue...")
        # Allow UI to render the loader before processing
        QApplication.processEvents()
        
        q = []
        # Get selected items
        for i in range(self.video_table.rowCount()):
            item = self.video_table.item(i, 0)
            if item.checkState() == Qt.Checked:
                video_data = item.data(Qt.UserRole)
                if video_data:
                    q.append(video_data)
        
        # --- NEW: Filter out items already in the active list ---
        q = [x for x in q if x['name'] not in self.row_map]
        
        if not q:
            self.loader.stop()
            if self.is_downloading:
                QMessageBox.information(self, "Info", "Selected files are already in queue.")
                self.set_download_status("Selected files are already queued", "warn")
            return

        self.lbl_selected.setText(f"{len(q)} files")

        # --- CONFLICT CHECK ---
        conflicts = []
        for item in q:
            if os.path.exists(os.path.join(self.download_path, item['name'])):
                conflicts.append(item['name'])
        
        if conflicts:
            # Hide loader to show popup
            self.loader.stop()
            box = QMessageBox(self)
            box.setWindowTitle("FILE CONFLICT")
            box.setText(f"{len(conflicts)} files already exist in the destination folder.")
            box.setInformativeText("How do you want to proceed?")
            box.setStyleSheet(self.styleSheet())
            
            btn_skip = box.addButton("Skip Existing", QMessageBox.ActionRole)
            btn_over = box.addButton("Overwrite All", QMessageBox.ActionRole)
            btn_cancel = box.addButton(QMessageBox.Cancel)
            
            box.exec()
            
            if box.clickedButton() == btn_cancel:
                self.lbl_download_status.setText("Download canceled")
                return
            elif box.clickedButton() == btn_skip:
                q = [x for x in q if x['name'] not in conflicts]
                if not q:
                    self.lbl_download_status.setText("No files left after skipping existing files")
                    return 
            
            # Restart loader if continuing
            self.loader.start("Preparing download queue...")
            QApplication.processEvents()
        # ----------------------

        self.stack.setCurrentIndex(3)
        self.dl_header.setText("Download")
        self.dl_bar.setValue(0)
        self._set_global_stream_text("Preparing queue")
        limit = self.concurrent_limit
        
        # --- NEW: APPEND OR RESET LOGIC ---
        start_index = 0
        if self.is_downloading:
            start_index = self.active_table.rowCount()
            self.active_table.setRowCount(start_index + len(q))
            self.cnt_queue += len(q) # Add to existing queue count
        else:
            self.active_table.setRowCount(len(q))
            self.row_map = {} 
            self.cnt_down = 0; self.cnt_queue = len(q)
        
        self.update_header_counts()
        self.set_download_status("Queue prepared", "info")
        self.update_window_title()
        
        for i, item in enumerate(q):
            row = start_index + i
            self.row_map[item['name']] = row

            self.active_table.setCellWidget(row, 0, self._make_file_name_cell(item['name']))
            
            bar_widget, bar_obj, percent_label = self._make_row_progress_cell()
            self.active_table.setCellWidget(row, 1, bar_widget)
            self.active_table.setItem(row, 2, QTableWidgetItem("Pending"))
            self.active_table.setItem(row, 3, QTableWidgetItem("--"))
            self.active_table.setItem(row, 4, QTableWidgetItem("--"))
            self.active_table.item(row, 2).setForeground(QBrush(QColor(self.theme["warning"])))
            self.active_table.item(row, 2).setData(Qt.UserRole, {"bar": bar_obj, "label": percent_label})
            
            for c in range(5): 
                if self.active_table.item(row,c): 
                    self.active_table.item(row,c).setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # Hide loader before starting async task
        self.loader.stop()
        asyncio.create_task(self.worker.add_to_queue(q, limit, self.download_path))

    def on_dl_start(self, f, r): 
        if not self.is_downloading:
            self.toggle_sleep_prevention(True)
            
        self.is_downloading = True
        self.queue_paused = False
        self.btn_pause.setText("Pause Queue")
        self.foot_btn_pause.setText("Pause Queue")
        self.check_footer_visibility()
        self.foot_lbl_name.setText("Batch download in progress...")
        self.update_window_title()
        
        self.cnt_down += 1; self.cnt_queue = max(0, self.cnt_queue - 1)
        self.update_header_counts()
        if f in self.row_map:
            row = self.row_map[f]
            self.active_table.item(row, 2).setText("Starting...")
            self.active_table.item(row, 2).setForeground(QBrush(QColor(self.theme["warning"])))
        self.set_download_status(f"Downloading: {f}", "info", elide=True)
        self._set_global_stream_text(f)

    def on_dl_progress(self, n, p, s, e, ps):
        self.dl_bar.setValue(p)
        speed_parts = s.split(" ", 1)
        if len(speed_parts) == 2:
            self.lbl_speed.setText(speed_parts[0])
            self.lbl_speed_unit.setText(speed_parts[1])
        else:
            self.lbl_speed.setText(s)
            self.lbl_speed_unit.setText("MB/s")
        self.lbl_eta.setText(e)
        self.lbl_size.setText(ps)
        self.foot_lbl_stat.setText(f"{p}%")
        self.foot_lbl_stat.setObjectName("StatusOk")
        self.foot_lbl_stat.style().unpolish(self.foot_lbl_stat)
        self.foot_lbl_stat.style().polish(self.foot_lbl_stat)
        if hasattr(self, "lbl_batch_percent"):
            self.lbl_batch_percent.setText(f"{p}%")
        if hasattr(self, "graph"):
            self.graph.update_value(p)
        self.update_window_title(progress=p)

    def update_individual_row(self, filename, percent, speed, eta, size):
        if filename in self.row_map:
            row = self.row_map[filename]
            status_item = self.active_table.item(row, 2)
            state_data = status_item.data(Qt.UserRole) if status_item else None
            was_done = status_item.text().lower() == "done" if status_item else False
            if state_data:
                state_data["bar"].setValue(percent)
                state_data["label"].setText(f"{percent}%")

            self.active_table.item(row, 2).setText(size if percent < 100 else "Done")
            self.active_table.item(row, 2).setForeground(QBrush(QColor(self.theme["success"] if percent == 100 else self.theme["info"])))
            self.active_table.item(row, 3).setText(speed if percent < 100 else "--")
            self.active_table.item(row, 4).setText(eta if percent < 100 else "00:00")
            if percent == 100 and not was_done:
                 self.cnt_down = max(0, self.cnt_down - 1)
                 self.update_header_counts()

    def on_queue_finished(self): 
        self.is_downloading = False; self.check_footer_visibility(); self.dl_header.setText("Download")
        self.set_download_status("All downloads completed", "ok")
        self._set_global_stream_text("Completed")
        self.cnt_down = 0; self.cnt_queue = 0; self.update_header_counts()
        self.toggle_sleep_prevention(False)
        self.update_window_title(state="complete")

        open_folder = QMessageBox.question(
            self,
            "Download Complete",
            "All downloads completed. Open download folder?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if open_folder == QMessageBox.Yes:
            try:
                os.startfile(self.download_path)
            except Exception:
                logger.exception("Failed to open download folder")

        if self.chk_shutdown.isChecked():
            response = QMessageBox.question(
                self,
                "Confirm Shutdown",
                "Batch is complete. Shutdown this computer in 60 seconds?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if response == QMessageBox.Yes:
                self.lbl_download_status.setText("Shutdown scheduled in 60 seconds")
                try:
                    subprocess.run(["shutdown", "/s", "/t", "60"], check=True)
                except Exception:
                    logger.exception("Failed to schedule shutdown")
                    QMessageBox.warning(self, "Shutdown Failed", "Could not schedule system shutdown.")
            else:
                self.lbl_download_status.setText("Shutdown canceled")

    def check_footer_visibility(self): self.footer.setVisible(self.is_downloading and self.stack.currentIndex() != 3)
    def create_stat_box(self, t, v, o, primary=False, compact=False): 
        b = QFrame()
        if primary:
            b.setObjectName("StatCardPrimary")
        elif compact:
            b.setObjectName("StatCardCompact")
        else:
            b.setObjectName("StatCard")
        vl = QVBoxLayout(b); vl.setSpacing(2); vl.setContentsMargins(12,10,12,10)
        vl.addWidget(QLabel(t.upper(), objectName="StatTitle"))
        value_name = "StatValueCompact" if compact else "StatValue"
        lb = QLabel(v, objectName=value_name)
        vl.addWidget(lb)
        setattr(self, o, lb)
        return b

    def create_speed_stat_box(self):
        card = QFrame()
        card.setObjectName("StatCardPrimary")
        layout = QVBoxLayout(card)
        layout.setSpacing(2)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.addWidget(QLabel("SPEED", objectName="StatTitle"))

        row = QHBoxLayout()
        self.lbl_speed = QLabel("0.0")
        self.lbl_speed.setObjectName("StatValue")
        self.lbl_speed_unit = QLabel("MB/s")
        self.lbl_speed_unit.setObjectName("StatUnit")
        row.addWidget(self.lbl_speed)
        row.addWidget(self.lbl_speed_unit, 0, Qt.AlignBottom)
        row.addStretch()
        layout.addLayout(row)
        return card

    def store_and_populate_chats(self, chats): 
        self.loader.stop() # Hide loader once data is ready
        self.all_chats = chats; self.apply_chat_filter(); self.stack.setCurrentIndex(1)
    
    def apply_chat_filter(self):
        s = self.sender()
        if s in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]:
            if s is self.btn_all:
                self._active_filter = "all"
            elif s is self.btn_ch:
                self._active_filter = "channel"
            elif s is self.btn_gr:
                self._active_filter = "group"
            elif s is self.btn_dm:
                self._active_filter = "dm"

        self.btn_all.setChecked(self._active_filter == "all")
        self.btn_ch.setChecked(self._active_filter == "channel")
        self.btn_gr.setChecked(self._active_filter == "group")
        self.btn_dm.setChecked(self._active_filter == "dm")

        counts = {"channel": 0, "group": 0, "dm": 0}
        for chat in self.all_chats:
            t = chat.get("type")
            if t in counts:
                counts[t] += 1

        self.btn_all.setText(f"All  {len(self.all_chats)}")
        self.btn_ch.setText(f"Channels  {counts['channel']}")
        self.btn_gr.setText(f"Groups  {counts['group']}")
        self.btn_dm.setText(f"DMs  {counts['dm']}")

        search_text = self.search_chats.text().lower(); self.chat_list.clear()
        for c in self.all_chats:
            t = c.get('type'); show_type = self._active_filter == 'all' or (self._active_filter == 'channel' and t == 'channel') or (self._active_filter == 'group' and t == 'group') or (self._active_filter == 'dm' and t == 'dm')
            if show_type and search_text in c['name'].lower():
                item = QListWidgetItem()
                item.setData(Qt.UserRole, c['id'])
                item.setData(Qt.UserRole + 1, c['name'])
                row_widget = self._make_chat_row(c)
                item.setSizeHint(QSize(0, 76))
                self.chat_list.addItem(item)
                self.chat_list.setItemWidget(item, row_widget)
    
    def populate_videos(self, v): 
        previous_ids = {item.get("id") for item in self.current_videos if isinstance(item, dict)}
        self.current_videos = v
        current_ids = {item.get("id") for item in v if isinstance(item, dict)}
        new_ids = [vid for vid in current_ids if vid is not None and vid not in previous_ids]
        if self._scan_in_progress and previous_ids and new_ids:
            for vid in new_ids:
                self._new_video_anim_state[vid] = {"frame": 0, "ttl": 16}
            if not self.new_video_anim_timer.isActive():
                self.new_video_anim_timer.start()
        if not self._scan_in_progress:
            self.list_stack.setCurrentIndex(0) # Switch back to Table View
        self.refresh_video_table()

    def _tick_new_video_animation(self):
        if not self._new_video_anim_state:
            self.new_video_anim_timer.stop()
            return

        expired = []
        for vid, state in self._new_video_anim_state.items():
            state["frame"] = (state["frame"] + 1) % len(self._new_video_anim_frames)
            state["ttl"] -= 1
            if state["ttl"] <= 0:
                expired.append(vid)

        for vid in expired:
            self._new_video_anim_state.pop(vid, None)

        if not self._new_video_anim_state:
            self.new_video_anim_timer.stop()
        self.schedule_video_filter_refresh()

    def toggle_sort(self, reverse_sort):
        self.btn_sort_new.setChecked(reverse_sort)
        self.btn_sort_old.setChecked(not reverse_sort)
        self.current_videos.sort(key=lambda x: x['id'], reverse=reverse_sort)
        self.refresh_video_table()
    
    def refresh_video_table(self):
        self.video_table.setSortingEnabled(False)
        self.video_table.blockSignals(True)
        s_txt = self.search_videos.text().lower()
        show_captions = self.chk_show_caption.isChecked()
        target_key = 'caption' if show_captions else 'name'
        f_vids = [v for v in self.current_videos if s_txt in v[target_key].lower()]
        self.video_table.setRowCount(len(f_vids))
        metrics = self.video_table.fontMetrics()
        for i, v in enumerate(f_vids):
            c = QTableWidgetItem()
            c.setCheckState(Qt.Unchecked)
            c.setTextAlignment(Qt.AlignCenter)
            c.setData(Qt.UserRole, v)
            self.video_table.setItem(i, 0, c)
            display_text = v['caption'] if show_captions else self._clean_video_display_name(v['name'])
            video_id = v.get("id")
            anim_state = self._new_video_anim_state.get(video_id)
            if anim_state:
                frame = self._new_video_anim_frames[anim_state["frame"]]
                display_text = f"[NEW{frame}] {display_text}"
            name_col_width = max(180, self.video_table.columnWidth(1) - 28)
            clipped = metrics.elidedText(display_text, Qt.ElideRight, name_col_width)
            item_text = QTableWidgetItem(clipped)
            item_text.setToolTip(display_text)
            self.video_table.setItem(i, 1, item_text)
            date_item = QTableWidgetItem(v.get('date_added', '-'))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.video_table.setItem(i, 2, date_item)
            sz = QTableWidgetItem(self._compact_size_text(v['size']))
            sz.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.video_table.setItem(i, 3, sz)
        self.video_table.blockSignals(False)
        self.update_selected_summary()

    def schedule_video_filter_refresh(self):
        self.video_filter_timer.start()

    def on_video_cell_double_click(self, row, col):
        check_item = self.video_table.item(row, 0)
        check_item.setCheckState(Qt.Unchecked if check_item.checkState() == Qt.Checked else Qt.Checked)
        self.update_selected_summary()

    def on_video_item_changed(self, item):
        if item and item.column() == 0:
            self.update_selected_summary()

    def toggle_select_all(self):
        if not self.video_table.rowCount(): return
        all_checked = True
        for i in range(self.video_table.rowCount()):
            item = self.video_table.item(i, 0)
            if not item or item.checkState() != Qt.Checked:
                all_checked = False
                break
        ns = Qt.Unchecked if all_checked else Qt.Checked
        self.video_table.blockSignals(True)
        for i in range(self.video_table.rowCount()): self.video_table.item(i,0).setCheckState(ns)
        self.video_table.blockSignals(False)
        self.update_selected_summary()

    def on_creds_found(self, a, h, p):
        self.inp_api.setText(a)
        self.inp_hash.setText(h)
        self.inp_phone.setText(p)
        if not self._auto_connect_attempted:
            self._auto_connect_attempted = True
            self.update_status("Auto-connecting with saved session...")
            QTimer.singleShot(150, self.do_connect)
    
    # --- AUTH METHODS WITH LOADING ---
    def do_connect(self): 
        self.loader.start("Connecting...")
        asyncio.create_task(self.worker.connect_client(self.inp_api.text(), self.inp_hash.text(), self.inp_phone.text()))
    
    def do_verify_otp(self):
        self.loader.start("Verifying code...")
        asyncio.create_task(self.worker.submit_otp(self.inp_otp.text()))
        
    def do_verify_pwd(self):
        self.loader.start("Verifying password...")
        asyncio.create_task(self.worker.submit_password(self.inp_2fa.text()))
        
    def on_request_otp(self):
        self.loader.stop()
        self.login_stack.setCurrentIndex(1)
        self.inp_hash.clear()
        self.inp_hash.setEchoMode(QLineEdit.Password)
        self.btn_toggle_hash.setText("Show")
        
    def on_request_pwd(self):
        self.loader.stop()
        self.login_stack.setCurrentIndex(2)

    def update_status(self, m): 
        self.loader.stop() # Stop loader on error
        self.lbl_login_status.setText(m)
        self._refresh_login_status_style(m)

    def toggle_hash_visibility(self):
        hidden = self.inp_hash.echoMode() == QLineEdit.Password
        self.inp_hash.setEchoMode(QLineEdit.Normal if hidden else QLineEdit.Password)
        self.btn_toggle_hash.setText("Hide" if hidden else "Show")

    def on_login_success(self):
        self.inp_hash.clear()
        self.stack.setCurrentIndex(1)
        self.update_window_title()

    def on_page_changed(self, index):
        self.check_footer_visibility()
        labels = {
            0: "Log In",
            1: "Chats",
            2: "Videos",
            3: "Downloader",
        }
        self.lbl_step.setText(labels.get(index, "Teleflow"))
        self.update_window_title()

    def _refresh_login_status_style(self, message):
        if not hasattr(self, "lbl_login_status"):
            return
        text = (message or "").upper()
        if text.startswith("ERROR") or text.startswith("AUTH ERROR"):
            obj = "StatusErr"
        elif "SUCCESS" in text or "CONNECTED" in text:
            obj = "StatusOk"
        else:
            obj = "StatusInfo"
        self.lbl_login_status.setObjectName(obj)
        self.lbl_login_status.style().unpolish(self.lbl_login_status)
        self.lbl_login_status.style().polish(self.lbl_login_status)

    def _make_chat_row(self, chat):
        row = QFrame()
        row.setObjectName("ChatRow")
        row.setAttribute(Qt.WA_Hover, True)
        row.setCursor(Qt.PointingHandCursor)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(18, 12, 18, 12)
        row_layout.setSpacing(12)

        name = chat.get("name", "?")
        initials = "".join([part[0] for part in name.split()[:2]]).upper() if name.strip() else "?"
        initials = initials or "?"
        avatar = QLabel(initials)
        chat_type = chat.get("type", "dm")
        if chat_type == "channel":
            avatar.setObjectName("AvatarBubbleChannel")
        elif chat_type == "group":
            avatar.setObjectName("AvatarBubbleGroup")
        else:
            avatar.setObjectName("AvatarBubbleDM")
        row_layout.addWidget(avatar)

        body = QVBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(4)
        title = QLabel(name)
        title.setObjectName("ChatTitle")
        members = chat.get("members")
        if members:
            meta = f"{chat_type.title()} - {members} members"
        else:
            meta = "Direct Message" if chat_type == "dm" else chat_type.title()
        subtitle = QLabel(meta)
        subtitle.setObjectName("ChatMeta")
        body.addWidget(title)
        body.addWidget(subtitle)
        row_layout.addLayout(body, 1)

        if chat_type == "channel":
            tag = "CH"
        elif chat_type == "group":
            tag = "GR"
        else:
            tag = "DM"
        status = QLabel(tag)
        if chat_type == "channel":
            status.setObjectName("TypeBadgeChannel")
        elif chat_type == "group":
            status.setObjectName("TypeBadgeGroup")
        else:
            status.setObjectName("TypeBadgeDM")
        row_layout.addWidget(status, 0, Qt.AlignVCenter)
        row.setMinimumHeight(76)
        return row

    def _clean_video_display_name(self, raw_name):
        return re.sub(r"^\d+_", "", raw_name or "")

    def _compact_size_text(self, size_text):
        match = re.match(r"\s*([\d.]+)\s*([A-Za-z]+)", size_text or "")
        if not match:
            return size_text
        value = float(match.group(1))
        unit = match.group(2).upper()
        return f"{value:.1f} {unit}"

    def _make_row_progress_cell(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        bar = HackerProgressBar(theme=self.theme)
        bar.setFixedHeight(6)
        bar.setValue(0)
        label = QLabel("0%")
        label.setObjectName("RowProgressPercent")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setMinimumWidth(38)

        layout.addWidget(bar, 1)
        layout.addWidget(label)
        return container, bar, label

    def _make_file_name_cell(self, filename):
        label = QLabel()
        label.setObjectName("ChatTitle")
        label.setTextFormat(Qt.RichText)
        label.setText(self._format_file_name_html(filename))
        label.setToolTip(filename)
        label.setTextInteractionFlags(Qt.NoTextInteraction)
        return label

    def _format_file_name_html(self, filename):
        escaped = (filename or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        match = re.match(r"^(\d+_)(.+)$", escaped)
        if not match:
            return escaped
        prefix = match.group(1)
        suffix = match.group(2)
        return f"<span style='color:{self.theme['text_faint']};'>{prefix}</span>{suffix}"

    def _set_global_stream_text(self, filename):
        self._global_stream_full = filename or ""
        self._update_global_stream_elide()

    def _update_global_stream_elide(self):
        if not hasattr(self, "lbl_global_stream"):
            return
        full_text = getattr(self, "_global_stream_full", self.lbl_global_stream.text()) or ""
        max_width = 520
        if hasattr(self, "batch_progress_card"):
            max_width = max(120, int(self.batch_progress_card.width() * 0.6))
        fm = QFontMetrics(self.lbl_global_stream.font())
        self.lbl_global_stream.setMaximumWidth(max_width)
        self.lbl_global_stream.setText(fm.elidedText(full_text, Qt.ElideRight, max_width))

    def set_download_status(self, text, level="info", elide=False):
        shown = text
        if elide:
            fm = QFontMetrics(self.lbl_download_status.font())
            shown = fm.elidedText(text, Qt.ElideMiddle, 520)
        self.lbl_download_status.setText(shown)
        mapping = {
            "info": "StatusInfo",
            "warn": "StatusWarn",
            "ok": "StatusOk",
            "err": "StatusErr",
        }
        self.lbl_download_status.setObjectName(mapping.get(level, "StatusInfo"))
        self.lbl_download_status.style().unpolish(self.lbl_download_status)
        self.lbl_download_status.style().polish(self.lbl_download_status)

    def update_selected_summary(self):
        selected_count = 0
        total_mb = 0.0
        for i in range(self.video_table.rowCount()):
            check_item = self.video_table.item(i, 0)
            size_item = self.video_table.item(i, 3)
            if check_item and check_item.checkState() == Qt.Checked:
                selected_count += 1
                if size_item:
                    total_mb += self._size_to_mb(size_item.text())
        self.lbl_selected_summary.setText(f"Selected: {selected_count} files ({self._format_mb(total_mb)})")

    def _size_to_mb(self, size_text):
        try:
            parts = size_text.strip().split()
            if len(parts) != 2:
                return 0.0
            value = float(parts[0])
            unit = parts[1].lower()
            if unit.startswith("kb"):
                return value / 1024.0
            if unit.startswith("mb"):
                return value
            if unit.startswith("gb"):
                return value * 1024.0
        except Exception:
            return 0.0
        return 0.0

    def _format_mb(self, mb):
        if mb >= 1024:
            return f"{mb / 1024:.2f} GB"
        return f"{mb:.1f} MB"

    def back_to_chat_from_video(self):
        self.worker.cancel_scan()
        self.stack.setCurrentIndex(1)

    def on_session_corrupted(self, error_text):
        self.loader.stop()
        answer = QMessageBox.critical(
            self,
            "Session Corrupted",
            f"The Telegram session appears corrupted:\n\n{error_text}\n\nClear saved credentials and sign in again?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer == QMessageBox.Yes:
            self.worker.reset_credentials_and_session()
            self.inp_api.clear()
            self.inp_hash.clear()
            self.inp_phone.clear()
            self.stack.setCurrentIndex(0)

    def on_operation_aborted(self):
        self.is_downloading = False
        self.cnt_down = 0
        self.cnt_queue = 0
        self.row_map = {}
        self.active_table.setRowCount(0)
        self.update_header_counts()
        self.check_footer_visibility()
        self.toggle_sleep_prevention(False)
        self.btn_pause.setText("Pause Queue")
        self.queue_paused = False
        self.foot_btn_pause.setText("Pause Queue")
        self.dl_header.setText("Download")
        self._set_global_stream_text("Stopped")
        self.dl_bar.setValue(0)
        self.foot_lbl_stat.setText("0%")
        self.foot_lbl_stat.setObjectName("FooterPercent")
        self.foot_lbl_stat.style().unpolish(self.foot_lbl_stat)
        self.foot_lbl_stat.style().polish(self.foot_lbl_stat)
        self.set_download_status("Download operation aborted", "warn")
        self.update_window_title(state="idle")

    def switch_account(self):
        reply = QMessageBox.question(
            self,
            "Switch Account",
            "This will clear the saved Telegram session and credentials. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.worker.stop_task()
        self.worker.cancel_scan()
        self.worker.reset_credentials_and_session()
        self._auto_connect_attempted = False
        self.inp_api.clear()
        self.inp_hash.clear()
        self.inp_phone.clear()
        self.login_stack.setCurrentIndex(0)
        self.stack.setCurrentIndex(0)
        self.update_status("Session cleared. Enter new credentials.")

    def update_window_title(self, progress=None, state=None):
        base = "Teleflow v4"
        if state == "complete":
            self.setWindowTitle(f"{base} - Complete")
            return
        if self.is_downloading:
            if progress is None:
                progress = int(self.dl_bar.value()) if hasattr(self, "dl_bar") else 0
            total = self.cnt_down + self.cnt_queue
            done = max(0, total - self.cnt_queue)
            self.setWindowTitle(f"{base} - Downloading ({done}/{max(total,1)}) {progress}%")
            return

        page_names = {
            0: "Sign In",
            1: "Select Chat",
            2: "Media Files",
            3: "Download",
        }
        page = page_names.get(self.stack.currentIndex(), "Home")
        self.setWindowTitle(f"{base} - {page}")

    def closeEvent(self, event):
        if self.is_downloading:
            reply = QMessageBox.question(
                self,
                "Downloads In Progress",
                "Downloads are still running. Closing now will abort the queue. Exit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return
            self.worker.stop_task()
            self.worker.cancel_scan()
        event.accept()

    def decrease_concurrency(self):
        self.concurrent_limit = max(1, self.concurrent_limit - 1)
        if hasattr(self, "lbl_concurrency_value"):
            self.lbl_concurrency_value.setText(str(self.concurrent_limit))

    def increase_concurrency(self):
        self.concurrent_limit = min(10, self.concurrent_limit + 1)
        if hasattr(self, "lbl_concurrency_value"):
            self.lbl_concurrency_value.setText(str(self.concurrent_limit))

def main():
    logger.info("Launching Teleflow GUI")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app_font = QFont("Google Sans")
    app_font.setPointSize(10)
    app_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(app_font)
    loop = qasync.QEventLoop(app); asyncio.set_event_loop(loop)
    worker = TelegramWorker(); window = MainWindow(worker); window.showMaximized(); loop.create_task(worker.check_saved_data())
    with loop: loop.run_forever()

if __name__ == "__main__": main()
