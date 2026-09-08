// =============================================================================
// 7. RESOURCE PACKS & TEXTURE SUITE RENDERER (MUTUALLY EXCLUSIVE)
// =============================================================================
const OFFICIAL_RESOURCE_PACKS = [
  {
    id: "sir_ultimate_pack",
    name: "SIR Ultimate 3D POM Pack",
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
    name: "SIR Legacy 32x Faithful",
    version: "1.8.9 / 26.2",
    tag: "⚔️ Hypixel Tournament 32x",
    author: "Sir Ahmed",
    gradient: "from-rose-950/60 via-red-900/40 to-slate-900/90",
    icon: "sparkles",
    iconColor: "text-rose-400",
    desc: "Faithful 32x HD PvP textures with custom short swords, transparent inventory GUI, clear crystal water, low fire, and custom day/night skyboxes.",
    features: ["Custom Short Swords & Bows", "Low Fire & Crystal Water", "Transparent Inventory & Hotbar", "Cosmic Night Skybox"],
    link: "https://sir-modpack.web.app/packs",
    file: "SIR_Legacy_32x.zip"
  }
];

STATE.resourcePacks = OFFICIAL_RESOURCE_PACKS;
if (!STATE.activeResourcePack) {
  STATE.activeResourcePack = "sir_ultimate_pack";
}

async function loadResourcePacksFromBridge() {
  renderResourcePacksGrid();
}

function selectResourcePack(packId) {
  STATE.activeResourcePack = packId;
  const chosen = OFFICIAL_RESOURCE_PACKS.find(p => p.id === packId);
  
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
      window.pywebview.api.set_active_resource_pack(activeInst, chosen ? chosen.file : "SIR_Ultimate_Pack.zip");
    } catch {}
  }
  
  renderResourcePacksGrid();
  showToast(`✓ Active Texture Pack: ${chosen ? chosen.name : packId}`, "success");
}

function renderResourcePacksGrid() {
  const container = document.getElementById('packs-grid') || document.getElementById('resourcepacks-list-container');
  if (!container) return;

  const isLight = document.documentElement.classList.contains('light');
  container.innerHTML = OFFICIAL_RESOURCE_PACKS.map(p => {
    const isActive = STATE.activeResourcePack === p.id;
    return `
      <div onclick="selectResourcePack('${p.id}')" class="feature-card p-5 rounded-3xl border transition-all cursor-pointer ${
        isActive 
          ? 'border-cyan-400 bg-cyan-950/25 ring-1 ring-cyan-400/50 shadow-lg shadow-cyan-500/15' 
          : (isLight ? 'bg-white border-slate-200 hover:border-slate-300 opacity-75' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 opacity-75')
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
            <span class="w-3 h-3 rounded-full ${isActive ? 'bg-emerald-400 shadow-[0_0_8px_#38ef7d]' : 'bg-slate-700'} shrink-0" title="${isActive ? 'Active Pack' : 'Inactive'}"></span>
          </div>

          <div class="flex items-center justify-between gap-2">
            <h4 class="text-sm font-black text-slate-900 dark:text-slate-100">${escapeHtml(p.name)}</h4>
            <span class="badge-tag text-[9px] font-mono px-2.5 py-0.5 rounded-full ${
              isActive 
                ? 'bg-cyan-500 text-slate-950 font-black' 
                : 'bg-slate-800 text-slate-400 border border-slate-700'
            }">
              ${isActive ? 'Active Pack' : 'Click to Activate'}
            </span>
          </div>

          <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-2 leading-relaxed">${escapeHtml(p.desc)}</p>

          <ul class="mt-3 space-y-1 py-2 border-y border-slate-200 dark:border-slate-800/80">
            ${p.features.map(f => `
              <li class="flex items-center gap-1.5 text-[11px] text-slate-600 dark:text-slate-300">
                <span class="w-1.5 h-1.5 rounded-full ${isActive ? 'bg-cyan-400' : 'bg-slate-600'}"></span>
                <span>${escapeHtml(f)}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
          <span class="text-[10px] font-bold ${isActive ? 'text-emerald-400' : 'text-slate-500'} flex items-center gap-1">
            ${isActive ? '● Active in Minecraft Profile' : '○ Standby in Shader Suite'}
          </span>
          <a href="${p.link}" target="_blank" onclick="event.stopPropagation()" class="px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-all flex items-center gap-1">
            <span>Pack Specs</span>
            <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
          </a>
        </div>
      </div>
    `;
  }).join('');

  refreshLucideIcons();
}

function renderPacksGrid() {
  renderResourcePacksGrid();
}
window.renderPacksGrid = renderResourcePacksGrid;

function refreshPacks() {
  loadResourcePacksFromBridge();
  showToast("✓ Resource packs list refreshed", "info");
}
window.refreshPacks = refreshPacks;

function openPacksDir() {
  if (window.pywebview && window.pywebview.api) {
    const activeInst = STATE.selectedInstanceId || '26.2';
    try {
      if (window.pywebview.api.open_resourcepacks_folder) {
        window.pywebview.api.open_resourcepacks_folder(activeInst);
        return;
      }
      window.pywebview.api.open_instance_folder(activeInst);
      return;
    } catch {}
  }
  showToast("Opening resource packs directory...", "info");
}
window.openPacksDir = openPacksDir;


