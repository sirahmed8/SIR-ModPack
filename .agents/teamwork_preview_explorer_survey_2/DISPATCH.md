# Dispatch: Survey Explorer 2 (Web Platform `website-next`)

## Identity
- Role: Explorer (Survey 2 - Web Platform `website-next`)
- Working Directory: d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/
- Parent Conversation ID: e6854040-b2f7-4215-a3ca-09a5a910d136

## Mandatory Inputs
- Original Request: `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md` (Read this first!)

## Mission & Objectives
Investigate the web platform in `d:/Projects/SIR ModPack/website-next`:
1. **Route Inventory**:
   - Enumerate all routes in `website-next/` (pages, app router routes, dynamic routes). Confirm if there are 35 distinct routes or identify every route present and needed.
2. **Authentication Gate**:
   - Inspect `/welcome` route and authentication guard (Next.js middleware, AuthContext, client-side guards).
   - Check if unauthenticated visitors are strictly redirected to `/welcome` and prevented from viewing any protected routes.
   - Check Google login implementation (Firebase Auth / Google provider) and Firestore / local storage profile synchronization.
3. **Interconnected Feature Pages**:
   - Check `/` (Home): Unified dashboard, deep-link quick launch buttons (`sirlauncher://`), live announcements.
   - Check `/download`: 3 download tiers, interactive SHA-256 cards, PowerShell commands, direct `sirlauncher://` install actions.
   - Check `/mods`: 221+ mod catalog, loader filters, 1-click "Install to Launcher" deep links.
   - Check `/shaders`: Interactive 3D RTX/POM slider, sun angles, water caustics.
   - Check `/skins`: 3D Skin & Cape Studio with 6 official preset capes and 6 dual-layer skins with 1-click cloud sync.
   - Check `/servers`: 360° Live Radar widget with direct-connect `sirlauncher://join?ip=...`.
   - Check `/crash-analyzer`: Automated diagnostic tool with 1-click recommended fix exporter.
   - Check `/benchmarks`: Public hardware rig simulator (120+ GPUs and CPUs).
   - Check `/changelog`: Filterable v1.0.0 Genesis timeline with category badges.
   - Check `/faq`: Comprehensive legal, server safety, and shader FAQ.
   - Check `/trainer`: In-browser Aim & CPS trainer with leaderboard submission.
   - Check all remaining routes (`/builder`, `/leaderboards`, `/seeds`, `/server-guide`, `/admin`, etc.) for styling, completeness, and interlinking.
4. **Build, Export & Deployment**:
   - Inspect `package.json`, `next.config.js` / `next.config.ts`, `firebase.json`.
   - Verify static export compatibility (`output: 'export'` or Firebase Hosting deployment pipeline).

## Output Requirements
Produce a comprehensive, structured report in:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/handoff.md`
Detailing:
- Complete list of routes found vs required.
- State of auth gate and Google / Firestore integration.
- State of each feature page (completeness, styling, deep links).
- Build and Firebase deployment configuration status.
- Required changes and recommended milestones.

## 2026-09-08T17:31:04Z
You are Survey Explorer 2 for the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/
The project workspace root is: d:/Projects/SIR ModPack

MANDATORY FIRST STEP:
Read your dispatch file at `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/DISPATCH.md` and read `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`.

YOUR ROLE & MISSION:
You are a READ-ONLY explorer. DO NOT modify any source code files.
Investigate the web platform in `d:/Projects/SIR ModPack/website-next`:
1. Route inventory: Enumerate all 35 routes in `website-next/` (app router pages, layouts, dynamic routes). List every route and its current state.
2. Authentication gate: Inspect `/welcome` route and authentication protection. Verify if non-logged-in visitors are strictly redirected to `/welcome` and cannot access protected routes. Inspect Google login (Firebase Auth) and Firestore / local storage synchronization.
3. Feature pages: Audit `/`, `/download`, `/mods`, `/shaders`, `/skins`, `/servers`, `/crash-analyzer`, `/benchmarks`, `/changelog`, `/faq`, `/trainer`, and all remaining routes (`/builder`, `/leaderboards`, `/seeds`, `/server-guide`, `/admin`, etc.) for styling, completeness, and deep links (`sirlauncher://`).
4. Build, export & deployment: Inspect `package.json`, Next.js configuration, Firebase hosting configuration (`firebase.json`), and static export compatibility.

OUTPUT:
Write your complete, structured survey report to:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/handoff.md`
Then call `send_message` to your parent (e6854040-b2f7-4215-a3ca-09a5a910d136) notifying that your survey handoff is complete.
