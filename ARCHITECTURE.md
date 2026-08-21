# 🌟 SIR ModPack Ecosystem — Complete Architectural & Technical Specification
> **CRITICAL INSTRUCTION FOR ALL AI AGENTS & ENGINEERS:**  
> Read this document completely before modifying any part of the SIR ModPack codebase. It describes the authoritative architecture, runtime flows, file mappings, authentication systems, shaders, installer logic, and cloud integrations.

---

## 1. Executive Summary & Core Mission
**SIR ModPack** is a comprehensive, production-grade Minecraft ecosystem that unifies three distinct gameplay paradigms into a single high-performance distribution:
1. **Modern 26.2 (Fabric Engine):** Ray-traced visuals, 2048 HD volumetric Bliss shaders, 32x PBR Parallax Occlusion Mapping (POM), Fresh Animations, and Distant Horizons LOD rendering with 144+ to 240+ FPS.
2. **Legacy 1.8.9 (Forge PvP Suite):** Zero-delay hit-registration, old 1.7 combat animations, raw mouse polling, OptiFine HD, Patcher memory leak fixes, and 500+ to 1000+ FPS.
3. **Vanilla+ Custom Engine (Modular Multi-Version):** Flexible custom instance creator supporting any Minecraft release (26.2, 1.21.4, 1.20.1, 1.19.2, 1.16.5, 1.12.2, 1.8.9) with modular mod, shader, and resource pack pickers.

---

## 2. Global Repository & Deployment Topography
- **Public Portal & Releases:** `https://sir-modpack.web.app` (Firebase Hosting)
- **Public GitHub Repo:** `https://github.com/sirahmed8/SIR-ModPack.git` (Branch: `main`)
- **Private Source Code Repo:** `https://github.com/sirahmed8/SIR-ModPack-private.git` (Branch: `master`)
- **Admin / Owner Identity:** `a7medorabe7@gmail.com`
- **Developer Linktree:** `https://linktr.ee/sir.ahmed`

---

## 3. Directory Layout & File Responsibilities

```
D:\Projects\SIR ModPack\
├── development\
│   ├── installer_source\
│   │   └── SIR_Installer_GUI.py      # Tkinter Master GUI, Hardware Governor & Cleaner
│   └── SIR Installer.spec            # PyInstaller build specification
├── SIR Package\
│   ├── SIR Installer.exe             # Recompiled silent installer executable (noconsole)
│   ├── SIR Icon.ico                  # Cyber-cyan crystal high-res icon
│   └── SIR Launcher\                 # Portable white-labeled launcher distribution
├── website-next\                     # Next.js 16 App Router Web Platform
│   ├── app\
│   │   ├── layout.tsx                # Root layout with Vercel Analytics, SEO Schema & Favicons
│   │   ├── page.tsx                  # Main landing page combining all sections
│   │   ├── globals.css               # Cyber-dark glassmorphism & Light Mode theme rules
│   │   ├── admin\page.tsx            # Owner / Admin Live Telemetry Console
│   │   └── changelog\page.tsx        # Standalone full changelog page
│   ├── components\
│   │   ├── Navbar.tsx                # Top glass navbar with user pill & language toggle
│   │   ├── HeroDownload.tsx          # 1-Click Gated Download matrix
│   │   ├── ProfilesMatrix.tsx        # Modern, Legacy & Vanilla+ 3-tab matrix + Customizer modal
│   │   ├── AccountLinking.tsx        # Google-backed Cracked Auth, Skin Stealer & IAS Sync
│   │   ├── ServerHostingPortal.tsx   # SaaS Cloud Server configurator (Aternos fallback)
│   │   ├── HavocPortal.tsx           # Solid obsidian-purple HAVOC PvP Engine spotlight
│   │   ├── ChangelogSection.tsx      # Main page bottom changelog (last 2 + full history modal)
│   │   └── AiChatWidget.tsx          # Gemini 3.5 AI Assistant with spring physics & resize handle
│   └── lib\
│       ├── firebase.ts               # Google Auth, Firestore, RTDB listeners
│       ├── gemini.ts                 # AI Assistant dynamic model resolution
│       ├── context.tsx               # Global bilingual (ar/en) & theme (dark/light) context
│       └── error-logger.ts           # Automatic Firestore error reporting boundary
├── instances\
│   ├── 26.2\minecraft\               # Modern Fabric instance (Iris, Sodium, Lithium, IAS)
│   └── 1.8.9\minecraft\              # Legacy Forge instance (OptiFine, Patcher, 1.7 Animations)
├── shaderpacks\
│   ├── SIR_Extreme_Shader.zip        # Max fidelity Bliss shader (2048 shadows, POM, SSS)
│   └── SIR_Balanced_Shader.zip       # 144+ FPS Bliss shader (1024 shadows, identical water/sun)
└── resourcepacks\
    ├── SIR_Ultimate_Pack.zip         # 32x PBR POM normal/specular maps + Fresh Animations
    └── SIR_Legacy_32x.zip            # Clean 32x PvP pack with low fire and transparent GUI
```

---

## 4. Minecraft Identity & IAS Authentication Architecture
1. **Google-Backed Cracked Identity:**
   - Logging in with Google assigns a verified owner UID.
   - The user selects a unique Cracked In-Game Name (IGN).
   - **Mojang Conflict Protection:** Prevents claiming registered official Mojang usernames (e.g. `Notch`, `Dream`, `Technoblade`) for cracked profiles.
   - **Skin Stealer & Custom PNG Uploader:** Users can fetch any player's skin texture by typing their IGN, or upload a custom `.png` skin.
   - **IAS Profile Export:** Automatically writes `account-switcher.json` compatible with `IAS-9.0.7+26.2-fabric.jar` and `InGameAccountSwitcher-Forge-1.8-8.0.1.jar`.
2. **Official Microsoft Authentication:**
   - Guides users through Microsoft OAuth / Device Code authorization inside SIR Launcher.

---

## 5. Desktop Silent Installer (`SIR_Installer_GUI.py`)
- **PyInstaller Build Command:**
  ```powershell
  py -m PyInstaller --onefile --noconsole --name="SIR Installer" --icon="D:\Projects\SIR ModPack\SIR Package\SIR Icon.ico" "D:\Projects\SIR ModPack\development\installer_source\SIR_Installer_GUI.py" --distpath="D:\Projects\SIR ModPack\SIR Package"
  ```
- **4-Target Platform Selection:**
  1. `opt_sir_launcher`: Full multi-version modern and legacy instance deployment.
  2. `opt_lunar`: Dedicated 1.8.9 competitive profile deployment for Lunar Client.
  3. `opt_both`: Simultaneous dual-launcher configuration.
  4. `opt_vanilla`: Clean custom instance on any version (26.2, 1.21.4, 1.20.1, 1.16.5, 1.8.9) with modular mod pickers.
- **Hardware Power Governor:**
  - `⚡ Max Performance Mode`: Uses all available CPU threads for instantaneous extraction.
  - `🍃 Smooth / Eco Mode`: Limits extraction threads to 2 and sets `IDLE_PRIORITY_CLASS` so the user's PC experiences 0% lag or freezing.
- **Deep Storage Cleaner:**
  - Scans and purges `_MEI*` temp folders, `.shadercache`, `.iris`, crash dumps, and old `AppData\Roaming\PrismLauncher` remnants.

---

## 6. Web Platform Design Tokens & UX
- **Accent Neon:** `#00e5ff` (Electric Cyan)
- **Secondary Neon:** `#38ef7d` (Vibrant Emerald)
- **Accent Purple:** `#c084fc` (Electric Violet for HAVOC & Vanilla+)
- **Dark Mode Background:** `#07090e` / `#0e121c` with seamless gradient-masked cyber grid (`mask-image: linear-gradient(to bottom, black 75%, transparent 100%)`).
- **Light Mode Overrides:** Crisp white glass panels (`rgba(255,255,255,0.92)`), deep slate headers (`#0f172a`), and high-contrast dark cyan/emerald typography.
- **Bilingual Engine:** Automatic Arabic (RTL) and English (LTR) layout switching with zero horizontal overflow or font shifting.

---

## 7. Cloud Services & Realtime Telemetry
- **Firebase Hosting:** `https://sir-modpack.web.app`
- **Firebase Realtime Database (RTDB):**
  - `/releases/latest.json`: Push update triggers with semantic versioning.
  - `/telemetry/downloads/installer`: Live installer download counter.
  - `/telemetry/downloads/bundle`: Live offline bundle download counter.
  - `/presence/active_users`: Live socket heartbeat counter.
- **Cloud Firestore:**
  - `error_reports/`: Client crash reports with stack traces and user agent.
  - `users/`: Google profiles, linked Minecraft IGNs, and skin URLs.
- **Vercel Web Analytics:** Real-time visitor tracking via `@vercel/analytics/react`.

---
*Authored and verified for the SIR ModPack Ecosystem — Production Standard v1.0.0.*
