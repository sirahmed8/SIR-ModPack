// --- TAB SWITCHING ENGINE ---
function switchTab(tabId) {
  if (tabId === 'settings') {
    openSettingsModal();
    return;
  }
  STATE.activeTab = tabId;

  // 1. Hide all view panels
  document.querySelectorAll('[id^="view-"]').forEach(el => {
    el.classList.remove('active');
    el.classList.add('hidden');
  });

  // 2. Show active view panel
  const activeView = document.getElementById(`view-${tabId}`);
  if (activeView) {
    activeView.classList.remove('hidden');
    activeView.classList.add('active');
  }

  // 3. Update sidebar active state
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  const activeNavBtn = document.getElementById(`nav-${tabId}`);
  if (activeNavBtn) {
    activeNavBtn.classList.add('active');
  }

  // 4. Load content for specific tab
  if (tabId === 'launchpad') {
    renderLaunchpad();
  } else if (tabId === 'instances') {
    renderInstances();
  } else if (tabId === 'mods') {
    if (!STATE.mods || STATE.mods.length === 0) {
      if (typeof loadModsFromBridge === 'function') {
        loadModsFromBridge();
      } else {
        renderMods();
      }
    } else {
      renderMods();
    }
  } else if (tabId === 'shaders') {
    renderShaders();
  } else if (tabId === 'servers') {
    renderServers();
  } else if (tabId === 'satellite') {
    renderSatellite();
  } else if (tabId === 'worlds') {
    if (typeof refreshWorlds === 'function') {
      refreshWorlds(true);
    } else {
      renderWorldsGrid();
    }
  } else if (tabId === 'packs') {
    renderPacksGrid();
  } else if (tabId === 'gallery') {
    renderGalleryGrid();
  } else if (tabId === 'skins') {
    renderSkinsStudio();
  } else if (tabId === 'logs') {
    refreshLogs();
  } else if (tabId === 'hardware') {
    refreshHardwareTelemetry();
  } else if (tabId === 'settings') {
    renderSettings();
  } else if (tabId === 'news') {
    renderNewsView();
  }

  // 5. Always refresh Lucide icons
  if (window.lucide) {
    lucide.createIcons();
    setTimeout(() => lucide.createIcons(), 50);
  }
}

async function renderNewsView() {
  const container = document.getElementById('news-feed-container');
  if (!container) return;

  // Render initial loading skeleton
  container.innerHTML = `
    <div class="space-y-4 animate-pulse">
      <div class="h-44 rounded-3xl bg-slate-900/60 border border-slate-800/80"></div>
      <div class="h-32 rounded-2xl bg-slate-900/40 border border-slate-800/60"></div>
      <div class="h-32 rounded-2xl bg-slate-900/40 border border-slate-800/60"></div>
    </div>
  `;

  let activeBroadcast = null;
  let changelogs = [];

  // Helper fetch with timeout
  const fetchWithTimeout = async (url, timeoutMs = 3500) => {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(url, { signal: controller.signal });
      clearTimeout(id);
      return res;
    } catch (e) {
      clearTimeout(id);
      throw e;
    }
  };

  // 1. Try web platform JSON endpoint
  try {
    const resp = await fetchWithTimeout('https://sir-modpack.web.app/api/news?format=json');
    if (resp.ok) {
      const data = await resp.json();
      if (data && data.broadcast && data.broadcast.active) {
        activeBroadcast = data.broadcast;
      }
      if (data && Array.isArray(data.changelogs) && data.changelogs.length > 0) {
        changelogs = data.changelogs;
      }
    }
  } catch (e) {
    // 2. Fallback direct to Firebase RTDB
    try {
      const bRes = await fetchWithTimeout('https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/broadcasts/active.json');
      if (bRes.ok) {
        const bData = await bRes.json();
        if (bData && bData.active) activeBroadcast = bData;
      }
    } catch (_) {}

    try {
      const cRes = await fetchWithTimeout('https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/changelogs.json');
      if (cRes.ok) {
        const cData = await cRes.json();
        if (cData) {
          changelogs = Array.isArray(cData) ? cData : Object.values(cData);
        }
      }
    } catch (_) {}
  }

  // 3. Fallback to production master genesis if offline
  if (changelogs.length === 0) {
    changelogs = [
      {
        version: "v1.0.0",
        headline: "Production Master Genesis — Dual-Engine Architecture & Zero-Defect Release",
        date: "September 2026",
        tag: "Official Master Release",
        categories: [
          {
            title: "Performance & Dual Core",
            items: [
              "Sub-second launch hot-swap between Modern 26.2 (Fabric + Sodium + Iris) and Legacy 1.8.9 (Forge + OptiFine).",
              "Dynamic G1GC/ZGC memory compaction trimming background launcher RAM to under 45 MB.",
              "1000Hz hit-registration tuning with zero input latency for competitive multiplayer."
            ]
          },
          {
            title: "Visuals & Shaders",
            items: [
              "Pre-bundled with proprietary SIR Modern 2048 Ray-Traced Shaders and Complementary Reimagined.",
              "3D Parallax Occlusion Mapping (POM) with 1,261 depth maps and 258 living mob animations.",
              "Dedicated Shaders Studio with interactive split comparison slider and hardware profiling."
            ]
          },
          {
            title: "Lunar Bridge & Cloud Sync",
            items: [
              "Bi-directional profile synchronization across all 6 Lunar Client profiles (C: ↔ D:).",
              "Cross-app Google Authentication linking SIR Launcher and SIR Server Manager via loopback session.",
              "Real-time SHA-256 delta patcher enabling instant OTA updates with zero redundant downloads."
            ]
          }
        ]
      }
    ];
  }

  let html = '';

  // Update Launchpad Highway Announcement Banner
  const launchpadBannerEl = document.getElementById('launchpad-broadcast-banner');
  if (launchpadBannerEl) {
    if (activeBroadcast && activeBroadcast.title) {
      launchpadBannerEl.innerHTML = `
        <div class="relative overflow-hidden p-5 rounded-2xl border border-amber-500/50 bg-gradient-to-r from-amber-950/40 via-[#0d1424]/90 to-cyan-950/40 shadow-xl backdrop-blur-2xl flex items-center justify-between flex-wrap gap-4 animate-in fade-in-0 slide-in-from-top-2 duration-300">
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 shrink-0">
              <i data-lucide="radio" class="w-5 h-5 animate-pulse"></i>
            </div>
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-black uppercase bg-amber-500 text-slate-950 shadow-sm">${activeBroadcast.category || "LIVE BROADCAST"}</span>
                <h4 class="text-sm font-black text-amber-300">${activeBroadcast.title}</h4>
              </div>
              <p class="text-xs text-slate-300 leading-relaxed max-w-2xl">${activeBroadcast.message || ""}</p>
            </div>
          </div>
          ${activeBroadcast.buttonUrl ? `
            <a href="${activeBroadcast.buttonUrl}" target="_blank" class="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-black text-xs transition-all flex items-center gap-2 shadow-lg shadow-amber-500/20 active:scale-95 cursor-pointer">
              <span>${activeBroadcast.buttonLabel || "Open Announcement"}</span>
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            </a>
          ` : ''}
        </div>
      `;
      launchpadBannerEl.classList.remove('hidden');
    } else {
      launchpadBannerEl.innerHTML = '';
      launchpadBannerEl.classList.add('hidden');
    }
  }

  // Render Live Broadcast Announcement (if active from Owner Page)
  if (activeBroadcast && activeBroadcast.title) {
    html += `
      <div class="feature-card p-6 border-amber-500/50 bg-gradient-to-r from-amber-950/40 via-slate-900/70 to-cyan-950/40 space-y-3 animate-in fade-in-0 slide-in-from-top-2 duration-300">
        <div class="flex items-center justify-between flex-wrap gap-3">
          <div class="flex items-center gap-3">
            <span class="px-3 py-1 rounded-full text-[11px] font-mono font-black uppercase bg-amber-500 text-slate-950 shadow-md shadow-amber-500/30 flex items-center gap-1.5">
              <i data-lucide="radio" class="w-3.5 h-3.5 animate-pulse"></i>
              <span>${activeBroadcast.category || "LIVE BROADCAST"}</span>
            </span>
            <h3 class="text-base font-black text-amber-300">${activeBroadcast.title}</h3>
          </div>
          ${activeBroadcast.buttonUrl ? `
            <a href="${activeBroadcast.buttonUrl}" target="_blank" class="px-4 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-xs transition-all flex items-center gap-1.5 shadow-md shadow-amber-500/20 active:scale-95 cursor-pointer">
              <span>${activeBroadcast.buttonLabel || "Open Announcement"}</span>
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            </a>
          ` : ''}
        </div>
        <p class="text-xs text-slate-200 leading-relaxed font-medium">
          ${activeBroadcast.message || ""}
        </p>
      </div>
    `;
  }

  // Master v1.0.0 Banner
  html += `
    <div class="feature-card p-6 border-cyan-500/40 bg-gradient-to-r from-cyan-950/40 via-slate-900/60 to-purple-950/40 space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-3">
          <span class="px-3 py-1 rounded-full text-[11px] font-mono font-bold uppercase bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20">Official Launch</span>
          <h3 class="text-lg font-black text-white">SIR ModPack v1.0.0 — Master Genesis Release</h3>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="openModal('whats-new-modal')" class="px-3.5 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 font-bold text-xs border border-slate-700 transition-all flex items-center gap-1.5 cursor-pointer">
            <i data-lucide="book-open" class="w-3.5 h-3.5 text-cyan-400"></i>
            <span>What's New</span>
          </button>
          <button onclick="switchTab('instances')" class="px-4 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 active:scale-95 cursor-pointer">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
            <span>Play Genesis Profiles</span>
          </button>
        </div>
      </div>
      <p class="text-xs text-slate-300 leading-relaxed">
        The ultimate unified Minecraft ecosystem has officially arrived! Seamlessly switch between Modern 26.2 (Fabric) and Legacy 1.8.9 (Forge), enjoy 2048 HD ray-traced shaders with 3D parallax textures, and dominate with 1000Hz hit-registration PvP.
      </p>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
        <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div class="flex items-center gap-1.5 text-cyan-400 font-bold text-xs">
            <i data-lucide="sun" class="w-3.5 h-3.5"></i>
            <span>SIR Modern 2048 Shaders</span>
          </div>
          <p class="text-[11px] text-slate-400">Volumetric fog, screen-space reflections, and 144 FPS balanced presets.</p>
        </div>
        <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div class="flex items-center gap-1.5 text-emerald-400 font-bold text-xs">
            <i data-lucide="zap" class="w-3.5 h-3.5"></i>
            <span>Hardware Governor</span>
          </div>
          <p class="text-[11px] text-slate-400">Dynamic G1GC/ZGC memory trimming flushes background RAM to &lt;45 MB.</p>
        </div>
        <div class="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <div class="flex items-center gap-1.5 text-purple-400 font-bold text-xs">
            <i data-lucide="moon" class="w-3.5 h-3.5"></i>
            <span>Lunar Client Bridge</span>
          </div>
          <p class="text-[11px] text-slate-400">1-click bi-directional sync across all 6 Lunar profiles and game options.</p>
        </div>
      </div>
    </div>

    <!-- Timeline Updates List -->
    <div class="space-y-4">
      <h4 class="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
        <i data-lucide="history" class="w-4 h-4 text-cyan-400"></i>
        <span>Release History & Ecosystem Changelog</span>
      </h4>
  `;

  changelogs.forEach(entry => {
    html += `
      <div class="p-5 rounded-2xl border border-slate-800/80 bg-slate-900/40 space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2.5">
            <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(0,229,255,0.4)]"></span>
            <span class="text-xs font-bold text-slate-200">${entry.version || "v1.0.0"} • ${entry.headline || "Official Release"}</span>
          </div>
          <span class="text-[11px] font-mono text-slate-500">${entry.date || "September 2026"}</span>
        </div>
    `;

    if (entry.categories && Array.isArray(entry.categories)) {
      entry.categories.forEach(cat => {
        html += `
          <div class="space-y-1.5 pt-1">
            <div class="text-[11px] font-bold text-cyan-400/90">${cat.title || ""}</div>
            <ul class="text-xs text-slate-400 space-y-1 list-disc list-inside">
              ${(cat.items || []).map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
        `;
      });
    }

    html += `</div>`;
  });

  html += `</div>`;

  container.innerHTML = html;
  refreshLucideIcons();
}
window.renderNewsView = renderNewsView;

// --- AUTO EXECUTE DEEP LINK ---
function handleIncomingDeepLink(dl) {
  if (!dl) return;
  const action = (dl.action || '').toLowerCase();
  const params = dl.params || {};

  if (action === 'join' || params.ip || params.server) {
    const serverIp = params.ip || params.server || '';
    if (typeof showToast === 'function' && serverIp) {
      showToast(`⚡ Deep-link connected: Server ${serverIp}`, 'info');
    }
    if (serverIp && typeof joinServer === 'function') {
      joinServer(serverIp);
    } else {
      switchTab('servers');
    }
  } else if (action === 'launch' || (action !== 'profile' && !params.name && params.profile)) {
    const prof = params.profile || '';
    if (typeof showToast === 'function' && prof) {
      showToast(`✨ Deep-link connected: Profile ${prof}`, 'info');
    }
    if (prof && typeof launchGame === 'function') {
      launchGame(prof);
    } else {
      switchTab('instances');
    }
  } else if (action === 'mod/install' || action.startsWith('mod')) {
    const modId = params.id || params.modId || '';
    if (modId) {
      if (typeof showToast === 'function') {
        showToast(`⚡ Deep-link installing mod: ${modId}`, 'info');
      }
      switchTab('mods');
      if (typeof installOnlineModById === 'function') {
        installOnlineModById(modId);
      }
    }
  } else if (action === 'profile' || params.name) {
    const profName = params.name || params.profile || '';
    if (profName) {
      if (typeof showToast === 'function') {
        showToast(`✨ Switched to profile: ${profName}`, 'info');
      }
      if (typeof selectInstance === 'function') {
        selectInstance(profName);
      }
    }
  } else if (action === 'shaders') {
    switchTab('shaders');
  } else if (action === 'auth') {
    const rawData = params.data || params.payload;
    if (rawData) {
      try {
        const authData = typeof rawData === 'string' ? JSON.parse(decodeURIComponent(rawData)) : rawData;
        if (authData && authData.uid && typeof window.onCloudAuthSuccess === 'function') {
          window.onCloudAuthSuccess({
            authenticated: true,
            uid: authData.uid,
            email: authData.email,
            displayName: authData.displayName,
            photoURL: authData.photoURL,
            idToken: authData.idToken,
            lastSync: Math.floor(Date.now() / 1000)
          });
        }
      } catch (e) {
        console.error('[DeepLink] Failed parsing auth data:', e);
      }
    }
  }
}
window.handleIncomingDeepLink = handleIncomingDeepLink;

async function installOnlineModById(modId) {
  if (!modId) return;
  try {
    if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.install_online_mod === 'function') {
      const activeInst = (window.STATE && window.STATE.selectedInstanceId) ? window.STATE.selectedInstanceId : '26.2-ultra';
      if (typeof showToast === 'function') {
        showToast(`📥 Downloading mod: ${modId}...`, 'info');
      }
      const res = await window.pywebview.api.install_online_mod(modId, activeInst);
      if (res && res.success) {
        if (typeof showToast === 'function') {
          showToast(`✓ Successfully installed mod ${modId}!`, 'success');
        }
        if (typeof loadModsFromBridge === 'function') {
          await loadModsFromBridge();
        }
      } else {
        if (typeof showToast === 'function') {
          showToast(res && res.error ? `Mod install error: ${res.error}` : `Failed to install mod ${modId}`, 'error');
        }
      }
    } else {
      console.log(`[DeepLink] Mod install queued for id: ${modId}`);
    }
  } catch (err) {
    console.error('[DeepLink] Failed installing mod by id:', err);
  }
}
window.installOnlineModById = installOnlineModById;

function checkAndExecuteDeepLink() {
  if (!window.__SIR_DEEP_LINK__) return;
  const dl = window.__SIR_DEEP_LINK__;
  window.__SIR_DEEP_LINK__ = null;
  handleIncomingDeepLink(dl);
}

document.addEventListener('DOMContentLoaded', () => {
  setTimeout(checkAndExecuteDeepLink, 350);
  setTimeout(renderNewsView, 500);
});

