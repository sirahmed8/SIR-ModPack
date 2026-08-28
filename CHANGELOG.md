# 📜 SIR ModPack — Official Ecosystem Changelog
### *Unified Minecraft Experience • Semantic Versioning (v1.0.0 • August 2026)*

---

## 🚀 [v1.0.0-PRO • Update 4] — Auth-Gated Ecosystem, SIR Core v1.0.0 & Professional Showcase (August 2026)

### 🔒 1. Web Platform Authentication Barrier & Feature Protection
- **Global `AuthGate` Architecture:** Protected all specialized ecosystem modules (`/capes`, `/builder`, `/benchmarks`, `/leaderboards`, `/trainer`, `/seeds`, `/server-guide`, `/skins`, `/profiles`) behind a cyber-dark Google Authentication gate.
- **Download & Account Creation Protection:** Requires Google login before streaming installer/bundles or creating/syncing cracked/offline profiles.
- **AI Chatbot Protection:** Chatbot input area is gated with a 1-click Google Sign-In button for verified users.
- **Publicly Accessible Pages:** Kept Home landing page (`/`), FAQ (`/faq`), Privacy Policy (`/privacy`), Terms of Service (`/terms`), Cookie Policy (`/cookies`), and Changelog (`/changelog`) freely accessible to all visitors.

### ⚡ 2. `SIR_Core-fabric-26.2.jar` (v1.0.0 Pro)
- **Standardized Versioning:** Renamed and recompiled as **v1.0.0** with full backward and forward compatibility (`>=1.20.0`).
- **JVM Memory Governor Daemon:** Background daemon monitors heap memory usage every 60s and compactor threshold (>88%) to prevent micro-stutters and frame drops.
- **3-Way Synergy Bridge:** Automatic optical shader hooks, 3D POM texture hooks, and hardware power tuning.

### 🎨 3. Launcher Profiles, Resource Packs & SIR Custom Mods Showcase
- **Profile Photo Banners & Badges:** Every instance profile (`SIR 26 Ultra`, `Balanced 144+ FPS`, `Competitive Speed`, `Legacy 1.8.9 Cinematic`, `Legacy 1.8.9 Balanced PvP`, `Legacy 1.8.9 Battle Suite`, `Sandbox Profile`) now includes a high-res themed banner, bulleted feature list, and documentation link.
- **Official SIR Custom Mods Suite:** Added rich showcase cards in the launcher mods tab for `SIR Core (v1.0.0)`, `HAVOC PvP Injector`, `Super Secret Settings Fix`, `PlayerAPI Integration`, `Sharpness Particles FX`, and `InGameAccountSwitcher (IAS)`.
- **Resource Packs Studio:** Enriched `SIR_Ultimate_Pack.zip` and `SIR_Legacy_32x.zip` with dedicated 3D POM badges, feature breakdowns, and specification links.

### 👕 4. 3D Cape Showroom & Classic Steve Preview
- **Local Standard `64x32` Cape Textures:** Generated 6 pixel-perfect Minecraft cape textures (`sir_founder.png`, `ender_dragon.png`, `optifine_banner.png`, `lunar_astral.png`, `cherry_blossom.png`, `diamond_gladiator.png`) eliminating cross-origin CORS errors.
- **Classic Normal Steve Skin:** Bundled authentic standard Minecraft Steve skin texture (`/skins/steve.png`) and cleaned search bar placeholder.

---

## 🚀 [v1.0.0-PRO • Update 3] — Cloud Self-Healing Engine & 20+ GB Bloat Elimination (August 2026)

### 🧹 1. 20+ GB Bloat Elimination & Massive 12+ GB Storage Recovery
- **Consolidation of Duplicate Instances:** Purged over 24 redundant nested asset duplicates across temporary build folders, test instances, and `SIR Package/SIR Launcher/` (recovering over 12 GB of disk space).
- **Lightweight Repository Footprint:** Optimized Git packfiles and removed duplicate runtime caches, shrinking `public_repo` from **1.97 GB down to 323 MB** while keeping 100% of all source code, configs, shaders, and packs intact.
- **C: Drive Temp & Cache Cleanup:** Safely cleaned PyInstaller build artifacts and `%TEMP%` junk files.

### 🌐 2. Cloud Self-Healing Downloader Engine
- **Standalone `SIR Installer.exe` (16 MB):** Added autonomous payload streaming from Cloud CDN (GitHub Releases). If run as a standalone 16 MB executable without local bundles, it streams modular zip archives (`payload_mods_26.2.zip`, `payload_mods_1.8.9.zip`, `payload_packs.zip`, `payload_shaders.zip`, `payload_configs.zip`) with live chunk streaming, speed calculation (`MB/s`), and progress bar feedback.
- **Launcher Profile Auto-Healing:** Added `InstanceService.heal_instance_if_needed()` in `SIR Launcher`. Before game launch, it checks if mods, configs, or instance definitions are intact, auto-recovering any missing files from the cloud within seconds.

### 🛡️ 3. Anti-Compromise & Anti-Corruption File Integrity Verification
- **Cryptographic & Structural CRC Checks:** Integrated `is_valid_zip()` in the installer.
- **Auto-Quarantine & Recovery:** If any local asset archive is corrupted, 0 bytes, or compromised, the installer quarantines it and automatically fetches a fresh, verified copy from the Cloud CDN.

### ⚡ 4. Comprehensive Mod Suite & High-Performance Optimization Tuning
- **Fabric/Forge Mod Audit:** Audited all 240+ Modern 26.2 Fabric mods and 57 Legacy 1.8.9 Forge mods. Safely eliminated a misplaced 1.8.9 Forge jar from the 26.2 Fabric folder.
- **High-Performance Presets:** Generated and synchronized pre-configured optimization files across both profiles:
  - `immediatelyfast.json`: Accelerated HUD, font, particle, and text rendering.
  - `ferritecore.properties`: Aggressive RAM reduction and memory compaction.
  - `modernfix-mixins.properties`: Dynamic resource allocation and fast load mixins.
  - `entity_culling.json`: Async occlusion culling for offscreen entities.
  - `betterfps.json`: Riven's Half algorithm for maximum 1.8.9 PvP framerates.
  - `options.txt` & `iris.properties`: Pre-configured for 260 Max FPS, gamma 1.0, and `SIR_Balanced_Shader.zip`.

---

## 🚀 [v1.0.0-PRO • Update 2] — Full Platform Polish & Visual Standardization (August 2026)

### 🎨 1. UI/UX Evolution & Custom CyberSelect Engine
- **Custom CyberSelect Dropdowns in Server Manager:** Replaced native square `<select>` elements in `SIR Server Manager` (Difficulty, Gamemode, Online Mode, Language) with custom Cyber-Dark/Light Glassmorphic dropdowns featuring `rounded-2xl` curvature, smooth spring open/close animations, and active neon cyan indicators.
- **MOTD Formatting Decoder:** Automatically decodes and displays color codes and formatting escapes cleanly in the server properties panel.
- **Standardized Desktop App Dimensions:** Standardized all 3 desktop applications (`SIR Launcher.exe`, `SIR Server Host.exe`, `SIR Installer.exe`) to uniform `1180x760` window dimensions with DPI-aware workarea centering.
- **Interactive Profile Selection in Hardware Benchmarks (`/benchmarks`):** Added dynamic profile dropdown allowing users to calculate predicted FPS, 1% lows, and frame times for *Modern 26.2 Ultra Extreme*, *Balanced 144+ FPS*, *Competitive Speed*, *Legacy 1.8.9 PvP*, *Vanilla 1.21.4*, and *Vanilla 1.8.9*.
- **Continuous Explorer Pagination (`/mods`, `/servers`, `store.js`):** Added interactive "View More Projects" / "View More Servers" pagination buttons with live remaining counters and smooth loading states across both the web platform and desktop launcher store.

### 🛡️ 2. Fabric Loader Engine & Mod Stability
- **Fabric Virtual Mod ID Resolution:** Resolved `e4mc` and third-party mod dependency errors by injecting `"provides": ["fabric", "fabric-api"]` into `fabric.mod.json` within `fabric-api-0.158.0+26.2.jar`.
- **Synchronized Mod Bundles:** Deployed patched Fabric API JAR across local profile directories, master distribution archives, and `%APPDATA%\SIR ModPack\instances\26.2\minecraft\mods\`.
- **Installer Startup & EULA Flow Fix:** Enhanced `SIR Installer` with non-blocking hardware initialization and instant EULA switch unlocking for the `Next Step ->` navigation flow.

### 🌐 3. Web Platform & Legal Policy Dual-Theme Polish
- **Dual-Theme Support on All Legal Pages:** Updated `Privacy Policy` (`/privacy`), `Terms of Service` (`/terms`), and `Cookie Policy` (`/cookies`) with seamless light and dark mode styling.
- **Resource Packs & Shaders Optical Lab:** Modernized `/packs` and `/shaders` with standardized `Modern 26.2 (Fabric)` branding, dual-theme containers, and 3D POM comparison matrices.
- **3D Skin & Cape Studio:** Angled default camera rotation (`Math.PI * 0.85`) to immediately showcase custom 3D capes upon loading, and switched default character preview to Steve.

---

## 🚀 [v1.0.0-PRO] — Initial Major Release (August 2026)

### 🛡️ 1. Multi-Layer Security Hardening & Zero-Vulnerability Engine
- **Centralized Security Engine (`lib/security.ts`):** Runtime validation enforcing strict alphanumeric regex for Minecraft IGNs (`/^[a-zA-Z0-9_]{3,16}$/`) and 6-digit sync pairing codes (`/^\d{6}$/`).
- **Input & HTML Sanitization:** Automatic stripping of dangerous control characters, scripts, and injection payloads (`sanitizeInput`, `sanitizeHtml`, `sanitizeObject`).
- **HTTP Security Headers:** Injected `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`, and strict permissions policies across all Next.js API routes.
- **Loopback Origin Verification:** Local pairing bridge enforces `ALLOWED_ORIGINS` and cryptographic constant-time comparison (`secrets.compare_digest`).

### 🧩 2. Anti-Monolith Modular Architecture
- **Decomposed Navbar:** Replaced monolithic component with dedicated, isolated modules (`BroadcastBanner.tsx`, `NotificationsPanel.tsx`, `UserAccountDropdown.tsx`, `NavLinks.tsx`).
- **Decomposed Account Studio:** Replaced 960-line monolithic manager with dedicated components (`SkinViewer3D.tsx`, `PresetSkinsGrid.tsx`, `MultiAccountManager.tsx`).
- **Spring Physics System:** Applied standard `--ease-spring: cubic-bezier(0.16, 1, 0.3, 1)` to all cards, dropdowns, modals, and interaction states.

---

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
