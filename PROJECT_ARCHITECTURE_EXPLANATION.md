# 🏗️ SIR ModPack — Comprehensive Architectural Blueprint & Engineering Specification
### *Unified Minecraft Experience • Semantic Versioning v1.0.0 • September 2026 (Update 7)*

---

## 🧭 1. System Architecture Overview

The **SIR ModPack Ecosystem** is an enterprise-grade, high-performance Minecraft platform consisting of one native dispatcher executable (`SIR ModPack.exe`) with three internal desktop modes, an asynchronous Python core engine, a resilient Native JVM launch pipeline, a full Next.js 16 web platform, dedicated isolated dual shaders (**`SIR Modern Shader.zip`** & **`SIR Legacy Shader.zip`**), dual resource packs (**`SIR Modern.zip`** with Patrix 3D POM models & **`SIR Legacy.zip`** 32x PvP), a dynamic Ocean Physics simulation engine, and a zero-telemetry hardware diagnostic bridge.

```mermaid
flowchart TD
    subgraph Client Application Layer ["Client Application Layer (PyWebView + Windows DWM)"]
        A[SIR ModPack.exe dispatcher]
        B[--mode launcher: Standalone Launcher Pro]
        C[--mode installer: Auto-Healing Installer]
        D[--mode server: Dedicated Host & Tunnel Manager]
    end

    subgraph Core Bridge & Hardware Engine ["Core Bridge & Hardware Engine (launcher_core)"]
        E[LauncherBridgeAPI Async Task Engine]
        E --> F[AuthService - Microsoft OAuth & UUIDv5 IAS]
        E --> G[SkinStudioService - Three.js 3D WebGL Studio]
        E --> H[LogsService - Non-blocking stdout/stderr Tailer]
        E --> I[HardwareMonitorService - Kernel Win32 Telemetry]
        E --> J[CloudSyncService - Firebase Sync Codes & RTDB]
        E --> K[VideoPresetService - Tri-Layer Graphics Engine]
        E --> L[ControlsService - Dual-Mode Keybinding Converter]
        E --> M[CleanerService & Deep Crash Analyzer]
    end

    subgraph Native JVM Pipeline ["Native JVM Pipeline (native_runner.py)"]
        N[Strict RAM Governor -Xmx/-Xms & G1GC]
        O[Pre-Launch LWJGL 2 / 3 DLL Extractor]
        P[Dynamic Classpath Assembly - Fabric 26.2 / Forge 1.8.9]
        Q[Stable JRE 21 LTS / JRE 8 Locator]
    end

    subgraph Profile Matrix ["Instances Profile Matrix (instances/)"]
        M1[26.2-ultra: 16 Chunks, POM, SIR Modern Shader, 144+ FPS]
        M2[26.2-balanced: 12 Chunks, Balanced Shaders, 180+ FPS]
        M3[26.2-performance: 8 Chunks, 0ms Sodium Boost, 350+ FPS]
        M4[26.2: Vanilla+ Modular Fabric 228 Mods, 300+ FPS]
        L1[1.8.9: PvP Battle Suite, 28 Mods, 500+ FPS]
        L2[1.8.9-ultra: HD 32x Skyboxes, SIR Legacy Shader, 300+ FPS]
        L3[1.8.9-balanced: Ranked Bedwars 12 Chunks, 450+ FPS]
        L4[1.8.9-performance: Zero-Delay Max FPS Engine, 600+ FPS]
    end

    subgraph Cloud & Web Platform ["Cloud & Web Platform (website-next & Firebase)"]
        W[Next.js 16 App Router - 32 Static Routes]
        W --> W1[AiChatbot.tsx: Gemini 4-Tier AI Waterfall]
        W --> W2[Firebase Realtime Database: Presence & OTA Releases]
        W --> W3[Firestore: Telemetry & Client Error Reporting]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> Native JVM Pipeline
    Native JVM Pipeline --> Profile Matrix
    E --> Profile Matrix
    W --> J
```

---

## 💻 2. Client Application Layer

### 1. `SIR Launcher.exe` (Standalone Desktop Launcher Pro)
- **Technology:** Python 3.13 / 3.14 + `pywebview` 6.2 + 20 Domain JavaScript Modules + Tailwind CSS + Lucide Icons + Spring Physics.
- **Key Modules:**
  - **Launchpad View:** 1-Click launch for Modern 26.2 (Fabric 0.16.10, 228 Mods) and Legacy 1.8.9 (Forge 11.15.1.2318, 28 Mods) with native Direct JVM Launch Engine.
  - **Cloud Self-Healing:** `InstanceService.heal_instance_if_needed()` validates instance integrity, auto-downloading missing jars or configs from Cloud CDN.
  - **Server Radar:** Live monitoring of 100+ public and custom multiplayer nodes with 3-state cycling toggle (`Fastest Ping` ➔ `Most Players` ➔ `Default Order`), ping telemetry, and 1-click join.
  - **3D Skin Studio & Capes Wardrobe:** Live 3D avatar viewport with angle rotation, Slim/Classic model switching, 8 creator presets, and 8 official Minecraft capes.
  - **Hardware & RAM Telemetry:** Real-time Win32 kernel telemetry reading CPU load, memory utilization, and dedicated GPU statistics.
  - **Content Managers:** Visual management for Mods (228 Modern Fabric mods & 28 Legacy Forge mods), Dedicated Dual Shaders (`SIR Modern Shader.zip` / `SIR Legacy Shader.zip`), Dual Resource Packs (`SIR Modern.zip` with Patrix 3D POM models / `SIR Legacy.zip`), Worlds/Saves, and Game Logs.

### 2. `SIR Installer.exe` (Standalone Smart Auto-Healing Installer)
- **Technology:** 16.6 MB standalone executable with cloud payload streaming and elevated UAC privileges.
- **Features:**
  - **Cloud CDN Downloader:** Streams modular archives (`payload_mods_26.2.zip`, `payload_mods_1.8.9.zip`, `payload_packs.zip`, `payload_shaders.zip`, `payload_configs.zip`) from GitHub Releases with live download speed (`MB/s`) and percentage tracking.
  - **Anti-Compromise & Anti-Corruption Engine:** Structural CRC verification (`is_valid_zip`) quarantines damaged archives and auto-recovers clean copies.
  - **Power Governor:** User toggle between **Turbo Mode** (all CPU threads) and **Smooth / Eco Mode** (background I/O priority for 0-lag responsiveness).
  - **Zero-Data Loss Deployer:** Non-destructive updates that preserve user save worlds, custom keybinds, and screenshot albums.

### 3. `SIR Server Manager.exe` (Standalone Server Host & Tunnel Manager)
- **Technology:** Native server manager with custom CyberSelect glassmorphic dropdowns and zero port-forwarding integration.
- **Features:**
  - **Playit.gg Zero-Port Tunnel:** Public TCP tunnel automation allowing friends to join private servers without router configuration.
  - **Live Telemetry Gauges:** Real-time monitoring of tick rate (TPS: 20.0), connected players, and RAM consumption.
  - **Auto-Restart Watchdog:** Automatic recovery and log diagnostic snapshotting in case of crash events.

---

## ⚡ 3. Memory Governor & Dynamic G1GC Optimization Model

The launcher enforces strict RAM boundaries without arbitrary upward clamps using `calculate_ram_parameters()`:

1. **Strict `-Xmx` and `-Xms` Formatting:**
   - Memory inputs (integers, floats, string units like `"6GB"` or `"6144M"`) are parsed to integer megabytes.
   - Exact values are passed to `-Xmx` and `-Xms` without silent reduction or clamping.
2. **Dynamic G1GC Nursery & Region Calculation:**
   - **≤ 3 GB:** Nursery 20%–30%, Reserve 10%, Region 1M–2M.
   - **3 GB – 8 GB:** Nursery 30%–40%, Reserve 15%, Region 4M–8M.
   - **8 GB – 16 GB:** Nursery 40%–50%, Reserve 20%, Region 16M.
   - **> 16 GB:** Nursery 50%–60%, Reserve 20%, Region 32M.
3. **Latency-Optimized GC Flags:**
   - `-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:+AlwaysPreTouch -XX:+UseStringDeduplication`
   - Target pause time `-XX:MaxGCPauseMillis=50` (Modern 26.2) and `200` (Legacy 1.8.9).

---

## 🎮 4. Tri-Layer Video Preset Engine & Graphics System

The `VideoPresetService` provides 1-click graphics optimization across 5 tiers: **Ultra**, **Balanced**, **Performance**, **Competitive**, and **Potato**:

```
+---------------------------------------------------------------------------------------------------+
| PRESET TIER  | MODERN 26.2 (FABRIC + SODIUM + IRIS)            | LEGACY 1.8.9 (FORGE + OPTIFINE)  |
+--------------+-------------------------------------------------+----------------------------------+
| Ultra        | 16 Chunks, Patrix 3D POM, SIR Modern Shader     | 16 Chunks, SIR Legacy Shader     |
| Balanced     | 12 Chunks, SIR Modern Shader, Cutout Leaves     | 12 Chunks, SIR Legacy Shader     |
| Performance  | 8 Chunks, Fast Leaves, Shaders OFF, Immediate   | 8 Chunks, Fast Render/Math, OFF  |
| Competitive  | 8 Chunks, 0ms Input Latency, Shaders OFF        | 8 Chunks, 0-Delay Hit Reg, OFF   |
| Potato       | 4 Chunks, Fast Leaves, Shaders OFF, 0 Mipmap    | 4 Chunks, Fast Trees, OFF        |
+---------------------------------------------------------------------------------------------------+
```

### Dedicated Dual-Shader Architecture:
- **`SIR Modern Shader.zip` (Modern 26.2 / Iris):** Crystal water refraction, dynamic wave caustics, godrays, celestial moonbeams, and 3D POM relief. Pre-configured via `config/iris.properties` (`shaderPack=SIR Modern Shader.zip`).
- **`SIR Legacy Shader.zip` (Legacy 1.8.9 / OptiFine):** GLSL `#version 120` optimized core, animated waving water, specular reflections, soft shadows, and 200+ FPS framerates. Pre-configured via `optionsshaders.txt` (`shaderPack=SIR Legacy Shader.zip`).

### Dual Resource Packs:
- **`SIR Modern.zip`:** Contains 88 custom 3D models and blockstates from Patrix geometry (3D crops, 3D ores, and 3D natural terrain).
- **`SIR Legacy.zip`:** Custom 32x faithful PvP resource pack with clear GUI and low-latency particles.

### Dynamic Physics Mod Ocean Waves Engine:
- Continuous rolling wave swells configured via `physics_client_config.json` (`oceanPhysics: true`, `oceanWeatherClear: 0.6`).
- Whitecap foam, wave spray particles, physical buoyancy on floating entities and boats, cloth and snow track physics.

---

## 📁 5. Profile Matrix Parity Specification

All 8 profile permutations are physically provisioned under `instances/`:

| Directory | Profile ID | MC Version | Mod Loader | Mods Count | Default RAM | Primary Shader | Primary Resource Pack | Target FPS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `26.2-ultra` | `sir-26-ultra` | 1.21.4 (26.2) | Fabric 0.16.10 | 228 Mods | 6GB – 12GB | `SIR Modern Shader.zip` | `SIR Modern.zip` (Patrix 3D) | 144+ FPS |
| `26.2-balanced` | `sir-26-balanced` | 1.21.4 (26.2) | Fabric 0.16.10 | 228 Mods | 4GB – 8GB | `SIR Modern Shader.zip` | `SIR Modern.zip` (Patrix 3D) | 180+ FPS |
| `26.2-performance` | `sir-26-competitive` | 1.21.4 (26.2) | Fabric 0.16.10 | 228 Mods | 3GB – 6GB | OFF (Sodium Fast) | `SIR Modern.zip` (Patrix 3D) | 350+ FPS |
| `26.2` | `sir-26-vanilla` | 1.21.4 (26.2) | Fabric 0.16.10 | 228 Mods | 4GB – 8GB | OFF (Vanilla+ Modpack) | `SIR Modern.zip` (Patrix 3D) | 300+ FPS |
| `1.8.9` | `sir-189-pvp` | 1.8.9 | Forge 11.15.1.2318 | 28 Mods | 2GB – 4GB | OFF (OptiFine Fast) | `SIR Legacy.zip` (32x PvP) | 500+ FPS |
| `1.8.9-ultra` | `sir-189-ultra` | 1.8.9 | Forge 11.15.1.2318 | 28 Mods | 3GB – 6GB | `SIR Legacy Shader.zip` | `SIR Legacy.zip` (32x PvP) | 300+ FPS |
| `1.8.9-balanced` | `sir-189-balanced` | 1.8.9 | Forge 11.15.1.2318 | 28 Mods | 2GB – 4GB | `SIR Legacy Shader.zip` | `SIR Legacy.zip` (32x PvP) | 450+ FPS |
| `1.8.9-performance` | `sir-189-competitive` | 1.8.9 | Forge 11.15.1.2318 | 28 Mods | 1.5GB – 3GB | OFF (Raw Mouse Input) | `SIR Legacy.zip` (32x PvP) | 600+ FPS |

---

## 🌐 6. Web Platform & Cloud Highway (`website-next/`)

- **Framework:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Framer Motion.
- **Static Pre-rendered Routes (32 Routes):**
  - Core: `/`, `/profiles`, `/mods`, `/shaders`, `/servers`, `/skins`, `/capes`, `/seeds`, `/trainer`, `/benchmarks`, `/builder`, `/leaderboards`, `/faq`, `/admin`, `/changelog`, `/compatibility`, `/server-guide`, `/packs`.
  - Legal & Governance: `/privacy`, `/terms`, `/cookies`, `/eula`, `/agreements`.
  - API & Syndication: `/api/status`, `/api/updates`, `/api/news`, `/api/servers`, `/news/index.xml`, `/sitemap.xml`, `/robots.txt`.
- **Firebase Realtime Database & Firestore Schema:**
  - Sync Codes: `launcherSyncCodes/{6_digit_code}`
    - Schema: `{"code": str, "userId": str, "username": str, "uuid": str, "skinUrl": str, "createdAt": int, "expiresAt": int, "claimed": bool}`
  - OTA Release Dispatcher: `releases/latest`
    - Schema: `{"version": str, "installerUrl": str, "bundleUrl": str, "isMandatory": bool, "changelog": str, "releaseDate": str}`
- **Gemini 4-Tier AI Waterfall:**
  - Automatic fallback cascade across `gemini-3.6-flash` ➔ `gemini-3.5-flash-lite` ➔ OpenRouter ➔ Offline Expert Rules.

---

## 🧪 7. Automated Test Harness & Quality Assurance

- **Master Test Harness (`tests/`):** 340 automated unit and integration tests across 25 test suites with **100% pass rate in 109.4s**.
- **Diagnostic Health Doctor (`ecosystem_doctor.py`):** Automated 6-tier ecosystem verification with **100% healthy status across all 6 layers**.
- **Coverage Areas:** Universal Atomic Persistence, Resilient HTTP Range Downloader, Win32 Kernel Telemetry Governor, 7-Matcher Crash Diagnostics, JRE Discovery & PE Header Verification, Classpath Assembly, Video Preset Tri-Layer Injection, Physics Mod Realistic Waves Calibration, and 8-Instance Matrix Parity with Isolated Dual Shaders.

---

## 🔒 8. Multi-Layer Security & Integrity Architecture

1. **Strict Input Sanitization:**
   - `lib/security.ts` sanitizes all incoming usernames, codes, and parameters with strict regex preventing XSS, SQL injection, and prototype pollution.
2. **Mandatory HTTP Security Headers:**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: SAMEORIGIN`
   - `X-XSS-Protection: 1; mode=block`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - Content Security Policy (CSP) restricting inline script execution.
3. **Atomic File Persistence:**
   - Universal atomic replace across all configuration and state writes preventing file corruption upon sudden power loss.
4. **Legal & Governance Protocols:**
   - [End User License Agreement (EULA)](EULA.md)
   - [Master Community Agreements](AGREEMENTS.md)
   - [Universal Privacy Policy](PRIVACY.md)
   - [Terms of Service](TERMS.md)
   - [Cookie Policy](COOKIES.md)
   - [Open Source License](LICENSE.md)

---

*© 2026 SIR ModPack Ecosystem. Developed with Craftsmanship by SIR Ahmed.*
