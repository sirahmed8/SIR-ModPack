// =============================================================================
// 8. SCREENSHOTS & IN-GAME MEDIA GALLERY STUDIO
// =============================================================================

let GALLERY_STATE = {
  activeScreenshot: null
};

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
    container.innerHTML = screenshots.map((s, idx) => {
      const displayImg = s.preview_url || s.path;
      const displayName = s.filename || s.name || `screenshot_${idx}.png`;
      const displaySize = s.size_kb ? `${s.size_kb} KB` : '';
      const encodedPath = encodeURIComponent(s.path);

      return `
        <div class="feature-card p-3 rounded-2xl border border-slate-800 space-y-2 group hover:border-cyan-500/50 transition-all bg-slate-900/50">
          <div class="aspect-video rounded-xl overflow-hidden bg-slate-950 relative border border-slate-800/80 cursor-pointer" onclick="openScreenshotLightbox('${escapeHtml(s.path)}', '${escapeHtml(displayImg)}', '${escapeHtml(displayName)}')">
            <img src="${escapeHtml(displayImg)}" alt="${escapeHtml(displayName)}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy">
            <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2 justify-between">
              <span class="text-[10px] text-cyan-300 font-mono font-bold bg-cyan-950/80 px-2 py-0.5 rounded-md border border-cyan-500/40">Click to View</span>
              <span class="text-[10px] text-slate-300 font-mono">${escapeHtml(displaySize)}</span>
            </div>
          </div>
          <div class="flex items-center justify-between pt-1">
            <span class="text-xs font-mono font-bold text-slate-300 truncate max-w-[140px]" title="${escapeHtml(displayName)}">${escapeHtml(displayName)}</span>
            <span class="text-[10px] text-slate-500 font-mono">${escapeHtml(s.date || '')}</span>
          </div>
          <div class="flex items-center gap-1.5 pt-1 border-t border-slate-800/60">
            <button onclick="copyScreenshot('${escapeHtml(s.path)}')" class="flex-1 py-1 rounded-lg text-[10px] font-bold bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center gap-1 transition-all" title="Copy image to Windows clipboard">
              <i data-lucide="copy" class="w-3 h-3"></i> Copy
            </button>
            <button onclick="exportScreenshot('${escapeHtml(s.path)}')" class="flex-1 py-1 rounded-lg text-[10px] font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center justify-center gap-1 transition-all" title="Export screenshot">
              <i data-lucide="download" class="w-3 h-3"></i> Export
            </button>
            <button onclick="deleteScreenshot('${escapeHtml(s.path)}')" class="px-2 py-1 rounded-lg text-[10px] font-bold bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 transition-all" title="Delete screenshot">
              <i data-lucide="trash-2" class="w-3 h-3"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');
  }
  refreshLucideIcons();
}
window.refreshScreenshots = refreshScreenshots;
window.renderGalleryGrid = refreshScreenshots;

async function copyScreenshot(filepath) {
  if (!filepath) return;
  if (window.pywebview && window.pywebview.api && window.pywebview.api.copy_screenshot_to_clipboard) {
    try {
      const res = await window.pywebview.api.copy_screenshot_to_clipboard(filepath);
      if (res && res.success) {
        showToast("✓ Screenshot copied to clipboard!", "success");
        return;
      } else {
        showToast(res.error || "Failed to copy image to clipboard", "warning");
        return;
      }
    } catch (e) {
      showToast("Clipboard copy failed: " + e, "warning");
      return;
    }
  }
  showToast("Clipboard copy not supported in this runtime", "info");
}
window.copyScreenshot = copyScreenshot;

async function exportScreenshot(filepath) {
  if (!filepath) return;
  if (window.pywebview && window.pywebview.api && window.pywebview.api.export_screenshot) {
    try {
      const res = await window.pywebview.api.export_screenshot(filepath);
      if (res && res.success) {
        showToast(`✓ Exported to: ${res.exported_to}`, "success");
        return;
      } else if (res && !res.success) {
        showToast(res.error || "Export canceled", "info");
        return;
      }
    } catch (e) {
      showToast("Export error: " + e, "warning");
      return;
    }
  }
  showToast("Exporting screenshot...", "info");
}
window.exportScreenshot = exportScreenshot;

async function deleteScreenshot(filepath) {
  if (!filepath) return;
  if (!confirm("Are you sure you want to delete this screenshot?")) return;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.delete_screenshot) {
    try {
      const res = await window.pywebview.api.delete_screenshot(filepath);
      if (res && res.success) {
        showToast("✓ Screenshot deleted", "success");
        refreshScreenshots();
        return;
      } else {
        showToast(res.error || "Could not delete screenshot", "warning");
        return;
      }
    } catch (e) {
      showToast("Delete error: " + e, "warning");
      return;
    }
  }
}
window.deleteScreenshot = deleteScreenshot;

function openScreenshotLightbox(path, url, name) {
  let modal = document.getElementById('screenshot-lightbox-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'screenshot-lightbox-modal';
    modal.className = 'fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex flex-col items-center justify-center p-6';
    modal.innerHTML = `
      <div class="w-full max-w-5xl flex items-center justify-between pb-3 text-white">
        <span id="lightbox-title" class="font-bold text-sm font-mono truncate"></span>
        <div class="flex items-center gap-2">
          <button id="lightbox-btn-copy" class="px-3 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold hover:bg-cyan-500/30 transition-all flex items-center gap-1.5">
            <i data-lucide="copy" class="w-3.5 h-3.5"></i> Copy
          </button>
          <button id="lightbox-btn-export" class="px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 text-xs font-bold hover:bg-slate-700 transition-all flex items-center gap-1.5">
            <i data-lucide="download" class="w-3.5 h-3.5"></i> Export
          </button>
          <button onclick="closeScreenshotLightbox()" class="w-8 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-300">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
      <div class="max-w-5xl max-h-[80vh] flex items-center justify-center overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
        <img id="lightbox-img" src="" alt="Preview" class="max-w-full max-h-[80vh] object-contain">
      </div>
    `;
    document.body.appendChild(modal);
  }

  document.getElementById('lightbox-title').textContent = name;
  document.getElementById('lightbox-img').src = url;
  document.getElementById('lightbox-btn-copy').onclick = () => copyScreenshot(path);
  document.getElementById('lightbox-btn-export').onclick = () => exportScreenshot(path);

  modal.classList.remove('hidden');
  refreshLucideIcons();
}
window.openScreenshotLightbox = openScreenshotLightbox;

function closeScreenshotLightbox() {
  const modal = document.getElementById('screenshot-lightbox-modal');
  if (modal) modal.classList.add('hidden');
}
window.closeScreenshotLightbox = closeScreenshotLightbox;

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

