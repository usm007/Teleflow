import os
import ctypes
import asyncio
import time
import re
import json
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
SCAN_CACHE_FILE = os.path.join(BASE_DIR, "scan_cache.json")

logger = logging.getLogger("teleflow")


class PauseRequestedError(Exception):
    pass


class ManualAbortError(Exception):
    pass

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
    
    # Real-time scan counter (scanned_count, total_count)
    scan_progress = Signal(int, int)
    scan_cache_loaded = Signal(int)
    scan_finished = Signal()
    
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
        self._scan_generation = 0
        
        # Queue Management
        self._download_queue = asyncio.Queue()
        self._active_tasks = set()
        self._batch_total_size = 0
        self._file_progress = {}
        self._global_downloaded = 0
        self._global_start_time = 0
        
    def set_pause(self, paused: bool):
        self.is_paused = paused

    def stop_task(self):
        self.is_cancelled = True

    def cancel_scan(self):
        self._scan_generation += 1

    def reset_credentials_and_session(self):
        try:
            if self.client:
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(self.client.disconnect())
                except RuntimeError:
                    pass
        except Exception:
            logger.debug("Failed to disconnect client during reset", exc_info=True)

        for target in [CRED_FILE, f"{SESSION_PATH}.session", f"{SESSION_PATH}.session-journal"]:
            if os.path.exists(target):
                try:
                    os.remove(target)
                except Exception:
                    logger.exception("Failed to remove %s", target)

        self.client = None
        self.phone = None
        self.request_creds.emit()

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
        total_videos = 0
        self._scan_generation += 1
        scan_generation = self._scan_generation
        self.scan_progress.emit(0, 0)

        cached_videos = self._get_cached_videos(chat_id)
        if cached_videos:
            self.videos_loaded.emit(cached_videos)
            self.scan_cache_loaded.emit(len(cached_videos))
        
        try:
            entity = await self.client.get_entity(chat_id)

            # Pull total matching messages once so UI can show determinate progress.
            try:
                total_probe = await self.client.get_messages(entity, limit=1, filter=InputMessagesFilterVideo)
                total_videos = int(getattr(total_probe, "total", 0) or 0)
            except Exception:
                logger.debug("Could not resolve total scan count for chat_id=%s", chat_id, exc_info=True)
                total_videos = 0

            self.scan_progress.emit(0, total_videos)

            if cached_videos:
                cached_count = len(cached_videos)
                if total_videos > 0:
                    self.scan_progress.emit(min(cached_count, total_videos), total_videos)

            async for msg in self.client.iter_messages(entity, limit=None, filter=InputMessagesFilterVideo):
                if scan_generation != self._scan_generation:
                    self.auth_status.emit("SCAN ABORTED")
                    return
                if msg.media and hasattr(msg.media, 'document'):
                    if any(isinstance(x, DocumentAttributeVideo) for x in msg.media.document.attributes):
                        size_mb = msg.media.document.size / (1024 * 1024)
                        
                        original_name = msg.file.name or f"video.mp4"
                        safe_name = self._sanitize_filename(original_name)
                        filename = f"{msg.id}_{safe_name}"
                        
                        raw_caption = msg.text or ""
                        clean_caption = raw_caption.replace('\n', ' ').strip()
                        display_caption = clean_caption if clean_caption else safe_name
                        date_added = msg.date.strftime("%Y-%m-%d %H:%M") if getattr(msg, "date", None) else "-"
                        
                        videos.append({
                            "id": msg.id, 
                            "chat_id": chat_id,
                            "name": filename,
                            "caption": display_caption, 
                            "date_added": date_added,
                            "size": f"{size_mb:.2f} MB", 
                            "msg": msg
                        })
                        
                        video_count += 1
                        if video_count % 10 == 0: 
                            self.scan_progress.emit(video_count, total_videos)

            self.scan_progress.emit(video_count, max(total_videos, video_count))
            self._save_scan_cache(chat_id, videos)
            self.videos_loaded.emit(videos)
            self.scan_finished.emit()
            
        except Exception as e:
            logger.exception("Scan failed for chat_id=%s", chat_id)
            self.auth_status.emit(f"SCAN ERROR: {e}")

    # --- DYNAMIC DOWNLOAD QUEUE ---
    
    async def add_to_queue(self, new_items, concurrent_limit, save_path):
        """Adds items to the queue. Starts the processor if not running."""
        entity_cache = {}

        # 1. Update Global Stats
        for item in new_items:
            if not item.get('msg'):
                chat_id = item.get('chat_id')
                msg_id = item.get('id')
                if not chat_id or not msg_id:
                    logger.warning("Skipping cached item without chat_id/msg_id: %s", item.get('name', '?'))
                    continue
                entity = entity_cache.get(chat_id)
                if entity is None:
                    entity = await self.client.get_entity(chat_id)
                    entity_cache[chat_id] = entity
                msg = await self.client.get_messages(entity, ids=msg_id)
                if not msg or not getattr(msg, 'file', None):
                    logger.warning("Could not hydrate cached message %s", msg_id)
                    continue
                item['msg'] = msg
                size_mb = msg.file.size / (1024 * 1024)
                item['size'] = f"{size_mb:.2f} MB"

            file_size = item['msg'].file.size
            self._batch_total_size += file_size
            self._file_progress[item['name']] = 0
            await self._download_queue.put(item)

        # 2. Start Processor if idle
        if not self.is_running:
            self.is_cancelled = False
            self.is_paused = False
            self.is_running = True
            self._global_downloaded = 0
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
                self._batch_total_size = 0
                self._file_progress = {}
                self._global_downloaded = 0
                return

            # Check if finished (Queue empty AND no active tasks)
            if self._download_queue.empty() and not self._active_tasks:
                self.queue_finished.emit()
                self.is_running = False
                # Reset stats for next clean run
                self._batch_total_size = 0
                self._file_progress = {}
                self._global_downloaded = 0
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
                if self.is_cancelled:
                    raise ManualAbortError("MANUAL_ABORT")
                
                # Never block telethon/Qt event loops inside callback.
                if self.is_paused:
                    raise PauseRequestedError("PAUSE_REQUESTED")

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
                previous = self._file_progress.get(filename, 0)
                delta = current - previous
                if delta < 0:
                    # Download restarted from 0 after pause/retry.
                    delta = current
                self._file_progress[filename] = current
                self._global_downloaded = max(0, self._global_downloaded + delta)
                global_current = self._global_downloaded
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
                previous = self._file_progress.get(filename, 0)
                if file_size > previous:
                    self._global_downloaded += file_size - previous
                self._file_progress[filename] = file_size
            except PauseRequestedError:
                previous = self._file_progress.get(filename, 0)
                if previous > 0:
                    self._global_downloaded = max(0, self._global_downloaded - previous)
                self._file_progress[filename] = 0
                while self.is_paused and not self.is_cancelled:
                    await asyncio.sleep(0.2)
                if not self.is_cancelled:
                    await self._download_queue.put(item)
                return
            except ManualAbortError:
                return
            except Exception as e:
                logger.exception("Download failed for %s", filename)
                self.individual_progress.emit(filename, 0, "FAILED", "--", "ERROR")
                previous = self._file_progress.get(filename, 0)
                if previous > 0:
                    self._global_downloaded = max(0, self._global_downloaded - previous)
                self._file_progress.pop(filename, None)
                self._batch_total_size = max(0, self._batch_total_size - file_size)

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

    def _secure_file_for_runtime(self, path):
        """Apply basic file-hardening used for app runtime artifacts."""
        try:
            os.chmod(path, 0o600)
        except Exception:
            logger.debug("Could not apply chmod 600 to %s", path, exc_info=True)

        if os.name == "nt":
            try:
                ctypes.windll.kernel32.SetFileAttributesW(path, 0x02)
            except Exception:
                logger.debug("Could not set hidden attribute on %s", path, exc_info=True)

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

        legacy_scan_cache_candidates = [
            os.path.abspath("scan_cache.json"),
            os.path.expanduser("~/.tbtgdl/scan_cache.json"),
        ]
        if not os.path.exists(SCAN_CACHE_FILE):
            for src in legacy_scan_cache_candidates:
                if src != SCAN_CACHE_FILE and os.path.exists(src):
                    try:
                        shutil.copy2(src, SCAN_CACHE_FILE)
                        self._secure_file_for_runtime(SCAN_CACHE_FILE)
                        logger.info("Migrated legacy scan cache file from %s", src)
                        break
                    except Exception:
                        logger.exception("Failed to migrate legacy scan cache from %s", src)

    def _get_cached_videos(self, chat_id):
        if not os.path.exists(SCAN_CACHE_FILE):
            return []
        try:
            with open(SCAN_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            videos = data.get(str(chat_id), [])
            return videos if isinstance(videos, list) else []
        except Exception:
            logger.debug("Failed to read scan cache", exc_info=True)
            return []

    def _save_scan_cache(self, chat_id, videos):
        try:
            self._ensure_runtime_dir()
            if os.path.exists(SCAN_CACHE_FILE):
                try:
                    if os.name == "nt":
                        ctypes.windll.kernel32.SetFileAttributesW(SCAN_CACHE_FILE, 0x80)
                except Exception:
                    logger.debug("Could not clear hidden attribute before writing scan cache", exc_info=True)
            data = {}
            if os.path.exists(SCAN_CACHE_FILE):
                with open(SCAN_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    data = {}

            # Persist lightweight metadata only; msg objects are re-hydrated when queued.
            stripped = []
            for v in videos:
                stripped.append({
                    "id": v.get("id"),
                    "chat_id": v.get("chat_id", chat_id),
                    "name": v.get("name", ""),
                    "caption": v.get("caption", ""),
                    "date_added": v.get("date_added", "-"),
                    "size": v.get("size", "0 MB"),
                })

            data[str(chat_id)] = stripped
            with open(SCAN_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
            self._secure_file_for_runtime(SCAN_CACHE_FILE)
        except Exception:
            logger.debug("Failed to save scan cache", exc_info=True)
