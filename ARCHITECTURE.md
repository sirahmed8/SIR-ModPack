# 🏛️ Architectural Deep-Dive: SIR Unified Minecraft Ecosystem

This document provides a comprehensive technical breakdown of the algorithms, cloud channels, and optimization pipelines powering the SIR Ecosystem.

---

## 1. 🔄 Multi-Engine Synchronization Architecture

The ecosystem coordinates three primary environments simultaneously:
1. **Modern 26.2 (Fabric Engine):**
   - Sodium 0.9.1 + Iris 1.11.2 for modern multi-threaded Vulkan-like OpenGL pipeline.
   - C2ME 0.4.2 for asynchronous chunk generation and thread pooling.
   - FerriteCore 9.0.0 & ModernFix 5.27.19 for string deduplication and dynamic resource reloading.
   - InGameAccountSwitcher (IAS 9.0.7) for in-game multi-account management.
2. **Legacy 1.8.9 (Forge Architecture):**
   - OptiFine HD U M5 + PolyPatcher 1.10.3 + BetterFps for maximum frame throughput.
   - TcpNoDelayMod-2.0 disabling Nagle's packet buffering for zero-delay hit registration.
   - RawInput-0.1.8 bypassing Windows pointer acceleration for 1000Hz mouse polling.
3. **Lunar Client Profile Bridge:**
   - Universal synchronization of `profiles.db`, 32x resource packs, and shader packs into `.lunarclient/`.

---

## 2. ⚡ Parallel Multi-Core Delta Sync Engine

The standalone installer (`SIR_Installer_GUI.py`) features a bespoke synchronization engine:
- **`ThreadPoolExecutor` Concurrency:** Up to 16 worker threads hash and copy files concurrently in Max Performance mode.
- **Smart Hash Comparison:** Compares file sizes and timestamps, falling back to CRC32 hashing only when required.
- **Hardware Power Governor:**
  - `EcoQoS / PROCESS_MODE_BACKGROUND_BEGIN`: Limits thread scheduling and throttles background I/O so the operating system stays responsive.
  - `Max Performance`: Uses `ABOVE_NORMAL_PRIORITY_CLASS` and unthrottled I/O.

---

## 3. 🌊 GLSL Optical Physics & Shader Pipeline

Built upon the modular Bliss and Photon architecture with custom optical extensions:
- **Voronoi Caustics:** Double-octave procedural caustics calculated in `waterBump.glsl` with refractive dispersion.
- **Snell's Law & Water Absorption:** Realistic light bending across water surfaces with wavelength-dependent underwater absorption in `water_absorbance_effects.glsl`.
- **Distant Horizons Projection Clamping:** Clamps `DHdepth` between `0.0001` and `0.9999` in `DistantHorizons_projections.glsl` to eliminate vertical stretching and smearing.

---

## 4. 🌐 Real-Time Cloud Data Highways

- **`/profiles/{ign}.json`:** Web 3D Skin Studio pushes player skin textures and model settings directly to Firebase RTDB; Desktop Installer automatically retrieves them on account binding.
- **`/broadcasts/active.json`:** Real-time push broadcast channel allowing administrators to send instant alerts simultaneously to the Website and Desktop Installer.
- **`/presence/sessions/`:** Live presence tracker capturing connected web visitors, active installer runs, and in-game players.
