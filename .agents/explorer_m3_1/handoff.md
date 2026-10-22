# Milestone 3 Explorer Investigation Report: Desktop Client UI, Cyber-Dark Tokens & HCI Experience

## Executive Summary
This report delivers an exhaustive, read-only architectural investigation into the SIR Launcher Modern Desktop Client UI (`development/launcher_ui/` and `development/launcher_source/SIR_Launcher_Modern.py`), evaluating compliance with **Feature 13 (Cyber-Dark UI Design System & HCI Experience)** and related desktop requirements.

---

## 1. Observation

### 1.1 Architecture & Windows DWM Dark Titlebar Integration
- **Entry Point**: `development/launcher_source/SIR_Launcher_Modern.py` lines 50–94
  - Uses `ctypes.windll.dwmapi.DwmSetWindowAttribute` to enforce immersive dark mode:
    - Attribute `20` / `19` (`DWMWA_USE_IMMERSIVE_DARK_MODE` = `1`)
    - Attribute `35` (`DWMWA_CAPTION_COLOR` = `0x000E0906` BGR for `#06090e`)
  - Ensures Per-Monitor V2 DPI awareness (`SetProcessDpiAwarenessContext(-4)` / `SetProcessDPIAware()`)
  - Window defaults: Initial `1180x760`, Minimum `960x620`, Background `#06090e`, centered on primary monitor.
  - Bridge binding: `pywebview.create_window(..., js_api=bridge_api, background_color='#06090e')`.

### 1.2 Cyber-Dark Glassmorphic Design Tokens & Theming (`app.css`)
- **Typography**: Imports Plus Jakarta Sans (`weights 400..800`) and JetBrains Mono (`weights 400..700`) at lines 1–4.
- **60-30-10 Color Palette**:
  - **60% Dominant Base**: `--bg-obsidian: #06090e` / `--bg-dark-base: #06090e` (lines 38–48, 533–550).
  - **30% Structural Surfaces**: `--bg-surface: rgba(16, 22, 36, 0.75)`, `--bg-card: #0d121f` with `backdrop-filter: blur(16px)` and subtle borders (`border-slate-800/80` / `rgba(255,255,255,0.06)`).
  - **10% High-Intent Accents**: `--neon-cyan: #00e5ff`, `--neon-emerald: #38ef7d`, `--neon-amber: #f59e0b`.
- **Curvature Hierarchy**:
  - Hero & major cards: `rounded-3xl` (24px) / `rounded-2xl` (16px).
  - Header pills & filter controls: `rounded-xl` (12px–14px).
  - Interactive badges & status pills: `rounded-full`.
- **Physics-Based Spring Micro-Interactions**:
  - Transitions configured with `cubic-bezier(0.16, 1, 0.3, 1)` and `duration-200 / duration-300`.
  - Active press feedback: `active:scale-[0.98]` / `active:scale-95`.
  - Hardware acceleration: `backface-visibility: hidden` and `will-change: transform`.
- **Dual-Theme Integrity**: Complete CSS variable mapping for both Cyber Obsidian Dark and Neomorphic Light mode (`html.light`, lines 533–840 and 1156–1756).

---

### 1.3 Concrete Bugs & Defects Discovered

#### Defect 1: Unclosed Modal HTML & Broken DOM Hierarchy
- **File**: `development/launcher_ui/index.html` (lines 2061–2126)
- **Observation**:
  In `#ms-browser-auth-modal` (line 2062), `<div class="modal-card max-w-sm text-center">` starts, but the closing tags `</div></div>` are missing before `<div id="confirm-action-modal">` begins at line 2101:
  ```html
  2093:       <div class="flex justify-between gap-3 pt-3 border-t border-slate-200 dark:border-slate-800">
  2094:         <button onclick="cancelMicrosoftAuth()" ...>Cancel</button>
  2095:         <button onclick="submitMicrosoftAccount()" ...>Re-open Browser</button>
  2096:       </div>
  2097:   <!-- Custom In-App Action Confirmation Modal -->
  2098:   <div id="confirm-action-modal" class="modal-backdrop hidden z-[99999]">
  ```
- **Consequence**: `#confirm-action-modal` is nested inside `#ms-browser-auth-modal`, corrupting layout and z-index positioning when modals open.

#### Defect 2: Duplicate Conflicting `showConfirmDialog` Breaking Account Removal
- **Files**:
  - `development/launcher_ui/js/i18n.js` (lines 5–75): Defines Promise-based `showConfirmDialog` targeting `#custom-dialog-modal` and returning `Promise<boolean>`.
  - `development/launcher_ui/js/modals.js` (lines 4–29): Overwrites `window.showConfirmDialog` with a callback-based version (`_confirmDialogCallback = onConfirm; openModal('confirm-action-modal');`) returning `undefined`.
  - `development/launcher_ui/js/auth.js` (line 132): Calls `const confirmed = await showConfirmDialog({...}); if (!confirmed) return;`.
- **Consequence**: Because `modals.js` is loaded after `i18n.js` (lines 2130 vs 2134 in `index.html`), `showConfirmDialog` returns `undefined`. In `auth.js`, `!confirmed` evaluates to `true`, causing account deletion to silently abort every time.

#### Defect 3: Missing Media & Screenshots Studio Frontend (`#view-gallery`)
- **Files**:
  - `development/launcher_ui/index.html` (lines 881–905): References `<button onclick="refreshScreenshots()">`, `<button onclick="openScreenshotsDir()">`, `<div id="gallery-grid">`.
  - `development/launcher_ui/js/navigation.js` (line 45): Calls `renderGalleryGrid();`.
  - `development/launcher_core/gallery_service.py` & `bridge.py` (lines 424–432, 487–492): Backend has complete implementations for `get_screenshots`, `delete_screenshot`, `open_screenshots_folder`, `set_as_wallpaper`, `reveal_screenshot`.
- **Consequence**: There is no `gallery.js` in `development/launcher_ui/js/`. Navigating to the Gallery tab or clicking "Refresh" / "Open Folder" throws `ReferenceError: renderGalleryGrid is not defined` / `ReferenceError: refreshScreenshots is not defined`.

#### Defect 4: Missing RCON Remote Console Frontend Handlers (`#view-rcon`)
- **Files**:
  - `development/launcher_ui/index.html` (lines 1080–1112): Calls `sendQuickRcon('/tps')`, `executeRconFromInput()`.
  - `development/launcher_core/bridge.py` (line 472): Backend provides `execute_rcon_command(command, host, port, password)`.
- **Consequence**: `sendQuickRcon` and `executeRconFromInput` are not implemented in any frontend JavaScript file, causing runtime `ReferenceError` when clicking RCON buttons.

#### Defect 5: Missing Resource Packs Actions in `js/packs.js`
- **Files**:
  - `development/launcher_ui/index.html` (lines 864–868): Calls `<button onclick="refreshPacks()">` and `<button onclick="openPacksDir()">`.
  - `development/launcher_ui/js/packs.js`: Defines `renderResourcePacksGrid()` and `renderPacksGrid()`, but lacks `refreshPacks()` and `openPacksDir()`.
- **Consequence**: Clicking "Refresh" or "Open Folder" in the Resource Packs panel throws `ReferenceError: refreshPacks is not defined` and `ReferenceError: openPacksDir is not defined`.

#### Defect 6: Bridge API Argument Mismatch in `toggle_mod`
- **Files**:
  - `development/launcher_ui/js/mods.js` (line 488): `await window.pywebview.api.toggle_mod(modId, enabled, activeInst);` (3 arguments).
  - `development/launcher_core/bridge.py` (line 199): `def toggle_mod(self, mod_id, enabled_state): return self.mods.toggle_mod(mod_id, enabled_state)` (2 arguments).
  - `development/launcher_core/mods_service.py` (line 45): `def toggle_mod(self, filename, enabled_state, instance_dir="26.2"):` (accepts 3 arguments).
- **Consequence**: Calling `toggle_mod` from the UI causes a Python `TypeError: toggle_mod() takes 3 positional arguments but 4 were given` (including `self`).

#### Defect 7: Mismatched Bridge Method Names
- `app.js` (line 121) calls `api.open_mods_folder(instId)`, but `bridge.py` (line 152) defines `open_instance_mods_folder(inst_id)`.
- `js/shaders.js` (line 66) calls `api.set_active_shader(target.file)`, but `bridge.py` (line 364) defines `apply_shader(preset_id, instance_dir)`.
- `js/packs.js` (line 51) calls `api.set_active_resource_pack(activeInst, chosen.file)`, but `bridge.py` (line 454) defines `toggle_resource_pack(pack_filename, enabled_state, instance_id)`.
- `app.js` (line 172) calls `api.set_power_governor(gov)`, which is not exposed on `bridge.py`.

#### Defect 8: Missing Server Refresh Function Alias
- `index.html` (line 694) calls `onclick="refreshServersLive()"`.
- `js/servers.js` (line 441) defines `async function loadServersLive()`.
- **Consequence**: Clicking "Refresh Live" in Servers view throws `ReferenceError: refreshServersLive is not defined`.

#### Defect 9: Missing Empty State in Instances Matrix
- In `js/instances.js` (lines 415–420), when a category filter matches 0 profiles, `container.innerHTML` is cleared with no fallback card or empty illustration.

---

## 2. Logic Chain

1. **Window Frame & DWM**:
   - `_apply_dwm_dark` in `SIR_Launcher_Modern.py` executes Win32 DWM APIs on `window.native.Handle`. This correctly sets caption color `0x000E0906` matching the `#06090e` obsidian body background, satisfying the dark titlebar requirement of Feature 13.
2. **CSS Token System**:
   - The token architecture in `app.css` follows the 60-30-10 palette, typography rules, curvature scale, and spring cubic-bezier transitions specified in the modern UI design system standards.
3. **5-State Completeness Assessment**:
   - **Launchpad**: 5/5 complete (Initial, Loading, Loaded, Error, Success).
   - **Mods / Online Store**: 5/5 complete (Initial, Shimmer/Loading spinner, Empty search fallback with CTA, Error toast, Overflow "View More" pagination).
   - **Servers Browser**: 4.5/5 complete (Missing empty state for custom IP scan failure is handled, but `refreshServersLive` button reference is mismatched).
   - **Instances Matrix**: 4/5 complete (Missing empty state card when 0 instances match a filter).
   - **Gallery & RCON**: 0/5 complete (Frontend JavaScript implementations missing).
4. **Bridge Interoperability**:
   - Python backend services (`gallery_service.py`, `rcon_service.py`, `mods_service.py`) are robust and functional, but argument and naming discrepancies between `bridge.py` and `launcher_ui` prevent seamless event execution.

---

## 3. Caveats
1. **Read-Only Explorer Scope**: No modifications to source code files were made during this investigation.
2. **PyWebView Runtime Dependency**: Full live DWM caption coloring requires running on Windows OS with PyWebView initialization; browser-only preview uses CSS window framing fallback.

---

## 4. Conclusion & Recommended Action Plan

The Desktop Client UI is visually impressive and strictly adheres to the Cyber-Dark Glassmorphic design tokens, Windows DWM titlebar integration, and performance standards. However, 9 concrete code defects must be resolved by the implementer:

### Action Items for Implementation:
1. **Fix `index.html` Modal Closing Tags** (lines 2099–2101): Add missing `</div></div>` to properly close `#ms-browser-auth-modal` before `#confirm-action-modal`.
2. **Unify `showConfirmDialog` in `js/modals.js` and `js/i18n.js`**: Use a single unified Promise-based dialog supporting both Promise `await` and callback patterns across `#custom-dialog-modal`.
3. **Implement `js/gallery.js`**: Create `gallery.js` defining `renderGalleryGrid()`, `refreshScreenshots()`, `openScreenshotsDir()`, `setAsWallpaper()`, and `deleteScreenshot()`, and include it in `index.html`.
4. **Implement RCON handlers in `js/diagnostics.js`**: Add `sendQuickRcon(cmd)` and `executeRconFromInput()` calling `window.pywebview.api.execute_rcon_command(...)`.
5. **Add Pack Helpers to `js/packs.js`**: Add `refreshPacks()` and `openPacksDir()`.
6. **Harmonize Bridge Method Signatures in `bridge.py` & UI**:
   - Update `toggle_mod(self, mod_id, enabled_state, instance_dir="26.2")` in `bridge.py`.
   - Add bridge alias `open_mods_folder(self, inst_id="26.2")`.
   - Add bridge alias `set_active_shader(self, shader_name, instance_dir="26.2")`.
   - Add bridge alias `set_active_resource_pack(self, instance_id, pack_name)`.
   - Add bridge handler `set_power_governor(self, mode)`.
7. **Add Server Alias**: Add `window.refreshServersLive = loadServersLive;` in `js/servers.js`.
8. **Add Empty State in `js/instances.js`**: Render an empty state card when `filtered.length === 0`.
9. **Eliminate Duplicate Function Definitions**: Deduplicate overlapping helper functions between `app.js` and `js/` modules.

---

## 5. Verification Method

### Test Suite Execution
Run the automated unit and bridge integration tests:
```powershell
python -m unittest tests/test_launcher_bridge.py
python -m unittest discover -s tests -p "test_*.py"
```

### Manual Visual & Functional Checklist
1. Launch the application: `python development/launcher_source/SIR_Launcher_Modern.py`.
2. Verify dark DWM titlebar (`#06090e`) on Windows 10/11.
3. Switch through all 13 sidebar tabs (`Launchpad`, `Instances`, `Mods`, `Shaders`, `Servers`, `Satellite`, `Worlds`, `Packs`, `Gallery`, `Skins`, `Logs`, `RCON`, `Hardware`, `Settings`) — verify zero console errors.
4. Test Account Removal in Account Manager Studio — verify confirmation dialog appears and deletes account upon confirmation.
5. Test Gallery tab — verify screenshot cards load, "Refresh" and "Open Folder" function correctly.
6. Test RCON tab — click `/tps` and type a command to verify response in the console output.
