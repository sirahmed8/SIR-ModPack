// --- CUSTOM CYBER DROPDOWN & ANIMATED LIST HELPERS ---
function openAnimatedDropdown(el) {
  if (!el) return;
  el.classList.remove('hidden', 'dropdown-animating-out');
  el.classList.add('dropdown-animating-in');

  const prefix = el.id.replace('-menu', '');
  const arrow = document.getElementById(`${prefix}-arrow`);
  if (arrow) arrow.style.transform = 'rotate(180deg)';
}

function closeAnimatedDropdown(el) {
  if (!el || el.classList.contains('hidden')) return;
  el.classList.remove('dropdown-animating-in');
  el.classList.add('dropdown-animating-out');

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
    closeAnimatedDropdown(menu);
    refreshLucideIcons();
  }
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.relative')) {
    document.querySelectorAll('[id$="-menu"]').forEach(m => {
      if (m.id !== 'account-menu') m.classList.add('hidden');
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


