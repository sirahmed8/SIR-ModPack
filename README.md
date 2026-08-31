# 💎 SIR ModPack — The Ultimate Minecraft Ecosystem
### *Unified Minecraft Platform • Desktop Suite • Shaders • Web Platform (v1.0.0)*

[![Next.js 16](https://img.shields.io/badge/Next.js-16.3-black?logo=next.js)](https://nextjs.org/)
[![React 19](https://img.shields.io/badge/React-19.0-61dafb?logo=react)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38bdf8?logo=tailwindcss)](https://tailwindcss.com/)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776ab?logo=python)](https://python.org/)
[![Proprietary: Closed Source](https://img.shields.io/badge/Model-Closed--Source%20Suite-blue.svg)](LICENSE.md)
[![Privacy: Zero--Telemetry](https://img.shields.io/badge/Privacy-Zero--Telemetry-cyan.svg)](PRIVACY.md)
[![Tests: 340 Passing](https://img.shields.io/badge/Tests-340%2F340%20Passed-brightgreen.svg)](walkthrough.md)

---

## 🌟 What is SIR ModPack?

**SIR ModPack** is a proprietary, closed-source high-throughput Minecraft distribution and desktop suite unifying **Modern 26.2 (Fabric 1.21.4)** and **Legacy 1.8.9 (Forge PvP)** into a single cohesive experience. GitHub is utilized exclusively as a reliable distribution channel for high-speed download mirrors of the standalone desktop binaries, installer, and offline packages.

The suite provides standalone desktop binaries, direct native JVM execution, the unified **SIR Master Shader** with crystal wave water and 3D POM relief textures, zero-port multiplayer server hosting, and a Next.js 16 web hub.

---

## 📦 Core Applications

| Application | Binary / Portal | Description |
| :--- | :--- | :--- |
| **SIR Launcher Pro** | `SIR Launcher.exe` | Standalone desktop launcher with native Direct JVM Launch Pipeline, 3D Skin Studio, Quick Presets, and Cloud Self-Healing. |
| **SIR Installer** | `SIR Installer.exe` | Autonomous auto-healing installer with cloud payload streaming, CRC archive validation, and zero-data-loss upgrades. |
| **SIR Server Manager** | `SIR Server Manager.exe` | Dedicated multiplayer server manager with custom CyberSelect menus, live TPS gauges, and Playit.gg zero-port public tunneling. |
| **SIR Web Platform** | [sir-modpack.web.app](https://sir-modpack.web.app) | Next.js 16 web hub with 30 prerendered static routes, AI assistant, live server radar, and skin wardrobe. |

---

## 🎮 Profile Matrix & Presets

SIR ModPack is streamlined into **6 official high-performance profiles**:

```
+-------------------------------------------------------------------------------------------------------------------------+
| ARCHETYPE              | DIRECTORY          | MC VERSION | LOADER       | MEMORY ALLOC | SHADER PACK         | FPS TARGET |
+------------------------+--------------------+------------+--------------+--------------+---------------------+------------+
| 26.2 Ultra Visuals     | 26.2-ultra         | 1.21.4     | Fabric 0.16  | 6GB – 12GB   | SIR_Master_Shader   | 144+ FPS   |
| 26.2 Balanced          | 26.2-balanced      | 1.21.4     | Fabric 0.16  | 4GB – 8GB    | SIR_Master_Shader   | 180+ FPS   |
| 26.2 Performance       | 26.2-performance   | 1.21.4     | Fabric 0.16  | 3GB – 6GB    | OFF (Sodium Boost)  | 500+ FPS   |
| 1.8.9 Ultra Visuals    | 1.8.9-ultra        | 1.8.9      | Forge 2318   | 3GB – 6GB    | SIR_Master_Shader   | 300+ FPS   |
| 1.8.9 Balanced PvP     | 1.8.9-balanced     | 1.8.9      | Forge 2318   | 2GB – 4GB    | OFF (Fast Render)   | 450+ FPS   |
| 1.8.9 Performance      | 1.8.9-performance  | 1.8.9      | Forge 2318   | 2GB – 4GB    | OFF (0ms RawInput)  | 600+ FPS   |
+------------------------+--------------------+------------+--------------+--------------+---------------------+------------+
```

### 1-Click Video Preset Tiers:
- **Ultra Cinematic:** 16-chunk render distance, 3D POM textures, volumetric raytraced shaders (`SIR_Extreme_Shader.zip`).
- **Balanced (144Hz):** 12-chunk view, smooth lighting, and optimized shader pass (`SIR_Balanced_Shader.zip`).
- **Performance (High FPS):** 8-chunk view, disabled shaders, immediate chunk builder (300+ FPS).
- **Competitive PvP (0ms):** 8-chunk view, disabled particle passes, raw mouse input, and instantaneous hit detection (400+ FPS).
- **Potato PC:** 4-chunk view, disabled shadows, fast leaves, and minimal overhead for low-end hardware (120+ FPS).

---

## ⚡ Quickstart Guide

### 1. Launch the Desktop Launcher:
Double-click `SIR Launcher.exe` or execute `SIR ModPack.exe --mode launcher`.

### 2. Deploy or Repair via Installer:
Double-click `SIR Installer.exe` to deploy or verify instances in `%APPDATA%\SIR ModPack\` with automatic cloud payload streaming.

### 3. Host a Dedicated Server:
Double-click `SIR Server Manager.exe` to manage local server instances with 1-click zero-port Playit.gg tunnels.

### 4. Run the Web Platform (Next.js 16):
```bash
cd website-next
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🩺 Diagnostics & Health Verification

Run the automated 6-layer ecosystem doctor to verify binaries, shaders, packs, mods, and instance profiles:

```powershell
# Run ecosystem diagnostics (100% automated health check)
python ecosystem_doctor.py

# Run the complete automated test harness (336 tests across 24 suites)
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📜 Documentation & Legal Policies

- [🏗️ Architectural Blueprint & Specification](PROJECT_ARCHITECTURE_EXPLANATION.md)
- [💎 Full Engineering Walkthrough (Milestones 1–5)](walkthrough.md)
- [📜 Official Changelog & Release Notes](CHANGELOG.md)
- [🔒 Universal Privacy Policy](PRIVACY.md)
- [⚖️ Terms of Service](TERMS.md)
- [🍪 Cookie Policy](COOKIES.md)
- [📜 End User License Agreement (EULA)](EULA.md)
- [🤝 Master Community Agreements](AGREEMENTS.md)
- [📄 Software License](LICENSE.md)

---

## 📬 Contact & Community

- **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **Web Platform:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **GitHub Organization:** [https://github.com/sirahmed8/SIR-ModPack](https://github.com/sirahmed8/SIR-ModPack)

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
