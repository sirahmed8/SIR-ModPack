// --- WIZARD NAVIGATION & LOCKED FLOW ---
function onStepPillClick(stageNum) {
  if (STATE.isInstalling) return;
  if (stageNum === 4) return;
  if (stageNum > 1 && !STATE.eulaAgreed) return;
  
  goToStage(stageNum);
}

function goToStage(stageNum) {
  if (STATE.isInstalling && stageNum !== 4) return;
  STATE.currentStage = stageNum;

  // Update Wizard Stage Panels
  document.querySelectorAll('.wizard-stage').forEach(el => el.classList.remove('active'));
  const stageEl = document.getElementById(`stage-${stageNum}`);
  if (stageEl) stageEl.classList.add('active');

  // Update Stepper Pills
  for (let i = 1; i <= 4; i++) {
    const pill = document.getElementById(`step-pill-${i}`);
    if (pill) {
      if (i === stageNum) {
        pill.className = "step-pill active flex-1 justify-center";
      } else if (i < stageNum) {
        pill.className = "step-pill completed flex-1 justify-center cursor-pointer";
      } else if (i === 4) {
        pill.className = "step-pill locked flex-1 justify-center";
      } else {
        pill.className = "step-pill flex-1 justify-center" + (STATE.eulaAgreed ? " cursor-pointer" : " locked");
      }
    }
  }

  updateNavButtons();
  if (window.lucide) lucide.createIcons();
}

function updateNavButtons() {
  const btnBack = document.getElementById('btn-footer-back');
  const btnNext = document.getElementById('btn-footer-next');
  const nextLabel = document.getElementById('btn-next-label');

  if (STATE.isInstalling) {
    if (btnBack) {
      btnBack.disabled = true;
      btnBack.className = "px-5 py-2 rounded-xl btn-secondary text-xs font-bold opacity-40 cursor-not-allowed flex items-center gap-1.5 transition-all";
    }
    if (btnNext) {
      btnNext.style.display = "none";
    }
    return;
  }

  if (btnBack) {
    if (STATE.currentStage > 1 && STATE.currentStage < 4) {
      btnBack.disabled = false;
      btnBack.className = "px-5 py-2 rounded-xl btn-secondary text-xs font-bold active:scale-95 cursor-pointer flex items-center gap-1.5 transition-all";
    } else {
      btnBack.disabled = true;
      btnBack.className = "px-5 py-2 rounded-xl btn-secondary text-xs font-bold opacity-50 cursor-not-allowed flex items-center gap-1.5 transition-all";
    }
  }

  if (btnNext) {
    btnNext.style.display = "inline-flex";
    if (STATE.currentStage === 1) {
      if (STATE.eulaAgreed) {
        btnNext.disabled = false;
        btnNext.className = "px-7 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black shadow-lg shadow-cyan-500/25 active:scale-95 cursor-pointer flex items-center gap-2 transition-all";
      } else {
        btnNext.disabled = true;
        btnNext.className = "px-7 py-2.5 rounded-xl btn-secondary text-xs font-black opacity-50 cursor-not-allowed flex items-center gap-2 transition-all";
      }
      if (nextLabel) nextLabel.innerText = I18N[STATE.currentLang].nextStep;
    } else if (STATE.currentStage === 2) {
      btnNext.disabled = false;
      btnNext.className = "px-7 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black shadow-lg shadow-cyan-500/25 active:scale-95 cursor-pointer flex items-center gap-2 transition-all";
      if (nextLabel) nextLabel.innerText = I18N[STATE.currentLang].nextStep;
    } else if (STATE.currentStage === 3) {
      btnNext.disabled = false;
      btnNext.className = "px-8 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-lg shadow-emerald-500/30 active:scale-95 cursor-pointer flex items-center gap-2 transition-all";
      if (nextLabel) nextLabel.innerText = I18N[STATE.currentLang].installNow;
    } else if (STATE.currentStage === 4) {
      btnNext.style.display = "none";
    }
  }
}

function nextStage() {
  if (STATE.currentStage === 1 && !STATE.eulaAgreed) {
    const sw = document.getElementById('eula-switch');
    if (sw) {
      sw.focus();
      sw.parentElement?.classList.add('animate-bounce');
      setTimeout(() => sw.parentElement?.classList.remove('animate-bounce'), 800);
    }
    return;
  }
  if (STATE.currentStage === 3) {
    goToStage(4);
    startInstallProcess();
  } else if (STATE.currentStage < 3) {
    goToStage(STATE.currentStage + 1);
  }
}

function prevStage() {
  if (STATE.isInstalling) return;
  if (STATE.currentStage > 1 && STATE.currentStage < 4) {
    goToStage(STATE.currentStage - 1);
  }
}

// --- STAGE 1: EULA TOGGLE ---
function toggleEulaSwitch(e) {
  const cb = document.getElementById('eula-switch');
  if (!cb) return;
  if (e && e.target === cb) {
    onEulaToggle(cb.checked);
    return;
  }
  cb.checked = !cb.checked;
  onEulaToggle(cb.checked);
}

function onEulaToggle(isChecked) {
  STATE.eulaAgreed = Boolean(isChecked);
  const cb = document.getElementById('eula-switch');
  if (cb && cb.checked !== STATE.eulaAgreed) {
    cb.checked = STATE.eulaAgreed;
  }
  updateNavButtons();

  const pill2 = document.getElementById('step-pill-2');
  if (pill2) {
    if (STATE.eulaAgreed) {
      pill2.classList.remove('locked');
      pill2.classList.add('cursor-pointer');
    } else {
      pill2.classList.add('locked');
      pill2.classList.remove('cursor-pointer');
    }
  }
}

// --- STAGE 2: TARGET SELECTION ---
function selectTarget(type) {
  STATE.targetType = type;
  const cardSir = document.getElementById('target-card-sir');
  const cardVanilla = document.getElementById('target-card-vanilla');
  const cardLunar = document.getElementById('target-card-lunar');

  const dotSir = document.getElementById('radio-dot-sir');
  const dotVanilla = document.getElementById('radio-dot-vanilla');
  const dotLunar = document.getElementById('radio-dot-lunar');

  [cardSir, cardVanilla, cardLunar].forEach(c => { if (c) c.className = "feature-card selectable p-4 space-y-2"; });
  [dotSir, dotVanilla, dotLunar].forEach(d => { if (d) d.className = "w-3.5 h-3.5 rounded-full bg-slate-400 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-700"; });

  if (type === 'sir_launcher' && cardSir && dotSir) {
    cardSir.className = "feature-card selectable selected p-4 space-y-2";
    dotSir.className = "w-3.5 h-3.5 rounded-full bg-cyan-400 border-2 border-slate-900 shadow-sm";
  } else if (type === 'vanilla' && cardVanilla && dotVanilla) {
    cardVanilla.className = "feature-card selectable selected p-4 space-y-2";
    dotVanilla.className = "w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-slate-900 shadow-sm";
  } else if (type === 'lunar' && cardLunar && dotLunar) {
    cardLunar.className = "feature-card selectable selected p-4 space-y-2";
    dotLunar.className = "w-3.5 h-3.5 rounded-full bg-amber-400 border-2 border-slate-900 shadow-sm";
  }

  // Update target installation path dynamically
  if (STATE.defaultPaths && STATE.defaultPaths[type]) {
    STATE.customPath = STATE.defaultPaths[type];
    const pathInput = document.getElementById('custom-path-input');
    if (pathInput) pathInput.value = STATE.defaultPaths[type];
  }
}

async function browseDestinationFolder() {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.browse_folder();
    if (res.success && res.path) {
      STATE.customPath = res.path;
      document.getElementById('custom-path-input').value = res.path;
    }
  }
}

// --- STAGE 3: RAM & GOVERNOR ---
function updateRamSlider(val) {
  STATE.allocatedRam = parseInt(val);
  const valEl = document.getElementById('ram-slider-val');
  if (valEl) {
    if (STATE.totalRam && STATE.allocatedRam >= STATE.totalRam - 2) {
      valEl.innerText = `${val} GB Dedicated (Max Safe Allocation)`;
    } else {
      valEl.innerText = `${val} GB Dedicated`;
    }
  }
}

function setGovernor(mode) {
  STATE.powerGovernor = mode;
  const btnTurbo = document.getElementById('gov-btn-turbo');
  const btnSmooth = document.getElementById('gov-btn-smooth');

  if (mode === 'turbo') {
    btnTurbo.className = "p-3 rounded-xl bg-cyan-500/15 text-cyan-700 dark:text-cyan-300 border border-cyan-500/40 text-xs font-extrabold flex items-center justify-center gap-2";
    btnSmooth.className = "p-3 rounded-xl btn-secondary text-xs font-bold flex items-center justify-center gap-2";
  } else {
    btnSmooth.className = "p-3 rounded-xl bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/40 text-xs font-extrabold flex items-center justify-center gap-2";
    btnTurbo.className = "p-3 rounded-xl btn-secondary text-xs font-bold flex items-center justify-center gap-2";
  }
}

// --- STAGE 4: LIVE INSTALLATION EXECUTION ---
async function startInstallProcess() {
  STATE.isInstalling = true;
  updateNavButtons();

  const stepperContainer = document.getElementById('stepper-bar-container');
  if (stepperContainer) {
    stepperContainer.classList.add('opacity-40', 'pointer-events-none');
  }

  const config = {
    target_type: STATE.targetType,
    custom_path: STATE.customPath,
    power_governor: STATE.powerGovernor,
    ram_gb: STATE.allocatedRam,
    comp_modern: document.getElementById('comp-modern')?.checked ?? true,
    comp_legacy: document.getElementById('comp-legacy')?.checked ?? true,
    comp_shaders: document.getElementById('comp-shaders')?.checked ?? true,
    comp_packs: document.getElementById('comp-packs')?.checked ?? true,
    create_shortcut: document.getElementById('comp-shortcut')?.checked ?? true,
    create_startmenu: document.getElementById('comp-startmenu')?.checked ?? true
  };

  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.start_installation(JSON.stringify(config));
    
    STATE.pollInterval = setInterval(async () => {
      try {
        const res = await window.pywebview.api.get_install_progress();
        const pctEl = document.getElementById('install-progress-pct');
        const statusEl = document.getElementById('install-status-label');
        const logEl = document.getElementById('install-log-label');
        const barEl = document.getElementById('install-progress-bar');

        if (pctEl) pctEl.innerText = `${res.progress}%`;
        if (statusEl) {
          const cleanStatus = (res.status || "").replace(/\.{3,}$/, "");
          statusEl.innerText = cleanStatus || "Deploying SIR ModPack Ecosystem";
        }
        if (logEl && res.log_line) {
          const cleanLog = (res.log_line || "").replace(/\.{3,}$/, "");
          logEl.innerText = cleanLog;
        }
        if (barEl) barEl.style.width = `${res.progress}%`;

        const descEl = document.getElementById('install-stage-desc');
        if (descEl) {
          if (res.progress < 20) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تهيئة مجلدات ومسارات التثبيت وفحص الملفات السابقة' : 'Setting up installation directory and verifying workspace structure';
          } else if (res.progress < 45) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تثبيت وتحديث بروفايلات فابريك 26.2 الحديث وفورج 1.8.9 الكلاسيكي' : 'Deploying Fabric 1.21.4 (Modern 26.2) and Forge 1.8.9 (Legacy PvP) instances';
          } else if (res.progress < 65) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'فك ونسخ مكتبات ومودات التحسين الفائقة (240+ مود معتمد)' : 'Installing and synchronizing verified performance and graphics mods suite (240+ jars)';
          } else if (res.progress < 80) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تثبيت حزم شيدرز SIR المتطورة وتجسيم البلوكات ثلاثي الأبعاد (3D POM)' : 'Deploying SIR Shaders 2.0 (Extreme & Balanced) with 3D Parallax Occlusion Mapping';
          } else if (res.progress < 95) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تطبيق إعدادات الذاكرة وتخصيص أنوية المعالج وربط الحسابات' : 'Configuring JVM garbage collection flags, dedicated RAM allocation, and local account bridges';
          } else {
            descEl.innerText = STATE.currentLang === 'ar' ? 'إنشاء اختصارات سطح المكتب وتأكيد اكتمال التثبيت بنجاح 100%' : 'Finalizing deployment manifest, creating desktop shortcuts, and verifying integrity';
          }
        }

        if (res.is_complete) {
          clearInterval(STATE.pollInterval);
          STATE.isInstalling = false;
          document.getElementById('install-progress-card').classList.add('hidden');
          document.getElementById('install-success-card').classList.remove('hidden');
          if (stepperContainer) stepperContainer.classList.remove('opacity-40', 'pointer-events-none');
        }
      } catch (e) {}
    }, 200);
  }
}

async function launchSirLauncher() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.launch_sir_launcher();
  }
}

async function openInstalledFolder() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.open_folder(STATE.customPath);
  }
}

// --- MODALS (CLEANER & REPAIR) ---

  }, 3500);
}

function openRepairModal() {
  document.getElementById('modal-repair').classList.remove('hidden');
}

function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}

async function runCleaner() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.execute_deep_clean();
      closeModal('modal-cleaner');
      showInAppModal("Storage Cleaner", res.message || "Cache and temporary logs cleaned successfully!", "check-circle");
    } catch (e) {
      closeModal('modal-cleaner');
      showInAppModal("Storage Cleaner", `Error: ${e}`, "alert-triangle");
    }
  }
}

async function runRepair() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.execute_self_repair();
      closeModal('modal-repair');
      let report = res.message || "All assets verified!";
      if (res.repaired_items && res.repaired_items.length > 0) {
        report += "\n\nRepaired Components:\n" + res.repaired_items.map(i => `• ${i}`).join("\n");
      }
      showInAppModal("Self-Repair Studio", report, "check-circle");
    } catch (e) {
      closeModal('modal-repair');
      showInAppModal("Self-Repair Studio", `Error: ${e}`, "alert-triangle");
    }
  }
}

// --- LANGUAGE & HARDWARE INITIALIZATION ---
function toggleLanguage() {
  STATE.currentLang = STATE.currentLang === 'en' ? 'ar' : 'en';
  document.documentElement.dir = STATE.currentLang === 'ar' ? 'rtl' : 'ltr';
  document.getElementById('lang-indicator').innerText = STATE.currentLang === 'ar' ? 'English' : 'عربي';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (I18N[STATE.currentLang][key]) {
      el.innerText = I18N[STATE.currentLang][key];
    }
  });

  updateNavButtons();
}

async function initHardwareSpecs() {
  if (STATE.specsFetched) return;

  if (window.pywebview && window.pywebview.api) {
    try {
      const specs = await window.pywebview.api.get_hardware_specs();
      if (!specs) return;
      STATE.specsFetched = true;

      const cpuEl = document.getElementById('cpu-name-label');
      const gpuEl = document.getElementById('gpu-name-label');
      const ramEl = document.getElementById('ram-gb-label');
      const coresEl = document.getElementById('cpu-cores-label');
      const tierEl = document.getElementById('rig-tier-badge');
      const reasonEl = document.getElementById('hw-recommendation-reason');

      if (cpuEl && specs.cpu_name) cpuEl.innerText = specs.cpu_name;
      if (gpuEl && specs.gpu_name) gpuEl.innerText = specs.gpu_name;
      if (ramEl && specs.ram_gb) ramEl.innerText = `${specs.ram_gb} GB RAM`;
      if (coresEl && specs.cpu_cores) coresEl.innerText = `${specs.cpu_cores} Cores`;
      if (tierEl && specs.tier_name) tierEl.innerText = specs.tier_name;
      if (reasonEl && specs.reason) reasonEl.innerText = specs.reason;

      STATE.totalRam = specs.ram_gb;

      // Dynamically configure RAM slider limits based on real physical RAM
      const slider = document.getElementById('ram-slider');
      const maxHint = document.getElementById('max-ram-hint');
      const recomHint = document.getElementById('recommended-ram-hint');

      if (slider && specs.ram_gb) {
        slider.min = 3;
        slider.max = specs.ram_gb;
        slider.value = specs.recommended_ram || 8;
        updateRamSlider(slider.value);
      }
      if (maxHint && specs.ram_gb) {
        maxHint.innerText = `${specs.ram_gb} GB Physical RAM (Max)`;
      }
      if (recomHint && specs.recommended_ram) {
        recomHint.innerText = `Recommended: ${specs.recommended_ram} GB`;
      }

      // Fetch default Windows client paths (on C:\ drive)
      try {
        const paths = await window.pywebview.api.get_default_target_paths();
        if (paths) {
          STATE.defaultPaths = paths;
          STATE.customPath = paths[STATE.targetType] || paths.sir_launcher;
          const pathInput = document.getElementById('custom-path-input');
          if (pathInput) pathInput.value = STATE.customPath;
        }
      } catch (err) {
        console.warn("Could not fetch target paths:", err);
      }

      // Check for previously interrupted installation
      checkResumeState();
    } catch (e) {
      console.error("Hardware specs fetch error:", e);
    }
  }
}
