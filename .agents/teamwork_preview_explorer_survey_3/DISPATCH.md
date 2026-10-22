# Dispatch: Survey Explorer 3 (Cross-Client Sync, Invariants, Test & Acceptance Criteria)

## Identity
- Role: Explorer (Survey 3 - Cross-Client Sync, Invariants, Test & Acceptance Criteria)
- Working Directory: d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3/
- Parent Conversation ID: e6854040-b2f7-4215-a3ca-09a5a910d136

## Mandatory Inputs
- Original Request: `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md` (Read this first!)

## Mission & Objectives
Investigate R3 Cross-Client Synchronization, Invariants, and overall Acceptance Criteria verification:
1. **Multi-Folder Directories & options.txt Harmonization**:
   - Inspect all 5 target directories:
     1. `d:/Projects/SIR ModPack`
     2. `C:/Users/a7med/AppData/Roaming/SIR ModPack`
     3. `C:/Users/a7med/.lunarclient`
     4. `C:/Users/a7med/AppData/Roaming/.minecraft`
     5. `C:/Users/a7med/AppData/Roaming/PrismLauncher`
   - Check if each exists, where `options.txt` is located in each, and the current settings (gamma: 1.0, vsync: false, Iris toggle: K, ReplayMod keybinds).
   - Check existing synchronization scripts or tooling in `d:/Projects/SIR ModPack`.
2. **Generational ZGC Flags**:
   - Inspect Minecraft profile definitions (launcher profiles, Prism instances, Lunar profiles, scripts) for Generational ZGC flags (`-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5`) across modern profiles (26.2).
3. **Bedrock Cross-Play & Server Health**:
   - Check Bedrock Cross-Play templates (`Geyser-Spigot/config.yml` on UDP 19132).
   - Check `server/server_health_check.py` and its integration.
4. **Drive D Invariant & Disk Management**:
   - Check current free space on Drive D (must maintain >= 18.00 GB).
   - Check how disk space is checked and monitored across the codebase and `ecosystem_doctor.py`.
5. **Git Repositories**:
   - Check Git status and remotes for `public_repo` (on `main`) and `website-next` (on `main`).
6. **Overall Test & Acceptance Verification Strategy**:
   - Inventory existing unit tests (`python -m unittest discover -s tests -p "test_*.py" -v`).
   - Identify how E2E tests and Acceptance Criteria should be structured.

## Output Requirements
Produce a comprehensive, structured report in:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3/handoff.md`
Detailing:
- Audit of the 5 directories and `options.txt` state.
- Audit of ZGC flags, Bedrock templates, server health check.
- Drive D free space status and invariant preservation plan.
- Git repository status (`public_repo`, `website-next`).

## 2026-09-08T17:31:04Z
You are Survey Explorer 3 for the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3/
The project workspace root is: d:/Projects/SIR ModPack

MANDATORY FIRST STEP:
Read your dispatch file at `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3/DISPATCH.md` and read `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`.

YOUR ROLE & MISSION:
You are a READ-ONLY explorer. DO NOT modify any source code files.
Investigate R3 Cross-Client Synchronization, Invariants, and overall Acceptance Criteria verification:
1. Multi-folder ecosystem & options.txt: Inspect all 5 directories:
   - `d:/Projects/SIR ModPack`
   - `C:/Users/a7med/AppData/Roaming/SIR ModPack`
   - `C:/Users/a7med/.lunarclient`
   - `C:/Users/a7med/AppData/Roaming/.minecraft`
   - `C:/Users/a7med/AppData/Roaming/PrismLauncher`
   Audit existence, options.txt state (gamma: 1.0, vsync: false, Iris toggle: K, ReplayMod keybinds), and sync scripts.
2. Generational ZGC flags: Audit profiles for `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5` across modern profiles (26.2).
3. Bedrock Cross-Play templates (`Geyser-Spigot/config.yml` UDP 19132) and `server/server_health_check.py`.
4. Drive D free space invariant (>= 18.00 GB) checking and protection.
5. Git repositories: Check status of `public_repo` (main) and `website-next` (main).
6. Unit test inventory (`python -m unittest discover -s tests -p "test_*.py" -v`).

OUTPUT:
Write your complete, structured survey report to:
`d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3/handoff.md`
Then call `send_message` to your parent (e6854040-b2f7-4215-a3ca-09a5a910d136) notifying that your survey handoff is complete.
