// =============================================================================
// SIR Installer Studio Pro — Modular Bootstrap Orchestrator
// Clean Architecture Standard
// =============================================================================


// --- CRASH / INTERRUPTION RESUME CONTROLLER ---
async function checkResumeState() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.check_resume_state();
      if (res && res.has_resume) {
        STATE.resumeData = res;
        const banner = document.getElementById('resume-banner');
        const bannerTitle = document.getElementById('resume-banner-title');
        const bannerDesc = document.getElementById('resume-banner-desc');
        const resumeBtnText = document.getElementById('resume-btn-text');

        if (banner) banner.classList.remove('hidden');
        if (bannerTitle) {
          bannerTitle.innerText = STATE.currentLang === 'ar' 
            ? `⚡ تم العثور على تقدم تثبيت محفوظ (${res.progress}%)` 
            : `⚡ Interrupted Installation Detected (${res.progress}%)`;
        }
        if (bannerDesc) {
          bannerDesc.innerText = STATE.currentLang === 'ar'
            ? `تم حفظ ملفات التثبيت السابقة بأمان عند مرحلة "${res.stage}". يمكنك المتابعة الآن مباشرة دون إعادة تحميل أو نسخ الملفات المكتملة!`
            : `Your previous session was safely preserved at "${res.stage}". You can resume immediately without re-copying verified files!`;
        }
        if (resumeBtnText) {
          resumeBtnText.innerText = STATE.currentLang === 'ar'
            ? `متابعة التثبيت من (${res.progress}%)`
            : `Resume Install (${res.progress}%)`;
        }
        if (window.lucide) lucide.createIcons();
      }
    } catch (e) {
      console.warn("Resume check error:", e);
    }
  }
}

async function resumeInstallation() {
  const banner = document.getElementById('resume-banner');
  if (banner) banner.classList.add('hidden');

  // If config was saved in resume data, apply it
  if (STATE.resumeData && STATE.resumeData.config) {
    const c = STATE.resumeData.config;
    if (c.ram_gb) STATE.allocatedRam = c.ram_gb;
    if (c.power_governor) STATE.powerGovernor = c.power_governor;
    if (c.custom_path) STATE.customPath = c.custom_path;
  }

  // Jump to stage 4 and start installation
  STATE.currentStage = 4;
  showStage(4);
  startInstallation();
}

async function dismissResumeState() {
  const banner = document.getElementById('resume-banner');
  if (banner) banner.classList.add('hidden');
  STATE.resumeData = null;
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.clear_resume_state();
    } catch (e) {}
  }
}

// Ensure hardware specs are fetched cleanly as soon as bridge is ready
let isSpecsLoading = false;
async function safeInitHardware() {
  if (STATE.specsFetched || isSpecsLoading) return;
  isSpecsLoading = true;
  try {
    await initHardwareSpecs();
  } finally {
    isSpecsLoading = false;
  }
}

window.addEventListener('pywebviewready', safeInitHardware);

document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();
  updateNavButtons();

  if (window.pywebview && window.pywebview.api) {
    safeInitHardware();
  } else {
    // Single graceful retry after short tick
    setTimeout(safeInitHardware, 250);
  }
});
