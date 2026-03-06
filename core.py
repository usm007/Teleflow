import os
import ctypes
import asyncio
import time
import re
import logging
import shutil
from telethon import TelegramClient, errors
from telethon.tl.types import DocumentAttributeVideo, InputMessagesFilterVideo
from PySide6.QtCore import QObject, Signal

# --- CONFIG ---
SESSION_NAME = "video_downloader"


def _resolve_base_dir():
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return os.path.join(appdata, "Teleflow")
    return os.path.expanduser("~/.tbtgdl")


BASE_DIR = _resolve_base_dir()
CRED_FILE = os.path.join(BASE_DIR, "credentials.txt")
SESSION_PATH = os.path.join(BASE_DIR, SESSION_NAME)

logger = logging.getLogger("teleflow")

class TelegramWorker(QObject):
    auth_status = Signal(str)
    request_creds = Signal()
    saved_creds_found = Signal(str, str, str)
    request_otp = Signal()
    request_password = Signal()
    login_success = Signal()
    session_corrupted = Signal(str)
    chats_loaded = Signal(list)
    videos_loaded = Signal(list)
    download_started = Signal(str, list)
    
    # Real-time scan counter
    scan_progress = Signal(int) 
    
    # Global Batch Progress
    download_progress = Signal(str, int, str, str, str) 
    
    # Individual Stats
    individual_progress = Signal(str, int, str, str, str)
    
    queue_finished = Signal()
    operation_aborted = Signal()

    def __init__(self):
        super().__init__()
        self._ensure_runtime_dir()
        self._migrate_legacy_files()
        self.client = None
        self.phone = None
        self.is_paused = False
        self.is_cancelled = False
        self.is_running = False
        
        # Queue Management
        self._download_queue = asyncio.Queue()
        self._active_tasks = set()
        self._batch_total_size = 0
        self._file_progress = {}
        self._global_start_time = 0
        
    def set_pause(self, paused: bool):
        self.is_paused = paused

    def stop_task(self):
        self.is_cancelled = True

    # --- AUTH & SCANNING (Unchanged) ---
    async def check_saved_data(self):
        api_id, api_hash, phone = self._load_credentials()
        if api_id and api_hash and phone:
            self.phone = phone
            self.saved_creds_found.emit(api_id, api_hash, phone)
        else:
            self.request_creds.emit()

    async def connect_client(self, api_id, api_hash, phone):
        self._save_credentials(api_id, api_hash, phone)
        self.phone = phone
        try:
            self.client = TelegramClient(SESSION_PATH, int(api_id), api_hash)
            await self.client.connect()
        except Exception as e:
            logger.exception("Failed to connect Telegram client")
            self.session_corrupted.emit(str(e)); return

        if not await self.client.is_user_authorized():
            try:
                await self.client.send_code_request(self.phone)
                self.request_otp.emit()
            except Exception as e:
                logger.exception("Failed to request OTP")
                self.auth_status.emit(f"AUTH ERROR: {e}")
        else:
            self.login_success.emit()
            await self.fetch_dialogs()

    async def submit_otp(self, code):
        try:
            await self.client.sign_in(self.phone, code)
            self.login_success.emit()
            await self.fetch_dialogs()
        except errors.SessionPasswordNeededError:
            self.request_password.emit()
        except Exception as e:
            logger.exception("OTP submission failed")
            self.auth_status.emit(f"ERROR: {e}")

    async def submit_password(self, password):
        try:
            await self.client.sign_in(password=password)
            self.login_success.emit()
            await self.fetch_dialogs()
        except Exception as e:
            logger.exception("Password submission failed")
            self.auth_status.emit(f"ERROR: {e}")

    async def fetch_dialogs(self):
        dialogs = await self.client.get_dialogs(limit=None)
        chat_list = []
        for d in dialogs:
            c_type = "dm"
            if d.is_channel:
                c_type = "channel" if d.entity.broadcast else "group"
            elif d.is_group:
                c_type = "group"
            chat_list.append({"id": d.id, "name": d.name, "type": c_type})
        self.chats_loaded.emit(chat_list)

    def _sanitize_filename(self, name):
        clean_name = re.sub(r'[\\/*?:"<>|]', "", name)
        clean_name = clean_name.strip()
        return clean_name if clean_name else "unnamed_file"

    async def scan_chat(self, chat_id):
        videos = []
        video_count = 0
        self.scan_progress.emit(0) 
        
        try:
            entity = await self.client.get_entity(chat_id)
            async for msg in self.client.iter_messages(entity, limit=None, filter=InputMessagesFilterVideo):
                if msg.media and hasattr(msg.media, 'document'):
                    if any(isinstance(x, DocumentAttributeVideo) for x in msg.media.document.attributes):
                        size_mb = msg.media.document.size / (1024 * 1024)
                        
                        original_name = msg.file.name or f"video.mp4"
                        safe_name = self._sanitize_filename(original_name)
                        filename = f"{msg.id}_{safe_name}"
                        
                        raw_caption = msg.text or ""
                        clean_caption = raw_caption.replace('\n', ' ').strip()
                        display_caption = clean_caption if clean_caption else safe_name
                        
                        videos.append({
                            "id": msg.id, 
                            "name": filename,
                            "caption": display_caption, 
                            "size": f"{size_mb:.2f} MB", 
                            "msg": msg
                        })
                        
                        video_count += 1
                        if video_count % 10 == 0: 
                            self.scan_progress.emit(video_count)

            self.scan_progress.emit(video_count)
            self.videos_loaded.emit(videos)
            
        except Exception as e:
            logger.exception("Scan failed for chat_id=%s", chat_id)
            self.auth_status.emit(f"SCAN ERROR: {e}")

    # --- DYNAMIC DOWNLOAD QUEUE ---
    
    async def add_to_queue(self, new_items, concurrent_limit, save_path):
        """Adds items to the queue. Starts the processor if not running."""
        # 1. Update Global Stats
        for item in new_items:
            self._batch_total_size += item['msg'].file.size
            self._file_progress[item['name']] = 0
            await self._download_queue.put(item)

        # 2. Start Processor if idle
        if not self.is_running:
            self.is_cancelled = False
            self.is_paused = False
            self.is_running = True
            self._global_start_time = time.time()
            asyncio.create_task(self._queue_processor(concurrent_limit, save_path))

    async def _queue_processor(self, concurrent_limit, save_path):
        os.makedirs(save_path, exist_ok=True)
        sem = asyncio.Semaphore(concurrent_limit)

        while True:
            # Check for cancellation
            if self.is_cancelled:
                self.operation_aborted.emit()
                self.is_running = False
                # Drain queue
                while not self._download_queue.empty():
                    self._download_queue.get_nowait()
                return

            # Check if finished (Queue empty AND no active tasks)
            if self._download_queue.empty() and not self._active_tasks:
                self.queue_finished.emit()
                self.is_running = False
                # Reset stats for next clean run
                self._batch_total_size = 0
                self._file_progress = {}
                return
            
            # Wait for pause
            if self.is_paused:
                await asyncio.sleep(1)
                continue

            # Fetch new task if semaphore available
            if not self._download_queue.empty():
                item = await self._download_queue.get()
                
                # Create Task
                task = asyncio.create_task(
                    self._download_worker(item, save_path, sem)
                )
                self._active_tasks.add(task)
                task.add_done_callback(self._active_tasks.discard)
            
            # Small sleep to yield control
            await asyncio.sleep(0.1)

    async def _download_worker(self, item, save_path, sem):
        filename = item['name']
        file_size = item['msg'].file.size
        path = os.path.join(save_path, filename)
        
        ind_start_time = time.time()
        last_emit_time = 0 
        
        async with sem:
            if self.is_cancelled: return
            
            self.download_started.emit(filename, [])
            ind_start_time = time.time()

            def progress_callback(current, total):
                nonlocal last_emit_time
                if self.is_cancelled: raise Exception("MANUAL_ABORT")
                
                # Check pause inside the download loop
                while self.is_paused:
                    time.sleep(1) # Blocking sleep is okay inside telethon callback, or use error to break
                    if self.is_cancelled: raise Exception("MANUAL_ABORT")

                current_time = time.time()
                if (current_time - last_emit_time < 0.1) and (current != total):
                    return
                last_emit_time = current_time
                
                # Individual Stats
                ind_elapsed = current_time - ind_start_time or 0.001
                ind_speed = current / ind_elapsed
                ind_percent = int((current / file_size) * 100)
                ind_speed_str = f"{ind_speed / (1024*1024):.2f} MB/s"
                ind_size_str = f"{current/(1024*1024):.1f}/{int(total/(1024*1024))} MB"
                
                ind_remaining = file_size - current
                ind_eta = ind_remaining / ind_speed if ind_speed > 0 else 0
                ind_eta_str = time.strftime('%M:%S', time.gmtime(ind_eta))
                
                self.individual_progress.emit(filename, ind_percent, ind_speed_str, ind_eta_str, ind_size_str)
                
                # Global Stats
                self._file_progress[filename] = current
                global_current = sum(self._file_progress.values())
                glob_elapsed = current_time - self._global_start_time or 0.001
                glob_speed = global_current / glob_elapsed
                glob_speed_str = f"{glob_speed / (1024*1024):.2f} MB/s"
                
                # Avoid division by zero if total size is 0
                total_size_safe = self._batch_total_size or 1
                glob_percent = int((global_current / total_size_safe) * 100)
                
                glob_remaining = self._batch_total_size - global_current
                glob_eta = glob_remaining / glob_speed if glob_speed > 0 else 0
                glob_eta_str = time.strftime('%H:%M:%S', time.gmtime(glob_eta))
                glob_prog_str = f"{global_current/(1024*1024):.1f} / {self._batch_total_size/(1024*1024):.1f} MB"
                
                self.download_progress.emit(f"BATCH EXFILTRATION", glob_percent, glob_speed_str, glob_eta_str, glob_prog_str)

            try:
                await self.client.download_media(item['msg'], file=path, progress_callback=progress_callback)
                self.individual_progress.emit(filename, 100, "DONE", "00:00", f"{file_size/(1024*1024):.1f} MB")
                # Ensure global progress reflects 100% for this file
                self._file_progress[filename] = file_size 
            except Exception as e:
                if "MANUAL_ABORT" in str(e): return
                logger.exception("Download failed for %s", filename)
                self.individual_progress.emit(filename, 0, "FAILED", "--", "ERROR")

    # --- CREDENTIALS IO ---
    def _load_credentials(self):
        if not os.path.exists(CRED_FILE): return None, None, None
        try:
            with open(CRED_FILE, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f.readlines()]
            return (lines[0], lines[1], lines[2]) if len(lines) >= 3 else (None, None, None)
        except Exception:
            logger.exception("Failed to load credentials file")
            return None, None, None

    def _save_credentials(self, api_id, api_hash, phone):
        self._ensure_runtime_dir()
        try:
            if os.name == "nt" and os.path.exists(CRED_FILE): ctypes.windll.kernel32.SetFileAttributesW(CRED_FILE, 0x80)
        except Exception:
            logger.debug("Could not clear hidden attribute before writing credentials", exc_info=True)
        with open(CRED_FILE, "w", encoding="utf-8") as f: f.write(f"{api_id}\n{api_hash}\n{phone}")
        try:
            if os.name == "nt": ctypes.windll.kernel32.SetFileAttributesW(CRED_FILE, 0x02)
        except Exception:
            logger.debug("Could not set hidden attribute on credentials file", exc_info=True)

    def _ensure_runtime_dir(self):
        os.makedirs(BASE_DIR, exist_ok=True)

    def _migrate_legacy_files(self):
        """Copy legacy data files into the current runtime directory when missing."""
        legacy_cred = os.path.expanduser("~/.tbtgdl/credentials.txt")
        if legacy_cred != CRED_FILE and os.path.exists(legacy_cred) and not os.path.exists(CRED_FILE):
            try:
                shutil.copy2(legacy_cred, CRED_FILE)
                logger.info("Migrated legacy credentials to %s", CRED_FILE)
            except Exception:
                logger.exception("Failed to migrate legacy credentials")

        legacy_session_candidates = [
            os.path.abspath(f"{SESSION_NAME}.session"),
            os.path.expanduser(f"~/.tbtgdl/{SESSION_NAME}.session"),
        ]
        target_session = f"{SESSION_PATH}.session"
        if not os.path.exists(target_session):
            for src in legacy_session_candidates:
                if os.path.exists(src):
                    try:
                        shutil.copy2(src, target_session)
                        logger.info("Migrated legacy session file from %s", src)
                        break
                    except Exception:
                        logger.exception("Failed to migrate legacy session file from %s", src)
