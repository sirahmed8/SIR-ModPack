// =============================================================================
// 1. INSTANCES & PROFILES MATRIX RENDERER
// =============================================================================
const MASTER_INSTANCES_LIST = [
  { 
    id: "26.2-ultra", 
    name: "SIR 26 Visuals", 
    loader: "Fabric 0.16.10", 
    version: "26.2", 
    category: "modern", 
    mods_count: 225, 
    badge: "✨ Enhanced Fidelity",
    gradient: "from-cyan-950/60 via-blue-900/40 to-slate-900/90",
    icon: "sparkles",
    iconColor: "text-cyan-400",
    desc: "Fabric 26.2 engine with enhanced shaders, crystal water, dynamic skies and 3D textures.",
    features: ["SIR Shader", "SIR Pack", "Fresh Animations", "Iris + Sodium Engine"],
    link: "https://sir-modpack.web.app"
  },
  { 
    id: "26.2-balanced", 
    name: "SIR 26 Balanced", 
    loader: "Fabric 0.16.10", 
    version: "26.2", 
    category: "modern", 
    mods_count: 225, 
    badge: "⚡ Standard Balanced",
    gradient: "from-emerald-950/60 via-teal-900/40 to-slate-900/90",
    icon: "zap",
    iconColor: "text-emerald-400",
    desc: "Fabric 26.2 calibrated with Lithium, FerriteCore and ImmediatelyFast for responsive gameplay.",
    features: ["SIR Master Balanced Preset", "ImmediatelyFast HUD/Font", "FerriteCore Memory Compactor", "Entity Culling Async"],
    link: "https://sir-modpack.web.app/benchmarks"
  },
  { 
    id: "26.2-performance", 
    name: "SIR 26 Performance", 
    loader: "Fabric 0.16.10", 
    version: "26.2", 
    category: "modern", 
    mods_count: 220, 
    badge: "🏆 Competitive Engine",
    gradient: "from-amber-950/60 via-orange-900/40 to-slate-900/90",
    icon: "flame",
    iconColor: "text-amber-400",
    desc: "High-framerate Fabric 26.2 engine with Sodium optimization, low-latency input and dynamic memory cleanup.",
    features: ["Multi-Core Optimization", "Low-Latency Input Polling", "Minimal Particle Clutter", "Dynamic RAM Purge"],
    link: "https://sir-modpack.web.app/profiles"
  },
  { 
    id: "26.2", 
    name: "SIR 26 Vanilla", 
    loader: "Vanilla", 
    version: "26.2", 
    category: "vanilla", 
    mods_count: 0, 
    is_vanilla: true,
    badge: "🌿 Pure Clean Vanilla",
    gradient: "from-slate-900 via-emerald-950/30 to-slate-900",
    icon: "leaf",
    iconColor: "text-emerald-400",
    desc: "Official pure Minecraft 26.2 without any mods or visual overhaul. Original vanilla gameplay accelerated by SIR Launcher.",
    features: ["Zero Mods (Pure Vanilla)", "Default Textures", "Vanilla Lighting", "Full Offline & Online Play"],
    link: "https://sir-modpack.web.app"
  },
  { 
    id: "1.8.9-ultra", 
    name: "SIR 1.8.9 Visuals", 
    loader: "Forge 1.8.9", 
    version: "1.8.9", 
    category: "legacy", 
    mods_count: 27, 
    badge: "🎬 Enhanced Classic",
    gradient: "from-purple-950/60 via-indigo-900/40 to-slate-900/90",
    icon: "eye",
    iconColor: "text-purple-400",
    desc: "Forge 1.8.9 with shader lighting, dynamic skies, 3D animated skins and high-definition clarity.",
    features: ["OptiFine Shaders & Dynamic Lights", "3D Player Skin Layers", "Custom HD Skyboxes", "SIR Legacy 32x Faithful"],
    link: "https://sir-modpack.web.app"
  },
  { 
    id: "1.8.9-balanced", 
    name: "SIR 1.8.9 Balanced", 
    loader: "Forge 1.8.9", 
    version: "1.8.9", 
    category: "legacy", 
    mods_count: 27, 
    badge: "⚔️ Standard Competitive",
    gradient: "from-rose-950/60 via-red-900/40 to-slate-900/90",
    icon: "swords",
    iconColor: "text-rose-400",
    desc: "Forge 1.8.9 calibrated for fluid combat animations, custom HUDs, and responsive click handling.",
    features: ["Fluid Animation Pack", "BetterFPS Engine", "MemoryFix Purge", "SIR Legacy 32x Faithful"],
    link: "https://sir-modpack.web.app/trainer"
  },
  { 
    id: "1.8.9-performance", 
    name: "SIR 1.8.9 Performance", 
    loader: "Forge 1.8.9", 
    version: "1.8.9", 
    category: "legacy", 
    mods_count: 27, 
    badge: "⚡ Low Latency Pure",
    gradient: "from-blue-950/60 via-cyan-900/40 to-slate-900/90",
    icon: "gauge",
    iconColor: "text-cyan-400",
    desc: "Forge 1.8.9 stripped for maximum motion clarity, instant input response and zero micro-stutters.",
    features: ["Raw Input Direct Engine", "No Lag Animations", "RAM Garbage Compaction", "Clean Minimal Assets"],
    link: "https://sir-modpack.web.app/download"
  }
];

STATE.instances = MASTER_INSTANCES_LIST;
STATE.instanceCategory = "all";

async function selectInstance(id, opts = {}) {
  STATE.selectedInstanceId = id;
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.select_instance(id);
    } catch {}
  }
  const inst = STATE.instances.find(i => i.id === id);
  renderLaunchpad();
  renderInstances();
  if (typeof refreshWorlds === 'function') {
    refreshWorlds(true);
  }
  if (inst && !opts.silent) {
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
      console.warn('Could not fetch Mojang versions');
    }
  }
}

function selectInstanceVersion(val, label) {
  const hiddenInput = document.getElementById('new-instance-version-val');
  const labelEl = document.getElementById('new-instance-version-label');
  const display = label || val;
  if (hiddenInput) hiddenInput.value = val;
  if (labelEl) labelEl.textContent = display;

  const menu = document.getElementById('new-instance-version-menu');
  if (menu) menu.classList.add('hidden');
  const arrow = document.getElementById('new-instance-version-arrow');
  if (arrow) arrow.classList.remove('rotate-180');

  handleVersionChange(val);
  renderVersionOptions(document.getElementById('toggle-snapshots-cb')?.checked || false);
}
window.selectInstanceVersion = selectInstanceVersion;

function renderVersionOptions(showSnapshots = false) {
  const menu = document.getElementById('new-instance-version-menu');
  if (!menu) return;

  const currentVal = document.getElementById('new-instance-version-val')?.value || '26.2';
  
  const defaultVersions = [
    { id: '26.2', name: '26.2', type: 'release' },
    { id: '26.1.2', name: '26.1.2', type: 'release' },
    { id: '26.1.1', name: '26.1.1', type: 'release' },
    { id: '26.1', name: '26.1', type: 'release' },
    { id: '25w08a', name: '25w08a (Snapshot)', type: 'snapshot' },
    { id: '1.21.5-pre1', name: '1.21.5-pre1 (Pre-Release)', type: 'snapshot' },
    { id: '24w46a', name: '24w46a (Snapshot)', type: 'snapshot' },
    { id: '1.21.4', name: '1.21.4', type: 'release' },
    { id: '1.21.3', name: '1.21.3', type: 'release' },
    { id: '1.21.1', name: '1.21.1', type: 'release' },
    { id: '1.20.6', name: '1.20.6', type: 'release' },
    { id: '1.20.4', name: '1.20.4', type: 'release' },
    { id: '1.20.1', name: '1.20.1', type: 'release' },
    { id: '1.19.4', name: '1.19.4', type: 'release' },
    { id: '1.18.2', name: '1.18.2', type: 'release' },
    { id: '1.16.5', name: '1.16.5', type: 'release' },
    { id: '1.12.2', name: '1.12.2', type: 'release' },
    { id: '1.8.9', name: '1.8.9', type: 'release' },
    { id: '1.7.10', name: '1.7.10', type: 'release' },
  ];

  const list = _cachedMinecraftVersions.length ? _cachedMinecraftVersions : defaultVersions;
  const filtered = list.filter(v => showSnapshots || v.type === 'release');

  menu.innerHTML = filtered.map(v => {
    const isSel = v.id === currentVal;
    const displayName = v.name || v.id;
    const isSnapshot = v.type === 'snapshot';
    return `
      <div 
        onclick="selectInstanceVersion('${escapeHtml(v.id)}', '${escapeHtml(displayName)}')" 
        class="dropdown-opt flex items-center justify-between px-3 py-2 text-xs font-bold rounded-xl cursor-pointer transition-all ${
          isSel 
            ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30' 
            : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/80 hover:text-slate-900 dark:hover:text-white'
        }"
      >
        <div class="flex items-center gap-2">
          <span>${escapeHtml(displayName)}</span>
          ${isSnapshot 
            ? '<span class="badge-tag bg-amber-500/20 text-amber-300 text-[9px] px-1.5 py-0.5 rounded font-mono">Snapshot</span>' 
            : '<span class="badge-tag bg-cyan-500/20 text-cyan-300 text-[9px] px-1.5 py-0.5 rounded font-mono">Release</span>'}
        </div>
        ${isSel ? '<i data-lucide="check" class="w-3.5 h-3.5 text-cyan-400"></i>' : ''}
      </div>
    `;
  }).join('');
  refreshLucideIcons();
}

function toggleSnapshotsFilter(show) {
  renderVersionOptions(show);
}

function submitNewInstance() {
  return submitCreateInstance();
}

async function submitCreateInstance() {
  const nameInput = document.getElementById('new-instance-name-input');
  const versionInput = document.getElementById('new-instance-version-val');
  const ramSlider = document.getElementById('new-inst-ram-slider');
  const perfCb = document.getElementById('new-inst-perf-cb');
  const submitBtn = document.getElementById('create-instance-submit-btn');

  const name = (nameInput?.value || '').trim();
  const version = versionInput?.value || '26.2';
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
    submitBtn.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Creating...</span>';
    refreshLucideIcons();
  }

  try {
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.create_instance(name, version, loader, ramGb, enablePerf);
      if (res.success) {
        closeModal('add-instance-modal');
        await loadInstancesFromBridge();
        if (res.instance?.id) {
          await selectInstance(res.instance.id, { silent: true });
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
  const defaultName = `${inst?.name || 'Instance'} (Copy)`;
  const newName = await showCustomPrompt({
    title: "Duplicate Profile",
    message: "Enter a name for the duplicated profile:",
    defaultValue: defaultName,
    placeholder: "Profile name...",
    confirmText: "Duplicate"
  });
  if (!newName) return;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.clone_instance) {
    try {
      const res = await window.pywebview.api.clone_instance(instId, newName);
      if (res?.success) {
        if (typeof loadInstancesFromBridge === 'function') {
          await loadInstancesFromBridge();
        }
        renderInstances();
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
  const profileName = inst?.name || instId;
  
  showConfirmDialog({
    title: "Delete Profile",
    message: `Are you sure you want to delete profile "${profileName}"? This will permanently remove its local directories, settings, and saved data.`,
    confirmText: "Delete Profile",
    cancelText: "Keep Profile",
    isDanger: true,
    onConfirm: async () => {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.delete_instance) {
        try {
          const res = await window.pywebview.api.delete_instance(instId);
          if (res?.success) {
            if (typeof loadInstancesFromBridge === 'function') {
              await loadInstancesFromBridge();
            }
            renderInstances();
            showToast(res.message || `✓ Profile "${profileName}" deleted`, 'info');
          } else {
            showToast('✗ ' + (res?.error || 'Failed to delete profile'), 'error');
          }
        } catch (e) {
          showToast('✗ Delete error: ' + (e.message || e), 'error');
        }
      } else {
        STATE.instances = STATE.instances.filter(i => i.id !== instId);
        renderInstances();
        showToast(`✓ Profile "${profileName}" deleted`, 'info');
      }
    }
  });
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

  if (!filtered || filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full p-8 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
        <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
          <i data-lucide="layers" class="w-6 h-6"></i>
        </div>
        <div>
          <h4 class="text-sm font-bold text-slate-200">No Instances Found in Category "${escapeHtml(cat)}"</h4>
          <p class="text-xs text-slate-400 mt-1">Create a new custom instance or reset your filter to view all profiles.</p>
        </div>
        <div class="flex items-center justify-center gap-3 pt-2">
          <button onclick="filterInstanceCategory('all')" class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 transition-all">
            Show All Profiles
          </button>
          <button onclick="openModal('add-instance-modal')" class="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black shadow-md shadow-cyan-500/20 transition-all flex items-center gap-1.5 cursor-pointer">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i>
            <span>Create Profile</span>
          </button>
        </div>
      </div>
    `;
    refreshLucideIcons();
    return;
  }

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
            <h4 class="text-sm font-black text-slate-900 dark:text-slate-100">${escapeHtml(inst.name)}</h4>
            <p class="text-xs text-slate-600 dark:text-slate-400 mt-1">${inst.fps_target || '200+ FPS'} • ${inst.tag || 'Minecraft Profile'}</p>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5 line-clamp-2">${escapeHtml(inst.desc || '')}</p>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
          <button onclick="selectInstance('${inst.id}')" class="flex-1 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
            isSelected 
              ? (isLight ? 'bg-[#0284c7] text-white shadow-md shadow-[#0284c7]/20' : 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/25') 
              : (isLight ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:bg-slate-700')
          }">${isSelected ? '✓ Active Profile' : 'Select Profile'}</button>
          <button onclick="launchGame('${inst.id}')" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-md shadow-emerald-500/20 transition-all hover:scale-105 cursor-pointer" title="Launch this instance">▶</button>
          <button onclick="duplicateInstance('${inst.id}')" class="p-2 rounded-xl ${isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:text-white'} transition-all cursor-pointer" title="Duplicate Profile">📋</button>
          <button onclick="openInstanceFolder('${inst.id}')" class="p-2 rounded-xl ${isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:text-white'} transition-all cursor-pointer" title="Open Profile Directory">📁</button>
          <button onclick="syncLunarProfile('${inst.id}')" class="p-2 rounded-xl ${isLight ? 'bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-300' : 'bg-slate-800 text-slate-300 hover:text-cyan-400'} transition-all cursor-pointer" title="Bi-Directional Lunar Client Sync (C: ↔ D:)">🌙</button>
          ${isCustom ? `
            <button onclick="deleteInstance('${inst.id}')" class="p-2 rounded-xl bg-rose-500/15 text-rose-500 hover:bg-rose-500 hover:text-white transition-all cursor-pointer" title="Delete Profile">🗑️</button>
          ` : ''}
        </div>
      </div>
    `;
  }).join('');
  refreshLucideIcons();
}

window.applyVideoPresetPrompt = async function(instId) {
  const choice = await showCustomPrompt({
    title: "Apply Video Preset",
    message: "Enter video preset to apply to this profile (ultra, balanced, performance):",
    defaultValue: "balanced",
    placeholder: "ultra / balanced / performance",
    confirmText: "Apply Preset"
  });
  if (choice) {
    const valid = choice.toLowerCase().trim();
    if (['ultra', 'balanced', 'performance'].includes(valid)) {
      if (window.applyVideoPreset) {
        window.applyVideoPreset(valid, instId);
      }
    } else {
      if (window.showToast) window.showToast('Invalid preset selected! Choose ultra, balanced, or performance.', 'error');
    }
  }
};

window.syncLunarProfile = async function(instId) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.sync_lunar_profile) {
    try {
      showToast(`🔄 Synchronizing ${instId} with Lunar Client...`, 'info');
      const res = await window.pywebview.api.sync_lunar_profile(instId, 'lunar_to_sir');
      if (res && res.success) {
        showToast(`✓ ${res.message}`, 'success');
      } else {
        showToast(`Notice: ${res?.error || 'Profile not linked in Lunar Client'}`, 'warning');
      }
    } catch (e) {
      showToast(`Sync error: ${e}`, 'error');
    }
  } else {
    showToast(`✓ [Simulation] Synchronized settings with Lunar Client for ${instId}`, 'success');
  }
};

window.syncAllLunarProfiles = async function(direction = 'lunar_to_sir') {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.sync_all_lunar_profiles) {
    try {
      showToast(`🔄 Synchronizing all profiles with Lunar Client...`, 'info');
      const res = await window.pywebview.api.sync_all_lunar_profiles(direction);
      if (res && res.success) {
        showToast(`✓ Synced ${res.synced_pairs_count} profile pairs with Lunar Client!`, 'success');
      } else {
        showToast(`Synced ${res?.synced_pairs_count || 0} profiles. ${res?.errors?.join(', ') || ''}`, 'warning');
      }
    } catch (e) {
      showToast(`Sync error: ${e}`, 'error');
    }
  }
};

window.openInstanceFolder = async function(instId) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_instance_folder) {
    try {
      const res = await window.pywebview.api.open_instance_folder(instId);
      if (res && res.success) {
        if (typeof showToast === 'function') showToast(`Opened directory: ${res.path}`, 'success');
        return;
      }
    } catch (e) {}
  }
  if (typeof showToast === 'function') showToast(`Opening profile directory for ${instId}...`, 'info');
};

