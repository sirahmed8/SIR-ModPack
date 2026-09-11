// =============================================================================
// DOWNLOADS MANAGER & NAVBAR NOTIFICATION TRAY
// =============================================================================
window.DOWNLOAD_STATE = {
  activeDownloads: new Map(),
  isOpen: false,
  activeTab: 'downloads'
};

function toggleDownloadHubDropdown() {
  const dropdown = document.getElementById('download-hub-dropdown');
  if (!dropdown) return;
  DOWNLOAD_STATE.isOpen = !DOWNLOAD_STATE.isOpen;
  if (DOWNLOAD_STATE.isOpen) {
    dropdown.classList.remove('hidden');
  } else {
    dropdown.classList.add('hidden');
  }
}
window.toggleDownloadHubDropdown = toggleDownloadHubDropdown;

// Close dropdown on click outside
document.addEventListener('click', (e) => {
  const container = document.getElementById('download-hub-container');
  const dropdown = document.getElementById('download-hub-dropdown');
  if (container && dropdown && !container.contains(e.target) && !dropdown.classList.contains('hidden')) {
    dropdown.classList.add('hidden');
    DOWNLOAD_STATE.isOpen = false;
  }
});

function switchTrayTab(tab) {
  DOWNLOAD_STATE.activeTab = tab;
  const downTab = document.getElementById('tray-tab-downloads');
  const alertTab = document.getElementById('tray-tab-alerts');
  const downView = document.getElementById('tray-downloads-view');
  const alertView = document.getElementById('tray-alerts-view');

  if (tab === 'downloads') {
    if (downTab) downTab.className = "px-2.5 py-1 rounded-lg bg-cyan-500 text-slate-950 font-bold transition-all";
    if (alertTab) alertTab.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium transition-all";
    if (downView) downView.classList.remove('hidden');
    if (alertView) alertView.classList.add('hidden');
  } else {
    if (alertTab) alertTab.className = "px-2.5 py-1 rounded-lg bg-cyan-500 text-slate-950 font-bold transition-all";
    if (downTab) downTab.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-white font-medium transition-all";
    if (alertView) alertView.classList.remove('hidden');
    if (downView) downView.classList.add('hidden');
  }
}
window.switchTrayTab = switchTrayTab;

function addActiveDownload(id, name, instance) {
  const item = {
    id,
    name,
    instance: instance || '26.2',
    progress: 10,
    speed: 'Connecting to Modrinth...',
    status: 'downloading',
    startTime: Date.now()
  };
  DOWNLOAD_STATE.activeDownloads.set(id, item);
  renderDownloadTray();
  updateDownloadBadge();

  // Simulated progressive network stream if backend is non-streaming
  let cur = 10;
  const interval = setInterval(() => {
    const it = DOWNLOAD_STATE.activeDownloads.get(id);
    if (!it || it.status !== 'downloading') {
      clearInterval(interval);
      return;
    }
    if (cur < 90) {
      cur += Math.floor(Math.random() * 15) + 5;
      if (cur > 90) cur = 90;
      const speed = (Math.random() * 3 + 2.5).toFixed(1) + ' MB/s';
      updateDownloadProgress(id, cur, `Downloading... ${speed}`);
    }
  }, 350);
}
window.addActiveDownload = addActiveDownload;

function updateDownloadProgress(id, progressPct, speedStr) {
  const item = DOWNLOAD_STATE.activeDownloads.get(id);
  if (!item) return;
  item.progress = Math.min(100, Math.max(0, progressPct));
  if (speedStr) item.speed = speedStr;
  renderDownloadTray();
}
window.updateDownloadProgress = updateDownloadProgress;

function completeDownload(id, success = true, errorMsg = '') {
  const item = DOWNLOAD_STATE.activeDownloads.get(id);
  if (!item) return;
  item.progress = 100;
  item.status = success ? 'completed' : 'failed';
  item.speed = success ? '✓ Verified & Installed' : (errorMsg || 'Failed');
  renderDownloadTray();
  updateDownloadBadge();
  setTimeout(() => {
    DOWNLOAD_STATE.activeDownloads.delete(id);
    renderDownloadTray();
    updateDownloadBadge();
  }, 4500);
}
window.completeDownload = completeDownload;

function cancelDownload(id) {
  const item = DOWNLOAD_STATE.activeDownloads.get(id);
  if (!item) return;
  item.status = 'cancelled';
  item.speed = 'Cancelled by user';
  showToast(`Cancelled download: ${item.name}`, 'info');
  if (item.abortController) {
    try { item.abortController.abort(); } catch {}
  }
  renderDownloadTray();
  updateDownloadBadge();
  setTimeout(() => {
    DOWNLOAD_STATE.activeDownloads.delete(id);
    renderDownloadTray();
    updateDownloadBadge();
  }, 1200);
}
window.cancelDownload = cancelDownload;

function updateDownloadBadge() {
  const badge = document.getElementById('download-hub-badge');
  const countTag = document.getElementById('download-active-count-tag');
  const count = DOWNLOAD_STATE.activeDownloads.size;
  if (badge) {
    if (count > 0) {
      badge.textContent = count;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }
  if (countTag) {
    countTag.textContent = count > 0 ? `${count} Active` : 'Idle';
    countTag.className = count > 0 
      ? "px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 font-mono text-[10px] font-bold animate-pulse"
      : "px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono text-[10px] font-bold";
  }
}

function renderDownloadTray() {
  const emptyEl = document.getElementById('tray-downloads-empty');
  const listEl = document.getElementById('tray-downloads-list');
  if (!listEl) return;

  const items = Array.from(DOWNLOAD_STATE.activeDownloads.values());
  if (items.length === 0) {
    if (emptyEl) emptyEl.classList.remove('hidden');
    listEl.innerHTML = '';
    return;
  }

  if (emptyEl) emptyEl.classList.add('hidden');
  listEl.innerHTML = items.map(item => `
    <div class="p-3 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2">
      <div class="flex items-center justify-between gap-2">
        <div class="min-w-0 flex-1">
          <h5 class="text-xs font-bold text-white truncate">${item.name}</h5>
          <span class="text-[10px] text-cyan-400 font-mono block">Target: ${item.instance}</span>
        </div>
        ${item.status === 'downloading' ? `
          <button onclick="cancelDownload('${item.id}')" class="px-2 py-1 rounded-lg bg-red-500/15 hover:bg-red-500/25 text-red-400 border border-red-500/30 text-[10px] font-bold transition-all cursor-pointer" title="Cancel Download">
            Cancel
          </button>
        ` : `
          <span class="text-[10px] font-mono text-emerald-400 font-bold">${item.speed}</span>
        `}
      </div>
      <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-300" style="width: ${item.progress}%"></div>
      </div>
      <div class="flex items-center justify-between text-[10px] text-slate-400 font-mono">
        <span>${item.speed}</span>
        <span class="font-bold text-slate-300">${item.progress}%</span>
      </div>
    </div>
  `).join('');
}
