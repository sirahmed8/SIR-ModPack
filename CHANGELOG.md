# 📜 SIR ModPack — Official Ecosystem Changelog
### *Unified Minecraft Experience • Semantic Versioning • 100% Free & Independent Platform*

> All notable changes to the SIR Ecosystem are documented here following [Semantic Versioning](https://semver.org/).
> Format: **MAJOR.MINOR.PATCH** — `v1.0.0` is the Genesis public launch. Future user-facing updates will be `v1.0.1` (patches) or `v1.1.0` (feature updates).
> Contact: `a7medorabe7@gmail.com`

---

## [Unreleased]
> Changes staged for the next public release. Will be assigned a version on launch.

- Nothing staged yet — ecosystem is live at `v1.0.0 Genesis`.

---

## [v1.1.0] — Planned: Q4 2026

> Future feature update milestone. Details TBD based on community feedback.

### ✨ Planned Features
- Multiplayer friends list integration with real-time party invites via Satellite Hub
- Built-in mod update checker against Modrinth & CurseForge APIs
- SIR Cloud Save — automatic world sync to Firebase Storage
- Web Platform `/trainer` page — interactive combo & PvP technique training simulator
- Skin wardrobe bulk import from NameMC & PMC

---

## [v1.0.1] — Planned: Q3 2026

> First patch release after community feedback on v1.0.0.

### 🔧 Bug Fixes
- _Reserved for hotfixes based on public v1.0.0 feedback_
- _Report issues to `a7medorabe7@gmail.com`_

---

## [v1.0.0] — September 8, 2026 — 🏆 Genesis Public Launch

> The **v1.0.0 Genesis** is the first complete public launch of the SIR ModPack Ecosystem.
> It ships as a production-ready, fully integrated suite of desktop applications, dual Minecraft engines,
> a Next.js 16 web platform, and cloud infrastructure — all under the **Free Independent Software Agreement**.
>
> **Tests:** 368/368 unit tests + 39 E2E adversarial tests — all passing.
> **Platform:** [sir-modpack.web.app](https://sir-modpack.web.app)
> **Contact:** `a7medorabe7@gmail.com`

---

### 🖥️ Desktop Applications Suite

#### SIR Launcher Pro (`SIR Launcher.exe`)
- **Direct JVM Launch Pipeline**: Native Java 21/25 execution with zero-overhead subprocess management — no wrapper, no overhead.
- **Generational ZGC Engine**: Auto-activates `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5` for Java 21+ systems with ≥ 6GB RAM, eliminating micro-stutters during world loading.
- **G1GC Fallback**: Auto-injects Aikar flags (`-XX:+ParallelRefProcEnabled -XX:+UseNUMA -XX:+AlwaysPreTouch -XX:MaxGCPauseMillis=20`) for ≤ 4GB or legacy Java.
- **3D Skin Studio**: Real-time OrbitControls WebGL skin viewer with outer layer toggle, zoom, pan and drag support.
- **Accounts Manager**: Full multi-account switcher with Microsoft OAuth2 PKCE loopback auth, offline username validation, and active profile selection.
- **Satellite Social Hub**: Online friends presence list, live message stream, direct message composer, and server party invite dispatcher.
- **Profile Creator**: Archive extraction (`.zip` / `.mrpack`) with automated migration scanner for PrismLauncher, Lunar Client, and Vanilla `.minecraft` instances.
- **6-Tab Game Settings**: ⚡ Memory & JVM · 🎮 Display & Window (Borderless/Fullscreen) · 🚀 Hardware & GPU (discrete GPU preference) · 🌐 Network & CDN Mesh Routing · 🎨 Visuals & Shaders (Iris K toggle) · 🛡️ Diagnostics & Privacy (Discord RPC, crash auto-report).
- **Quick Presets Bar**: Horizontal scrolling pill buttons for instant one-click profile switching across all 8 instance profiles.
- **Live Server Radar**: Real-time ICMP ping scanner with color-coded latency indicators for all 12 configured servers.
- **Game Integrity Doctor**: Automated CRC-32 validation of the full mod payload against `delta_manifest.json` with self-healing re-download.
- **Win32 RAM Compactor**: Calls `EmptyWorkingSet` via `psapi.dll` to purge unused JVM memory pages without server interruption.
- **Launch Console**: Scrollable real-time JVM log output drawer with copy-to-clipboard support.
- **First-Time Onboarding Wizard**: 4-step guided setup: Welcome Overview → Language & Theme → Google Cloud Auth → Completion.
- **Crash Analyzer**: Regex-based log parser for Fabric 26.2 (Iris/Sodium) and Forge 1.8.9 (LaunchWrapper) crash patterns with Firestore error reporting.
- **Discord RPC Integration**: Live presence with profile name, current instance, and elapsed playtime via `pypresence`.
- **Persistent Window Branding**: Win32 HWND daemon locks title to `SIR Launcher — The Ultimate Minecraft Experience`.
- **Tray Icon Service**: Non-blocking background tray with minimize-to-tray, restore, and quit — excludes WebView2 HWNDs to prevent freeze.
- **Theme System**: Dark Cyber (cyan neon) and Modern OLED (pitch black) themes with RTL Arabic language support.

#### SIR Server Manager (`SIR Server Manager.exe`)
- **Live TPS & RAM Sparklines**: 60-second historical canvas sparkline graphs (cubic bezier) for server TPS (msPT calculation) and heap RAM usage.
- **Restart Scheduler**: `ServerRestartScheduler` broadcasts in-game countdown warnings at 10m, 5m, 1m, 30s, and 10s before clean restart.
- **World Snapshot Auto-Backup**: `prune_world_snapshots()` keeps the last 5 world backups and prunes older `.zip` archives automatically.
- **Discord Webhook Bot**: `post_discord_webhook()` for server start/stop/crash/player-count event notifications to Discord channels.
- **3D Player Studio**: Connected player avatars via Minotar 64px API with moderation actions: OP, De-OP, Whitelist, Kick, Ban, Teleport, Gamemode.
- **1-Click Plugin Store**: Browse and install Paper/Purpur plugins from within the manager UI.
- **Playit.gg QR Tunnel**: Zero-port public server hosting via Playit.gg with QR code modal for mobile sharing.
- **Web Audio Chimes**: System event sound feedback for player join/leave, server start, and warnings.
- **Glassmorphism UI**: Full cyber glassmorphism redesign with OLED dark surfaces and glowing accent borders.

#### SIR Installer (`SIR Installer.exe`)
- **Pre-Flight Diagnostic Matrix**: Validates Disk space (≥ 15 GB), RAM (≥ 4 GB), CPU AVX2 support, Java 21 LTS presence, and write permissions before extraction.
- **Java 21 LTS Auto-Downloader**: Detects missing or below-minimum Java and triggers 1-click Adoptium Java 21 LTS download.
- **Real-Time Throughput Speedometer**: Live MB/s extraction progress, file count, and percentage bar during payload extraction.
- **Custom Drive Selector**: User selects installation drive with remaining free space displayed per drive.
- **Peer Profile Replication**: Auto-replicates `26.2-ultra` to `26.2-balanced` and `26.2-performance` without redundant downloads.
- **URL/Protocol Associations**: Registers `sirlauncher://` deep link protocol on Windows for web-to-launcher profile creation.
- **CRC-32 Archive Validation**: Validates every extracted file's CRC against `delta_manifest.json` before marking install as complete.

---

### 🎮 Minecraft Engine — Modern 26.2 (Fabric 0.19.4)

#### Instance Profiles
- **26.2-ultra**: 221 mods · 6–12 GB RAM · SIR Modern Shader · 144+ FPS target
- **26.2-balanced**: 221 mods · 4–8 GB RAM · SIR Modern Shader · 180+ FPS target
- **26.2-performance**: 221 mods · 3–6 GB RAM · Sodium only (no shader) · 350+ FPS target
- **26.2** (Pure Vanilla): 0 mods · 2–4 GB RAM · Pure Vanilla · 240+ FPS target

#### Performance Mods Stack (Key Mods)
- **Sodium + Indium**: Fully rewritten chunk renderer — up to 400% faster than vanilla Optifine.
- **Lithium**: Server tick optimizer — entity AI, block ticking, and pathfinding overhaul.
- **Starlight**: Complete light engine rewrite — eliminates chunk light lag on chunk generation.
- **FerriteCore**: Reduces Java heap usage by up to 40% via memory layout optimizations.
- **EntityCulling**: GPU-side occlusion culling of off-screen entities.
- **C2ME (Concurrent Chunk Management Engine)**: Multi-threaded chunk generation — `globalExecutorParallelism = 6`, `maxChunkGenerationThreads = 4`.
- **ImmediatelyFast**: Batch renders UI, item frames, signs, armor stands, and text.
- **Nvidium** *(26.2-performance only)*: NVIDIA GPU mesh shading pipeline for extreme FPS uplift.

#### Visual & Shader Mods
- **Iris Shaders**: Full-featured shader loader (toggle: `K`). Ships with `SIR Modern Shader.zip` — custom Complementary Reimagined derivative.
- **Complementary Reimagined** (base shader): PBR materials, volumetric clouds, screen-space GI, PCSS shadows.
- **Continuity**: Connected textures and emissive rendering for glass, bricks, and neon block packs.
- **3D Patrix Resource Pack** (`SIR Modern.zip`): 3D Blockbench POM models with correct UV coordinates (clamped ≤ 16.0).
- **Physics Mod**: Block destruction, particle physics, ragdolls — `maxPhysicsObjects = 450`, `fireParticleLimit = 5000`.
- **Dynamic Lights (LambDynamicLights)**: Held torches, lava buckets, and flaming arrows cast real-time dynamic light.
- **Ambient Sounds 6**: Biome-reactive layered ambient audio engine.
- **Sound Physics Remastered**: Real-room acoustic simulation — `rayCount = 24`, `maxReflectionOrder = 3`, `renderSoundBounces = true`.
- **Presence Footsteps**: Material-sensitive footstep sounds — `terrain_mixing = true`, `armor_shuffle = true`, `global_volume = 0.85`.
- **Puddleflood**: Rain puddle translucent layer integrated with SIR Modern Shader specular reflections (`layer.translucent = puddleflood:puddle`).

#### Gameplay & QoL Mods
- **ReplayMod**: Full session recording/playback. Keybinds: Overview `B`, Marker `M`, Play/Pause `P`, Repo `X`, Path Preview `H`, Position `I`, Time `O`.
- **Xaero's World Map + Minimap**: Persistent world map with waypoints, death markers, and cave mode.
- **BetterF3**: Color-coded, modular debug HUD replacing vanilla F3 overlay.
- **InventoryHUD+**: Configurable item overlay — armor durability, active effects, held item count.
- **Inventory Profiles Next**: Item-sorting hotkeys, locked slots, and auto-refill system.
- **Jade**: Block and entity info popup (WAILA successor) with mod-specific data support.
- **AppleSkin**: Saturation and hunger overlay on the food icon.
- **Chat Heads**: Player face avatars in chat messages via Crafatar API.
- **Punchy**: First-person combat animations — patched for 26.2 (`minecraft: *` wildcard dependency).

#### Multiplayer & Server
- **Essential**: Social layer — friends list, voice chat, item sharing, and cosmetics.
- **Fabric API**: Core Fabric mod lifecycle, event bus, and registry extensions.
- **TagKey crash fix**: Purged `PigPen` and `Runelic` JARs to eliminate `Missing tag TagKey[minecraft:banner_pattern/...]` crash on server join.
- **Smooth Online Compatibility**: Verified joinability on Hypixel, Minemen, and private Purpur/Paper servers.

---

### 🥊 Minecraft Engine — Legacy 1.8.9 (Forge 2318)

#### Instance Profiles
- **1.8.9**: 28 mods · 2–4 GB RAM · No shader · 500+ FPS target
- **1.8.9-ultra**: 28 mods · 3–6 GB RAM · SIR Legacy Shader · 300+ FPS target
- **1.8.9-balanced**: 28 mods · 2–4 GB RAM · SIR Legacy Shader · 450+ FPS target
- **1.8.9-performance**: 28 mods · 1.5–3 GB RAM · No shader (raw OptiFine) · 600+ FPS target

#### PvP & Performance Mods Stack
- **OptiFine HD**: Shader pipeline, connected textures, dynamic lights, and FPS optimization for 1.8.9.
- **SIR Legacy Shader** (`SIR Legacy Shader.zip`): Custom lightweight shader — POM normal maps, subtle volumetric fog, PvP-safe sky.
- **SIR Legacy Resource Pack** (`SIR Legacy.zip`): 32x clean PvP pack — transparent nametags, short swords, FPS-optimized textures.
- **Patcher**: `unfocused_fps = true` (60 FPS cap when window not focused), `static_items = true` (disables item rotation for major PvP FPS gains).
- **Keystrokes Mod**: WASD + mouse button press visualization overlay.
- **In-Game Account Switcher (IAS)**: Switch Minecraft alts mid-session without relaunching.
- **Better Sprinting**: Dual-axis sprint toggle and sneak keybinds.
- **ToggleSneak**: One-press sneak toggle for bridging.
- **Freelook**: `R` key freelook camera without rotating player.
- **Textbook (Ingame Macro)**: Configurable macro scripts for auto-GG, messages, and hotbar management.

#### HUD & Telemetry (Lunar Client Profiles)
- Configured `REACH_DISPLAY` (0.01-block precision), `COMBO` counter, `CPS` left/right meters, `PING`, `TPS` across all 10 Lunar profiles.
- `ARMORSTATUS` with live durability bars, `POTION_EFFECTS` with translucent pill formatting.
- Lunar Memory: 8 GB (Visuals), 6 GB (Balanced), 4 GB (Performance/PvP).
- Low-Latency JVM injection: `-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=20 -XX:+AlwaysPreTouch`.
- Engine optimization: `lazyChunkLoading: true`, `fastMath: true`, `fastRender: true`, `renderRegions: true`.

---

### 🌐 Web Platform — Next.js 16 (`sir-modpack.web.app`)

#### Architecture
- **Framework**: Next.js 16.3.2 with Turbopack — 37 static routes compiled in ~1.7s.
- **Rendering**: 100% static export — zero server compute, CDN-edge delivery via Firebase Hosting.
- **Auth Gate**: `middleware.ts` enforces redirect of all unauthenticated visitors to `/welcome`. Verified via live MCP browser audit — zero bypass.
- **Stack**: React 19 · TypeScript strict · Tailwind CSS 4 · Framer Motion · Lucide React · Firebase Auth/Firestore.

#### Routes & Pages
| Route | Description |
|:------|:------------|
| `/welcome` | Auth entry gate — Google OAuth sign-in landing page |
| `/main` | Authenticated dashboard — quick links, server status, news feed |
| `/download` | Installer & launcher download hub with platform detection |
| `/mods` | Full 221-mod catalog with OLED dark cards, search, and category filters |
| `/builder` | Interactive Modpack Studio — 30+ mods, 6 categories, preset bundles, RAM calculator, JSON export |
| `/compatibility` | GPU Benchmark Station — Tier S–C ratings, 6-profile FPS predictions, feature support matrix |
| `/shaders` | Shader showcase — SIR Modern & SIR Legacy with visual comparison |
| `/packs` | Resource pack browser — SIR Modern 3D POM and SIR Legacy 32x |
| `/profiles` | Instance profile matrix — all 8 profiles with specs and deep links |
| `/skins` | 3D Skin Studio — NameMC search, preview, upload, and wardrobe |
| `/capes` | Cape browser and preview (Optifine, LabyMod, Essential format) |
| `/servers` | Live server radar — ICMP ping, player count, status badges |
| `/server-guide` | Dedicated server setup — Bedrock Cross-Play (GeyserMC), Aikar+ZGC JVM flags, Spark/Chunky commands |
| `/leaderboards` | Esports Top-3 Podium (Gold/Silver/Bronze), category filtering, kill/win stats |
| `/news` | News feed with RSS XML at `/news/index.xml` |
| `/changelog` | This changelog rendered in the web platform |
| `/benchmarks` | GPU tier benchmark results and FPS graphs |
| `/seeds` | Curated Minecraft seed browser with biome previews |
| `/trainer` | PvP technique trainer (CPS, combos, strafing guides) |
| `/crash-analyzer` | Crash log paste-and-analyze tool for Fabric & Forge crash reports |
| `/faq` | Frequently asked questions |
| `/admin` | Admin dashboard — RBAC protected, `admin` role only |
| `/privacy` | Full Privacy Policy (Zero-Telemetry) |
| `/terms` | Terms of Service — Free Independent Software Agreement |
| `/cookies` | Cookie Policy — Firebase Auth session cookies only |
| `/eula` | End User License Agreement — v1.0.0 |
| `/agreements` | Community Platform Agreement |

#### UI/UX Design System
- **Theme**: OLED deep obsidian (`#090e17`) surfaces, cyan neon (`#00e5ff`) accents, emerald success states.
- **Typography**: Geist Sans UI / Geist Mono for code metrics.
- **Motion**: Framer Motion spring physics — `fade-in + zoom-in-95` modal entrances, `active:scale-[0.98]` press mechanics.
- **HCI Compliance**: Fitts's Law (44×44px min targets), Hick-Hyman (single dominant CTA), Doherty Threshold (<400ms feedback).
- **Accessibility**: Full semantic HTML, `aria-label` on all icon buttons, keyboard navigation (Tab/Enter/Escape).
- **5-State Patterns**: Initial, Loading (skeletons), Empty (illustration + CTA), Error (retry trigger), Partial/Overflow on every view.

---

### ☁️ Cloud & Firebase Infrastructure

- **Firebase Auth**: Google OAuth 2.0 sign-in — TLS 1.3. Session persisted in `localStorage` via Firebase SDK.
- **Firestore**: User profiles at `/users/{uid}/` — preferences, bookmarks, scores. Crash diagnostics at `/crash_reports/{id}/`.
- **Firebase Hosting**: CDN edge delivery for all 37 static routes + 265 assets. Zero cold-start latency.
- **Gemini AI Assistant**: In-app chat powered by Gemini API — no persistent personal profile association.
- **Real-Time Broadcast Banner**: Emergency announcements pushed to all connected clients via Firestore listeners.

---

### 🔒 Legal & Compliance Suite

- **LICENSE.md** (`/license`): Free Independent Software Agreement — zero FOSS/GPL/MIT/Apache claims. Community redistribution permitted with attribution.
- **PRIVACY.md** (`/privacy`): Zero-Telemetry Privacy-by-Design — no behavioral tracking, no password storage, no gameplay surveillance. Optional Firebase cloud features with explicit consent.
- **TERMS.md** (`/terms`): Terms of Service — platform identity, permitted use, prohibited actions, liability limitations.
- **COOKIES.md** (`/cookies`): Cookie Policy — only Firebase Auth session cookies set. No third-party advertising cookies.
- **EULA.md** (`/eula`): End User License Agreement — Mojang Studios brand compliance, ASM bytecode modification acknowledgment, no resale clause.
- **AGREEMENTS.md** (`/agreements`): Community Platform Agreement — contributor terms, content standards, and dispute resolution.

---

### 🧪 Quality Assurance

| Suite | Result |
|:------|:-------|
| Unit Tests | **368 / 368 PASSED** — 107.634s — EXIT 0 |
| E2E Adversarial Tests | **39 / 39 CLEARED** (RBAC, payload, rate-limit, SQL injection, XSS) |
| Ecosystem Doctor | **6/6 Diagnostic Layers — 100% HEALTHY** |
| Next.js Build | **37/37 routes — Turbopack — EXIT 0** |
| Firebase Deploy | **265+ assets — Live on sir-modpack.web.app** |
| Drive D Free Space | **18.56 GB ≥ 18.00 GB — invariant maintained** |

---

### 📦 Distribution & Repositories

- **`public_repo`** *(public — GitHub)*: Desktop applications source, installer, server manager, launcher UI, Minecraft instance configs.
- **`website-next`** *(private — GitHub)*: Next.js 16 web platform source — protected by private repository to prevent credential exposure.
- **`SIR_Apps_Suite.zip`**: Self-contained offline bundle of all 3 EXEs + configs for manual distribution.

---

*For support or bug reports, contact: `a7medorabe7@gmail.com`*
*Platform: 100% Free & Independent — Free Independent Software Agreement*
*© 2026 SIR ModPack Ecosystem — NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.*
