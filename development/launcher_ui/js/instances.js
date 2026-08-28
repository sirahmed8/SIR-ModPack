// =============================================================================
// 1. INSTANCES & PROFILES MATRIX RENDERER
// =============================================================================
const MASTER_INSTANCES_LIST = [
  { 
    id: "sir-26-ultra", 
    name: "SIR 26 (Ultra Visuals)", 
    loader: "Fabric", 
    version: "26.2", 
    category: "modern", 
    mods_count: 241, 
    fps_est: "90 - 180+ FPS", 
    badge: "✨ Raytraced Masterpiece",
    gradient: "from-cyan-950/60 via-blue-900/40 to-slate-900/90",
    icon: "sparkles",
    iconColor: "text-cyan-400",
    desc: "Master 2048 Shader Engine with Solas crystal transparent water, circular glowing sun & 3D POM.",
    features: ["SIR Extreme Shader 2.0", "SIR Ultimate Pack (3D POM)", "Fresh Mob Animations", "Iris + Sodium OptiEngine"],
    link: "https://sir-modpack.web.app/shaders"
  },
  { 
    id: "sir-26-balanced", 
    name: "SIR 26 (Balanced 144+ FPS)", 
    loader: "Fabric", 
    version: "26.2", 
    category: "modern", 
    mods_count: 241, 
    fps_est: "144 - 280+ FPS", 
    badge: "⚡ Esports Balanced",
    gradient: "from-emerald-950/60 via-teal-900/40 to-slate-900/90",
    icon: "zap",
    iconColor: "text-emerald-400",
    desc: "Optimized SIR Balanced Shader + Lithium + FerriteCore + ImmediatelyFast with zero frame drops.",
    features: ["SIR Balanced Shader", "ImmediatelyFast HUD/Font", "FerriteCore RAM Compactor", "Entity Culling Async"],
    link: "https://sir-modpack.web.app/benchmarks"
  },
  { 
    id: "sir-26-comp", 
    name: "SIR 26 (Competitive Speed)", 
    loader: "Fabric", 
    version: "26.2", 
    category: "modern", 
    mods_count: 220, 
    fps_est: "240 - 600+ FPS", 
    badge: "🏆 0ms Latency PvP",
    gradient: "from-amber-950/60 via-orange-900/40 to-slate-900/90",
    icon: "flame",
    iconColor: "text-amber-400",
    desc: "Zero-shader maximum framerate engine with Sodium, dynamic memory purges & tournament low latency.",
    features: ["360+ FPS Multi-Core Pipeline", "Low-Latency Input Polling", "Minimal Particle Clutter", "Dynamic RAM Purge"],
    link: "https://sir-modpack.web.app/profiles"
  },
  { 
    id: "sir-26-vanilla", 
    name: "SIR 26 (Modular Vanilla+)", 
    loader: "Vanilla+", 
    version: "26.2 - 1.8.9", 
    category: "modern", 
    mods_count: 35, 
    fps_est: "200+ FPS", 
    badge: "🍃 Pure Vanilla+",
    gradient: "from-blue-950/60 via-slate-900/40 to-slate-900/90",
    icon: "layers",
    iconColor: "text-blue-400",
    desc: "Direct %APPDATA%/.minecraft integration with auto Java 8/25 runtime switching.",
    features: ["Vanilla+ Quality of Life", "Auto Java Runtime Bridge", "Lightweight Footprint", "Fast Boot in 3s"],
    link: "https://sir-modpack.web.app"
  },
  { 
    id: "sir-189-cine", 
    name: "Legacy 1.8.9 (Ultra Cinematic)", 
    loader: "Forge", 
    version: "1.8.9", 
    category: "legacy", 
    mods_count: 57, 
    fps_est: "240+ FPS", 
    badge: "🎬 Classic Raytracing",
    gradient: "from-purple-950/60 via-indigo-900/40 to-slate-900/90",
    icon: "eye",
    iconColor: "text-purple-400",
    desc: "OptiFine shader lighting, dynamic skybox, 3D animated skins, custom capes & HD texture clarity.",
    features: ["OptiFine Shaders & Dynamic Lights", "3D Player Skin Layers", "Custom HD Skyboxes", "HD Font & Clean UI"],
    link: "https://sir-modpack.web.app/shaders"
  },
  { 
    id: "sir-189-balanced", 
    name: "Legacy 1.8.9 (Balanced PvP)", 
    loader: "Forge", 
    version: "1.8.9", 
    category: "legacy", 
    mods_count: 57, 
    fps_est: "500+ FPS", 
    badge: "⚔️ Hypixel BedWars",
    gradient: "from-rose-950/60 via-red-900/40 to-slate-900/90",
    icon: "swords",
    iconColor: "text-rose-400",
    desc: "1.7 fluid animations, custom HUD, 32x Faithful texture clarity, BetterFPS & zero micro-stutters.",
    features: ["1.7 Blockhit & Sword Fluidity", "BetterFPS Riven Algorithm", "FoamFix Memory Reducer", "SIR Legacy 32x Faithful"],
    link: "https://sir-modpack.web.app/packs"
  },
  { 
    id: "sir-189-battle", 
    name: "Legacy 1.8.9 PvP Battle Suite", 
    loader: "Forge", 
    version: "1.8.9", 
    category: "legacy", 
    mods_count: 57, 
    fps_est: "1000+ FPS", 
    badge: "⚡ Tournament God Mode",
    gradient: "from-fuchsia-950/60 via-pink-900/40 to-slate-900/90",
    icon: "zap",
    iconColor: "text-fuchsia-400",
    desc: "Pure tournament speed: 0ms RawInput mouse polling, instant keystrokes, short swords & reach tracers.",
    features: ["0ms RawInput Mouse Polling", "Instant Keystroke Overlay", "Custom Short Swords", "Patcher Zero Delay"],
    link: "https://sir-modpack.web.app/trainer"
  },
  { 
    id: "sir-custom", 
    name: "Custom Sandbox Profile", 
    loader: "Fabric / Forge", 
    version: "Multi", 
    category: "modern", 
    mods_count: 0, 
    fps_est: "Dynamic", 
    badge: "🛠️ Sandbox Studio",
    gradient: "from-slate-950/60 via-slate-800/40 to-slate-900/90",
    icon: "settings",
    iconColor: "text-slate-400",
    desc: "Create and configure your own custom modpack with 1-click mod installer and dynamic version selector.",
    features: ["Custom Loader Selection", "Modrinth/CurseForge Sync", "Modular Memory Tuning", "Independent Game Dir"],
    link: "https://sir-modpack.web.app/builder"
  }
];

STATE.instances = MASTER_INSTANCES_LIST;
STATE.instanceCategory = "all";

async function selectInstance(id) {
  STATE.selectedInstanceId = id;
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.select_instance(id);
    } catch {}
  }
  const inst = STATE.instances.find(i => i.id === id);
  renderLaunchpad();
  renderInstances();
  if (inst) {
    showToast(`✓ Selected Profile: ${inst.name}`, 'success');
  }
}

function filterInstanceCategory(cat) {
  STATE.instanceCategory = (cat || 'all').toLowerCase();
  ['all', 'modern', 'legacy'].forEach(c => {
    const btn = document.getElementById(`inst-filter-${c}`);
    if (btn) {
      if (c === STATE.instanceCategory) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    }
  });
  // Update dynamic counts
  const allCount = document.getElementById('inst-count-all');
  const modernCount = document.getElementById('inst-count-modern');
  const legacyCount = document.getElementById('inst-count-legacy');
  if (allCount) allCount.textContent = STATE.instances.length;
  if (modernCount) modernCount.textContent = STATE.instances.filter(i => (i.category || '').toLowerCase() === 'modern').length;
  if (legacyCount) legacyCount.textContent = STATE.instances.filter(i => (i.category || '').toLowerCase() === 'legacy').length;
  renderInstances();
}

// =============================================================================
// INSTANCE CREATION STUDIO & UNIVERSAL VERSION ENGINE
// =============================================================================
let _selectedInstanceLoader = 'fabric';
let _cachedMinecraftVersions = [];

function selectLoaderType(loaderId) {
  _selectedInstanceLoader = loaderId;
  const loaders = ['fabric', 'forge', 'neoforge', 'vanilla'];
  loaders.forEach(id => {
    const card = document.getElementById(`loader-card-${id}`);
    if (!card) return;
    if (id === loaderId) {
      card.className = 'p-3 rounded-xl border border-cyan-500 bg-cyan-500/10 ring-1 ring-cyan-500/40 cursor-pointer transition-all';
    } else {
      card.className = 'p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900/60 hover:border-slate-300 dark:hover:border-slate-700 cursor-pointer transition-all';
    }
  });
}

function handleVersionChange(version) {
  const neoforgeCard = document.getElementById('loader-card-neoforge');
  const isOld = ['1.8', '1.7', '1.12', '1.16', '1.18', '1.19'].some(v => version.includes(v));
  if (neoforgeCard) {
    if (isOld) {
      neoforgeCard.style.opacity = '0.4';
      neoforgeCard.style.pointerEvents = 'none';
      if (_selectedInstanceLoader === 'neoforge') {
        selectLoaderType('forge');
      }
    } else {
      neoforgeCard.style.opacity = '1';
      neoforgeCard.style.pointerEvents = 'auto';
    }
  }
}

async function loadVersionsManifest() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_minecraft_versions) {
    try {
      const res = await window.pywebview.api.get_minecraft_versions();
      if (res?.success && Array.isArray(res.versions)) {
        _cachedMinecraftVersions = res.versions;
        renderVersionOptions(false);
      }
    } catch (e) {
      console.warn('Could not fetch Mojang versions:', e);
    }
  }
}

function renderVersionOptions(showSnapshots = false) {
  const select = document.getElementById('new-instance-version-select');
  if (!select || !_cachedMinecraftVersions.length) return;

  const currentVal = select.value;
  const filtered = _cachedMinecraftVersions.filter(v => showSnapshots || v.type === 'release');
  
  select.innerHTML = filtered.map(v => `
    <option value="${v.id}" ${v.id === currentVal ? 'selected' : ''}>
      ${v.id} ${v.type === 'release' ? '(Release)' : '(Snapshot/Beta)'}
    </option>
  `).join('');
}

function toggleSnapshotsFilter(show) {
  renderVersionOptions(show);
}

function submitNewInstance() {
  return submitCreateInstance();
}

async function submitCreateInstance() {
  const nameInput = document.getElementById('new-instance-name-input');
  const versionSelect = document.getElementById('new-instance-version-select');
  const ramSlider = document.getElementById('new-inst-ram-slider');
  const perfCb = document.getElementById('new-inst-perf-cb');
  const submitBtn = document.getElementById('create-instance-submit-btn');

  const name = (nameInput?.value || '').trim();
  const version = versionSelect?.value || '1.21.4';
  const loader = _selectedInstanceLoader || 'fabric';
  const ramGb = parseInt(ramSlider?.value || '8', 10);
  const enablePerf = perfCb ? perfCb.checked : true;

  if (!name) {
    showToast('Please enter a display name for your profile', 'error');
    if (nameInput) nameInput.focus();
    return;
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<div class="w-4 h-4 border-2 border-slate-950/40 border-t-slate-950 rounded-full animate-spin"></div><span>Creating Profile...</span>';
  }

  try {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.create_instance) {
      const res = await window.pywebview.api.create_instance(name, version, loader, ramGb, enablePerf);
      if (res?.success) {
        closeModal('add-instance-modal');
        if (nameInput) nameInput.value = '';
        await loadInstances();
        if (res.instance?.id) {
          await selectInstance(res.instance.id);
        }
        showToast(res.message || `✓ Created Minecraft ${version} (${loader}) profile!`, 'success');
      } else {
        showToast('✗ ' + (res?.error || 'Failed to create profile'), 'error');
      }
    } else {
      closeModal('add-instance-modal');
      showToast(`✓ [Simulation] Created Profile: ${name} (${version})`, 'success');
    }
  } catch (err) {
    showToast('✗ Error creating profile: ' + (err.message || err), 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4"></i><span>Create & Setup Profile</span>';
      refreshLucideIcons();
    }
  }
}

async function duplicateInstance(instId) {
  const inst = STATE.instances.find(i => i.id === instId);
  const newName = prompt(`Enter name for duplicated profile:`, `${inst?.name || 'Instance'} (Copy)`);
  if (!newName) return;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.clone_instance) {
    try {
      const res = await window.pywebview.api.clone_instance(instId, newName);
      if (res?.success) {
        await loadInstances();
        showToast(`✓ Duplicated profile: ${newName}`, 'success');
      } else {
        showToast('✗ ' + (res?.error || 'Failed to clone profile'), 'error');
      }
    } catch (e) {
      showToast('✗ Clone error: ' + (e.message || e), 'error');
    }
  }
}

async function deleteInstance(instId) {
  const inst = STATE.instances.find(i => i.id === instId);
  if (!confirm(`Are you sure you want to delete "${inst?.name || instId}"? This will permanently remove its files.`)) {
    return;
  }

  if (window.pywebview && window.pywebview.api && window.pywebview.api.delete_instance) {
    try {
      const res = await window.pywebview.api.delete_instance(instId);
      if (res?.success) {
        await loadInstances();
        showToast(res.message || '✓ Profile deleted', 'info');
      } else {
        showToast('✗ ' + (res?.error || 'Failed to delete profile'), 'error');
      }
    } catch (e) {
      showToast('✗ Delete error: ' + (e.message || e), 'error');
    }
  }
}

function renderInstances() {
  const container = document.getElementById('instances-grid');
  if (!container) return;

  const cat = (STATE.instanceCategory || 'all').toLowerCase();
  const filtered = STATE.instances.filter(i => {
    if (cat === 'all') return true;
    return (i.category || '').toLowerCase() === cat;
  });

  const isLight = document.documentElement.classList.contains('light');

  container.innerHTML = filtered.map(inst => {
    const isSelected = inst.id === STATE.selectedInstanceId;
    const isCustom = inst.isCustom || inst.id.startsWith('custom-');
    return `
      <div class="feature-card p-5 rounded-2xl border transition-all duration-200 ${
        isSelected 
          ? (isLight ? 'border-[#0284c7] ring-2 ring-[#0284c7]/30 bg-white' : 'border-cyan-400 bg-cyan-950/20 ring-1 ring-cyan-400/40') 
          : (isLight ? 'border-slate-200 bg-white hover:border-slate-300' : 'border-slate-800 hover:border-slate-700')
      }">
        <div class="flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2">
              <h4 class="text-sm font-black text-slate-900 dark:text-slate-100">${escapeHtml(inst.name)}</h4>
              <span class="badge-tag text-[9px] font-mono px-2 py-0.5 rounded-full ${
                (inst.loader || '').includes('Fabric') ? 'bg-cyan-500/15 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30' : 'bg-purple-500/15 text-purple-600 dark:text-purple-400 border border-purple-500/30'
              }">${inst.loader || 'Vanilla'} ${inst.version || ''}</span>
            </div>
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">${inst.fps_target || '200+ FPS'} • ${inst.tag || 'Minecraft Profile'}</p>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 line-clamp-2">${escapeHtml(inst.desc || '')}</p>
          </div>
          ${isSelected ? '<span class="w-3 h-3 rounded-full bg-cyan-400 shadow-[0_0_8px_#00e5ff] shrink-0"></span>' : ''}
        </div>

        <div class="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
          <button onclick="selectInstance('${inst.id}')" class="flex-1 py-2 rounded-xl text-xs font-bold transition-all ${
            isSelected 
              ? (isLight ? 'bg-[#0284c7] text-white' : 'bg-cyan-500 text-slate-950') 
              : (isLight ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:bg-slate-700')
          }">${isSelected ? 'Active Profile' : 'Select Profile'}</button>
          <button onclick="launchGame('${inst.id}')" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-md shadow-emerald-500/20 transition-all hover:scale-105" title="Launch this instance">▶</button>
          <button onclick="duplicateInstance('${inst.id}')" class="p-2 rounded-xl ${isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:text-white'} transition-all" title="Duplicate Profile">📋</button>
          <button onclick="openInstanceMods('${inst.id}')" class="p-2 rounded-xl ${isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:text-white'} transition-all" title="Open Mods Folder">📁</button>
          ${isCustom ? `
            <button onclick="deleteInstance('${inst.id}')" class="p-2 rounded-xl bg-rose-500/15 text-rose-500 hover:bg-rose-500 hover:text-white transition-all" title="Delete Profile">🗑️</button>
          ` : ''}
        </div>
      </div>
    `;
  }).join('');
  refreshLucideIcons();
}


