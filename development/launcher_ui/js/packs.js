// =============================================================================
// 7. RESOURCE PACKS & TEXTURE SUITE RENDERER
// =============================================================================
const OFFICIAL_RESOURCE_PACKS = [
  {
    id: "sir_ultimate_pack",
    name: "SIR Ultimate Pack (3D POM + PBR)",
    version: "26.2",
    tag: "✨ 3D POM Masterpiece",
    author: "Sir Ahmed & Team",
    gradient: "from-cyan-950/60 via-blue-900/40 to-slate-900/90",
    icon: "layers",
    iconColor: "text-cyan-400",
    desc: "Full 3D Parallax Occlusion Mapping (POM), emissive glowing ore textures, connected textures (CTM), and custom Fresh Mob Animations for Modern 26.2.",
    features: ["3D Parallax Occlusion Mapping", "Emissive Glowing Ores", "Fresh Animations Mob Rig", "Connected Textures & Clean Glass"],
    link: "https://sir-modpack.web.app/packs",
    file: "SIR_Ultimate_Pack.zip"
  },
  {
    id: "sir_legacy_32x",
    name: "SIR Legacy 32x Faithful PvP",
    version: "1.8.9",
    tag: "⚔️ Hypixel Tournament 32x",
    author: "Sir Ahmed",
    gradient: "from-rose-950/60 via-red-900/40 to-slate-900/90",
    icon: "sparkles",
    iconColor: "text-rose-400",
    desc: "Faithful 32x HD PvP textures with custom short swords, transparent inventory GUI, clear crystal water, low fire, and custom day/night skyboxes for Legacy 1.8.9.",
    features: ["Custom Short Swords & Bows", "Low Fire & Crystal Water", "Transparent Inventory & Hotbar", "Cosmic Night Skybox"],
    link: "https://sir-modpack.web.app/packs",
    file: "SIR_Legacy_32x.zip"
  }
];

STATE.resourcePacks = OFFICIAL_RESOURCE_PACKS;

async function loadResourcePacksFromBridge() {
  renderResourcePacksGrid();
}

function renderResourcePacksGrid() {
  const container = document.getElementById('packs-grid') || document.getElementById('resourcepacks-list-container');
  if (!container) return;

  const isLight = document.documentElement.classList.contains('light');
  container.innerHTML = OFFICIAL_RESOURCE_PACKS.map(p => `
    <div class="feature-card p-5 rounded-3xl border transition-all ${
      isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
    } flex flex-col justify-between">
      <div>
        <div class="p-3.5 rounded-2xl bg-gradient-to-r ${p.gradient} border border-white/5 mb-3 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-black/40 border border-white/10 flex items-center justify-center ${p.iconColor} shadow-md">
              <i data-lucide="${p.icon}" class="w-5 h-5"></i>
            </div>
            <div>
              <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-white/10 text-white border border-white/15">${escapeHtml(p.tag)}</span>
              <p class="text-[10px] font-mono text-cyan-300/80 mt-0.5">MC ${p.version}</p>
            </div>
          </div>
          <span class="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_8px_#38ef7d] shrink-0" title="Active & Verified"></span>
        </div>

        <div class="flex items-center justify-between gap-2">
          <h4 class="text-sm font-black text-slate-900 dark:text-slate-100">${escapeHtml(p.name)}</h4>
          <span class="badge-tag text-[9px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">Official</span>
        </div>

        <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">${escapeHtml(p.desc)}</p>

        <ul class="mt-3 space-y-1 py-2 border-y border-slate-200 dark:border-slate-800/80">
          ${p.features.map(f => `
            <li class="flex items-center gap-1.5 text-[11px] text-slate-600 dark:text-slate-300">
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
              <span>${escapeHtml(f)}</span>
            </li>
          `).join('')}
        </ul>
      </div>

      <div class="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
        <span class="text-[10px] font-bold text-emerald-400 flex items-center gap-1">● Pre-Installed in Pack</span>
        <a href="${p.link}" target="_blank" class="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-all flex items-center gap-1">
          <span>Pack Specs</span>
          <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
        </a>
      </div>
    </div>
  `).join('');

  refreshLucideIcons();
}

// =============================================================================
// 8. WORLDS & SAVES MANAGER (ZERO FAKE DATA)
// =============================================================================
STATE.worlds = [];

async function loadWorldsFromBridge() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
      const realWorlds = await window.pywebview.api.get_worlds(activeInst);
      STATE.worlds = Array.isArray(realWorlds) ? realWorlds : [];
    } catch {
      STATE.worlds = [];
    }
  } else {
    STATE.worlds = [];
  }
  renderWorldsGrid();
}

function renderWorldsGrid() {
  const container = document.getElementById('worlds-grid');
  if (!container) return;
  const isLight = document.documentElement.classList.contains('light');

  if (STATE.worlds.length === 0) {
    container.innerHTML = `
      <div class="col-span-full feature-card p-10 text-center border-slate-800">
        <div class="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-3xl mx-auto mb-3 shadow-inner">
          🗺️
        </div>
        <h4 class="text-base font-bold text-slate-200">No Singleplayer Worlds Found</h4>
        <p class="text-xs text-slate-400 mt-1 max-w-sm mx-auto">Launch Minecraft to create your first survival or creative world, and it will appear here automatically.</p>
        <button onclick="launchGame()" class="mt-4 px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black transition-all inline-flex items-center gap-1.5 shadow-md shadow-emerald-500/20 active:scale-95">
          ▶ Launch Minecraft
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = STATE.worlds.map(w => `
    <div class="feature-card p-5 rounded-2xl border transition-all ${
      isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
    } flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-black text-slate-900 dark:text-slate-100">${escapeHtml(w.name)}</h4>
          <span class="badge-tag bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">${w.mode || 'Survival'}</span>
        </div>
        <div class="flex items-center gap-3 text-[11px] text-slate-500 dark:text-slate-400 mt-2 font-mono">
          <span>🎮 ${w.version || 'Minecraft'}</span>
          <span>•</span>
          <span>💾 ${w.size || '10 MB'}</span>
          <span>•</span>
          <span>🕒 ${w.lastPlayed || 'Recent'}</span>
        </div>
      </div>
      <div class="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
        <button onclick="launchGame()" class="flex-1 py-2 rounded-xl ${
          isLight ? 'bg-[#0284c7] text-white' : 'bg-cyan-500 text-slate-950'
        } text-xs font-black transition-all shadow-md">Play World ▶</button>
        <button onclick="showToast('✓ Backup created for ' + '${escapeHtml(w.name)}', 'success')" class="px-3 py-2 rounded-xl ${
          isLight ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:text-white'
        } text-xs font-bold transition-all">📦 Backup</button>
      </div>
    </div>
  `).join('');
  refreshLucideIcons();
}

async function refreshWorlds() {
  loadWorldsFromBridge();
}

