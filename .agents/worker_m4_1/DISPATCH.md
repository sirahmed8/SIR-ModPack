## 2026-08-30T03:54:24Z
You are a Worker subagent (worker_m4_1) implementing Milestone 4: Next.js 16 Web Hub, Firebase Cloud & Gemini AI Assistant for the SIR Minecraft Ecosystem.

Your working directory is: D:\Projects\SIR ModPack\.agents\worker_m4_1\
Read the authoritative documents:
1. Authoritative Request: D:\Projects\SIR ModPack\.agents\ORIGINAL_REQUEST.md
2. Master Roadmap: D:\Projects\SIR ModPack\PROJECT.md (Milestone 4, Features 17-20)
3. Explorer Reports:
   - D:\Projects\SIR ModPack\.agents\explorer_m4_1\handoff.md
   - D:\Projects\SIR ModPack\.agents\explorer_m4_2\handoff.md
   - D:\Projects\SIR ModPack\.agents\spec_miner_m4_1\handoff.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & File Ownership:
You have exclusive write ownership over files in `website-next/` (especially `website-next/app/layout.tsx`, `website-next/lib/context.tsx`, `website-next/lib/firebase.ts`, `website-next/lib/gemini.ts`, `website-next/lib/error-logger.ts`, `website-next/lib/multiAccounts.ts`, `website-next/lib/security.ts`, `website-next/lib/storage.ts`) and `development/launcher_core/cloud_sync_service.py` if needed.

Your Implementation Tasks:
1. Update `website-next/app/layout.tsx` to import and render `AiChatbot` from `@/components/AiChatbot` (instead of legacy `AiChatWidget`).
2. Fix `website-next/lib/context.tsx` to avoid synchronous `setState` in initial effect / React 19 `react-hooks/set-state-in-effect` linting errors, and clean up any unused variables.
3. Update `generateLauncherSyncCode` in `website-next/lib/firebase.ts` to emit the canonical contract schema:
   `{"code": code, "userId": uid || "guest", "username": cleanIgn, "uuid": profile.uuid || "", "skinUrl": profile.skinUrl || "", "createdAt": rtdbServerTimestamp(), "expiresAt": Date.now() + 30 * 60 * 1000, "claimed": false, "name": cleanIgn, "ign": cleanIgn, "ownerUid": uid || "guest"}`.
   Fix `prefer-const` on `docId` in `firebase.ts:665` and replace explicit `any` types with strict TypeScript types/interfaces where applicable.
4. Clean up explicit `any` types and unused variables in `website-next/lib/gemini.ts`, `website-next/lib/error-logger.ts`, `website-next/lib/multiAccounts.ts`, `website-next/lib/security.ts`, and `website-next/lib/storage.ts`.
5. Ensure `development/launcher_core/cloud_sync_service.py` has `claim_sync_code(code, username)` for full method parity with `bridge.py` and `auth_service.py`.
6. Run builds and verification commands:
   - `cd website-next; npx tsc --noEmit`
   - `cd website-next; npm run lint`
   - `cd website-next; npm run build`
   - `python -m unittest tests/test_cloud_sync_and_auth.py`
   - Run any other relevant test suites.
7. Write your changes and verification logs to `D:\Projects\SIR ModPack\.agents\worker_m4_1\changes.md` and `D:\Projects\SIR ModPack\.agents\worker_m4_1\handoff.md`.
8. Send a completion message back to your orchestrator when done.
