# BRIEFING — 2026-08-30T02:57:30Z

## Mission
Investigate Feature 7 (Strict RAM Parameter Allocation) and Feature 8 (Pre-Launch Natives Extraction) in native_runner.py and instance directories for Milestone 2.

## 🔒 My Identity
- Archetype: explorer
- Roles: [investigator, analyst]
- Working directory: D:\Projects\SIR ModPack\.agents\explorer_m2_1
- Original parent: 619c3ef7-4451-4adc-9c7a-d1eaffe6a8e8
- Milestone: Milestone 2: Native JVM Launch Pipeline & Compatibility

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Investigate Feature 7 (RAM parameter allocation: -Xmx, -Xms)
- Investigate Feature 8 (Pre-Launch Natives Extraction for LWJGL 2 & 3)
- Write structured handoff report to D:\Projects\SIR ModPack\.agents\explorer_m2_1\handoff.md

## Current Parent
- Conversation ID: 619c3ef7-4451-4adc-9c7a-d1eaffe6a8e8
- Updated: 2026-08-30T02:50:28Z

## Investigation State
- **Explored paths**:
  - `development/launcher_core/native_runner.py` (RAM parsing, calculate_ram_parameters, build_jvm_args, extract_natives, resolve_natives_dir, inspect_instance_config)
  - `development/launcher_core/instance_service.py` (RAM args, create_custom_instance, launch_instance)
  - `tests/test_native_runner.py` (Full 40-test suite)
  - `instances/26.2`, `instances/26.2-ultra`, `instances/1.8.9` (instance.cfg, mmc-pack.json)
  - `%APPDATA%/.minecraft/libraries` (LWJGL 2 & 3 native jars and DLL architectures)
- **Key findings**:
  - `_parse_to_mb` dropped "4GB" / "6144MB" to default 8192 MB due to regex missing trailing 'B'.
  - `instance_service.py` had hardcoded `f"-Xms{max(2, ram_gb // 2)}G"`, leading to illegal `-Xms2G -Xmx1G` for 1GB allocations.
  - `inspect_instance_config` failed to find `instance.cfg` / `mmc-pack.json` when passed `instances/26.2/minecraft` subfolder.
  - `extract_natives` was extracting LWJGL 2 jars after LWJGL 3, causing a 32-bit legacy `lwjgl.dll` to overwrite the 64-bit modern `lwjgl.dll` in 26.2.
- **Unexplored areas**: None (investigation complete).

## Key Decisions Made
- Formulated concrete code modifications for `native_runner.py` and `instance_service.py`.
- Formatted and generated complete 5-component handoff report in `handoff.md`.

## Artifact Index
- D:\Projects\SIR ModPack\.agents\explorer_m2_1\BRIEFING.md — Persistent context & state
- D:\Projects\SIR ModPack\.agents\explorer_m2_1\progress.md — Liveness & step progress
- D:\Projects\SIR ModPack\.agents\explorer_m2_1\handoff.md — Final 5-component handoff report
