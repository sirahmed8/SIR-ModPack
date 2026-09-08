// =============================================================================
// 8. SCREENSHOTS & IN-GAME MEDIA GALLERY STUDIO
// =============================================================================

async function refreshScreenshots() {
  const container = document.getElementById('gallery-grid');
  if (!container) return;

  let screenshots = [];
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_screenshots) {
    try {
      const activeInst = STATE.selectedInstanceId || '26.2';
      const res = await window.pywebview.api.get_screenshots(activeInst);
      if (res && res.success && Array.isArray(res.screenshots)) {
        screenshots = res.screenshots;
      }
    } catch (e) {
      console.warn("Could not fetch screenshots from bridge:", e);
    }
  }

  if (!screenshots || screenshots.length === 0) {
    container.innerHTML = `
      <div class="col-span-full p-8 text-center rounded-2xl bg-slate-900/40 border border-dashed border-slate-800 space-y-3">
        <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
          <i data-lucide="image" class="w-6 h-6"></i>
        </div>
        <div>
          <h4 class="text-sm font-bold text-slate-200">No Screenshots Captured Yet</h4>
          <p class="text-xs text-slate-400 mt-1">Press F2 in-game to capture high-resolution moments with SIR Shaders active.</p>
        </div>
        <div class="flex items-center justify-center gap-3 pt-2">
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-400 font-mono text-[11px]">
            <i data-lucide="camera" class="w-3.5 h-3.5 text-cyan-400"></i>
            <span>Captures save to instance /screenshots</span>
          </div>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = screenshots.map(s => `
      <div class="feature-card p-3 rounded-2xl border border-slate-800 space-y-2 group">
        <div class="aspect-video rounded-xl overflow-hidden bg-slate-950 relative border border-slate-800/80">
          <img src="${escapeHtml(s.url || s.path)}" alt="${escapeHtml(s.name)}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
        </div>
        <div class="flex items-center justify-between pt-1">
          <span class="text-xs font-mono font-bold text-slate-300 truncate">${escapeHtml(s.name)}</span>
          <span class="text-[10px] text-slate-500 font-mono">${escapeHtml(s.date || '')}</span>
        </div>
      </div>
    `).join('');
  }
  refreshLucideIcons();
}
window.refreshScreenshots = refreshScreenshots;
window.renderGalleryGrid = refreshScreenshots;

function openScreenshotsDir() {
  if (window.pywebview && window.pywebview.api) {
    const activeInst = STATE.selectedInstanceId || '26.2';
    try {
      if (window.pywebview.api.open_screenshots_folder) {
        window.pywebview.api.open_screenshots_folder(activeInst);
        return;
      }
      window.pywebview.api.open_instance_folder(activeInst);
      return;
    } catch {}
  }
  showToast("Opening screenshots folder...", "info");
}
window.openScreenshotsDir = openScreenshotsDir;
