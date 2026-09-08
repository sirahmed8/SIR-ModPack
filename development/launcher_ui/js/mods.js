// =============================================================================
// 2. MODS & ONLINE STORE HUB RENDERER
// =============================================================================
STATE.mods = [];
STATE.modCategory = "all";
STATE.modSearchQuery = "";

function selectModCategoryDropdown(cat, label) {
  STATE.modCategory = cat;
  const labelEl = document.getElementById('mod-category-label');
  if (labelEl) labelEl.textContent = label;
  
  // Highlight active dropdown option
  const opts = document.querySelectorAll('#mod-category-menu .dropdown-opt');
  opts.forEach(opt => {
    if (opt.textContent.trim().includes(cat) || (cat === 'All' && opt.textContent.includes('All Categories'))) {
      opt.className = "dropdown-opt flex items-center justify-between px-3 py-2 text-xs font-bold rounded-xl cursor-pointer transition-all bg-cyan-500/15 text-cyan-400 border border-cyan-500/30";
      if (!opt.querySelector('i')) {
        const icon = document.createElement('i');
        icon.setAttribute('data-lucide', 'check');
        icon.className = 'w-3.5 h-3.5 text-cyan-400';
        opt.appendChild(icon);
      }
    } else {
      opt.className = "dropdown-opt flex items-center justify-between px-3 py-2 text-xs font-bold rounded-xl cursor-pointer transition-all text-slate-300 hover:bg-slate-800/80 hover:text-white";
      const check = opt.querySelector('i');
      if (check) check.remove();
    }
  });

  const menu = document.getElementById('mod-category-menu');
  if (menu) menu.classList.add('hidden');
  
  renderMods();
  refreshLucideIcons();
}

function filterModCategory(cat) {
  selectModCategoryDropdown(cat, cat === 'All' ? 'All Categories' : cat);
}

function handleModSearch(query) {
  STATE.modSearchQuery = (query || "").toLowerCase().trim();
  renderMods();
}

STATE.modsLoading = false;

async function loadModsFromBridge() {
  STATE.modsLoading = true;
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = (STATE.selectedInstanceId && STATE.selectedInstanceId !== '26.2') ? STATE.selectedInstanceId : '26.2-ultra';
      const realMods = await window.pywebview.api.get_mods(activeInst, '', 'All');
      if (Array.isArray(realMods)) {
        STATE.mods = realMods;
      }
    } catch (e) {
      console.warn('Error loading real mods:', e);
    } finally {
      STATE.modsLoading = false;
    }
  } else {
    STATE.modsLoading = false;
  }
  renderMods();
}

const SIR_MODS_DOCS = {
  sir_core: {
    title: "SIR Core Engine",
    version: "v1.0.0 Pro",
    author: "Sir Ahmed & Engineering Team",
    icon: "cpu",
    iconColor: "text-cyan-400",
    badge: "🌟 Official Ecosystem Core",
    weblink: "https://sir-modpack.web.app/mods?doc=sir_core",
    desc: "The heartbeat of the SIR Ecosystem. SIR Core provides high-frequency asynchronous asset healing, dynamic JVM RAM compaction, 3-way shader/resource pack optical synergy, and automatic power mode governance.",
    architecture: `
      <div class="p-3.5 rounded-2xl bg-cyan-950/30 border border-cyan-500/30 space-y-2">
        <h4 class="text-xs font-bold text-cyan-300 flex items-center gap-1.5"><i data-lucide="layers" class="w-3.5 h-3.5"></i> Architecture & Core Systems</h4>
        <ul class="space-y-1.5 text-[11px] text-slate-300">
          <li><strong>• Asynchronous Asset Auto-Healer:</strong> Scans instances prior to knot launch, validating sha256 checksums and automatically retrieving missing dependencies in under 3 seconds.</li>
          <li><strong>• Dynamic RAM Compactor:</strong> Triggers aggressive garbage collection compacting unreferenced heap segments during world transitions, reducing memory footprint by up to 45%.</li>
          <li>• 3-Way Shader/POM Synergy: Injects direct normal and specular hooks bridging Iris/Sodium with SIR Modern Shader optical passes for zero-glitch 3D Parallax Occlusion Mapping.</li>
          <li>• Win32 Hardware Governor: Bridges CPU affinity masks, thread pools, and process priority flags ('Turbo' vs 'Eco').</li>
        </ul>
      </div>
    `,
    configs: [
      { key: "enableAutoHealing", val: "true", desc: "Verifies and restores missing jars/configs before launch" },
      { key: "memoryCompactionIntervalSeconds", val: "180", desc: "Background heap compaction cycle frequency" },
      { key: "shaderSynergyHooks", val: "true", desc: "Direct Iris/SIR Modern GLSL optical pass alignment" },
      { key: "hardwarePowerMode", val: "TURBO", desc: "Process priority: TURBO (High) / ECO (BelowNormal)" }
    ],
    hotkeys: ["F4: Cycle Optical Shaders", "F8: Force Garbage Collection", "F10: Toggle In-Game HUD Diagnostics"]
  },
  havoc_pvp: {
    title: "HAVOC PvP Injector & Kernel Engine",
    version: "v1.0.0",
    author: "HAVOC Core Team",
    icon: "swords",
    iconColor: "text-rose-400",
    badge: "⚔️ Competitive PvP Engine",
    weblink: "https://sir-modpack.web.app/mods?doc=havoc_pvp",
    desc: "Engineered specifically for competitive 1.8.9 Bedwars, Nodebuff, and Modern 26.2 sword mechanics. HAVOC minimizes input latency to 0ms and provides deterministic hit registration.",
    architecture: `
      <div class="p-3.5 rounded-2xl bg-rose-950/30 border border-rose-500/30 space-y-2">
        <h4 class="text-xs font-bold text-rose-300 flex items-center gap-1.5"><i data-lucide="zap" class="w-3.5 h-3.5"></i> Competitive Hit Engine</h4>
        <ul class="space-y-1.5 text-[11px] text-slate-300">
          <li><strong>• 0ms Direct Polling:</strong> Bypasses Windows standard USB polling delays, delivering instant click-to-packet transmission.</li>
          <li><strong>• Hitbox Smoothing:</strong> Client-side interpolation prevents phantom misses during high-velocity strafing and combo chaining.</li>
          <li><strong>• Anti-Cheat Safe:</strong> 100% compliant with Hypixel, GommeHD, and MinemenClub packet cadence standards.</li>
        </ul>
      </div>
    `,
    configs: [
      { key: "rawMouseInput", val: "true", desc: "Bypasses OS acceleration curves for 1:1 mouse precision" },
      { key: "hitboxTraceCorrection", val: "true", desc: "Smooths client packet timing during sprint resets" },
      { key: "customHitParticles", val: "true", desc: "Renders crisp high-contrast hit sparks without particle lag" }
    ],
    hotkeys: ["R: Toggle Reach Visualizer", "V: Toggle Sprint Hold", "C: In-Game Combat Calibration Menu"]
  },
  super_secret_settings: {
    title: "Super Secret Settings Fix",
    version: "v1.0.0",
    author: "PrideSyria & SIR Team",
    icon: "sparkles",
    iconColor: "text-purple-400",
    badge: "🎨 Classic Optical Filters",
    weblink: "https://sir-modpack.web.app/mods?doc=super_secret_settings",
    desc: "Restores the iconic Minecraft 1.8.9 'Super Secret Settings' GLSL post-processing shaders and retro filters directly into Modern Minecraft 26.2 without performance overhead.",
    architecture: `
      <div class="p-3.5 rounded-2xl bg-purple-950/30 border border-purple-500/30 space-y-2">
        <h4 class="text-xs font-bold text-purple-300 flex items-center gap-1.5"><i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Retro Post-Processing Suite</h4>
        <ul class="space-y-1.5 text-[11px] text-slate-300">
          <li><strong>• 16 Classic Filters:</strong> Phosphor CRT, Sobel Outline, 8-Bit Pixelate, Desaturate, Invert, Blur, and Scanlines.</li>
          <li><strong>• Iris & Sodium Compatible:</strong> Executes downstream of the rasterizer pipeline without causing framebuffer conflicts.</li>
        </ul>
      </div>
    `,
    configs: [
      { key: "activeFilter", val: "none", desc: "Currently active post-processing pipeline pass" },
      { key: "allowShaderPassInShaders", val: "true", desc: "Allows chaining retro filters on top of SIR Modern Shaders" }
    ],
    hotkeys: ["F4: Cycle to Next Secret Shader Filter", "Shift + F4: Reset Optical Filters to None"]
  },
  player_api: {
    title: "PlayerAPI Integration",
    version: "v1.8.9 / 26.2",
    author: "PrideSyria & SIR Team",
    icon: "activity",
    iconColor: "text-emerald-400",
    badge: "🏃 Kinematics & Animations Hub",
    weblink: "https://sir-modpack.web.app/mods?doc=player_api",
    desc: "Player model kinematics framework powering 3D skin layer depth physics, dynamic swimming and crawling poses, and classic 1.7 sword blockhitting fluidity.",
    architecture: `
      <div class="p-3.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/30 space-y-2">
        <h4 class="text-xs font-bold text-emerald-300 flex items-center gap-1.5"><i data-lucide="activity" class="w-3.5 h-3.5"></i> Kinematics Framework</h4>
        <ul class="space-y-1.5 text-[11px] text-slate-300">
          <li><strong>• 3D Skin Depth Extrusion:</strong> Renders skin hats, jackets, and sleeves with physical voxel thickness and natural physics.</li>
          <li><strong>• 1.7 Blockhit Interpolator:</strong> Restores smooth simultaneous sword swinging and blocking animations.</li>
        </ul>
      </div>
    `,
    configs: [
      { key: "blockhitAnimation", val: "CLASSIC_1_7", desc: "Sword swing & block animation model" },
      { key: "skinLayer3DDepth", val: "1.25px", desc: "Voxel depth extrusion for player skin outerwear" }
    ],
    hotkeys: ["K: Toggle Dynamic Emotes Menu", "H: Toggle First-Person Hand Model Animation"]
  },
  sharpness_particles: {
    title: "Sharpness Particles FX",
    version: "v1.8.9 / 26.2",
    author: "PrideSyria & SIR Team",
    icon: "zap",
    iconColor: "text-amber-400",
    badge: "✨ Particle Burst Suite",
    weblink: "https://sir-modpack.web.app/mods?doc=sharpness_particles",
    desc: "High-contrast critical hit and sharpness particle renderer with asynchronous particle pooling, zero frame drops, and customizable color hues.",
    architecture: `
      <div class="p-3.5 rounded-2xl bg-amber-950/30 border border-amber-500/30 space-y-2">
        <h4 class="text-xs font-bold text-amber-300 flex items-center gap-1.5"><i data-lucide="zap" class="w-3.5 h-3.5"></i> High-Speed Particle Pool</h4>
        <ul class="space-y-1.5 text-[11px] text-slate-300">
          <li><strong>• Particle Memory Pooling:</strong> Pre-allocates particle memory buffers to prevent Java GC spikes during intense PvP fights.</li>
          <li><strong>• Vibrant Sharpness Glow:</strong> Emits bright cyan/gold sparks on critical hits with adjustable density.</li>
        </ul>
      </div>
    `,
    configs: [
      { key: "particleMultiplier", val: "1.5x", desc: "Particle count density per critical strike" },
      { key: "particleHueMode", val: "DYNAMIC_NEON", desc: "Color mode: DYNAMIC_NEON / CLASSIC_SHARP / CRIT_GOLD" }
    ],
    hotkeys: ["P: Toggle Particle Density (1x / 2x / 3x / Off)"]
  },
  ias_switcher: {
    title: "InGameAccountSwitcher (IAS)",
    version: "v9.0.7",
    author: "The_Fireplace",
    icon: "users",
    iconColor: "text-blue-400",
    badge: "🔑 Offline & Alt Switcher",
    weblink: "https://sir-modpack.web.app/mods?doc=ias_switcher",
    desc: "Allows hot-swapping between Offline / Cracked profiles and Microsoft accounts directly inside Minecraft menus without closing the game client.",
    architecture: `
      <div class="p-3.5 rounded-2xl bg-blue-950/30 border border-blue-500/30 space-y-2">
        <h4 class="text-xs font-bold text-blue-300 flex items-center gap-1.5"><i data-lucide="users" class="w-3.5 h-3.5"></i> Hot-Swap Session Token Engine</h4>
        <ul class="space-y-1.5 text-[11px] text-slate-300">
          <li><strong>• In-Game GUI Overlay:</strong> Accessible directly from the main menu and multiplayer server list.</li>
          <li><strong>• Zero Client Restart:</strong> Re-authenticates Yggdrasil session tokens on the fly in milliseconds.</li>
          <li><strong>• Encrypted Storage:</strong> Persists offline and Microsoft tokens securely in local AES-256 encrypted storage.</li>
        </ul>
      </div>
    `,
    configs: [
      { key: "storeLocalOfflineAccounts", val: "true", desc: "Persists cracked usernames across game launches" },
      { key: "autoRelogServerOnSwitch", val: "true", desc: "Reconnects to active multiplayer server with new identity" }
    ],
    hotkeys: ["Main Menu -> Click 'Accounts' button (Top Left)"]
  }
};

function openModDocumentationModal(modId) {
  const doc = SIR_MODS_DOCS[modId] || SIR_MODS_DOCS.sir_core;
  const modal = document.getElementById('mod-docs-modal');
  if (!modal) return;

  const titleEl = document.getElementById('docs-modal-title');
  const badgeEl = document.getElementById('docs-modal-badge');
  const authorEl = document.getElementById('docs-modal-author');
  const iconEl = document.getElementById('docs-modal-icon');
  const weblinkEl = document.getElementById('docs-modal-weblink');
  const bodyEl = document.getElementById('docs-modal-body');

  if (titleEl) titleEl.textContent = doc.title;
  if (badgeEl) badgeEl.textContent = doc.badge;
  if (authorEl) authorEl.textContent = `${doc.version} • by ${doc.author}`;
  if (iconEl) iconEl.setAttribute('data-lucide', doc.icon);
  if (weblinkEl) weblinkEl.href = doc.weblink;

  if (bodyEl) {
    bodyEl.innerHTML = `
      <p class="text-xs text-slate-200 leading-relaxed font-medium">${escapeHtml(doc.desc)}</p>
      ${doc.architecture}
      
      <div class="space-y-2">
        <h4 class="text-xs font-bold text-white flex items-center gap-1.5">
          <i data-lucide="sliders" class="w-3.5 h-3.5 text-cyan-400"></i>
          <span>Configuration Keys & Parameters</span>
        </h4>
        <div class="space-y-1.5 font-mono text-[10px]">
          ${doc.configs.map(c => `
            <div class="p-2 rounded-xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
              <span class="text-cyan-300 font-bold">${escapeHtml(c.key)}: <span class="text-emerald-400">${escapeHtml(c.val)}</span></span>
              <span class="text-slate-400">${escapeHtml(c.desc)}</span>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="space-y-2">
        <h4 class="text-xs font-bold text-white flex items-center gap-1.5">
          <i data-lucide="keyboard" class="w-3.5 h-3.5 text-amber-400"></i>
          <span>In-Game Hotkeys & Controls</span>
        </h4>
        <div class="flex flex-wrap gap-2">
          ${doc.hotkeys.map(hk => `
            <span class="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-[10px] font-mono text-slate-300 font-bold">${escapeHtml(hk)}</span>
          `).join('')}
        </div>
      </div>
    `;
  }

  modal.classList.remove('hidden');
  modal.style.display = 'flex';
  modal.scrollTop = 0;
  refreshLucideIcons();
}
window.openModDocumentationModal = openModDocumentationModal;

function closeModDocsModal() {
  const modal = document.getElementById('mod-docs-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}
window.closeModDocsModal = closeModDocsModal;

const OFFICIAL_SIR_MODS = [
  {
    id: "sir_core",
    name: "SIR Core",
    version: "1.0.0",
    category: "Core Engine",
    badge: "🌟 Official Ecosystem Core",
    author: "Sir Ahmed & Team",
    gradient: "from-cyan-950/60 via-blue-900/40 to-slate-900/90",
    icon: "cpu",
    iconColor: "text-cyan-400",
    desc: "Official core ecosystem mod for SIR Ultimate. Features 3-Way Shader/POM synergy, JVM Memory Governor daemon, and Win32 hardware power acceleration.",
    features: ["Auto Memory Compactor", "3-Way Shader/Pack Synergy", "Telemetry & Hardware Bridge", "Zero Micro-Stutter Engine"],
    link: "https://sir-modpack.web.app/mods"
  },
  {
    id: "havoc_pvp",
    name: "HAVOC PvP Injector & Kernel Engine",
    version: "1.0.0",
    category: "PvP Engine",
    badge: "⚔️ Competitive PvP",
    author: "HAVOC Team",
    gradient: "from-rose-950/60 via-red-900/40 to-slate-900/90",
    icon: "swords",
    iconColor: "text-rose-400",
    desc: "Next-gen tournament PvP engine featuring instant click response, velocity smoothing, and client-side reach tracer optimization.",
    features: ["Instant Hit Registration", "0ms Click Input Polling", "Reach Visualizer", "Low Latency Netcode"],
    link: "https://sir-modpack.web.app"
  },
  {
    id: "super_secret_settings",
    name: "Super Secret Settings Fix",
    version: "1.0.0",
    category: "Visuals",
    badge: "🎨 Classic Optical Filters",
    author: "PrideSyria",
    gradient: "from-purple-950/60 via-indigo-900/40 to-slate-900/90",
    icon: "sparkles",
    iconColor: "text-purple-400",
    desc: "Restores classic Minecraft retro post-processing shaders, CRT filters, and secret visual camera passes seamlessly.",
    features: ["Post-Processing Restorer", "Retro CRT & 8-Bit Shaders", "Smooth Camera FX", "Zero Performance Cost"],
    link: "https://sir-modpack.web.app/shaders"
  },
  {
    id: "player_api",
    name: "PlayerAPI Integration",
    version: "1.8.9",
    category: "Animations",
    badge: "🏃 Player Movement Hub",
    author: "PrideSyria",
    gradient: "from-emerald-950/60 via-teal-900/40 to-slate-900/90",
    icon: "activity",
    iconColor: "text-emerald-400",
    desc: "Core animation and player model framework enabling 3D skin layers, custom crawling, fluid swimming, and 1.7 blockhit animations.",
    features: ["1.7 Sword Fluidity", "3D Skin Extrusions", "Dynamic Crawling & Swimming", "EMF Compatibility"],
    link: "https://sir-modpack.web.app"
  },
  {
    id: "sharpness_particles",
    name: "Sharpness Particles FX",
    version: "1.8.9",
    category: "PvP Visuals",
    badge: "✨ Particle Burst",
    author: "PrideSyria",
    gradient: "from-amber-950/60 via-yellow-900/40 to-slate-900/90",
    icon: "zap",
    iconColor: "text-amber-400",
    desc: "Vibrant high-contrast critical hit and sharpness particle effects with zero particle lag or FPS reduction.",
    features: ["Custom PvP Hit Particles", "No-Lag Particle Buffer", "Adjustable Intensity", "Hypixel Safe"],
    link: "https://sir-modpack.web.app"
  },
  {
    id: "ias_switcher",
    name: "InGameAccountSwitcher (IAS)",
    version: "9.0.7",
    category: "Accounts",
    badge: "🔑 Offline & Alt Switcher",
    author: "The_Fireplace",
    gradient: "from-blue-950/60 via-slate-900/40 to-slate-900/90",
    icon: "users",
    iconColor: "text-blue-400",
    desc: "Seamlessly switch between Microsoft and Cracked/Offline accounts directly in-game without closing Minecraft.",
    features: ["In-Game Switcher GUI", "Offline & Microsoft Alts", "Skin & Cape Preserver", "Encrypted Local Storage"],
    link: "https://sir-modpack.web.app/accounts"
  }
];

function renderMods() {
  const container = document.getElementById('mods-grid');
  if (!container) return;

  const countBadge = document.getElementById('mods-count-badge');
  const btnSpan = document.querySelector('#btn-subtab-installed span');
  const isVanilla = STATE.selectedInstanceId === '26.2' || (STATE.selectedInstanceId && STATE.selectedInstanceId.includes('vanilla'));

  const activeCount = STATE.mods.filter(m => m.enabled !== false).length;
  const totalCount = STATE.mods.length;

  if (isVanilla) {
    if (countBadge) countBadge.textContent = `0 Mods (Pure Vanilla Active)`;
    if (btnSpan) btnSpan.textContent = `Installed (0)`;
    container.innerHTML = `
      <div class="col-span-full text-center py-16 px-6 feature-card rounded-3xl border border-emerald-500/20 bg-emerald-950/10 space-y-3">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10">
          <i data-lucide="leaf" class="w-7 h-7"></i>
        </div>
        <h3 class="text-base font-black text-slate-100">🌿 Pure Clean Vanilla Profile Active</h3>
        <p class="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          This profile is running official unmodded Minecraft 26.2. No mods or visual overhauls are loaded. You can switch to an Enhanced SIR profile (Visuals, Balanced, or Performance) from Quick Presets to play with mods.
        </p>
      </div>
    `;
    refreshLucideIcons();
    return;
  }

  if (STATE.modsLoading && totalCount === 0) {
    const preCount = window.__SIR_MODS_COUNT_PRE_HYDRATE__ || 228;
    if (countBadge) countBadge.textContent = `Scanning ${preCount}+ Mods...`;
    if (btnSpan) btnSpan.textContent = `Installed (${preCount}+)`;
    container.innerHTML = `
      <div class="col-span-full py-16 px-6 flex flex-col items-center justify-center space-y-4">
        <div class="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
          <i data-lucide="loader-2" class="w-6 h-6 animate-spin"></i>
        </div>
        <div class="text-center space-y-1">
          <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200">Cataloging ${preCount}+ Active Mods...</h4>
          <p class="text-xs text-slate-500 dark:text-slate-400">Verifying bytecode, shaders, and fabric dependencies</p>
        </div>
      </div>
    `;
    refreshLucideIcons();
    return;
  }

  if (countBadge) countBadge.textContent = `${activeCount} Active Mods`;
  if (btnSpan) btnSpan.textContent = `Installed (${totalCount})`;

  const isLight = document.documentElement.classList.contains('light');

  const filtered = STATE.mods.filter(m => {
    const isAll = !STATE.modCategory || STATE.modCategory.toLowerCase() === 'all';
    const matchCat = isAll || (m.category && m.category.toLowerCase() === STATE.modCategory.toLowerCase());
    const matchSearch = !STATE.modSearchQuery || 
      (m.name && m.name.toLowerCase().includes(STATE.modSearchQuery)) || 
      (m.desc && m.desc.toLowerCase().includes(STATE.modSearchQuery)) ||
      (m.filename && m.filename.toLowerCase().includes(STATE.modSearchQuery));
    return matchCat && matchSearch;
  });

  // Render Official SIR Mods Highlight Cards (High-Contrast Deep Cyber Theme)
  const sirCardsHtml = OFFICIAL_SIR_MODS.map(s => {
    return `
      <div class="col-span-full md:col-span-1 p-4 rounded-2xl official-mod-card ${s.id} flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="badge-tag text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 border border-cyan-200 dark:border-cyan-500/40">${escapeHtml(s.badge)}</span>
            <span class="text-[9px] font-mono text-slate-500 dark:text-slate-400 font-bold">v${escapeHtml(s.version)}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-black/60 border border-slate-200 dark:border-white/10 flex items-center justify-center ${s.iconColor} shrink-0 shadow-md">
              <i data-lucide="${s.icon}" class="w-4 h-4"></i>
            </div>
            <div class="min-w-0 flex-1">
              <h4 class="text-xs font-black text-slate-900 dark:text-white truncate">${escapeHtml(s.name)}</h4>
              <p class="text-[10px] text-cyan-600 dark:text-cyan-400 font-mono font-semibold">By ${escapeHtml(s.author)}</p>
            </div>
          </div>
          <p class="text-[11px] text-slate-600 dark:text-slate-300 mt-2 line-clamp-2 leading-relaxed">${escapeHtml(s.desc)}</p>
        </div>
        <div class="mt-3 pt-2.5 border-t border-slate-200 dark:border-white/10 flex items-center justify-between">
          <span class="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1">● Pre-Installed &amp; Active</span>
          <button onclick="openModDocumentationModal('${s.id}')" class="px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-[11px] font-black shadow-md shadow-cyan-500/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer">
            <i data-lucide="book-open" class="w-3.5 h-3.5"></i>
            <span>Documentation</span>
          </button>
        </div>
      </div>
    `;
  }).join('');

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full mb-4">
        <h3 class="text-xs font-black text-cyan-400 uppercase tracking-widest mb-3 flex items-center gap-2">
          <i data-lucide="sparkles" class="w-4 h-4"></i>
          <span>Official SIR Custom Suite</span>
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
          ${sirCardsHtml}
        </div>
      </div>
      <div class="col-span-full feature-card p-8 text-center border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 text-slate-900 dark:text-slate-100">
        <p class="text-xs text-slate-500 dark:text-slate-400">${STATE.mods.length === 0 ? 'No additional third-party mods installed yet. Drop JARs above or browse the Online Store!' : 'No other installed mods match your search query.'}</p>
        ${STATE.mods.length > 0 ? '<button onclick="filterModCategory(\'All\')" class="mt-3 px-4 py-1.5 rounded-xl bg-cyan-500 text-slate-950 text-xs font-bold">Show All Mods</button>' : ''}
      </div>
    `;
    refreshLucideIcons();
    return;
  }

  const normalModsHtml = filtered.map(mod => `
    <div class="feature-card p-4 rounded-2xl border transition-all bg-white dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 text-slate-900 dark:text-slate-100 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3.5 min-w-0 flex-1">
        <div class="w-10 h-10 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center shrink-0 overflow-hidden shadow-sm">
          ${mod.icon_url ? `
            <img src="${mod.icon_url}" class="w-full h-full object-cover" onerror="this.onerror=null; this.parentElement.innerHTML='<i data-lucide=\\'package\\' class=\\'w-5 h-5 text-cyan-400\\'></i>'; if(window.lucide) lucide.createIcons();" alt="${escapeHtml(mod.name)}">
          ` : `
            <i data-lucide="${mod.category === 'Performance' ? 'zap' : mod.category === 'Visuals' ? 'sun' : mod.category === 'PvP' ? 'swords' : mod.category === 'Audio' ? 'volume-2' : 'package'}" class="w-5 h-5 ${mod.category === 'Performance' ? 'text-emerald-400' : mod.category === 'Visuals' ? 'text-cyan-400' : mod.category === 'PvP' ? 'text-amber-400' : 'text-slate-400'}"></i>
          `}
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h4 class="text-xs font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(mod.name.replace(/_/g, ' '))}</h4>
            ${mod.author ? `<span class="text-[10px] text-slate-400 font-mono">by ${escapeHtml(mod.author)}</span>` : ''}
            <span class="badge-tag text-[9px] px-2 py-0.5 rounded-full font-semibold ${
              mod.category === 'Performance' ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' :
              mod.category === 'Visuals' ? 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30' :
              mod.category === 'PvP' ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border border-amber-500/30' :
              'bg-slate-500/15 text-slate-600 dark:text-slate-300 border border-slate-500/30'
            }">${mod.category || 'Utility'}</span>
            <span class="text-[9px] font-mono text-slate-400">v${mod.version || '1.0'}</span>
          </div>
          <p class="text-[11px] text-slate-600 dark:text-slate-400 mt-1 line-clamp-1">${escapeHtml(mod.desc || 'Optimized modular package.')}</p>
        </div>
      </div>
      <label class="relative inline-flex items-center cursor-pointer shrink-0">
        <input type="checkbox" ${mod.enabled ? 'checked' : ''} onchange="toggleMod('${mod.filename || mod.id}', this.checked)" class="sr-only peer">
        <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-500"></div>
      </label>
    </div>
  `).join('');

  container.innerHTML = `
    <div class="col-span-full mb-2">
      <h3 class="text-xs font-black text-cyan-400 uppercase tracking-widest mb-3 flex items-center gap-2">
        <i data-lucide="sparkles" class="w-4 h-4"></i>
        <span>Official SIR Custom Suite</span>
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
        ${sirCardsHtml}
      </div>
      <h3 class="text-xs font-black text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
        <i data-lucide="package" class="w-4 h-4"></i>
        <span>Installed Engine Mods (${filtered.length})</span>
      </h3>
    </div>
    ${normalModsHtml}
  `;

  refreshLucideIcons();
}

function showDependencyPromptModal(modName, missingList, onConfirm) {
  let modal = document.getElementById('mod-dependency-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'mod-dependency-modal';
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md hidden';
    document.body.appendChild(modal);
  }

  const listHtml = missingList.map(item => `
    <div class="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800">
      <div class="flex items-center gap-2">
        <i data-lucide="package-plus" class="w-4 h-4 text-cyan-400"></i>
        <span class="text-xs font-bold text-white">${escapeHtml(item.name || item.id)}</span>
      </div>
      <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold ${item.action === 'enable' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'}">
        ${item.action === 'enable' ? 'Requires Enabling' : 'Requires Install'}
      </span>
    </div>
  `).join('');

  modal.innerHTML = `
    <div class="w-full max-w-md bg-slate-950 border border-cyan-500/30 rounded-3xl p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95 duration-200">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-cyan-500/20 flex items-center justify-center text-cyan-400">
          <i data-lucide="alert-triangle" class="w-5 h-5"></i>
        </div>
        <div>
          <h3 class="text-sm font-black text-white">Missing Mod Dependencies</h3>
          <p class="text-xs text-slate-400"><strong class="text-cyan-300">${escapeHtml(modName)}</strong> requires additional mods to run properly.</p>
        </div>
      </div>
      <div class="space-y-2 max-h-48 overflow-y-auto custom-scroll">
        ${listHtml}
      </div>
      <div class="flex items-center justify-end gap-3 pt-2">
        <button id="btn-dep-cancel" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white bg-slate-900 border border-slate-800 transition-all">Cancel</button>
        <button id="btn-dep-confirm" class="px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-cyan-400 hover:bg-cyan-300 shadow-lg shadow-cyan-500/30 transition-all flex items-center gap-1.5">
          <i data-lucide="check" class="w-3.5 h-3.5"></i>
          <span>Install & Enable All</span>
        </button>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
  refreshLucideIcons();

  document.getElementById('btn-dep-cancel').onclick = () => {
    modal.classList.add('hidden');
    renderMods();
  };
  document.getElementById('btn-dep-confirm').onclick = async () => {
    modal.classList.add('hidden');
    if (onConfirm) await onConfirm();
  };
}

async function toggleMod(modId, enabled) {
  const activeInst = STATE.selectedInstanceId || '26.2-ultra';
  if (enabled && window.pywebview && window.pywebview.api) {
    try {
      const depCheck = await window.pywebview.api.check_mod_dependencies(modId, activeInst);
      if (depCheck && depCheck.has_missing && depCheck.missing.length > 0) {
        showDependencyPromptModal(depCheck.mod_name || modId, depCheck.missing, async () => {
          await window.pywebview.api.resolve_and_install_dependencies(depCheck.missing, activeInst);
          await window.pywebview.api.toggle_mod(modId, true, activeInst);
          await loadModsFromBridge();
          showToast(`✓ Enabled ${depCheck.mod_name} and installed required dependencies!`, 'success');
        });
        return;
      }
    } catch (e) {
      console.warn('Dependency check error:', e);
    }
  }

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.toggle_mod(modId, enabled, activeInst);
    } catch {}
  }
  const m = STATE.mods.find(x => (x.filename === modId || x.id === modId));
  if (m) m.enabled = enabled;
  renderMods();
  showToast(`✓ Updated mod status: ${enabled ? 'Enabled' : 'Disabled'}`, 'success');
}

function switchModsSubTab(subTab) {
  const instView = document.getElementById('mods-installed-view');
  const onlineView = document.getElementById('mods-online-view');
  const btnInst = document.getElementById('btn-subtab-installed');
  const btnOnline = document.getElementById('btn-subtab-online');

  if (subTab === 'installed') {
    if (instView) instView.classList.remove('hidden');
    if (onlineView) onlineView.classList.add('hidden');
    if (btnInst) btnInst.className = "px-4 py-1.5 rounded-xl text-xs font-bold bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5";
    if (btnOnline) btnOnline.className = "px-4 py-1.5 rounded-xl text-xs font-bold text-slate-400 hover:text-slate-200 transition-all flex items-center gap-1.5";
    renderMods();
  } else {
    if (instView) instView.classList.add('hidden');
    if (onlineView) onlineView.classList.remove('hidden');
    if (btnInst) btnInst.className = "px-4 py-1.5 rounded-xl text-xs font-bold text-slate-400 hover:text-slate-200 transition-all flex items-center gap-1.5";
    if (btnOnline) btnOnline.className = "px-4 py-1.5 rounded-xl text-xs font-bold bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5";
    executeStoreSearch();
  }
  refreshLucideIcons();
}

function handleModDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  const el = document.getElementById('mod-dropzone');
  if (el) {
    el.classList.add('border-cyan-400', 'bg-cyan-950/40', 'scale-[1.01]');
  }
}

function handleModDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  const el = document.getElementById('mod-dropzone');
  if (el) {
    el.classList.remove('border-cyan-400', 'bg-cyan-950/40', 'scale-[1.01]');
  }
}

async function handleModDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  handleModDragLeave(e);
  const dt = e.dataTransfer;
  if (!dt || !dt.files || dt.files.length === 0) return;
  const files = Array.from(dt.files).filter(f => f.name.toLowerCase().endsWith('.jar'));
  if (files.length === 0) {
    showToast('Please drop valid Minecraft mod .jar files.', 'warning');
    return;
  }
  for (const file of files) {
    await processModUpload(file);
  }
}

async function handleModFileInput(e) {
  const files = Array.from(e.target.files || []).filter(f => f.name.toLowerCase().endsWith('.jar'));
  for (const file of files) {
    await processModUpload(file);
  }
  e.target.value = '';
}

async function processModUpload(file) {
  const activeInst = STATE.selectedInstanceId || '26.2-ultra';
  showToast(`⚡ Remapping & installing ${file.name} with 5-pass ASM engine...`, 'info');
  
  const reader = new FileReader();
  reader.onload = async function() {
    const dataUrl = reader.result;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.install_dropped_mod) {
      try {
        const res = await window.pywebview.api.install_dropped_mod(dataUrl, file.name, activeInst);
        if (res.success) {
          showToast(`✓ ${res.message}`, 'success');
          await loadModsFromBridge();
        } else {
          showToast(`✗ Failed to install mod: ${res.error}`, 'error');
        }
      } catch (err) {
        showToast(`Remap error: ${err}`, 'error');
      }
    } else {
      showToast(`✓ [Simulation] Remapped and installed ${file.name}`, 'success');
    }
  };
  reader.readAsDataURL(file);
}

