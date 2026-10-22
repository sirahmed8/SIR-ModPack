# Handoff Report: Milestone 4 Specification Mining

**Agent**: `spec_miner_m4_1`  
**Working Directory**: `D:\Projects\SIR ModPack\.agents\spec_miner_m4_1\`  
**Date**: 2026-08-30  
**Handoff Type**: Hard Handoff (Task Complete)

---

## 1. Observation

1. **Authoritative Contracts & Requirements**:
   - `D:\Projects\SIR ModPack\.agents\ORIGINAL_REQUEST.md`: Lines 22-26 define R3 (Next.js 16 App Router platform with React 19, TypeScript strict typing, Tailwind CSS, Lucide icons, Framer Motion; Firebase Realtime Database & Firestore for live telemetry, user error reporting, OTA update dispatching; Gemini AI Assistant chatbot with automatic fallback routing for real-time user assistance, profile tuning, and crash diagnosis).
   - `D:\Projects\SIR ModPack\PROJECT.md`: Lines 44-47 outline Features 17-20 (Next.js 16 Web Platform Hardening, Feature-Rich AI Chatbot UI, Firebase Cloud Telemetry & Sync Alignment, Gemini Multi-Tier AI Assistant); lines 71-76 define the Cloud Sync Highway interface contract (`launcherSyncCodes/{6_digit_code}` and `releases/latest`).

2. **Web Application Architecture (`website-next/`)**:
   - `website-next/package.json`: Lines 11-24 confirm dependencies: `next: 16.3.2`, `react: 19.2.8`, `@google/generative-ai: ^0.24.0`, `firebase: ^11.3.1`, `framer-motion: ^12.4.7`, `tailwindcss: ^4`, `@tailwindcss/postcss: ^4`.
   - `website-next/next.config.ts`: Lines 1-11 configure static export parameters:
     ```ts
     const nextConfig: NextConfig = {
       output: "export",
       trailingSlash: true,
       images: { unoptimized: true }
     };
     ```
   - `npx tsc --noEmit` executed in `website-next/` passed with exit code `0`.
   - `npm run build` executed in `website-next/` passed cleanly in `2.2s`, statically prerendering all 30 application routes into `out/`.

3. **AI Chatbot & Audio/Speech Synthesis (`website-next/components/`)**:
   - `website-next/components/AiChatbot.tsx`:
     - Line 137: Implements Web Speech API text-to-speech engine (`SpeechSynthesisUtterance`), pitch/rate tuning, and regex language detection (`/[\u0600-\u06FF]/.test(cleanText) ? "ar-SA" : "en-US"`).
     - Line 163: Implements bi-directional mouse and touch window resizing (`handleStartResize`, `handleMoveResize`) bounded between 300px-950px width and 380px-920px height.
     - Line 353: Implements responsive fullscreen maximization and 3 mobile height presets (45vh, 72vh, 95vh).
     - Line 317: Implements formatted rendering of bold text, neon code chips, hyperlinks, and smart action pills.
     - Line 289: Implements single-message clipboard copy and full transcript export.
   - `website-next/app/layout.tsx`: Line 9 currently references legacy `AiChatWidget.tsx` rather than `AiChatbot.tsx`.

4. **Firebase Cloud Highway & Database Rules**:
   - `website-next/database.rules.json`: Lines 9-12 declare root `launcherSyncCodes` with `.read: true, .write: true`. Lines 35-43 define `presence/sessions/$sessionId`. Lines 13-16 define `releases`.
   - `website-next/lib/firebase.ts`:
     - Lines 853-899: `generateLauncherSyncCode(profile, uid)` creates 6-digit code with 30m TTL, writing to `launcherSyncCodes/{code}`, `cloud_accounts/{cleanIgn.toLowerCase()}`, and `users/{uid}/launcherSyncCodes/{code}`.
     - Lines 406-422: `recordDownloadMetric(type, userId)` atomic increment in RTDB `analytics/downloads/{type}` + Firestore `download_events`.
     - Lines 467-510: `initPresenceTracker(userId)` and `subscribeToLivePresence(callback)` using `presence/sessions`.
     - Lines 318-340: `submitErrorReport(report)` to Firestore `error_reports` and RTDB `analytics/errors_count`.
     - Lines 370-401: `getLatestRelease()` and `publishReleaseToRTDB(release)` at `releases/latest`.

5. **Python Launcher Integration (`development/launcher_core/`)**:
   - `development/launcher_core/cloud_sync_service.py`: Line 17 queries `https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/launcherSyncCodes/{code}.json`.
   - `development/launcher_core/auth_service.py`:
     - Line 414: `redeem_sync_code(code)` fetches code JSON from RTDB and parses `username` / `name` / `ign`, `skinUrl`, `model`, then invokes `add_offline_account()`.
     - Line 380: `sync_cloud_accounts()` fetches `cloud_accounts.json` from RTDB and syncs to `ias_accounts.json`.
     - Line 448: `remove_account()` sends HTTP DELETE to `cloud_accounts/{name.lower()}.json`.
   - `development/launcher_core/crash_analyzer.py`: Lines 1-254 define zero-dependency crash diagnostics across 8 distinct failure modes (Mixin conflicts, Java version mismatches, 5 OOM variants, native DLLs, missing dependencies, corrupted world regions, shader errors).

6. **Gemini Multi-Tier AI Architecture (`website-next/lib/gemini.ts`)**:
   - Lines 8-40: `SIR_SYSTEM_INSTRUCTION` domain system instruction covering dual engine architecture, shaders, power governor, and G1GC RAM recommendations.
   - Lines 90-181: `askSirAIDetailed(prompt, history)` executes 4-tier fallback waterfall:
     1. Google AI SDK `gemini-3.6-flash`
     2. Google AI SDK `gemini-3.5-flash-lite`
     3. OpenRouter `meta-llama/llama-3.3-70b-instruct`
     4. Autonomous offline expert rule engine (`getOfflineExpertResponse`)
   - Lines 187-337: Administrative AI utility functions (`polishAnnouncementWithAI`, `polishChangelogWithAI`, `translateBroadcastToArabic`, `translateChangelogToArabic`).

---

## 2. Logic Chain

1. **Web Platform Build Stability**:
   - The Next.js 16 application in `website-next/` relies on React 19 and Tailwind CSS v4.
   - Because `next.config.ts` specifies `output: "export"`, any server-side database connection or dynamic SSR dependency at build time will break static compilation.
   - Running `npx tsc --noEmit` and `npm run build` confirmed that all 30 routes compile cleanly to pure static HTML/JS/CSS assets without errors.

2. **Chatbot Evolution & UI Requirements**:
   - The original `AiChatWidget.tsx` contained static rate-limiting counters and lacked Web Speech API synthesis, responsive fullscreen toggling, and multi-preset mobile heights.
   - The newer `AiChatbot.tsx` implements the complete specification for Feature 18, including Arabic/English TTS, spring-animated window resizing, export transcripts, code snippet styling, and Gemini 3.6 Flash connectivity.
   - Wiring `AiChatbot.tsx` into `app/layout.tsx` satisfies all acceptance criteria for Feature 18.

3. **Cloud Sync & Telemetry Alignment**:
   - The Python launcher retrieves sync codes by calling `GET /launcherSyncCodes/{code}.json`.
   - In `website-next/lib/firebase.ts`, `generateLauncherSyncCode` generates a 6-digit numeric string and saves `{ ...profile, name, ign, ownerUid, schemaVersion, expiresAt, createdAt }`.
   - To guarantee complete contract adherence with `PROJECT.md § Cloud Sync Highway` and `auth_service.py`, sync payloads should include `username: cleanIgn`, `code: code`, `userId: uid || "guest"`, and `claimed: false`.
   - On launcher redemption, updating `claimed: true` ensures one-time claim protection.

4. **Gemini AI Intelligence & Crash Diagnosis**:
   - Technical support queries frequently relate to RAM allocation, shader compatibility, and game crashes.
   - The 4-tier fallback chain ensures 100% uptime: if Google AI or OpenRouter experiences network or rate-limit issues, the offline rule engine answers deterministic inquiries.
   - Bridging the 8 diagnostic regex patterns from `crash_analyzer.py` into the web assistant knowledge base allows users to paste crash logs directly into the web chat for instant resolution.

---

## 3. Caveats

1. **Firebase Security Rules**: The root `launcherSyncCodes` node has `.read: true, .write: true` in `database.rules.json` to allow unauthenticated desktop launchers and guest web users to exchange sync codes. A validation rule should enforce `newData.hasChildren(['name', 'expiresAt'])` to prevent invalid payloads.
2. **OpenRouter API Key**: The OpenRouter fallback in `website-next/lib/gemini.ts` requires `NEXT_PUBLIC_OPENROUTER_API_KEY`. If empty, the waterfall skips Tier 3 and falls back directly to Tier 4 offline expert engine.
3. **Web Speech API Browser Permissions**: Text-to-speech relies on client browser support for `window.speechSynthesis`. If the host OS lacks Arabic voice packs, it falls back to the default system voice.

---

## 4. Conclusion

All explicit and implicit specifications for Milestone 4 (Features 17, 18, 19, and 20) have been thoroughly mined, analyzed, validated against the existing codebase, and documented in detail in `spec.md`. The Next.js 16 platform builds cleanly with static export, the `AiChatbot.tsx` component is fully designed, Firebase schemas and Python launcher contracts are harmonized, and the Gemini AI multi-tier architecture is rigorously specified.

---

## 5. Verification Method

To independently verify this specification:

1. **Verify Next.js 16 Static Build**:
   ```pwsh
   cd "D:\Projects\SIR ModPack\website-next"
   npx tsc --noEmit
   npm run build
   ```
   *Expected result*: Exit code 0, 30 static pages generated in `out/`.

2. **Verify Specification Documents**:
   Inspect `D:\Projects\SIR ModPack\.agents\spec_miner_m4_1\spec.md` and `D:\Projects\SIR ModPack\.agents\spec_miner_m4_1\handoff.md`.
