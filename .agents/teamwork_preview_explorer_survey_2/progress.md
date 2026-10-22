# Progress Report — Explorer 2 (Web Platform `website-next` Survey)

- **Status**: Investigation Complete — Synthesizing Handoff Report
- **Last visited**: 2026-09-08T17:42:00Z

## Completed Tasks
1. Enumerated and verified all 35 static App Router routes in `website-next/` via Next.js Turbopack build (`npm run build` -> 35/35 static pages generated in 720ms).
2. Inspected `/welcome` gate and `GlobalAuthGuard` authentication redirect loop in `layout.tsx` and `components/GlobalAuthGuard.tsx`.
3. Verified Google OAuth (Firebase Auth), Firestore user profile synchronization, and local storage cache mechanisms.
4. Identified critical security gap: `/admin` page lacks role-based authorization check (any logged-in Google user can access admin controls).
5. Audited all feature pages (`/`, `/download`, `/mods`, `/shaders`, `/skins`, `/servers`, `/crash-analyzer`, `/benchmarks`, `/changelog`, `/faq`, `/trainer`, `/builder`, `/leaderboards`, `/seeds`, `/server-guide`, `/admin`, `/compatibility`, `/auth/desktop`, legal suite).
6. Audited native `sirlauncher://` deep links: verified presence on `/auth/desktop`, `/shaders`, and `/servers`; identified absence on `/` (launcher quick-launch), `/download` (1-click installer), and `/mods` (1-click mod install).
7. Discovered broken internal links: references to non-existent `/profiles` and `/packs` in `sitemap.ts`, `gemini.ts`, `AiChatbot.tsx`, and `shaders/page.tsx`.
8. Audited static export and deployment configs (`package.json`, `next.config.ts`, `firebase.json`).
