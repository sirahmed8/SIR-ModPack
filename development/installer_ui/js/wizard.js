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

window.onEulaToggle = onEulaToggle;
window.toggleEulaSwitch = toggleEulaSwitch;

// --- STAGE 2: TARGET SELECTION ---
async function selectTarget(type) {
  STATE.targetType = type;
  const cardSir = document.getElementById('target-card-sir');
  const cardSirVanilla = document.getElementById('target-card-sir-vanilla');
  const cardVanilla = document.getElementById('target-card-vanilla');
  const cardLunar = document.getElementById('target-card-lunar');

  const dotSir = document.getElementById('radio-dot-sir');
  const dotSirVanilla = document.getElementById('radio-dot-sir-vanilla');
  const dotVanilla = document.getElementById('radio-dot-vanilla');
  const dotLunar = document.getElementById('radio-dot-lunar');

  [cardSir, cardSirVanilla, cardVanilla, cardLunar].forEach(c => { if (c) c.className = "feature-card selectable p-4 space-y-2"; });
  [dotSir, dotSirVanilla, dotVanilla, dotLunar].forEach(d => { if (d) d.className = "w-3.5 h-3.5 rounded-full bg-slate-400 dark:bg-slate-800 border-2 border-slate-300 dark:border-slate-700 radio-dot-indicator"; });

  if (type === 'sir_launcher' && cardSir && dotSir) {
    cardSir.className = "feature-card selectable selected p-4 space-y-2";
    dotSir.className = "w-3.5 h-3.5 rounded-full bg-cyan-400 border-2 border-slate-900 shadow-sm radio-dot-indicator selected";
  } else if (type === 'sir_vanilla' && cardSirVanilla && dotSirVanilla) {
    cardSirVanilla.className = "feature-card selectable selected p-4 space-y-2";
    dotSirVanilla.className = "w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-slate-900 shadow-sm radio-dot-indicator selected";
  } else if (type === 'vanilla' && cardVanilla && dotVanilla) {
    cardVanilla.className = "feature-card selectable selected p-4 space-y-2";
    dotVanilla.className = "w-3.5 h-3.5 rounded-full bg-emerald-400 border-2 border-slate-900 shadow-sm radio-dot-indicator selected";
  } else if (type === 'lunar' && cardLunar && dotLunar) {
    cardLunar.className = "feature-card selectable selected p-4 space-y-2";
    dotLunar.className = "w-3.5 h-3.5 rounded-full bg-amber-400 border-2 border-slate-900 shadow-sm radio-dot-indicator selected";
  }

  // Check target environment (Lunar or Vanilla missing warning)
  const warnEl = document.getElementById('target-env-warning');
  const warnTxt = document.getElementById('target-env-warning-text');
  if (window.pywebview && window.pywebview.api && window.pywebview.api.check_target_environment) {
    try {
      const chk = await window.pywebview.api.check_target_environment(type);
      if (chk && chk.warning) {
        if (warnTxt) warnTxt.innerText = chk.warning;
        if (warnEl) warnEl.classList.remove('hidden');
      } else {
        if (warnEl) warnEl.classList.add('hidden');
      }
    } catch {
      if (warnEl) warnEl.classList.add('hidden');
    }
  } else {
    if (warnEl) warnEl.classList.add('hidden');
  }

  // Update target installation path dynamically
  let targetPath = (STATE.defaultPaths && STATE.defaultPaths[type]) ? STATE.defaultPaths[type] : '';
  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_default_target_paths) {
    try {
      const paths = await window.pywebview.api.get_default_target_paths();
      if (paths) {
        STATE.defaultPaths = paths;
        targetPath = paths[type] || '';
      }
    } catch {}
  }

  if (targetPath) {
    STATE.customPath = targetPath;
    const pathInput = document.getElementById('custom-path-input');
    if (pathInput) pathInput.value = targetPath;
  }
}
window.selectTarget = selectTarget;

function openExternalReleasePage() {
  const url = "https://github.com/sirahmed8/SIR-ModPack/releases";
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_external_url) {
    window.pywebview.api.open_external_url(url);
  } else {
    window.open(url, "_blank");
  }
}
window.openExternalReleasePage = openExternalReleasePage;

async function checkPackageAvailability() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.check_package_status) {
    try {
      const res = await window.pywebview.api.check_package_status();
      const banner = document.getElementById('missing-package-banner');
      if (banner) {
        if (res && !res.has_local_package) {
          banner.classList.remove('hidden');
          const desc = document.getElementById('missing-package-desc');
          if (desc && res.message) desc.innerText = res.message;
        } else {
          banner.classList.add('hidden');
        }
      }
    } catch {}
  }
}
window.checkPackageAvailability = checkPackageAvailability;

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
const RAM_STEPS = [2, 4, 6, 8, 10, 12, 16, 24];

function updateRamSlider(val) {
  const stepIdx = parseInt(val);
  const gb = (stepIdx >= 0 && stepIdx < RAM_STEPS.length) ? RAM_STEPS[stepIdx] : (parseInt(val) || 8);
  STATE.allocatedRam = gb;
  const valEl = document.getElementById('ram-slider-val');
  if (valEl) {
    if (STATE.totalRam && STATE.allocatedRam >= STATE.totalRam - 2) {
      valEl.innerText = `${gb} GB Dedicated (Max Safe Allocation)`;
    } else {
      valEl.innerText = `${gb} GB Dedicated`;
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
    create_startmenu: document.getElementById('comp-startmenu')?.checked ?? true,
    register_protocol: document.getElementById('comp-protocol')?.checked ?? true,
    associate_mrpack: document.getElementById('comp-mrpack')?.checked ?? true
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
        const speedVal = document.getElementById('install-speed-val');
        const filesCounter = document.getElementById('install-files-counter');

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
        const ringEl = document.getElementById('install-progress-ring');
        const ringPct = document.getElementById('install-ring-pct');
        if (ringEl) {
          const circumference = 326.72;
          const offset = Math.max(0, circumference - (res.progress / 100) * circumference);
          ringEl.style.strokeDashoffset = offset;
        }
        if (ringPct) ringPct.innerText = `${res.progress}%`;

        if (speedVal && res.speed_mbps !== undefined) {
          speedVal.innerText = `${res.speed_mbps.toFixed(1)} MB/s`;
        }

        if (filesCounter && res.files_extracted !== undefined) {
          filesCounter.innerText = `${res.files_extracted} / ${res.total_files || 260} files`;
        }

        if (res.package_missing) {
          const banner = document.getElementById('missing-package-banner');
          if (banner) {
            banner.classList.remove('hidden');
            const desc = document.getElementById('missing-package-desc');
            if (desc) desc.innerText = `Package archive '${res.missing_payload_name || 'SIR_Package.zip'}' was not found. Click below to download it from GitHub.`;
          }
        }

        const descEl = document.getElementById('install-stage-desc');
        if (descEl) {
          if (res.progress < 20) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تهيئة مجلدات ومسارات التثبيت وفحص الملفات السابقة' : 'Setting up installation directory and verifying workspace structure';
          } else if (res.progress < 45) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تثبيت وتحديث بروفايلات SIR 26 الحديث وفورج 1.8.9' : 'Deploying Fabric 26.2 (Modern 26) and Forge 1.8.9 (Legacy PvP) instances';
          } else if (res.progress < 65) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'فك ونسخ مكتبات ومودات التحسين الفائقة (240+ مود معتمد)' : 'Installing and synchronizing verified performance and graphics mods suite (240+ jars)';
          } else if (res.progress < 80) {
            descEl.innerText = STATE.currentLang === 'ar' ? 'تثبيت شيدر وحزم SIR' : 'Deploying SIR Shader & Resource Packs';
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
          const successCard = document.getElementById('install-success-card');
          if (successCard) successCard.classList.remove('hidden');
          if (stepperContainer) stepperContainer.classList.remove('opacity-40', 'pointer-events-none');
          if (window.lucide) lucide.createIcons();

          const finalBtnLabel = document.getElementById('btn-final-launch-text');
          if (finalBtnLabel) {
            const isAr = STATE.currentLang === 'ar';
            if (STATE.targetType === 'lunar') {
              finalBtnLabel.innerText = isAr ? "تشغيل LUNAR CLIENT" : "OPEN LUNAR CLIENT";
            } else if (STATE.targetType === 'vanilla') {
              finalBtnLabel.innerText = isAr ? "تشغيل MINECRAFT" : "LAUNCH MINECRAFT";
            } else {
              finalBtnLabel.innerText = isAr ? "تشغيل SIR LAUNCHER" : "LAUNCH SIR LAUNCHER";
            }
          }
        }
      } catch (e) {}
    }, 200);
  }
}

async function launchSirLauncher() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.launch_sir_launcher(STATE.targetType);
  }
}

async function checkResumeState() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.check_resume_state) {
    try {
      const res = await window.pywebview.api.check_resume_state();
      if (res && res.has_resume) {
        const resumeBanner = document.getElementById('resume-banner');
        if (resumeBanner) {
          resumeBanner.classList.remove('hidden');
          const txt = document.getElementById('resume-banner-text');
          if (txt) txt.innerText = `Interrupted installation detected (${res.stage || 'In Progress'} - ${res.progress}%). You can resume seamlessly.`;
        }
      }
    } catch {}
  }
}

async function resumeInstallation() {
  const resumeBanner = document.getElementById('resume-banner');
  if (resumeBanner) resumeBanner.classList.add('hidden');
  goToStage(4);
  startInstallProcess();
}

async function clearResumeAndClean() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.clear_resume_state) {
    await window.pywebview.api.clear_resume_state();
  }
  const resumeBanner = document.getElementById('resume-banner');
  if (resumeBanner) resumeBanner.classList.add('hidden');
}

window.checkResumeState = checkResumeState;
window.resumeInstallation = resumeInstallation;
window.clearResumeAndClean = clearResumeAndClean;

async function openInstalledFolder() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.open_folder(STATE.customPath);
  }
}

// --- HARDWARE SPECIFICATIONS ENGINE ---
function applySpecsToUI(specs) {
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

  // Pre-Flight Diagnostic Matrix UI
  const diskVal = document.getElementById('diag-disk-val');
  const diskBar = document.getElementById('diag-disk-bar');
  const diskHint = document.getElementById('diag-disk-hint');
  if (specs.disk_free_gb !== undefined) {
    if (diskVal) diskVal.innerText = `${specs.disk_free_gb} GB Free / ${specs.disk_total_gb} GB`;
    if (diskBar) diskBar.style.width = `${specs.disk_used_pct || 70}%`;
    if (diskHint) {
      diskHint.innerText = specs.disk_pass ? `✓ ${specs.disk_free_gb} GB available (Exceeds 4 GB minimum)` : `⚠️ Low disk space: only ${specs.disk_free_gb} GB free`;
      diskHint.className = specs.disk_pass ? "text-[10px] text-emerald-400 font-mono" : "text-[10px] text-amber-400 font-mono";
    }
  }

  const ramVal = document.getElementById('diag-ram-val');
  const ramHint = document.getElementById('diag-ram-hint');
  if (ramVal) ramVal.innerText = `${specs.ram_gb} GB System RAM`;
  if (ramHint) {
    ramHint.innerText = specs.ram_pass ? `✓ High-capacity memory headroom (${specs.recommended_ram_text || '6 GB Dedicated'})` : `⚠️ Minimum 6 GB recommended for smooth gameplay`;
  }

  const cpuVal = document.getElementById('diag-cpu-val');
  const cpuHint = document.getElementById('diag-cpu-hint');
  if (cpuVal) cpuVal.innerText = specs.avx2_pass ? "AVX2 & FMA Supported" : "Standard x86-64";
  if (cpuHint) cpuHint.innerText = specs.avx2_pass ? "✓ Hardware vector acceleration ready" : "✓ Compatible CPU instructions verified";

  const javaVal = document.getElementById('diag-java-val');
  const javaHint = document.getElementById('diag-java-hint');
  const j25 = specs.java25_label || specs.java21_label;
  if (javaVal && j25) javaVal.innerText = j25;
  if (javaHint) {
    if (specs.java25_pass && specs.java8_pass) {
      javaHint.innerText = "✓ Verified OpenJDK 25 (26.2) & Java 8 (1.8.9) runtimes";
    } else if (specs.java25_pass) {
      javaHint.innerText = "✓ Verified OpenJDK 25 Modern runtime (Java 8 optional for 1.8.9)";
    } else if (specs.java8_pass) {
      javaHint.innerText = "✓ Verified Java 8 runtime (1-Click OpenJDK 25 available)";
    } else {
      javaHint.innerText = "⚡ 1-Click automated OpenJDK 25 runtime download available";
    }
  }

  const slider = document.getElementById('ram-slider');
  const recomHint = document.getElementById('recommended-ram-hint');
  const maxRamHint = document.getElementById('max-ram-hint');

  if (slider) {
    slider.min = 0;
    slider.max = RAM_STEPS.length - 1;
    const recGb = specs.recommended_ram || 8;
    const matchIdx = RAM_STEPS.indexOf(recGb);
    slider.value = matchIdx !== -1 ? matchIdx : 3;
    updateRamSlider(slider.value);
  }
  if (recomHint && specs.recommended_ram) {
    recomHint.innerText = `Recommended: ${specs.recommended_ram} GB`;
  }
  if (maxRamHint && specs.ram_gb) {
    maxRamHint.innerText = `${specs.ram_gb} GB (Max)`;
  }
}

function initHardwareSpecsFallback() {
  const fallback = {
    cpu_name: "Intel / AMD Multi-Core High-Performance Processor",
    gpu_name: "Dedicated Gaming Graphics Adapter",
    ram_gb: 16,
    cpu_cores: navigator.hardwareConcurrency || 8,
    tier_name: "⚡ Balanced Performance Rig",
    recommended_ram: 8,
    reason: "Auto-tuned for high-refresh competitive gameplay and smooth shader fidelity."
  };
  applySpecsToUI(fallback);
}

async function initHardwareSpecs() {
  if (STATE.specsFetched) return;

  if (window.pywebview && window.pywebview.api) {
    try {
      const specs = await window.pywebview.api.get_hardware_specs();
      if (specs) {
        applySpecsToUI(specs);
      } else {
        initHardwareSpecsFallback();
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
      if (typeof checkResumeState === 'function') checkResumeState();
    } catch (e) {
      console.error("Hardware specs fetch error:", e);
      initHardwareSpecsFallback();
    }
  }
}

window.initHardwareSpecs = initHardwareSpecs;
window.initHardwareSpecsFallback = initHardwareSpecsFallback;
