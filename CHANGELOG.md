# 📜 SIR ModPack — Official Ecosystem Changelog
### *Unified Minecraft Experience • Semantic Versioning • 100% Free & Independent Platform*

> Changes follow [Semantic Versioning](https://semver.org/): **MAJOR.MINOR.PATCH**
> Contact: `a7medorabe7@gmail.com` • Platform: [sir-modpack.web.app](https://sir-modpack.web.app)

---

## [v1.0.0] — September 8, 2026 — 🏆 Genesis Public Launch

> First complete public release of the SIR ModPack Ecosystem — a production-ready, fully integrated
> suite of desktop apps, dual Minecraft engines, a Next.js 16 web platform, and Firebase cloud infrastructure,
> all under the **Free Independent Software Agreement**.
>
> **368/368 unit tests + 39 E2E adversarial tests — all passing.**

---

### 🖥️ SIR Launcher Pro

- **Direct JVM Launch Pipeline** — native Java 21/25 execution with zero-overhead subprocess management; no wrapper.
- **Generational ZGC Engine** — auto-activates `-XX:+UseZGC -XX:+ZGenerational -XX:ZAllocationSpikeTolerance=5` for Java 21+ with ≥ 6 GB RAM, eliminating micro-stutters during world loading.
- **G1GC Aikar Fallback** — auto-injects `-XX:+ParallelRefProcEnabled -XX:+UseNUMA -XX:+AlwaysPreTouch -XX:MaxGCPauseMillis=20` for legacy Java or ≤ 4 GB systems.
- **Accounts Manager** — full multi-account switcher with Microsoft OAuth2 PKCE loopback auth, offline username validation, and active profile selector.
- **Satellite Social Hub** — online friends presence list, live message stream, direct message composer, and server party invite dispatcher.
- **Profile Creator** — archive extraction (`.zip` / `.mrpack`) with automated migration scanner for PrismLauncher, Lunar Client, and Vanilla `.minecraft` instances.
- **6-Tab Game Settings** — ⚡ Memory & JVM · 🎮 Display & Window (Borderless/Fullscreen) · 🚀 Hardware & GPU (discrete GPU preference) · 🌐 Network & CDN Mesh Routing · 🎨 Visuals & Shaders (Iris K toggle) · 🛡️ Diagnostics & Privacy (Discord RPC, crash auto-report).
- **3D Skin Studio** — real-time OrbitControls WebGL viewer with outer layer toggle, zoom, pan, and drag.
- **Quick Presets Bar** — horizontal scrolling pill buttons for instant one-click profile switching across all 8 profiles.
- **Live Server Radar** — real-time ICMP ping scanner with color-coded latency for all 12 configured servers.
- **Game Integrity Doctor** — CRC-32 validation of the full mod payload against `delta_manifest.json` with self-healing re-download.
- **Win32 RAM Compactor** — calls `EmptyWorkingSet` via `psapi.dll` to flush unused JVM pages without interruption.
- **Launch Console Drawer** — scrollable real-time JVM log output with copy-to-clipboard.
- **First-Time Onboarding Wizard** — 4-step guided setup: Welcome (v1.0.0 Genesis card) → Language & Theme → Google Cloud Auth → Completion.
- **Crash Analyzer** — regex log parser for Fabric 26.2 (Iris/Sodium) and Forge 1.8.9 (LaunchWrapper) patterns with Firestore reporting.
- **Discord RPC** — live presence with profile, instance name, and elapsed playtime via `pypresence`.
- **Persistent Window Branding** — Win32 HWND daemon locks title to `SIR Launcher — The Ultimate Minecraft Experience`.
- **Tray Icon** — non-blocking background tray (minimize / restore / quit); WebView2 HWNDs excluded to prevent freeze.
- **Dual Theme System** — Dark Cyber (cyan neon) and Modern OLED (pitch black) with full RTL Arabic support.
- **Custom Ping Modal** — add and manage server pings with theme-safe `THEMES.get()` lookup (KeyError hardened).
- **Web Sync Modal** — cloud preferences sync with theme-safe lookup (KeyError hardened).

---

### 🖥️ SIR Server Manager

- **Live TPS & RAM Sparklines** — 60-second historical canvas sparkline graphs (cubic bezier) for TPS (msPT) and heap RAM.
- **Restart Scheduler** — `ServerRestartScheduler` broadcasts in-game countdown warnings at 10 min, 5 min, 1 min, 30 s, and 10 s before clean restart.
- **World Snapshot Auto-Backup** — `prune_world_snapshots()` keeps 5 latest world backups and prunes older `.zip` archives.
- **Discord Webhook Bot** — `post_discord_webhook()` for server start / stop / crash / player-count event notifications.
- **3D Player Studio** — connected player Minotar 64px avatars with moderation actions: OP, De-OP, Whitelist, Kick, Ban, Teleport, Gamemode.
- **1-Click Plugin Store** — browse and install Paper / Purpur plugins from within the manager UI.
- **Playit.gg QR Tunnel** — zero-port public hosting via Playit.gg with QR code modal for mobile sharing.
- **Web Audio Chimes** — event sound feedback for player join / leave, server start, and warnings.
- **Glassmorphism UI** — full cyber redesign with OLED dark surfaces and glowing accent borders.

---

### 🖥️ SIR Installer

- **Pre-Flight Diagnostic Matrix** — validates: Disk (≥ 15 GB), RAM (≥ 4 GB), CPU AVX2, Java 21 LTS, write permissions.
- **Java 21 LTS Auto-Downloader** — 1-click Adoptium Java 21 download if missing or below minimum.
- **Real-Time Throughput Speedometer** — live MB/s, file count, and percentage bar during payload extraction.
- **Custom Drive Selector** — user picks installation drive; remaining free space shown per drive.
- **Peer Profile Replication** — auto-replicates `26.2-ultra` to `26.2-balanced` and `26.2-performance`.
- **`sirlauncher://` Deep Link** — registers URL/protocol association on Windows for web-to-launcher profile creation.
- **CRC-32 Validation** — validates every file's CRC against `delta_manifest.json` before marking install complete.

---

### 🎮 Minecraft Engine — Modern 26.2 (Fabric 0.19.4)

#### Instance Profiles
| Profile | Mods | RAM | Shader | FPS Target |
|:--------|:-----|:----|:-------|:-----------|
| 26.2-ultra | 221 | 6–12 GB | SIR Modern Shader | 144+ |
| 26.2-balanced | 221 | 4–8 GB | SIR Modern Shader | 180+ |
| 26.2-performance | 221 | 3–6 GB | OFF (Sodium boost) | 350+ |
| 26.2 (Pure Vanilla) | 0 | 2–4 GB | OFF | 240+ |

#### Performance Core
- **Sodium + Indium** — fully rewritten chunk renderer, up to 400% faster than vanilla/OptiFine.
- **Lithium** — server tick optimizer: entity AI, block ticking, pathfinding.
- **Starlight** — complete light engine rewrite; eliminates chunk light lag.
- **FerriteCore** — reduces heap usage by up to 40% via memory layout optimization.
- **EntityCulling** — GPU-side occlusion culling for off-screen entities.
- **C2ME** — multi-threaded chunk gen: `globalExecutorParallelism = 6`, `maxChunkGenerationThreads = 4`.
- **ImmediatelyFast** — batch renders UI, item frames, signs, armor stands, and text.
- **Nvidium** *(26.2-performance only)* — NVIDIA mesh shading pipeline for extreme FPS uplift.

#### Visuals & Shaders
- **Iris Shaders** — full shader loader (toggle: `K`). Ships `SIR Modern Shader.zip` — custom Complementary Reimagined derivative.
- **Continuity** — connected textures and emissive rendering.
- **3D Patrix Resource Pack** (`SIR Modern.zip`) — Blockbench POM models, UV coordinates clamped ≤ 16.0.
- **Physics Mod** — block destruction, particle physics, ragdolls: `maxPhysicsObjects = 450`, `fireParticleLimit = 5000`.
- **Dynamic Lights (LambDynamicLights)** — held torches, lava buckets, flaming arrows cast real-time light.
- **Ambient Sounds 6** — biome-reactive layered ambient audio.
- **Sound Physics Remastered** — room acoustic simulation: `rayCount = 24`, `maxReflectionOrder = 3`, `renderSoundBounces = true`.
- **Presence Footsteps** — material-sensitive footstep audio: `terrain_mixing = true`, `armor_shuffle = true`, `global_volume = 0.85`.
- **Puddleflood** — rain puddle translucent layer integrated with SIR Modern Shader specular reflections.

#### Gameplay & QoL
- **ReplayMod** — session recording. Keybinds: Overview `B` · Marker `M` · Play/Pause `P` · Repo `X` · Path `H` · Position `I` · Time `O`.
- **Xaero's World Map + Minimap** — persistent map with waypoints, death markers, cave mode.
- **BetterF3** — color-coded modular debug HUD.
- **InventoryHUD+** — armor durability, effects, held item count overlay.
- **Inventory Profiles Next** — item-sort hotkeys, locked slots, auto-refill.
- **Jade** — block/entity info popup (WAILA successor) with mod-specific data.
- **AppleSkin** — saturation and hunger overlay.
- **Chat Heads** — player face avatars in chat via Crafatar API.
- **Punchy** — first-person combat animations; patched for 26.2 (`minecraft: *` wildcard dependency).

#### Multiplayer
- **Essential** — social layer: friends list, voice chat, item sharing, cosmetics.
- **TagKey crash fix** — purged `PigPen` and `Runelic` JARs, resolving `Missing tag TagKey[minecraft:banner_pattern/...]` crash on server join.
- **Verified joinability** — Hypixel, Minemen, private Purpur/Paper servers.

---

### 🥊 Minecraft Engine — Legacy 1.8.9 (Forge 2318)

#### Instance Profiles
| Profile | Mods | RAM | Shader | FPS Target |
|:--------|:-----|:----|:-------|:-----------|
| 1.8.9 | 28 | 2–4 GB | OFF | 500+ |
| 1.8.9-ultra | 28 | 3–6 GB | SIR Legacy Shader | 300+ |
| 1.8.9-balanced | 28 | 2–4 GB | SIR Legacy Shader | 450+ |
| 1.8.9-performance | 28 | 1.5–3 GB | OFF (raw OptiFine) | 600+ |

#### PvP & Performance
- **OptiFine HD** — shader pipeline, connected textures, dynamic lights, FPS optimization.
- **SIR Legacy Shader** (`SIR Legacy Shader.zip`) — lightweight POM shader with PvP-safe sky.
- **SIR Legacy Resource Pack** (`SIR Legacy.zip`) — 32x clean PvP pack; transparent nametags, short swords.
- **Patcher** — `unfocused_fps = true` (60 FPS cap when unfocused), `static_items = true` (disables item rotation for major PvP FPS gains).
- **Keystrokes Mod** — WASD + mouse button press visualization.
- **IAS (In-Game Account Switcher)** — switch Minecraft alts mid-session.
- **Better Sprinting** — dual-axis sprint toggle and sneak keybinds.
- **ToggleSneak** — one-press sneak toggle for bridging.
- **Freelook** — `R` key freelook without rotating player.
- **Textbook (Ingame Macro)** — configurable scripts for auto-GG, messages, hotbar management.

#### HUD & Telemetry (Lunar Client Profiles × 10)
- `REACH_DISPLAY` (0.01-block precision) · `COMBO` counter · `CPS` left/right · `PING` · `TPS`.
- `ARMORSTATUS` with live durability · `POTION_EFFECTS` translucent pill formatting.
- Memory: 8 GB (Visuals) · 6 GB (Balanced) · 4 GB (Performance/PvP).
- JVM injection: `-XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=20 -XX:+AlwaysPreTouch`.
- Engine opts: `lazyChunkLoading: true` · `fastMath: true` · `fastRender: true` · `renderRegions: true`.

---

### 🌐 Web Platform — Next.js 16 (`sir-modpack.web.app`)

#### Architecture
- Next.js 16.3.2 + Turbopack — **37 static routes** compiled in ~1.7s.
- 100% static export — zero server compute, Firebase Hosting CDN delivery.
- `middleware.ts` auth gate — all unauthenticated visitors → `/welcome`. Zero bypass (live MCP verified).
- Stack: React 19 · TypeScript strict · Tailwind CSS 4 · Framer Motion · Lucide React · Firebase Auth/Firestore.

#### All Routes
| Route | Description |
|:------|:------------|
| `/welcome` | Auth entry gate — Google OAuth sign-in |
| `/main` | Authenticated dashboard — quick links, server status, news |
| `/download` | Installer & launcher download hub with platform detection |
| `/mods` | 221-mod catalog with OLED dark cards, search, category filters |
| `/builder` | Modpack Studio — 30+ mods, 6 categories, preset bundles, RAM calculator, JSON export, deep link |
| `/compatibility` | GPU Benchmark Station — Tier S–C, 6-profile FPS predictions, feature support matrix |
| `/shaders` | Shader showcase — SIR Modern & SIR Legacy with visual comparison |
| `/packs` | Resource pack browser — SIR Modern 3D POM and SIR Legacy 32x |
| `/profiles` | Instance profile matrix — all 8 profiles with specs |
| `/skins` | 3D Skin Studio — NameMC search, preview, upload, wardrobe |
| `/capes` | Cape browser and preview (OptiFine, LabyMod, Essential) |
| `/servers` | Live server radar — ICMP ping, player count, status badges |
| `/server-guide` | Server setup — Bedrock Cross-Play (GeyserMC), Aikar+ZGC JVM flags, Spark/Chunky commands |
| `/leaderboards` | Esports Top-3 Podium (Gold/Silver/Bronze), category filtering |
| `/news` | News feed with RSS at `/news/index.xml` |
| `/changelog` | This changelog rendered on the web |
| `/benchmarks` | GPU tier benchmark results |
| `/seeds` | Minecraft seed browser with biome previews |
| `/trainer` | PvP technique trainer — CPS, combos, strafing guides |
| `/crash-analyzer` | Paste-and-analyze crash logs for Fabric & Forge |
| `/faq` | Frequently asked questions |
| `/admin` | Admin dashboard — RBAC protected, `admin` role only |
| `/privacy` | Privacy Policy — Zero-Telemetry |
| `/terms` | Terms of Service |
| `/cookies` | Cookie Policy |
| `/eula` | End User License Agreement |
| `/agreements` | Community Platform Agreement |

#### UI / Design System
- OLED deep obsidian (`#090e17`) surfaces · cyan neon (`#00e5ff`) accents · emerald success states.
- Framer Motion spring physics — `fade-in + zoom-in-95` modal entrances, `active:scale-[0.98]` press mechanics.
- HCI-compliant: Fitts's Law (44×44px min targets) · Hick-Hyman (single primary CTA) · Doherty Threshold (<400ms feedback).
- Full semantic HTML · `aria-label` on all icon buttons · keyboard navigation (Tab / Enter / Escape).
- 5-state patterns on every view: Initial · Loading (skeleton) · Empty (illustration + CTA) · Error (retry) · Overflow.

---

### ☁️ Firebase Cloud Infrastructure

- **Firebase Auth** — Google OAuth 2.0, TLS 1.3, session persisted via Firebase SDK.
- **Firestore** — user profiles `/users/{uid}/` (preferences, bookmarks, scores) · crash reports `/crash_reports/{id}/`.
- **Firebase Hosting** — CDN edge delivery for 37 static routes + 265 assets. Zero cold-start.
- **Gemini AI Assistant** — in-app chat via Gemini API, no persistent personal profile association.
- **Real-Time Broadcast Banner** — emergency announcements pushed to all clients via Firestore listeners.

---

### 🔒 Legal Suite

| Document | Description |
|:---------|:------------|
| [`LICENSE.md`](LICENSE.md) | Free Independent Software Agreement — zero FOSS/GPL/MIT/Apache claims |
| [`PRIVACY.md`](PRIVACY.md) | Zero-Telemetry Privacy-by-Design — no tracking, no password storage |
| [`TERMS.md`](TERMS.md) | Terms of Service — permitted use, prohibited actions, liability |
| [`COOKIES.md`](COOKIES.md) | Cookie Policy — Firebase Auth session cookies only, zero advertising cookies |
| [`EULA.md`](EULA.md) | End User License Agreement — Mojang brand compliance, ASM acknowledgment |
| [`AGREEMENTS.md`](AGREEMENTS.md) | Community Platform Agreement — contributor terms, dispute resolution |

---

### 🧪 Quality Assurance

| Suite | Result |
|:------|:-------|
| Unit Tests | **368 / 368 PASSED** — 107.634s — EXIT 0 |
| E2E Adversarial Tests | **39 / 39 CLEARED** — RBAC · payload · rate-limit · injection · XSS |
| Ecosystem Doctor | **6 / 6 Diagnostic Layers — 100% HEALTHY** |
| Delta Manifest Validator | **2783 / 2783 files — 100% VALID** — 5.41 GB hash-verified |
| Next.js Build | **37 / 37 routes — Turbopack — EXIT 0** |
| Firebase Deploy | **265 assets → `https://sir-modpack.web.app`** |
| Drive D Free Space | **18.56 GB ≥ 18.00 GB — invariant maintained** |

---

### 📦 Distribution

| Repository | Visibility | Contents |
|:-----------|:-----------|:---------|
| `public_repo` | **Public** | Desktop apps source, installer, server manager, launcher UI, Minecraft instance configs, docs |
| `website-next` | **Private** | Next.js 16 web platform source |
| `SIR_Apps_Suite.zip` | Offline bundle | All 3 compiled EXEs + configs for manual distribution |

---

*Contact: `a7medorabe7@gmail.com`*
*© 2026 SIR ModPack Ecosystem — NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.*
