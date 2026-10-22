# Dispatch: Worker M2 (Web Platform Elevation & Security Hardening)

## Identity
- Role: Implementation Worker (Milestone 2)
- Working Directory: `d:/Projects/SIR ModPack/.agents/worker_m2/`
- Parent Conversation ID: `e6854040-b2f7-4215-a3ca-09a5a910d136`

## Mandatory Inputs (Read These First!)
- `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`
- `d:/Projects/SIR ModPack/PROJECT.md`
- `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_2/handoff.md`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Exclusive Write Ownership
You own the following files in `website-next/` exclusively:
- `website-next/app/admin/page.tsx`
- `website-next/components/HeroDownload.tsx`
- `website-next/components/ProfilesMatrix.tsx`
- `website-next/app/download/page.tsx`
- `website-next/app/mods/page.tsx`
- `website-next/app/crash-analyzer/page.tsx`
- `website-next/app/shaders/page.tsx`
- `website-next/components/AiChatbot.tsx`
- `website-next/app/sitemap.ts`
- `website-next/app/profiles/page.tsx` (new redirect page)
- `website-next/app/packs/page.tsx` (new redirect page)

## Detailed Implementation Tasks
1. **Security Hardening on `/admin` (`website-next/app/admin/page.tsx`)**:
   - Integrate `useEcosystem()` to check role:
     `userProfile?.role === "owner" || userProfile?.role === "admin" || userProfile?.email === "sir.ahmed.owner@gmail.com"`
   - If not authorized, render a cyber-styled "Access Denied — Administrator Privileges Required" card with a "Return to Dashboard" button.
2. **Wire Native `sirlauncher://` Deep Links Across Feature Pages**:
   - **`/` (Hero & ProfilesMatrix)**: In `HeroDownload.tsx` and `ProfilesMatrix.tsx`, provide quick-launch buttons invoking `sirlauncher://launch?profile=26.2-ultra` (or selected profile).
   - **`/download`**: In `app/download/page.tsx`, add an interactive "1-Click Launcher Install" button with `sirlauncher://install?tier=${tier.id}` alongside the direct ZIP download cards.
   - **`/mods`**: In `app/mods/page.tsx`, add a "⚡ Install to Launcher" button on mod cards and mod modal calling `sirlauncher://mod/install?id=${encodeURIComponent(mod.id)}`.
3. **Dead Link Remediation**:
   - In `app/shaders/page.tsx:252`: Change `href="/profiles"` to `href="/skins"`.
   - In `components/AiChatbot.tsx`: Replace `/packs` references with `/shaders`.
   - In `app/sitemap.ts`: Ensure URLs refer only to existing routes.
   - Create `app/profiles/page.tsx` and `app/packs/page.tsx` as lightweight client-side redirect pages (to `/skins` and `/shaders`).
4. **Crash Analyzer Exporter (`app/crash-analyzer/page.tsx`)**:
   - Add a 1-click button "Export Diagnostic Report & Fix" that downloads a formatted `.txt` report containing the error diagnosis, matched cause, and recommended JVM launch flags.
5. **Static Compilation & Build Verification**:
   - In `website-next/`, run `npm run build`.
   - Verify all static routes compile cleanly with zero TypeScript or build errors and generate the `out/` export directory.

## Handoff Requirements
Write complete results, build logs, and route verification outputs to:
`d:/Projects/SIR ModPack/.agents/worker_m2/handoff.md`
Then call `send_message` to parent (`e6854040-b2f7-4215-a3ca-09a5a910d136`).
