/**
 * command_palette.js — Raycast / Linear Universal Spotlight Command Palette (Ctrl+K / Cmd+K)
 * Provides spotlight fuzzy-search for profiles, navigation, mods, shaders, and system diagnostics.
 */

(function () {
  'use strict';

  let isOpen = false;
  let activeIndex = 0;
  let flatResults = [];

  const SEMANTIC_GROUPS = [
    'PROFILES & ENGINES',
    'NAVIGATION',
    'MODS & PACKS',
    'SYSTEM TOOLS'
  ];

  const STATIC_COMMANDS = [
    // PROFILES & ENGINES
    { id: 'launch-active', title: 'Launch Active Game Profile', subtitle: 'Start Minecraft immediately with active configuration', group: 'PROFILES & ENGINES', icon: 'play', action: () => { if (window.launchGame) window.launchGame(); } },
    { id: 'profile-26-ultra', title: 'Modern 26.2 Ultra Fidelity', subtitle: 'Fabric 26.2 • SIR Modern Extreme Shaders • 24 Chunks', group: 'PROFILES & ENGINES', icon: 'sparkles', action: () => { if (window.selectInstance) window.selectInstance('26.2-ultra'); if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'profile-26-balanced', title: 'Modern 26.2 Balanced (144Hz)', subtitle: 'Fabric 26.2 • Balanced Shaders • 16 Chunks', group: 'PROFILES & ENGINES', icon: 'zap', action: () => { if (window.selectInstance) window.selectInstance('26.2-balanced'); if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'profile-26-perf', title: 'Modern 26.2 Competitive FPS', subtitle: 'Fabric 26.2 • Max FPS • 8 Chunks', group: 'PROFILES & ENGINES', icon: 'gauge', action: () => { if (window.selectInstance) window.selectInstance('26.2-performance'); if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'profile-189-ultra', title: 'Legacy 1.8.9 Ultra PvP', subtitle: 'Forge 1.8.9 • PvP Shaders • 16 Chunks', group: 'PROFILES & ENGINES', icon: 'swords', action: () => { if (window.selectInstance) window.selectInstance('1.8.9-ultra'); if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'profile-189-balanced', title: 'Legacy 1.8.9 Balanced PvP', subtitle: 'Forge 1.8.9 • Smooth PvP • 12 Chunks', group: 'PROFILES & ENGINES', icon: 'zap', action: () => { if (window.selectInstance) window.selectInstance('1.8.9-balanced'); if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'profile-189-perf', title: 'Legacy 1.8.9 Competitive PvP', subtitle: 'Forge 1.8.9 • 500+ FPS Hypixel Mode', group: 'PROFILES & ENGINES', icon: 'gauge', action: () => { if (window.selectInstance) window.selectInstance('1.8.9-performance'); if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'profile-26-vanilla', title: 'Pure Vanilla 26.2', subtitle: 'Unmodified Official Minecraft 26.2', group: 'PROFILES & ENGINES', icon: 'box', action: () => { if (window.selectInstance) window.selectInstance('26.2'); if (window.switchTab) window.switchTab('dashboard'); } },

    // NAVIGATION
    { id: 'nav-dashboard', title: 'Launchpad Dashboard', subtitle: 'Quick launch, telemetry overview, and active player card', group: 'NAVIGATION', icon: 'compass', action: () => { if (window.switchTab) window.switchTab('dashboard'); } },
    { id: 'nav-mods', title: 'Mods & Content Hub', subtitle: 'Manage 240+ installed mods, dropzone & mod store', group: 'NAVIGATION', icon: 'package', action: () => { if (window.switchTab) window.switchTab('mods'); } },
    { id: 'nav-instances', title: 'Profiles & Instances Matrix', subtitle: 'View all 8 Modern & Legacy game profiles', group: 'NAVIGATION', icon: 'layers', action: () => { if (window.switchTab) window.switchTab('instances'); } },
    { id: 'nav-shaders', title: 'Shaders Studio', subtitle: 'Configure SIR Modern 2048 & Balanced shaders', group: 'NAVIGATION', icon: 'sun', action: () => { if (window.switchTab) window.switchTab('shaders'); } },
    { id: 'nav-packs', title: 'Resource Packs Studio', subtitle: 'Manage 3D POM textures and animations', group: 'NAVIGATION', icon: 'folder-archive', action: () => { if (window.switchTab) window.switchTab('packs'); } },
    { id: 'nav-servers', title: 'Multiplayer Server Manager', subtitle: 'Server controls, RCON console, backup & restore', group: 'NAVIGATION', icon: 'server', action: () => { if (window.switchTab) window.switchTab('servers'); } },
    { id: 'nav-skins', title: 'Skin & Cosmetics Studio', subtitle: '3D interactive preview, animated capes', group: 'NAVIGATION', icon: 'user', action: () => { if (window.switchTab) window.switchTab('skins'); } },
    { id: 'nav-settings', title: 'System & Hardware Settings', subtitle: 'RAM allocation, JVM flags, GPU selector & window lifecycle', group: 'NAVIGATION', icon: 'settings', action: () => { if (window.switchTab) window.switchTab('settings'); } },

    // MODS & PACKS
    { id: 'shader-sir-modern', title: 'SIR Modern 2048 Shaders', subtitle: 'Volumetric fog, screen-space reflections & 3D relief', group: 'MODS & PACKS', icon: 'sun', action: () => { if (window.switchTab) window.switchTab('shaders'); } },
    { id: 'shader-complementary', title: 'Complementary Reimagined Shaders', subtitle: 'High-speed lighting passes & crystal clear water refraction', group: 'MODS & PACKS', icon: 'sparkles', action: () => { if (window.switchTab) window.switchTab('shaders'); } },
    { id: 'store-search-mods', title: 'Browse Modrinth Store', subtitle: 'Explore and 1-click install community mods via Python bridge', group: 'MODS & PACKS', icon: 'download', action: () => { if (window.switchTab) window.switchTab('mods'); const btn = document.getElementById('tab-btn-store'); if (btn) btn.click(); } },

    // SYSTEM TOOLS
    { id: 'lunar-sync', title: 'Sync Lunar Client Profiles Now (C: ↔ D:)', subtitle: 'Bidirectional sync for options, keybinds & packs', group: 'SYSTEM TOOLS', icon: 'moon', action: () => { if (window.syncAllLunarProfiles) window.syncAllLunarProfiles(); } },
    { id: 'tool-repair', title: 'Run Asset Integrity & Self-Repair Scan', subtitle: 'Verify SHA-256 hashes and heal corrupted files', group: 'SYSTEM TOOLS', icon: 'wrench', action: () => { if (window.runSelfRepair) window.runSelfRepair(); } },
    { id: 'tool-open-appdata', title: 'Open Minecraft AppData Directory', subtitle: 'Explore local game files on disk', group: 'SYSTEM TOOLS', icon: 'folder-open', action: () => { if (window.pywebview && window.pywebview.api && window.pywebview.api.open_instance_folder) window.pywebview.api.open_instance_folder(); } },
    { id: 'tool-feedback', title: 'Developer Feedback Highway', subtitle: 'Report errors or send feature suggestions with diagnostics', group: 'SYSTEM TOOLS', icon: 'message-square-plus', action: () => { if (window.openFeedbackModal) window.openFeedbackModal('issue'); } },
    { id: 'tool-rshift-guide', title: 'In-Game HUD Menu Guide', subtitle: 'Access Armor, Potion, Inventory HUD+ with Right Shift', group: 'SYSTEM TOOLS', icon: 'help-circle', action: () => { if (window.showToast) window.showToast('ℹ️ Press RIGHT SHIFT in-game to toggle the Client HUD menu!', 'info'); } }
  ];

  function initCommandPalette() {
    createPaletteDOM();
    bindKeyboardShortcuts();
  }

  function createPaletteDOM() {
    if (document.getElementById('command-palette-modal')) return;

    const modal = document.createElement('div');
    modal.id = 'command-palette-modal';
    modal.className = 'fixed inset-0 z-[9999] hidden flex items-start justify-center pt-[10vh] px-4 backdrop-blur-md bg-black/70 transition-all duration-200';
    modal.innerHTML = `
      <div id="command-palette-container" class="w-full max-w-2xl rounded-2xl bg-[#0b0f19] border border-cyan-500/30 shadow-2xl shadow-cyan-950/60 overflow-hidden flex flex-col max-h-[75vh] animate-in fade-in-0 zoom-in-95 duration-150">
        <!-- Single Seamless Spotlight Search Header (No nested box) -->
        <div class="relative flex items-center gap-3.5 px-5 py-4 border-b border-slate-800/80 bg-[#0d1220]">
          <i data-lucide="search" class="w-5 h-5 text-cyan-400 shrink-0"></i>
          <input
            id="command-palette-input"
            type="text"
            placeholder="Type a command, launch profile, or search mods..."
            class="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 font-medium border-0 ring-0 focus:ring-0 focus:outline-none"
            style="outline: none !important; box-shadow: none !important; border: none !important;"
            autocomplete="off"
            spellcheck="false"
          />
          <div class="flex items-center gap-2 shrink-0 select-none">
            <span class="px-2 py-0.5 rounded-md bg-slate-800/90 border border-slate-700/80 text-[10px] font-mono text-slate-400 font-bold">ESC</span>
            <button onclick="closeCommandPalette()" class="w-6 h-6 rounded-md hover:bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center cursor-pointer transition-colors" title="Close (Esc)">
              <i data-lucide="x" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <!-- Ergonomic Results List with Bottom Gradient Mask & pb-6 -->
        <div
          id="command-palette-results"
          class="p-2.5 px-3 overflow-y-auto flex-1 custom-scrollbar space-y-1 pb-6"
          style="max-height: 480px; mask-image: linear-gradient(to bottom, black calc(100% - 40px), transparent 100%); -webkit-mask-image: linear-gradient(to bottom, black calc(100% - 40px), transparent 100%);"
        >
          <!-- Results injected dynamically -->
        </div>

        <!-- Footer / Keyboard hints -->
        <div class="p-2.5 px-4 bg-[#080c14] border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 select-none">
          <div class="flex items-center gap-3">
            <span class="flex items-center gap-1"><span class="font-mono bg-slate-800/90 border border-slate-700/60 px-1 rounded text-slate-300">↑↓</span> Navigate</span>
            <span class="flex items-center gap-1"><span class="font-mono bg-slate-800/90 border border-slate-700/60 px-1 rounded text-slate-300">↵</span> Select</span>
            <span class="flex items-center gap-1"><span class="font-mono bg-slate-800/90 border border-slate-700/60 px-1 rounded text-slate-300">ESC</span> Close</span>
          </div>
          <span class="text-cyan-400/90 font-mono font-bold text-[10px] tracking-wider">SIR COMMAND PALETTE</span>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.addEventListener('click', (e) => {
      if (e.target === modal) closePalette();
    });

    const input = document.getElementById('command-palette-input');
    input.addEventListener('input', () => {
      filterCommands(input.value.trim());
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateResults(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateResults(-1);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        executeActiveResult();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        closePalette();
      }
    });
  }

  function bindKeyboardShortcuts() {
    window.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        togglePalette();
      }
    });
  }

  function togglePalette() {
    if (isOpen) {
      closePalette();
    } else {
      openPalette();
    }
  }

  function openPalette() {
    isOpen = true;
    const modal = document.getElementById('command-palette-modal');
    if (!modal) return;
    const container = document.getElementById('command-palette-container');
    modal.classList.remove('hidden');
    if (container) {
      container.classList.remove('palette-exit', 'animate-out', 'fade-out-0', 'zoom-out-95');
      container.classList.add('palette-enter');
    }
    const input = document.getElementById('command-palette-input');
    if (input) {
      input.value = '';
      setTimeout(() => input.focus(), 50);
    }
    filterCommands('');
    if (window.lucide) lucide.createIcons();
  }

  function closePalette() {
    if (!isOpen) return;
    isOpen = false;
    const modal = document.getElementById('command-palette-modal');
    if (!modal) return;
    const container = document.getElementById('command-palette-container');
    if (container) {
      container.classList.remove('palette-enter', 'animate-in', 'fade-in-0', 'zoom-in-95');
      container.classList.add('palette-exit');
      setTimeout(() => {
        modal.classList.add('hidden');
        container.classList.remove('palette-exit');
      }, 140);
    } else {
      modal.classList.add('hidden');
    }
  }

  function getDynamicModCommands() {
    const modCommands = [];
    const sourceMods = (window.STATE && Array.isArray(window.STATE.mods) && window.STATE.mods.length > 0)
      ? window.STATE.mods
      : ((window.state && Array.isArray(window.state.installedMods)) ? window.state.installedMods : []);

    sourceMods.slice(0, 150).forEach((mod) => {
      const name = mod.name || mod.id || mod.filename || 'Unknown Mod';
      const desc = mod.description || (mod.version ? `Version: ${mod.version}` : 'Installed Minecraft Mod');
      modCommands.push({
        id: `mod-${mod.id || name}`,
        title: name,
        subtitle: desc,
        group: 'MODS & PACKS',
        icon: 'package',
        action: () => {
          if (window.switchTab) window.switchTab('mods');
          const searchInput = document.getElementById('mods-search-input');
          if (searchInput) {
            searchInput.value = name;
            if (window.filterInstalledMods) window.filterInstalledMods();
          }
        }
      });
    });
    return modCommands;
  }

  function filterCommands(query) {
    const all = [...STATIC_COMMANDS, ...getDynamicModCommands()];
    const q = query.toLowerCase();

    let matches = [];
    if (!q) {
      matches = STATIC_COMMANDS;
    } else {
      matches = all.filter((cmd) => {
        return cmd.title.toLowerCase().includes(q) ||
               cmd.subtitle.toLowerCase().includes(q) ||
               cmd.group.toLowerCase().includes(q);
      }).slice(0, 30);
    }

    // Group matches under semantic headers
    const grouped = {};
    SEMANTIC_GROUPS.forEach(g => { grouped[g] = []; });

    matches.forEach(item => {
      const g = item.group || 'SYSTEM TOOLS';
      if (!grouped[g]) grouped[g] = [];
      grouped[g].push(item);
    });

    // Flatten for keyboard traversal
    flatResults = [];
    SEMANTIC_GROUPS.forEach(g => {
      grouped[g].forEach(item => flatResults.push(item));
    });

    activeIndex = 0;
    renderResults(grouped);
  }

  function renderResults(grouped) {
    const container = document.getElementById('command-palette-results');
    if (!container) return;

    if (flatResults.length === 0) {
      container.innerHTML = `
        <div class="py-12 text-center text-slate-500">
          <i data-lucide="help-circle" class="w-8 h-8 mx-auto mb-2 text-slate-600"></i>
          <p class="text-sm font-bold text-slate-300">No matching commands or mods found</p>
          <p class="text-xs text-slate-500 mt-1">Try searching for a mod name, 'profile', 'lunar', or 'preset'</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    let html = '';
    let globalIdx = 0;

    SEMANTIC_GROUPS.forEach(groupName => {
      const items = grouped[groupName] || [];
      if (items.length === 0) return;

      html += `
        <div class="px-3 pt-2.5 pb-1 flex items-center justify-between select-none">
          <span class="text-[10px] font-black uppercase tracking-wider text-slate-400">${groupName}</span>
          <span class="px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-500/30 text-[9px] font-mono font-bold">${items.length}</span>
        </div>
      `;

      items.forEach(item => {
        const isSelected = globalIdx === activeIndex;
        const activeClass = isSelected
          ? 'bg-cyan-500/15 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.15)] text-white'
          : 'bg-slate-900/40 hover:bg-cyan-500/10 border-transparent hover:border-cyan-500/30 text-slate-300';

        html += `
          <div
            data-palette-idx="${globalIdx}"
            class="palette-item h-11 px-3 py-1 rounded-xl border flex items-center justify-between gap-3 cursor-pointer transition-all duration-150 ${activeClass}"
          >
            <div class="flex items-center gap-3 min-w-0 flex-1">
              <div class="w-7 h-7 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center shrink-0 text-cyan-400">
                <i data-lucide="${item.icon || 'terminal'}" class="w-3.5 h-3.5"></i>
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-xs font-bold truncate ${isSelected ? 'text-white' : 'text-slate-100'}">${escapeHtml(item.title)}</div>
                <div class="text-[10px] text-slate-400 truncate leading-tight">${escapeHtml(item.subtitle)}</div>
              </div>
            </div>
            <div class="flex items-center gap-1.5 shrink-0 select-none">
              <span class="px-1.5 py-0.5 rounded-md bg-slate-800/90 border border-slate-700/70 text-[9px] font-mono text-slate-400 font-semibold flex items-center gap-1">
                <span>↵</span>
                <span>Enter</span>
              </span>
            </div>
          </div>
        `;

        globalIdx++;
      });
    });

    container.innerHTML = html;

    // Attach click handlers
    container.querySelectorAll('.palette-item').forEach((el) => {
      el.addEventListener('click', () => {
        const idx = parseInt(el.getAttribute('data-palette-idx'), 10);
        if (!isNaN(idx) && flatResults[idx]) {
          activeIndex = idx;
          executeActiveResult();
        }
      });
    });

    if (window.lucide) window.lucide.createIcons();
    ensureVisible();
  }

  function navigateResults(delta) {
    if (flatResults.length === 0) return;
    activeIndex = (activeIndex + delta + flatResults.length) % flatResults.length;
    
    // Update active class without full DOM rerender for speed
    const container = document.getElementById('command-palette-results');
    if (container) {
      container.querySelectorAll('.palette-item').forEach(el => {
        const idx = parseInt(el.getAttribute('data-palette-idx'), 10);
        if (idx === activeIndex) {
          el.className = 'palette-item h-11 px-3 py-1 rounded-xl border flex items-center justify-between gap-3 cursor-pointer transition-all duration-150 bg-cyan-500/15 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.15)] text-white';
        } else {
          el.className = 'palette-item h-11 px-3 py-1 rounded-xl border flex items-center justify-between gap-3 cursor-pointer transition-all duration-150 bg-slate-900/40 hover:bg-cyan-500/10 border-transparent hover:border-cyan-500/30 text-slate-300';
        }
      });
    }

    ensureVisible();
  }

  function ensureVisible() {
    const container = document.getElementById('command-palette-results');
    const items = container ? container.querySelectorAll('.palette-item') : [];
    if (items[activeIndex]) {
      items[activeIndex].scrollIntoView({ block: 'nearest' });
    }
  }

  function executeActiveResult() {
    if (flatResults[activeIndex]) {
      const selected = flatResults[activeIndex];
      closePalette();
      try {
        selected.action();
      } catch (err) {
        console.error('Error executing palette action:', err);
      }
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  window.initCommandPalette = initCommandPalette;
  window.openCommandPalette = openPalette;
  window.closeCommandPalette = closePalette;
  window.toggleCommandPalette = togglePalette;

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCommandPalette);
  } else {
    initCommandPalette();
  }
})();

