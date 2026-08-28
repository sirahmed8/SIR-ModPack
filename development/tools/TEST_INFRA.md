# E2E Test Infra: Aetheris Minecraft Ecosystem

## Test Philosophy
- Requirement-driven, opaque-box, independent verification deriving from `ORIGINAL_REQUEST.md`.
- Methodology: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + Real-World Workload Scenarios + White-Box Adversarial Stress Testing.

## Feature Inventory Mapping
| # | Feature | Requirement | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Scenario) |
|---|---------|-------------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| 1 | F1: Duplicate Mod Purge | R1 | 5 cases | 5 cases | ✓ | ✓ |
| 2 | F2: Incompatible Mod Removal | R1 | 5 cases | 5 cases | ✓ | ✓ |
| 3 | F3: Missing Dependencies | R1 | 5 cases | 5 cases | ✓ | ✓ |
| 4 | F4: Manifest & Shader Fixes | R1 | 5 cases | 5 cases | ✓ | ✓ |
| 5 | F5: Prism 1.8.9 Population | R1, R4 | 5 cases | 5 cases | ✓ | ✓ |
| 6 | F6: Entity & Block Culling | R2 | 5 cases | 5 cases | ✓ | ✓ |
| 7 | F7: C2ME Threading & SIMD | R2 | 5 cases | 5 cases | ✓ | ✓ |
| 8 | F8: Physics & Particle Limits | R2 | 5 cases | 5 cases | ✓ | ✓ |
| 9 | F9: Network & Frametime Tuning| R2 | 5 cases | 5 cases | ✓ | ✓ |
| 10| F10: Aetheris Core Memory | R3 | 5 cases | 5 cases | ✓ | ✓ |
| 11| F11: Mixin & Performance Hooks| R3 | 5 cases | 5 cases | ✓ | ✓ |
| 12| F12: Launcher Sync & RPC | R3, R4 | 5 cases | 5 cases | ✓ | ✓ |
| 13| F13: Launcher & Share Parity | R4 | 5 cases | 5 cases | ✓ | ✓ |

## Test Architecture
- **Test Runner**: Python-based automated test suite `tests/run_e2e_tests.py` using standard verification libraries (zipfile, json, toml, javap / classfile bytecode inspection).
- **Pass/Fail Semantics**: Exit code 0 indicates 100% test pass. Any failed assertion yields non-zero exit code with detailed diagnostic log.
- **Directory Layout**:
  - `tests/e2e/test_tier1_features.py`
  - `tests/e2e/test_tier2_boundaries.py`
  - `tests/e2e/test_tier3_pairwise.py`
  - `tests/e2e/test_tier4_workloads.py`
  - `tests/e2e/test_tier5_adversarial.py`

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Target Profile |
|---|----------|--------------------|----------------|
| 1 | High-Speed Flight Chunk Generation | F1, F3, F7, F9, F10 | Modern 26.2 (Balanced & Visual) |
| 2 | High-Density Mob & Chest Megabase Rendering | F6, F8, F9, F11 | Modern 26.2 (Visual & Performance) |
| 3 | TNT Explosion & Heavy Ragdoll Physics Stress | F8, F10, F11 | Modern 26.2 (Visual & Balanced) |
| 4 | Clean Profile Startup & Log Audit | F1, F2, F3, F4, F5, F13 | Lunar 26.2, Prism 26.2, Lunar 1.8.9, Prism 1.8.9 |
| 5 | Cross-Launcher Configuration Parity Check | F5, F12, F13 | Lunar vs Prism vs AetherisShare |

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥65 tests (5 tests × 13 core features).
- **Tier 2 (Boundary & Corner Cases)**: ≥65 tests (limit values, invalid formats, empty dirs, max thread allocations).
- **Tier 3 (Pairwise Combinations)**: ≥15 cross-feature interaction tests.
- **Tier 4 (Real-World Application Scenarios)**: 5 comprehensive multi-system workload tests.
- **Tier 5 (Adversarial White-Box & Security Forensics)**: Bytecode disassembly checks, mixin refmap verification, zero hardcoding audit.
- **Total Minimum Test Count**: ≥150 assertions.
