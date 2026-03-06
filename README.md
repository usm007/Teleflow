```markdown
# TELEFLOW v4 - SECURE DATA EXFILTRATION SUITE

**Teleflow** is a professional-grade, high-performance Telegram video downloader built with a sleek **Grey & Green** terminal aesthetic. It features a robust asynchronous engine, a "cyber-ops" inspired interface, and a new **Concurrent Batch Processor** designed for maximum efficiency and stability.

---

## 🛡️ Key Features

### **Core Engine & Performance**
* **Concurrent Downloading:** Download up to **10 files simultaneously**. Includes a dynamic thread selector to balance speed and stability.
* **Robust Network Handler:** Automatically handles **Telegram Data Center (DC) migrations**, preventing downloads from freezing or crashing due to server-side shifts.
* **Session Persistence:** Maintains secure session states to avoid repeated logins.
* **Resumable Queue:** Pause and Resume the entire download batch instantly without losing progress.

### **Cyber-Ops Interface**
* **Symmetric Security Uplink:** A dual-pane login screen featuring interactive setup instructions and clickable resource links.
* **Active Uplink Manifest:** A unified, scrollable dashboard tracking live downloads ("Active") versus pending files ("Queued") with color-coded status indicators.
* **Real-time Telemetry:** A split-view dashboard featuring live throughput graphs, hex data streams, and a "drama" terminal log that tracks every packet exfiltrated.
* **Payload Directory:** A smooth, borderless file manager with "New > Old" and "Old > New" sorting, search highlighting, and one-click selection.

---

## 🚀 Installation & Setup

### **1. Clone the Repository**
```bash
git clone [https://github.com/YOUR_USERNAME/Teleflow.git](https://github.com/YOUR_USERNAME/Teleflow.git)
cd Teleflow

```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt

```

### **3. Run the Application**

```bash
python main.py

```

---

## 📦 Compilation (Build .exe)

To compile Teleflow into stable Windows artifacts that run without Python installed:

1. **Install PyInstaller:**
```bash
pip install pyinstaller

```


2. **Build portable executable:**
*(One-file output for easy sharing)*
```bash
pyinstaller --noconsole --onefile --name="Teleflow_v4" --icon="icon.ico" --add-data="icon.ico;." main.py

```


3. **Build installer payload + Setup executable (recommended):**
*(Requires Inno Setup 6)*
```bash
pyinstaller --noconfirm --clean teleflow.spec
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\teleflow.iss

```

If Inno Setup is installed in a different location, set:
```bash
set ISCC=YOUR_FULL_PATH_TO_ISCC.exe

```


4. **Use reproducible scripts (preferred):**
```bash
scripts\build_portable.bat
scripts\build_installer.bat

```


5. **Optional signing (recommended for SmartScreen trust):**
Set your certificate thumbprint before running build scripts:
```bash
set SIGN_CERT_SHA1=YOUR_CERT_THUMBPRINT

```


6. **Locate artifacts:**
- `dist\Teleflow_v4.exe` (portable)
- `release\Teleflow_v4_Setup.exe` (installer)

The scripts auto-sign and verify binaries if `SIGN_CERT_SHA1` is set.

---

## 🛠️ Configuration Guide

To establish a secure uplink, you need your own Telegram API credentials:

1. Navigate to [my.telegram.org](https://my.telegram.org).
2. Login with your phone number and the code sent to your Telegram app.
3. Go to **API Development Tools** and create a new application.
4. Input your generated `api_id` and `api_hash` into the Teleflow login screen.

---

## 🖥️ Tech Stack

* **GUI Framework:** PySide6 (Qt for Python)
* **Telegram Protocol:** Telethon (MTProto)
* **Asynchronous Engine:** qasync (Asyncio integration for Qt) - *Fixes UI freezing during heavy loads.*
* **Interface:** Custom CSS-themed widgets with dynamic paint events.

---

## 📦 Project Structure

* `main.py`: The central controller managing navigation, the new Split-View UI, and high-level logic.
* `core.py`: The heavy-duty engine handling Telegram connections, concurrent semaphores, and download logic.
* `assets.py`: Custom-painted hacker widgets including the graph, hex stream, and scanline overlay.
* `requirements.txt`: Project dependencies.

---

> **Note:** This tool is intended for personal backup and educational use. Ensure you comply with Telegram's Terms of Service and respect content ownership.


**Screenshots:**


<img width="1919" height="1020" alt="dddddddddd" src="https://github.com/user-attachments/assets/7111df9a-17c6-4349-bb92-05f78c2d2c01" />


<img width="1919" height="1022" alt="aaaaaa" src="https://github.com/user-attachments/assets/9aa56026-baa3-4e24-a63f-ddc6db6be782" />


<img width="1919" height="1079" alt="bbbbbbbbbbb" src="https://github.com/user-attachments/assets/38a53551-7599-4125-aa3d-e06a333987f2" />


<img width="1919" height="1022" alt="ccccccccc" src="https://github.com/user-attachments/assets/4537422f-fecd-421e-89d5-014164b73c40" />
