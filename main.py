import sys
import os
import asyncio
import qasync
import random
import webbrowser
import ctypes
import logging
from logging.handlers import RotatingFileHandler
import subprocess

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QListWidget, QTableWidget, QTableWidgetItem, QProgressBar, 
    QFrame, QHeaderView, QLineEdit, QPushButton, QStackedWidget, 
    QAbstractItemView, QListWidgetItem, QGridLayout, QSizePolicy, QSpinBox,
    QCheckBox, QFileDialog, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QCursor, QIcon, QColor, QBrush
from core import TelegramWorker, BASE_DIR
from themes import get_theme, resolve_theme_mode
from stylesheet_builder import build_stylesheet
from assets import (DecryptLabel, HackerProgressBar, TerminalLog, CyberGraph, 
                    CyberHexStream, ScanlineOverlay, MatrixLoader, CyberLoadingOverlay)


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
        default_dl = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_path = self.settings.value("download_path", default_dl)
        saved_theme_pref = self.settings.value("theme_preference", "system")
        self.theme_preference = saved_theme_pref if saved_theme_pref in ("system", "dark", "light") else "system"
        self.theme_mode = resolve_theme_mode(self.theme_preference, QApplication.instance())
        self.theme = get_theme(self.theme_mode)
        
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

        self.scanlines = ScanlineOverlay(self.central_container, theme=self.theme)
        self.scanlines.raise_()
        self.stack = QStackedWidget(); self.global_layout.addWidget(self.stack)

        self.init_footer(); self.init_login_page(); self.init_chat_page(); self.init_video_page(); self.init_download_page()
        self.is_downloading = False; self.all_chats = []; self.current_videos = []; self.sort_reverse = False
        
        # --- LOADING OVERLAY ---
        self.loader = CyberLoadingOverlay(self.central_container, theme=self.theme)
        self.loader.raise_()
        
        self.worker.saved_creds_found.connect(self.on_creds_found)
        self.worker.request_creds.connect(lambda: self.stack.setCurrentIndex(0))
        self.worker.login_success.connect(lambda: self.stack.setCurrentIndex(1))
        self.worker.chats_loaded.connect(self.store_and_populate_chats)
        self.worker.videos_loaded.connect(self.populate_videos)
        self.worker.scan_progress.connect(self.update_scan_progress)
        self.worker.download_started.connect(self.on_dl_start)
        self.worker.download_progress.connect(self.on_dl_progress)
        self.worker.individual_progress.connect(self.update_individual_row)
        self.worker.queue_finished.connect(self.on_queue_finished)
        self.worker.auth_status.connect(self.update_status)
        self.worker.request_otp.connect(self.on_request_otp)
        self.worker.request_password.connect(self.on_request_pwd)
        self.stack.currentChanged.connect(self.check_footer_visibility)

        self.drama_timer = QTimer(self)
        self.drama_timer.timeout.connect(self.generate_drama)
        self.drama_phrases = [
            "BYPASSING SECURE LAYER...", "REROUTING PACKETS...", "HANDSHAKE: ACK_SYN...", 
            "DECRYPTING STREAM...", "PROXY CHAIN: ROTATING...", "BUFFER FLUSH INITIALIZED...",
            "TRACE: 127.0.0.1...", "DC_ID: MATCH CONFIRMED...", "INJECTING HEADER...", 
            "PACKET LOSS: COMPENSATING...", "OPTIMIZING THREADS...", "PING: 14ms...",
            "ENCRYPTION: AES-256...", "SESSION: PERSISTENT...", "UPLINK ESTABLISHED..."
        ]
        self.row_map = {} 
        self.cnt_down = 0
        self.cnt_queue = 0

        self.apply_theme(self.theme_mode)

    def resizeEvent(self, event): 
        self.scanlines.setGeometry(self.rect())
        self.loader.setGeometry(self.rect()) # KEEP OVERLAY FULL SIZE
        super().resizeEvent(event)

    def init_top_bar(self):
        bar = QFrame()
        bar.setObjectName("TopBar")
        bar.setFixedHeight(66)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title = QLabel("Teleflow v4")
        title.setObjectName("AppTitle")
        subtitle = QLabel("PROFESSIONAL TELEGRAM MEDIA MANAGEMENT")
        subtitle.setObjectName("AppSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        layout.addLayout(title_box)
        layout.addStretch()

        self.top_mode_badge = QLabel("Theme: Dark")
        self.top_mode_badge.setObjectName("MetaBadge")
        layout.addWidget(self.top_mode_badge)

        self.btn_theme_toggle = QPushButton("Toggle Theme")
        self.btn_theme_toggle.setObjectName("Secondary")
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        layout.addWidget(self.btn_theme_toggle)
        return bar

    def make_decrypt_label(self, text, size):
        label = DecryptLabel(text, size=size, theme=self.theme)
        self.decrypt_labels.append(label)
        return label

    def _sync_theme_controls(self):
        if hasattr(self, "top_mode_badge"):
            self.top_mode_badge.setText(f"Theme: {self.theme_mode.title()}")
        if hasattr(self, "theme_pref_combo"):
            blocked = self.theme_pref_combo.blockSignals(True)
            self.theme_pref_combo.setCurrentText(self.theme_preference.title())
            self.theme_pref_combo.blockSignals(blocked)
        if hasattr(self, "theme_pref_combo_login"):
            blocked = self.theme_pref_combo_login.blockSignals(True)
            self.theme_pref_combo_login.setCurrentText(self.theme_preference.title())
            self.theme_pref_combo_login.blockSignals(blocked)

    def set_theme_preference(self, mode):
        mode = mode.lower()
        if mode not in ("system", "dark", "light"):
            return
        self.theme_preference = mode
        self.settings.setValue("theme_preference", mode)
        self.settings.sync()
        self.theme_mode = resolve_theme_mode(mode, QApplication.instance())
        self.apply_theme(self.theme_mode)

    def toggle_theme(self):
        next_mode = "light" if self.theme_mode == "dark" else "dark"
        self.set_theme_preference(next_mode)

    def apply_theme(self, mode):
        self.theme_mode = mode
        self.theme = get_theme(mode)
        self.setStyleSheet(build_stylesheet(self.theme))

        for label in self.decrypt_labels:
            label.set_theme(self.theme)

        for widget_name in ["scanlines", "loader", "term_log", "graph", "hex_stream", "dl_bar", "matrix_loader"]:
            widget = getattr(self, widget_name, None)
            if widget and hasattr(widget, "set_theme"):
                widget.set_theme(self.theme)

        if hasattr(self, "lbl_manifest"):
            self.lbl_manifest.setStyleSheet(
                f"color:{self.theme['text_faint']}; font-weight:700; font-size:15px; letter-spacing:0.5px;"
            )
        if hasattr(self, "lbl_chat_types"):
            self.lbl_chat_types.setStyleSheet(
                f"color:{self.theme['text_faint']}; font-family:'Consolas'; font-size:10px; font-weight:700;"
            )
        if hasattr(self, "lbl_save_location"):
            self.lbl_save_location.setStyleSheet(f"color:{self.theme['text_muted']}; font-weight:700;")
        if hasattr(self, "lbl_threads"):
            self.lbl_threads.setStyleSheet(f"color:{self.theme['text_muted']}; font-weight:700;")
        if hasattr(self, "txt_path"):
            self.txt_path.setStyleSheet(
                f"color:{self.theme['accent']}; border:1px solid {self.theme['border']}; background:{self.theme['surface_elevated']};"
            )
        if hasattr(self, "login_guides"):
            for lbl in self.login_guides:
                lbl.setStyleSheet(f"color:{self.theme['text_muted']};")

        self._sync_theme_controls()

    # --- PAGES ---
    def init_login_page(self):
        p = QWidget()
        layout = QHBoxLayout(p)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(22)

        guide_area = QWidget()
        g_main = QVBoxLayout(guide_area)
        g_main.setAlignment(Qt.AlignCenter)

        guide_pan = QFrame()
        guide_pan.setObjectName("Panel")
        guide_pan.setMaximumWidth(460)
        guide_pan.setMinimumWidth(320)
        guide_pan.setMinimumHeight(420)

        g_ly = QVBoxLayout(guide_pan)
        g_ly.setContentsMargins(32, 28, 32, 28)
        g_ly.setSpacing(12)
        g_ly.addWidget(QLabel("UPLINK CONFIGURATION", objectName="GuideHeader", alignment=Qt.AlignLeft))
        g_ly.addWidget(QLabel("Connect once, then reuse your saved session securely.", objectName="MetaBadge"))

        steps = [
            '1. Open <a href="https://my.telegram.org">my.telegram.org</a> in your browser.',
            '2. Login with your phone number.',
            '3. Enter the code sent to your <b>Telegram App</b>.',
            '4. Click on <b>"API development tools"</b>.',
            '5. Create new app (Title: <i>MyDL</i>, Shortname: <i>dl123</i>).',
            '6. Copy the <b>api_id</b> and <b>api_hash</b>.',
            '7. Paste keys here and click <b>ESTABLISH UPLINK</b>.'
        ]
        self.login_guides = []
        for step in steps:
            lbl = QLabel(step, objectName="GuideStep")
            lbl.setOpenExternalLinks(True)
            lbl.setWordWrap(True)
            g_ly.addWidget(lbl)
            self.login_guides.append(lbl)

        g_ly.addSpacing(8)
        appearance_row = QHBoxLayout()
        appearance_row.addWidget(QLabel("Theme", objectName="MetaBadge"))
        self.theme_pref_combo_login = QComboBox()
        self.theme_pref_combo_login.addItems(["System", "Dark", "Light"])
        self.theme_pref_combo_login.setFixedWidth(140)
        self.theme_pref_combo_login.currentTextChanged.connect(lambda v: self.set_theme_preference(v.lower()))
        appearance_row.addWidget(self.theme_pref_combo_login)
        appearance_row.addStretch()
        g_ly.addLayout(appearance_row)

        g_main.addWidget(guide_pan)
        layout.addWidget(guide_area, 1)

        login_area = QWidget()
        l_main = QVBoxLayout(login_area)
        l_main.setAlignment(Qt.AlignCenter)

        login_pan = QFrame()
        login_pan.setObjectName("Panel")
        login_pan.setMaximumWidth(460)
        login_pan.setMinimumWidth(340)
        login_pan.setMinimumHeight(380)

        self.login_stack = QStackedWidget(login_pan)
        pl = QVBoxLayout(login_pan)
        pl.setContentsMargins(18, 18, 18, 18)
        pl.addWidget(self.login_stack)

        pg0 = QWidget()
        p0l = QVBoxLayout(pg0)
        p0l.setSpacing(16)
        p0l.setContentsMargins(20,20,20,20)
        p0l.addWidget(self.make_decrypt_label("SYSTEM LOGIN", size=24), alignment=Qt.AlignCenter)
        self.inp_api = QLineEdit(placeholderText="API ID"); p0l.addWidget(self.inp_api)
        self.inp_hash = QLineEdit(placeholderText="API Hash"); p0l.addWidget(self.inp_hash)
        self.inp_phone = QLineEdit(placeholderText="Phone Number"); p0l.addWidget(self.inp_phone)
        btn_con = QPushButton("ESTABLISH UPLINK"); btn_con.clicked.connect(self.do_connect); p0l.addWidget(btn_con, alignment=Qt.AlignRight)
        self.lbl_login_status = QLabel("Ready...", alignment=Qt.AlignCenter)
        self.lbl_login_status.setObjectName("MetaBadge")
        p0l.addWidget(self.lbl_login_status)
        self.login_stack.addWidget(pg0)

        pg1 = QWidget()
        p1l = QVBoxLayout(pg1)
        p1l.setSpacing(16)
        p1l.setContentsMargins(20,20,20,20)
        p1l.addWidget(self.make_decrypt_label("VERIFY CODE", size=24), alignment=Qt.AlignCenter)
        self.inp_otp = QLineEdit(placeholderText="Code"); p1l.addWidget(self.inp_otp)
        btn_otp = QPushButton("VERIFY"); btn_otp.clicked.connect(self.do_verify_otp); p1l.addWidget(btn_otp, alignment=Qt.AlignRight)
        self.login_stack.addWidget(pg1)

        pg2 = QWidget()
        p2l = QVBoxLayout(pg2)
        p2l.setSpacing(16)
        p2l.setContentsMargins(20,20,20,20)
        p2l.addWidget(self.make_decrypt_label("CLOUD PWD", size=24), alignment=Qt.AlignCenter)
        self.inp_2fa = QLineEdit(placeholderText="2FA Password"); self.inp_2fa.setEchoMode(QLineEdit.Password); p2l.addWidget(self.inp_2fa)
        btn_2fa = QPushButton("AUTHENTICATE"); btn_2fa.clicked.connect(self.do_verify_pwd); p2l.addWidget(btn_2fa, alignment=Qt.AlignRight)
        self.login_stack.addWidget(pg2)
        l_main.addWidget(login_pan)
        layout.addWidget(login_area, 1)
        self.stack.addWidget(p)

    def init_chat_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(42, 28, 42, 28); layout.setSpacing(14)
        h_ly = QHBoxLayout(); h_ly.addWidget(self.make_decrypt_label("SOURCE NODE SELECTION", size=25)); h_ly.addStretch()
        self.lbl_chat_types = QLabel("🟢 Channel | 🔵 Group | 👤 DM")
        self.lbl_chat_types.setObjectName("MetaBadge")
        h_ly.addWidget(self.lbl_chat_types); layout.addLayout(h_ly)

        f_bar = QHBoxLayout(); self.search_chats = QLineEdit(placeholderText="Search Nodes..."); self.search_chats.setFixedWidth(280); self.search_chats.textChanged.connect(self.apply_chat_filter); f_bar.addWidget(self.search_chats); f_bar.addSpacing(12)
        self.btn_all = QPushButton("ALL"); self.btn_ch = QPushButton("CHANNELS"); self.btn_gr = QPushButton("GROUPS"); self.btn_dm = QPushButton("DMs")
        for b in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]:
            b.setCheckable(True); b.setObjectName("FilterBtn"); b.setFixedWidth(100); b.clicked.connect(self.apply_chat_filter); f_bar.addWidget(b)
        self.btn_all.setChecked(True); f_bar.addStretch(); layout.addLayout(f_bar)

        list_shell = QFrame()
        list_shell.setObjectName("Panel")
        shell_layout = QVBoxLayout(list_shell)
        shell_layout.setContentsMargins(12, 12, 12, 12)
        self.chat_list = QListWidget(); self.chat_list.itemClicked.connect(self.start_chat_scan)
        shell_layout.addWidget(self.chat_list)
        layout.addWidget(list_shell)
        self.stack.addWidget(p)

    def start_chat_scan(self, item):
        self.stack.setCurrentIndex(2)
        # Switch to Matrix View
        self.list_stack.setCurrentIndex(1) 
        self.matrix_loader.set_count(0)
        asyncio.create_task(self.worker.scan_chat(item.data(Qt.UserRole)))

    def update_scan_progress(self, count):
        self.matrix_loader.set_count(count)

    def init_video_page(self):
        p = QWidget()
        layout = QVBoxLayout(p)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        layout.addWidget(self.make_decrypt_label("PAYLOAD DIRECTORY", size=20))

        sl = QHBoxLayout()
        self.search_videos = QLineEdit(placeholderText="Search Payloads...")
        self.search_videos.setFixedWidth(320)
        self.search_videos.textChanged.connect(self.refresh_video_table)
        sl.addWidget(self.search_videos)
        sl.addSpacing(10)
        self.btn_sort_new = QPushButton("NEW > OLD")
        self.btn_sort_new.setObjectName("FilterBtn")
        self.btn_sort_new.clicked.connect(lambda: self.toggle_sort(True))
        self.btn_sort_old = QPushButton("OLD > NEW")
        self.btn_sort_old.setObjectName("FilterBtn")
        self.btn_sort_old.clicked.connect(lambda: self.toggle_sort(False))
        sl.addWidget(self.btn_sort_new)
        sl.addWidget(self.btn_sort_old)

        self.chk_show_caption = QCheckBox("Show Captions")
        self.chk_show_caption.setCursor(Qt.PointingHandCursor)
        self.chk_show_caption.stateChanged.connect(self.refresh_video_table)
        sl.addWidget(self.chk_show_caption)
        sl.addStretch()
        layout.addLayout(sl)

        self.list_stack = QStackedWidget()

        self.video_table = QTableWidget(0, 4)
        self.video_table.setHorizontalHeaderLabels(["SEL", "NO", "FILENAME", "SIZE"])
        self.video_table.setAlternatingRowColors(True)
        self.video_table.setShowGrid(False)
        self.video_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.video_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.video_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.video_table.setFocusPolicy(Qt.NoFocus)
        self.video_table.verticalHeader().setVisible(False)
        self.video_table.setWordWrap(True)
        self.video_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.video_table.setColumnWidth(0, 45)
        self.video_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.video_table.setColumnWidth(1, 60)
        self.video_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.video_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.video_table.setColumnWidth(3, 100)
        self.video_table.cellDoubleClicked.connect(self.on_video_cell_double_click)
        self.list_stack.addWidget(self.video_table)

        self.matrix_loader = MatrixLoader(theme=self.theme)
        self.list_stack.addWidget(self.matrix_loader)

        layout.addWidget(self.list_stack)

        path_layout = QHBoxLayout()
        self.lbl_save_location = QLabel("SAVE LOCATION:")
        path_layout.addWidget(self.lbl_save_location)
        self.txt_path = QLineEdit(self.download_path)
        self.txt_path.setReadOnly(True)
        path_layout.addWidget(self.txt_path)
        btn_browse = QPushButton("BROWSE")
        btn_browse.setFixedSize(110, 36)
        btn_browse.setObjectName("Secondary")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        pref_layout = QHBoxLayout()
        pref_layout.addWidget(QLabel("Appearance", objectName="MetaBadge"))
        self.theme_pref_combo = QComboBox()
        self.theme_pref_combo.addItems(["System", "Dark", "Light"])
        self.theme_pref_combo.currentTextChanged.connect(lambda v: self.set_theme_preference(v.lower()))
        self.theme_pref_combo.setFixedWidth(140)
        pref_layout.addWidget(self.theme_pref_combo)
        pref_layout.addStretch()
        layout.addLayout(pref_layout)

        bl = QHBoxLayout()
        bk = QPushButton("BACK")
        bk.setObjectName("Secondary")
        bk.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_sel_all = QPushButton("SELECT ALL")
        self.btn_sel_all.setObjectName("Secondary")
        self.btn_sel_all.clicked.connect(self.toggle_select_all)
        dl = QPushButton("START DOWNLOAD")
        dl.clicked.connect(self.start_download_batch)
        self.lbl_threads = QLabel("THREADS:")
        self.spin_concurrent = QSpinBox()
        self.spin_concurrent.setRange(1, 10)
        self.spin_concurrent.setValue(3)
        self.spin_concurrent.setFixedSize(70, 36)
        bl.addWidget(bk)
        bl.addWidget(self.btn_sel_all)
        bl.addStretch()
        bl.addWidget(self.lbl_threads)
        bl.addWidget(self.spin_concurrent)
        bl.addSpacing(10)
        bl.addWidget(dl)
        layout.addLayout(bl)
        self.stack.addWidget(p)

    def _make_visual_panel(self, widget):
        b = QFrame(); b.setObjectName("Panel"); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); vl = QVBoxLayout(b); vl.setContentsMargins(0,0,0,0); vl.addWidget(widget); return b

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_path)
        if folder:
            self.download_path = folder
            self.txt_path.setText(folder)
            self.settings.setValue("download_path", folder)

    def init_download_page(self):
        p = QWidget()
        layout = QVBoxLayout(p)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        self.dl_header = self.make_decrypt_label("EXFILTRATION IN PROGRESS", size=25)
        header_row.addWidget(self.dl_header)
        header_row.addSpacing(18)
        self.chk_shutdown = QCheckBox("Auto shutdown after completion")
        self.chk_shutdown.setCursor(Qt.PointingHandCursor)
        header_row.addWidget(self.chk_shutdown)
        header_row.addStretch()
        btn_ab = QPushButton("ABORT & BACK")
        btn_ab.setObjectName("Destructive")
        btn_ab.setFixedSize(130, 34)
        btn_ab.clicked.connect(self.go_back_keep_downloading)
        header_row.addWidget(btn_ab)
        layout.addLayout(header_row)

        split_layout = QHBoxLayout()
        split_layout.setSpacing(12)

        active_frame = QFrame()
        active_frame.setObjectName("SectionPanel")
        af_lay = QVBoxLayout(active_frame)
        af_lay.setContentsMargins(16, 14, 16, 14)
        af_lay.setSpacing(10)

        hud_layout = QHBoxLayout()
        self.lbl_manifest = QLabel("LIVE DOWNLOAD MANIFEST")
        self.lbl_manifest.setObjectName("MetaBadge")
        hud_layout.addWidget(self.lbl_manifest)
        hud_layout.addStretch()
        self.lbl_active_count = QLabel("▼ ACTIVE: 0", objectName="CountGreen")
        self.lbl_queue_count = QLabel("⏳ QUEUED: 0", objectName="CountYellow")
        hud_layout.addWidget(self.lbl_active_count)
        hud_layout.addSpacing(18)
        hud_layout.addWidget(self.lbl_queue_count)
        af_lay.addLayout(hud_layout)

        self.active_table = QTableWidget(0, 5)
        self.active_table.setObjectName("ActiveStats")
        self.active_table.verticalHeader().setVisible(False)
        self.active_table.horizontalHeader().setVisible(False)
        self.active_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.active_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.active_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.active_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.active_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.active_table.setShowGrid(False)
        self.active_table.setFocusPolicy(Qt.NoFocus)
        self.active_table.setSelectionMode(QAbstractItemView.NoSelection)
        af_lay.addWidget(self.active_table)
        split_layout.addWidget(active_frame, 3)

        telemetry_frame = QFrame()
        telemetry_frame.setObjectName("SectionPanel")
        telemetry_frame.setFixedWidth(260)
        df_lay = QVBoxLayout(telemetry_frame)
        df_lay.setContentsMargins(8, 8, 8, 8)
        df_lay.setSpacing(6)

        self.term_log = TerminalLog(theme=self.theme)
        self.graph = CyberGraph(theme=self.theme)
        self.hex_stream = CyberHexStream(theme=self.theme)

        df_lay.addWidget(QLabel("SYSTEM LOGS", objectName="MetaBadge"))
        v1 = self._make_visual_panel(self.term_log)
        v1.setFixedHeight(102)
        df_lay.addWidget(v1)
        df_lay.addWidget(QLabel("NETWORK TRAFFIC", objectName="MetaBadge"))
        v2 = self._make_visual_panel(self.graph)
        v2.setFixedHeight(102)
        df_lay.addWidget(v2)
        df_lay.addWidget(QLabel("HEX STREAM", objectName="MetaBadge"))
        v3 = self._make_visual_panel(self.hex_stream)
        v3.setFixedHeight(102)
        df_lay.addWidget(v3)
        split_layout.addWidget(telemetry_frame, 1)
        layout.addLayout(split_layout)

        prog_frame = QFrame()
        prog_frame.setObjectName("SectionPanel")
        prog_frame.setFixedHeight(186)
        pf_layout = QVBoxLayout(prog_frame)
        pf_layout.setContentsMargins(20, 18, 20, 18)
        pf_layout.setSpacing(10)
        self.dl_bar = HackerProgressBar(theme=self.theme)
        pf_layout.addWidget(self.dl_bar)
        stats_g = QGridLayout()
        stats_g.setSpacing(15)
        stats_g.addWidget(self.create_stat_box("TOTAL THROUGHPUT", "0.0 MB/s", "lbl_speed"), 0, 0)
        stats_g.addWidget(self.create_stat_box("TOTAL ETA", "00:00:00", "lbl_eta"), 0, 1)
        stats_g.addWidget(self.create_stat_box("TOTAL SIZE", "0 / 0 MB", "lbl_size"), 0, 2)
        stats_g.addWidget(self.create_stat_box("PKT LOSS", "0.00%", "lbl_loss", True), 1, 0)
        stats_g.addWidget(self.create_stat_box("CIPHER", "AES-256", "lbl_enc", True), 1, 1)
        stats_g.addWidget(self.create_stat_box("DISK I/O", "ACTIVE", "lbl_disk", True), 1, 2)
        pf_layout.addLayout(stats_g)
        layout.addWidget(prog_frame)

        btn_l = QHBoxLayout()
        btn_bk = QPushButton("BACK")
        btn_bk.setObjectName("Secondary")
        btn_bk.clicked.connect(self.go_back_keep_downloading)
        self.btn_pause = QPushButton("QUEUE PAUSE")
        self.btn_pause.setObjectName("Amber")
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_st = QPushButton("STOP")
        self.btn_st.setObjectName("Destructive")
        self.btn_st.clicked.connect(self.stop_download)
        btn_l.addWidget(btn_bk)
        btn_l.addWidget(self.btn_pause)
        btn_l.addWidget(self.btn_st)
        btn_l.addStretch()
        layout.addLayout(btn_l)
        self.stack.addWidget(p)

    def init_footer(self):
        self.footer = QFrame(); self.footer.setObjectName("Footer"); self.footer.setFixedHeight(75); self.footer.hide(); layout = QHBoxLayout(self.footer); layout.setContentsMargins(20, 10, 20, 10); self.foot_lbl_name = QLabel("..."); self.foot_lbl_name.setObjectName("StatValue"); layout.addWidget(self.foot_lbl_name, 1); self.foot_lbl_stat = QLabel("0%"); self.foot_lbl_stat.setObjectName("StatValueGreen"); layout.addWidget(self.foot_lbl_stat); self.foot_btn_pause = QPushButton("QUEUE PAUSE"); self.foot_btn_pause.setObjectName("Amber"); self.foot_btn_pause.setFixedSize(135, 35); self.foot_btn_pause.clicked.connect(self.toggle_pause); layout.addWidget(self.foot_btn_pause); btn_st = QPushButton("STOP"); btn_st.setObjectName("Destructive"); btn_st.setFixedSize(80, 35); btn_st.clicked.connect(self.stop_download); layout.addWidget(btn_st); btn_ex = QPushButton("EXPAND"); btn_ex.setFixedSize(100, 35); btn_ex.clicked.connect(lambda: self.stack.setCurrentIndex(3)); layout.addWidget(btn_ex); self.global_layout.addWidget(self.footer)

    def generate_drama(self):
        phrase = random.choice(self.drama_phrases)
        colors = [self.theme["accent"], self.theme["success"], self.theme["text_muted"], self.theme["warning"]]
        self.term_log.add_entry(phrase, random.choice(colors))

    def go_back_keep_downloading(self): self.stack.setCurrentIndex(2); self.check_footer_visibility()
    def toggle_pause(self): is_p = (self.btn_pause.text() == "QUEUE PAUSE"); self.btn_pause.setText("QUEUE RESUME" if is_p else "QUEUE PAUSE"); self.foot_btn_pause.setText(self.btn_pause.text()); self.worker.set_pause(is_p); self.term_log.add_entry(f"SYSTEM: {'PAUSE' if is_p else 'RESUME'} SIGNAL RECEIVED", self.theme["warning"] if is_p else self.theme["success"])
    def stop_download(self): self.worker.stop_task(); self.term_log.add_entry("KILL SIGNAL SENT.", self.theme["danger"])
    
    def toggle_sleep_prevention(self, enable):
        try:
            if enable:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
            else:
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        except Exception:
            logger.debug("Sleep prevention toggle failed", exc_info=True)

    def update_header_counts(self):
        self.lbl_active_count.setText(f"▼ ACTIVE: {self.cnt_down}")
        self.lbl_queue_count.setText(f"⏳ QUEUED: {self.cnt_queue}")

    def start_download_batch(self):
        # 1. Show Loader
        self.loader.start("ALLOCATING THREADS...")
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
            return

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
            box.setStyleSheet(f"background-color: {self.theme['surface_alt']}; color: {self.theme['text']};")
            
            btn_skip = box.addButton("Skip Existing", QMessageBox.ActionRole)
            btn_over = box.addButton("Overwrite All", QMessageBox.ActionRole)
            btn_cancel = box.addButton(QMessageBox.Cancel)
            
            box.exec()
            
            if box.clickedButton() == btn_cancel:
                return
            elif box.clickedButton() == btn_skip:
                q = [x for x in q if x['name'] not in conflicts]
                if not q: return 
            
            # Restart loader if continuing
            self.loader.start("ALLOCATING THREADS...")
            QApplication.processEvents()
        # ----------------------

        self.stack.setCurrentIndex(3)
        limit = self.spin_concurrent.value()
        
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
        
        for i, item in enumerate(q):
            row = start_index + i
            self.row_map[item['name']] = row
            
            name_item = QTableWidgetItem(item['name'])
            name_item.setForeground(QBrush(QColor(self.theme["warning"]))) 
            self.active_table.setItem(row, 0, name_item)
            
            self.active_table.setItem(row, 1, QTableWidgetItem("PENDING"))
            self.active_table.setItem(row, 2, QTableWidgetItem("--"))
            self.active_table.setItem(row, 3, QTableWidgetItem("--"))
            self.active_table.setItem(row, 4, QTableWidgetItem("--"))
            
            for c in range(5): 
                if self.active_table.item(row,c): 
                    self.active_table.item(row,c).setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        # Hide loader before starting async task
        self.loader.stop()
        asyncio.create_task(self.worker.add_to_queue(q, limit, self.download_path))

    def on_dl_start(self, f, r): 
        if not self.is_downloading:
            self.toggle_sleep_prevention(True)
            self.drama_timer.start(800)
            
        self.is_downloading = True
        self.check_footer_visibility()
        self.foot_lbl_name.setText(f"BATCH EXFILTRATION...")
        
        self.cnt_down += 1; self.cnt_queue = max(0, self.cnt_queue - 1)
        self.update_header_counts()
        if f in self.row_map:
            row = self.row_map[f]
            self.active_table.item(row, 0).setForeground(QBrush(QColor(self.theme["success"])))
            self.active_table.item(row, 1).setText("INIT...")

    def on_dl_progress(self, n, p, s, e, ps): 
        self.dl_bar.setValue(p); self.lbl_speed.setText(s); self.lbl_eta.setText(e); self.lbl_size.setText(ps); self.foot_lbl_stat.setText(f"{p}%"); self.graph.update_value(min(100, int(p)+random.randint(-5,5))); self.lbl_loss.setText(f"0.0{random.randint(1,5)}%"); self.lbl_disk.setText(f"{random.randint(50,200)} MB/s")

    def update_individual_row(self, filename, percent, speed, eta, size):
        if filename in self.row_map:
            row = self.row_map[filename]
            self.active_table.item(row, 0).setForeground(QBrush(QColor(self.theme["success"])))
            self.active_table.item(row, 1).setText(f"{percent}%")
            self.active_table.item(row, 1).setForeground(QColor(self.theme["success"]) if percent==100 else QColor(self.theme["text"]))
            self.active_table.item(row, 2).setText(size if percent<100 else "COMPLETE")
            self.active_table.item(row, 3).setText(speed if percent<100 else "--")
            self.active_table.item(row, 4).setText(eta if percent<100 else "00:00")
            if percent == 100 and "COMPLETE" not in self.active_table.item(row, 2).text():
                 self.cnt_down = max(0, self.cnt_down - 1)
                 self.update_header_counts()

    def on_queue_finished(self): 
        self.is_downloading = False; self.check_footer_visibility(); self.dl_header.setText("BATCH COMPLETE")
        self.drama_timer.stop()
        self.term_log.add_entry("ALL OPERATIONS COMPLETE.", self.theme["text"])
        self.cnt_down = 0; self.cnt_queue = 0; self.update_header_counts()
        self.toggle_sleep_prevention(False)
        if self.chk_shutdown.isChecked():
            response = QMessageBox.question(
                self,
                "Confirm Shutdown",
                "Batch is complete. Shutdown this computer in 60 seconds?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if response == QMessageBox.Yes:
                self.term_log.add_entry("SYSTEM HALT: 60 SECONDS", self.theme["danger"])
                try:
                    subprocess.run(["shutdown", "/s", "/t", "60"], check=True)
                except Exception:
                    logger.exception("Failed to schedule shutdown")
                    QMessageBox.warning(self, "Shutdown Failed", "Could not schedule system shutdown.")
            else:
                self.term_log.add_entry("SYSTEM HALT CANCELLED.", self.theme["warning"])

    def check_footer_visibility(self): self.footer.setVisible(self.is_downloading and self.stack.currentIndex() != 3)
    def create_stat_box(self, t, v, o, g=False): 
        b = QFrame(); b.setStyleSheet("background-color: transparent; border: none;") 
        vl = QVBoxLayout(b); vl.setSpacing(0); vl.setContentsMargins(0,0,0,0)
        vl.addWidget(QLabel(t, objectName="StatTitle"))
        lb = QLabel(v, objectName="StatValueGreen" if g else "StatValue")
        vl.addWidget(lb)
        setattr(self, o, lb)
        return b

    def store_and_populate_chats(self, chats): 
        self.loader.stop() # Hide loader once data is ready
        self.all_chats = chats; self.apply_chat_filter(); self.stack.setCurrentIndex(1)
    
    def apply_chat_filter(self):
        s = self.sender(); [b.setChecked(False) for b in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm] if s and s in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]]
        if s and s in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]: s.setChecked(True)
        search_text = self.search_chats.text().lower(); self.chat_list.clear()
        for c in self.all_chats:
            t = c.get('type'); show_type = self.btn_all.isChecked() or (self.btn_ch.isChecked() and t == 'channel') or (self.btn_gr.isChecked() and t == 'group') or (self.btn_dm.isChecked() and t == 'dm')
            if show_type and search_text in c['name'].lower():
                tag = "🟢 " if t == 'channel' else "🔵 " if t == 'group' else "👤 "
                item = QListWidgetItem(f"{tag} {c['name']}"); item.setData(Qt.UserRole, c['id']); self.chat_list.addItem(item)
    
    def populate_videos(self, v): 
        self.current_videos = v
        self.list_stack.setCurrentIndex(0) # Switch back to Table View
        self.refresh_video_table()

    def toggle_sort(self, reverse_sort):
        self.current_videos.sort(key=lambda x: x['id'], reverse=reverse_sort)
        self.refresh_video_table()
    
    def refresh_video_table(self):
        self.video_table.setSortingEnabled(False)
        s_txt = self.search_videos.text().lower()
        show_captions = self.chk_show_caption.isChecked()
        target_key = 'caption' if show_captions else 'name'
        f_vids = [v for v in self.current_videos if s_txt in v[target_key].lower()]
        self.video_table.setRowCount(len(f_vids))
        for i, v in enumerate(f_vids):
            c = QTableWidgetItem()
            c.setCheckState(Qt.Unchecked)
            c.setData(Qt.UserRole, v)
            self.video_table.setItem(i, 0, c)
            num = QTableWidgetItem(str(i+1))
            num.setTextAlignment(Qt.AlignCenter)
            self.video_table.setItem(i, 1, num)
            display_text = v['caption'] if show_captions else v['name']
            item_text = QTableWidgetItem(display_text)
            item_text.setToolTip(display_text)
            self.video_table.setItem(i, 2, item_text)
            sz = QTableWidgetItem(v['size'])
            sz.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.video_table.setItem(i, 3, sz)
        self.video_table.resizeRowsToContents()

    def on_video_cell_double_click(self, row, col):
        check_item = self.video_table.item(row, 0); check_item.setCheckState(Qt.Checked if check_item.checkState() == Qt.Unchecked else Qt.Unchecked)
    def toggle_select_all(self):
        if not self.video_table.rowCount(): return
        ns = Qt.Checked if self.video_table.item(0,0).checkState() == Qt.Unchecked else Qt.Unchecked
        for i in range(self.video_table.rowCount()): self.video_table.item(i,0).setCheckState(ns)
    def on_creds_found(self, a, h, p): self.inp_api.setText(a); self.inp_hash.setText(h); self.inp_phone.setText(p)
    
    # --- AUTH METHODS WITH LOADING ---
    def do_connect(self): 
        self.loader.start("ESTABLISHING UPLINK...")
        asyncio.create_task(self.worker.connect_client(self.inp_api.text(), self.inp_hash.text(), self.inp_phone.text()))
    
    def do_verify_otp(self):
        self.loader.start("VERIFYING IDENTITY...")
        asyncio.create_task(self.worker.submit_otp(self.inp_otp.text()))
        
    def do_verify_pwd(self):
        self.loader.start("DECRYPTING...")
        asyncio.create_task(self.worker.submit_password(self.inp_2fa.text()))
        
    def on_request_otp(self):
        self.loader.stop()
        self.login_stack.setCurrentIndex(1)
        
    def on_request_pwd(self):
        self.loader.stop()
        self.login_stack.setCurrentIndex(2)

    def update_status(self, m): 
        self.loader.stop() # Stop loader on error
        self.lbl_login_status.setText(m)

def main():
    logger.info("Launching Teleflow GUI")
    app = QApplication(sys.argv); loop = qasync.QEventLoop(app); asyncio.set_event_loop(loop)
    worker = TelegramWorker(); window = MainWindow(worker); window.showMaximized(); loop.create_task(worker.check_saved_data())
    with loop: loop.run_forever()

if __name__ == "__main__": main()
