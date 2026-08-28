# 📜 SIR ModPack — Official Ecosystem Changelog
### *Unified Minecraft Experience • Semantic Versioning (v1.0.0 • August 2026)*

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
