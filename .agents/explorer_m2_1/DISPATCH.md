## 2026-08-30T02:50:28Z
You are Explorer 1 for Milestone 2: Native JVM Launch Pipeline & Compatibility.
Your working directory is: D:\Projects\SIR ModPack\.agents\explorer_m2_1

Read:
- ORIGINAL_REQUEST: D:\Projects\SIR ModPack\.agents\ORIGINAL_REQUEST.md
- PROJECT: D:\Projects\SIR ModPack\PROJECT.md
- TEST_INFRA: D:\Projects\SIR ModPack\TEST_INFRA.md

Your scope:
Investigate Feature 7 (Strict RAM Parameter Allocation) and Feature 8 (Pre-Launch Natives Extraction) in `development/launcher_core/native_runner.py` and instance directories.
1. Inspect how `-Xmx` and `-Xms` are assembled. Ensure user-selected RAM limits are strictly preserved without being overwritten by hardcoded defaults.
2. Inspect native extraction logic for LWJGL 2 (1.8.9 Forge: `lwjgl64.dll`, `OpenAL64.dll`) and LWJGL 3 (Modern Fabric 26.2). Ensure pre-launch DLL extraction from libraries / natives cache to the instance's natives folder before JVM process spawn.
3. Formulate concrete code modifications and write a structured handoff report to `D:\Projects\SIR ModPack\.agents\explorer_m2_1\handoff.md`.
When finished, send a message back with your findings.
