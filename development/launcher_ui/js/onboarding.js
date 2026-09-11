/**
 * onboarding.js — First-Time User Welcome Onboarding Wizard for SIR Launcher.
 * Features:
 * - Multi-step guided setup (Welcome -> Language/Theme -> Google Auth -> Finish)
 * - Auto-detects hardware and sets default optimal presets
 * - Stores completion flag in localStorage
 */

window.CURRENT_ONBOARDING_STEP = 1;

function checkFirstTimeOnboarding() {
  const completed = localStorage.getItem('sir_onboarding_completed');
  if (!completed) {
    setTimeout(() => {
      openOnboardingModal();
    }, 450);
  }
}

function openOnboardingModal() {
  window.CURRENT_ONBOARDING_STEP = 1;
  updateOnboardingStepView();
  if (typeof openModal === 'function') {
    openModal('welcome-onboarding-modal');
  } else {
    const el = document.getElementById('welcome-onboarding-modal');
    if (el) el.classList.remove('hidden');
  }
}

function closeOnboardingModal() {
  localStorage.setItem('sir_onboarding_completed', 'true');
  if (typeof closeModal === 'function') {
    closeModal('welcome-onboarding-modal');
  } else {
    const el = document.getElementById('welcome-onboarding-modal');
    if (el) el.classList.add('hidden');
  }
}

function setOnboardingStep(step) {
  window.CURRENT_ONBOARDING_STEP = step;
  updateOnboardingStepView();
}

function nextOnboardingStep() {
  if (window.CURRENT_ONBOARDING_STEP < 4) {
    window.CURRENT_ONBOARDING_STEP++;
    updateOnboardingStepView();
  } else {
    completeOnboarding();
  }
}

function prevOnboardingStep() {
  if (window.CURRENT_ONBOARDING_STEP > 1) {
    window.CURRENT_ONBOARDING_STEP--;
    updateOnboardingStepView();
  }
}

function updateOnboardingStepView() {
  const step = window.CURRENT_ONBOARDING_STEP;
  for (let i = 1; i <= 4; i++) {
    const view = document.getElementById(`onboarding-step-${i}`);
    const dot = document.getElementById(`onboarding-dot-${i}`);
    if (view) {
      if (i === step) {
        view.classList.remove('hidden');
        view.classList.add('animate-in', 'fade-in-0', 'zoom-in-95', 'duration-200');
      } else {
        view.classList.add('hidden');
        view.classList.remove('animate-in', 'fade-in-0', 'zoom-in-95', 'duration-200');
      }
    }
    if (dot) {
      if (i === step) {
        dot.className = 'w-8 h-2 rounded-full bg-cyan-400 transition-all duration-300';
      } else if (i < step) {
        dot.className = 'w-2 h-2 rounded-full bg-cyan-600/60 transition-all duration-300';
      } else {
        dot.className = 'w-2 h-2 rounded-full bg-slate-700 transition-all duration-300';
      }
    }
  }

  const prevBtn = document.getElementById('onboarding-prev-btn');
  const nextBtn = document.getElementById('onboarding-next-btn');
  if (prevBtn) {
    prevBtn.style.visibility = step === 1 ? 'hidden' : 'visible';
  }
  if (nextBtn) {
    if (step === 4) {
      nextBtn.innerHTML = `
        <svg class="w-4 h-4 text-slate-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
        <span>Enter Launchpad</span>
      `;
      nextBtn.className = 'px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-400 to-cyan-400 hover:from-emerald-300 hover:to-cyan-300 text-slate-950 font-black text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/25 flex items-center gap-2 cursor-pointer';
    } else {
      nextBtn.innerHTML = `
        <span>Continue</span>
        <svg class="w-4 h-4 text-slate-950" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
      `;
      nextBtn.className = 'px-6 py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-black text-xs tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/25 flex items-center gap-2 cursor-pointer';
    }
  }
}

function selectOnboardingLang(lang) {
  if (typeof setLanguage === 'function') {
    setLanguage(lang);
  }
  document.querySelectorAll('.onboarding-lang-btn').forEach(b => {
    b.classList.remove('border-cyan-400', 'bg-cyan-500/15');
  });
  const activeBtn = document.getElementById(`onboarding-lang-${lang}`);
  if (activeBtn) {
    activeBtn.classList.add('border-cyan-400', 'bg-cyan-500/15');
  }
}

function selectOnboardingTheme(theme) {
  if (typeof setTheme === 'function') {
    setTheme(theme);
  }
  document.querySelectorAll('.onboarding-theme-btn').forEach(b => {
    b.classList.remove('border-cyan-400', 'bg-cyan-500/15');
  });
  const activeBtn = document.getElementById(`onboarding-theme-${theme}`);
  if (activeBtn) {
    activeBtn.classList.add('border-cyan-400', 'bg-cyan-500/15');
  }
}

function completeOnboarding() {
  closeOnboardingModal();
  if (typeof soundFx !== 'undefined' && soundFx.playSuccess) {
    soundFx.playSuccess();
  }
  if (typeof showToast === 'function') {
    showToast('Welcome to SIR Ecosystem! All systems initialized.', 'success');
  }
  setTimeout(() => {
    if (typeof startQuickStartTour === 'function') {
      startQuickStartTour();
    }
  }, 900);
}

window.CURRENT_ONBOARDING_ENGINE = 'modern';

function selectOnboardingEngine(engineKey) {
  window.CURRENT_ONBOARDING_ENGINE = engineKey;
  const modernCard = document.getElementById('onboarding-engine-modern');
  const legacyCard = document.getElementById('onboarding-engine-legacy');
  const modernBadge = document.getElementById('onboarding-engine-modern-badge');
  const legacyBadge = document.getElementById('onboarding-engine-legacy-badge');
  const recProfile = document.getElementById('onboarding-rec-profile-name');

  const targetInstId = engineKey === 'legacy' ? '1.8.9-ultra' : '26.2-ultra';

  if (engineKey === 'modern') {
    if (modernCard) modernCard.className = "cursor-pointer transition-all hover:scale-[1.02] active:scale-95 p-3.5 rounded-2xl bg-cyan-500/15 border-2 border-cyan-400 ring-2 ring-cyan-400/50 space-y-1.5 select-none";
    if (legacyCard) legacyCard.className = "cursor-pointer transition-all hover:scale-[1.02] active:scale-95 p-3.5 rounded-2xl bg-purple-500/5 border border-purple-500/20 hover:border-purple-500/40 space-y-1.5 select-none";
    if (modernBadge) modernBadge.classList.remove('hidden');
    if (legacyBadge) legacyBadge.classList.add('hidden');
    if (recProfile) {
      recProfile.textContent = "Modern 26.2 Ultra";
      recProfile.className = "font-bold text-cyan-300";
    }
    if (typeof showToast === 'function') {
      showToast('✓ Selected Modern 26.2 (Fabric 0.19 · 221 Mods · Raytracing)', 'info');
    }
  } else {
    if (legacyCard) legacyCard.className = "cursor-pointer transition-all hover:scale-[1.02] active:scale-95 p-3.5 rounded-2xl bg-purple-500/15 border-2 border-purple-400 ring-2 ring-purple-400/50 space-y-1.5 select-none";
    if (modernCard) modernCard.className = "cursor-pointer transition-all hover:scale-[1.02] active:scale-95 p-3.5 rounded-2xl bg-cyan-500/5 border border-cyan-500/20 hover:border-cyan-500/40 space-y-1.5 select-none";
    if (legacyBadge) legacyBadge.classList.remove('hidden');
    if (modernBadge) modernBadge.classList.add('hidden');
    if (recProfile) {
      recProfile.textContent = "Legacy 1.8.9 Ultra";
      recProfile.className = "font-bold text-purple-300";
    }
    if (typeof showToast === 'function') {
      showToast('✓ Selected Legacy 1.8.9 (Forge PvP · 28 Mods · 600+ FPS)', 'info');
    }
  }

  // Set active instance in STATE and persist
  if (typeof STATE !== 'undefined') {
    STATE.selectedInstanceId = targetInstId;
  }
  try {
    localStorage.setItem('sir_selected_instance', targetInstId);
  } catch (e) {}

  if (typeof selectInstance === 'function') {
    selectInstance(targetInstId);
  }
}

function startQuickStartTour() {
  const steps = [
    { title: "Dual-Engine Architecture", text: "Switch seamlessly between Fabric 26.2 and Forge 1.8.9 from the top profile dropdown or Launchpad presets.", tab: "launchpad" },
    { title: "Top Ecosystem Controls", text: "Monitor active downloads, trim RAM working sets with 1 click, and synchronize cloud settings in the navbar.", tab: "launchpad" },
    { title: "Curated Server Radar", text: "Check ping latencies across competitive and survival networks in the Servers tab.", tab: "servers" },
    { title: "Ecosystem Ready!", text: "Launch any profile with 1 click or direct-connect into multiplayer servers.", tab: "launchpad" }
  ];
  let cur = 0;
  function showTourStep() {
    if (cur >= steps.length) {
      if (typeof showToast === 'function') showToast("✓ Quick-start tour completed!", "success");
      return;
    }
    const s = steps[cur];
    if (s.tab && typeof switchTab === 'function') switchTab(s.tab);
    if (typeof showToast === 'function') {
      showToast(`📍 Tour [${cur + 1}/${steps.length}] ${s.title}: ${s.text}`, 'info');
    }
    cur++;
    if (cur < steps.length) {
      setTimeout(showTourStep, 3500);
    }
  }
  showTourStep();
}

window.checkFirstTimeOnboarding = checkFirstTimeOnboarding;
window.openOnboardingModal = openOnboardingModal;
window.closeOnboardingModal = closeOnboardingModal;
window.nextOnboardingStep = nextOnboardingStep;
window.prevOnboardingStep = prevOnboardingStep;
window.selectOnboardingLang = selectOnboardingLang;
window.selectOnboardingTheme = selectOnboardingTheme;
window.completeOnboarding = completeOnboarding;
window.selectOnboardingEngine = selectOnboardingEngine;
window.startQuickStartTour = startQuickStartTour;
