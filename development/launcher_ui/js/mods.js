// =============================================================================
// 2. MODS & ONLINE STORE HUB RENDERER
// =============================================================================
STATE.mods = [];
STATE.modCategory = "all";
STATE.modSearchQuery = "";

function filterModCategory(cat) {
  STATE.modCategory = cat;
  const pills = document.querySelectorAll('#mod-category-pills .filter-pill');
  pills.forEach(btn => {
    if (btn.textContent.trim().toLowerCase() === String(cat).toLowerCase()) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  renderMods();
}

function handleModSearch(query) {
  STATE.modSearchQuery = (query || "").toLowerCase().trim();
  renderMods();
}

async function loadModsFromBridge() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
      const realMods = await window.pywebview.api.get_mods(activeInst, '', 'All');
      if (Array.isArray(realMods) && realMods.length > 0) {
        STATE.mods = realMods;
      }
    } catch (e) {
      console.warn('Error loading real mods:', e);
    }
  }
  renderMods();
}

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
    link: "https://sir-modpack.web.app/profiles"
  }
];

function renderMods() {
  const container = document.getElementById('mods-grid');
  if (!container) return;

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

  const countBadge = document.getElementById('mods-count-badge');
  const activeCount = STATE.mods.filter(m => m.enabled).length;
  if (countBadge) countBadge.innerText = `${activeCount} Active / ${STATE.mods.length} Installed Mods`;

  // Render Official SIR Mods Highlight Cards
  const sirCardsHtml = OFFICIAL_SIR_MODS.map(s => `
    <div class="col-span-full md:col-span-1 p-4 rounded-2xl bg-gradient-to-r ${s.gradient} border border-cyan-500/30 flex flex-col justify-between shadow-lg shadow-cyan-500/5">
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="badge-tag text-[9px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">${escapeHtml(s.badge)}</span>
          <span class="text-[9px] font-mono text-slate-400">v${escapeHtml(s.version)}</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-xl bg-black/40 border border-white/10 flex items-center justify-center ${s.iconColor} shrink-0 shadow-md">
            <i data-lucide="${s.icon}" class="w-4 h-4"></i>
          </div>
          <div class="min-w-0 flex-1">
            <h4 class="text-xs font-black text-white truncate">${escapeHtml(s.name)}</h4>
            <p class="text-[10px] text-cyan-300 font-mono">By ${escapeHtml(s.author)}</p>
          </div>
        </div>
        <p class="text-[11px] text-slate-300 mt-2 line-clamp-2 leading-relaxed">${escapeHtml(s.desc)}</p>
      </div>
      <div class="mt-3 pt-2 border-t border-white/10 flex items-center justify-between">
        <span class="text-[10px] font-bold text-emerald-400 flex items-center gap-1">● Pre-Installed & Active</span>
        <a href="${s.link}" target="_blank" class="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-white/20 text-white text-[10px] font-bold transition-all flex items-center gap-1">
          <span>Docs</span>
          <i data-lucide="external-link" class="w-3 h-3"></i>
        </a>
      </div>
    </div>
  `).join('');

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
      <div class="col-span-full feature-card p-8 text-center border-slate-800">
        <p class="text-xs text-slate-400">No other installed mods match your search query.</p>
        <button onclick="filterModCategory('All')" class="mt-3 px-4 py-1.5 rounded-xl bg-cyan-500 text-slate-950 text-xs font-bold">Show All Mods</button>
      </div>
    `;
    refreshLucideIcons();
    return;
  }

  const normalModsHtml = filtered.map(mod => `
    <div class="feature-card p-4 rounded-2xl border transition-all ${
      isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
    } flex items-center justify-between gap-4">
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <h4 class="text-xs font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(mod.name.replace(/_/g, ' '))}</h4>
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

async function toggleMod(modId, enabled) {
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
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

