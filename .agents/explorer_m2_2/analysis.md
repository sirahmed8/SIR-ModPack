# Deep Codebase Analysis: Milestone 2 — Features 7 & 10
**Author**: Explorer 2 (Milestone 2: Native JVM Launch Pipeline & Compatibility)  
**Date**: 2026-08-30  
**Scope**: 
- **Feature 7**: Strict RAM Parameter Allocation (`native_runner.py`, `instance_service.py`, `shared_core`)
- **Feature 10**: Stable JRE Runtime Locator (`java_service.py`, `native_runner.py`, `shared_core/runtime.py`)

---

## 1. Executive Summary

Milestone 2 establishes the high-performance Native JVM execution pipeline for the SIR Minecraft Ecosystem, supporting both **Modern Fabric 26.2 (Minecraft 1.21.4+)** and **Legacy Forge 1.8.9**.

Our deep investigation identified critical architectural gaps, hardcoded clamps, and deduplication bugs in the existing codebase:
1. **Feature 7 (Strict RAM Parameter Allocation)**:
   - In `native_runner.py` line 549, `max_ram = max(4, ram_gb)` forcibly clamps `-Xmx` to a minimum of 4GB. If a user on a 4GB system or a lightweight legacy profile configures 1GB, 2GB, or 3GB, `-Xmx` is forcibly overwritten to 4GB, which can cause immediate JVM startup crashes (`Could not reserve enough space for object heap`) or system memory exhaustion.
   - In `native_runner.py` line 548, `min_ram = max(2, ram_gb // 2)` results in an invalid configuration where `-Xms` (2GB) exceeds user-selected `-Xmx` (1GB), causing an immediate JVM initialization fatal error.
   - G1GC nursery and region size parameters are statically hardcoded (`-XX:G1HeapRegionSize=32M`), which is suboptimal or invalid for heaps $< 4\text{GB}$ (violating the G1GC ~2048 region target) and lacks dynamic nursery percentage scaling (`G1NewSizePercent` / `G1MaxNewSizePercent`).
2. **Feature 10 (Stable JRE Runtime Locator)**:
   - In `java_service.py` line 51-54, deduplication logic adds `norm.lower()` to `seen_paths` *before* resolving `javaw.exe`, resulting in duplicate entries for the same binary (e.g. `java.exe` vs `javaw.exe`).
   - `java_service.py` has **no architecture detection (x64 vs ARM64 vs x86 32-bit)**. 32-bit JREs in `C:\Program Files (x86)\Java` are parsed as generic runtimes without bitness flags, which risks loading 64-bit LWJGL DLLs on a 32-bit JVM (`UnsatisfiedLinkError`) or crashing on RAM allocations $> 1.5\text{GB}$.
   - Version probing uses rudimentary substring matching (`"21" in raw_ver` or `"1.8" in raw_ver`), which fails for versions like `25-ea`, `22`, `23`, `24`, `11`, `17.0.12`, or vendor strings.
   - Registry discovery is limited to `HKEY_LOCAL_MACHINE` and ignores `HKEY_CURRENT_USER` (where modern user-level Adoptium/Temurin or Microsoft OpenJDK installers register).

---

## 2. Feature 7: Strict RAM Parameter Allocation

### 2.1 Problem Analysis & Existing Code Inspection

In `development/launcher_core/native_runner.py` (lines 546–581):
```python
def build_jvm_args(self, ram_gb: int = 8, natives_dir: str = "", power_mode: str = "turbo") -> List[str]:
    """Constructs Aikar's tuned high-performance JVM optimization flags."""
    min_ram = max(2, ram_gb // 2)
    max_ram = max(4, ram_gb)  # <--- CRITICAL BUG: Forced fallback degradation / clamp!
    
    args = [
        f"-Xms{min_ram}G",
        f"-Xmx{max_ram}G",
        f"-Djava.library.path={natives_dir}",
        "-Dfile.encoding=UTF-8",
        "-Djava.net.preferIPv4Stack=true",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=15",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M",  # <--- CRITICAL BUG: Fixed 32M breaks heaps < 4GB!
        "-XX:+AlwaysPreTouch",
        "-XX:+UseStringDeduplication",
        ...
```

#### Key Flaws Identified:
1. **Forced Clamping Violation**:
   - For `ram_gb = 1`: `min_ram = 2`, `max_ram = 4`. Output is `-Xms2G -Xmx4G`. If the system only has 2GB physical RAM, this immediately fails. Furthermore, if `max_ram` was not clamped, `-Xms2G -Xmx1G` would throw `Error: Incompatible minimum and maximum heap sizes specified`.
   - For `ram_gb = 2`: `min_ram = 2`, `max_ram = 4`. The user's explicit 2GB setting is ignored and overridden to 4GB.
   - For `ram_gb = 3`: `min_ram = 2`, `max_ram = 4`. Overridden to 4GB.
2. **Missing Granular Unit Support (MB & GB)**:
   - Does not accept granular memory values (e.g. 1024MB, 3072MB, 6144MB), floating point GB (e.g. 2.5GB), or explicit `(min_ram, max_ram)` boundary tuples.
3. **Static Heap Region Size (`-XX:G1HeapRegionSize=32M`)**:
   - G1GC functions by dividing heap into $\sim 2048$ regions.
   - On a 2GB heap, `32M` region size yields only 64 regions ($2048\text{MB} / 32\text{MB} = 64$), causing GC pauses to spike and defeating G1GC's incremental pause targets.
   - Region sizes must scale dynamically:
     - Heap $< 2\text{GB}$: 1MB or omitted (JVM ergonomic default)
     - Heap $2\text{GB} - 4\text{GB}$: 2MB
     - Heap $4\text{GB} - 8\text{GB}$: 4MB–8MB
     - Heap $8\text{GB} - 16\text{GB}$: 16MB
     - Heap $\ge 16\text{GB}$: 32MB
4. **Static Nursery Sizing**:
   - Sizing of the young generation (`G1NewSizePercent` and `G1MaxNewSizePercent`) must adapt to heap size:
     - Low memory ($\le 3\text{GB}$): `G1NewSizePercent=20`, `G1MaxNewSizePercent=30`, `G1ReservePercent=10` (prevents young gen from crowding out old gen).
     - Standard memory ($4\text{GB} - 8\text{GB}$): `G1NewSizePercent=30`, `G1MaxNewSizePercent=40`, `G1ReservePercent=15` (Aikar baseline).
     - High memory ($> 8\text{GB} - 16\text{GB}$): `G1NewSizePercent=40`, `G1MaxNewSizePercent=50`, `G1ReservePercent=20`.
     - Massive memory ($> 16\text{GB}$): `G1NewSizePercent=50`, `G1MaxNewSizePercent=60`, `G1ReservePercent=20`.
5. **Instance Configuration Overrides**:
   - `instance_service.py` (`launch_instance`) ignores instance-specific `instance.cfg` memory settings (`MinMemAlloc`, `MaxMemAlloc`, `OverrideMemory`) and blindly uses global `launcher_settings.json` `ram_allocated_gb`.

---

### 2.2 Strict RAM Allocation Implementation Strategy

#### Model Design:
```python
def calculate_ram_parameters(
    max_ram: int | float | str = 8,
    min_ram: Optional[int | float | str] = None,
    mc_version: str = "26.2"
) -> Dict[str, Any]:
    """Strictly parses and normalizes RAM boundaries without arbitrary upward clamps."""
    
    # 1. Parse max_ram to MB
    max_mb = _parse_to_mb(max_ram, default_mb=8192)
    
    # 2. Parse min_ram to MB (strictly bounded: 256MB <= min_mb <= max_mb)
    if min_ram is not None:
        min_mb = _parse_to_mb(min_ram, default_mb=max(256, max_mb // 2))
        min_mb = max(256, min(min_mb, max_mb))
    else:
        # Default policy: min_mb = max(512, max_mb // 2) if max_mb >= 1024 else max_mb
        min_mb = max(512, max_mb // 2) if max_mb >= 1024 else max_mb
        min_mb = min(min_mb, max_mb)

    # 3. Format -Xms and -Xmx arguments
    xms_arg = f"-Xms{min_mb // 1024}G" if min_mb % 1024 == 0 else f"-Xms{min_mb}M"
    xmx_arg = f"-Xmx{max_mb // 1024}G" if max_mb % 1024 == 0 else f"-Xmx{max_mb}M"

    # 4. Calculate dynamic G1GC Nursery and Region Parameters
    max_gb = max_mb / 1024.0
    if max_gb <= 3.0:
        new_size_pct = 20
        max_new_size_pct = 30
        reserve_pct = 10
        region_size = "1M" if max_gb < 2.0 else "2M"
    elif max_gb <= 8.0:
        new_size_pct = 30
        max_new_size_pct = 40
        reserve_pct = 15
        region_size = "4M" if max_gb <= 4.0 else "8M"
    elif max_gb <= 16.0:
        new_size_pct = 40
        max_new_size_pct = 50
        reserve_pct = 20
        region_size = "16M"
    else:
        new_size_pct = 50
        max_new_size_pct = 60
        reserve_pct = 20
        region_size = "32M"

    is_legacy_189 = any(k in str(mc_version) for k in ["1.8", "1.7"])
    pause_millis = 200 if is_legacy_189 else 50

    return {
        "min_mb": min_mb,
        "max_mb": max_mb,
        "xms_flag": xms_arg,
        "xmx_flag": xmx_arg,
        "new_size_pct": new_size_pct,
        "max_new_size_pct": max_new_size_pct,
        "reserve_pct": reserve_pct,
        "region_size": region_size,
        "pause_millis": pause_millis,
    }
```

---

## 3. Feature 10: Stable JRE Runtime Locator

### 3.1 Problem Analysis & Existing Code Inspection

In `development/launcher_core/java_service.py`:
```python
def discover_java_installations(self) -> Dict[str, Any]:
    found: List[Dict[str, Any]] = []
    seen_paths = set()

    def _add_candidate(path: str, source: str) -> None:
        norm = os.path.normpath(path)
        if norm.lower() in seen_paths or not os.path.exists(norm):
            return
        seen_paths.add(norm.lower())  # <--- CRITICAL BUG: norm is added before javaw resolution!

        # Detect javaw vs java
        javaw_candidate = os.path.join(os.path.dirname(norm), "javaw.exe")
        target_exe = javaw_candidate if os.path.isfile(javaw_candidate) else norm
        ...
```

#### Key Flaws Identified:
1. **Deduplication Defect**:
   - `_add_candidate` registers `path` into `seen_paths` *before* mapping `java.exe` to `javaw.exe`. When `which("java")` returns `C:\...\java.exe` and `which("javaw")` returns `C:\...\javaw.exe`, both resolve to `javaw.exe` but both pass the `seen_paths` check, resulting in duplicate entries.
2. **Zero Architecture / Bitness Validation**:
   - `java_service.py` does not inspect whether a runtime is 64-bit (`x64`, `ARM64`) or 32-bit (`x86`).
   - If an old 32-bit JRE 8 (e.g. `C:\Program Files (x86)\Java\jre1.8.0_251\bin\javaw.exe`) is present, it is presented as a valid candidate for all profiles without flagging that:
     - It cannot allocate $> 1.5\text{GB}$ RAM.
     - It will immediately crash with `UnsatisfiedLinkError` when attempting to load 64-bit LWJGL natives (`lwjgl64.dll`, `OpenAL64.dll`).
3. **Naive Version & Vendor Parsing**:
   - `is_j21 = "21" in raw_ver or "21" in parent_name`
   - `is_j8 = "1.8" in raw_ver or "8." in raw_ver...`
   - Fails to parse Java 22, 23, 24, 25, 17, 11, or complex vendor release tags (`Temurin-21.0.6+7-LTS`, `25-ea`).
   - Lacks structured extraction of `major_version: int`, `vendor: str`, `is_lts: bool`, and `is_64bit: bool`.
4. **Registry Scope Limitation**:
   - Scans only `HKEY_LOCAL_MACHINE`.
   - Misses `HKEY_CURRENT_USER`, which modern per-user installers (Adoptium, Microsoft OpenJDK, Scoop) use.
   - Does not request `winreg.KEY_WOW64_64KEY` to ensure 64-bit registry keys are accessible.
5. **Divergent Implementations across Codebase**:
   - `launcher_core/java_service.py` has one locator.
   - `launcher_core/native_runner.py` has a separate `detect_java` with hardcoded paths.
   - `shared_core/runtime.py` has `detect_system_java`.
   - `sir_core/launcher/java_locator.py` has another `locate_java_runtimes`.
   - These 4 locators diverge in behavior, priority, and parsing accuracy.

---

### 3.2 Stable JRE Runtime Locator Implementation Strategy

#### Architectural Components:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        JavaService / RuntimeLocator                    │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Multi-Source Discovery:                                            │
│    ├── Windows Registry (HKLM & HKCU, WOW64_64KEY, 15+ vendor keys)    │
│    ├── Filesystem Standard Roots (Program Files, LocalAppData, .jdks) │
│    ├── Managed Runtime Pools (SIR runtime/, Prism, Lunar, .minecraft)  │
│    └── Environment & Path (JAVA_HOME, JDK_HOME, PATH, where.exe)       │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Direct PE Header Inspection (Instant 0ms Architecture Detection):   │
│    ├── Read PE Magic (0x8664 -> x64, 0xAA64 -> ARM64, 0x014c -> x86)   │
│    └── Instant bitness validation (is_64bit: bool)                     │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Deep Semver & Vendor Parser:                                        │
│    ├── Regex extraction for Java 8 through 25+                         │
│    ├── Major version integer resolution (8, 11, 17, 21, 22..25)        │
│    ├── Vendor classification (Adoptium Temurin, Microsoft, Zulu, etc.) │
│    └── LTS Classification (8, 11, 17, 21)                              │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Target Resolver & Auto-Downloader:                                  │
│    ├── Modern 26.2 -> Eclipse Temurin 21 LTS x64 (Priority 1)          │
│    ├── Legacy 1.8.9 -> JRE 8 x64 (Priority 1)                          │
│    └── Automatic Adoptium API v3 downloader for missing runtimes       │
└────────────────────────────────────────────────────────────────────────┘
```

#### 1. Instant PE Binary Architecture Detection (Zero Subprocess Overhead):
```python
def get_pe_binary_arch(exe_path: str) -> Dict[str, Any]:
    """Reads Windows PE header to determine binary machine architecture without spawning subprocess."""
    try:
        with open(exe_path, "rb") as f:
            if f.read(2) != b"MZ":
                return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
            f.seek(0x3C)
            pe_offset_bytes = f.read(4)
            if len(pe_offset_bytes) < 4:
                return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
            pe_offset = struct.unpack("<I", pe_offset_bytes)[0]
            f.seek(pe_offset)
            if f.read(4) != b"PE\0\0":
                return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
            machine = struct.unpack("<H", f.read(2))[0]
            if machine == 0x8664:
                return {"is_valid": True, "arch": "x64", "is_64bit": True}
            elif machine == 0xAA64:
                return {"is_valid": True, "arch": "ARM64", "is_64bit": True}
            elif machine == 0x014c:
                return {"is_valid": True, "arch": "x86 (32-bit)", "is_64bit": False}
            return {"is_valid": True, "arch": f"Other ({hex(machine)})", "is_64bit": False}
    except Exception:
        return {"is_valid": False, "arch": "Unknown", "is_64bit": False}
```

#### 2. Robust Version & Vendor Parser:
```python
def parse_java_runtime_info(java_exe: str) -> Dict[str, Any]:
    """Executes java -version and extracts structured semver, vendor, LTS, and architecture metadata."""
    norm_exe = os.path.normpath(java_exe)
    pe_info = get_pe_binary_arch(norm_exe)
    
    try:
        res = subprocess.run(
            [norm_exe, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2.5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0,
        )
        out = res.stdout or ""
    except Exception:
        out = ""

    # Semver extraction
    raw_ver = "Unknown"
    major = 0
    m_ver = re.search(r'(?:version|openjdk version)\s+"?([0-9._]+(?:-[a-zA-Z0-9.+]+)?)"?', out, re.IGNORECASE)
    if m_ver:
        raw_ver = m_ver.group(1)
        if raw_ver.startswith("1."):
            parts = raw_ver.split(".")
            if len(parts) > 1:
                try: major = int(parts[1])
                except ValueError: major = 8
        else:
            m_maj = re.match(r"^(\d+)", raw_ver)
            if m_maj:
                major = int(m_maj.group(1))

    # Architecture refinement
    is_64bit = pe_info.get("is_64bit", True)
    arch = pe_info.get("arch", "x64")
    if "64-Bit" in out or "x86_64" in out or "amd64" in out:
        is_64bit = True
        arch = "x64"
    elif "32-Bit" in out:
        is_64bit = False
        arch = "x86 (32-bit)"

    # Vendor Classification
    out_lower = out.lower()
    path_lower = norm_exe.lower()
    if "temurin" in out_lower or "adoptium" in out_lower or "adoptium" in path_lower:
        vendor = "Eclipse Adoptium (Temurin)"
    elif "microsoft" in out_lower or "microsoft" in path_lower:
        vendor = "Microsoft OpenJDK"
    elif "zulu" in out_lower or "azul" in out_lower or "zulu" in path_lower:
        vendor = "Azul Zulu"
    elif "corretto" in out_lower or "amazon" in out_lower or "corretto" in path_lower:
        vendor = "Amazon Corretto"
    elif "bellsoft" in out_lower or "liberica" in out_lower or "bellsoft" in path_lower:
        vendor = "BellSoft Liberica"
    elif "hotspot" in out_lower or "oracle" in out_lower or "java(tm)" in out_lower:
        vendor = "Oracle Java"
    elif "openjdk" in out_lower:
        vendor = "OpenJDK"
    else:
        vendor = "Custom JDK"

    is_lts = major in (8, 11, 17, 21)
    is_temurin_21 = (major == 21 and "Adoptium" in vendor and is_64bit)
    is_modern_ready = (major >= 21 and is_64bit)
    is_legacy_ready = (major == 8 and is_64bit)

    return {
        "name": f"{vendor} Java {major or raw_ver} ({arch})",
        "path": norm_exe,
        "raw_version": raw_ver,
        "major_version": major,
        "vendor": vendor,
        "arch": arch,
        "is_64bit": is_64bit,
        "is_lts": is_lts,
        "is_temurin_21": is_temurin_21,
        "is_java21": (major == 21),
        "is_java8": (major == 8),
        "is_modern_ready": is_modern_ready,
        "is_legacy_ready": is_legacy_ready,
        "recommended": is_temurin_21 or is_modern_ready,
    }
```

---

## 4. Integration Matrix

| Subsystem | File | Required Alignment |
|---|---|---|
| **Native Runner** | `development/launcher_core/native_runner.py` | Replace clamped `build_jvm_args` with `calculate_ram_parameters`; delegate `detect_java` and `ensure_java_runtime` directly to unified `JavaService`. |
| **Java Service** | `development/launcher_core/java_service.py` | Add full registry + FS scanning, PE header arch detection, semver parsing, Temurin 21 priority ranking, and `get_best_runtime(mc_version)`. |
| **Instance Service** | `development/launcher_core/instance_service.py` | In `launch_instance`, honor `instance.cfg` memory overrides if present before falling back to global settings; pass strict RAM parameters to `native_runner`. |
| **Bridge API** | `development/launcher_core/bridge.py` | Expose `discover_java_installations` returning enriched metadata (`arch`, `vendor`, `major_version`, `is_64bit`). |
| **Shared Core Runtime** | `development/shared_core/runtime.py` | Harmonize `detect_system_java` to use the unified architecture-aware discovery logic. |

---

## 5. Comprehensive Test Infrastructure Plan

### 5.1 Test Suite Structure (`tests/test_native_runner.py` & `tests/test_java_service.py`)

#### Tier 1: Feature Coverage (RAM & JRE Locator)
1. `test_strict_ram_allocation_exact_bounds_4g`: Validates exact `-Xmx4G` and `-Xms2G` without forced alterations.
2. `test_strict_ram_allocation_exact_bounds_8g`: Validates exact `-Xmx8G` and `-Xms4G`.
3. `test_strict_ram_allocation_exact_bounds_16g`: Validates exact `-Xmx16G` and `-Xms8G`.
4. `test_strict_ram_mb_granularity`: Validates 6144MB, 3072MB granular memory inputs.
5. `test_power_mode_thread_allocation`: Validates `turbo` vs `smooth` GC worker thread calculations.
6. `test_discover_java_installations_structure`: Validates structured discovery payload.
7. `test_no_duplicate_canonical_paths`: Validates strict executable path deduplication.
8. `test_version_parsing_java_8_through_25`: Validates parser across Java 8, 11, 17, 21, 22, 23, 24, 25.
9. `test_eclipse_temurin_21_selection_for_modern`: Validates Eclipse Temurin 21 LTS selection for Modern 26.2.
10. `test_jre_8_selection_for_legacy_189`: Validates JRE 8 x64 selection for Legacy 1.8.9.

#### Tier 2: Boundary & Corner Cases
1. `test_low_ram_boundary_1g_no_forced_4g_clamp`: Validates 1GB allocation produces `-Xmx1G` (or `-Xmx1024M`) and `-Xms512M`, strictly preventing `-Xms > -Xmx` and avoiding forced 4GB inflation.
2. `test_odd_and_fractional_ram_values`: Tests 3GB (3072MB), 5GB (5120MB), 7GB (7168MB) allocations and verifies proper G1GC region sizing.
3. `test_custom_min_max_ram_pair`: Tests explicit `min_ram` / `max_ram` pairs.
4. `test_g1gc_region_size_scaling`: Tests region size scaling across heap tiers (1M for $<2\text{GB}$, 2M for $2-4\text{GB}$, 4M/8M for $4-8\text{GB}$, 16M for $8-16\text{GB}$, 32M for $>16\text{GB}$).
5. `test_nursery_percentage_scaling_by_heap_tier`: Tests `G1NewSizePercent` and `G1MaxNewSizePercent` dynamic adjustment.
6. `test_pe_architecture_detection_x64_vs_32bit`: Tests binary PE header parser on 64-bit and 32-bit executables.
7. `test_32bit_jre_rejection_for_high_ram_and_modern`: Validates 32-bit JREs are flagged `is_64bit=False` and excluded from modern profile recommendations.
8. `test_missing_and_corrupted_java_binary_validation`: Validates handling of non-existent binaries and non-executable files.
9. `test_registry_and_path_discovery_fallbacks`: Validates graceful error handling during registry query failures.
10. `test_auto_download_runtime_url_construction`: Validates Adoptium API endpoints for Java 21 LTS and Java 8.

---

## 6. Implementation Blueprint for M2 Implementer

1. **Step 1 (`java_service.py`)**:
   - Implement `get_pe_binary_arch(exe_path)` for instant zero-overhead PE header inspection.
   - Implement `parse_java_runtime_info(exe_path)` supporting Java 8–25 semver and vendor tagging.
   - Expand registry scanning to HKCU and add missing vendor subkeys.
   - Expand filesystem discovery paths.
   - Fix canonical path deduplication by resolving `javaw.exe` *before* inserting into `seen_paths`.
   - Add `get_best_runtime_for_version(mc_version)` and `find_eclipse_temurin_21()`.
2. **Step 2 (`native_runner.py`)**:
   - Refactor `build_jvm_args` to eliminate `max(4, ram_gb)` and `max(2, ram_gb // 2)` clamps.
   - Implement dynamic G1GC nursery and region size calculation based on allocated heap.
   - Wire `detect_java` to invoke `JavaService.get_best_runtime_for_version`.
3. **Step 3 (`instance_service.py`)**:
   - Ensure `launch_instance` reads instance-specific `instance.cfg` memory overrides before global defaults.
4. **Step 4 (`tests/test_native_runner.py`)**:
   - Add Tier 1 and Tier 2 unit tests covering all RAM boundaries and Java locator permutations.
