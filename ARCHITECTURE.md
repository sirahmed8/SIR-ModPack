# 🏗️ SIR ModPack — Comprehensive Architectural Blueprint & Engineering Specification
### *Unified Minecraft Experience • Semantic Versioning v1.0.0 • August 2026*

---

## 🧭 1. System Architecture Overview

The **SIR ModPack Ecosystem** is an enterprise-grade, high-performance Minecraft platform consisting of three native desktop applications, a full Next.js 16 web platform, a GLSL shader compilation engine, 3D Parallax Occlusion Mapping (POM) resource packs, and a zero-telemetry hardware diagnostic bridge.

```mermaid
flowchart TD
    subgraph Client Application Layer
        A[SIR Desktop Launcher v1.0.0]
        B[SIR Installer Studio Pro v1.0.0]
        C[SIR Server Orchestrator Pro v1.0.0]
    end

    subgraph Core Bridge & Hardware Engine
        D[Bridge API - bridge.py]
        D --> E[AuthService - accounts.json & IAS Alt Switcher]
        D --> F[SkinStudioService - 3D Skin Renderer & Capes]
        D --> G[LogsService - Physical latest.log Scanner]
        D --> H[HardwareMonitorService - Kernel Win32 Telemetry]
        D --> I[CloudSyncService - Firebase RTDB 6-Digit Resolver]
        D --> J[ServerService & RCON - Dedicated World Host]
    end

    subgraph Graphics & Audio Engine
        K[Master Bliss GLSL Shader Engine]
        K --> K1[SIR Extreme Shader - Raytraced Visuals]
        K --> K2[SIR Balanced Shader - 144+ FPS Esports]
        L[3D POM Resource Pack Engine - SIR Ultimate Pack]
        M[WebAudio Synthesizer - Tactile Micro-Spring Sound FX]
    end

    subgraph Legal Compliance Gateway
        N[EULA & Terms Enforcer v2026.1]
        N --> N1[Universal Privacy Policy]
        N --> N2[Terms of Service & EULA]
        N --> N3[Cookie & Local Storage Policy]
        N --> N4[Mojang Brand & EULA Compliance]
    end

    subgraph Next.js 16 Web Platform
        O[Next.js 16 App Router - 27 Prerendered Static Routes]
        O --> O1[SWR Storage Cache Engine - storage.ts]
        O --> O2[Theme-Aware Hardware Eco Mode]
        O --> O3[Interactive Cookie & Storage Studio - /cookies]
        O --> O4[Minecraft Account Linking Hub - /profiles]
    end

    A --> D
    A --> N
    A --> K
    A --> M
    B --> D
    C --> J
    O --> I
```

---

## 💻 2. Client Application Layer

### 1. SIR Launcher (`SIR Launcher.exe`)
- **Technology:** Python 3.14 + `pywebview` 6.2 + Tailwind CSS + Lucide Icons + WebAudio API.
- **Key Modules:**
  - **Launchpad View:** 1-Click launch for Modern 26.2 (Fabric 1.21.4) and Legacy 1.8.9 (Forge/Paper PvP).
  - **Server Radar:** Live monitoring of 100+ public and custom multiplayer nodes with 3-state cycling toggle (`Fastest Ping` ➔ `Most Players` ➔ `Default Order`), ping telemetry, and 1-click join.
  - **3D Skin Studio & Capes Wardrobe:** Live 3D avatar viewport with angle rotation, Slim/Classic model switching, 8 creator presets, and 8 official Minecraft capes.
  - **Hardware & RAM Telemetry:** Real-time Win32 kernel telemetry reading CPU load, memory utilization, and dedicated GPU statistics.
  - **Content Managers:** Visual management for Mods, Shaders, Resource Packs, Worlds/Saves, and Game Logs.
  - **Custom Animated Menus:** Solid obsidian dropdowns with smooth pop animations, click-outside auto-dismissal, and no shadow cropping.

### 2. SIR Installer Pro (`SIR Installer.exe`)
- **Technology:** Standalone executable with multi-threaded extraction and elevated UAC privileges.
- **Features:**
  - **Automated Hardware Rig Tuning:** Detects CPU core count, RAM capacity, and GPU vendor to auto-configure optimal memory allocation.
  - **Power Governor:** User toggle between **Turbo Mode** (max speed decompression) and **Smooth / Eco Mode** (background I/O priority for 0-lag responsiveness).
  - **Zero-Data Loss Deployer:** Non-destructive updates that preserve user save worlds, custom keybinds, and screenshot albums.

### 3. SIR Server Orchestrator Pro (`SIR Server Host.exe`)
- **Technology:** Native server manager with zero port-forwarding integration.
- **Features:**
  - **Playit.gg Zero-Port Tunnel:** Public TCP tunnel automation allowing friends to join private servers without router configuration.
  - **Live Telemetry Gauges:** Real-time monitoring of tick rate (TPS: 20.0), connected players, and RAM consumption.
  - **Auto-Restart Watchdog:** Automatic recovery and log diagnostic snapshotting in case of crash events.

---

## 🌐 3. Web Platform Architecture (`website-next/`)

- **Framework:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Framer Motion.
- **Routes (27 Static Prerendered Pages):**
  - `/` (Cinematic Entrance & Feature Showcase)
  - `/builder` (Custom Modpack Preset Configurator)
  - `/profiles` (Modern 26.2 & Legacy 1.8.9 Interactive Matrix)
  - `/shaders` (Bliss Shader & 3D POM Technical Showcase)
  - `/servers` (Live Multiplayer Server Radar & Telemetry)
  - `/cookies` (Interactive Storage Studio & Cache Pruning)
  - `/privacy` (Universal Privacy Policy)
  - `/terms` (Terms of Service & EULA)
  - `/changelog` (Official Release Notes)
  - `/admin` (Owner & Analytics Dashboard)

---

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*\n