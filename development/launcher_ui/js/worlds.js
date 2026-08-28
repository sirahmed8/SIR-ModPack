// =============================================================================
// 7. RESOURCE PACKS & 3D POM MANAGER
// =============================================================================
STATE.packs = [
  { id: "sir-ultimate-pack", name: "SIR Ultimate 3D POM Pack", resolution: "128x HD", enabled: true, version: "2026.1", desc: "Ultra-detailed normal and specular depth maps for raytraced 3D POM block relief." },
  { id: "sir-legacy-32x", name: "SIR Legacy 32x Faithful", resolution: "32x Crisp", enabled: true, version: "1.8.9 / 26.2", desc: "High-contrast clean PvP faithful textures with crystal short swords and clear glass." }
];

async function loadResourcePacksFromBridge() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
      const realPacks = await window.pywebview.api.get_resource_packs(activeInst);
      if (Array.isArray(realPacks) && realPacks.length > 0) {
        STATE.packs = realPacks;
      }
    } catch (e) {
      console.warn("Failed to load packs from bridge:", e);
    }
  }
  renderPacksGrid();
}

function renderPacksGrid() {
  const container = document.getElementById('packs-grid');
  if (!container) return;
  const isLight = document.documentElement.classList.contains('light');
  
  if (STATE.packs.length === 0) {
    container.innerHTML = `
      <div class="col-span-full feature-card p-10 text-center border-slate-800">
        <p class="text-xs text-slate-400">No resource packs found.</p>
        <button onclick="openPacksDir()" class="mt-3 px-4 py-1.5 rounded-xl bg-cyan-500 text-slate-950 text-xs font-bold">Open Resourcepacks Folder</button>
      </div>
    `;
    return;
  }

  container.innerHTML = STATE.packs.map(pack => {
    const isAct = pack.enabled || pack.active;
    return `
      <div onclick="selectSinglePack('${escapeHtml(pack.filename)}')" class="feature-card p-5 rounded-2xl border transition-all cursor-pointer ${
        isAct 
          ? (isLight ? 'bg-cyan-50/70 border-cyan-500 ring-2 ring-cyan-400/40 shadow-md' : 'bg-cyan-950/20 border-cyan-500 ring-1 ring-cyan-500/40 shadow-lg shadow-cyan-500/10')
          : (isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700')
      } flex items-center justify-between gap-4">
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h4 class="text-sm font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(pack.name.replace(/_/g, ' '))}</h4>
            <span class="badge-tag text-[9px] px-2 py-0.5 rounded-full font-bold ${
              isAct ? 'bg-cyan-500 text-slate-950 font-black' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
            }">${isAct ? 'Active Pack' : (pack.resolution || 'HD Pack')}</span>
            <span class="text-[9px] font-mono text-slate-400">v${pack.version || '1.0'}</span>
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">${escapeHtml(pack.desc || 'Clean resource pack.')}</p>
        </div>
        <div class="flex items-center gap-3">
          <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
            isAct 
              ? 'border-cyan-500 bg-cyan-500 text-slate-950 shadow-sm' 
              : 'border-slate-400 dark:border-slate-600 bg-transparent'
          }">
            ${isAct ? '<div class="w-2.5 h-2.5 rounded-full bg-slate-950"></div>' : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
  refreshLucideIcons();
}

async function selectSinglePack(filename) {
  STATE.packs.forEach(p => {
    p.enabled = (p.filename === filename);
    p.active = (p.filename === filename);
  });
  renderPacksGrid();

  const activeInst = STATE.selectedInstanceId || '26.2';
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.toggle_resource_pack(filename, true, activeInst);
    } catch (e) {
      console.warn('Failed to toggle pack on bridge:', e);
    }
  }
  const activePack = STATE.packs.find(p => p.filename === filename);
  showToast(`✓ Active Resource Pack: ${activePack ? activePack.name : filename}`, 'success');
}

async function refreshPacks() {
  loadResourcePacksFromBridge();
}

function openPacksDir() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.open_resourcepacks_folder('26.2');
  } else {
    showToast('✓ Opened Resourcepacks folder!', 'success');
  }
}

