# Handoff Report: Milestone 4 Investigation (Firebase Cloud & Gemini AI Assistant)

## 1. Observation
- **Authoritative Documents & Roadmap**:
  - `D:\Projects\SIR ModPack\PROJECT.md` (Features 18, 19, 20 and Interface Contracts lines 60–76).
  - Interface Contract for Cloud Sync Highway defines:
    - Sync Codes Path: `launcherSyncCodes/{6_digit_code}`
    - Schema: `{"code": str, "userId": str, "username": str, "uuid": str, "skinUrl": str, "createdAt": int, "expiresAt": int, "claimed": bool}`
    - OTA Release Path: `releases/latest`
    - Schema: `{"version": str, "installerUrl": str, "bundleUrl": str, "isMandatory": bool, "changelog": str, "releaseDate": str}`
- **Firebase Implementation in `website-next/lib/firebase.ts`**:
  - RTDB connection configured to `https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app` (line 46).
  - Presence tracking active in `initPresenceTracker` (lines 467–498) and `subscribeToLivePresence` (lines 500–510) using `presence/sessions`.
  - Atomic download metrics active in `recordDownloadMetric` (lines 406–422) with `analytics/downloads/{installer|bundle}` via `rtdbIncrement(1)`.
  - OTA release updates active in `getLatestRelease` (lines 370–396) and `publishReleaseToRTDB` (lines 398–401) via `releases/latest`.
  - Broadcast engine active in `publishBroadcastMessage` (lines 752–776) and `subscribeToBroadcast` (lines 806–818) via `broadcasts/active`.
  - Client diagnostics and error reports active in `submitErrorReport` (lines 318–340) and `website-next/lib/error-logger.ts` (lines 1–88) piping to Firestore `error_reports`.
  - `generateLauncherSyncCode` (lines 853–899): Writes payload `{ ...profile, name: cleanIgn, ign: cleanIgn, ownerUid: uid || "guest", schemaVersion: 1, expiresAt: Date.now() + 30 * 60 * 1000, createdAt: rtdbServerTimestamp() }`. Notice `userId` is written as `ownerUid`, `username` as `ign`/`name`, `code` is omitted in the body, and `claimed: false` is not set.
- **Python Launcher Implementation in `development/launcher_core/`**:
  - `cloud_sync_service.py` (lines 11–28) defines `resolve_6digit_sync_code(code)` reading `f"{self.rtdb_url}/launcherSyncCodes/{urllib.parse.quote(code)}.json"`.
  - `auth_service.py` (lines 408–428) defines `redeem_sync_code(code)` parsing `username or name or ign` from the RTDB record.
  - `bridge.py` (lines 623–720) exposes `sync_cloud_code(code)` and `claim_sync_code(code, username)`.
- **Gemini AI Assistant Implementation in `website-next/lib/gemini.ts`**:
  - 4-Tier Waterfall:
    - Tier 1: `gemini-3.6-flash` (lines 91–128)
    - Tier 2: `gemini-3.5-flash-lite` (lines 91–128)
    - Tier 3: OpenRouter API with `meta-llama/llama-3.3-70b-instruct` (lines 130–171)
    - Tier 4: Autonomous Offline Expert Rules Engine `getOfflineExpertResponse` (lines 173–180 & 339–363)
  - Bilingual localization (Arabic RTL & English LTR) embedded in system prompt and translation helpers (lines 267–337).
- **Interactive UI Components in `website-next/`**:
  - `website-next/components/AiChatbot.tsx` (lines 1–699): Implements Web Speech API text-to-speech (`speakMessage`), tactile sound effects (`soundFx.playClick()`, `soundFx.playCelebration()`), Fullscreen maximize toggle (`Maximize2`/`Minimize2`), 3-direction mouse/touch drag resize handlers, mobile S/M/L presets, quick prompts bar, and smart action buttons (`suggestedAction`).
  - `website-next/app/layout.tsx` (lines 9 and 186): Imports and renders `<AiChatWidget />` instead of `<AiChatbot />`.

---

## 2. Logic Chain
1. The project requirement specifies a shared Cloud Sync Highway between the Web App and Desktop Launcher via Firebase RTDB.
2. The schema defined in `PROJECT.md` line 73 requires 8 exact fields: `code`, `userId`, `username`, `uuid`, `skinUrl`, `createdAt`, `expiresAt`, `claimed`.
3. In `website-next/lib/firebase.ts`, `generateLauncherSyncCode` emits a payload with non-canonical field names (`ownerUid` instead of `userId`, `ign` instead of `username`) and omits `code` and `claimed: false`.
4. Updating `generateLauncherSyncCode` to emit the canonical schema ensures full contract compliance while keeping backward-compatible aliases for legacy consumers.
5. In `development/launcher_core/cloud_sync_service.py`, adding `claim_sync_code(code, username)` ensures exact method parity with `bridge.py:706` and `auth_service.py:408`.
6. For the AI Assistant, `website-next/components/AiChatbot.tsx` satisfies all Milestone 4 requirements (speech synthesis, fullscreen mode, tactile sound FX, mobile height presets, 4-tier source badge, smart action buttons).
7. `website-next/app/layout.tsx` must be updated from `<AiChatWidget />` to `<AiChatbot />` to make these features active in production.

---

## 3. Caveats
- No changes to source code files were made during this turn, strictly adhering to the explorer read-only protocol.
- Google GenAI API keys (`NEXT_PUBLIC_GEMINI_API_KEY`) and Firebase config environment variables are provided with production-safe client fallbacks in the repository.
- OpenRouter key (`NEXT_PUBLIC_OPENROUTER_API_KEY`) is optional and gracefully falls back to Tier 4 offline expert rules if unconfigured.

---

## 4. Conclusion
1. **Firebase Cloud Architecture**: Complete and operational for presence, download metrics, OTA releases, live broadcasts, and error diagnostics.
2. **Contract Alignment**: Identified exact schema adjustments needed in `website-next/lib/firebase.ts` (`generateLauncherSyncCode`) and method parity in `development/launcher_core/cloud_sync_service.py`.
3. **Gemini AI Assistant**: 4-tier waterfall (`gemini-3.6-flash` -> `gemini-3.5-flash-lite` -> OpenRouter -> offline expert) is fully architected. Mounting `<AiChatbot />` in `website-next/app/layout.tsx` immediately provides the full suite of TTS, fullscreen, audio effects, and smart action interactions.

---

## 5. Verification Method
1. **Contract & Auth Test Suite**:
   ```bash
   python -m unittest tests/test_cloud_sync_and_auth.py
   python -m unittest tests/test_challenger_m3_accounts_sync_bridge.py
   ```
2. **Schema & Code Inspection**:
   - Inspect `website-next/lib/firebase.ts` lines 853–899 (`generateLauncherSyncCode`).
   - Inspect `website-next/app/layout.tsx` lines 9 & 186 (`<AiChatbot />` inclusion).
   - Inspect `website-next/lib/gemini.ts` lines 88–181 (`askSirAIDetailed` 4-tier fallback).
   - Inspect `website-next/components/AiChatbot.tsx` lines 137–160 (TTS), 389–410 (Sound FX), 514–520 (Fullscreen).
