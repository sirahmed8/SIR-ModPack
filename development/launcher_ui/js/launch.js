// --- LAUNCHPAD & LAUNCH ENGINE ---
function renderLaunchpad() {
  const currentInst = STATE.instances.find(i => i.id === STATE.selectedInstanceId) || STATE.instances[0];
  const nameEl = document.getElementById('hero-player-name');
  const activeNameEl = document.getElementById('active-account-name');
  const activeSuiteEl = document.getElementById('active-suite-title');

  if (nameEl) nameEl.innerText = STATE.activeAccountName || 'No account';
  if (activeNameEl) activeNameEl.innerText = STATE.activeAccountName || 'No account';
  if (activeSuiteEl) activeSuiteEl.innerText = currentInst ? `Active: ${currentInst.name}` : 'Active: SIR 26 (Ultra Visuals)';
  // Update FPS estimate banner dynamically
  const fpsBanner = document.getElementById('launchpad-fps-banner');
  if (fpsBanner && currentInst) fpsBanner.innerText = currentInst.fps_est || '180–240 FPS';

  // Render Quick Presets Carousel
  const presetsContainer = document.getElementById('quick-presets-bar');
  if (presetsContainer) {
    const isAr = STATE.currentLang === 'ar';
    const titleHtml = `<span class="text-xs font-bold text-slate-400 px-2 flex items-center gap-1 shrink-0">
      <i data-lucide="zap" class="w-3.5 h-3.5 text-amber-400"></i>
      <span>${isAr ? 'الإعدادات السريعة:' : 'Quick Presets:'}</span>
    </span>`;
    const presetsHtml = STATE.instances.map(inst => {
      const isAct = inst.id === (currentInst ? currentInst.id : 'sir-26-ultra');
      return `<button onclick="selectInstance('${inst.id}')" class="px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 shrink-0 ${
        isAct 
          ? 'bg-cyan-400 text-slate-950 shadow-md shadow-cyan-400/40 font-black' 
          : 'bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700/80 border border-slate-700/50'
      }">
        <span>${escapeHtml(inst.name)}</span>
      </button>`;
    }).join('');
    presetsContainer.innerHTML = titleHtml + presetsHtml;
    if (window.lucide) lucide.createIcons();
  }

}

async function launchActiveGame() {
  launchGame();
}

async function launchGame(instId = null) {
  if (STATE.isLaunching) return;
  STATE.isLaunching = true;

  const targetInst = instId || STATE.selectedInstanceId || 'sir-26-ultra';
  const launchBtn = document.getElementById('main-launch-btn') || document.querySelector('button[onclick*="launchActiveGame"]');
  const originalText = launchBtn ? launchBtn.innerText : "LAUNCH GAME";

  if (launchBtn) {
    launchBtn.innerText = STATE.currentLang === 'ar' ? "جاري التحقق والتشغيل..." : "VERIFYING & LAUNCHING...";
    launchBtn.classList.add('opacity-80', 'animate-pulse');
  }

  // Live status polling loop for version downloads & launch steps
  let statusInterval = null;
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_launch_status) {
    statusInterval = setInterval(async () => {
      try {
        const stat = await window.pywebview.api.get_launch_status();
        if (stat && stat.status && stat.status !== 'Idle' && launchBtn) {
          launchBtn.innerText = stat.status;
        }
      } catch {}
    }, 400);
  }

  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.launch_game(targetInst);
      if (statusInterval) clearInterval(statusInterval);
      if (res && res.error) {
        showToast('⚠ ' + res.error, 'error');
      } else if (res && res.success) {
        showToast(res.message || `✓ Game started successfully!`, 'success');
      }
    } catch (e) {
      if (statusInterval) clearInterval(statusInterval);
      console.warn("Launch exception:", e);
      showToast('⚠ Launch error: ' + (e.message || e), 'error');
    }
  } else {
    setTimeout(() => {
      if (statusInterval) clearInterval(statusInterval);
      showToast(`✓ Launched ${targetInst} as ${STATE.activeAccountName}`, 'success');
    }, 800);
  }

  setTimeout(() => {
    if (statusInterval) clearInterval(statusInterval);
    STATE.isLaunching = false;
    if (launchBtn) {
      launchBtn.innerText = originalText;
      launchBtn.classList.remove('opacity-80', 'animate-pulse');
    }
  }, 2500);
}

