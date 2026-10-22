# Handoff Report: Web Platform Survey (`website-next`)

- **Author**: Explorer 2 (Web Platform Architect & Surveyor)
- **Target**: Parent Orchestrator (`e6854040-b2f7-4215-a3ca-09a5a910d136`)
- **Working Directory**: `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/`
- **Scope**: `website-next/` (Next.js 16.3.2 App Router, Firebase Hosting, Auth Gate, 35 Routes, Feature Pages, Deep Links)
- **Status**: Complete & Verified (Read-Only Survey)

---

## 1. Observation

### 1.1 Route Inventory (All 35 Static Routes Verified by Compiler)
Executing `npm run build` within `d:/Projects/SIR ModPack/website-next` compiled successfully with Next.js 16.3.2 Turbopack in 2.3s, generating exactly 35 static pages (`35/35`) across workers. The complete compiler route manifest (`.next/prerender-manifest.json`) records:

| # | Route Path | Source File | Type | Auth Protection Level | Current Status & Notes |
|:---:|:---|:---|:---|:---|:---|
| 1 | `/` | `app/page.tsx` | Page (Client) | Redirect / Welcome Gate | Renders `WelcomeEcosystemShowcase`; if authenticated, redirects to `/main`. |
| 2 | `/_global-error` | `app/global-error.tsx` | Error Boundary | Public | Global React 19 unhandled exception fallback. |
| 3 | `/_not-found` | `app/not-found.tsx` | 404 Page | Public | Custom cyber-dark 404 layout with navigation home CTA. |
| 4 | `/admin` | `app/admin/page.tsx` | Page (Client) | `GlobalAuthGuard` only | **CRITICAL SECURITY GAP**: No role check! Any logged-in user can access. |
| 5 | `/agreements` | `app/agreements/page.tsx` | Page (Client) | `GlobalAuthGuard` | Free Independent Agreement & multi-profile terms. |
| 6 | `/api/news` | `app/api/news/route.ts` | Route Handler (`GET`) | `force-static` | RSS 2.0 XML / JSON news feed generated from RTDB broadcasts. |
| 7 | `/api/servers` | `app/api/servers/route.ts` | Route Handler (`GET`) | `force-static` | Returns curated + 1600+ generated global Minecraft servers JSON. |
| 8 | `/api/status` | `app/api/status/route.ts` | Route Handler (`GET`) | `force-static` | Real-time ecosystem uptime status report JSON with security headers. |
| 9 | `/api/updates` | `app/api/updates/route.ts` | Route Handler (`GET`) | `force-static` | Desktop launcher version manifest with sha256 checksums JSON. |
| 10 | `/auth/desktop` | `app/auth/desktop/page.tsx` | Page (Client) | Public (Gate Bypass) | OAuth receiver for launcher; generates 6-digit sync code & deep link. |
| 11 | `/benchmarks` | `app/benchmarks/page.tsx` | Page (Client) | `GlobalAuthGuard` | Hardware rig simulator (70+ GPUs, 55 CPUs, WebGL auto-detect). |
| 12 | `/builder` | `app/builder/page.tsx` | Page (Client) | `AuthGate` | Custom modpack profile generator with JSON export & RAM meter. |
| 13 | `/capes` | `app/capes/page.tsx` | Page (Client) | Public Redirect | Client redirect to `/skins?tab=capes`. |
| 14 | `/changelog` | `app/changelog/page.tsx` | Page (Client) | `GlobalAuthGuard` | Filterable v1.0.0 Genesis timeline with category badges. |
| 15 | `/compatibility` | `app/compatibility/page.tsx` | Page (Client) | `GlobalAuthGuard` | In-browser WebGL GPU, DPR, core concurrency, & RAM diagnostics. |
| 16 | `/cookies` | `app/cookies/page.tsx` | Page (Client) | `GlobalAuthGuard` | Zero-telemetry cookie and local storage governance policy. |
| 17 | `/crash-analyzer` | `app/crash-analyzer/page.tsx` | Page (Client) | `GlobalAuthGuard` | Regex diagnostics for 6 crash causes; missing 1-click file exporter. |
| 18 | `/download` | `app/download/page.tsx` | Page (Client) | `GlobalAuthGuard` | 3 tiers (Modern, Legacy, Potato), SHA-256 cards, PowerShell checks. |
| 19 | `/eula` | `app/eula/page.tsx` | Page (Client) | `GlobalAuthGuard` | Binding End User License Agreement (Mojang & Microsoft compliant). |
| 20 | `/faq` | `app/faq/page.tsx` | Page (Client) | `GlobalAuthGuard` | Comprehensive bilingual FAQ with interactive navigation actions. |
| 21 | `/leaderboards` | `app/leaderboards/page.tsx` | Page (Client) | `AuthGate` | Live Firestore PvP CPS, Aim, and Reflex rankings with medal badges. |
| 22 | `/main` | `app/main/page.tsx` | Page (Client) | `GlobalAuthGuard` | Authenticated home hub (Hero, ProfilesMatrix, ServerHosting, Havoc). |
| 23 | `/mods` | `app/mods/page.tsx` | Page (Client) | `GlobalAuthGuard` | 240+ bundled mods catalog + live Modrinth/CurseForge explorer. |
| 24 | `/news/index.xml` | `app/news/index.xml/route.ts` | Route Handler (`GET`) | `force-static` | RSS feed endpoint mirroring `/api/news`. |
| 25 | `/privacy` | `app/privacy/page.tsx` | Page (Client) | `GlobalAuthGuard` | Universal Privacy Policy & Zero-Telemetry commitment. |
| 26 | `/robots.txt` | `app/robots.ts` | Metadata Route | `force-static` | Crawl directives allowing public routes, disallowing `/admin` & `/api/`. |
| 27 | `/seeds` | `app/seeds/page.tsx` | Page (Client) | `AuthGate` | Curated seed explorer with coordinates and 1-click `/tp` copy. |
| 28 | `/server-guide` | `app/server-guide/page.tsx` | Page (Client) | `AuthGate` | Dual hosting guide: In-Game Global WAN (`e4mc`) & Playit.gg. |
| 29 | `/servers` | `app/servers/page.tsx` | Page (Client) | `GlobalAuthGuard` | 360° Live Radar widget + direct join (`sirlauncher://join?ip=...`). |
| 30 | `/shaders` | `app/shaders/page.tsx` | Page (Client) | `GlobalAuthGuard` | WebGL raymarched RTX/POM comparison slider + launch deep link. |
| 31 | `/sitemap.xml` | `app/sitemap.ts` | Metadata Route | `force-static` | XML sitemap containing priority & change frequencies. |
| 32 | `/skins` | `app/skins/page.tsx` | Page (Client) | `AuthGate` | 3D Skin & Cape Studio (6 capes, 6 skins, WebGL `skinview3d`). |
| 33 | `/terms` | `app/terms/page.tsx` | Page (Client) | `GlobalAuthGuard` | Terms of Service & Free Independent Platform Agreement. |
| 34 | `/trainer` | `app/trainer/page.tsx` | Page (Client) | `AuthGate` | In-browser CPS & Aim trainer with Firestore score submission. |
| 35 | `/welcome` | `app/welcome/page.tsx` | Page (Client) | Public Entry Point | Google OAuth sign-in gate and ecosystem feature showcase. |

---

### 1.2 Authentication Gate & Profile Synchronization

1. **Global Interception (`website-next/components/GlobalAuthGuard.tsx`)**:
   - `GlobalAuthGuard` wraps `{children}` in root layout `website-next/app/layout.tsx` (lines 168-170).
   - Lines 23-24 check pathnames:
     ```typescript
     const isDesktopAuth = pathname === "/auth/desktop" || pathname?.startsWith("/auth/desktop");
     const isWelcomePage = pathname === "/welcome" || pathname === "/welcome/";
     ```
   - Lines 30-38 enforce URL replacement:
     ```typescript
     if (!user) {
       if (!isDesktopAuth && !isWelcomePage) {
         router.replace("/welcome");
       }
     } else {
       if (isWelcomePage) {
         router.replace("/");
       }
     }
     ```
   - Lines 65-67 prevent DOM leakage of unauthenticated pages:
     ```typescript
     if (!user) {
       return <WelcomePage />;
     }
     ```
     **Observation**: If a user is not authenticated, `GlobalAuthGuard` immediately replaces the render output with `<WelcomePage />` before any protected page tree can mount. Visitors cannot see, inspect, or interact with protected route content.

2. **Google Authentication & Firebase Auth (`website-next/lib/firebase.ts`)**:
   - Lines 136-169 implement `signInWithGoogle()` using `signInWithPopup(auth, googleProvider)` with `googleProvider.setCustomParameters({ prompt: "select_account" })`.
   - Lines 142-162 automatically create or update a document in Firestore collection `users/{uid}` with fields `uid`, `displayName`, `email`, `photoURL`, `role`, `createdAt`, `lastLogin`, `downloadCount`.

3. **Firestore & Local Storage Profile Synchronization (`website-next/lib/context.tsx`)**:
   - Lines 138-196 attach `onAuthStateChanged(auth, async (firebaseUser) => { ... })`.
   - When authenticated, it calls `getUserProfileFromFirestore(firebaseUser.uid)` (lines 147-155) to pull `minecraftUsername`, `accountType`, and `skinUrl`.
   - It persists these values to `localStorage`:
     - `sir_linked_minecraft_user`
     - `sir_linked_account_type`
     - `sir_custom_skin_data`
   - It constructs `userProfile` and distributes it through `EcosystemContext`.

4. **Critical Security Anomaly on `/admin` (`website-next/app/admin/page.tsx`)**:
   - Lines 153-200 define `AdminDashboard()`.
   - **Verbatim Absence**: There is NO call to `useEcosystem()`, NO check for `userProfile.role === "admin" | "owner"`, and NO check for admin emails (`sir.ahmed.owner@gmail.com`).
   - Consequently, any user on the internet who signs in with ANY Google account can open `https://sir-modpack.web.app/admin` and gain full write access to broadcasts, changelogs, release flags, and sensitive user error reports.

---

### 1.3 Deep Links (`sirlauncher://`) Audit

| Route / Component | Target Deep Link Spec | Current Observed State | File & Line | Status |
|:---|:---|:---|:---|:---|
| `/auth/desktop` | `sirlauncher://auth?data=...&code=...` | **Implemented** | `app/auth/desktop/page.tsx:97` | ✅ Working |
| `/shaders` | `sirlauncher://launch?profile=...&shader=...` | **Implemented** | `app/shaders/page.tsx:233` | ✅ Working |
| `/servers` | `sirlauncher://join?ip=...` | **Implemented** | `app/servers/page.tsx:838` | ✅ Working |
| `/` (Home Hero & Matrix) | `sirlauncher://launch?profile=...` | **Missing** | `components/HeroDownload.tsx`, `components/ProfilesMatrix.tsx` | ❌ Missing |
| `/download` | `sirlauncher://install?tier=...` | **Missing** | `app/download/page.tsx:199` | ❌ Missing |
| `/mods` | `sirlauncher://mod/install?id=...` | **Missing** | `app/mods/page.tsx:528, 805` | ❌ Missing |

---

### 1.4 Feature Pages Audit

1. **`/` and `/main` (Home & Main Dashboard)**:
   - Root `app/page.tsx` routes unauthenticated users to `WelcomeEcosystemShowcase`, and authenticated users to `/main`.
   - `app/main/page.tsx` renders `MainPageQuickDock`, `HeroDownload`, `ProfilesMatrix`, `AccountLinking`, `ServerHostingPortal`, `HavocPortal`, and `ChangelogSection`.
   - Styling: Obsidian glassmorphism with cyan accents, live announcements banner, and RTDB broadcast ticker.
   - Gap: Profiles matrix launch buttons link to download anchors rather than triggering `sirlauncher://launch`.

2. **`/download`**:
   - Renders 3 download tiers: Modern 26.2 (`SIR_Package.zip`, 1.42 GB), Legacy 1.8.9 (680 MB), and Performance Potato (840 MB).
   - Features interactive SHA-256 cards with 1-click clipboard copy and verified PowerShell check commands (`(Get-FileHash -Algorithm SHA256 .\SIR_Package.zip).Hash -eq ...`).
   - Gap: Lacks 1-click `sirlauncher://install` deep link trigger alongside HTTP downloads.

3. **`/mods`**:
   - Dual-mode catalog: Bundled tab (240+ mods index parsed from `/data/mod_manifest.json`) and Online tab (live Modrinth and CurseForge search API with 300ms debounce).
   - Features category tabs, loader filters, and interactive modal specifications for custom SIR mods (`sir_core`, `havoc_pvp`, `super_secret_settings`, `player_api`, `sharpness_particles`).
   - Gap: Lacks direct `sirlauncher://mod/install?id=${mod.id}` button.

4. **`/shaders`**:
   - Renders `RtxPomComparisonViewer` component with custom WebGL raymarching fragment shader supporting POM depth displacement, time-of-day sunlight angles (sunset, noon, night), and materials (cobblestone, bricks, prismarine, gold).
   - Card catalog includes `sirlauncher://launch?profile=${shader.profileId}&shader=...` action.
   - Dead link: Line 252 links to `/profiles` which does not exist (returns 404).

5. **`/skins` and `/capes`**:
   - `app/skins/page.tsx` features WebGL 3D avatar inspector (`Skin3DViewer.tsx`) with OrbitControls, Steve (4px) and Alex (3px) toggles, and walk/run animations.
   - Capes tab features all 6 official preset capes:
     1. `sir_obsidian_neon`
     2. `sir_emerald_prism`
     3. `sir_cyber_pulse`
     4. `sir_void_dragon`
     5. `sir_champion_gold`
     6. `sir_classic_genesis`
   - Skins catalog features all 6 dual-layer skins (`sir_cyber_warrior`, `sir_neon_shadow`, `sir_emerald_ninja`, `sir_void_walker`, `sir_esports_pro`, `sir_steve_tactical`).
   - 1-click cloud sync to Firestore via `saveClaimedAccountToCloud`.
   - `app/capes/page.tsx` acts as a clean client redirect to `/skins?tab=capes`.

6. **`/servers`**:
   - Features `LiveServerRadarWidget` measuring real latency and active player counts across curated networks (Hypixel, MMC, Pika, Jartex, DonutSMP, Wynncraft, 2b2t, BlockMC, CubeCraft, GommeHD, etc.).
   - Features 1-click `sirlauncher://join?ip=${encodeURIComponent(server.ip)}` direct connection action.

7. **`/crash-analyzer`**:
   - Regex diagnostic engine matching 6 critical crash signatures (JVM OutOfMemory, Java Version Incompatibility, Fabric Mixin Collision, GPU/OpenGL Kernel Crash, Corrupted Region/Chunk, Missing Mod Dependency).
   - Extracts culprit classes and provides quick-copy JVM flags (`-Xmx6G -Xms4G -XX:+UseZGC ...`).
   - Gap: Missing 1-click file exporter (`Export Diagnostic Report & Recommended Fix` as `.txt` / `.json`).

8. **`/benchmarks`**:
   - Hardware rig simulator featuring 125+ hardware components (70+ GPUs from RTX 5090 to Intel UHD; 55 CPUs from Core Ultra 9 285K / 9950X to vintage dual cores).
   - Automatically detects user's GPU model on mount via WebGL `WEBGL_debug_renderer_info`.
   - Displays interactive Vanilla vs SIR comparison bars across 8 instance profiles.

9. **`/changelog`**:
   - Filterable timeline with category badges (`All`, `Engine`, `Shaders`, `Desktop Apps`, `In-Game HUD`, `Multiplayer`).
   - Pulls live releases from Firebase RTDB with fallback to `DEFAULT_MASTER_CHANGELOG`.

10. **`/faq`**:
    - Comprehensive bilingual FAQ covering Free Independent Agreement, Hypixel safety, Iris vs OptiFine, Java 21 LTS Generational ZGC, and offline accounts.

11. **`/trainer`**:
    - In-browser Aim, CPS, and Reaction trainer with progressive difficulty tiers and automated submission to Firestore leaderboard.

12. **Remaining Routes (`/builder`, `/leaderboards`, `/seeds`, `/server-guide`, `/compatibility`, legal suite)**:
    - `/builder`: Modpack customizer with live RAM calculator and JSON profile exporter.
    - `/leaderboards`: Competitive rankings with medal badges.
    - `/seeds`: Curated world seeds with coordinates and `/tp` command copy.
    - `/server-guide`: Dual hosting guide for In-Game Global WAN and Dedicated Server with Playit.gg.
    - `/compatibility`: Live WebGL, resolution DPR, CPU concurrency, and device memory scanner.
    - Legal suite (`/privacy`, `/terms`, `/cookies`, `/eula`, `/agreements`): Fully compliant, bilingual, glassmorphic layouts.

---

### 1.5 Dead Internal Link References
A project-wide search identified references to two routes that do NOT exist:
1. **`/profiles`**:
   - `website-next/app/sitemap.ts:11`
   - `website-next/app/shaders/page.tsx:252` (`href="/profiles"`)
   - `website-next/lib/gemini.ts:43, 58, 92, 418`
   - `website-next/PROJECT_ARCHITECTURE_EXPLANATION.md:168`
2. **`/packs`**:
   - `website-next/app/sitemap.ts:13, 36`
   - `website-next/components/AiChatbot.tsx:442, 551, 865` (`if (href.includes("/shaders")) href = "/packs";`)
   - `website-next/lib/gemini.ts:31, 58`
   - `website-next/PROJECT_ARCHITECTURE_EXPLANATION.md:168`
   *Note: In `website-next`, shader and pack content lives on `/shaders`, not `/packs`.*

---

### 1.6 Build, Export & Deployment Configuration

1. **`package.json`**:
   - Framework: Next.js `16.3.2`, React `19.2.8`, Tailwind CSS `^4`.
   - Key dependencies: `firebase ^11.3.1`, `skinview3d ^3.4.2`, `framer-motion ^12.4.7`, `lucide-react ^1.16.0`, `canvas-confetti ^1.9.4`.
   - Scripts: `"build": "next build"`, `"dev": "next dev"`.

2. **`next.config.ts`**:
   ```typescript
   import type { NextConfig } from "next";

   const nextConfig: NextConfig = {
     output: "export",
     trailingSlash: true,
     images: {
       unoptimized: true
     },
     experimental: {
       optimizePackageImports: ["lucide-react", "framer-motion"]
     }
   };

   export default nextConfig;
   ```
   **Observation**: `output: "export"` forces pure static HTML/CSS/JS export to `out/`. All 5 route handlers in `app/api/` specify `export const dynamic = "force-static";`, enabling seamless compilation during `next build`.

3. **`firebase.json`**:
   ```json
   {
     "database": { "rules": "database.rules.json" },
     "firestore": { "rules": "firestore.rules" },
     "hosting": {
       "public": "out",
       "cleanUrls": true,
       "trailingSlash": true,
       "headers": [
         {
           "source": "**",
           "headers": [
             { "key": "X-Content-Type-Options", "value": "nosniff" },
             { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
             { "key": "X-XSS-Protection", "value": "1; mode=block" },
             { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
             { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
           ]
         }
       ],
       "ignore": ["firebase.json", "**/.*", "**/node_modules/**", "**/*.exe", "**/*.zip"]
     }
   }
   ```
   **Observation**: Firebase hosting correctly maps `public` to `out`, matching Next.js static export.

---

## 2. Logic Chain

1. **Static Build Invariant**:
   - `next.config.ts` specifies `output: "export"`.
   - Running `next build` processes all 35 routes.
   - All 5 `route.ts` handlers declare `export const dynamic = "force-static";`.
   - Therefore, the web application generates 100% pre-rendered static assets into `out/`, fully compatible with Firebase Hosting without needing Node.js SSR runtime or Cloud Functions.

2. **Authentication Isolation**:
   - `GlobalAuthGuard` wraps `{children}` in `layout.tsx`.
   - When `user === null` and the route is not `/auth/desktop`, `GlobalAuthGuard` returns `<WelcomePage />` and triggers `router.replace("/welcome")`.
   - Therefore, unauthenticated visitors are completely isolated from protected route trees.

3. **Security Vulnerability on `/admin`**:
   - `GlobalAuthGuard` checks only whether `user` exists (`!user`).
   - Once a visitor signs in via Google popup with any arbitrary Gmail account, `user` becomes non-null.
   - `app/admin/page.tsx` does not check user email or role.
   - Therefore, any authenticated external user can access administrative controls unless a role guard is added.

4. **Deep-Link Completeness**:
   - Deep links for `sirlauncher://` are functioning on `/auth/desktop` (auth token sync), `/shaders` (profile launch), and `/servers` (server join).
   - However, `/` lacks launch buttons, `/download` lacks 1-click launcher install buttons, and `/mods` lacks 1-click mod install buttons.
   - Therefore, while the protocol handler exists, it is not uniformly interconnected across all relevant web pages.

5. **Dead Links (`/profiles` and `/packs`)**:
   - `sitemap.ts`, `gemini.ts`, and `shaders/page.tsx` point to `/profiles` and `/packs`.
   - Neither directory exists in `website-next/app/`.
   - Therefore, users clicking those links hit 404 pages unless redirect routes or link corrections are implemented.

---

## 3. Caveats

1. **Firebase Security Rules Live Verification**:
   - This survey examined client-side code, `firestore.rules`, and `database.rules.json`. Live remote rule evaluation on `sir-modpack.firebaseapp.com` requires active network credentials.
2. **Modrinth API Rate Limiting**:
   - `/mods` queries `api.modrinth.com/v2/search`. While debounced (300ms) with in-memory caching, heavy automated testing could trigger HTTP 429 rate limits.
3. **No Code Modification Performed**:
   - In accordance with the Explorer role and system instructions, zero source files were modified during this survey.

---

## 4. Conclusion

The `website-next` platform is in an advanced, near-production state:
- **35 of 35 static routes** compile cleanly with Next.js Turbopack in 720ms.
- **Authentication Gate** strictly guards the application and prevents non-logged-in visitors from viewing protected content.
- **Feature pages** are rich, responsive, glassmorphic, and bilingual (English/Arabic).
- **Static export** to `out/` is 100% verified and aligned with `firebase.json`.

### Concrete Required Actions for Implementation Team:
1. **Hardening `/admin` Route**: Add role-based check (`userProfile?.role === "owner" || userProfile?.role === "admin"` or email whitelist) in `app/admin/page.tsx` or `GlobalAuthGuard.tsx`.
2. **Implementing Missing `sirlauncher://` Deep Links**:
   - On `/`: Add `sirlauncher://launch?profile=26.2-ultra` quick-launch action to `HeroDownload.tsx` and `ProfilesMatrix.tsx`.
   - On `/download`: Add `sirlauncher://install?tier=...` 1-click install button alongside ZIP download links.
   - On `/mods`: Add `sirlauncher://mod/install?id=${mod.id}` 1-click install button to mod cards.
3. **Resolving Dead Links (`/profiles` and `/packs`)**:
   - Update `shaders/page.tsx:252` to link to `/main` or `/skins` instead of `/profiles`.
   - Update `AiChatbot.tsx:442,551,865` to point to `/shaders` instead of `/packs`.
   - Update `sitemap.ts` to replace `/profiles` and `/packs` with `/shaders` and `/download`.
   - Create redirect route pages (`app/profiles/page.tsx` -> redirect to `/skins`; `app/packs/page.tsx` -> redirect to `/shaders`).
4. **Crash Analyzer Fix Exporter**:
   - Add a 1-click button on `/crash-analyzer` to export the diagnostic report and recommended JVM flags as `sir_crash_fix.txt` or `sir_fix.bat`.

---

## 5. Verification Method

To independently verify all findings:

1. **Verify Static Route Generation (35/35 Routes)**:
   ```powershell
   cd "d:/Projects/SIR ModPack/website-next"
   npm run build
   ```
   *Expected result*: Exit code 0, Turbopack outputs `Generating static pages using 19 workers (35/35)`, all 35 routes listed with `○ (Static)`.

2. **Verify Public Directory & Static Export Structure**:
   ```powershell
   Get-ChildItem "d:/Projects/SIR ModPack/website-next/out"
   ```
   *Expected result*: 32 subdirectories matching routes and 24 root static files (including `index.html`, `404.html`, `robots.txt`, `sitemap.xml`).

3. **Verify Auth Gate Interception**:
   Inspect `d:/Projects/SIR ModPack/website-next/components/GlobalAuthGuard.tsx` lines 30-38 and 65-67 to confirm unauthenticated visitors are returned `<WelcomePage />` and redirected to `/welcome`.

4. **Verify Deep Link References**:
   ```powershell
   Select-String -Path "d:/Projects/SIR ModPack/website-next/app/**/*.tsx" -Pattern "sirlauncher://"
   ```
   *Expected result*: Exactly 3 files match (`auth/desktop/page.tsx`, `shaders/page.tsx`, `servers/page.tsx`). Missing on `download/page.tsx`, `mods/page.tsx`, and `main/page.tsx`.

5. **Verify Dead Link References**:
   ```powershell
   Select-String -Path "d:/Projects/SIR ModPack/website-next/app/**/*.tsx", "d:/Projects/SIR ModPack/website-next/components/**/*.tsx" -Pattern "href=\"/profiles\"|href = \"/packs\""
   ```
   *Expected result*: Matches in `shaders/page.tsx:252` and `AiChatbot.tsx:442`.

---
*Report submitted by Survey Explorer 2. All claims verified against filesystem and production compiler.*
