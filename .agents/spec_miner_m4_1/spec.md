# Milestone 4 Specification Document: Web Hub, Firebase & Gemini AI

**Agent ID**: `spec_miner_m4_1`  
**Working Directory**: `D:\Projects\SIR ModPack\.agents\spec_miner_m4_1\`  
**Target Milestone**: Milestone 4 (Features 17, 18, 19, 20)  
**Authoritative Sources**: `ORIGINAL_REQUEST.md`, `PROJECT.md`, `website-next/`, `development/launcher_core/`, `database.rules.json`, `firestore.rules`.

---

## Executive Summary & System Architecture

Milestone 4 establishes the cloud, web, telemetry, and artificial intelligence foundation of the SIR Minecraft Ecosystem. It bridges the desktop native Python runtime with the Next.js 16 Web Platform and Firebase Realtime Database / Cloud Firestore, orchestrated with Gemini AI multi-model technical intelligence.

```
+---------------------------------------------------------------------------------------+
|                                    SIR WEB HUB (Next.js 16)                           |
|  - React 19 + TypeScript Strict + Tailwind CSS v4 + Framer Motion                     |
|  - Static HTML/JS Export (output: "export", unoptimized images, trailingSlash)        |
|  - 30 Pre-rendered Static Routes + Cyber-Dark Glassmorphic UI                         |
+------------------------------------------+--------------------------------------------+
                                           |
                   +-----------------------+-----------------------+
                   |                                               |
                   v                                               v
+------------------------------------+           +------------------------------------+
|     FIREBASE CLOUD HIGHWAY         |           |        GEMINI AI ASSISTANT         |
|  - RTDB /launcherSyncCodes         |           |  - Tier 1: gemini-3.6-flash        |
|  - RTDB /cloud_accounts            |           |  - Tier 2: gemini-3.5-flash-lite   |
|  - RTDB /presence/sessions         |           |  - Tier 3: OpenRouter LLaMA 3.3 70B|
|  - RTDB /analytics/downloads       |           |  - Tier 4: Offline Rule Engine     |
|  - RTDB /releases/latest           |           |  - Web Speech API (TTS En & Ar)    |
|  - Firestore /users                |           |  - 8-Pattern Crash Stack Diagnosis |
|  - Firestore /error_reports        |           |  - Arabic RTL Localization Engine  |
+------------------+-----------------+           +------------------------------------+
                   ^
                   | (HTTP REST / Polling)
                   v
+---------------------------------------------------------------------------------------+
|                       PYTHON LAUNCHER RUNTIME (PyWebView + Core)                      |
|  - LauncherBridgeAPI.sync_cloud_code() -> /launcherSyncCodes/{code}.json              |
|  - AuthService.sync_cloud_accounts()   -> /cloud_accounts.json                        |
|  - AuthService.remove_account()        -> DELETE /cloud_accounts/{name}.json          |
|  - InGameAccountSwitcher (IAS) Sync    -> ias_accounts.json local mirror              |
+---------------------------------------------------------------------------------------+
```

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Web Platform | Next.js 16 Static Export Build | Clean compilation of Next.js 16 App Router to static distribution (`out/`) with zero SSR server dependencies | `next.config.ts`, `package.json`, 30 page routes | 30 static HTML/JS pages in `out/`, 0 hydration errors | Exits with non-zero status code on type errors or dynamic SSR calls | `website-next/next.config.ts`, `package.json` |
| 2 | Web Platform | Strict TypeScript & Hook State | Strict type safety and zero-warning React 19 hook lifecycle management across context and components | React state hooks, DOM event listeners, LocalStorage | Clean typecheck (`tsc --noEmit`), synced RTL/LTR & dark/light theme | Falls back to default state and logs warning on storage access failure | `website-next/lib/context.tsx`, `tsconfig.json` |
| 3 | AI Chatbot | Speech Synthesis (TTS) | Dual-language (Arabic/English) text-to-speech engine using Web Speech API with active visual state | Formatted chat message string, message ID | Audio speech output via browser synthesis; toggle stop/play | Graceful fallback if `speechSynthesis` is unsupported or muted | `website-next/components/AiChatbot.tsx:137` |
| 4 | AI Chatbot | Fullscreen & Mobile Presets | Dynamic window mode toggling between floating resizable box, maximized modal, and 3 mobile height presets (45vh, 72vh, 95vh) | User click on Maximize / Preset button | Responsive CSS layout override (`calc(100vw - 20px)`, `100dvh`) | Restricts dimensions to viewport bounds preventing overflow | `website-next/components/AiChatbot.tsx:353` |
| 5 | AI Chatbot | Bi-Directional Resizing | Mouse & touch edge/corner dragging to customize chat window width (300px-950px) and height (380px-920px) | MouseMove / TouchMove client coordinates | Smooth inline CSS dimension updates | Clamps to min/max boundaries; prevents mobile pull-to-refresh (`touch-action: none`) | `website-next/components/AiChatbot.tsx:163` |
| 6 | AI Chatbot | Rich Markdown & Code Formatting | Custom parser for bold text, inline code chips, markdown links, code snippets, and list bullets | Raw text response from LLM | Structured JSX with neon code chips and safe external links | Renders raw string if format tokens are malformed | `website-next/components/AiChatbot.tsx:317` |
| 7 | AI Chatbot | Smart Action Pills & Quick Prompts | Contextual intent detector and 6 one-click preset prompt buttons for RAM, Shaders, PvP, HAVOC, IAS, and Crashes | Message text content / Button click | Direct navigation link pill (e.g. `/shaders`, `/mods`) | Returns undefined if no trigger keyword detected | `website-next/components/AiChatbot.tsx:59`, `lib/gemini.ts:58` |
| 8 | AI Chatbot | Audio FX & Transcript Export | Haptic click sounds, celebration sound on receipt, single message copy, and full timestamped transcript export | User interaction event | Copied clipboard text, audio chime playback | Stubs silently if sound disabled or clipboard permissions denied | `website-next/components/AiChatbot.tsx:289`, `lib/sound.ts` |
| 9 | Cloud Sync | 6-Digit Launcher Sync Code Protocol | Ephemeral 6-digit sync code generation on web and instant redemption on Python launcher to import Minecraft accounts | `PlayerCloudProfile`, optional Google `uid` | 6-digit numeric string (e.g. `"481920"`), stored in RTDB with 30m TTL | Returns expired error if queried after 30-minute expiration window | `website-next/lib/firebase.ts:853`, `auth_service.py:408` |
| 10 | Cloud Sync | Global Cloud Accounts Mirror | Shared RTDB directory `/cloud_accounts` allowing automatic launcher discovery of web-created profiles | `cleanIgn`, `skinUrl`, `model`, `accountType` | RTDB record at `cloud_accounts/{ign_lower}` | Logs warning and skips unauthenticated writes if rules mismatch | `website-next/lib/firebase.ts:877`, `auth_service.py:380` |
| 11 | Cloud Sync | Multi-Account Cloud Vault | Firestore subcollection and RTDB mapping storing multiple claimed Minecraft identities per user | `uid`, `ClaimedAccountItem` | Persisted records in Firestore `users/{uid}/claimedAccounts` and RTDB | Fails gracefully if user is unauthenticated guest | `website-next/lib/multiAccounts.ts:31` |
| 12 | Telemetry | Real-Time Presence Engine | Live tracking of active web visitors and in-game players using RTDB connection state and `onDisconnect` hooks | Firebase Auth `uid` / anonymous session ID | Public active session count streamed via `onValue` listener | Defaults count to 1 if RTDB snapshot is empty or offline | `website-next/lib/firebase.ts:467` |
| 13 | Telemetry | Atomic Metrics Counters | Concurrent safe counters for installer downloads, bundle downloads, and total error exceptions | Download trigger event / Error event | Atomic increment in RTDB (`rtdbIncrement(1)`) + Firestore log | Silently ignores increment failure if client is offline | `website-next/lib/firebase.ts:406` |
| 14 | Telemetry | Automated Diagnostic Error Logging | Client diagnostic snapshot capturing platform, screen resolution, userAgent, JS heap memory, and error stack | `Error` instance, optional severity & user notes | Structured document in Firestore `error_reports` + RTDB counter bump | Generates fallback local reference ID `LOC-XXXXXX` on network failure | `website-next/lib/error-logger.ts:48`, `firebase.ts:318` |
| 15 | OTA Dispatch | Live Push Releases & Mandatory Updates | Real-time version notification and mandatory update enforcement dispatched from RTDB `/releases/latest` | `ReleaseInfo` payload (version, URLs, changelog) | Instant update alert in launcher and web download cards | Falls back to hardcoded Genesis v1.0.0 release metadata | `website-next/lib/firebase.ts:370`, `PROJECT.md § Cloud Sync` |
| 16 | Broadcast | Global Announcement Channel | Real-time administrative broadcast banner with bilingual title, description, and action button | `BroadcastMessage` payload | Mirrored broadcast alert in RTDB `/broadcasts/active` & Firestore | Clears active banner when dismissed or expired | `website-next/lib/firebase.ts:752` |
| 17 | Gemini AI | 4-Tier Multi-Model Waterfall | Resilient AI query pipeline falling back through multiple LLM providers down to deterministic offline rules | User query prompt, multi-turn history | AI text response, source tag (`gemini-3.6-flash`, `openrouter`, etc.) | Never fails: falls back to offline expert engine on total network outage | `website-next/lib/gemini.ts:90` |
| 18 | Gemini AI | Domain Prompt Tuning & Knowledge Base | Comprehensive system instructions injecting ecosystem architecture (Modern 26.2, Legacy 1.8.9, Shaders, RAM GC flags, IAS) | User query string | Highly contextual, accurate, technical guidance in user's language | N/A (Guaranteed deterministic knowledge base) | `website-next/lib/gemini.ts:8` |
| 19 | Gemini AI | Deep Crash Stack Diagnosis Integration | Automated diagnosis of 8 crash categories (Mixin, Java version, 5 OOM variants, Native DLLs, Missing deps, World corruption, Shaders) | Raw crash log text or latest.log snippet | Precise root cause identification and step-by-step fix recommendation | Flags unknown crash and prompts user to run Launcher Self-Repair | `development/launcher_core/crash_analyzer.py:48` |
| 20 | Gemini AI | Bilingual & Arabic Translation Engine | Dedicated AI utilities for translating changelogs, broadcasts, and user queries to high-tech Arabic with RTL layout | English / Arabic raw draft strings | Strict JSON payload containing `titleAr`, `messageAr`, `headlineAr` | Falls back to original text if JSON parse fails | `website-next/lib/gemini.ts:267` |

---

## Edge Cases

| # | Feature | Input | Observed / Required Behavior |
|---|---------|-------|------------------------------|
| 1 | Next.js Static Export | Dynamic Server Component or Route Handler without static generation | Build fails if dynamic API routes require node server. All routes must be static or client-rendered with static metadata. |
| 2 | Next.js Static Export | Next.js `<Image>` component without `unoptimized: true` | Build fails in static export mode. `next.config.ts` must configure `images: { unoptimized: true }`. |
| 3 | AiChatbot Speech Synthesis | Speech synthesis triggered on Arabic text when system has only English voice | Web Speech API selects closest voice; `utterance.lang = "ar-SA"`. If no Arabic voice installed, browser falls back to default voice. |
| 4 | AiChatbot Speech Synthesis | Rapid double-click on speaker icon while speaking | Cancels ongoing speech immediately (`window.speechSynthesis.cancel()`) and resets `speakingMessageId` to null. |
| 5 | AiChatbot Window Resizing | Dragging resize handle past viewport boundaries on mobile | Dimensions clamped to `Math.min(window.innerWidth - 16, 950)` and `Math.min(window.innerHeight - 20, 920)`. |
| 6 | AiChatbot Auth Gating | Unauthenticated user clicks quick prompt | Chat is locked with Google Sign-In prompt; prompt text is preserved until login completes. |
| 7 | Sync Code Generation | User generates sync code without signing into Google | Sync code is created under global `launcherSyncCodes/{code}` with `ownerUid: "guest"` and expires in 30 minutes. |
| 8 | Sync Code Redemption | Launcher enters expired or non-existent 6-digit code | Python launcher receives `null` from RTDB; displays user-friendly error `"Code expired or not found on website"`. |
| 9 | Sync Code Claiming | Concurrent redemption of the same sync code by multiple launchers | Code resolves successfully; profile is imported; claimed status should be set to true to prevent stale reuse. |
| 10 | Presence Tracking | User closes browser tab abruptly | Firebase Realtime Database triggers `onDisconnect(ref).remove()`, automatically subtracting user from active count. |
| 11 | Presence Tracking | Browser offline / no internet connection | Presence initialization catches error; `subscribeToLivePresence` falls back to minimum count of 1. |
| 12 | Gemini AI Fallback | Gemini 3.6 Flash rate limit (HTTP 429) or quota exhaustion | Automatically catches error, logs warning, and switches to Tier 2 (`gemini-3.5-flash-lite`). |
| 13 | Gemini AI Fallback | Complete internet cutoff / Google AI & OpenRouter unreachable | Falls back to Tier 4 `getOfflineExpertResponse`, returning instant offline answers for RAM, Shaders, PvP, and IAS. |
| 14 | Crash Diagnosis | 0-byte or completely empty crash log file | Crash analyzer returns `{ type: "UNKNOWN", cause: "Empty crash report content", fix: "Check latest.log or run Self-Repair" }`. |
| 15 | Crash Diagnosis | Fatal JVM crash dump (`hs_err_pid*.log`) with missing DLL | Parses `# Problematic frame: # nvoglv64.dll`, identifies NVIDIA GPU driver crash, recommends clean driver reinstall. |
| 16 | Crash Diagnosis | Mixin conflict between custom optimization mods | Extracts offending mod name from `Mixin [...] from mod [mod_name] FAILED` and specifies target game class. |
| 17 | Crash Diagnosis | Incompatible Java runtime version (e.g. running 26.2 on Java 8) | Parses `UnsupportedClassVersionError: class file version 65.0`, identifies Java 21 requirement, prompts to switch JRE. |
| 18 | Error Logger | Client browser with `window.performance.memory` blocked or undefined | Gracefully defaults memory diagnostic field to `"n/a"`, logs platform and userAgent without throwing exceptions. |

---

## Detailed Feature Specifications

### Feature 17: Next.js 16 Web Platform Hardening

#### 1. Build Parameters & Static Export Configuration
- **Framework**: Next.js `16.3.2` (Turbopack engine), React `19.2.8`, TypeScript `5.x`.
- **CSS Architecture**: Tailwind CSS `v4` (`@tailwindcss/postcss: ^4`, `@import "tailwindcss";`).
- **Configuration (`next.config.ts`)**:
  ```ts
  import type { NextConfig } from "next";

  const nextConfig: NextConfig = {
    output: "export",
    trailingSlash: true,
    images: {
      unoptimized: true
    }
  };

  export default nextConfig;
  ```
- **Export Requirements**:
  - Target output directory: `website-next/out/`.
  - All 30 routes statically generated (`○ Static`).
  - Zero dynamic server-only headers, cookies, or database connections in page render phase.
  - Client components explicitly marked with `"use client";`.

#### 2. TypeScript & Code Standards
- `strict: true` in `tsconfig.json`.
- Zero `any` types in data models; explicit interfaces for all API responses, Firestore documents, and RTDB nodes.
- Co-located interface declarations in `lib/firebase.ts`, `lib/gemini.ts`, `lib/storage.ts`, `lib/i18n.ts`.

#### 3. React 19 State & Context Lifecycle (`lib/context.tsx`)
- **Context Contract (`EcosystemContextType`)**:
  - Language: `lang: "en" | "ar"`, `setLang: (lang: Language) => void`, `dir: "ltr" | "rtl"`.
  - Theme: `theme: "dark" | "light"`, `themeMode: "system" | "dark" | "light"`, `setThemeMode()`, `toggleTheme()`.
  - Performance: `perfMode: "cinematic" | "eco"`, `togglePerfMode()`.
  - Sound: `soundFx: boolean`, `toggleSoundFx()`.
  - Cookie Consent: `cookieConsent: CookieConsentState`, `setConsent()`.
  - Auth & Profile: `user: User | null`, `userProfile: UserProfile | null`, `setUserProfile()`.
  - Modals & Reporting: `welcomeOpen`, `errorModalOpen`, `activeErrorData`, `triggerErrorReport()`, `triggerSuggestion()`.
- **Storage Access Resilience**: All `localStorage` and `document.cookie` operations must be wrapped in `try/catch` blocks to prevent exceptions in private browsing or restricted iframe contexts.

---

### Feature 18: Feature-Rich AI Chatbot UI (`AiChatbot.tsx`)

#### 1. Speech Synthesis (Web Speech API)
- **API**: `window.speechSynthesis` & `SpeechSynthesisUtterance`.
- **Language Detection**:
  - Regex test: `/[\u0600-\u06FF]/.test(cleanText)`.
  - If Arabic detected: `utterance.lang = "ar-SA"`.
  - If English: `utterance.lang = "en-US"`.
- **Tuning**: `rate = 1.05`, `pitch = 1.0`.
- **State Management**: `speakingMessageId` tracks active message ID. Active speaker icon pulses with `VolumeX` icon.

#### 2. Dynamic Viewport Modes & Mobile Presets
- **Floating Resizable Mode**: Default width `440px`, height `600px` (clamped to `min-w-300`, `max-w-950`, `min-h-380`, `max-h-920`).
- **Fullscreen Mode**: Stretches to `calc(100vw - 20px)` and `calc(100dvh - 20px)` with `Minimize2` toggle.
- **Mobile Height Presets**:
  - `📱 S`: 45% viewport height (`0.45 * (innerHeight - 30)`).
  - `📖 M`: 72% viewport height (`0.72 * (innerHeight - 30)`).
  - `🚀 L`: 95% viewport height (`0.95 * (innerHeight - 30)`).

#### 3. Touch & Mouse Resizing Engine
- Resizing handles:
  - Top handle: `cursor-ns-resize`, `touch-action: none`.
  - Left handle: `cursor-ew-resize`, `touch-action: none`.
  - Top-Left corner: `cursor-nwse-resize`, `touch-action: none`.
- Prevents text selection during drag: `document.body.style.userSelect = "none"`.
- Prevents mobile pull-to-refresh: `overscroll-behavior: contain`.

#### 4. Formatting, Code Chips & Smart Action Pills
- Markdown parser highlights bold text (`<strong className="text-white font-bold">`), inline code chips (`<code className="px-1.5 py-0.5 rounded-md bg-[#06090e] border border-cyan-500/30 text-cyan-300 font-mono text-[11px]">`), and markdown links (`<a className="text-cyan-400 underline">`).
- **Smart Quick Action Pills**:
  - Shaders: `href: "/shaders"`, `label: "Open Shaders Optical Lab" / "فتح مختبر الشيدرز الضوئي"`.
  - Mods: `href: "/mods"`, `label: "Browse 240+ Mods Suite" / "تصفح كتالوج المودات (240+)"`.
  - Downloads: `href: "/#downloads"`, `label: "Download SIR Launcher v1.0.0" / "تحميل لانشر SIR v1.0.0"`.
  - PvP Trainer: `href: "/trainer"`, `label: "Open PvP Reflex Trainer" / "فتح مدرب الـ PvP ورد الفعل"`.
  - Benchmarks: `href: "/benchmarks"`, `label: "Calculate Rig FPS" / "حساب فريمات جهازك بدقة"`.
  - Skins: `href: "/skins"`, `label: "Open 3D Skin Studio" / "فتح استوديو السكنات ثلاثي الأبعاد"`.
  - Servers: `href: "/servers"`, `label: "Explore Multiplayer Servers" / "استكشاف سيرفرات اللعب الجماعي"`.

#### 5. Layout Integration
- Replace legacy `AiChatWidget.tsx` with `AiChatbot.tsx` in `website-next/app/layout.tsx`.

---

### Feature 19: Firebase Cloud Telemetry & Sync Alignment

#### 1. Realtime Database (RTDB) Schemas
- **Root `launcherSyncCodes/{code}`**:
  ```json
  {
    "code": "481920",
    "userId": "firebase_uid_or_guest",
    "ownerUid": "firebase_uid_or_guest",
    "name": "SirPlayer",
    "ign": "SirPlayer",
    "username": "SirPlayer",
    "uuid": "8b584d4b-70ad-5421-9954-bfda3a41b2c4",
    "skinUrl": "https://mc-heads.net/skin/SirPlayer",
    "model": "classic",
    "accountType": "offline",
    "schemaVersion": 1,
    "createdAt": 1756525764000,
    "expiresAt": 1756527564000,
    "claimed": false
  }
  ```
- **Root `cloud_accounts/{ign_lower}`**:
  ```json
  {
    "name": "SirPlayer",
    "ign": "SirPlayer",
    "type": "offline",
    "accountType": "offline",
    "skinUrl": "https://mc-heads.net/avatar/SirPlayer/32",
    "model": "classic",
    "updatedAt": 1756525764000
  }
  ```
- **Root `presence/sessions/{sessionId}`**:
  ```json
  {
    "online": true,
    "lastSeen": 1756525764000,
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
  }
  ```
- **Root `analytics/downloads`**:
  ```json
  {
    "installer": 1420,
    "bundle": 890
  }
  ```
- **Root `analytics/errors_count`**: integer counter (e.g. `42`).
- **Root `releases/latest`**:
  ```json
  {
    "version": "v1.0.0",
    "releaseDate": "2026-08-21",
    "installerUrl": "https://sir-modpack.web.app/share/SIR_ModPack.exe",
    "bundleUrl": "https://github.com/sir-modpack/sir-modpack-public/releases/download/v1.0.0/SIR_Offline_Bundle_1.1GB.zip",
    "isMandatory": false,
    "changelog": [
      "Initial Public Release of SIR ModPack v1.0.0",
      "Modern 26.2 Fabric with Sodium/Lithium/Iris & SIR Shaders",
      "Legacy 1.8.9 Forge with OptiFine & Patcher",
      "Integrated InGameAccountSwitcher (IAS) for Offline/Cracked accounts",
      "Hardware Power Governor in SIR ModPack Installer mode"
    ],
    "minimumLauncherVersion": "1.0.0"
  }
  ```
- **Root `broadcasts/active`**:
  ```json
  {
    "active": true,
    "type": "update",
    "title": "SIR ModPack v1.0.0 Gold Release Live!",
    "titleAr": "إطلاق النسخة الذهبية من حزمة ومثبت SIR v1.0.0!",
    "message": "Experience 240+ Fabric mods and 1000Hz Legacy Forge PvP now.",
    "messageAr": "استمتع بأكثر من 240 موديلاً ومحرك البفب فائق الاستجابة 1000Hz الآن.",
    "version": "v1.0.0",
    "buttonLabel": "Install Now",
    "buttonLabelAr": "تثبيت الآن",
    "buttonUrl": "/#downloads",
    "timestamp": 1756525764000,
    "author": "SIR Ahmed"
  }
  ```

#### 2. Cloud Firestore Schemas
- **Collection `users/{uid}`**:
  - Fields: `uid`, `displayName`, `email`, `photoURL`, `minecraftUsername`, `accountType`, `skinUrl`, `role`, `createdAt`, `lastLogin`, `downloadCount`.
  - Subcollection `users/{uid}/claimedAccounts/{ign}`:
    - Fields: `name`, `ign`, `skinUrl`, `model`, `accountType`, `type`, `updatedAt`.
- **Collection `error_reports/{reportId}`**:
  - Fields: `errorMessage`, `errorStack`, `componentStack`, `url`, `userAgent`, `userId`, `userEmail`, `clientNotes`, `severity` (`"low"` | `"medium"` | `"critical"`), `status` (`"open"` | `"investigating"` | `"resolved"`), `deviceInfo` (`{ platform, screen, language, memory }`), `timestamp`.
- **Collection `download_events/{eventId}`**:
  - Fields: `downloadType` (`"installer"` | `"bundle"`), `userId`, `timestamp`, `platform`.
- **Collection `changelogs/{changelogId}`**:
  - Fields: `id`, `version`, `date`, `dateAr`, `tag`, `tagAr`, `headline`, `headlineAr`, `categories: [{ title, titleAr, items, itemsAr }]`, `buttonLabel`, `buttonLabelAr`, `buttonUrl`, `createdAt`.

#### 3. Sync Code Generation & Claiming Protocol
1. **Generation (Web Hub)**:
   - User customizes skin in 3D Skin Studio or enters IGN in Account Linking.
   - Web invokes `generateLauncherSyncCode(profile, uid)`.
   - Generates 6-digit random string `Math.floor(100000 + Math.random() * 900000)`.
   - Writes document to RTDB `launcherSyncCodes/{code}` with 30-minute expiration (`Date.now() + 30 * 60 * 1000`).
   - Writes to `cloud_accounts/{ign_lower}`.
   - If user is authenticated, writes to `users/{uid}/launcherSyncCodes/{code}`.
2. **Redemption (Desktop Launcher)**:
   - User enters 6-digit code in Launcher UI -> triggers `LauncherBridgeAPI.sync_cloud_code(code)`.
   - `AuthService.redeem_sync_code(code)` performs HTTP GET to `https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/launcherSyncCodes/{code}.json`.
   - Launcher checks if `expiresAt < now()` or `claimed === true`.
   - Launcher extracts `name` / `ign`, `skinUrl`, `model`.
   - Launcher calls `add_offline_account(name, skin_url, model)`.
   - Launcher updates local accounts list, writes to `ias_accounts.json` for in-game IAS mod, and sets active account.
   - Launcher sends PATCH to `launcherSyncCodes/{code}.json` setting `{"claimed": true, "claimedAt": timestamp}`.

---

### Feature 20: Gemini Multi-Tier AI Assistant

#### 1. 4-Tier Fallback Waterfall Architecture
```
+-------------------------------------------------------------+
|                  User Prompt & Chat History                 |
+------------------------------+------------------------------+
                               |
                               v
               +-------------------------------+
               | Tier 1: Google AI SDK         |
               | Model: gemini-3.6-flash       |
               +---------------+---------------+
                               | (Failure / Rate Limit / Timeout)
                               v
               +-------------------------------+
               | Tier 2: Google AI SDK         |
               | Model: gemini-3.5-flash-lite  |
               +---------------+---------------+
                               | (Failure / Quota Exhaustion)
                               v
               +-------------------------------+
               | Tier 3: OpenRouter API        |
               | Model: meta-llama/llama-3.3-70b|
               +---------------+---------------+
                               | (Network Down / Offline)
                               v
               +-------------------------------+
               | Tier 4: Autonomous Rule Engine|
               | Deterministic Expert DB       |
               +-------------------------------+
```

#### 2. System Instruction Tuning (`SIR_SYSTEM_INSTRUCTION`)
- Injects 5 master technical domains:
  1. **Dual Engine**: Modern 26.2 (Fabric, Sodium, Lithium, Iris, ModernFix, FerriteCore, Distant Horizons) vs Legacy 1.8.9 (Forge, OptiFine, Patcher, HitDelayFix, 1000Hz polling rate raw input).
  2. **Shaders 2.0**: SIR Extreme (2048 Shadowmap, Volumetric Godrays, SSS, SSR, 3D POM, Distant Horizons depth buffer fix) vs SIR Balanced (1024 Shadowmap, steady 144+ FPS).
  3. **Launcher & Installer**: Hardware Power Governor (Max Performance vs Eco Smooth Mode), Firebase Realtime updater, InGameAccountSwitcher (IAS).
  4. **RAM & Java Tuning**: 4GB-6GB optimal allocation (`-Xms4G -Xmx6G`), G1GC flags (`-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200`), >8GB GC latency warning.
  5. **Cloud Hosting & HAVOC**: Cloud server tiering, HAVOC PvP Injector roadmap.

#### 3. Deep Crash Stack Diagnosis Integration
The AI Assistant system knowledge base and crash diagnostic utilities must incorporate the 8 diagnostic patterns identified from `crash_analyzer.py`:
1. **Mixin Conflict**: Regex pattern `Mixin [...] from mod [mod_name] FAILED`. Fix: Update/disable conflicting mod.
2. **Java Version Mismatch**: `UnsupportedClassVersionError` (e.g. class 65.0 vs 52.0). Fix: Switch runtime to Eclipse Temurin 21 LTS.
3. **5 Out-of-Memory Variants**:
   - Heap: `Java heap space` -> Increase RAM to 6GB-8GB.
   - Direct: `Direct buffer memory` -> Add `-XX:MaxDirectMemorySize=2G`.
   - Metaspace: `Metaspace` -> Add `-XX:MaxMetaspaceSize=512M`.
   - GC Overhead: `GC overhead limit exceeded` -> Switch to G1GC and raise heap.
   - Native Thread: `unable to create new native thread` -> Reduce background tasks / lower render distance.
4. **Native Linkage Error**: `UnsatisfiedLinkError` / missing `lwjgl64.dll` / `OpenAL64.dll`. Fix: Run Launcher Self-Repair to extract native DLLs.
5. **Missing Mod Dependency**: `ClassNotFoundException` / `NoClassDefFoundError` for `Fabric API`, `Cloth Config`, `trove4j`, etc. Fix: Download and enable required dependency.
6. **Corrupted World Region**: `RegionFormatException` / `AnvilException` on `r.X.Z.mca`. Fix: Restore backup or prune region with MCA Selector.
7. **Shader & OpenGL Error**: `OpenGLException` / `GL_OUT_OF_MEMORY` / `GLFW error 6554`. Fix: Switch to Balanced shader profile or update GPU drivers.
8. **Native JVM Fatal Dump**: `hs_err_pid*.log` / `nvoglv64.dll` / `atio6axx.dll` / `ig9icd64.dll`. Fix: Clean GPU driver reinstall.

#### 4. Arabic Localization & Administrative AI Tools
- `translateBroadcastToArabic(draft)`: Generates strict JSON `{ titleAr, messageAr, buttonLabelAr }`.
- `translateChangelogToArabic(changelog)`: Translates changelog categories and release notes into natural Arabic.
- `polishAnnouncementWithAI(draft, instruction, tone)`: Refines broadcast announcements into cyberpunk hype or professional alerts.
- `polishChangelogWithAI(draft, instruction)`: Transforms raw commit notes into structured changelogs with tags and category items.

---

## Consistency Matrix: Python Launcher vs Web Platform

| Entity / Protocol | Python Launcher Expectation | Web Hub (`website-next`) Implementation | Status / Resolution |
|-------------------|-----------------------------|------------------------------------------|---------------------|
| Sync Code Path | `launcherSyncCodes/{code}.json` | `launcherSyncCodes/{code}` | **ALIGNED**: Both use `launcherSyncCodes/{code}` root path in RTDB. |
| Sync Code Field Names | Expects `username` or `name` or `ign`, `skinUrl`, `model`, `accountType` | Writes `name`, `ign`, `skinUrl`, `model`, `accountType`, `ownerUid`, `expiresAt` | **HARMONIZED**: Both `name`, `ign`, and `username` populated in payload to guarantee 100% interoperability. |
| Sync Code Claim Status | Checks if code exists and is not null | Writes `schemaVersion: 1`, `expiresAt: timestamp + 30m` | **ENHANCED**: Added `claimed: bool` flag and expiration timestamp verification. |
| Global Cloud Accounts | Queries `cloud_accounts.json` and sends `DELETE cloud_accounts/{name}.json` on remove | Writes `cloud_accounts/{ign_lower}` with `{ name, ign, type, skinUrl, model }` | **ALIGNED**: Matches key casing (`toLowerCase()`) and data schema. |
| In-Game IAS Format | Formats account UUID as `uuid.uuid5(uuid.NAMESPACE_DNS, "OfflinePlayer:" + name)` | In web, `uuid` generated or matched with offline DNS namespace UUIDv5 | **ALIGNED**: Identical UUID generation ensures inventory and player stats match in offline mode. |
| Latest Release Path | `releases/latest.json` | `releases/latest` in RTDB | **ALIGNED**: Schema contains `version`, `installerUrl`, `bundleUrl`, `isMandatory`, `changelog`. |
| Broadcast Banner Path | Listens to `broadcasts/active` | Writes to RTDB `broadcasts/active` & mirrors to Firestore | **ALIGNED**: Real-time push without polling overhead. |
| Error Reporting | Catches launcher crashes, formats diagnostic stack trace | Writes to Firestore `error_reports` and increments RTDB `analytics/errors_count` | **ALIGNED**: Shared severity and status fields (`open`, `investigating`, `resolved`). |

---

## Verification & Test Plan

1. **Next.js 16 Static Build Verification**:
   - Command: `cd website-next && npm run build`
   - Success Criteria: Zero compile errors, zero TypeScript errors (`tsc --noEmit`), 30 static pages generated in `out/`.
2. **AiChatbot Component Verification**:
   - Validate `AiChatbot.tsx` is imported in `app/layout.tsx`.
   - Verify speech synthesis triggers without exceptions and detects Arabic/English correctly.
   - Verify drag resizing and maximize toggles function smoothly on both desktop and mobile viewports.
3. **Firebase & Cloud Sync Verification**:
   - Generate sync code on web via `generateLauncherSyncCode({ ign: "TestPlayer", model: "classic", skinUrl: "..." })`.
   - Query endpoint `GET /launcherSyncCodes/{code}.json` from Python test script and verify JSON response.
   - Validate presence tracker connects and cleans up session on disconnect.
4. **Gemini AI Waterfall Verification**:
   - Execute test query against `askSirAIDetailed("What are optimal RAM settings?")`.
   - Verify response returns valid text, source identifier, and suggested action pill (`/benchmarks` or `/shaders`).
   - Verify Tier 4 offline fallback returns appropriate response when API keys are disabled.
