// --- STORE & MOD BROWSER ---
function toggleStoreSortDropdown() {
  toggleCustomDropdown('store-sort-menu');
}

function selectStoreSort(s, labelText) {
  STATE.storeSort = s;
  const map = { downloads: 'Most Downloads', popularity: 'Popularity', updated: 'Recently Updated', newest: 'Newest' };
  const labelEl = document.getElementById('store-sort-label');
  if (labelEl) labelEl.textContent = labelText || map[s] || s;
  toggleCustomDropdown('store-sort-menu');
  executeStoreSearch();
}

function setStoreProvider(p) {
  STATE.storeProvider = p;
  ['modrinth', 'curseforge'].forEach(id => {
    const btn = document.getElementById('btn-provider-' + id);
    if (!btn) return;
    if (id === p) {
      btn.className = "px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-500 text-slate-950 shadow-sm flex items-center gap-1.5";
    } else {
      btn.className = "px-3 py-1.5 rounded-lg text-xs font-bold text-slate-400 hover:text-slate-200 flex items-center gap-1.5";
    }
  });
  executeStoreSearch();
}

function setStoreType(t) {
  STATE.storeType = t;
  const pills = document.querySelectorAll('#store-type-pills .filter-pill');
  pills.forEach(btn => {
    if (btn.id === `type-pill-${t}`) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
  executeStoreSearch();
}

async function executeStoreSearch() {
  const input = document.getElementById('store-search-input');
  const query = input ? input.value.trim() : (STATE.storeSearchQuery || '');
  const container = document.getElementById('store-results-container');
  if (!container) return;

  STATE.storeSearchQuery = query;

  container.innerHTML = `<div class="col-span-full flex items-center justify-center gap-3 py-12">
    <div class="w-5 h-5 border-2 border-cyan-500/40 border-t-cyan-400 rounded-full animate-spin"></div>
    <span class="text-xs text-slate-400">Fetching live projects from Modrinth API...</span>
  </div>`;

  try {
    const type = STATE.storeType || 'mod';
    const sort = STATE.storeSort || 'downloads';
    const cleanType = type === 'shader' ? 'shader' : (type === 'resourcepack' ? 'resourcepack' : (type === 'modpack' ? 'modpack' : 'mod'));
    const url = `https://api.modrinth.com/v2/search?query=${encodeURIComponent(query)}&facets=[[%22project_type:${cleanType}%22]]&limit=24&index=${sort}`;

    const resp = await fetch(url);
    if (!resp.ok) throw new Error('API status ' + resp.status);
    const data = await resp.json();
    const hits = data.hits || [];

    if (!hits.length) {
      container.innerHTML = `<div class="col-span-full text-center py-10 text-slate-400 text-xs">No projects found for "${escapeHtml(query)}". Try another keyword.</div>`;
      return;
    }

    STATE.storeHits = hits;
    STATE.storeOffset = 0;
    STATE.storeTotalHits = data.total_hits || hits.length;

    renderStoreHits(hits, false);
  } catch (err) {
    container.innerHTML = `<div class="col-span-full text-center py-10 text-rose-400 text-xs">Search error: ${escapeHtml(err.message)}. Check your internet connection.</div>`;
  }
}

function renderStoreHits(hits, isAppend) {
  const container = document.getElementById('store-results-container');
  if (!container) return;

  const isLight = document.documentElement.classList.contains('light');
  const cleanType = STATE.storeType || 'mod';

  const cardsHtml = hits.map(h => {
    const name = h.title || 'Untitled';
    const desc = h.description || 'High quality community creation.';
    const dlCount = h.downloads || 0;
    const downloads = dlCount > 1e6 ? (dlCount / 1e6).toFixed(1) + 'M' : (dlCount > 1e3 ? (dlCount / 1e3).toFixed(0) + 'K' : dlCount);
    const icon = h.icon_url || 'https://raw.githubusercontent.com/modrinth/art/master/brand/logo.png';
    const author = h.author || 'Creator';
    const categories = (h.categories || []).slice(0, 2).map(c => `<span class="badge-tag text-[9px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">${c}</span>`).join(' ');

    return `
      <div class="feature-card p-4 rounded-2xl border transition-all ${
        isLight ? 'bg-white border-slate-200 hover:border-slate-300' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
      } flex items-center justify-between gap-4">
        <div class="flex items-center gap-3.5 min-w-0 flex-1">
          <img src="${escapeHtml(icon)}" class="w-11 h-11 rounded-2xl object-cover border border-slate-700/80 shrink-0 shadow-md" onerror="this.src='https://raw.githubusercontent.com/modrinth/art/master/brand/logo.png'">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <h4 class="text-xs font-black text-slate-900 dark:text-slate-100 truncate">${escapeHtml(name)}</h4>
              <span class="text-[10px] text-slate-400">by ${escapeHtml(author)}</span>
              ${categories}
            </div>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 mt-1 line-clamp-1">${escapeHtml(desc)}</p>
          </div>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <span class="text-[10px] font-mono text-slate-400">⬇ ${downloads}</span>
          <button onclick="installOnlineModToProfile('${escapeHtml(h.slug || h.id)}', '${escapeHtml(name)}')" class="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-slate-950 text-xs font-black shadow-md shadow-cyan-500/20 transition-all hover:scale-105 active:scale-95 flex items-center gap-1.5 cursor-pointer">
            <i data-lucide="download" class="w-3.5 h-3.5"></i>
            <span>Install</span>
          </button>
        </div>
      </div>
    `;
  }).join('');

  // Remove existing load more button
  const oldBtn = document.getElementById('store-load-more-btn-box');
  if (oldBtn) oldBtn.remove();

  if (isAppend) {
    container.insertAdjacentHTML('beforeend', cardsHtml);
  } else {
    container.innerHTML = cardsHtml;
  }

  // Add Load More button if more projects exist
  const currentCount = (STATE.storeOffset || 0) + hits.length;
  if (currentCount < (STATE.storeTotalHits || 0)) {
    const loadMoreHtml = `
      <div id="store-load-more-btn-box" class="col-span-full pt-4 text-center">
        <button onclick="loadMoreStoreProjects()" class="px-8 py-3 rounded-2xl bg-white dark:bg-slate-900 hover:bg-cyan-500/10 border border-slate-300 dark:border-cyan-500/30 text-slate-800 dark:text-cyan-400 font-bold text-xs shadow-md hover:scale-105 active:scale-95 transition-all inline-flex items-center gap-2 cursor-pointer">
          <i data-lucide="flame" class="w-4 h-4 text-amber-500"></i>
          <span>View More Projects (+24 of ${(STATE.storeTotalHits || 0).toLocaleString()} available)</span>
        </button>
      </div>
    `;
    container.insertAdjacentHTML('beforeend', loadMoreHtml);
  }

  refreshLucideIcons();
}

async function loadMoreStoreProjects() {
  const btnBox = document.getElementById('store-load-more-btn-box');
  if (btnBox) {
    btnBox.innerHTML = `
      <div class="inline-flex items-center gap-2 text-xs text-cyan-400 font-bold">
        <div class="w-4 h-4 border-2 border-cyan-400/40 border-t-cyan-400 rounded-full animate-spin"></div>
        <span>Fetching more projects...</span>
      </div>
    `;
  }

  const nextOffset = (STATE.storeOffset || 0) + 24;
  const query = STATE.storeSearchQuery || '';
  const type = STATE.storeType || 'mod';
  const sort = STATE.storeSort || 'downloads';
  const cleanType = type === 'shader' ? 'shader' : (type === 'resourcepack' ? 'resourcepack' : (type === 'modpack' ? 'modpack' : 'mod'));
  const url = `https://api.modrinth.com/v2/search?query=${encodeURIComponent(query)}&facets=[[%22project_type:${cleanType}%22]]&limit=24&offset=${nextOffset}&index=${sort}`;

  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error('API status ' + resp.status);
    const data = await resp.json();
    const hits = data.hits || [];
    STATE.storeOffset = nextOffset;
    renderStoreHits(hits, true);
  } catch (err) {
    showToast(`Failed to load more: ${err.message}`, 'error');
    if (btnBox) btnBox.remove();
  }
}

async function installOnlineModToProfile(slug, title) {
  const activeInst = STATE.selectedInstanceId || '26.2';
  showToast(`⏳ Downloading & installing ${title} to ${activeInst}...`, 'info');
  
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.install_online_mod(slug, activeInst);
      if (res && res.success) {
        showToast(res.message || `✓ Installed ${title}!`, 'success');
        if (typeof loadModsFromBridge === 'function') loadModsFromBridge();
      } else {
        showToast(`✗ Failed to install ${title}: ${res?.error || 'Unknown error'}`, 'error');
      }
    } catch (e) {
      showToast(`✗ Install error: ${e.message || e}`, 'error');
    }
  } else {
    showToast(`✓ [Simulation] Installed ${title} into profile ${activeInst}!`, 'success');
  }
}

async function checkModUpdatesLive() {
  const activeInst = STATE.selectedInstanceId || '26.2';
  showToast(`🔍 Scanning ${activeInst} mods for latest verified updates...`, 'info');
  
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.check_mod_updates(activeInst);
      if (res && res.success) {
        showToast(res.message || '✓ All mods are up-to-date!', 'success');
      } else {
        showToast(`✗ Scan error: ${res?.error || 'Could not verify mod hashes'}`, 'error');
      }
    } catch (e) {
      showToast(`✗ Scan failed: ${e.message || e}`, 'error');
    }
  } else {
    showToast(`✓ [Simulation] Checked 48 mods: All mods are up-to-date!`, 'success');
  }
}

