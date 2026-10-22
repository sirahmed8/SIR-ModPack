# Dispatch: E2E Testing Track (Test Writer)

## Identity
- Role: Test Writer (E2E Testing Track)
- Working Directory: `d:/Projects/SIR ModPack/.agents/teamwork_preview_test_writer_e2e/`
- Parent Conversation ID: `e6854040-b2f7-4215-a3ca-09a5a910d136`

## Mandatory Inputs (Read These First!)
- `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`
- `d:/Projects/SIR ModPack/PROJECT.md`

## Mission & Scope
Design and build the comprehensive, opaque-box E2E test suite derived strictly from user requirements in `ORIGINAL_REQUEST.md`:
1. **Create `TEST_INFRA.md`** at workspace root following the E2E Testing Track template:
   - Test philosophy (opaque-box, requirement-driven)
   - Complete Feature Inventory mapped to Tiers 1-4
   - Coverage thresholds and methodology
2. **Build E2E Test Suite in `tests_e2e/`**:
   - `test_e2e_suite.py` (and supporting runner/harness):
     - **Tier 1 (Feature Coverage)**: Isolated happy-path checks for all features (desktop deep-links, latency radar cache, integrity doctor, RAM compactor, skin studio, server restart scheduler, backup pruning, sparklines, installer diagnostics, adoptium downloader, drive selector, web routes, auth gate, options sync, ZGC flags, Bedrock gateway, Drive D space, git repos).
     - **Tier 2 (Boundary & Corner Cases)**: Empty/invalid deep-link URLs, extreme latencies, corrupted delta files, invalid memory trimming PIDs, invalid skin dimensions, zero countdown restart, prune with < 5 archives, extreme TPS/RAM sparkline inputs, zero disk/RAM hardware specs, invalid drive letters, unauthenticated route access attempts, missing options.txt lines, Drive D space boundary at 18.00 GB.
     - **Tier 3 (Cross-Feature Combinations)**: Web-to-Launcher deep link actions, launcher skin change synced to instance, server restart with automated world backup, installer drive validation matched with launcher instance path, auth token sync from web to desktop.
     - **Tier 4 (Real-World Workload Scenarios)**: Full user onboarding journey (Installer hardware check -> Launcher install -> Skin selection -> Server join via Radar -> RAM compaction during gameplay -> Server manager backup & restart cycle).
3. **Publish `TEST_READY.md`** at workspace root:
   - Test runner command (`python -m unittest discover -s tests_e2e -p "test_*.py" -v` or `python tests_e2e/test_e2e_suite.py`)
   - Complete coverage table and feature checklist across all 4 tiers.
4. **Execute and Verify**:
   - Run the newly created E2E test suite to verify initial execution results.

## Handoff Requirements
Write complete results and command outputs to:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_test_writer_e2e/handoff.md`

## 2026-09-08T17:41:28Z
You are the E2E Test Writer for the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/teamwork_preview_test_writer_e2e/
The project workspace root is: d:/Projects/SIR ModPack

MANDATORY FIRST STEP:
Read your dispatch file at `d:/Projects/SIR ModPack/.agents/teamwork_preview_test_writer_e2e/DISPATCH.md`, read `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`, and read `d:/Projects/SIR ModPack/PROJECT.md`.

MISSION:
1. Create `TEST_INFRA.md` at workspace root documenting the 4-tier opaque-box test architecture.
2. Implement comprehensive E2E test suite in `tests_e2e/test_e2e_suite.py` covering:
   - Tier 1: Feature Coverage across all inventoried features.
   - Tier 2: Boundary & Corner Cases (empty/malformed URLs, invalid PIDs, edge memory limits, 18.00 GB disk boundary).
   - Tier 3: Cross-Feature Combinations (web-to-desktop deep links, skin sync, restart backup cycle).
   - Tier 4: Real-World Workload Scenarios (complete user journeys).
3. Publish `TEST_READY.md` at workspace root with runner instructions and coverage matrices.
4. Execute the test suite and verify test execution.

OUTPUT:
Write complete report to `d:/Projects/SIR ModPack/.agents/teamwork_preview_test_writer_e2e/handoff.md` and send message to parent (e6854040-b2f7-4215-a3ca-09a5a910d136).
