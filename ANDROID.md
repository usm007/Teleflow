# Teleflow Android Implementation

This repository now includes an initial native Android scaffold under `android/`.

## Current Status

- Android Gradle project initialized
- App module created with Jetpack Compose
- Launchable `MainActivity` and initial Teleflow placeholder UI
- Auth/session foundation implemented:
	- Auth state machine (`credentials -> otp -> password -> authenticated`)
	- Encrypted local session storage (`EncryptedSharedPreferences`)
	- `AuthRepository` + `AuthViewModel` wiring
	- Compose login/auth screen integrated in app shell
- Phase 3 scan flow implemented:
	- Chat selection and loading pipeline
	- Cached-first video rendering per selected chat
	- Inline scan progress text (`scanned / total (%)`)
	- Incremental new-video insertion during scanning
	- Search filter on scanned video list
- Phase 4 queue controls implemented (simulated backend):
	- Queue latest scanned videos into downloader
	- Concurrency controls (`- / +`, 1 to 10)
	- Pause/resume and stop queue actions
	- Per-item progress, speed, ETA, and state labels
	- Global queue status summary (active/queued/done)
- Local persistence implemented for Android prototype:
	- Scan cache persisted per chat (`scan_cache_android.json`)
	- Scan-run counters persisted for incremental fake scan growth
	- Download queue state persisted (`download_queue_android.json`)
	- Concurrency and pause state restored after app restart
- Background runtime scaffolding implemented:
	- Foreground download service with persistent notification
	- WorkManager heartbeat worker placeholder for resilient queue sync
	- Automatic service start/stop trigger based on queue activity

## Next Steps

1. Integrate real Telegram transport/client for Android auth/scan/download (replace simulated repositories)
2. Replace file-based prototype persistence with Room-backed models for chats/videos/jobs
3. Add Android instrumentation tests for auth, scan, and queue flows
4. Harden queue lifecycle across process death and reboot events
5. Add release pipeline for signed debug/release APK/AAB artifacts

## Open in Android Studio

1. Open Android Studio
2. Choose `Open` and select `android/`
3. Let Gradle sync complete
4. Run on emulator or physical device
