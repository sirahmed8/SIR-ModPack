# 🚀 SIR Launcher — Custom Client Architecture & Build Guide

This document details the customization and build pipeline for **SIR Launcher**, engineered from the Prism Launcher codebase located at `D:\Projects\SIR ModPack\PrismLauncher-develop`.

---

## 🎨 1. Rebranding & Visual Identity

| Component | Target Source Path | Customization Applied |
| :--- | :--- | :--- |
| **Application Name** | `launcher/CMakeLists.txt` / `BuildConfig.h.in` | Changed `Prism Launcher` to **`SIR Launcher`** |
| **Window Title & Org** | `launcher/Application.cpp` | `Launcher::AppName = "SIR Launcher"`, `OrgName = "SIR Team"` |
| **Desktop Icon** | `program_info/prismlauncher.ico` & `.png` | Replaced with official glowing **SIR Crystal Emblem** |
| **App Metainfo** | `program_info/org.prismlauncher.PrismLauncher.metainfo.xml.in` | Set application summary: *"The Ultimate High-Performance Minecraft Client"* |

---

## ⚡ 2. Pre-Configured Engine Presets

1. **Memory Allocation:**
   * Default Minimum: `6144 MB` (6 GB)
   * Default Maximum: `8192 MB` (8 GB)
   * Prevents heap warnings and ensures optimal Generational ZGC operation.
2. **Pre-Bundled Instance Presets:**
   * `SIR Ultimate (Modern 26.2)` — 104+ Fabric mods + Distant Horizons + Master Bliss Shaders.
   * `SIR Legacy (1.8.9 PvP)` — High FPS OptiFine engine (7000+ FPS).

---

## 🔨 3. Build & Compilation Pipeline

### Prerequisites:
* **CMake 3.22+**
* **Ninja Build System**
* **Qt 6.6+ (Core, Gui, Widgets, Network, Concurrent, Svg)**
* **MSVC C++ 2022 (v143 toolset) or Clang/GCC**

### Build Commands:
```powershell
cd "D:\Projects\SIR ModPack\PrismLauncher-develop"
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release --parallel
```
The output binary `SIRLauncher.exe` will be located in `build/bin/Release/`.
