# Challenger 2 Report: Milestone 3 (Accounts, Cloud Sync & Bridge APIs Adversarial Verification)

**Agent**: `challenger_m3_2` (EMPIRICAL CHALLENGER)  
**Milestone**: M3 (Desktop Client UI, Video Presets & Accounts — Scope 2: Accounts, Sync & Bridge APIs)  
**Parent Conversation ID**: `49dbe1b0-c85d-471e-87d2-e4aeb12f093d`  
**Verdict**: ⚠️ **REQUEST_CHANGES**  
**Execution Test Result**: 12/15 tests passing, 3 failing with reproducible empirical defects.

---

## 1. Observation

Adversarial test suite `tests/test_challenger_m3_accounts_sync_bridge.py` was constructed and executed with `python -m unittest tests/test_challenger_m3_accounts_sync_bridge.py`.

### Test Execution Output:
```
.....C:\msys64\ucrt64\lib\python3.14\tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 500: 'Internal Server Error'>
  _warnings.warn(self.warn_message, ResourceWarning)
....----------------------------------------
Exception occurred during processing of request from ('127.0.0.1', 37389)
Traceback (most recent call last):
  File "C:\msys64\ucrt64\lib\python3.14\socketserver.py", line 318, in _handle_request_noblock
    self.process_request(request, client_address)
  File "C:\msys64\ucrt64\lib\python3.14\socketserver.py", line 349, in process_request
    self.finish_request(request, client_address)
  File "C:\msys64\ucrt64\lib\python3.14\socketserver.py", line 362, in finish_request
    self.RequestHandlerClass(request, client_address, self)
  File "C:\msys64\ucrt64\lib\python3.14\socketserver.py", line 766, in __init__
    self.handle()
  File "C:\msys64\ucrt64\lib\python3.14\http\server.py", line 500, in handle
    self.handle_one_request()
  File "C:\msys64\ucrt64\lib\python3.14\http\server.py", line 488, in handle_one_request
    method()
  File "D:\Projects\SIR ModPack\development\launcher_core\auth_service.py", line 656, in do_GET
    auth_svc_ref._ms_browser_state["status"] = "error"
TypeError: 'NoneType' object does not support item assignment
----------------------------------------
FF.F..
======================================================================
FAIL: test_microsoft_loopback_callback_http_success_and_error (tests.test_challenger_m3_accounts_sync_bridge.TestChallengerM3AccountsSyncBridge.test_microsoft_loopback_callback_http_success_and_error)
Verify the local HTTP callback handler processes ?code= and ?error= requests.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Projects\SIR ModPack\tests\test_challenger_m3_accounts_sync_bridge.py", line 333, in test_microsoft_loopback_callback_http_success_and_error
    self.assertIn("error", poll_err, "OAuth error state was not registered in poll response")
AssertionError: 'error' not found in {'success': False, 'pending': True} : OAuth error state was not registered in poll response

======================================================================
FAIL: test_microsoft_loopback_port_fallback_when_ports_occupied (tests.test_challenger_m3_accounts_sync_bridge.TestChallengerM3AccountsSyncBridge.test_microsoft_loopback_port_fallback_when_ports_occupied)
Verify port fallback mechanism when primary ports (52135, 52136) are occupied.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Projects\SIR ModPack\tests\test_challenger_m3_accounts_sync_bridge.py", line 298, in test_microsoft_loopback_port_fallback_when_ports_occupied
    self.assertFalse(port_hijacked, f"Port {bound_port} was hijacked despite active listener on same port")
AssertionError: True is not false : Port 52135 was hijacked despite active listener on same port

======================================================================
FAIL: test_resource_pack_injection_on_missing_options_txt (tests.test_challenger_m3_accounts_sync_bridge.TestChallengerM3AccountsSyncBridge.test_resource_pack_injection_on_missing_options_txt)
Verify behavior when toggle_pack is called on an instance lacking options.txt.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\Projects\SIR ModPack\tests\test_challenger_m3_accounts_sync_bridge.py", line 555, in test_resource_pack_injection_on_missing_options_txt
    self.assertTrue(file_created, "options.txt should be created if not present when setting active resource pack")
AssertionError: False is not true : options.txt should be created if not present when setting active resource pack

----------------------------------------------------------------------
Ran 15 tests in 8.135s

FAILED (failures=3)
```

---

## 2. Logic Chain & Defect Analysis

### Defect 1: Loopback Port Hijacking & Fallback Failure via `allow_reuse_address = True`
- **Observation**: `development/launcher_core/auth_service.py:596` sets `allow_reuse_address = True` on `CustomTCPServer`.
- **Reasoning**:
  1. On Windows, `SO_REUSEADDR` enables multiple processes/sockets to bind to the exact same port (e.g. `52135`).
  2. When another instance or process is already listening on `52135`, `socketserver.TCPServer(("127.0.0.1", 52135))` does not raise `OSError` (WSAEADDRINUSE), thus bypassing the intended fallback loop `[52135, 52136, 52137, 0]`.
  3. This causes port collision, race conditions, and possible interception of Microsoft OAuth callback tokens by zombie server threads or concurrent instances.
- **Proposed Fix**: Set `allow_reuse_address = False` on `CustomTCPServer` in `auth_service.py` so that a busy port properly raises an exception and cleanly falls back to `52136` -> `52137` -> ephemeral port `0`.

### Defect 2: Unhandled `TypeError: 'NoneType' object does not support item assignment` on OAuth Callback
- **Observation**: `development/launcher_core/auth_service.py:656`, `740`, `746`, `760`, `762`.
- **Reasoning**:
  1. `OAuthCallbackHandler.do_GET` directly performs `auth_svc_ref._ms_browser_state["status"] = "error"`.
  2. If the user session has timed out, been reset, or polled to completion (where `_ms_browser_state` is set to `None`), arriving HTTP requests trigger an unhandled `TypeError` in the server thread.
  3. In `_handle_browser_code`, `self._ms_browser_state["status"]` is mutated without null-checks.
- **Proposed Fix**: Guard all access to `_ms_browser_state` with `if auth_svc_ref._ms_browser_state is not None:` and `if self._ms_browser_state is not None:`.

### Defect 3: `PacksService.toggle_pack` Silently Skips Instances Missing `options.txt`
- **Observation**: `development/launcher_core/packs_service.py:118`.
- **Reasoning**:
  1. `toggle_pack()` iterates over `opt_paths` and only applies changes `if os.path.exists(opt_path):`.
  2. For fresh or clean custom instances that haven't launched yet (and therefore have no pre-existing `options.txt`), `toggle_pack()` executes 0 writes and creates no file.
  3. The method returns `{"success": True, "enabled": True}`, giving the UI and caller a false indication of success while leaving the instance unconfigured.
- **Proposed Fix**: When no candidate `options.txt` exists on disk, `toggle_pack` should create `instances/<instance_id>/minecraft/options.txt` with `version:3955\nresourcePacks:[...]\n` using `atomic_write_text`.

---

## 3. Verified Passing Components (Production-Grade)

The following components were empirically tested and confirmed fully functional and compliant:

1. **RFC 4122 UUIDv5 Determinism & Validation (`auth_service.py`)**:
   - Version 5 (SHA-1 namespace) and Variant 1 (RFC 4122) verified.
   - Deterministic 1:1 parity with standard library across boundary lengths (2–16 chars, underscores, digits, mixed-case).
   - Strict rejection of spaces, unicode, special characters, and SQL/XSS injection payloads.
   - Case-insensitive existing account switching verified.

2. **In-Game IAS Multi-Instance Sync (`auth_service.py`)**:
   - Simultaneous atomic propagation of `ias_accounts.json` verified across root directory, standard Fabric/Forge instances (`26.2`, `1.8.9`), custom profiles, MMC profiles (`mmc-pack.json`), and legacy config profiles (`instance.cfg`).
   - Zero credential leakage: verified that no OAuth tokens, passwords, or hashes exist in `ias_accounts.json`.
   - Account selection and deletion instantly reflect across all instance files.

3. **Microsoft OAuth PKCE Math (`auth_service.py`)**:
   - RFC 7636 S256 code challenge generation verified against manual SHA256 base64url calculation.

4. **Cloud Sync Service (`cloud_sync_service.py`)**:
   - 6-digit code format validation.
   - Graceful handling of Firebase `"null"` (expired/non-existent code).
   - Resilience against HTTP 500, URLError connection drops, and network timeouts.

5. **Bridge API Alias Methods (`bridge.py`)**:
   - `create_offline_account`: Fully functional.
   - `sync_cloud_code`: Fully functional.
   - `toggle_mod`: Fully functional across both signature conventions (`(inst, filename)` and `(filename, state, inst)`).
   - `open_mods_folder`: Fully functional.
   - `set_active_shader`: Fully functional.
   - `set_power_governor`: Fully functional.
   - `send_rcon_command`: Fully functional.

---

## 4. Caveats

- Tests for remote Microsoft OAuth endpoints (`login.microsoftonline.com`, `user.auth.xboxlive.com`) were tested via local loopback listener simulation and unit test mocks, as live Microsoft login requires interactive end-user browser interaction and active MSA credentials.
- No other uninvestigated areas.

---

## 5. Conclusion & Action Items

**Verdict**: **REQUEST_CHANGES**

### Action Items for Worker / Implementer:
1. **`development/launcher_core/auth_service.py`**:
   - Set `allow_reuse_address = False` on `CustomTCPServer` (line 596).
   - Add null checks for `_ms_browser_state` in `OAuthCallbackHandler.do_GET` (line 656) and `_handle_browser_code` (lines 740, 746, 760, 762).
2. **`development/launcher_core/packs_service.py`**:
   - In `toggle_pack()`, ensure that if no candidate `options.txt` exists on disk, `options.txt` is created in `instances/<instance_id>/minecraft/options.txt` with the active resource pack list.

---

## 6. Verification Method

To reproduce all findings independently, run:
```powershell
python -m unittest tests/test_challenger_m3_accounts_sync_bridge.py
```
Expected: 15 tests executed, 3 failing on the documented defects.
Once remediated, all 15 tests will pass 100%.
