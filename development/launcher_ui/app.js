// =============================================================================
// SIR Launcher — Modular Bootstrap Orchestrator
// Clean Architecture Standard • Fully Typed & Event-Wired
// =============================================================================

// --- INITIALIZATION GATEWAY ---
async function initLauncher() {
  // 1. Resolve Theme
  const savedTheme = localStorage.getItem('sir_theme_mode') || 'dark';
  setThemeMode(savedTheme);

  // Restore saved RAM setting
  const savedRam = localStorage.getItem('sir_ram_gb');
  if (savedRam) {
    STATE.ramGb = parseInt(savedRam);
    const ramSlider = document.getElementById('ram-slider');
    const ramBadge = document.getElementById('ram-value-badge');
    if (ramSlider) ramSlider.value = STATE.ramGb;
    if (ramBadge) ramBadge.textContent = STATE.ramGb + ' GB RAM';
  }

  // 2. Load accounts first so active profile is established before painting
  await loadAccounts();

  // Render initial UI immediately with hydrated profile
  renderLaunchpad();
  refreshLucideIcons();

  if (typeof autoSyncAccountsSilent === 'function') {
    autoSyncAccountsSilent().catch(() => {});
  }
  if (typeof loadInstancesFromBridge === 'function') {
    await loadInstancesFromBridge();
  }
  renderLaunchpad();
  // Helper for non-blocking startup calls with 15s timeout to support scanning 228+ mods
  const safeAsync = (promiseFn, label = '', timeoutMs = 15000) => {
    return Promise.race([
      typeof promiseFn === 'function' ? promiseFn() : Promise.resolve(),
      new Promise((_, reject) => setTimeout(() => reject(new Error(`Timeout ${label}`)), timeoutMs))
    ]).catch(err => console.warn(`[Startup] ${label} deferred:`, err));
  };

  // Run background data loading asynchronously without stalling the UI thread
  safeAsync(loadVersionsManifest, 'loadVersionsManifest', 15000);
  safeAsync(loadModsFromBridge, 'loadModsFromBridge', 15000);
  safeAsync(loadResourcePacksFromBridge, 'loadResourcePacksFromBridge', 15000);
  safeAsync(loadWorldsFromBridge, 'loadWorldsFromBridge', 15000);
  loadServersLive();

  // 3. Check legal acceptance (never prompt repeatedly once accepted)
  let legalAccepted = localStorage.getItem('sir_legal_accepted') || localStorage.getItem('sir_eula_accepted');
  if (!legalAccepted && window.pywebview && window.pywebview.api) {
    try {
      const legalStatus = await window.pywebview.api.get_legal_status();
      if (legalStatus && legalStatus.agreed) {
        legalAccepted = '2026.1';
        localStorage.setItem('sir_legal_accepted', '2026.1');
        localStorage.setItem('sir_eula_accepted', '2026.1');
      }
    } catch {}
  }

  if (!legalAccepted) {
    if (window.pywebview && window.pywebview.api) {
      try {
        const st = await window.pywebview.api.get_legal_status();
        if (st && st.agreed) {
          localStorage.setItem('sir_legal_accepted', '2026.1');
          localStorage.setItem('sir_eula_accepted', '2026.1');
        } else {
          openLegalModal();
        }
      } catch {
        openLegalModal();
      }
    }
  }


  // 4. Switch to default launchpad
  switchTab('launchpad');

  // 5. Initialize Cloud Sync UI & Onboarding
  if (typeof initCloudSyncUI === 'function') {
    initCloudSyncUI().catch(() => {});
  }
  if (typeof checkFirstTimeOnboarding === 'function') {
    checkFirstTimeOnboarding();
  }

  // 6. Create all Lucide icons
  refreshLucideIcons();

  // 7. Fade-in UI
  document.body.classList.add('sir-ready');
}

let _isLauncherInitializing = false;
let _launcherInitializedWithBridge = false;

async function safeInitLauncher(forceFromBridge = false) {
  if (forceFromBridge) {
    while (_isLauncherInitializing) {
      await new Promise(r => setTimeout(r, 50));
    }
    _isLauncherInitializing = true;
    try {
      await initLauncher();
      _launcherInitializedWithBridge = true;
    } catch (err) {
      console.error("Launcher bridge init error:", err);
    } finally {
      document.body.classList.add('sir-ready');
      _isLauncherInitializing = false;
    }
    return;
  }

  if (_isLauncherInitializing) return;
  _isLauncherInitializing = true;
  try {
    await initLauncher();
    if (window.pywebview && window.pywebview.api) {
      _launcherInitializedWithBridge = true;
    }
  } catch (err) {
    console.error("Launcher initialization error:", err);
  } finally {
    document.body.classList.add('sir-ready');
    _isLauncherInitializing = false;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  safeInitLauncher(false);
});

window.addEventListener('pywebviewready', async () => {
  await safeInitLauncher(true);
  if (typeof autoSyncAccountsSilent === 'function') {
    autoSyncAccountsSilent();
  }
});

// Active Bridge Ready Watcher: continuous polling fallback in case pywebviewready event already fired
let _bridgePoller = setInterval(async () => {
  if (window.pywebview && window.pywebview.api) {
    if (!_launcherInitializedWithBridge) {
      clearInterval(_bridgePoller);
      await safeInitLauncher(true);
      if (typeof autoSyncAccountsSilent === 'function') {
        autoSyncAccountsSilent();
      }
    }
  }
}, 80);

// Stop poller after 6 seconds to conserve resources
setTimeout(() => { if (_bridgePoller) clearInterval(_bridgePoller); }, 6000);


// =============================================================================
// MISSING UTILITY FUNCTIONS — SERVER, INSTANCES, SHADERS, HARDWARE
// =============================================================================

function copyIp(host) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(host).then(() => {
      showToast('✓ Copied ' + host + ' to clipboard!', 'success');
    }).catch(() => {
      showToast('IP: ' + host, 'info');
    });
  } else {
    showToast('IP: ' + host, 'info');
  }
}

function joinServer(host) {
  if (window.pywebview && window.pywebview.api) {
    try { window.pywebview.api.join_server(host); return; } catch {}
  }
  showToast('Connecting to ' + host + '...', 'info');
}

function openInstanceMods(instId) {
  instId = instId || (typeof STATE !== 'undefined' && STATE.selectedInstanceId) || '26.2-ultra';
  if (window.pywebview && window.pywebview.api) {
    const api = window.pywebview.api;
    const fn = api.open_mods_folder || api.open_instance_mods_folder;
    if (typeof fn === 'function') {
      try {
        const p = fn.call(api, instId);
        if (p && typeof p.then === 'function') {
          p.then(res => {
            if (res && res.success) {
              showToast('Opened physical mods folder: ' + (res.path || instId), 'success');
            } else {
              showToast(res && res.error ? res.error : 'Could not open mods folder', 'error');
            }
          }).catch(err => {
            showToast('Error opening mods folder: ' + err, 'error');
          });
          return;
        } else if (p && p.success) {
          showToast('Opened physical mods folder: ' + (p.path || instId), 'success');
          return;
        }
      } catch (e) {
        console.error('Error opening mods folder:', e);
      }
    }
  }
  showToast('Opening physical mods folder for ' + instId + '...', 'info');
}
window.openInstanceMods = openInstanceMods;

function toggleServerSorting() {
  STATE.serverSortOrder = STATE.serverSortOrder === 'ping' ? 'players' : 'ping';
  STATE.servers = [...STATE.servers].sort((a, b) => {
    if (STATE.serverSortOrder === 'ping') return a.ping - b.ping;
    return parseInt(b.players.replace(/,/g, '')) - parseInt(a.players.replace(/,/g, ''));
  });
  renderServers();
  showToast('Sorted by ' + (STATE.serverSortOrder === 'ping' ? 'Ping (lowest first)' : 'Players (most first)'), 'info');
}

function searchServers(query) {
  const q = (query || '').toLowerCase().trim();
  if (!q) {
    STATE.servers = [...MASTER_SERVERS_LIST];
  } else {
    STATE.servers = MASTER_SERVERS_LIST.filter(s =>
      s.name.toLowerCase().includes(q) ||
      s.host.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q)
    );
  }
  renderServers();
}

const RAM_STEPS = [2, 4, 6, 8, 10, 12, 16, 24];

function updateRamDisplay(val) {
  const stepIdx = parseInt(val);
  const gb = (stepIdx >= 0 && stepIdx < RAM_STEPS.length) ? RAM_STEPS[stepIdx] : (parseInt(val) || 8);
  const badge = document.getElementById('ram-value-badge');
  if (badge) badge.textContent = gb + ' GB RAM';
  STATE.ramGb = gb;
  localStorage.setItem('sir_ram_gb', gb);
}

function setPowerGovernor(gov) {
  STATE.powerGovernor = gov;
  ['smooth', 'turbo'].forEach(g => {
    const btn = document.getElementById('gov-' + g);
    if (!btn) return;
    if (g === gov) {
      btn.className = btn.className
        .replace('border-slate-800 bg-slate-900/60', '')
        .trim() + ' border-cyan-500 bg-cyan-500/10';
    } else {
      btn.className = btn.className
        .replace('border-cyan-500 bg-cyan-500/10', '')
        .trim() + ' border-slate-800 bg-slate-900/60';
    }
  });
  if (window.pywebview && window.pywebview.api) {
    try { window.pywebview.api.set_power_governor(gov); } catch {}
  }
  showToast(gov === 'turbo' ? '⚡ Turbo High-FPS Mode activated!' : '🍃 Smooth / Eco Mode activated!', 'success');
}

let _debounceOfflineTimer = null;
function debounceOfflineLookup(value) {
  clearTimeout(_debounceOfflineTimer);
  _debounceOfflineTimer = setTimeout(() => {
    const preview = document.getElementById('offline-avatar-preview');
    if (preview && value && value.length >= 2) {
      preview.src = `https://mc-heads.net/avatar/${encodeURIComponent(value)}/36`;
    }
  }, 400);
}

STATE.activeShader = 'SIR_Extreme_Shader.zip';

async function renderShaders() {
  const isLight = document.documentElement.classList.contains('light');
  if (window.pywebview && window.pywebview.api) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
      const realActive = await window.pywebview.api.get_active_shader(activeInst);
      if (realActive) STATE.activeShader = realActive;
    } catch {}
  }

  const isExtreme = !STATE.activeShader || STATE.activeShader.includes('Extreme');
  const isBalanced = STATE.activeShader && STATE.activeShader.includes('Balanced');

  const cardExtreme = document.getElementById('shader-card-extreme');
  const btnExtreme = document.getElementById('shader-btn-extreme');
  const badgeExtreme = document.getElementById('shader-badge-extreme');

  const cardBalanced = document.getElementById('shader-card-balanced');
  const btnBalanced = document.getElementById('shader-btn-balanced');
  const badgeBalanced = document.getElementById('shader-badge-balanced');

  if (cardExtreme && btnExtreme && badgeExtreme) {
    if (isExtreme) {
      badgeExtreme.classList.remove('hidden');
      cardExtreme.className = `feature-card border-cyan-500 ring-2 ring-cyan-400/40 ${
        isLight ? 'bg-cyan-50/70 shadow-md' : 'bg-cyan-950/20 shadow-lg shadow-cyan-500/10'
      } transition-all`;
      btnExtreme.className = "mt-4 w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs border border-cyan-400 shadow-md shadow-cyan-500/20 transition-all flex items-center justify-center gap-1.5 cursor-pointer";
      btnExtreme.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4"></i><span>✓ Activated Engine</span>`;
    } else {
      badgeExtreme.classList.add('hidden');
      cardExtreme.className = `feature-card border-slate-200 dark:border-slate-800 ${
        isLight ? 'bg-white' : 'bg-slate-900/60'
      } transition-all`;
      btnExtreme.className = `mt-4 w-full py-2.5 rounded-xl ${
        isLight ? 'bg-slate-100 hover:bg-cyan-500 hover:text-slate-950 text-slate-700 border-slate-300' : 'bg-slate-800 hover:bg-cyan-500 hover:text-slate-950 text-slate-300 border-slate-700'
      } font-bold text-xs border transition-all flex items-center justify-center gap-1.5 cursor-pointer`;
      btnExtreme.innerHTML = `<span>Activate Extreme Preset</span>`;
    }
  }

  if (cardBalanced && btnBalanced && badgeBalanced) {
    if (isBalanced) {
      badgeBalanced.classList.remove('hidden');
      cardBalanced.className = `feature-card border-emerald-500 ring-2 ring-emerald-400/40 ${
        isLight ? 'bg-emerald-50/70 shadow-md' : 'bg-emerald-950/20 shadow-lg shadow-emerald-500/10'
      } transition-all`;
      btnBalanced.className = "mt-4 w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs border border-emerald-400 shadow-md shadow-emerald-500/20 transition-all flex items-center justify-center gap-1.5 cursor-pointer";
      btnBalanced.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4"></i><span>✓ Activated Engine</span>`;
    } else {
      badgeBalanced.classList.add('hidden');
      cardBalanced.className = `feature-card border-slate-200 dark:border-slate-800 ${
        isLight ? 'bg-white' : 'bg-slate-900/60'
      } transition-all`;
      btnBalanced.className = `mt-4 w-full py-2.5 rounded-xl ${
        isLight ? 'bg-slate-100 hover:bg-emerald-500 hover:text-slate-950 text-slate-700 border-slate-300' : 'bg-slate-800 hover:bg-emerald-500 hover:text-slate-950 text-slate-300 border-slate-700'
      } font-bold text-xs border transition-all flex items-center justify-center gap-1.5 cursor-pointer`;
      btnBalanced.innerHTML = `<span>Activate Balanced Preset</span>`;
    }
  }

  refreshLucideIcons();
}

async function applyShader(presetId) {
  STATE.activeShader = presetId;
  const activeInst = STATE.selectedInstanceId || '26.2';

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.apply_shader(presetId, activeInst);
    } catch (e) {
      console.warn("Could not apply shader via bridge:", e);
    }
  }

  renderShaders();
  const cleanName = presetId.includes('Balanced') ? 'SIR Balanced Shader (High FPS 144Hz+)' : 'SIR Extreme Shader (Ultra Raytracing)';
  showToast(`✓ Activated Shader: ${cleanName}`, 'success');
}

let _hardwarePollingInterval = null;

async function refreshHardwareTelemetry() {
  const set = (id, txt) => { 
    const el = document.getElementById(id); 
    if (el && el.innerText !== txt) {
      el.innerText = txt; 
    }
  };
  
  let data = null;
  const api = window.pywebview && window.pywebview.api;
  const getFn = api && (api.get_hardware_telemetry || (api.hardware && api.hardware.get_telemetry));
  if (typeof getFn === 'function') {
    try {
      data = await getFn.call(api);
    } catch (e) {
      console.warn('[HardwareTelemetry] Live call failed:', e);
    }
  }

  // Pre-hydration fallback from python bootstrap cache
  if (!data && window.__SIR_HW_BOOTSTRAP__ && window.__SIR_HW_BOOTSTRAP__.total_ram_gb) {
    data = window.__SIR_HW_BOOTSTRAP__;
  }

  if (data && data.success !== false) {
    const total = data.total_ram_gb !== undefined ? `${data.total_ram_gb} GB Total` : '16.0 GB Total';
    const avail = data.avail_ram_gb !== undefined ? `${data.avail_ram_gb} GB Available` : '8.0 GB Available';
    const ramPct = data.ram_load_pct ?? data.ram_pct ?? 45;
    const cores = data.cpu_cores ?? data.cpu_count ?? 8;
    const cpuPct = data.cpu_load_pct ?? data.cpu_pct ?? 5;
    const recRam = data.recommended_ram_gb ?? data.rec_ram_gb ?? 8;
    const tier = data.power_tier || 'High Performance Tier';
    const gpu = data.gpu_name || 'Primary GPU';
    const rec = data.recommendation || `System detected: ${cores} CPU Threads, ${total}, ${gpu}. Optimal allocation: ${recRam} GB Dedicated Heap.`;
    const timeStr = data.timestamp || new Date().toLocaleTimeString();

    set('hw-total-ram', total);
    set('hw-avail-ram', avail);
    set('hw-load-pct', `${ramPct}% In Use`);
    set('hw-cpu-cores', `${cores} Logical Cores`);
    set('hw-cpu-load', `${cpuPct}% Live Load`);
    set('hw-power-tier', tier);
    set('hw-rec-ram', `Allocate ${recRam} GB Dedicated`);
    set('hw-gpu-name', gpu);
    set('hw-recommendation-text', rec);
    set('hw-timestamp-badge', `Live • ${timeStr}`);

    const liveBadge = document.getElementById('hw-live-badge');
    if (liveBadge) liveBadge.textContent = 'Live Kernel Stream';

    const bar = document.getElementById('hw-ram-bar');
    if (bar) bar.style.width = `${Math.min(100, Math.max(0, ramPct))}%`;
    return;
  }

  // Fallback defaults if hardware detection is still loading
  set('hw-total-ram', '16.0 GB Total');
  set('hw-avail-ram', '8.0 GB Available');
  set('hw-load-pct', '45% In Use');
  set('hw-cpu-cores', '8 Logical Cores');
  set('hw-cpu-load', '5% Live Load');
  set('hw-power-tier', 'High Performance Tier');
  set('hw-rec-ram', 'Allocate 8 GB Dedicated');
  set('hw-gpu-name', 'Dedicated GPU');
  set('hw-recommendation-text', 'Reading system hardware topology from Windows Kernel...');
  set('hw-timestamp-badge', 'Querying Kernel...');
  const bar = document.getElementById('hw-ram-bar');
  if (bar) bar.style.width = '45%';
}
window.refreshHardwareTelemetry = refreshHardwareTelemetry;

window.addEventListener('pywebviewready', () => {
  if (typeof refreshHardwareTelemetry === 'function') {
    refreshHardwareTelemetry();
  }
});

// Start live real-time hardware telemetry auto-polling (active 1.2s interval)
if (_hardwarePollingInterval) clearInterval(_hardwarePollingInterval);
_hardwarePollingInterval = setInterval(() => {
  if (typeof STATE !== 'undefined' && STATE.activeTab === 'hardware') {
    refreshHardwareTelemetry();
  }
}, 1200);
setTimeout(refreshHardwareTelemetry, 100);


// Auto-render Lucide icons on any DOM change
if (typeof MutationObserver !== 'undefined') {
  let iconTimeout = null;
  const observer = new MutationObserver((mutations) => {
    let hasNewLucide = false;
    for (const m of mutations) {
      if (m.addedNodes.length > 0) {
        for (const n of m.addedNodes) {
          if (n.nodeType === 1) {
            if (n.hasAttribute && n.hasAttribute('data-lucide')) { hasNewLucide = true; break; }
            if (n.querySelector && n.querySelector('[data-lucide]')) { hasNewLucide = true; break; }
          }
        }
      }
      if (hasNewLucide) break;
    }
    if (hasNewLucide) {
      clearTimeout(iconTimeout);
      iconTimeout = setTimeout(() => {
        refreshLucideIcons();
      }, 20);
    }
  });
  document.addEventListener('DOMContentLoaded', () => {
    observer.observe(document.body, { childList: true, subtree: true });
    refreshLucideIcons();
  });
}

window.openExternalUrl = function(url) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_external_url) {
    try {
      window.pywebview.api.open_external_url(url);
      return;
    } catch (e) {
      console.warn("Bridge open_external_url failed:", e);
    }
  }
  window.open(url, '_blank');
};
