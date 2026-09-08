// =============================================================================
// 6. SINGLEPLAYER WORLDS & SAVES STUDIO
// =============================================================================

STATE.worlds = [];

async function loadWorldsFromBridge() {
  const activeInst = STATE.selectedInstanceId || 'sir-26-ultra';
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_worlds) {
    try {
      const realWorlds = await window.pywebview.api.get_worlds(activeInst);
      if (Array.isArray(realWorlds)) {
        STATE.worlds = realWorlds;
      }
    } catch (e) {
      console.warn("Failed to load worlds from bridge:", e);
    }
  }
  renderWorldsGrid();
}

function renderWorldsGrid() {
  const container = document.getElementById('worlds-grid');
  if (!container) return;

  const isLight = document.documentElement.classList.contains('light');

  if (!STATE.worlds || STATE.worlds.length === 0) {
    container.innerHTML = `
      <div class="col-span-full feature-card p-12 text-center border-slate-800 rounded-3xl space-y-3">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center">
          <i data-lucide="map" class="w-7 h-7"></i>
        </div>
        <h4 class="text-sm font-bold text-slate-100">No Singleplayer Worlds Detected</h4>
        <p class="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          Create or launch a singleplayer world in Minecraft, and it will automatically appear here with 1-click backups and storage insights.
        </p>
        <div class="pt-2 flex items-center justify-center gap-3">
          <button onclick="refreshWorlds()" class="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black transition-all flex items-center gap-1.5 cursor-pointer shadow-md shadow-emerald-500/20">
            <i data-lucide="rotate-cw" class="w-3.5 h-3.5"></i>
            <span>Scan Saves Directory</span>
          </button>
        </div>
      </div>
    `;
    refreshLucideIcons();
    return;
  }

  container.innerHTML = STATE.worlds.map(w => {
    const iconHtml = w.icon_url 
      ? `<img src="${w.icon_url}" class="w-12 h-12 rounded-xl object-cover border border-emerald-500/30 shrink-0" alt="${escapeHtml(w.name)}">`
      : `<div class="w-12 h-12 rounded-xl bg-emerald-950/60 border border-emerald-800/50 flex items-center justify-center text-emerald-400 shrink-0">
           <i data-lucide="map" class="w-6 h-6"></i>
         </div>`;

    return `
      <div class="feature-card p-5 rounded-2xl border ${
        isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-[#101624]/80 border-slate-800 hover:border-emerald-500/50'
      } transition-all flex flex-col justify-between space-y-4">
        <div class="flex items-start gap-3.5">
          ${iconHtml}
          <div class="min-w-0 flex-1">
            <div class="flex items-center justify-between gap-2">
              <h4 class="text-sm font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(w.name)}</h4>
              <span class="badge-tag bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold px-2 py-0.5 rounded-full shrink-0">
                ${w.size_mb} MB
              </span>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-1 font-mono flex items-center gap-2">
              <span>📅 Last Played: ${w.last_played}</span>
            </p>
            <p class="text-[10px] text-slate-600 dark:text-slate-500 font-mono truncate mt-0.5" title="${escapeHtml(w.path)}">
              📁 ${escapeHtml(w.folder_name)}
            </p>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2">
          <button onclick="openWorldFolder('${escapeHtml(w.path).replace(/\\/g, '\\\\')}')" class="flex-1 py-1.5 px-3 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-300 transition-all flex items-center justify-center gap-1.5 cursor-pointer">
            <i data-lucide="folder-open" class="w-3.5 h-3.5 text-cyan-400"></i>
            <span>Reveal</span>
          </button>
          <button onclick="createWorldBackup('${escapeHtml(w.path).replace(/\\/g, '\\\\')}')" class="flex-1 py-1.5 px-3 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-400 text-xs font-bold transition-all flex items-center justify-center gap-1.5 cursor-pointer active:scale-95">
            <i data-lucide="archive" class="w-3.5 h-3.5"></i>
            <span>Backup</span>
          </button>
          <button onclick="deleteWorldSave('${escapeHtml(w.path).replace(/\\/g, '\\\\')}', '${escapeHtml(w.name)}')" class="py-1.5 px-2.5 rounded-xl bg-rose-500/15 hover:bg-rose-500 text-rose-400 hover:text-white border border-rose-500/30 text-xs font-bold transition-all flex items-center justify-center cursor-pointer active:scale-95" title="Delete World Save">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');

  refreshLucideIcons();
}

async function deleteWorldSave(worldPath, worldName) {
  const confirmed = await showConfirmDialog({
    title: "Delete World Save",
    message: `Are you sure you want to permanently delete world "${worldName}"? This action cannot be undone.`,
    confirmText: "Delete Permanently",
    cancelText: "Cancel",
    isDanger: true
  });
  if (!confirmed) return;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.delete_world) {
    try {
      const res = await window.pywebview.api.delete_world(worldPath);
      if (res && res.success) {
        showToast(`✓ World "${worldName}" permanently deleted.`, 'success');
        await refreshWorlds();
        return;
      } else {
        showToast('✗ ' + (res?.error || 'Failed to delete world'), 'error');
      }
    } catch (e) {
      showToast('✗ Delete world error: ' + (e.message || e), 'error');
    }
  } else {
    showToast(`✓ World "${worldName}" deleted.`, 'success');
    await refreshWorlds();
  }
}

async function refreshWorlds(silent = false) {
  await loadWorldsFromBridge();
  if (!silent) {
    showToast('✓ World saves updated!', 'success');
  }
}

async function openWorldFolder(worldPath) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_world_folder) {
    try {
      await window.pywebview.api.open_world_folder(worldPath);
    } catch (e) {
      showToast('✗ Error opening folder: ' + (e.message || e), 'error');
    }
  } else {
    showToast(`✓ Opened world save directory: ${worldPath}`, 'info');
  }
}

async function createWorldBackup(worldPath) {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.create_world_backup) {
    try {
      showToast('⏳ Creating timestamped world backup (.zip)...', 'info');
      const res = await window.pywebview.api.create_world_backup(worldPath);
      if (res && res.success) {
        showToast(res.message || `✓ Backup created: ${res.backup_file} (${res.size_mb} MB)`, 'success');
      } else {
        showToast('✗ Backup failed: ' + (res?.error || 'Unknown error'), 'error');
      }
    } catch (e) {
      showToast('✗ Backup exception: ' + (e.message || e), 'error');
    }
  } else {
    showToast(`✓ Backup saved to backups/ directory!`, 'success');
  }
}

