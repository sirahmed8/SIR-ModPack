# Dispatch: Worker M3 (Cross-Client Synchronization & Invariant Preservation)

## Identity
- Role: Implementation Worker (Milestone 3)
- Working Directory: `d:/Projects/SIR ModPack/.agents/worker_m3/`
- Parent Conversation ID: `e6854040-b2f7-4215-a3ca-09a5a910d136`

## Mandatory Inputs (Read These First!)
- `d:/Projects/SIR ModPack/.agents/ORIGINAL_REQUEST.md`
- `d:/Projects/SIR ModPack/PROJECT.md`
- `d:/Projects/SIR ModPack/.agents/teamwork_preview_explorer_survey_3/handoff.md`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Exclusive Write Ownership
You own the following files and directories exclusively:
- `d:/Projects/SIR ModPack/exports/` (pruning stale test exports)
- `d:/Projects/SIR ModPack/build_apps/` (pruning PyInstaller work artifacts)
- `d:/Projects/SIR ModPack/website-next/.next/cache/` (pruning compiler cache)
- `d:/Projects/SIR ModPack/tests/test_system_audit_invariants.py`
- `d:/Projects/SIR ModPack/development/tools/sync_options.py`
- `C:/Users/a7med/.lunarclient/profiles.json`
- `C:/Users/a7med/AppData/Roaming/.minecraft/options.txt`
- `C:/Users/a7med/AppData/Roaming/.minecraft/optionsLC.txt`
- `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2/` (options.txt and instance.cfg)
- `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/1.8.9/` (options.txt)
- `d:/Projects/SIR ModPack/server/Fabric_26.2_Server/start_server.bat`
- `d:/Projects/SIR ModPack/server/Fabric_26.2_Server/start_server.sh`

## Detailed Implementation Tasks
1. **Restore Drive D Free Space Invariant ($\ge 18.00\text{ GB}$)**:
   - Safely prune stale test archives in `exports/` (contains ~776 MB of old zip exports).
   - Prune PyInstaller build work cache in `build_apps/` (~113 MB).
   - Prune `.next/cache` (~193 MB).
   - Verify Drive D free space increases to $> 18.6\text{ GB}$.
   - Update `tests/test_system_audit_invariants.py` line 90 check from `>= 15.0` to strictly enforce `>= 18.0` GB.
2. **Harmonize `options.txt` Across All 5 Directories**:
   - Create canonical synchronization tool `development/tools/sync_options.py` that enforces:
     - `gamma:1.0`
     - `enableVsync:false`
     - `key_iris.keybind.toggleShaders:key.keyboard.k`
     - All ReplayMod keybinds (`playeroverview: b`, `marker: m`, `playpause: p`, `keyframerepository: x`, `pathpreview: h`, `positionkeyframe: i`, `timekeyframe: o`)
   - Apply synchronization across:
     1. `d:/Projects/SIR ModPack` instances
     2. `C:/Users/a7med/AppData/Roaming/SIR ModPack` instances
     3. `C:/Users/a7med/.lunarclient` (`optionsLC.txt` gamma: 1.0)
     4. `C:/Users/a7med/AppData/Roaming/.minecraft` (root `options.txt` and instances)
     5. `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2/minecraft` and `1.8.9/minecraft`
3. **Enforce Generational ZGC Flags across All Modern 26.2 Profiles**:
   - Flags required: `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5`
   - In `C:/Users/a7med/.lunarclient/profiles.json`: update modern 26.2 profiles (`SIR 26 Visuals`, `SIR 26 Balanced`, `SIR 26 Performance`) to use Generational ZGC instead of G1GC.
   - In `server/Fabric_26.2_Server/start_server.bat` and `start_server.sh`: append `-XX:ZAllocationSpikeTolerance=5` to `JVM_FLAGS`.
   - In `C:/Users/a7med/AppData/Roaming/PrismLauncher/instances/26.2/`: ensure `instance.cfg` contains the ZGC flags.
4. **Verification**:
   - Run `python tests/test_system_audit_invariants.py` and ensure all invariant tests pass.
   - Run `python ecosystem_doctor.py` and ensure 100% healthy.
   - Check Drive D free space to confirm it is $\ge 18.00\text{ GB}$.

## Handoff Requirements
Write complete results and command outputs to:
`d:/Projects/SIR ModPack/.agents/worker_m3/handoff.md`
Then call `send_message` to parent (`e6854040-b2f7-4215-a3ca-09a5a910d136`).

## 2026-09-08T17:41:28Z
You are Worker M3 for Milestone 3 (Cross-Client Synchronization & Invariant Preservation) of the SIR ModPack Project.
Your working directory is: d:/Projects/SIR ModPack/.agents/worker_m3/
The project workspace root is: d:/Projects/SIR ModPack
