# MISSION BRIEFING: OPERATIONAL MANUAL

**Teleflow v3.0** is a professional-grade Telegram extraction tool designed for high-speed, concurrent data saving. This manual outlines standard operating procedures for secure uplink and payload acquisition.

---



## 📡 PHASE 1: UPLINK CONFIGURATION

Before commencing operations, you must establish a secure handshake with the Telegram Data Center (DC).

### 1. Acquire Credentials
1. Navigate to [my.telegram.org](https://my.telegram.org) securely.
  
2. Login and select **"API Development Tools"**.
   
3. Create a new application (Name: `Teleflow_Ops`, Shortname: `tflow`).
  
4. Copy your unique `App api_id` and `App api_hash`



<img width="1100" height="533" alt="Screenshot_1" src="https://github.com/user-attachments/assets/4b7c95b6-5be0-4a3f-b10a-fb391b011175" />


<img width="619" height="257" alt="Screenshot_2" src="https://github.com/user-attachments/assets/ac04783b-b90f-46ac-8139-79a2016288ac" />


<img width="895" height="373" alt="Screenshot_3" src="https://github.com/user-attachments/assets/0217170d-1842-4e57-9f06-eeb42090b9fe" />


<img width="1198" height="411" alt="App-configuration" src="https://github.com/user-attachments/assets/9c564a40-9163-46cb-a7ff-de22afe8ba5e" />.






### 2. Establish Connection
* **Launch Teleflow.**
* Input your **API ID** and **API HASH** into the designated terminal fields.
* Input your target phone number (Format: `+123456789`).
* Click **[ESTABLISH UPLINK]**.
* *System will request a One-Time-Pad (OTP) sent to your Telegram App.*

> **⚠️ SECURITY NOTE:** Credentials are stored locally in `~/.tbtgdl/credentials.txt` with standard OS-level protection.

---





## 🎯 PHASE 2: TARGET ACQUISITION

Once authenticated, the system will decrypt your dialog graph.

1.  **Select Source Node:**
    * Use the **Filter Tabs** to toggle between `CHANNELS` (Green), `GROUPS` (Blue), and `DMs` (Grey).
    * Use the **Search Bar** to isolate specific targets by name.
2.  **Initiate Scan:**
    * Double-click a target to begin the metadata scan.
    * *The Matrix Loader will visualize the retrieval of video objects.*

---





## 📂 PHASE 3: PAYLOAD ANALYSIS

The **Payload Directory** lists all available video assets. You must identify valid targets before exfiltration.

### The Metadata Grid
| Column | Description |
| :--- | :--- |
| **SEL** | Checkbox for target selection. |
| **DATE** | **[NEW]** Timestamp of upload (YYYY-MM-DD HH:MM). Use this to verify incident windows. |
| **FILENAME** | The sanitized name of the file. |
| **SIZE** | File footprint in Megabytes (MB). |

### Filtering Protocols
* **Search:** Type keywords to filter the list instantly.
* **Sort:** Use **[NEW > OLD]** to prioritize recent intelligence.
* **Captions:** Toggle `[x] SHOW CAPTIONS` to read message context instead of filenames.

---





## 🚀 PHASE 4: EXFILTRATION (DOWNLOAD)

1.  **Select Targets:**
    * Click individual rows or use **[SELECT ALL]**.
2.  **Set Destination:**
    * Verify the **SAVE LOCATION** path is writable.
3.  **Thread Control:**
    * Adjust the **THREADS** counter.
    * *Recommended:* `3` for stealth, `10` for maximum throughput.
4.  **Execute:**
    * Click **[START EXFILTRATION]**.



### Active Uplink Manifest
During the operation, the dashboard provides real-time telemetry:
* **Throughput Graph:** Monitors network speed stability.
* **Hex Stream:** Visualizes packet decryption.
* **Terminal Log:** Tracks critical system events (Connects, Retries, Errors).

> **MISSION COMPLETE:** Enable `[x] AUTO SHUTDOWN` if leaving the terminal unattended.

---





### 🔧 TROUBLESHOOTING

* **Error: AUTH_KEY_UNREGISTERED**
    * *Solution:* Delete `credentials.txt` and re-authenticate.
* **Error: FLOOD_WAIT_X**
    * *Solution:* Telegram is throttling your IP. Pause operations for `X` seconds.

---
*End of Transmission // Teleflow Dev Team*
