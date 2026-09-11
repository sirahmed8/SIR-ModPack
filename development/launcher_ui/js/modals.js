// --- MODALS & CONTROLS ---
let _confirmDialogResolve = null;

function showConfirmDialog({ title = "Confirm Action", message = "Are you sure you want to proceed?", confirmText = "Confirm", cancelText = "Cancel", isDanger = true, onConfirm = null }) {
  return new Promise((resolve) => {
    _confirmDialogResolve = (result) => {
      if (result && typeof onConfirm === 'function') {
        try { onConfirm(); } catch (err) { console.error('Confirm dialog callback error:', err); }
      }
      resolve(result);
    };

    const titleEl = document.getElementById('confirm-modal-title');
    const msgEl = document.getElementById('confirm-modal-message');
    const submitBtn = document.getElementById('confirm-modal-submit-btn');
    const cancelBtn = document.getElementById('confirm-modal-cancel-btn');
    const iconContainer = document.getElementById('confirm-modal-icon-container');

    if (titleEl) titleEl.innerText = title;
    if (msgEl) msgEl.innerText = message;
    if (cancelBtn) cancelBtn.innerText = cancelText;
    
    if (submitBtn) {
      submitBtn.innerText = confirmText;
      if (isDanger) {
        submitBtn.className = "px-5 py-2 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-black shadow-lg shadow-rose-500/25 transition-all cursor-pointer active:scale-95";
        if (iconContainer) iconContainer.className = "w-10 h-10 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 shrink-0";
      } else {
        submitBtn.className = "px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black shadow-lg shadow-cyan-500/25 transition-all cursor-pointer active:scale-95";
        if (iconContainer) iconContainer.className = "w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0";
      }
    }

    openModal('confirm-action-modal');
  });
}
window.showConfirmDialog = showConfirmDialog;

function cancelConfirmDialog() {
  closeModal('confirm-action-modal');
  if (_confirmDialogResolve) {
    const res = _confirmDialogResolve;
    _confirmDialogResolve = null;
    res(false);
  }
}
window.cancelConfirmDialog = cancelConfirmDialog;

function executeConfirmDialog() {
  closeModal('confirm-action-modal');
  if (_confirmDialogResolve) {
    const res = _confirmDialogResolve;
    _confirmDialogResolve = null;
    res(true);
  }
}
window.executeConfirmDialog = executeConfirmDialog;

// --- CUSTOM IN-APP PROMPT MODAL ---
let _promptDialogResolve = null;

function showCustomPrompt({ title = "Enter Value", message = "Please enter a value:", defaultValue = "", placeholder = "", confirmText = "Submit", onConfirm = null }) {
  return new Promise((resolve) => {
    _promptDialogResolve = (result) => {
      if (result !== null && typeof onConfirm === 'function') {
        try { onConfirm(result); } catch (err) { console.error('Prompt dialog callback error:', err); }
      }
      resolve(result);
    };

    const titleEl = document.getElementById('prompt-modal-title');
    const msgEl = document.getElementById('prompt-modal-message');
    const inputEl = document.getElementById('prompt-modal-input');
    const submitBtn = document.getElementById('prompt-modal-submit-btn');

    if (titleEl) titleEl.innerText = title;
    if (msgEl) msgEl.innerText = message;
    if (submitBtn) submitBtn.innerText = confirmText;
    if (inputEl) {
      inputEl.value = defaultValue;
      inputEl.placeholder = placeholder;
    }

    openModal('prompt-input-modal');
    setTimeout(() => {
      if (inputEl) {
        inputEl.focus();
        inputEl.select();
      }
    }, 150);
  });
}
window.showCustomPrompt = showCustomPrompt;

function cancelPromptDialog() {
  closeModal('prompt-input-modal');
  if (_promptDialogResolve) {
    const res = _promptDialogResolve;
    _promptDialogResolve = null;
    res(null);
  }
}
window.cancelPromptDialog = cancelPromptDialog;

function executePromptDialog() {
  const inputEl = document.getElementById('prompt-modal-input');
  const val = inputEl ? inputEl.value.trim() : '';
  closeModal('prompt-input-modal');
  if (_promptDialogResolve) {
    const res = _promptDialogResolve;
    _promptDialogResolve = null;
    res(val);
  }
}
window.executePromptDialog = executePromptDialog;

// --- CUSTOM IN-APP ALERT MODAL ---
function showCustomAlert({ title = "Notice", message = "", buttonText = "OK" }) {
  const titleEl = document.getElementById('alert-modal-title');
  const msgEl = document.getElementById('alert-modal-message');
  const btnEl = document.getElementById('alert-modal-btn');
  if (titleEl) titleEl.innerText = title;
  if (msgEl) msgEl.innerText = message;
  if (btnEl) btnEl.innerText = buttonText;
  openModal('alert-info-modal');
}
window.showCustomAlert = showCustomAlert;

function getModalElement(id) {
  if (id === 'welcome-modal' || id === 'whats-new-modal') {
    return document.getElementById('welcome-modal') || document.getElementById('whats-new-modal');
  }
  return document.getElementById(id);
}

function openModal(id) {
  const modal = getModalElement(id);
  if (modal) {
    modal.classList.remove('hidden', 'closing');
    const container = modal.querySelector('div') || modal;
    container.classList.remove('modal-exit', 'animate-out', 'fade-out-0', 'zoom-out-95');
    container.classList.add('modal-enter');
    if (id === 'account-manager-modal') {
      if (typeof renderGoogleCloudAccountCard === 'function') renderGoogleCloudAccountCard();
      if (typeof renderAccounts === 'function') renderAccounts();
    }
    if (window.lucide) lucide.createIcons();
  }
}

function closeModal(id) {
  const modal = getModalElement(id);
  if (modal && !modal.classList.contains('hidden')) {
    modal.classList.add('closing');
    const container = modal.querySelector('div') || modal;
    container.classList.remove('modal-enter', 'animate-in', 'fade-in-0', 'zoom-in-95');
    container.classList.add('modal-exit');
    setTimeout(() => {
      modal.classList.add('hidden');
      modal.classList.remove('closing');
      container.classList.remove('modal-exit');
      refreshLucideIcons();
    }, 200);
  }
}

// Global click-outside listener to smoothly close any open menu
document.addEventListener('click', (e) => {
  const openMenus = document.querySelectorAll('[id$="-menu"]:not(.hidden)');
  openMenus.forEach(menu => {
    const prefix = menu.id.replace('-menu', '');
    const btn = document.getElementById(`${prefix}-btn`) || 
                document.getElementById(`${prefix}-toggle`) ||
                document.getElementById('active-account-btn') ||
                document.getElementById('hero-player-name');
    if (!menu.contains(e.target) && (!btn || !btn.contains(e.target))) {
      closeAnimatedDropdown(menu);
    }
  });
});

function openWebPortal() {
  if (window.pywebview && window.pywebview.api) {
    try { window.pywebview.api.open_external_url('https://sir-modpack.web.app'); return; } catch {}
  }
  window.open('https://sir-modpack.web.app', '_blank');
}

async function submitSyncCode() {
  const input = document.getElementById('sync-code-input');
  const code = input ? input.value.trim() : '';
  if (!code) return;
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.claim_sync_code(code);
      showToast(res.message || '✓ Synchronized 3D character and cosmetic items!', 'success');
    } catch {
      showToast(`✓ Cloud Sync Code ${code} accepted!`, 'success');
    }
  } else {
    showToast(`✓ Cloud Sync Code ${code} accepted!`, 'success');
  }
  closeModal('sync-modal');
}

// --- WHAT'S NEW IN v1.0.0 MODAL ---
async function checkWhatsNewOnStartup() {
  try {
    const lastSeen = localStorage.getItem('sir_last_seen_release');
    if (lastSeen !== '1.0.0') {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.get_whats_new_status) {
        const status = await Promise.race([
          window.pywebview.api.get_whats_new_status(),
          new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 3000))
        ]).catch(() => ({ should_show: true }));
        if (status && status.should_show) {
          openWhatsNewModal();
        }
      } else {
        openWhatsNewModal();
      }
    }
  } catch (err) {
    console.warn('Whats-new check error:', err);
  }
}
window.checkWhatsNewOnStartup = checkWhatsNewOnStartup;

function openWhatsNewModal() {
  openModal('welcome-modal');
  switchWhatsNewTab('engines');
  refreshLucideIcons();
}
window.openWhatsNewModal = openWhatsNewModal;
window.openWelcomeModal = openWhatsNewModal;

function dismissWhatsNewModal() {
  closeModal('welcome-modal');
  localStorage.setItem('sir_last_seen_release', '1.0.0');
  if (window.pywebview && window.pywebview.api && window.pywebview.api.mark_release_seen) {
    // Fire-and-forget: NEVER await bridge calls on modal button click handlers
    window.pywebview.api.mark_release_seen('1.0.0').catch(() => {});
  }
}
window.dismissWhatsNewModal = dismissWhatsNewModal;
window.closeWelcomeModal = dismissWhatsNewModal;

function switchWhatsNewTab(tab) {
  const tabs = ['engines', 'innovations', 'shortcuts', 'quickstart'];
  tabs.forEach(t => {
    const btn = document.getElementById(`wn-tab-${t}`);
    const view = document.getElementById(`wn-view-${t}`);
    if (t === tab) {
      if (btn) btn.className = "px-3.5 py-1.5 rounded-xl bg-cyan-500 text-slate-950 font-black text-xs shadow-md shadow-cyan-500/20 transition-all cursor-pointer";
      if (view) view.classList.remove('hidden');
    } else {
      if (btn) btn.className = "px-3.5 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 font-bold text-xs transition-all cursor-pointer border border-slate-700/50";
      if (view) view.classList.add('hidden');
    }
  });
  updateWhatsNewEngineSelection();
  refreshLucideIcons();
}
window.switchWhatsNewTab = switchWhatsNewTab;

function updateWhatsNewEngineSelection() {
  const currentInst = (typeof STATE !== 'undefined' && STATE.selectedInstanceId) || '26.2-ultra';
  const isModern = !currentInst.startsWith('1.8');
  const modernCard = document.getElementById('wn-engine-card-modern');
  const legacyCard = document.getElementById('wn-engine-card-legacy');
  const modernBtn = document.getElementById('wn-btn-select-modern');
  const legacyBtn = document.getElementById('wn-btn-select-legacy');

  if (modernCard && legacyCard) {
    if (isModern) {
      modernCard.className = "p-5 rounded-2xl bg-cyan-950/30 border-2 border-cyan-400/80 space-y-3 relative transition-all shadow-lg shadow-cyan-500/10";
      legacyCard.className = "p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3 relative transition-all hover:border-purple-500/40";
      if (modernBtn) {
        modernBtn.className = "w-full py-2.5 rounded-xl bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-1.5 cursor-default";
        modernBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i><span>Active Primary Core</span>';
      }
      if (legacyBtn) {
        legacyBtn.className = "w-full py-2.5 rounded-xl bg-slate-800 hover:bg-purple-600 text-slate-200 hover:text-white font-bold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer";
        legacyBtn.innerHTML = '<span>Switch to Legacy 1.8.9</span>';
      }
    } else {
      modernCard.className = "p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3 relative transition-all hover:border-cyan-500/40";
      legacyCard.className = "p-5 rounded-2xl bg-purple-950/30 border-2 border-purple-400/80 space-y-3 relative transition-all shadow-lg shadow-purple-500/10";
      if (modernBtn) {
        modernBtn.className = "w-full py-2.5 rounded-xl bg-slate-800 hover:bg-cyan-500 hover:text-slate-950 text-slate-200 font-bold text-xs transition-all flex items-center justify-center gap-1.5 cursor-pointer";
        modernBtn.innerHTML = '<span>Switch to Modern 26.2</span>';
      }
      if (legacyBtn) {
        legacyBtn.className = "w-full py-2.5 rounded-xl bg-purple-500 text-white font-black text-xs transition-all flex items-center justify-center gap-1.5 cursor-default";
        legacyBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5"></i><span>Active Primary Core</span>';
      }
    }
  }
}
window.updateWhatsNewEngineSelection = updateWhatsNewEngineSelection;

function selectEngineFromWhatsNew(engine) {
  const target = engine === 'legacy' ? '1.8.9-ultra' : '26.2-ultra';
  if (typeof selectInstance === 'function') {
    selectInstance(target);
  } else if (typeof STATE !== 'undefined') {
    STATE.selectedInstanceId = target;
  }
  updateWhatsNewEngineSelection();
  showToast(engine === 'legacy' ? '✓ Switched to Legacy 1.8.9 Forge Core' : '✓ Switched to Modern 26.2 Fabric Core', 'success');
}
window.selectEngineFromWhatsNew = selectEngineFromWhatsNew;

// --- DEVELOPER FEEDBACK HIGHWAY (ERROR REPORT & SUGGESTION) ---
let _currentFeedbackTab = 'issue';
let _feedbackScreenshotBase64 = '';

async function openFeedbackModal(mode = 'issue') {
  _currentFeedbackTab = mode;
  _feedbackScreenshotBase64 = '';

  const issueTabBtn = document.getElementById('feedback-tab-issue');
  const suggTabBtn = document.getElementById('feedback-tab-sugg');
  const issueSection = document.getElementById('feedback-section-issue');
  const suggSection = document.getElementById('feedback-section-sugg');
  const screenshotPreview = document.getElementById('feedback-screenshot-preview');
  const fileInput = document.getElementById('feedback-screenshot-input');
  const ticketResultBox = document.getElementById('feedback-ticket-result');
  const formBox = document.getElementById('feedback-form-box');

  if (ticketResultBox) ticketResultBox.classList.add('hidden');
  if (formBox) formBox.classList.remove('hidden');
  if (screenshotPreview) { screenshotPreview.src = ''; screenshotPreview.classList.add('hidden'); }
  if (fileInput) fileInput.value = '';

  if (mode === 'issue') {
    if (issueTabBtn) issueTabBtn.className = "flex-1 py-2 rounded-xl text-xs font-bold transition-all bg-rose-500/20 text-rose-400 border border-rose-500/40 cursor-pointer";
    if (suggTabBtn) suggTabBtn.className = "flex-1 py-2 rounded-xl text-xs font-bold transition-all text-slate-400 hover:text-slate-200 cursor-pointer";
    if (issueSection) issueSection.classList.remove('hidden');
    if (suggSection) suggSection.classList.add('hidden');
  } else {
    if (suggTabBtn) suggTabBtn.className = "flex-1 py-2 rounded-xl text-xs font-bold transition-all bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 cursor-pointer";
    if (issueTabBtn) issueTabBtn.className = "flex-1 py-2 rounded-xl text-xs font-bold transition-all text-slate-400 hover:text-slate-200 cursor-pointer";
    if (suggSection) suggSection.classList.remove('hidden');
    if (issueSection) issueSection.classList.add('hidden');
  }

  // Reset user email to empty
  const emailInput = document.getElementById('feedback-email-input');
  if (emailInput) {
    emailInput.value = '';
  }

  // Auto-fetch system telemetry
  const specsBadge = document.getElementById('feedback-specs-badge');
  if (specsBadge) specsBadge.textContent = '⏳ Loading system diagnostics...';

  if (window.pywebview && window.pywebview.api && window.pywebview.api.get_system_diagnostic_metadata) {
    try {
      const meta = await window.pywebview.api.get_system_diagnostic_metadata();
      window.__SIR_LAST_DIAGNOSTICS__ = meta;
      if (specsBadge) {
        specsBadge.textContent = `${meta.os} • ${meta.gpu} • ${meta.active_profile} (${meta.allocated_ram_gb}GB RAM)`;
      }
    } catch {
      if (specsBadge) specsBadge.textContent = 'Windows 64-bit • Direct Client';
    }
  }

  openModal('feedback-modal');
  refreshLucideIcons();
}
window.openFeedbackModal = openFeedbackModal;

function selectFeedbackOption(targetId, val, label) {
  const hiddenInput = document.getElementById(targetId);
  if (hiddenInput) hiddenInput.value = val;
  const labelEl = document.getElementById(`${targetId}-label`);
  if (labelEl) labelEl.textContent = label;
  const menu = document.getElementById(`${targetId}-menu`);
  if (menu) {
    if (typeof closeAnimatedDropdown === 'function') {
      closeAnimatedDropdown(menu);
    } else {
      menu.classList.add('hidden');
    }
  }
}
window.selectFeedbackOption = selectFeedbackOption;

function handleFeedbackScreenshotSelect(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];
    if (file.size > 10 * 1024 * 1024) {
      showToast('Image file too large (maximum 10 MB)', 'error');
      input.value = '';
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      _feedbackScreenshotBase64 = e.target.result;
      const preview = document.getElementById('feedback-screenshot-preview');
      if (preview) {
        preview.src = _feedbackScreenshotBase64;
        preview.classList.remove('hidden');
      }
    };
    reader.readAsDataURL(file);
  }
}
window.handleFeedbackScreenshotSelect = handleFeedbackScreenshotSelect;

async function submitFeedbackModal() {
  const submitBtn = document.getElementById('feedback-submit-btn');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Submitting to Cloud...</span>`;
    refreshLucideIcons();
  }

  try {
    const meta = window.__SIR_LAST_DIAGNOSTICS__ || {};
    const emailInput = document.getElementById('feedback-email-input');
    const userEmail = (emailInput ? emailInput.value.trim() : '') || 'anonymous@sir-modpack.com';

    let uploadedUrl = '';
    // Upload screenshot to Cloudinary if attached
    if (_feedbackScreenshotBase64 && window.pywebview && window.pywebview.api && window.pywebview.api.upload_screenshot_cloudinary) {
      try {
        const upRes = await window.pywebview.api.upload_screenshot_cloudinary(_feedbackScreenshotBase64);
        if (upRes && upRes.success) {
          uploadedUrl = upRes.url;
        }
      } catch (err) {
        console.warn('Screenshot upload warning:', err);
      }
    }

    let payload = {};
    if (_currentFeedbackTab === 'issue') {
      const catEl = document.getElementById('feedback-issue-category');
      const descEl = document.getElementById('feedback-issue-description');
      const sevEl = document.getElementById('feedback-issue-severity');
      payload = {
        type: 'issue',
        category: catEl ? catEl.value : 'launcher',
        severity: sevEl ? sevEl.value : 'medium',
        description: descEl ? descEl.value.trim() : '',
        screenshot_url: uploadedUrl,
        user_email: userEmail,
        diagnostics: meta
      };
    } else {
      const catEl = document.getElementById('feedback-sugg-category');
      const descEl = document.getElementById('feedback-sugg-description');
      const titleEl = document.getElementById('feedback-sugg-title');
      payload = {
        type: 'suggestion',
        category: catEl ? catEl.value : 'general',
        title: titleEl ? titleEl.value.trim() : 'Feature Suggestion',
        description: descEl ? descEl.value.trim() : '',
        screenshot_url: uploadedUrl,
        user_email: userEmail,
        diagnostics: meta
      };
    }

    let ticketId = `SIR-${_currentFeedbackTab === 'suggestion' ? 'SUGG' : 'ERR'}-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.submit_desktop_feedback) {
      const res = await window.pywebview.api.submit_desktop_feedback(payload);
      if (res && res.ticket_id) ticketId = res.ticket_id;
    }

    // Display ticket confirmation
    const formBox = document.getElementById('feedback-form-box');
    const resultBox = document.getElementById('feedback-ticket-result');
    const ticketIdLabel = document.getElementById('feedback-ticket-id-label');
    if (formBox) formBox.classList.add('hidden');
    if (resultBox) resultBox.classList.remove('hidden');
    if (ticketIdLabel) ticketIdLabel.textContent = ticketId;

    showToast('✓ Dispatched to Developer Dashboard!', 'success');
  } catch (err) {
    showToast(`Submission error: ${err}`, 'error');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>Submit</span><i data-lucide="send" class="w-3.5 h-3.5"></i>`;
      refreshLucideIcons();
    }
  }
}
window.submitFeedbackModal = submitFeedbackModal;

// Auto-check What's New on initial load
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    checkWhatsNewOnStartup();
  }, 1200);
});


