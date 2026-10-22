# SIR ModPack — 4-Tier Opaque-Box E2E Test Architecture (`TEST_INFRA.md`)

## 1. Test Philosophy: Opaque-Box & Requirement-Driven

The testing infrastructure for the **SIR ModPack Master Interconnected Ecosystem** adheres strictly to the **Opaque-Box (Black-Box) Testing Paradigm**. 

All test assertions, expectations, and validation criteria are derived directly from the authoritative product specifications established in:
- `ORIGINAL_REQUEST.md`
- `PROJECT.md` § Requirements, Feature Inventory & Interface Contracts

### Core Tenets:
1. **Specification as Single Source of Truth**: Tests verify observable behavior, contract conformance, external outputs, filesystem state changes, and process interactions against documented contracts. Tests do NOT couple to internal private variables or transient implementation trivia.
2. **Zero-Facade & Real Logic Verification**: Tests never use fake assertions (`assertTrue(True)`). All tests invoke actual service bridges, parsers, validators, cryptographic hashing routines, filesystem mutations, and process supervisors.
3. **Hermetic & Isolated State**: Each test establishes its own isolated sandbox environment (isolated temporary test roots, unique session IDs, clean directory structures) and guarantees full teardown cleanup without polluting developer workspaces or production user runtimes.
4. **Adversarial & Fault-Tolerant Resilience**: Systems must withstand malformed inputs, edge values, corrupted manifests, hostile deep-links, resource starvation, and abrupt cancellations without crashing, memory leaking, or corrupting user data.

---

## 2. 4-Tier Test Architecture Overview

```
+---------------------------------------------------------------------------------+
|                        TIER 4: REAL-WORLD WORKLOAD SCENARIOS                    |
|   Complete end-to-end user journeys: Onboarding, PvP Tournament, Server Admin   |
+---------------------------------------------------------------------------------+
                                        ▲
+---------------------------------------------------------------------------------+
|                     TIER 3: CROSS-FEATURE COMBINATIONS                          |
|   Web-to-Launcher Deep Links, Skin-to-Instance Sync, Backup-Restart Cycles,     |
|   Installer Hardware-to-Instance Profile Matching, OAuth Web-Desktop Handoff    |
+---------------------------------------------------------------------------------+
                                        ▲
+---------------------------------------------------------------------------------+
|                     TIER 2: BOUNDARY & CORNER CASES                             |
|   Empty/Corrupt URLs, Negative PIDs, 18.00 GB Boundary, 0-byte Skins,           |
|   Corrupt Delta Manifests, Buffer Overflows, Unauthenticated Route Access       |
+---------------------------------------------------------------------------------+
                                        ▲
+---------------------------------------------------------------------------------+
|                     TIER 1: FEATURE COVERAGE (HAPPY PATH)                       |
|   18 Isolated Functional Verifications covering Desktop, Server, Installer,    |
|   Web Platform, Sync Invariants, JVM Tuning, and Diagnostics                    |
+---------------------------------------------------------------------------------+
```

---

## 3. Complete Feature Inventory & Tier Mapping

| Feature ID | Ecosystem Feature | Specification Source | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Combination) | Tier 4 (Scenario) |
|---|---|---|:---:|:---:|:---:|:---:|
| **F01** | `sirlauncher://` Native Deep Links | `PROJECT.md` #1 | `test_f01_deep_link_protocol_parsing` | `test_b01_malformed_and_injection_deep_links` | `test_c01_web_to_launcher_instance_dispatch` | Scenario 1, 2 |
| **F02** | Multiplayer Latency Radar | `PROJECT.md` #2 | `test_f02_multiplayer_latency_radar` | `test_b02_extreme_latency_and_socket_timeouts` | `test_c02_radar_to_direct_connect_flow` | Scenario 2 |
| **F03** | Game Integrity Doctor & Self-Healing | `PROJECT.md` #3 | `test_f03_game_integrity_doctor` | `test_b03_corrupt_manifest_and_tampered_jars` | `test_c03_integrity_repair_before_launch` | Scenario 1 |
| **F04** | Win32 RAM Compactor (`psapi.dll`) | `PROJECT.md` #4 | `test_f04_win32_ram_compactor` | `test_b04_invalid_pids_and_zero_memory_trim` | `test_c04_ram_compaction_on_game_boot` | Scenario 2 |
| **F05** | 3D Skin & Cape Studio (4px/3px) | `PROJECT.md` #5 | `test_f05_skin_and_cape_studio` | `test_b05_invalid_skin_dimensions_and_empty_user` | `test_c05_skin_studio_instance_sync` | Scenario 1, 2 |
| **F06** | ServerRestartScheduler & Alerts | `PROJECT.md` #6 | `test_f06_server_restart_scheduler` | `test_b06_zero_negative_countdown_restart` | `test_c06_server_restart_with_auto_backup` | Scenario 3 |
| **F07** | Automated World Snapshots (`keep=5`)| `PROJECT.md` #7 | `test_f07_automated_world_snapshots` | `test_b07_prune_retention_below_threshold` | `test_c06_server_restart_with_auto_backup` | Scenario 3 |
| **F08** | 60s Telemetry Sparklines | `PROJECT.md` #8 | `test_f08_telemetry_canvas_sparklines` | `test_b08_extreme_tps_and_heap_overflow` | `test_c07_sparklines_during_heavy_load` | Scenario 3 |
| **F09** | Pre-Flight Hardware Diagnostic Matrix | `PROJECT.md` #9 | `test_f09_installer_hardware_matrix` | `test_b09_zero_spec_hardware_boundary` | `test_c08_installer_hardware_to_instance_config`| Scenario 1 |
| **F10** | Adoptium OpenJDK 21 LTS Downloader | `PROJECT.md` #10 | `test_f10_adoptium_openjdk21_service` | `test_b10_network_failure_and_corrupt_java_bin` | `test_c08_installer_hardware_to_instance_config`| Scenario 1 |
| **F11** | Custom Drive Selection Engine | `PROJECT.md` #11 | `test_f11_custom_drive_selector` | `test_b11_nonexistent_and_restricted_drives` | `test_c09_drive_selector_to_instance_path` | Scenario 1 |
| **F12** | Web Platform Routes (35 Static Routes)| `PROJECT.md` #12, 18 | `test_f12_web_platform_routes_exist` | `test_b12_unauthenticated_protected_route_access` | `test_c01_web_to_launcher_instance_dispatch` | Scenario 1 |
| **F13** | Strict Welcome & OAuth Security Gate | `PROJECT.md` #13 | `test_f13_strict_welcome_auth_gate` | `test_b12_unauthenticated_protected_route_access` | `test_c10_web_to_desktop_auth_token_handoff` | Scenario 1 |
| **F14** | `options.txt` Cross-Client Invariant | `PROJECT.md` #21 | `test_f14_options_txt_harmonization` | `test_b13_corrupted_options_txt_recovery` | `test_c11_options_harmonization_across_instances` | Scenario 1, 2 |
| **F15** | Generational ZGC JVM Invariant | `PROJECT.md` #22 | `test_f15_generational_zgc_flags` | `test_b14_low_ram_fallback_gc_configuration` | `test_c08_installer_hardware_to_instance_config`| Scenario 1 |
| **F16** | Bedrock Cross-Play Gateway Config | `PROJECT.md` #23 | `test_f16_bedrock_crossplay_gateway` | `test_b15_malformed_bedrock_raknet_packet` | `test_c12_bedrock_and_java_dual_ping` | Scenario 3 |
| **F17** | Drive D $\ge 18.00\text{ GB}$ Storage Invariant| `PROJECT.md` #19, 20 | `test_f17_drive_d_storage_invariant` | `test_b16_drive_d_exact_boundary_threshold` | `test_c13_storage_invariant_after_full_backup` | Scenario 3 |
| **F18** | Git Repositories Health & Branches | `PROJECT.md` #29 | `test_f18_git_repositories_branch_status`| `test_b17_untracked_and_dirty_git_worktrees` | `test_c14_git_release_parity_validation` | Acceptance |

---

## 4. Detailed Tier Specifications & Methodology

### Tier 1: Feature Coverage (Opaque-Box Functional Verification)
Each test in Tier 1 validates a single feature against its specification contract:
- Input parameters are well-formed and valid (Happy Path).
- Return payloads match expected schemas, keys, and types.
- Side-effects on disk, state, or network buffers are deterministic and verified.

### Tier 2: Boundary & Corner Cases (Defensive Robustness)
Tier 2 subjects all interfaces to hostile, degraded, and edge-condition inputs:
- **String & URL Stress**: Empty strings, malformed URI encodings, shell command injection strings (`; rm -rf /`, `& calc.exe`), SQL meta-characters, oversized 100KB payloads.
- **Numerical Boundaries**: Negative countdown timers, zero seconds, negative PIDs, zero-byte allocations, RAM and disk usage at exact boundary thresholds (18.00 GB vs 17.99 GB).
- **Filesystem Anomalies**: Missing directories, 0-byte corrupt JSON manifests, truncated archives, read-only permissions.
- **Security Boundaries**: Unauthenticated access attempts to `/admin`, `/mods`, `/servers`, `/download` verifying immediate intercept by the Auth Gate.

### Tier 3: Cross-Feature Combinations (Integration Workflows)
Tier 3 tests the interaction between two or more subsystems:
- **Web-to-Launcher Deep-Link Execution**: Web portal constructs deep link -> Launcher parses command -> Instance selector activates requested profile -> Shaders preset is applied.
- **Skin Studio to Modern & Legacy Instances**: User selects preset skin (`sir_cyber_warrior`) and cape (`sir_obsidian_neon`) -> Assets are written and mirrored to both Modern (`26.2`) and Legacy (`1.8.9`) instance configurations.
- **Server Restart & Automated Snapshot Retention**: Scheduler triggers restart countdown -> Automated world backup `.zip` is generated -> 5-rotation pruning runs, eliminating older archives -> Discord webhook notification is formatted.
- **Hardware Profile Auto-Matching**: Installer diagnostic measures hardware capabilities -> Maps machine to appropriate tier (`ultra`, `balanced`, or `comp`) -> Injects Generational ZGC flags (`-XX:+UseZGC -XX:+ZGenerational`) and dedicated memory into `instance.cfg`.

### Tier 4: Real-World Workload Scenarios (Full User Journeys)
Tier 4 simulates multi-step, realistic persona journeys:
1. **Scenario 1 (New User Onboarding Journey)**:
   - Unauthenticated visitor hits `/welcome` -> Completes Google OAuth -> Visits `/download` -> Downloads Installer Pro -> Diagnostic matrix passes hardware (RAM, Disk, AVX2, Java 21) -> Selects target volume -> Modern 26.2 instance configured with Generational ZGC and custom `options.txt` -> Launcher opens ready to play.
2. **Scenario 2 (Competitive PvP Tournament Journey)**:
   - User launches SIR Launcher Pro -> Latency Radar identifies optimal server (<20ms ping) -> User joins directly -> Win32 RAM Compactor flushes working set memory pages to free background RAM -> Skin Studio activates tournament skin (`sir_esports_pro`) -> Invariant settings enforce VSync disabled and low input lag.
3. **Scenario 3 (Server Administrator 24/7 Maintenance Journey)**:
   - Administrator opens Server Manager Pro -> Live sparklines display active TPS (20.0) and heap memory -> Administrator triggers on-demand backup -> Automated world snapshot created and verified -> 5-archive retention policy pruned -> Graceful 600s restart scheduled with warning broadcasts across chat and Discord.

---

## 5. Test Execution & Quality Gates

### Execution Command:
```bash
python -m unittest discover -s tests_e2e -p "test_*.py" -v
```
or standalone:
```bash
python tests_e2e/test_e2e_suite.py
```

### Quality Acceptance Gates:
1. **100% Pass Rate**: 0 failures, 0 errors across all 4 tiers.
2. **Invariant Strictness**: Free space on Drive D must remain $\ge 18.00\text{ GB}$.
3. **Zero Resource Leakage**: All temporary files, mock processes, and threads must be cleaned up upon test suite completion.
4. **Deterministic Runtime**: Test suite should complete in under 30 seconds on local developer workstation.
