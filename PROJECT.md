# Project: SIR Minecraft Ecosystem Full-Stack Hardening

## Architecture
The SIR Minecraft Ecosystem is an integrated high-performance desktop and cloud gaming platform composed of:
1. **Python Core Launcher Engine & Native JVM Pipeline (`development/launcher_core/`, `shared_core/`)**:
   - Asynchronous non-blocking bridge execution and task queuing (`LauncherBridgeAPI`).
   - Resilient chunked parallel streaming downloader with HTTP Range requests and exponential backoff.
   - Atomic state persistence (`atomic_write_json`, atomic text file replace) preventing file corruption.
   - Dynamic JVM classpath resolution, stable JRE 21 LTS / JRE 8 runtime locator, strict RAM parameter enforcement, and pre-launch native binaries extraction (LWJGL 2 / LWJGL 3).
   - Non-blocking stdout/stderr tailing, PID telemetry governor with working-set memory trimming, and deep crash report analyzer.
2. **Desktop Client UI & HCI Experience (`development/launcher_ui/`, `SIR_Launcher_Modern.py`)**:
   - Hardware-accelerated PyWebView with Windows DWM dark titlebar integration (`0x000E0906`).
   - Cyber-Dark Glassmorphic design system (Plus Jakarta Sans + JetBrains Mono, 60-30-10 palette, 24px/14px curvature, cubic-bezier spring micro-interactions).
   - Profile & server matrices with instant live filtering and custom instance builder.
   - Tri-layer 1-Click Video Preset engine (`options.txt`, `sodium-options.json`, `iris.properties`).
   - Three.js / SkinView3D WebGL studio with 3D walking animations, classic/slim models, and custom cape injection.
   - Account management: Microsoft OAuth 2.0 PKCE loopback listener + offline IAS UUIDv5 accounts + in-game `ias_accounts.json` sync + Firebase cloud sync.
3. **Web Platform & Cloud Highway (`website-next/`)**:
   - Next.js 16 App Router platform with React 19, TypeScript strict typing, Tailwind CSS v4, Lucide icons, Framer Motion.
   - Firebase Realtime Database & Firestore: active presence, atomic download metrics, OTA update dispatch, live announcements, and client error reporting.
   - Gemini AI Assistant: 4-tier fallback waterfall (`gemini-3.6-flash` -> `gemini-3.5-flash-lite` -> OpenRouter -> offline expert rules) with domain system instructions and Arabic translation.
4. **Automated Verification & Test Harness (`tests/`, `ecosystem_doctor.py`)**:
   - End-to-end programmatic verification of bridge APIs, native JVM runner, classpath resolution, profile permutations (Modern Fabric 26.2 & Legacy Forge 1.8.9), and health checks.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Async Bridge & Non-blocking I/O | Prevent UI freezes during downloads, checks, and hash computations | M1 | Survey Explorer 1 / R1 |
| 2 | Resilient Chunked Downloader | HTTP Range chunked streaming with exponential backoff and SHA-256 validation | M1 | Survey Explorer 1 / R1 |
| 3 | Atomic File Persistence | Universal atomic write patterns across all instance, config, and state files | M1 | Survey Explorer 1 / R1 |
| 4 | Zero Mock Telemetry & Cleaner | Remove fabricated metrics; implement real disk cleaning, repair, and hardware telemetry | M1 | Survey Explorer 1 / R1 |
| 5 | Telemetry Governor & Memory Trimming | Monitor child JVM PID, CPU/RAM working set, and apply EmptyWorkingSet memory trimming | M1 | Survey Explorer 1 / R1 |
| 6 | Deep Crash Stack-Trace Analyzer | Automated diagnosis of mixin conflicts, class version mismatches, and native crash logs | M1 | Survey Explorer 1 / R1 |
| 7 | Strict RAM Parameter Allocation | Strictly honor user-selected RAM boundaries (-Xmx/-Xms) without forced overrides | M2 | Survey Explorer 1 / R1 |
| 8 | Pre-Launch Natives Extraction | Dynamic extraction of LWJGL 2 / 3 DLLs (lwjgl64.dll, OpenAL64.dll) preventing linkage crashes | M2 | Survey Explorer 1 / R1 |
| 9 | Dynamic Classpath Assembly | Dynamic classpath resolution from mmc-pack.json, instance.cfg, version.json for Fabric 26.2 & Forge 1.8.9 | M2 | Survey Explorer 1 / R1 |
| 10 | Stable JRE Runtime Locator | Discovery and provisioning of Eclipse Temurin 21 LTS for 26.2 and JRE 8 for 1.8.9 | M2 | Survey Explorer 1 / R1 |
| 11 | Dual-Mode Keybinding Injection | GLFW token strings for 26.2 vs numeric LWJGL scancodes for 1.8.9 in options.txt | M2 | Survey Explorer 1 / R1 |
| 12 | Non-blocking stdout/stderr Tailer | Real-time process log tailing and live event streaming | M2 | Survey Explorer 1 / R1 |
| 13 | Cyber-Dark Glassmorphic UI Tokens | Complete 60-30-10 OKLCH/Hex palette, curvature hierarchy, and spring micro-interactions | M3 | Survey Explorer 2 / R2 |
| 14 | 1-Click Video Preset Engine | Tri-layer configuration injector across Vanilla, Sodium, and Iris configs | M3 | Survey Explorer 2 / R2 |
| 15 | 3D Skin & Capes WebGL Studio | Three.js / SkinView3D real-time 3D animation, model switching, and cape injection | M3 | Survey Explorer 2 / R2 |
| 16 | Bi-Modal Account & IAS Sync | Microsoft OAuth 2.0 PKCE loopback + offline UUIDv5 accounts + in-game ias_accounts.json | M3 | Survey Explorer 2 / R2 |
| 17 | Next.js 16 Web Platform Hardening | Clean Turbopack static export, strict TypeScript typing, fix React hooks in context.tsx | M4 | Survey Explorer 3 / R3 |
| 18 | Feature-Rich AI Chatbot UI | Integrate advanced AiChatbot.tsx (speech synthesis, fullscreen, audio effects) into web layout | M4 | Survey Explorer 3 / R3 |
| 19 | Firebase Cloud Telemetry & Sync Alignment | Harmonize launcherSyncCodes path, live presence, atomic download metrics, error reporting | M4 | Survey Explorer 3 / R3 |
| 20 | Gemini Multi-Tier AI Assistant | 4-tier model waterfall with domain prompt tuning and Arabic localization | M4 | Survey Explorer 3 / R3 |
| 21 | Instance Profile Matrix Parity | Provision and synchronize missing instance directories (26.2-balanced, 26.2-performance, 1.8.9-*) | M5 | Survey Explorer 3 / R4 |
| 22 | Automated E2E Verification Suite | Complete test suite covering bridge APIs, native JVM runner, profile permutations, and health | M5 | Survey Explorer 3 / R4 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Python Core Engine & Telemetry Hardening | Features 1, 2, 3, 4, 5, 6 (Async I/O, resilient downloader, atomic persistence, zero mock data, telemetry governor, crash analyzer) | none | DONE |
| 2 | M2: Native JVM Launch Pipeline & Compatibility | Features 7, 8, 9, 10, 11, 12 (Strict RAM, pre-launch natives extraction, dynamic classpath, JRE locator, dual keybindings, live tailer) | M1 | DONE |
| 3 | M3: Desktop Client UI, Video Presets & Accounts | Features 13, 14, 15, 16 (Cyber-dark UI, video presets, 3D skin studio, Microsoft OAuth + offline IAS accounts) | M1, M2 | DONE |
| 4 | M4: Next.js 16 Web Hub, Firebase & Gemini AI | Features 17, 18, 19, 20 (Strict Next.js 16 build/lint, AiChatbot integration, Firebase sync alignment, Gemini AI waterfall) | none | DONE |
| 5 | M5: Profile Matrix Parity & E2E Verification | Features 21, 22 (Instance directory sync, 100% E2E test pass across Modern 26.2 & Legacy Forge 1.8.9) | M1, M2, M3, M4 | VERIFIED |

## Interface Contracts

### Python Bridge ↔ Desktop Webview (`LauncherBridgeAPI`)
- `install_online_mod(project_id, version_id, file_name, callback)` -> `{"success": bool, "file": str, "error": str}` (non-blocking async)
- `check_mod_updates(instance_name, callback)` -> `{"success": bool, "updates": list, "count": int}` (non-blocking async)
- `launch_instance(instance_name, ram_gb, power_mode, java_path, custom_args)` -> `{"success": bool, "pid": int, "log_file": str, "error": str}`
- `apply_video_preset(instance_name, preset_name)` -> `{"success": bool, "applied": list[str], "error": str}`
- `start_microsoft_browser_auth()` -> `{"success": bool, "auth_url": str, "port": int}`
- `create_offline_account(username)` -> `{"success": bool, "account": dict, "error": str}`
- `sync_cloud_code(code)` -> `{"success": bool, "synced_accounts": list, "error": str}`

### Cloud Sync Highway (Web ↔ Launcher via Firebase RTDB)
- Sync Codes path: `launcherSyncCodes/{6_digit_code}`
  - Schema: `{"code": str, "userId": str, "username": str, "uuid": str, "skinUrl": str, "createdAt": int, "expiresAt": int, "claimed": bool}`
- OTA Release path: `releases/latest`
  - Schema: `{"version": str, "installerUrl": str, "bundleUrl": str, "isMandatory": bool, "changelog": str, "releaseDate": str}`

## Code Layout
- `development/launcher_core/`: Core backend services (bridge, instance, auth, native_runner, hardware_monitor, logs, store, controls, cleaner, repair, syncer, satellite).
- `development/shared_core/`: Shared runtime utilities (atomic persistence, path resolution, DPI, DWM window attributes).
- `development/launcher_ui/`: Frontend interface (HTML5, app.css, app.js, js/modules).
- `development/installer_core/`: Installer backend and extraction logic.
- `development/server_core/`: Server manager backend and core downloader.
- `website-next/`: Next.js 16 web application (App router, components, lib/firebase, lib/gemini).
- `instances/`: Minecraft instance configurations (26.2, 1.8.9, custom profiles).
- `tests/`: Automated pytest / unittest test suite.
