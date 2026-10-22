# Progress — Milestone 1 (Desktop Applications & PyInstaller Packaging)

Last visited: 2026-09-08T17:54:30Z
Status: Completed

## Tasks Checklist
- [x] 1. Extend Deep-Link Protocol Routing in `development/launcher_ui/js/navigation.js`
  - [x] 1.1 Add route for `mod/install`: triggers `switchTab('mods')` and `installOnlineModById(modId)`
  - [x] 1.2 Add route for `profile`: triggers toast and `selectInstance(profName)`
  - [x] 1.3 Add genuine `installOnlineModById(modId)` helper connecting to `bridge.py`
  - [x] 1.4 Validate syntax with `node --check`
- [x] 2. Update Master Packaging Synchronization (`build_ecosystem.py`)
  - [x] 2.1 Add `website-next/public/share` and `website-next/out/share` to distribution targets
  - [x] 2.2 Add `--sync-only` flag support for immediate distribution sync
  - [x] 2.3 Prevent self-copy collisions when source equals destination
  - [x] 2.4 Synchronize fresh 35.4 MB `SIR Launcher.exe` into `website-next/public/share/` and `website-next/out/share/`
  - [x] 2.5 Verify SHA-256 hash parity across distribution hubs
- [x] 3. Packaging & Binary Verification
  - [x] 3.1 Verify all 3 executables exist and have valid PE metadata (`SIR Launcher.exe`, `SIR Server Manager.exe`, `SIR Installer.exe`)
  - [x] 3.2 Verify PyInstaller spec files (`SIR Launcher.spec`, `SIR Server Manager.spec`, `SIR Installer.spec`)
  - [x] 3.3 Verify clean PyInstaller compilation (task-90 compiling `SIR Installer.spec` passed with code 0)
- [x] 4. Verification & Testing
  - [x] 4.1 Run `python -m unittest tests/test_native_runner.py tests/test_tray_and_window_lifecycle.py -v` (47/47 passed, 100% OK)
  - [x] 4.2 Run `python ecosystem_doctor.py` (100% HEALTHY across all 6 layers)
  - [x] 4.3 Verify Drive D free space invariant $\ge 18.00\text{ GB}$ (18.34 GB free)
- [x] 5. Documentation & Handoff
  - [x] 5.1 Write comprehensive `handoff.md`
  - [x] 5.2 Send coordination message to parent (`e6854040-b2f7-4215-a3ca-09a5a910d136`)
