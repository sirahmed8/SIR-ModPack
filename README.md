# 💎 SIR ModPack — The Ultimate Minecraft Experience
### *Unified Minecraft Platform • Desktop Suite • Shaders • Web Platform (v1.0.0)*

[![Next.js 16](https://img.shields.io/badge/Next.js-16.3-black?logo=next.js)](https://nextjs.org/)
[![React 19](https://img.shields.io/badge/React-19.0-61dafb?logo=react)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8?logo=tailwindcss)](https://tailwindcss.com/)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776ab?logo=python)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE.md)
[![Privacy: Zero--Telemetry](https://img.shields.io/badge/Privacy-Zero--Telemetry-cyan.svg)](PRIVACY.md)

---

## 🌟 What is SIR ModPack?
**SIR ModPack** is an enterprise-grade Minecraft distribution and desktop ecosystem unifying **Modern 26.2 (Fabric 1.21.4)** and **Legacy 1.8.9 (Forge/Paper PvP)**. It provides one public dispatcher executable, custom shaders, 3D POM textures, zero-port server hosting, and a high-performance web platform.

The public desktop entrypoint is **`SIR ModPack.exe`**. It opens the requested internal mode with `--mode launcher`, `--mode installer`, or `--mode server`. Per-user state is stored in `%APPDATA%\SIR ModPack\`, while Prism keeps official Microsoft credentials in its private local account store.

---

## 📦 Core Applications

| Application | Binary / Portal | Description |
| :--- | :--- | :--- |
| **SIR ModPack dispatcher** | `SIR ModPack.exe` | One public EXE. Use `--mode launcher`, `--mode installer`, or `--mode server` for the three desktop modes. |
| **SIR Web Platform** | `sir-modpack.web.app` | Next.js 16 portal with 29 prerendered static routes, bilingual RTL/LTR engine, modular architecture, and military-grade input validation. |

---

## 📜 Documentation & Legal Policies

- [🏗️ Project Architecture & Engineering Guide](PROJECT_ARCHITECTURE_EXPLANATION.md)
- [📜 Official Changelog & Release Notes](CHANGELOG.md)
- [🔒 Universal Privacy Policy (v2026.2)](PRIVACY.md)
- [⚖️ Terms of Service & EULA (v2026.2)](TERMS.md)
- [🍪 Cookie & Local Storage Policy (v2026.2)](COOKIES.md)
- [💎 Full Project Overview](PROJECT.md)

---

## ⚡ Quickstart

### 1. Run SIR ModPack:
Double-click `SIR ModPack.exe`, or use one of these explicit modes:

```text
SIR ModPack.exe --mode launcher
SIR ModPack.exe --mode installer
SIR ModPack.exe --mode server
```

### 2. Run the Next.js Web Platform:
```bash
cd website-next
npm run dev
# Open http://localhost:3000
```

---

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
