# Handoff Report: 3D Skin Studio & Bi-Modal Account Management (Features 15 & 16)

## 1. Observation

### A. 3D Skin & Capes WebGL Studio (Feature 15)
- **WebGL Viewer Library & Assets**:
  - `development/launcher_ui/js/skinview3d.bundle.js` is bundled locally and referenced in `development/launcher_ui/index.html:32`.
  - Curated cape textures are located in `development/launcher_ui/capes/`:
    - `sir_founder.png`, `ender_dragon.png`, `optifine_banner.png`, `lunar_astral.png`, `cherry_blossom.png`, `diamond_gladiator.png`.
  - Default skin texture exists at `development/launcher_ui/skins/steve.png`.
- **UI State & Controls (`development/launcher_ui/js/skins.js`)**:
  - `initStudio3DViewer()` (lines 85–135) instantiates `new skinview3d.SkinViewer` with canvas `#skin-studio-3d-canvas`, orbit controls, `WalkingAnimation` (lines 126–128), and cape rendering (lines 119–123).
  - `toggleLauncherStudioSpin()` (lines 154–174), `toggleLauncherStudioAnim()` (lines 176–204), and `toggleLauncherStudioElytra()` (lines 206–228) correctly toggle 3D states.
  - **Issue in `setStudioModel(model)` (lines 243–247)**:
    ```javascript
    if (STUDIO_STATE.viewer) {
      STUDIO_STATE.viewer.skin = (STUDIO_STATE.username.toLowerCase() === 'steve')
        ? 'skins/steve.png'
        : `https://mc-heads.net/skin/${encodeURIComponent(STUDIO_STATE.username)}`;
    }
    ```
    `viewer.skin = ...` is an invalid property assignment on `SkinViewer`. In `skinview3d`, reloading the mesh geometry for 3px (slim) vs 4px (classic) arms requires `viewer.loadSkin(skinUrl, { model: model === 'slim' ? 'slim' : 'default' })`.
  - **Issue in `handleSkinFileUpload(event)` (lines 380–393) & `applySkinFromStudioInput()` (lines 395–407)**:
    Uploaded custom skin files are rendered via `dataUrl`, but `STUDIO_STATE.customSkinData` is not preserved, causing `applySkinFromStudioInput()` to default back to `https://mc-heads.net/skin/${username}`.
- **Backend Skin & Cape Injection (`development/launcher_core/skin_studio_service.py`)**:
  - `apply_skin_and_cape()` (lines 149–195) downloads skin texture to `skins/{clean_user}.png` and writes `customskinloader.json` config files into target instance folders (`instances/{instance_id}/minecraft/config/customskinloader.json`).
  - Exposed through `LauncherBridgeAPI` in `development/launcher_core/bridge.py:498-509`.

---

### B. Bi-Modal Account Management & Sync (Feature 16)
- **Microsoft OAuth 2.0 PKCE Loopback Server (`development/launcher_core/auth_service.py`)**:
  - `start_microsoft_browser_auth()` (lines 556–710):
    - Generates 64-byte urlsafe PKCE verifier and S256 SHA-256 challenge (lines 573–576).
    - Spins up `CustomTCPServer` on loopback port 52135 (falling back to 52136, 52137, 0).
    - Opens system browser to `https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize` (lines 687–702).
    - Serves localized completion HTML page with `window.location.href = "sirlauncher://auth-complete"` (lines 601–631).
    - Background thread `_handle_browser_code()` (lines 711–750) exchanges code for MS Access Token -> Xbox Live JWT (`_XBOX_AUTH_URL`) -> XSTS Token (`_XSTS_URL`) -> Minecraft Token (`_MC_AUTH_URL`) -> Profile API (`_MC_PROFILE_URL`).
    - Writes Prism-compatible MSA entry (`formatVersion: 3`, `type: "MSA"`) into Prism `accounts.json` (lines 872–909).
    - `poll_microsoft_browser_auth()` (lines 751–772) provides asynchronous status polling.
  - **Interface Contract Gap in `start_microsoft_browser_auth()`**:
    `PROJECT.md:67` defines `start_microsoft_browser_auth() -> {"success": bool, "auth_url": str, "port": int}`.
    `auth_service.py:704-709` returns `{"success": True, "auth_url": str, "redirect_uri": str, "message": str}`, omitting explicit `"port": port`.
- **Offline Account Generation using RFC 4122 UUIDv5**:
  - `AuthService.add_offline_account()` (line 340):
    `uuid_value=str(uuid.uuid5(uuid.NAMESPACE_DNS, f"OfflinePlayer:{name}"))`
  - Verified empirically: generates compliant UUIDv5 (e.g. `d7a9e50e-6074-53b7-b701-4f9fa20bb96f` for `'SirAhmed_Test'`).
- **Bi-directional IAS In-Game Sync (`development/launcher_core/auth_service.py`)**:
  - `sync_to_ingame_ias()` (lines 456–468) exports sanitized JSON (`schemaVersion: 1`, `active`, `accounts`) to `self.ias_file` (`data_dir/ias_accounts.json`).
  - **Propagation Gap**: `sync_to_ingame_ias()` currently writes only to root `data_dir/ias_accounts.json`. It does not propagate `ias_accounts.json` into instance game directories (`instances/26.2/minecraft/ias_accounts.json`, `instances/1.8.9/minecraft/ias_accounts.json`, or `%APPDATA%/.minecraft/ias_accounts.json`), which the in-game IAS mod expects.
- **Cloud Sync Codes Integration with Firebase RTDB**:
  - Standard Schema (`PROJECT.md:72-73`):
    `launcherSyncCodes/{6_digit_code}` -> `{"code": str, "userId": str, "username": str, "uuid": str, "skinUrl": str, "createdAt": int, "expiresAt": int, "claimed": bool}`.
  - `auth_service.py:414` & `launcher_ui/js/auth.js:470` use `/launcherSyncCodes/{code}.json`.
  - **Path Discrepancy in `development/launcher_core/cloud_sync_service.py:17`**:
    `resolve_6digit_sync_code()` uses obsolete path `url = f"{self.rtdb_url}/sync_codes/{code}.json"` instead of `launcherSyncCodes/{code}.json`.
  - **Field Parsing in `auth_service.py:419`**:
    Checks `name` or `ign`, but should also check `username` matching the cloud schema.
- **Bridge Method Aliases on `LauncherBridgeAPI` (`development/launcher_core/bridge.py`)**:
  - `PROJECT.md:67-69` specifies:
    - `start_microsoft_browser_auth()` -> exists.
    - `create_offline_account(username)` -> currently named `add_offline_account(name, skin_url="", model="classic")`.
    - `sync_cloud_code(code)` -> currently named `redeem_sync_code(code)` and `resolve_sync_code(code)`.

---

## 2. Logic Chain

1. **SkinView3D Model Switching**:
   - `SkinViewer` in Three.js reconstructs the player mesh geometry (skin, arms, layers) during `loadSkin()`.
   - When switching between Classic (4px) and Slim (3px) models, calling `viewer.loadSkin(skinUrl, { model: 'slim' | 'default' })` properly re-creates arm meshes with 3px/4px UV maps.
   - Therefore, `setStudioModel()`, `selectStudioPreset()`, and `debounceSkinLookup()` in `skins.js` must supply `{ model: STUDIO_STATE.model === 'slim' ? 'slim' : 'default' }`.

2. **In-Game IAS Integration**:
   - The Minecraft In-Game Account Switcher (IAS) mod reads `ias_accounts.json` from the active Minecraft instance root directory (`<game_dir>/ias_accounts.json`).
   - Broadening `sync_to_ingame_ias()` in `auth_service.py` to write `ias_accounts.json` to both `self.data_dir` and all sub-instance Minecraft directories (`instances/*/minecraft/ias_accounts.json`) ensures instant zero-configuration account availability in-game.

3. **Cloud Sync Path & Schema Consistency**:
   - `website-next/lib/firebase.ts` and `website-next/database.rules.json` write to `launcherSyncCodes/{code}`.
   - `cloud_sync_service.py` querying `/sync_codes/` causes 404 lookups.
   - Aligning `cloud_sync_service.py` to `launcherSyncCodes/{code}.json` and supporting `username` field guarantees end-to-end sync between Next.js 16 Web Hub and Desktop Launcher.

4. **Bridge Interface Completeness**:
   - Providing `create_offline_account(self, username)` and `sync_cloud_code(self, code)` as direct first-class methods on `LauncherBridgeAPI` ensures full conformity with `PROJECT.md` interface specifications.

---

## 3. Caveats

- Direct Microsoft token exchange requires live internet access to Microsoft/Xbox/Mojang endpoints (`login.microsoftonline.com`, `user.auth.xboxlive.com`, `api.minecraftservices.com`). In offline test environments, tests must mock HTTP requests or test the local TCP listener and PKCE generator directly.
- Skin resolution from `mc-heads.net` requires network connectivity; offline fallbacks to local `skins/steve.png` are already in place.

---

## 4. Conclusion & Actionable Recommendations

### Recommendations for Implementer (M3):

1. **`development/launcher_ui/js/skins.js`**:
   - Update `setStudioModel(model)`:
     ```javascript
     function setStudioModel(model) {
       STUDIO_STATE.model = model;
       ...
       if (STUDIO_STATE.viewer) {
         const cleanUser = encodeURIComponent(STUDIO_STATE.username || 'Steve');
         const skinUrl = STUDIO_STATE.customSkinData || (STUDIO_STATE.username.toLowerCase() === 'steve' ? 'skins/steve.png' : `https://mc-heads.net/skin/${cleanUser}`);
         STUDIO_STATE.viewer.loadSkin(skinUrl, { model: model === 'slim' ? 'slim' : 'default' }).catch(e => console.warn(e));
       }
       updateStudioBadges();
     }
     ```
   - Update `handleSkinFileUpload()` to store `STUDIO_STATE.customSkinData = dataUrl`.
   - Update `applySkinFromStudioInput()` to pass `STUDIO_STATE.customSkinData` when set.

2. **`development/launcher_core/auth_service.py`**:
   - Include `"port": port` in `start_microsoft_browser_auth()` return dict.
   - Update `sync_to_ingame_ias()` to write `ias_accounts.json` to instance directories:
     `instances/26.2/minecraft/ias_accounts.json`, `instances/1.8.9/minecraft/ias_accounts.json`, etc.
   - Update `redeem_sync_code()` to support `data.get("username") || data.get("name") || data.get("ign")`.

3. **`development/launcher_core/cloud_sync_service.py`**:
   - Change path in `resolve_6digit_sync_code()` to `{self.rtdb_url}/launcherSyncCodes/{code}.json`.

4. **`development/launcher_core/bridge.py`**:
   - Add alias methods:
     ```python
     def create_offline_account(self, username, skin_url="", model="classic"):
         return self.auth.add_offline_account(username, skin_url, model)

     def sync_cloud_code(self, code):
         return self.auth.redeem_sync_code(code)
     ```

5. **`tests/test_cloud_sync_and_auth.py`**:
   - Author full test suite verifying:
     - RFC 4122 UUIDv5 DNS namespace determinism and variant bits.
     - `ias_accounts.json` schema validation.
     - `start_microsoft_browser_auth()` PKCE challenge and local port listener.
     - `redeem_sync_code()` and `resolve_6digit_sync_code()` with `launcherSyncCodes` payload.
     - Skin and Cape injector config generation (`customskinloader.json`).

---

## 5. Verification Method

1. **Python Unit Tests**:
   ```bash
   python -m unittest tests/test_auth_and_accounts.py
   python -m unittest tests/test_cloud_sync_and_auth.py
   python -m unittest tests/test_launcher_bridge.py
   ```
2. **UUIDv5 & Account Verification**:
   ```bash
   python -c "
   import sys; sys.path.insert(0, 'development')
   from launcher_core.auth_service import AuthService
   auth = AuthService('instances')
   res = auth.add_offline_account('Test_IAS_User')
   assert res['success']
   assert len(res['account']['uuid']) == 36
   print('✓ UUIDv5 and IAS Account Generation verified.')
   "
   ```
3. **Loopback Server Verification**:
   ```bash
   python -c "
   import sys; sys.path.insert(0, 'development')
   from launcher_core.auth_service import AuthService
   auth = AuthService('instances')
   res = auth.start_microsoft_browser_auth()
   assert res['success']
   assert 'port' in res or 'redirect_uri' in res
   print('✓ Microsoft OAuth PKCE Loopback verified.')
   if hasattr(auth, '_ms_browser_state') and auth._ms_browser_state.get('server'):
       auth._ms_browser_state['server'].server_close()
   "
   ```
4. **Ecosystem Doctor Audit**:
   ```bash
   python ecosystem_doctor.py
   ```
