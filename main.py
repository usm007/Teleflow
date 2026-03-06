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
    QCheckBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QCursor, QIcon, QColor, QBrush
from core import TelegramWorker, BASE_DIR
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
    myappid = u'teleflow.downloader.pro.v3' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    logger.debug("Could not set AppUserModelID", exc_info=True)

STYLESHEET = """
    QMainWindow { background-color: #121212; }
    QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
    QLineEdit { 
        background-color: #1e1e1e; border: 1px solid #333; border-radius: 4px;
        color: white; padding: 12px; font-family: 'Consolas', monospace; font-size: 13px;
    }
    QLineEdit:focus { border: 1px solid #4caf50; background-color: #252526; }
    QFrame#Panel { background-color: #1e1e1e; border: 1px solid #333; border-radius: 6px; }
    QFrame#Footer { background-color: #0f0f0f; border-top: 1px solid #333; }
    
    QFrame#SectionPanel {
        background-color: #161616;
        border: 1px solid #333;
        border-radius: 6px;
    }
    
    QLabel#GuideHeader { color: #4caf50; font-weight: bold; font-size: 18px; margin-bottom: 15px; }
    QLabel#GuideStep { color: #aaa; font-size: 13px; line-height: 1.6; }
    
    QListWidget { background-color: #1e1e1e; border: 1px solid #333; border-radius: 6px; color: #ddd; outline: none; }
    QListWidget::item { padding: 12px; border-bottom: 1px solid #252526; }
    QListWidget::item:selected { background-color: #2d362e; border-left: 4px solid #4caf50; color: white; }
    
    /* --- CLEAN VIDEO LIST --- */
    QTableWidget { 
        background-color: #121212; 
        border: none; 
        gridline-color: transparent; 
        color: #888; 
        outline: none; 
        selection-background-color: transparent; 
        selection-color: #fff; 
    }
    QTableWidget::item { 
        padding: 8px; 
        border-bottom: 1px solid #1a1a1a; 
    }
    QTableWidget::item:hover {
        background-color: #161616; 
        color: #ffffff; 
    }
    QTableWidget::item:selected {
        background-color: transparent; 
        color: #ffffff; 
    }
    
    QTableWidget::indicator { width: 14px; height: 14px; border: 1px solid #555; border-radius: 2px; background: transparent; }
    QTableWidget::indicator:checked { background-color: #4caf50; border: 1px solid #4caf50; }
    
    QHeaderView::section { background-color: #121212; color: #555; border: none; border-bottom: 1px solid #333; padding: 10px; font-weight: bold; text-transform: uppercase; font-size: 10px; }

    QPushButton { background-color: #2e7d32; color: white; border: none; padding: 10px 20px; font-weight: 600; border-radius: 4px; }
    QPushButton:hover { background-color: #388e3c; }
    QPushButton#Secondary { background-color: #333; color: #ccc; }
    QPushButton#Destructive { background-color: #b71c1c; color: white; }
    QPushButton#Amber { background-color: #ff8f00; color: black; }
    
    QPushButton#FilterBtn { background-color: #222; color: #666; border: 1px solid #333; font-size: 11px; }
    QPushButton#FilterBtn:checked { background-color: #222; color: #4caf50; border: 1px solid #4caf50; }
    QPushButton#FilterBtn:hover { border: 1px solid #555; color: #aaa; }
    
    QSpinBox { background-color: #1e1e1e; border: 1px solid #333; color: #4caf50; padding: 5px; font-weight: bold; font-family: 'Consolas'; }
    QSpinBox::up-button, QSpinBox::down-button { background-color: #333; width: 20px; }
    
    QCheckBox { color: #888; font-weight: bold; spacing: 8px; font-family: 'Segoe UI'; font-size: 13px; }
    QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #555; border-radius: 4px; background: #111; }
    QCheckBox::indicator:checked { background: #4caf50; border: 1px solid #4caf50; }
    QCheckBox:checked { color: #4caf50; }
    
    /* --- SCROLLBAR --- */
    QScrollBar:vertical { border: none; background: #0f0f0f; width: 10px; margin: 0px 0px 0px 0px; }
    QScrollBar::handle:vertical { background: #333; min-height: 20px; border-radius: 5px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

    QLabel#StatTitle { color: #bbbbbb; font-size: 10px; font-weight: bold; letter-spacing: 0.5px; }
    QLabel#StatValue { color: #ffffff; font-family: 'Consolas'; font-size: 12px; }
    QLabel#StatValueGreen { color: #4caf50; font-size: 12px; font-family: 'Consolas'; font-weight: bold; }
    
    QTableWidget#ActiveStats { 
        background-color: #0f0f0f; 
        border: none; 
        font-family: 'Consolas'; 
        font-size: 15px; 
        font-weight: bold;
        selection-background-color: transparent;
    }
    QTableWidget#ActiveStats::item { 
        padding-left: 10px; padding-right: 10px; 
        color: #eee; 
        border-bottom: 1px solid #222; 
    }

    QLabel#CountGreen { color: #4caf50; font-family: 'Consolas'; font-size: 16px; font-weight: 900; letter-spacing: 1px; }
    QLabel#CountYellow { color: #ffca28; font-family: 'Consolas'; font-size: 16px; font-weight: 900; letter-spacing: 1px; }
"""

class MainWindow(QMainWindow):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setWindowIcon(QIcon(resource_path("icon.ico"))) 
        self.setWindowTitle("TELEFLOW v3.0 GUI")
        self.resize(1000, 700) 
        
        # Load Settings (Last Download Path)
        self.settings = QSettings("Teleflow", "Downloader")
        default_dl = os.path.join(os.path.expanduser("~"), "Downloads")
        self.download_path = self.settings.value("download_path", default_dl)
        
        center = QApplication.primaryScreen().availableGeometry().center()
        frame_geo = self.frameGeometry()
        frame_geo.moveCenter(center)
        self.move(frame_geo.topLeft())
        
        self.setStyleSheet(STYLESHEET)
        
        self.central_container = QWidget(); self.setCentralWidget(self.central_container)
        self.global_layout = QVBoxLayout(self.central_container); self.global_layout.setContentsMargins(0,0,0,0)
        self.scanlines = ScanlineOverlay(self.central_container); self.scanlines.raise_()
        self.stack = QStackedWidget(); self.global_layout.addWidget(self.stack)

        self.init_footer(); self.init_login_page(); self.init_chat_page(); self.init_video_page(); self.init_download_page()
        self.is_downloading = False; self.all_chats = []; self.current_videos = []; self.sort_reverse = False
        
        # --- LOADING OVERLAY ---
        self.loader = CyberLoadingOverlay(self.central_container)
        
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

    def resizeEvent(self, event): 
        self.scanlines.setGeometry(self.rect())
        self.loader.setGeometry(self.rect()) # KEEP OVERLAY FULL SIZE
        super().resizeEvent(event)

    # --- PAGES ---
    def init_login_page(self):
        p = QWidget(); layout = QHBoxLayout(p); layout.setContentsMargins(30, 0, 30, 0); layout.setSpacing(0)
        guide_area = QWidget(); g_main = QVBoxLayout(guide_area); g_main.setAlignment(Qt.AlignCenter)
        guide_pan = QFrame(); guide_pan.setObjectName("Panel")
        
        guide_pan.setMaximumWidth(420); guide_pan.setMinimumWidth(300); guide_pan.setMinimumHeight(350)
        
        g_ly = QVBoxLayout(guide_pan); g_ly.setContentsMargins(40, 40, 40, 40); g_ly.setSpacing(15)
        g_ly.addWidget(QLabel("UPLINK CONFIGURATION", objectName="GuideHeader", alignment=Qt.AlignLeft))
        steps = [
            '1. Open <a href="https://my.telegram.org" style="color: #4caf50;">my.telegram.org</a> in your browser.',
            '2. Login with your phone number.',
            '3. Enter the code sent to your <b>Telegram App</b>.',
            '4. Click on <b>"API development tools"</b>.',
            '5. Create new app (Title: <i>MyDL</i>, Shortname: <i>dl123</i>).',
            '6. Copy the <b>api_id</b> and <b>api_hash</b>.',
            '7. Paste keys here and click <b>ESTABLISH UPLINK</b>.'
        ]
        for step in steps:
            lbl = QLabel(step, objectName="GuideStep")
            lbl.setOpenExternalLinks(True); lbl.setWordWrap(True); g_ly.addWidget(lbl)
        g_main.addWidget(guide_pan); layout.addWidget(guide_area, 1)

        login_area = QWidget(); l_main = QVBoxLayout(login_area); l_main.setAlignment(Qt.AlignCenter)
        login_pan = QFrame(); login_pan.setObjectName("Panel")
        
        login_pan.setMaximumWidth(420); login_pan.setMinimumWidth(300); login_pan.setMinimumHeight(320)
        
        self.login_stack = QStackedWidget(login_pan); pl = QVBoxLayout(login_pan); pl.addWidget(self.login_stack)
        
        pg0 = QWidget(); p0l = QVBoxLayout(pg0); p0l.setSpacing(20); p0l.setContentsMargins(20,20,20,20)
        p0l.addWidget(DecryptLabel("SYSTEM LOGIN", size=24), alignment=Qt.AlignCenter)
        self.inp_api = QLineEdit(placeholderText="API ID"); p0l.addWidget(self.inp_api)
        self.inp_hash = QLineEdit(placeholderText="API Hash"); p0l.addWidget(self.inp_hash)
        self.inp_phone = QLineEdit(placeholderText="Phone Number"); p0l.addWidget(self.inp_phone)
        btn_con = QPushButton("ESTABLISH UPLINK"); btn_con.clicked.connect(self.do_connect); p0l.addWidget(btn_con)
        self.lbl_login_status = QLabel("Ready...", alignment=Qt.AlignCenter); p0l.addWidget(self.lbl_login_status)
        self.login_stack.addWidget(pg0)
        
        pg1 = QWidget(); p1l = QVBoxLayout(pg1); p1l.setSpacing(20); p1l.setContentsMargins(20,20,20,20)
        p1l.addWidget(DecryptLabel("VERIFY CODE", size=24), alignment=Qt.AlignCenter)
        self.inp_otp = QLineEdit(placeholderText="Code"); p1l.addWidget(self.inp_otp)
        btn_otp = QPushButton("VERIFY"); btn_otp.clicked.connect(self.do_verify_otp); p1l.addWidget(btn_otp)
        self.login_stack.addWidget(pg1)

        pg2 = QWidget(); p2l = QVBoxLayout(pg2); p2l.setSpacing(20); p2l.setContentsMargins(20,20,20,20)
        p2l.addWidget(DecryptLabel("CLOUD PWD", size=24), alignment=Qt.AlignCenter)
        self.inp_2fa = QLineEdit(placeholderText="2FA Password"); self.inp_2fa.setEchoMode(QLineEdit.Password); p2l.addWidget(self.inp_2fa)
        btn_2fa = QPushButton("AUTHENTICATE"); btn_2fa.clicked.connect(self.do_verify_pwd); p2l.addWidget(btn_2fa)
        self.login_stack.addWidget(pg2)
        l_main.addWidget(login_pan); layout.addWidget(login_area, 1); self.stack.addWidget(p)

    def init_chat_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(50,50,50,50)
        h_ly = QHBoxLayout(); h_ly.addWidget(DecryptLabel("SOURCE NODE SELECTION", size=25)); h_ly.addStretch()
        h_ly.addWidget(QLabel("🟢 Channel | 🔵 Group | 👤 DM", styleSheet="color:#888; font-family:'Consolas'; font-size:10px; font-weight:bold;")); layout.addLayout(h_ly)
        f_bar = QHBoxLayout(); self.search_chats = QLineEdit(placeholderText="Search Nodes..."); self.search_chats.setFixedWidth(250); self.search_chats.textChanged.connect(self.apply_chat_filter); f_bar.addWidget(self.search_chats); f_bar.addSpacing(20)
        self.btn_all = QPushButton("ALL"); self.btn_ch = QPushButton("CHANNELS"); self.btn_gr = QPushButton("GROUPS"); self.btn_dm = QPushButton("DMs")
        for b in [self.btn_all, self.btn_ch, self.btn_gr, self.btn_dm]:
            b.setCheckable(True); b.setObjectName("FilterBtn"); b.setFixedWidth(100); b.clicked.connect(self.apply_chat_filter); f_bar.addWidget(b)
        self.btn_all.setChecked(True); f_bar.addStretch(); layout.addLayout(f_bar)
        self.chat_list = QListWidget(); self.chat_list.itemClicked.connect(self.start_chat_scan); layout.addWidget(self.chat_list); self.stack.addWidget(p)

    def start_chat_scan(self, item):
        self.stack.setCurrentIndex(2)
        # Switch to Matrix View
        self.list_stack.setCurrentIndex(1) 
        self.matrix_loader.set_count(0)
        asyncio.create_task(self.worker.scan_chat(item.data(Qt.UserRole)))

    def update_scan_progress(self, count):
        self.matrix_loader.set_count(count)

    def init_video_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(40,40,40,40); layout.addWidget(DecryptLabel("PAYLOAD DIRECTORY", size=20))
        
        sl = QHBoxLayout(); self.search_videos = QLineEdit(placeholderText="Search Payloads..."); self.search_videos.setFixedWidth(300); self.search_videos.textChanged.connect(self.refresh_video_table); sl.addWidget(self.search_videos); sl.addSpacing(20)
        self.btn_sort_new = QPushButton("FILTER: NEW > OLD"); self.btn_sort_new.setObjectName("FilterBtn"); self.btn_sort_new.clicked.connect(lambda: self.toggle_sort(True))
        self.btn_sort_old = QPushButton("FILTER: OLD > NEW"); self.btn_sort_old.setObjectName("FilterBtn"); self.btn_sort_old.clicked.connect(lambda: self.toggle_sort(False))
        sl.addWidget(self.btn_sort_new); sl.addSpacing(5); sl.addWidget(self.btn_sort_old)
        sl.addSpacing(20)
        self.chk_show_caption = QCheckBox("SHOW CAPTIONS")
        self.chk_show_caption.setCursor(Qt.PointingHandCursor)
        self.chk_show_caption.stateChanged.connect(self.refresh_video_table)
        sl.addWidget(self.chk_show_caption)
        sl.addStretch(); layout.addLayout(sl)
        
        self.list_stack = QStackedWidget()
        
        # 1. TABLE VIEW
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
        
        # 2. MATRIX VIEW
        self.matrix_loader = MatrixLoader()
        self.list_stack.addWidget(self.matrix_loader)
        
        layout.addWidget(self.list_stack)
        
        # --- NEW: FOLDER SELECTION ---
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("SAVE LOCATION:", styleSheet="color:#aaa; font-weight:bold;"))
        self.txt_path = QLineEdit(self.download_path)
        self.txt_path.setReadOnly(True)
        self.txt_path.setStyleSheet("color:#4caf50; border:1px solid #333; background:#111;")
        path_layout.addWidget(self.txt_path)
        btn_browse = QPushButton("BROWSE")
        btn_browse.setFixedSize(100, 35)
        btn_browse.setObjectName("Secondary")
        btn_browse.clicked.connect(self.browse_folder)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)
        layout.addSpacing(10)
        
        bl = QHBoxLayout(); bk = QPushButton("BACK"); bk.setObjectName("Secondary"); bk.clicked.connect(lambda: self.stack.setCurrentIndex(1)); self.btn_sel_all = QPushButton("SELECT ALL"); self.btn_sel_all.setObjectName("Secondary"); self.btn_sel_all.clicked.connect(self.toggle_select_all); dl = QPushButton("START EXFILTRATION"); dl.clicked.connect(self.start_download_batch); t_lbl = QLabel("THREADS:"); t_lbl.setStyleSheet("color:#aaa; font-weight:bold;"); self.spin_concurrent = QSpinBox(); self.spin_concurrent.setRange(1, 10); self.spin_concurrent.setValue(3); self.spin_concurrent.setFixedSize(60, 35); bl.addWidget(bk); bl.addWidget(self.btn_sel_all); bl.addStretch(); bl.addWidget(t_lbl); bl.addWidget(self.spin_concurrent); bl.addSpacing(10); bl.addWidget(dl); layout.addLayout(bl); self.stack.addWidget(p)

    def _make_visual_panel(self, widget):
        b = QFrame(); b.setObjectName("Panel"); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); vl = QVBoxLayout(b); vl.setContentsMargins(0,0,0,0); vl.addWidget(widget); return b

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder", self.download_path)
        if folder:
            self.download_path = folder
            self.txt_path.setText(folder)
            self.settings.setValue("download_path", folder)

    def init_download_page(self):
        p = QWidget(); layout = QVBoxLayout(p); layout.setContentsMargins(30, 30, 30, 30)
        
        h_l = QHBoxLayout()
        self.dl_header = DecryptLabel("EXFILTRATION IN PROGRESS", size=25)
        h_l.addWidget(self.dl_header); h_l.addSpacing(25)
        self.chk_shutdown = QCheckBox("AUTO SHUTDOWN on Mission Completion")
        self.chk_shutdown.setCursor(Qt.PointingHandCursor)
        h_l.addWidget(self.chk_shutdown); h_l.addStretch()
        btn_ab = QPushButton("ABORT & BACK"); btn_ab.setObjectName("Destructive"); btn_ab.setFixedSize(120, 30); btn_ab.clicked.connect(self.go_back_keep_downloading)
        h_l.addWidget(btn_ab); layout.addLayout(h_l)
        
        split_layout = QHBoxLayout(); split_layout.setSpacing(10)
        active_frame = QFrame(); active_frame.setObjectName("SectionPanel")
        af_lay = QVBoxLayout(active_frame); af_lay.setContentsMargins(15,15,15,15)
        hud_layout = QHBoxLayout()
        lbl_manifest = QLabel(">> UPLINK MANIFEST"); lbl_manifest.setStyleSheet("color:#888; font-weight:bold; font-size:16px; letter-spacing:1px;") 
        hud_layout.addWidget(lbl_manifest); hud_layout.addStretch() 
        self.lbl_active_count = QLabel("▼ ACTIVE: 0", objectName="CountGreen")
        self.lbl_queue_count = QLabel("⏳ QUEUED: 0", objectName="CountYellow")
        hud_layout.addWidget(self.lbl_active_count); hud_layout.addSpacing(25); hud_layout.addWidget(self.lbl_queue_count)
        af_lay.addLayout(hud_layout)
        
        self.active_table = QTableWidget(0, 5); self.active_table.setObjectName("ActiveStats")
        self.active_table.verticalHeader().setVisible(False); self.active_table.horizontalHeader().setVisible(False)
        
        self.active_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.active_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # Percent
        self.active_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents) # Size
        self.active_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents) # Speed
        self.active_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # ETA
        
        self.active_table.setShowGrid(False)
        self.active_table.setFocusPolicy(Qt.NoFocus); self.active_table.setSelectionMode(QAbstractItemView.NoSelection)
        af_lay.addWidget(self.active_table); split_layout.addWidget(active_frame, 3) 

        drama_frame = QFrame(); drama_frame.setObjectName("SectionPanel"); drama_frame.setFixedWidth(240)
        df_lay = QVBoxLayout(drama_frame); df_lay.setContentsMargins(5,5,5,5); df_lay.setSpacing(5)
        self.term_log = TerminalLog(); self.graph = CyberGraph(); self.hex_stream = CyberHexStream()
        df_lay.addWidget(QLabel(">> SYSTEM LOGS", styleSheet="color:#aaa; font-size:8px; font-weight:bold; margin-left:5px;"))
        v1 = self._make_visual_panel(self.term_log); v1.setFixedHeight(100); df_lay.addWidget(v1)
        df_lay.addWidget(QLabel(">> NETWORK TRAFFIC", styleSheet="color:#aaa; font-size:8px; font-weight:bold; margin-left:5px;"))
        v2 = self._make_visual_panel(self.graph); v2.setFixedHeight(100); df_lay.addWidget(v2)
        df_lay.addWidget(QLabel(">> HEX STREAM", styleSheet="color:#aaa; font-size:8px; font-weight:bold; margin-left:5px;"))
        v3 = self._make_visual_panel(self.hex_stream); v3.setFixedHeight(100); df_lay.addWidget(v3)
        split_layout.addWidget(drama_frame, 1); layout.addLayout(split_layout)

        prog_frame = QFrame(); prog_frame.setObjectName("SectionPanel"); prog_frame.setFixedHeight(180)
        pf_layout = QVBoxLayout(prog_frame); pf_layout.setContentsMargins(20,20,20,20)
        self.dl_bar = HackerProgressBar(); pf_layout.addWidget(self.dl_bar)
        stats_g = QGridLayout(); stats_g.setSpacing(15)
        stats_g.addWidget(self.create_stat_box("TOTAL THROUGHPUT", "0.0 MB/s", "lbl_speed"), 0, 0)
        stats_g.addWidget(self.create_stat_box("TOTAL ETA", "00:00:00", "lbl_eta"), 0, 1)
        stats_g.addWidget(self.create_stat_box("TOTAL SIZE", "0 / 0 MB", "lbl_size"), 0, 2)
        stats_g.addWidget(self.create_stat_box("PKT_LOSS", "0.00%", "lbl_loss", True), 1, 0)
        stats_g.addWidget(self.create_stat_box("CYPHER", "AES-256", "lbl_enc", True), 1, 1)
        stats_g.addWidget(self.create_stat_box("DISK_I/O", "ACTIVE", "lbl_disk", True), 1, 2)
        pf_layout.addLayout(stats_g); layout.addWidget(prog_frame)
        
        btn_l = QHBoxLayout(); btn_bk = QPushButton("BACK"); btn_bk.setObjectName("Secondary"); btn_bk.clicked.connect(self.go_back_keep_downloading); self.btn_pause = QPushButton("QUEUE PAUSE"); self.btn_pause.setObjectName("Amber"); self.btn_pause.clicked.connect(self.toggle_pause); self.btn_st = QPushButton("STOP"); self.btn_st.setObjectName("Destructive"); self.btn_st.clicked.connect(self.stop_download)
        btn_l.addWidget(btn_bk); btn_l.addWidget(self.btn_pause); btn_l.addWidget(self.btn_st); layout.addLayout(btn_l); self.stack.addWidget(p)

    def init_footer(self):
        self.footer = QFrame(); self.footer.setObjectName("Footer"); self.footer.setFixedHeight(75); self.footer.hide(); layout = QHBoxLayout(self.footer); layout.setContentsMargins(20, 10, 20, 10); self.foot_lbl_name = QLabel("..."); self.foot_lbl_name.setStyleSheet("font-weight: bold; color: white;"); layout.addWidget(self.foot_lbl_name, 1); self.foot_lbl_stat = QLabel("0%"); layout.addWidget(self.foot_lbl_stat); self.foot_btn_pause = QPushButton("QUEUE PAUSE"); self.foot_btn_pause.setObjectName("Amber"); self.foot_btn_pause.setFixedSize(135, 35); self.foot_btn_pause.clicked.connect(self.toggle_pause); layout.addWidget(self.foot_btn_pause); btn_st = QPushButton("STOP"); btn_st.setObjectName("Destructive"); btn_st.setFixedSize(80, 35); btn_st.clicked.connect(self.stop_download); layout.addWidget(btn_st); btn_ex = QPushButton("EXPAND"); btn_ex.setFixedSize(100, 35); btn_ex.clicked.connect(lambda: self.stack.setCurrentIndex(3)); layout.addWidget(btn_ex); self.global_layout.addWidget(self.footer)

    def generate_drama(self):
        phrase = random.choice(self.drama_phrases)
        colors = ["#4caf50", "#00ff41", "#008f11", "#a2ff00"]
        self.term_log.add_entry(phrase, random.choice(colors))

    def go_back_keep_downloading(self): self.stack.setCurrentIndex(2); self.check_footer_visibility()
    def toggle_pause(self): is_p = (self.btn_pause.text() == "QUEUE PAUSE"); self.btn_pause.setText("QUEUE RESUME" if is_p else "QUEUE PAUSE"); self.foot_btn_pause.setText(self.btn_pause.text()); self.worker.set_pause(is_p); self.term_log.add_entry(f"SYSTEM: {'PAUSE' if is_p else 'RESUME'} SIGNAL RECEIVED", "#ff8f00" if is_p else "#00ff41")
    def stop_download(self): self.worker.stop_task(); self.term_log.add_entry("KILL SIGNAL SENT.", "#b71c1c")
    
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
            box.setStyleSheet("background-color: #222; color: #eee;")
            
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
            name_item.setForeground(QBrush(QColor("#ffca28"))) 
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
            self.active_table.item(row, 0).setForeground(QBrush(QColor("#4caf50")))
            self.active_table.item(row, 1).setText("INIT...")

    def on_dl_progress(self, n, p, s, e, ps): 
        self.dl_bar.setValue(p); self.lbl_speed.setText(s); self.lbl_eta.setText(e); self.lbl_size.setText(ps); self.foot_lbl_stat.setText(f"{p}%"); self.graph.update_value(min(100, int(p)+random.randint(-5,5))); self.lbl_loss.setText(f"0.0{random.randint(1,5)}%"); self.lbl_disk.setText(f"{random.randint(50,200)} MB/s")

    def update_individual_row(self, filename, percent, speed, eta, size):
        if filename in self.row_map:
            row = self.row_map[filename]
            self.active_table.item(row, 0).setForeground(QBrush(QColor("#4caf50")))
            self.active_table.item(row, 1).setText(f"{percent}%")
            self.active_table.item(row, 1).setForeground(QColor("#4caf50") if percent==100 else QColor("#ffffff"))
            self.active_table.item(row, 2).setText(size if percent<100 else "COMPLETE")
            self.active_table.item(row, 3).setText(speed if percent<100 else "--")
            self.active_table.item(row, 4).setText(eta if percent<100 else "00:00")
            if percent == 100 and "COMPLETE" not in self.active_table.item(row, 2).text():
                 self.cnt_down = max(0, self.cnt_down - 1)
                 self.update_header_counts()

    def on_queue_finished(self): 
        self.is_downloading = False; self.check_footer_visibility(); self.dl_header.setText("BATCH COMPLETE")
        self.drama_timer.stop()
        self.term_log.add_entry("ALL OPERATIONS COMPLETE.", "#ffffff")
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
                self.term_log.add_entry("SYSTEM HALT: 60 SECONDS", "#b71c1c")
                try:
                    subprocess.run(["shutdown", "/s", "/t", "60"], check=True)
                except Exception:
                    logger.exception("Failed to schedule shutdown")
                    QMessageBox.warning(self, "Shutdown Failed", "Could not schedule system shutdown.")
            else:
                self.term_log.add_entry("SYSTEM HALT CANCELLED.", "#ffca28")

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
