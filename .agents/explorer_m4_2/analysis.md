# Milestone 4 Deep-Dive Investigation: Firebase Cloud Architecture & Gemini AI Assistant

## 1. Executive Summary

This investigation analyzes the cloud data architecture, interface contracts, and AI assistant infrastructure for the **SIR Minecraft Ecosystem** (Milestone 4: Features 18, 19, and 20).

The ecosystem connects a Next.js 16 web platform (`website-next`) with a high-performance Python desktop launcher (`development/launcher_core/`) and native Minecraft instances across Modern 26.2 (Fabric) and Legacy 1.8.9 (Forge).

### Key Findings
1. **Firebase Cloud Highway**:
   - Realtime Database (RTDB) and Cloud Firestore are well-structured for presence tracking (`presence/sessions`), atomic download counters (`analytics/downloads`), OTA updates (`releases/latest`), and live broadcasts (`broadcasts/active`).
   - Client error diagnostics (`error-logger.ts`, `ErrorReportModal.tsx`) collect rich browser/hardware telemetry and pipe into Firestore `error_reports` and RTDB `analytics/errors_count`.
2. **Contract Alignment (`launcherSyncCodes/{code}`)**:
   - The canonical interface contract requires: `{"code": str, "userId": str, "username": str, "uuid": str, "skinUrl": str, "createdAt": int, "expiresAt": int, "claimed": bool}`.
   - In `website-next/lib/firebase.ts` (`generateLauncherSyncCode`), several fields are named differently (`ownerUid` vs `userId`, `ign` vs `username`) and `claimed: false` is omitted upon creation.
   - In `development/launcher_core/cloud_sync_service.py`, `resolve_6digit_sync_code` is present, while `claim_sync_code` referenced in `bridge.py` needs strict implementation parity with `auth_service.py`'s `redeem_sync_code`.
3. **Gemini AI Assistant**:
   - The 4-tier waterfall is implemented in `website-next/lib/gemini.ts`: `gemini-3.6-flash` -> `gemini-3.5-flash-lite` -> OpenRouter (`meta-llama/llama-3.3-70b-instruct`) -> offline autonomous expert rules.
   - `website-next/components/AiChatbot.tsx` contains the complete interactive implementation (Web Speech API TTS, `soundFx` haptics, fullscreen mode, mouse/touch drag resizing, mobile S/M/L presets, smart quick action links).
   - **Crucial Layout Gap**: `website-next/app/layout.tsx` currently renders `<AiChatWidget />` (the basic widget) rather than `<AiChatbot />` (the feature-complete component).

---

## 2. Firebase Cloud Architecture (RTDB & Firestore)

### 2.1 Configuration & Multi-Environment Setup
- **Config file**: `website-next/lib/firebase.ts` (lines 38–47)
- **Project Details**:
  - Project ID: `sir-modpack`
  - RTDB Base URL: `https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app`
  - Storage Bucket: `sir-modpack.firebasestorage.app`
- **Client/SSR Initialization**: Safely initialized using `!getApps().length ? initializeApp(firebaseConfig) : getApp()`.

### 2.2 Telemetry & Real-Time Highway Mapping

| Feature | Service | Path / Collection | Operation / Behavior | Status |
|---|---|---|---|---|
| **Active Presence** | RTDB | `presence/sessions/{userId}` | `onDisconnect().remove()`, `online: true`, `lastSeen` server timestamp | Fully Implemented (`initPresenceTracker`, `subscribeToLivePresence`) |
| **Atomic Downloads** | RTDB + Firestore | RTDB: `analytics/downloads/{installer\|bundle}`<br>Firestore: `download_events` | `rtdbIncrement(1)` on RTDB; `addDoc` with platform & user ID in Firestore | Fully Implemented (`recordDownloadMetric`, `subscribeToDownloads`) |
| **OTA Releases** | RTDB | `releases/latest` | Version metadata, installer URL, bundle URL, mandatory toggle, changelog | Fully Implemented (`getLatestRelease`, `publishReleaseToRTDB`, `toggleMandatoryUpdate`) |
| **Live Announcements** | RTDB + Firestore | RTDB: `broadcasts/active`<br>Firestore: `broadcasts/active` | Primary write to RTDB with Firestore mirror; listener in `navbar/BroadcastBanner.tsx` | Fully Implemented (`publishBroadcastMessage`, `subscribeToBroadcast`, `dismissBroadcastMessage`) |
| **Error Diagnostics** | Firestore + RTDB | Firestore: `error_reports`<br>RTDB: `analytics/errors_count` | Detailed device telemetry (screen, platform, memory heap, URL) | Fully Implemented (`submitErrorReport`, `logErrorToFirestore`, `ErrorReportModal.tsx`) |
| **Community Suggestions**| Firestore | Firestore: `suggestions` & `error_reports` | Unified admin view with category filters | Fully Implemented (`submitSuggestion`) |
| **Master Changelogs** | Firestore + RTDB | Firestore: `changelogs`<br>RTDB: `changelogs/{version}` | Dual-mirrored version changelog engine with master genesis fallback | Fully Implemented (`publishChangelogEntry`, `fetchChangelogEntries`) |

---

## 3. Interface Contract Alignment: Web ↔ Python Launcher

### 3.1 Contract Specification (`PROJECT.md`)
```
Cloud Sync Highway (Web ↔ Launcher via Firebase RTDB):
- Sync Codes path: `launcherSyncCodes/{6_digit_code}`
- Schema: {"code": str, "userId": str, "username": str, "uuid": str, "skinUrl": str, "createdAt": int, "expiresAt": int, "claimed": bool}
- OTA Release path: `releases/latest`
- Schema: {"version": str, "installerUrl": str, "bundleUrl": str, "isMandatory": bool, "changelog": str, "releaseDate": str}
```

### 3.2 Schema Comparison & Gap Analysis

#### A. Sync Codes Schema (`launcherSyncCodes/{code}`)
| Contract Field | Type | `generateLauncherSyncCode` (Current) | Target Canonical Implementation | Gap Assessment |
|---|---|---|---|---|
| `code` | string | Key only | `code: code` (in body) | Missing in body payload |
| `userId` | string | `ownerUid: uid \|\| "guest"` | `userId: uid \|\| "guest"` | Key alias needed (`userId` canonical) |
| `username` | string | `ign: cleanIgn`, `name: cleanIgn` | `username: cleanIgn` | Key alias needed (`username` canonical) |
| `uuid` | string | (none) | `uuid: deterministic_or_user_uuid` | Missing in web generation |
| `skinUrl` | string | `skinUrl: profile.skinUrl` | `skinUrl: profile.skinUrl` | Fully Aligned |
| `createdAt` | int/timestamp | `rtdbServerTimestamp()` | `Date.now()` or `rtdbServerTimestamp()` | Aligned |
| `expiresAt` | int | `Date.now() + 30 * 60 * 1000` | `Date.now() + 30 * 60 * 1000` | Fully Aligned |
| `claimed` | bool | (none) | `claimed: false` | Missing in web generation |

#### B. Python Launcher Side (`launcher_core/`)
- `development/launcher_core/cloud_sync_service.py`:
  - `resolve_6digit_sync_code(code)`: Queries `https://.../launcherSyncCodes/{code}.json`.
  - Missing method: `claim_sync_code(code, username="")` (referenced in `bridge.py` line 706).
- `development/launcher_core/auth_service.py`:
  - `redeem_sync_code(code)`: Parses `username or name or ign`, resolves skin, calls `add_offline_account` and triggers IAS sync.
- `development/launcher_core/bridge.py`:
  - `sync_cloud_code(code)` routes to `auth.redeem_sync_code(code)`.
  - `claim_sync_code(code, username)` calls `cloud_sync.claim_sync_code(code, username)`.

### 3.3 Exact Code Alignment Recommendation
Update `generateLauncherSyncCode` in `website-next/lib/firebase.ts`:
```typescript
export async function generateLauncherSyncCode(profile: PlayerCloudProfile, uid?: string): Promise<string> {
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  const cleanIgn = (profile.ign || "SirPlayer").trim();
  const nowMs = Date.now();
  
  // Canonical Contract Schema
  const payload = {
    code: code,
    userId: uid || "guest",
    ownerUid: uid || "guest",
    username: cleanIgn,
    name: cleanIgn,
    ign: cleanIgn,
    uuid: (profile as any).uuid || "",
    skinUrl: profile.skinUrl || `https://mc-heads.net/skin/${encodeURIComponent(cleanIgn)}`,
    model: profile.model || "classic",
    accountType: profile.accountType || "offline",
    schemaVersion: 1,
    claimed: false,
    createdAt: nowMs,
    expiresAt: nowMs + 30 * 60 * 1000,
  };

  const globalCodeRef = ref(rtdb, `launcherSyncCodes/${code}`);
  await set(globalCodeRef, payload);

  // Redundant copy under user path if authenticated
  if (uid && uid !== "guest") {
    try {
      const userCodeRef = ref(rtdb, `users/${uid}/launcherSyncCodes/${code}`);
      await set(userCodeRef, payload);
    } catch {}
  }

  return code;
}
```

---

## 4. Gemini AI Assistant Architecture

### 4.1 4-Tier Waterfall Fallback System
The architecture in `website-next/lib/gemini.ts` implements a resilient multi-tier waterfall:

```
[User Query]
     │
     ▼
[Tier 1: Google Gemini 3.6 Flash / 3.7 Flash] ──(Success)──> [Return AI Response]
     │ (API failure or rate limit)
     ▼
[Tier 2: Google Gemini 3.5 Flash-Lite] ──────────(Success)──> [Return AI Response]
     │ (API failure or quota limit)
     ▼
[Tier 3: OpenRouter API (Llama 3.3 70B)] ────────(Success)──> [Return AI Response]
     │ (Network failure or key unconfigured)
     ▼
[Tier 4: Autonomous Offline Expert Rules] ───────────────────> [Return Rule Response]
```

### 4.2 SDK & Model Specification
- **Current SDK in `package.json`**: `"@google/generative-ai": "^0.24.0"`.
- **SDK Note**: As outlined in `gemini-api-dev` skill, the modern unified SDK is `@google/genai` with current models `gemini-3.7-flash`, `gemini-3.5-flash-lite`, and `gemini-2.5-flash`.
- **Response Format (`AiResponse`)**:
  ```typescript
  export interface AiResponse {
    text: string;
    source: "gemini-3.6-flash" | "gemini-3.5-flash-lite" | "gemini-fallback" | "openrouter" | "offline-expert";
    modelUsed: string;
    suggestedAction?: {
      labelEn: string;
      labelAr: string;
      href: string;
    };
  }
  ```

### 4.3 Domain System Instructions & Crash Diagnosis
`SIR_SYSTEM_INSTRUCTION` in `gemini.ts` contains:
1. **Dual Engine Architecture**: Modern 26.2 (Fabric + Sodium/Lithium/Iris/DH) & Legacy 1.8.9 (Forge + Patcher/OptiFine/HitDelayFix).
2. **Shader Suite 2.0**: SIR Extreme (2048 Shadowmap, POM, caustics) vs SIR Balanced (1024, 144+ FPS lock).
3. **Launcher & Power Governor**: Max Performance vs Eco/Smooth extraction mode; Firebase RTDB push updater; IAS cracked/Microsoft switcher.
4. **RAM & Java Tuning**: 4GB–6GB standard boundary; G1GC flags (`-XX:+UseG1GC -XX:MaxGCPauseMillis=200`).
5. **Crash Diagnostics & Troubleshooting Matrix**:
   - **Exit Code 1**: Mod incompatibility, missing dependency (e.g. Indium for Sodium), or Fabric Loader mismatch.
   - **Exit Code -1073740791 (0xC0000409)**: GPU driver crash or corrupt OpenAL/LWJGL natives. Solution: Re-extract natives via launcher repair.
   - **MixinApplyError**: Conflict between two mods modifying the same bytecode. Solution: Check latest mod versions.
   - **Java Version Incompatibility**: JRE 21 LTS required for 26.2, JRE 8 required for 1.8.9.

### 4.4 Autonomous Offline Expert Engine
`getOfflineExpertResponse` provides instant deterministic answers without network calls:
- Query contains `ram` / `memory` / `رام` -> RAM bounds & GC explanation.
- Query contains `shader` / `شيدر` -> Shaders 2.0 configuration guide.
- Query contains `1.8.9` / `pvp` / `بفب` -> Legacy 1.8.9 PvP tuning.
- Query contains `crash` / `lag` / `كراش` -> Crash resolution steps.
- Query contains `offline` / `cracked` / `مكرك` -> IAS account switching.
- Query contains `havoc` / `هافوك` -> HAVOC project roadmap.

---

## 5. AI Chatbot UI/UX & Interactive Capabilities

### 5.1 Component Comparison: `AiChatbot.tsx` vs `AiChatWidget.tsx`

| Feature | `AiChatbot.tsx` (Advanced) | `AiChatWidget.tsx` (Basic) |
|---|---|---|
| **Text-to-Speech (TTS)** | Full Web Speech API synthesis (`speakMessage`, `Volume2`/`VolumeX`, auto AR/EN voice) | ❌ Not available |
| **Audio Haptic FX** | `soundFx.playClick()`, `soundFx.playCelebration()` | ❌ Not available |
| **Fullscreen Mode** | Maximize/Restore toggle (`Maximize2`/`Minimize2`, dynamic viewport bounds) | ❌ Not available |
| **Window Resizing** | 3 Drag Handles (Top, Left, Corner) with mouse + touch support | Mouse-only corner drag |
| **Mobile Height Presets** | 📱 S (45vh), 📖 M (72vh), 🚀 L (95vh) quick preset pills | ❌ Not available |
| **Smart Action Injection** | Smart quick links (`/shaders`, `/mods`, `/#downloads`, `/trainer`, `/benchmarks`, etc.) | ❌ Not available |
| **Transcript Export** | 1-Click copy formatted transcript to clipboard (`Share2` / `Check`) | ❌ Not available |
| **4-Tier Source Badge** | Model badge indicator (`gemini-3.6-flash`, `openrouter`, `offline-expert`) | Basic role display |
| **Google Auth Gate** | Built-in Google sign-in CTA button | Basic query limiter |

### 5.2 Layout Integration Fix
In `website-next/app/layout.tsx`:
- Line 9: `import { AiChatWidget } from "@/components/AiChatWidget";`
- Line 186: `<AiChatWidget />`
- **Recommendation**: Replace with `import AiChatbot from "@/components/AiChatbot";` and `<AiChatbot />` to activate all advanced features across the web platform.

---

## 6. Implementation Checklist for Milestone 4

- [ ] **Task 1: Contract Alignment in `website-next/lib/firebase.ts`**
  - Update `generateLauncherSyncCode` to write all canonical fields (`code`, `userId`, `username`, `uuid`, `skinUrl`, `createdAt`, `expiresAt`, `claimed: false`).
- [ ] **Task 2: Launcher Cloud Sync Bridge Completion**
  - Add `claim_sync_code(code, username)` to `CloudSyncService` in `development/launcher_core/cloud_sync_service.py` to match `bridge.py` and `AuthService`.
- [ ] **Task 3: Layout Integration of `AiChatbot.tsx`**
  - Update `website-next/app/layout.tsx` to mount `<AiChatbot />` instead of `<AiChatWidget />`.
- [ ] **Task 4: Enriched Crash Diagnosis in `gemini.ts`**
  - Add specific Minecraft exit codes, Mixin errors, and JRE version rules to `SIR_SYSTEM_INSTRUCTION` and `getOfflineExpertResponse`.
- [ ] **Task 5: Verification & Test Execution**
  - Run `tests/test_cloud_sync_and_auth.py` and `tests/test_challenger_m3_accounts_sync_bridge.py` to confirm 100% pass rate.
