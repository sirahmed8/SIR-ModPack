# Dispatch: Worker M4 (Final Acceptance & Production Deployment)

## Identity
- Role: Implementation Worker (Milestone 4 - Final Acceptance & Deployment)
- Working Directory: `d:/Projects/SIR ModPack/.agents/worker_m4/`
- Parent Conversation ID: `e6854040-b2f7-4215-a3ca-09a5a910d136`

## Mandatory Inputs (Read These First!)
- `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`
- `d:/Projects/SIR ModPack/PROJECT.md`
- `d:/Projects/SIR ModPack/TEST_READY.md`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Detailed Tasks
1. **Execute Complete E2E Test Suite (Tiers 1-4)**:
   - Command: `python tests_e2e/test_e2e_suite.py`
   - Verify 100% of the 39 tests pass with 0 failures and 0 errors.
2. **Execute Complete Unit Test Suite (368+ Tests)**:
   - Command: `python -m unittest discover -s tests -p "test_*.py" -v`
   - Verify all 368+ tests pass with 0 failures and 0 errors.
3. **Execute Ecosystem Health Doctor**:
   - Command: `python ecosystem_doctor.py`
   - Verify 100% healthy across all 6 diagnostic layers.
4. **Verify Drive D Invariant**:
   - Confirm Drive D free space $\ge 18.00\text{ GB}$.
5. **Build & Deploy Web Platform to Firebase Hosting**:
   - In `website-next/`:
     - Run `npm run build` to generate `out/`.
     - Deploy to Firebase Hosting: `npx firebase-tools deploy --only hosting` (or `firebase deploy --only hosting`).
     - Verify deployment succeeds with URL: `https://sir-modpack.web.app`.
6. **Git Status & Sync for Both Repositories**:
   - In `website-next/`:
     - Run `git status`.
     - Commit any uncommitted changes with message `feat(web): elevate all 35 routes, harden /admin auth gate, and wire sirlauncher deep links`.
     - Push to remote `main`.
   - In `public_repo/`:
     - Run `git status`.
     - If changes exist, commit and push to `main`.
     - Confirm working tree is clean.

## Output Requirements
Write complete execution outputs and verification logs to:
`d:/Projects/SIR ModPack/.agents/worker_m4/handoff.md`
Then call `send_message` to parent (`e6854040-b2f7-4215-a3ca-09a5a910d136`).

## 2026-09-08T18:00:00Z
You are Worker M4 for Milestone 4 (Final Acceptance & Production Deployment) of the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/worker_m4/
The project workspace root is: d:/Projects/SIR ModPack

MANDATORY FIRST STEP:
Read your dispatch file at `d:/Projects/SIR ModPack/.agents/worker_m4/DISPATCH.md`, read `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`, and read `d:/Projects/SIR ModPack/TEST_READY.md`.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MISSION:
1. Run E2E Test Suite: `python tests_e2e/test_e2e_suite.py` (verify 39/39 tests pass).
2. Run Full Unit Test Suite: `python -m unittest discover -s tests -p "test_*.py" -v` (verify all 368+ tests pass with 0 failures, 0 errors).
3. Run Ecosystem Doctor: `python ecosystem_doctor.py` (verify 100% healthy across all 6 layers).
4. Verify Drive D Free Space: confirm >= 18.00 GB free.
5. Build and Deploy Web Platform to Firebase Hosting:
   - In `website-next/`, run `npm run build`.
   - Deploy to Firebase Hosting: `npx firebase-tools deploy --only hosting` (or `firebase deploy --only hosting`).
   - Verify deployment succeeded to `sir-modpack.web.app`.
6. Git Status & Push:
   - In `website-next/`: check `git status`, commit changes if any, push to `main`.
   - In `public_repo/`: check `git status`, commit changes if any, push to `main`.
   - Confirm both working trees are clean.

OUTPUT:
Write detailed completion report with exact command logs and deployment URL to:
`d:/Projects/SIR ModPack/.agents/worker_m4/handoff.md`
Then call `send_message` to parent (e6854040-b2f7-4215-a3ca-09a5a910d136).

