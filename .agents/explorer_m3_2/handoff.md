# Investigation Report: 1-Click Video Preset Engine (Milestone 3 / Feature 14)

## 1. Observation

### 1.1 Codebase Entry Points & Contracts
- **`PROJECT.md` (Line 66)**:
  ```markdown
  - `apply_video_preset(instance_name, preset_name)` -> `{"success": bool, "applied": list[str], "error": str}`
  ```
- **`development/launcher_core/bridge.py` (Lines 155-156)**:
  ```python
  def apply_video_preset(self, inst_id="sir-26-ultra", preset_name="balanced"):
      return self.instances.apply_video_preset(inst_id, preset_name)
  ```
- **`development/launcher_core/instance_service.py` (Lines 932-1116)**:
  `InstanceService.apply_video_preset(self, inst_id="sir-26-ultra", preset_name="balanced")` performs instance directory resolution, loads existing `options.txt` to preserve controls/audio, and injects configuration across target directories.
- **`development/launcher_core/shaders_service.py` (Lines 59-85)**:
  `ShadersService.apply_shader_preset(self, preset_id_or_file, instance_dir="26.2")` writes shader settings to `instances/{instance_dir}/minecraft/optionsshaders.txt`.
- **`development/launcher_ui/js/launch.js` (Lines 100-117)**:
  Frontend `applyVideoPreset(presetName, instId = null)` calls `window.pywebview.api.apply_video_preset(activeInst, presetName)` and displays toast notifications.
- **`development/launcher_ui/js/instances.js` (Lines 487-499)**:
  Frontend `applyVideoPresetPrompt(instId)` uses `prompt()` to request preset input and validates against `['ultra', 'balanced', 'performance']`.

---

### 1.2 Configuration Target Artifacts & Injection Schemes

#### Modern 26.2 (Fabric 0.16.10 + Sodium 0.9.1 + Iris 1.7+)
1. **Vanilla `options.txt`**:
   - `renderDistance`: `4` (Potato), `8` (Competitive), `12` (Balanced), `16` (Ultra)
   - `simulationDistance`: `4` (Potato), `6` (Competitive), `8` (Balanced), `10` (Ultra)
   - `graphicsMode`: `1` (Fast for Potato & Competitive), `0` (Fancy for Balanced & Ultra)
   - `smoothLighting`: `false` (Potato & Competitive), `true` (Balanced & Ultra)
   - `biomeBlendRadius`: `0` (Potato), `3` (Competitive), `7` (Balanced), `15` (Ultra)
   - `entityDistanceScaling`: `0.5` (Potato), `0.8` (Competitive), `1.0` (Balanced), `1.5` (Ultra)
   - `entityShadows`: `false` (Potato & Competitive), `true` (Balanced & Ultra)
   - `particles`: `2` (Minimal for Potato & Competitive), `0` (All for Balanced & Ultra)
   - `mipmapLevels`: `0` (Potato & Competitive), `4` (Balanced & Ultra)
   - `clouds`: `false` (Potato & Competitive), `fancy` (Balanced & Ultra)
   - `gamma`: `1.0` (Potato & Competitive - full brightness), `0.0` (Balanced & Ultra)
   - `version: 3465`, `guiScale: 2`, `enableVsync: false`, `attackIndicator: 1`, `autoSaveIndicator: true`, `onboardAccessibility: false`
2. **Sodium `config/sodium-options.json`**:
   - Quality:
     * `leaves_quality`: `"FAST"` (Potato/Competitive) vs `"CUTOUT"` (Balanced/Ultra)
     * `weather_quality`: `"FAST"` (Potato/Competitive) vs `"HIGH"` (Balanced/Ultra)
     * `cloud_distance`: `16` (Potato), `32` (Competitive), `128` (Balanced/Ultra)
     * `menu_background_blur`: `0` (Potato/Competitive), `5` (Balanced/Ultra)
     * `improved_transparency`: `False` (Potato/Competitive), `True` (Balanced/Ultra)
     * `weather_radius`: `2` (Potato), `5` (Competitive), `10` (Balanced/Ultra)
   - Performance:
     * `chunk_builder`: `"IMMEDIATE"` (Potato/Competitive) vs `"SEMI_BLOCKING"` (Balanced/Ultra)
     * `animate_only_visible_textures`: `True`
   - Notifications:
     * `hide_donation_prompt`: `True`
3. **Iris `config/iris.properties`**:
   - Potato & Competitive: `enableShaders=false\nshaderPack=OFF\n`
   - Balanced: `enableShaders=true\nshaderPack=SIR_Balanced_Shader.zip\n`
   - Ultra: `enableShaders=true\nshaderPack=SIR_Extreme_Shader.zip\n`

#### Legacy 1.8.9 (Forge 11.15.1.2318 + OptiFine HD U M5)
1. **Vanilla `options.txt`**:
   - `renderDistance`: `4` (Potato), `8` (Competitive), `12` (Balanced), `16` (Ultra)
   - `fancyGraphics`: `false` (Potato/Competitive), `true` (Balanced/Ultra)
   - `ao`: `0` (Potato), `1` (Competitive), `2` (Balanced/Ultra)
   - `clouds`: `false` (Potato/Competitive), `true` (Balanced/Ultra)
   - `particles`: `2` (Potato/Competitive), `0` (Balanced/Ultra)
   - `anisotropicFiltering`: `1` (Potato/Competitive), `4` (Balanced), `8` (Ultra)
   - `guiScale: 2`, `gamma: 1.0`, `fullscreen: false`, `enableVsync: false`, `resourcePacks: ["SIR_Legacy_32x.zip"]`
2. **OptiFine `optionsof.txt`**:
   - `ofRenderDistanceChunks`: `4` (Potato), `8` (Competitive), `12` (Balanced), `16` (Ultra)
   - `ofFastRender`: `true` (Potato/Competitive), `false` (Balanced/Ultra)
   - `ofFastMath`: `true` (Potato/Competitive/Balanced), `false` (Ultra)
   - `ofSmoothFps`: `false` (Potato/Competitive), `true` (Balanced/Ultra)
   - `ofAo`: `0` (Potato), `1` (Competitive), `2` (Balanced/Ultra)
   - `ofClouds`: `3` (Off for Potato/Competitive), `1` (Fast for Balanced/Ultra)
   - `ofTrees`: `1` (Fast for Potato/Competitive), `2` (Fancy for Balanced/Ultra)
   - `ofDynamicLights`: `3` (Off for Potato/Competitive), `1` (Fancy for Balanced/Ultra)
3. **OptiFine Shaders `optionsshaders.txt`**:
   - Potato & Competitive: `shaderPack=OFF\n`
   - Balanced: `shaderPack=SIR_Balanced_Shader.zip\n`
   - Ultra: `shaderPack=SIR_Extreme_Shader.zip\n`

---

### 1.3 Empirical Test Execution
- Ran `python .agents/explorer_m3_2/test_edge_cases.py`:
  * All 4 tests passed, confirming preservation of custom keybindings (`key_key.sprint`) and sound volume (`soundCategory_master`) across preset injections.
  * Verified that `"cinematic"` keyword fell back to Balanced shader instead of Ultra/Extreme shader due to missing keyword match in `instance_service.py:1073`.
- Ran existing test suites `tests/test_launcher_bridge.py` and `tests/test_native_runner.py`:
  * 51/51 tests passed in 20.5s.

---

## 2. Logic Chain

1. **Preset Recognition Logic**:
   - Observation: In `instance_service.py:1073`, the check is:
     `if "ultra" in preset_clean or "extreme" in preset_clean or "high" in preset_clean:`
   - Logic: When a user requests the preset `"cinematic"` (as named in the UI card `"✨ Cinematic Master"`), it does not match `"ultra"`, `"extreme"`, or `"high"`, and thus drops into `else:` (Balanced preset).
   - Deduction: Adding `"cinematic"` and `"fidelity"` to the Ultra branch ensures keyword parity across UI descriptions and backend parsers.

2. **Cross-Service Shader Synchronization**:
   - Observation: `ShadersService.apply_shader_preset(preset_id, instance_dir)` writes to `instances/{instance_dir}/minecraft/optionsshaders.txt`.
   - Logic: On Modern 26.2 (Fabric), the active shader mod is Iris, which reads `config/iris.properties` (or `minecraft/config/iris.properties`), whereas `optionsshaders.txt` is primarily read by OptiFine on Legacy 1.8.9.
   - Deduction: When a user applies a shader preset from the Shaders tab, `ShadersService` must write both `optionsshaders.txt` and `config/iris.properties` so the change applies consistently regardless of whether the profile is running Iris (26.2) or OptiFine (1.8.9).

3. **Exception Safety & Contract Adherence**:
   - Observation: The return dictionary contract in `PROJECT.md` specifies `{"success": bool, "applied": list[str], "error": str}`.
   - Logic: If an IO error, directory access lock, or permission issue occurs during file injection, `apply_video_preset` should be wrapped in an outer `try...except Exception as e:` block that returns `{"success": False, "applied": [], "error": str(e), "message": f"Failed to apply preset: {e}"}`.

4. **UI Validation & Ergonomics**:
   - Observation: `development/launcher_ui/js/instances.js:491` validates preset input with:
     `if (['ultra', 'balanced', 'performance'].includes(valid))`
   - Logic: If a user enters `potato` or `competitive` or `cinematic` in the instance cards, the UI validation fails with `'Invalid preset selected!'` even though the backend supports these modes.
   - Deduction: The UI validator should expand valid options to include `['ultra', 'balanced', 'performance', 'competitive', 'potato', 'extreme', 'cinematic', 'low']` or provide a modern modal/dropdown selector without `window.prompt()`.

---

## 3. Caveats

- **Active Running Game Instances**: Modifying `options.txt` while Minecraft is currently running will be overwritten by the game process when Minecraft exits. This is standard Minecraft engine behavior; presets should be applied prior to launching or when the instance is idle.
- **Custom Shader Pack Variations**: Custom shader packs other than `SIR_Extreme_Shader.zip` and `SIR_Balanced_Shader.zip` can be selected via the shader pack dropdown or files, falling back to literal pack filenames when specified.
- No other caveats.

---

## 4. Conclusion

1. The core 1-Click Video Preset Engine (Feature 14) architecture is well-structured and implements genuine tri-layer configuration injection (`options.txt`, `sodium-options.json`, `iris.properties`) for Modern 26.2 Fabric and dual-layer injection (`options.txt`, `optionsof.txt`, `optionsshaders.txt`) for Legacy 1.8.9 Forge.
2. The engine non-destructively preserves user keybindings, audio sliders, and custom options.
3. Four minor refinements are recommended for complete Milestone 3 production polish:
   - **Recommendation A**: Add `"cinematic"`, `"fidelity"`, `"max"` to the Ultra preset match branch in `instance_service.py:1017` and `1073`.
   - **Recommendation B**: Wrap `apply_video_preset` in a top-level `try...except` block returning `{"success": False, "applied": [], "error": str(e)}` on unexpected I/O errors.
   - **Recommendation C**: Update `ShadersService.apply_shader_preset` in `shaders_service.py` to write both `optionsshaders.txt` and `config/iris.properties` for cross-version consistency.
   - **Recommendation D**: Add `tests/test_video_presets.py` to the automated test suite to continuously verify tri-layer injection across all 4 profile archetypes (Potato, Competitive, Balanced, Ultra) on both Modern and Legacy instances.

---

## 5. Verification Method

### Automated Unit Test Command
```bash
python -m unittest tests/test_launcher_bridge.py
```

### Dedicated Preset Verification Script
Run the newly created edge case verification suite:
```bash
python .agents/explorer_m3_2/test_edge_cases.py
```

### Expected Results
- `Ran 4 tests in <1.0s`
- `OK`
- Verified existence of `options.txt`, `sodium-options.json`, and `iris.properties` for Modern 26.2.
- Verified existence of `options.txt`, `optionsof.txt`, and `optionsshaders.txt` for Legacy 1.8.9.
- Verified keybinding preservation (`key_key.sprint:key.keyboard.f` for Modern, `key_key.sprint:33` for Legacy).
