<img width="1677" height="552" alt="Screenshot_1" src="https://github.com/user-attachments/assets/623022c9-0d61-4983-a77e-31e9b1151db8" />

# TELEFLOW v4 - Telegram Video Downloader
Teleflow is a desktop Telegram video downloader built with PySide6 + Telethon, focused on speed, stable concurrent downloads, and clean workflow from chat scan to batch download.

---

## Latest Release

- Version: `v4.1.1`
- Portable executable: `Teleflow_v4.exe`
- Installer executable: `Teleflow_v4_Setup.exe`
- Release page: https://github.com/usm007/Teleflow-4.0/releases/tag/v4.1.0

## Legacy Versions (History Preserved)

Older Teleflow lines are now preserved in this same repository as dedicated branches:

- `legacy/v1`
- `legacy/v2`
- `legacy/v3`


## Key Features

- Concurrent downloads (1 to 10) with live queue controls
- Session persistence to reduce repeated login steps
- Scan cache persistence to speed up subsequent scans
- Scan progress with `scanned / total` and percentage
- Search, sort, select-all, and batch download workflow

---

## Installation & Setup

### 1. Clone repository

```bash
git clone https://github.com/usm007/Teleflow-4.0.git
cd Teleflow-4.0
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run app

```bash
python main.py
```

---

## Build Windows Executables

Prerequisites:

- Python environment with dependencies installed
- `pyinstaller`
- Inno Setup 6 (for installer build)

Recommended build commands:

```bat
scripts\build_portable.bat
scripts\build_installer.bat
```

Optional code signing:

```bat
set SIGN_CERT_SHA1=YOUR_CERT_THUMBPRINT
```

If Inno Setup is in a custom location:

```bat
set ISCC=YOUR_FULL_PATH_TO_ISCC.exe
```

Build outputs:

- `dist\Teleflow_v4.exe` (portable)
- `release\Teleflow_v4_Setup.exe` (installer)

---

## Download Prebuilt Files

Use GitHub Releases to download prebuilt binaries:

- https://github.com/usm007/Teleflow-4.0/releases

---

## Telegram API Credentials

To use the app you need your own Telegram API credentials:

1. Open https://my.telegram.org
2. Sign in with your phone number
3. Open API Development Tools and create an app
4. Enter `api_id` and `api_hash` in Teleflow

---

## Tech Stack

- PySide6 (Qt for Python)
- Telethon (Telegram MTProto)
- qasync (asyncio + Qt event loop integration)

---

## Project Structure

- `main.py`: UI flow, page navigation, event wiring
- `core.py`: Telegram auth, scanning, queue/download engine
- `assets.py`: custom UI widgets and painted components
- `themes.py` / `stylesheet_builder.py`: theme tokens and stylesheet generation

---

Note: Use this tool for personal backup and lawful usage only. Respect Telegram terms and content ownership.
