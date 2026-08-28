// --- TAB SWITCHING ENGINE ---
function switchTab(tabId) {
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
    renderMods();
  } else if (tabId === 'shaders') {
    renderShaders();
  } else if (tabId === 'servers') {
    renderServers();
  } else if (tabId === 'satellite') {
    renderSatellite();
  } else if (tabId === 'worlds') {
    renderWorldsGrid();
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
  }

  // 5. Always refresh Lucide icons
  if (window.lucide) {
    lucide.createIcons();
    setTimeout(() => lucide.createIcons(), 50);
  }
}

