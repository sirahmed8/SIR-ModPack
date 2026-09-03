# 🤝 SIR ModPack — Master User & Distribution Agreements
### *Version 1.0.0 (26.2) • Effective September 2026 • Community Governance & Security Framework*

---

## 🏛️ 1. Scope & Framework
This document outlines the **Master User Agreements, Community Standards, Fair Play Guidelines, and Distribution Protocols** governing the entire SIR Minecraft Ecosystem.

---

## 🎮 2. Multi-Profile Gameplay & Competitive Integrity Agreement
1. **Multiplayer Server Compatibility & Fair Play Protocol:**
   - The SIR Ecosystem focuses strictly on client-side rendering optimization (Sodium, Iris, ModernFix, FerriteCore, OptiFine HD U M5), memory compaction, and local input responsiveness.
   - The software does not modify server-side movement packets, reach, or server-side hit detection mechanics. Experimental modules (e.g. HAVOC) are intended exclusively for offline practice and private development environments.
   - Users agree to adhere to specific multiplayer server rules (including Hypixel, Minemen Club, GommeHD, and Bedwars practice servers). Users are solely responsible for ensuring their active client mods adhere to each server's specific modification rules.
2. **Offline & Local Sandbox Identity Management:**
   - Offline UUIDv5 generation is provided strictly for private local LAN play, custom sandbox development, and educational environments.
   - Users acknowledge that accessing official Mojang authentication services requires an official, purchased Minecraft account. The ecosystem does not facilitate copyright infringement or bypass official account verification.

---

## ⚡ 3. Software Distribution & Binary Integrity Agreement
1. **Official Distribution Channels:**
   - Binaries and releases are officially published exclusively via:
     - Official Website: [https://sir-modpack.web.app](https://sir-modpack.web.app)
     - Developer Repository: [https://github.com/sirahmed8/SIR-ModPack](https://github.com/sirahmed8/SIR-ModPack)
     - Developer Linktree: [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
2. **Autonomous Auto-Healing & Payloads:**
   - The SIR Installer and Launcher include built-in CRC32 / SHA-256 integrity validators.
   - If corrupted files or missing native DLLs are detected, the ecosystem automatically pulls clean replacement assets over TLS 1.3 encryption.

---

## 🔒 4. Privacy, Security & Data Sovereignty Agreement
- **Zero-Telemetry Protocol:** No behavioral telemetry, location data, or keystroke tracking is transmitted.
- **Hardware Telemetry Protection:** Hardware monitoring (`GlobalMemoryStatusEx`, `GetSystemTimes`) runs strictly in local process memory to manage JVM memory compaction and prevent lag spikes.
- **Safe Storage Protocol:** All settings and accounts are safely stored in `%APPDATA%\SIR ModPack\` with atomic staging to eliminate corrupted files.

---

## 🤝 5. Community & Developer Relations
- **Suggestions & Issues:** Feature requests, performance benchmarks, and bug reports may be submitted through the Web Portal Error Reporter or GitHub issues.
- **Creator Rights:** All mod developers and shader artists receive full credit and attribution in [PROJECT_ARCHITECTURE_EXPLANATION.md](PROJECT_ARCHITECTURE_EXPLANATION.md).

---

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
