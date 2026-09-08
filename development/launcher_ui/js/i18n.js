
// =============================================================================
// UNIVERSAL CUSTOM DIALOG & TOAST SYSTEM (Replaces Native Browser Alerts)
// =============================================================================
function showConfirmDialog({
  title = "Confirm Action",
  message = "Are you sure you want to proceed?",
  icon = "alert-triangle",
  confirmText = "Confirm",
  cancelText = "Cancel",
  isDanger = true
}) {
  return new Promise((resolve) => {
    const modal = document.getElementById('custom-dialog-modal');
    if (!modal) {
      resolve(confirm(message));
      return;
    }

    const titleEl = document.getElementById('dialog-title');
    const msgEl = document.getElementById('dialog-message');
    const iconContainer = document.getElementById('dialog-icon-container');
    const iconEl = document.getElementById('dialog-icon');
    const confirmBtn = document.getElementById('dialog-confirm-btn');
    const cancelBtn = document.getElementById('dialog-cancel-btn');

    if (titleEl) titleEl.innerText = title;
    if (msgEl) msgEl.innerText = message;
    if (cancelBtn) {
      cancelBtn.innerText = cancelText;
      cancelBtn.style.display = cancelText ? 'block' : 'none';
    }
    if (confirmBtn) {
      confirmBtn.innerText = confirmText;
      if (isDanger) {
        confirmBtn.className = "px-5 py-2.5 rounded-xl text-xs font-black bg-rose-500 hover:bg-rose-400 text-white shadow-lg shadow-rose-500/20 transition-all hover:scale-105 active:scale-95";
      } else {
        confirmBtn.className = "px-5 py-2.5 rounded-xl text-xs font-black bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all hover:scale-105 active:scale-95";
      }
    }

    if (iconContainer) {
      if (isDanger) {
        iconContainer.className = "w-12 h-12 rounded-2xl bg-rose-500/15 border border-rose-500/40 flex items-center justify-center text-rose-500 shrink-0 shadow-lg shadow-rose-500/10";
      } else {
        iconContainer.className = "w-12 h-12 rounded-2xl bg-cyan-500/15 border border-cyan-500/40 flex items-center justify-center text-cyan-500 shrink-0 shadow-lg shadow-cyan-500/10";
      }
    }

    if (iconEl) {
      iconEl.setAttribute('data-lucide', icon);
    }
    refreshLucideIcons();

    modal.classList.remove('hidden');

    const handleConfirm = () => {
      cleanup();
      resolve(true);
    };

    const handleCancel = () => {
      cleanup();
      resolve(false);
    };

    const cleanup = () => {
      modal.classList.add('hidden');
      confirmBtn.removeEventListener('click', handleConfirm);
      if (cancelBtn) cancelBtn.removeEventListener('click', handleCancel);
    };

    confirmBtn.addEventListener('click', handleConfirm, { once: true });
    if (cancelBtn) cancelBtn.addEventListener('click', handleCancel, { once: true });
  });
}

function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('sir-toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'sir-toast-container';
    toastContainer.className = 'fixed bottom-6 right-6 z-[999999] flex flex-col gap-2 pointer-events-none';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const isLight = document.documentElement.classList.contains('light');
  
  let iconName = 'info';
  let borderClass = 'border-cyan-500/40 text-cyan-400';
  if (type === 'success' || message.includes('✓')) {
    iconName = 'check-circle';
    borderClass = isLight ? 'border-emerald-500 text-emerald-700 bg-white shadow-xl' : 'border-emerald-500/50 text-emerald-400 bg-slate-900/95';
  } else if (type === 'error' || type === 'danger') {
    iconName = 'alert-circle';
    borderClass = isLight ? 'border-rose-500 text-rose-700 bg-white shadow-xl' : 'border-rose-500/50 text-rose-400 bg-slate-900/95';
  } else {
    borderClass = isLight ? 'border-cyan-500 text-cyan-700 bg-white shadow-xl' : 'border-cyan-500/50 text-cyan-400 bg-slate-900/95';
  }

  toast.className = `pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-2xl border shadow-2xl backdrop-blur-xl transition-all duration-300 transform translate-y-4 opacity-0 ${borderClass}`;
  toast.innerHTML = `
    <i data-lucide="${iconName}" class="w-5 h-5 shrink-0"></i>
    <span class="text-xs font-bold text-slate-800 dark:text-slate-100">${escapeHtml(message.replace(/^[✓⚠❌ℹ]\s*/, ''))}</span>
  `;

  toastContainer.appendChild(toast);
  refreshLucideIcons();

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-4', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
  });

  setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('translate-y-4', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}


async function loadInstancesFromBridge() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const data = await window.pywebview.api.get_instances();
      if (data && Array.isArray(data.instances) && data.instances.length > 0) {
        STATE.instances = data.instances;
        if (data.selected) STATE.selectedInstanceId = data.selected;
      }
    } catch (e) {
      console.warn("Could not load instances from bridge:", e);
    }
  }
  renderLaunchpad();
}


function refreshLucideIcons() {
  try {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
      window.lucide.createIcons();
    }
  } catch (err) {
    console.warn('Lucide icon render error:', err);
  }
}

