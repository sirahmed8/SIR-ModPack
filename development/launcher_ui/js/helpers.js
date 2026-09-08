// --- CUSTOM CYBER DROPDOWN & ANIMATED LIST HELPERS ---
function openAnimatedDropdown(el) {
  if (!el) return;
  el.classList.remove('hidden', 'dropdown-animating-out');
  el.classList.add('dropdown-animating-in');
  if (el.parentElement) {
    el.parentElement.style.zIndex = '100';
  }

  const prefix = el.id.replace('-menu', '');
  const arrow = document.getElementById(`${prefix}-arrow`);
  if (arrow) arrow.style.transform = 'rotate(180deg)';
}

function closeAnimatedDropdown(el) {
  if (!el || el.classList.contains('hidden')) return;
  el.classList.remove('dropdown-animating-in');
  el.classList.add('dropdown-animating-out');
  if (el.parentElement && el.parentElement.style.zIndex === '100') {
    el.parentElement.style.zIndex = '';
  }

  const prefix = el.id.replace('-menu', '');
  const arrow = document.getElementById(`${prefix}-arrow`);
  if (arrow) arrow.style.transform = 'rotate(0deg)';

  setTimeout(() => {
    if (el.classList.contains('dropdown-animating-out')) {
      el.classList.add('hidden');
      el.classList.remove('dropdown-animating-out');
    }
  }, 160);
}

function toggleDropdown(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const isHidden = el.classList.contains('hidden') || el.classList.contains('dropdown-animating-out');

  if (id === 'account-menu' && typeof renderAccounts === 'function') {
    renderAccounts();
  }

  document.querySelectorAll('[id$="-menu"]').forEach(other => {
    if (other.id !== id && !other.classList.contains('hidden')) {
      closeAnimatedDropdown(other);
    }
  });

  if (isHidden) {
    openAnimatedDropdown(el);
  } else {
    closeAnimatedDropdown(el);
  }
}

function toggleCustomDropdown(menuId) {
  toggleDropdown(menuId);
}

function selectCyberDropdown(prefix, value, label) {
  const input = document.getElementById(`${prefix}-intensity`) || document.getElementById(`${prefix}-scale`) || document.getElementById(`${prefix}-input`);
  const labelEl = document.getElementById(`${prefix}-label`);
  const menu = document.getElementById(`${prefix}-menu`);
  if (input) input.value = value;
  if (labelEl) labelEl.textContent = label;
  if (menu) {
    menu.querySelectorAll('.dropdown-opt').forEach(opt => {
      if (opt.getAttribute('data-val') === String(value)) {
        opt.className = 'dropdown-opt flex items-center justify-between px-3 py-2 text-xs font-bold rounded-xl cursor-pointer transition-all bg-cyan-500/15 text-cyan-400 border border-cyan-500/30';
        if (!opt.querySelector('svg') && !opt.querySelector('i')) {
          const icon = document.createElement('i');
          icon.setAttribute('data-lucide', 'check');
          icon.className = 'w-3.5 h-3.5 text-cyan-400';
          opt.appendChild(icon);
        }
      } else {
        opt.className = 'dropdown-opt flex items-center justify-between px-3 py-2 text-xs font-bold rounded-xl cursor-pointer transition-all text-slate-300 hover:bg-slate-800/80 hover:text-white';
        const chk = opt.querySelector('svg, i');
        if (chk) chk.remove();
      }
    });
    if (window.refreshLucideIcons) refreshLucideIcons();
    
    const wrapper = document.getElementById(prefix);
    if (wrapper) {
      toggleCustomDropdown(prefix);
    }
  }
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.relative')) {
    document.querySelectorAll('[id$="-menu"]').forEach(m => {
      if (!m.classList.contains('hidden')) {
        closeAnimatedDropdown(m);
      }
    });
  }
});


async function submitNewAccount() {
  const input = document.getElementById('offline-name-input');
  const name = input ? input.value.trim() : '';
  if (!name) return;
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.add_offline_account(name);
    } catch {}
  } else {
    STATE.accounts.push({ name, type: "offline", active: true });
    STATE.activeAccountName = name;
  }

  if (input) input.value = '';
  closeModal('add-account-modal');
  await loadAccounts();
}

function selectOfflineSkinPreset(name, url) {
  const input = document.getElementById('offline-name-input');
  if (input) input.value = name;
}

function setOfflineModel(model) {
  const classic = document.getElementById('offline-model-classic');
  const slim = document.getElementById('offline-model-slim');
  if (classic && slim) {
    if (model === 'classic') {
      classic.className = 'flex-1 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold transition-all';
      slim.className = 'flex-1 py-1.5 rounded-xl bg-slate-800 text-slate-400 border border-transparent text-xs font-bold transition-all';
    } else {
      slim.className = 'flex-1 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold transition-all';
      classic.className = 'flex-1 py-1.5 rounded-xl bg-slate-800 text-slate-400 border border-transparent text-xs font-bold transition-all';
    }
  }
}

// --- SMART KEYBOARD FORM ERGONOMICS (ENTER KEY) ---
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter' || e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
  const target = e.target;
  if (!target) return;

  // 1. Textareas always allow standard multi-line insertion
  if (target.tagName === 'TEXTAREA') return;

  if (target.tagName === 'INPUT') {
    const form = target.closest('form');
    if (form) {
      const inputs = Array.from(form.elements).filter(el => 
        (el.tagName === 'INPUT' || el.tagName === 'SELECT') && 
        el.type !== 'hidden' && !el.disabled && el.offsetParent !== null
      );
      const currentIndex = inputs.indexOf(target);
      if (currentIndex !== -1 && currentIndex < inputs.length - 1) {
        e.preventDefault();
        inputs[currentIndex + 1].focus();
        if (typeof inputs[currentIndex + 1].select === 'function') {
          inputs[currentIndex + 1].select();
        }
        return;
      } else if (currentIndex === inputs.length - 1) {
        const submitBtn = form.querySelector('button[type="submit"], .btn-primary, button.bg-cyan-500, button.bg-emerald-500');
        if (submitBtn) {
          e.preventDefault();
          submitBtn.click();
          return;
        }
      }
    }

    // Modal context without standard <form> tag
    const modal = target.closest('.modal-card, .modal-backdrop, #settings-modal');
    if (modal) {
      const inputs = Array.from(modal.querySelectorAll('input:not([type="hidden"]), select:not([disabled])')).filter(el => 
        !el.disabled && el.offsetParent !== null
      );
      const currentIndex = inputs.indexOf(target);
      if (inputs.length > 1 && currentIndex !== -1 && currentIndex < inputs.length - 1) {
        e.preventDefault();
        inputs[currentIndex + 1].focus();
        if (typeof inputs[currentIndex + 1].select === 'function') {
          inputs[currentIndex + 1].select();
        }
        return;
      }

      // Single input or last input in modal: trigger primary action button
      const primaryBtn = modal.querySelector('button.bg-cyan-500, button.bg-emerald-500, button[onclick*="submit"], button[onclick*="add"], button[onclick*="save"]');
      if (primaryBtn) {
        e.preventDefault();
        primaryBtn.click();
        return;
      }
    }

    // Standalone quick search inputs: blur on Enter to let user view results
    if (target.type === 'search' || target.id?.includes('search') || target.classList?.contains('search-input')) {
      target.blur();
    }
  }
});

function scrollQuickPresets(delta) {
  const bar = document.getElementById('quick-presets-bar');
  if (bar) {
    bar.scrollBy({ left: delta, behavior: 'smooth' });
  }
}
