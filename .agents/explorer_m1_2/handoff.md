# Technical Investigation & Architecture Blueprint: Universal Atomic File Persistence & InstanceService Launch Pipeline Hardening

**Author**: Explorer 2 (Milestone 1 — Core Engine & Telemetry Specialist)  
**Target Workspace**: `D:\Projects\SIR ModPack`  
**Date**: 2026-08-29  
**Status**: Investigation Complete & Technical Blueprint Validated  

---

## 1. Observation

A comprehensive inspection of the file persistence mechanisms and launch pipeline across `development/shared_core`, `development/launcher_core`, and `development/server_core` revealed the following exact observations:

### 1.1 Universal Atomic File Persistence Infrastructure
1. **`development/shared_core/runtime.py` (lines 304–343)**:
   - `atomic_write_json(path: str, value: Any) -> None` (lines 304–323) implements atomic replacement using `tempfile.mkstemp(prefix=".sir-", suffix=".tmp", dir=os.path.dirname(target))`, serializing JSON with `indent=2, ensure_ascii=False`, performing explicit `handle.flush()` and kernel-level `os.fsync(handle.fileno())`, followed by `os.replace(temp_path, target)` with cleanup in `finally`.
   - `atomic_write_text(path: str, content: str, encoding: str = "utf-8") -> None` (lines 325–343) implements atomic text replacement using `tempfile.mkstemp(prefix=".sir-txt-", suffix=".tmp", dir=os.path.dirname(target))`, writing content, flushing, calling `os.fsync(handle.fileno())`, and executing `os.replace(temp_path, target)`.
   - Creating temporary files in `dir=os.path.dirname(target)` ensures same-volume placement, satisfying the requirement of `os.replace` on Windows.
   - However, on Windows, transient file locks caused by antivirus scans or Windows Search indexer can cause `os.replace` to throw a transient `PermissionError` if not wrapped in a short backoff retry loop.

### 1.2 Identification of All Raw Non-Atomic Writes (`open(..., 'w')`) Across the Ecosystem

Direct inspection identified the exact locations where raw `open(..., "w")` or un-buffered direct writes are performed and must be migrated to atomic persistence:

1. **`development/launcher_core/instance_service.py`**:
   - **Line 644 (`_download_payload_if_missing`)**:
     ```python
     with open(local_zip, "wb") as out_f:
         shutil.copyfileobj(resp, out_f)
     ```
     Writes directly to the target zip file without temporary staging or validation, risking a corrupted, incomplete archive upon network abort.
   - **Line 669 (`heal_instance_if_needed`)**:
     ```python
     with open(cfg_file, "w", encoding="utf-8") as f:
         f.write(f"[General]\nConfigVersion=1.2\nname={inst.get('name', 'SIR Profile')}\niconKey=default\nInstanceType=OneSix\n")
     ```
     Non-atomic raw write of `instance.cfg`.
   - **Lines 719–723 (`heal_instance_if_needed`)**:
     ```python
     with open(options_path, "w", encoding="utf-8") as f:
         f.write("version:3465\ngamma:1.0\nmaxFps:260\nfov:0.0\nrenderDistance:12\nsimulationDistance:8\nguiScale:0\ngraphicsMode:0\nsmoothLighting:true\nentityDistanceScaling:1.0\nentityShadows:true\nresourcePacks:[\"vanilla\",\"file/SIR_Ultimate_Pack.zip\"]\nincompatibleResourcePacks:[]\nsoundCategory_master:1.0\nsoundCategory_music:0.0\nbiomeBlendRadius:7\n")
     ```
     and line 722:
     ```python
     with open(options_path, "w", encoding="utf-8") as f:
         f.write("renderDistance:12\ngamma:1.0\nfullscreen:false\nmaxFps:260\nresourcePacks:[\"SIR_Legacy_32x.zip\"]\n")
     ```
     Non-atomic raw writes of `options.txt`.
   - **Line 728 (`heal_instance_if_needed`)**:
     ```python
     with open(iris_path, "w", encoding="utf-8") as f:
         f.write("enableShaders=true\nshaderPack=SIR_Balanced_Shader.zip\n")
     ```
     Non-atomic raw write of `iris.properties`.
   - **Lines 16–27 (fallback functions)**:
     The fallback implementations of `atomic_write_json` and `atomic_write_text` in `instance_service.py` lack `os.fsync` and use a naive `path + ".tmp"` instead of `tempfile.mkstemp`.

2. **`development/launcher_core/bridge.py`**:
   - **Lines 227–228 (`install_online_mod`)**:
     ```python
     with open(save_path, "wb") as f_out:
         f_out.write(dl_resp.read())
     ```
     Non-atomic direct stream write on the calling bridge thread.
   - **Lines 513–518 (`accept_legal_terms`)**:
     ```python
     with open(agree_file, "w", encoding="utf-8") as f:
         json.dump({
             "version": version,
             "timestamp": now_ts,
             "agreed": True
         }, f, indent=2)
     ```
     Non-atomic `open(..., "w")` with `json.dump` for `legal_agreement.json`.

3. **`development/launcher_core/controls_service.py`**:
   - **Lines 88–90 (`apply_control_profile`)**:
     ```python
     with open(opt_path, "w", encoding="utf-8") as f:
         f.writelines(new_lines)
     ```
     Direct non-atomic write of `options.txt`.

4. **`development/server_core/server_bridge.py`**:
   - **Lines 145–146 (`init_server_instance`)**:
     ```python
     with open(eula_path, "w", encoding="utf-8") as f:
         f.write("# Generated by SIR Server Orchestrator Pro\neula=true\n")
     ```
   - **Lines 163–164 (`init_server_instance`)**:
     ```python
     with open(props_path, "w", encoding="utf-8") as f:
         f.write(default_props)
     ```
   - **Lines 496–497 (`save_server_properties`)**:
     ```python
     with open(props_path, "w", encoding="utf-8") as f:
         f.writelines(lines)
     ```
     All three are raw non-atomic file writes. Furthermore, `server_bridge.py` only imports `atomic_write_json` on line 13 and lacks `atomic_write_text`.

5. **`development/launcher_core/export_service.py`**:
   - **Lines 53–54 (`import_custom_profile_json`)**:
     ```python
     with open(os.path.join(custom_dir, "profile.json"), "w", encoding="utf-8") as f:
         json.dump(data, f, indent=2)
     ```
     Non-atomic JSON file write.

6. **`development/launcher_core/packs_service.py`**:
   - **Lines 137–138 (`toggle_pack`)**:
     ```python
     with open(opt_path, "w", encoding="utf-8") as f:
         f.writelines(new_lines)
     ```
     Non-atomic `options.txt` write.

7. **`development/launcher_core/shaders_service.py`**:
   - **Lines 77–84 (`apply_shader_preset`)**:
     ```python
     with open(target_cfg, "w", encoding="utf-8") as f:
         if filename != "OFF":
             f.write(f"shaderPack={filename}\n")
             ...
     ```
     Non-atomic `optionsshaders.txt` write.
   - **Lines 117–123 (`save_fine_shader_options`)**:
     ```python
     with open(bliss_cfg, "w", encoding="utf-8") as f:
         f.write(f"MOTION_BLUR={'1' if options_dict.get('motion_blur') else '0'}\n")
         ...
     ```
     Non-atomic `bliss.txt` write.

8. **`development/launcher_core/skin_studio_service.py`**:
   - **Lines 159–160 (`apply_skin_and_cape`)**:
     ```python
     with open(skin_file, "wb") as f:
         f.write(resp.read())
     ```
   - **Lines 178–186 (`apply_skin_and_cape`)**:
     ```python
     with open(skin_cfg, "w", encoding="utf-8") as f:
         json.dump({ ... }, f, indent=2)
     ```
     Non-atomic `customskinloader.json` configuration write.

9. **`development/launcher_core/store_service.py`**:
   - **Lines 184–185 (`install_project`)**:
     ```python
     with open(save_path, "wb") as out_f:
         out_f.write(dl_resp.read())
     ```
     Non-atomic binary stream write.

---

### 1.3 `InstanceService` Launch Pipeline & Missing Method Analysis
Inspection of `development/launcher_core/instance_service.py` (lines 597–895) revealed:
1. **Method Renaming & Missing Signature**:
   - At line 601, the method is defined as:
     ```python
     def _launch_result(self, *, success, profile_id, instance_id="", mode="offline", pid=None,
                        message="", error_code="", log_path="", error=""):
     ```
   - Any external callers, older test suites, or dynamic dispatchers calling `_build_launch_response` will trigger `AttributeError: 'InstanceService' object has no attribute '_build_launch_response'`.
2. **`UnboundLocalError` Risk**:
   - In `launch_instance` at lines 881–882:
     ```python
     except Exception as ex:
         err_msg = str(ex) if native_res.get("success") else (native_res.get("error") or f"Could not launch Minecraft instance: {ex}")
     ```
     If `self.native_runner` is `None` (or raises an exception before assigning `native_res`), `native_res` is unbound when entering this block, causing Python to raise `UnboundLocalError: local variable 'native_res' referenced before assignment`.
3. **Implicit `None` Return on Fallback Failure**:
   - Lines 840–850 search for `exe` in `launcher_candidates`.
   - If `exe` is `None` (Prism not bundled/installed) and `native_runner` failed:
     ```python
     exe = next((e for e in launcher_candidates if os.path.isfile(e)), None)
     if exe:
         ...
     # No else branch or terminal return statement!
     ```
     The function terminates without returning, implicitly returning `None`. The UI bridge receives `null` and hangs indefinitely with no error modal displayed to the user.

---

## 2. Logic Chain

```
[Observation 1.1 & 1.2: Raw open(..., 'w') across 9 core files]
   ↓
[Logic Step 1]: In desktop environments, sudden process termination, Windows power-state transitions, or abrupt user closure during file writes truncates files to 0 bytes or leaves invalid partial JSON.
   ↓
[Logic Step 2]: Atomic writes with same-directory temp files, os.fsync, and os.replace ensure that existing valid configurations are never replaced until the new payload is completely flushed to physical disk.
   ↓
[Conclusion 1]: All raw open(..., "w") calls in instance_service.py, bridge.py, server_bridge.py, controls_service.py, packs_service.py, shaders_service.py, export_service.py, and skin_studio_service.py must be replaced with atomic_write_json and atomic_write_text.

[Observation 1.3: InstanceService _launch_result vs _build_launch_response & UnboundLocalError]
   ↓
[Logic Step 3]: When native_runner is unavailable or fails, and Prism is absent, launch_instance returns None instead of a structured error dictionary, breaking the pywebview JSON-RPC contract.
   ↓
[Logic Step 4]: Referencing native_res inside exception handlers without prior initialization causes UnboundLocalError during error handling.
   ↓
[Conclusion 2]: InstanceService must: (a) provide _build_launch_response as a backward-compatible alias to _launch_result, (b) initialize native_res = None, (c) safely guard error string extraction, and (d) provide an explicit terminal return with error_code="LAUNCH_ENGINE_UNAVAILABLE".
```

---

## 3. Caveats

1. **Windows Volume Boundaries**:
   - `os.replace` fails across different filesystem drive letters (e.g. from `C:\Users\...\AppData\Local\Temp` to `D:\Projects\...`). All atomic writes must strictly use `dir=os.path.dirname(target)` as implemented in `shared_core.runtime`.
2. **Log File Appending**:
   - Launch stdout/stderr append operations (`open(log_path, "a")`) and live process log handlers do NOT use atomic replace because they stream ongoing append-only telemetry. These are kept as standard file handles with explicit flushing.
3. **No Direct Source Editing During Investigation**:
   - In accordance with explorer rules, all changes are documented in blueprint specifications below for execution by the implementer.

---

## 4. Conclusion & Actionable Blueprint

### 4.1 Concrete Diff Blueprint: `shared_core/runtime.py` Hardening

Enhance `atomic_write_json` and `atomic_write_text` to include a Windows-resilient retry mechanism for transient file locks:

```python
# In development/shared_core/runtime.py:
def atomic_write_json(path: str, value: Any) -> None:
    """Write JSON through a same-directory temporary file and atomic replace."""
    target = os.path.abspath(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".sir-", suffix=".tmp", dir=os.path.dirname(target))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        
        # Retry loop for Windows transient file locks
        for attempt in range(5):
            try:
                os.replace(temp_path, target)
                break
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

def atomic_write_text(path: str, content: str, encoding: str = "utf-8") -> None:
    """Write text through a same-directory temporary file and atomic replace."""
    target = os.path.abspath(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".sir-txt-", suffix=".tmp", dir=os.path.dirname(target))
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        
        for attempt in range(5):
            try:
                os.replace(temp_path, target)
                break
            except (PermissionError, OSError):
                if attempt == 4:
                    raise
                time.sleep(0.05)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
```

---

### 4.2 Concrete Diff Blueprint: `launcher_core/instance_service.py`

```python
# In development/launcher_core/instance_service.py:

# 1. Provide backward-compatible alias on InstanceService
def _build_launch_response(self, *args, **kwargs):
    """Backward-compatible alias for _launch_result."""
    return self._launch_result(*args, **kwargs)

# 2. Update heal_instance_if_needed with atomic persistence:
def heal_instance_if_needed(self, inst, inst_dir, mc_game_dir, mc_version):
    try:
        os.makedirs(inst_dir, exist_ok=True)
        os.makedirs(mc_game_dir, exist_ok=True)
        
        # 1. Instance Definition (.cfg / mmc-pack.json)
        cfg_file = os.path.join(inst_dir, "instance.cfg")
        if not os.path.isfile(cfg_file) and not os.path.isfile(os.path.join(inst_dir, "mmc-pack.json")):
            atomic_write_text(
                cfg_file,
                f"[General]\nConfigVersion=1.2\nname={inst.get('name', 'SIR Profile')}\niconKey=default\nInstanceType=OneSix\n"
            )

        # 2. Per-Profile Mods Suite Healing ...
        # (Mods, Shaders, Packs downloads use resilient stream staging)

        # 5. High-Performance Configuration Presets Healing
        cfg_dir = os.path.join(mc_game_dir, "config")
        os.makedirs(cfg_dir, exist_ok=True)
        options_path = os.path.join(mc_game_dir, "options.txt")
        
        if not os.path.isfile(options_path):
            if is_modern:
                atomic_write_text(
                    options_path,
                    "version:3465\ngamma:1.0\nmaxFps:260\nfov:0.0\nrenderDistance:12\nsimulationDistance:8\nguiScale:0\ngraphicsMode:0\nsmoothLighting:true\nentityDistanceScaling:1.0\nentityShadows:true\nresourcePacks:[\"vanilla\",\"file/SIR_Ultimate_Pack.zip\"]\nincompatibleResourcePacks:[]\nsoundCategory_master:1.0\nsoundCategory_music:0.0\nbiomeBlendRadius:7\n"
                )
            else:
                atomic_write_text(
                    options_path,
                    "renderDistance:12\ngamma:1.0\nfullscreen:false\nmaxFps:260\nresourcePacks:[\"SIR_Legacy_32x.zip\"]\n"
                )

        if is_modern:
            iris_path = os.path.join(cfg_dir, "iris.properties")
            if not os.path.isfile(iris_path):
                atomic_write_text(
                    iris_path,
                    "enableShaders=true\nshaderPack=SIR_Balanced_Shader.zip\n"
                )

        return True
    except Exception:
        return False

# 3. Robust launch_instance method:
def launch_instance(self, inst_id, account=None, on_log_callback=None, extra_args=None):
    ...
    native_res = None
    # 1. Primary: Direct Native JVM Launch Engine
    if self.native_runner:
        native_res = self.native_runner.launch(
            instance_dir=mc_game_dir,
            mc_version=mc_version,
            loader=loader_type,
            account=account_dict,
            ram_gb=ram_gb,
            power_mode=power_mode
        )
        if native_res.get("success"):
            pid = native_res.get("pid")
            log_path = native_res.get("log_path", "")
            self.running_processes[inst_id] = pid
            return self._launch_result(
                success=True,
                profile_id=inst_id,
                instance_id=instance_id,
                mode=account_type,
                pid=pid,
                message=f"✓ Launched {inst['name']} (Native Java Direct Engine)",
                log_path=log_path,
            )

    # 2. Secondary Fallback: Managed Runner (if Prism present)
    launcher_candidates = [
        os.path.join(self.prism_root, "prismlauncher.exe"),
        os.path.join(self.root_dir, "prism", "prismlauncher.exe"),
        os.path.join(self.root_dir, "SIR Launcher", "bin", "prismlauncher.exe"),
        os.path.join(self.root_dir, "SIR Launcher", "prismlauncher.exe"),
        os.path.join(self.root_dir, "bin", "prismlauncher.exe")
    ]
    exe = next((e for e in launcher_candidates if os.path.isfile(e)), None)
    if exe:
        seed_prism_config(self.prism_root, self.instances_dir)
        cmd = [exe, "--dir", os.path.dirname(self.instances_dir), "--launch", instance_id]
        if account_name:
            if account_type == "microsoft":
                cmd.extend(["--profile", account_name])
            else:
                cmd.extend(["--offline", account_name])
        if extra_args:
            cmd.extend([str(item) for item in extra_args])

        log_path = os.path.join(self.launch_log_dir, f"{inst_id}-{int(time.time())}.log")
        try:
            with open(log_path, "a", encoding="utf-8") as log_handle:
                log_handle.write("$ " + " ".join(cmd) + "\n")
                log_handle.flush()
                proc = subprocess.Popen(
                    cmd,
                    cwd=os.path.dirname(exe),
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
                )
            self.running_processes[inst_id] = proc
            return self._launch_result(
                success=True,
                profile_id=inst_id,
                instance_id=instance_id,
                mode=account_type,
                pid=proc.pid,
                message=f"Launching {inst['name']}…",
                log_path=log_path,
            )
        except Exception as ex:
            err_msg = str(ex) if (native_res and native_res.get("success")) else ((native_res and native_res.get("error")) or f"Could not launch Minecraft instance: {ex}")
            return self._launch_result(
                success=False,
                profile_id=inst_id,
                instance_id=instance_id,
                mode=account_type,
                error_code="LAUNCH_FAILED",
                error=err_msg,
            )

    # 3. Terminal fallback if neither engine succeeded
    err_msg = (native_res and native_res.get("error")) or "Launch failed: Native JVM runner could not start instance and Prism fallback executable was not found."
    return self._launch_result(
        success=False,
        profile_id=inst_id,
        instance_id=instance_id,
        mode=account_type,
        error_code="LAUNCH_ENGINE_UNAVAILABLE",
        error=err_msg,
    )
```

---

### 4.3 Concrete Diff Blueprint: `launcher_core/bridge.py`
In `development/launcher_core/bridge.py`:
- In `accept_legal_terms` (line 513): Replace raw file write with `atomic_write_json(agree_file, {"version": version, "timestamp": now_ts, "agreed": True})`.

---

### 4.4 Concrete Diff Blueprint: `launcher_core/controls_service.py`
In `development/launcher_core/controls_service.py`:
- Import `atomic_write_text` from `shared_core.runtime`.
- In `apply_control_profile` (line 88): Replace raw `open(..., "w")` with `atomic_write_text(opt_path, "".join(new_lines))`.

---

### 4.5 Concrete Diff Blueprint: `server_core/server_bridge.py`
In `development/server_core/server_bridge.py`:
- Import `atomic_write_json, atomic_write_text` from `shared_core.runtime`.
- In `init_server_instance` (line 145): `atomic_write_text(eula_path, "# Generated by SIR Server Orchestrator Pro\neula=true\n")`.
- In `init_server_instance` (line 163): `atomic_write_text(props_path, default_props)`.
- In `save_server_properties` (line 496): `atomic_write_text(props_path, "".join(lines))`.

---

## 5. Verification Method

To independently verify these architectural findings and fixes:

1. **Verify Atomic JSON & Text Persistence Utilities**:
   ```pwsh
   python -c "
   import sys; sys.path.insert(0, 'D:/Projects/SIR ModPack/development')
   from shared_core.runtime import atomic_write_json, atomic_write_text
   atomic_write_json('test_atomic.json', {'test': 123})
   atomic_write_text('test_atomic.txt', 'hello world\n')
   import os; assert os.path.exists('test_atomic.json') and os.path.exists('test_atomic.txt')
   os.remove('test_atomic.json'); os.remove('test_atomic.txt')
   print('Atomic Persistence OK')
   "
   ```

2. **Verify InstanceService Launch Response Contract**:
   ```pwsh
   python -c "
   import sys; sys.path.insert(0, 'D:/Projects/SIR ModPack/development')
   from launcher_core.instance_service import InstanceService
   service = InstanceService('D:/Projects/SIR ModPack', 'D:/Projects/SIR ModPack/instances')
   res = service.launch_instance('non_existent_profile')
   assert isinstance(res, dict) and res.get('success') is False
   assert res.get('errorCode') == 'PROFILE_NOT_FOUND'
   print('InstanceService Launch Contract OK')
   "
   ```

3. **Verify ControlsService & ServerBridge Persistence**:
   ```pwsh
   python -c "
   import sys; sys.path.insert(0, 'D:/Projects/SIR ModPack/development')
   from launcher_core.controls_service import ControlsService
   from server_core.server_bridge import ServerBridgeAPI
   cs = ControlsService('D:/Projects/SIR ModPack')
   sb = ServerBridgeAPI('D:/Projects/SIR ModPack')
   print('Services Instantiation OK')
   "
   ```

### Invalidation Conditions
- Any file persistence operation resulting in a 0-byte or corrupted `.json`, `.cfg`, or `options.txt` when a process is killed mid-write.
- Any invocation of `launch_instance` returning `None` instead of a dictionary adhering to the launch contract.
- Any `AttributeError` or `UnboundLocalError` during failed launch attempts.
