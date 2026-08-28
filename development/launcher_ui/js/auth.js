// --- ACCOUNTS MANAGEMENT ---
async function loadAccounts() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const data = await window.pywebview.api.get_accounts();
      if (data && Array.isArray(data.accounts)) {
        const seen = new Set();
        STATE.accounts = data.accounts.map(a => ({
          name: a.displayName || a.name || a.username || 'SirPlayer',
          type: a.accountType || a.type || 'offline',
          skinUrl: a.skinUrl || `https://mc-heads.net/avatar/${encodeURIComponent(a.displayName || a.name || 'Steve')}/32`
        })).filter(a => {
          const k = a.name.toLowerCase();
          if (seen.has(k)) return false;
          seen.add(k);
          return true;
        });
        STATE.activeAccountName = data.active || (STATE.accounts[0] ? STATE.accounts[0].name : 'SirAhmed1');
      }
    } catch (e) {
      console.warn("Could not load accounts from bridge:", e);
    }
  }

  if (!STATE.accounts || STATE.accounts.length === 0) {
    STATE.accounts = [
      { name: "SirAhmed1", type: "offline", skinUrl: "https://mc-heads.net/avatar/SirAhmed1/32" },
      { name: "W1hm", type: "microsoft", skinUrl: "https://mc-heads.net/avatar/W1hm/32" }
    ];
    STATE.activeAccountName = "SirAhmed1";
  }

  renderAccounts();
  renderLaunchpad();
}

function renderAccounts() {
  const container = document.getElementById('accounts-list-container');
  const mgrContainer = document.getElementById('account-manager-list');

  if (container) {
    container.innerHTML = STATE.accounts.map(acc => {
      const isAct = acc.name === STATE.activeAccountName;
      const isMs = (acc.type || '').toLowerCase().includes('microsoft') || (acc.type || '').toLowerCase() === 'msa';
      return `
        <div class="flex items-center justify-between p-2 rounded-xl border transition-all ${
          isAct ? 'bg-cyan-500/15 border-cyan-500/50' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
        }">
          <div onclick="selectAccount('${escapeHtml(acc.name)}')" class="flex items-center gap-2.5 min-w-0 cursor-pointer flex-1">
            <img src="https://mc-heads.net/avatar/${encodeURIComponent(acc.name)}/32" class="w-6 h-6 rounded-md object-cover border border-slate-700" onerror="this.src='https://minotar.net/avatar/Steve/32.png'">
            <div class="min-w-0">
              <h5 class="text-xs font-bold text-slate-100 truncate">${escapeHtml(acc.name)}</h5>
              <span class="text-[9px] font-mono ${isMs ? 'text-emerald-400' : 'text-cyan-400'}">${isMs ? 'Microsoft Official' : 'Offline / IAS'}</span>
            </div>
          </div>
          <div class="flex items-center gap-1">
            ${isAct ? '<span class="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_#00e5ff]"></span>' : `
              <button onclick="selectAccount('${escapeHtml(acc.name)}')" class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold text-slate-300 hover:text-cyan-300">Use</button>
            `}
            <button onclick="removeAccount('${escapeHtml(acc.name)}')" class="p-1.5 rounded-full text-slate-500 hover:text-rose-400 hover:bg-rose-500/15 text-xs transition-all flex items-center justify-center w-6 h-6" title="Remove Account">✕</button>
          </div>
        </div>
      `;
    }).join('');
  }

  if (mgrContainer) {
    if (!STATE.accounts || STATE.accounts.length === 0) {
      mgrContainer.innerHTML = `
        <div class="p-6 text-center text-slate-400 text-xs bg-slate-950/60 rounded-2xl border border-slate-800">
          No registered accounts yet. Click "+ Microsoft" or "+ Offline" above to add your first profile.
        </div>
      `;
    } else {
      mgrContainer.innerHTML = STATE.accounts.map(acc => {
        const isAct = acc.name === STATE.activeAccountName;
        const isMs = (acc.type || '').toLowerCase().includes('microsoft') || (acc.type || '').toLowerCase() === 'msa';
        return `
          <div class="flex items-center justify-between p-3 rounded-2xl border transition-all ${
            isAct ? 'bg-cyan-500/15 border-cyan-500/50 shadow-md' : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
          }">
            <div class="flex items-center gap-3 min-w-0 flex-1">
              <img src="https://mc-heads.net/avatar/${encodeURIComponent(acc.name)}/40" class="w-10 h-10 rounded-xl object-cover border border-slate-700 shrink-0 shadow-sm" onerror="this.src='https://minotar.net/avatar/Steve/40.png'">
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <h4 class="text-sm font-bold text-slate-100 truncate">${escapeHtml(acc.name)}</h4>
                  <span class="badge-tag text-[9px] px-2 py-0.5 rounded-full font-mono ${isMs ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' : 'bg-cyan-950 text-cyan-400 border border-cyan-800/40'}">
                    ${isMs ? 'Microsoft Official' : 'Offline / IAS'}
                  </span>
                  ${isAct ? '<span class="text-[10px] font-bold text-emerald-400">● Active</span>' : ''}
                </div>
                <p class="text-[10px] text-slate-500 font-mono mt-0.5">Profile ID: ${escapeHtml(acc.name.toLowerCase())} • Fast IAS Switch Enabled</p>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              ${!isAct ? `
                <button onclick="selectAccount('${escapeHtml(acc.name)}'); closeModal('account-manager-modal')" class="px-3 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs font-bold border border-cyan-500/40 transition-all active:scale-95 cursor-pointer">Select</button>
              ` : `
                <span class="px-3 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 text-xs font-bold border border-emerald-500/40">In Use</span>
              `}
              <button onclick="removeAccount('${escapeHtml(acc.name)}')" class="p-2 rounded-xl text-slate-500 hover:text-rose-400 hover:bg-rose-500/15 text-xs transition-all flex items-center justify-center cursor-pointer" title="Remove Profile">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
        `;
      }).join('');
    }
  }
  refreshLucideIcons();
}

async function selectAccount(name) {
  STATE.activeAccountName = name;
  const acc = STATE.accounts.find(a => a.name === name);
  if (acc) STATE.activeAccount = acc;

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.select_account(name);
    } catch (e) {
      console.warn("Select account bridge failed", e);
    }
  }

  renderAccounts();
  renderLaunchpad();
  toggleDropdown('account-menu');
}

async function removeAccount(name) {
  const confirmed = await showConfirmDialog({
    title: "Remove Account",
    message: `Are you sure you want to remove account @${name}? This will unlink the profile from SIR Launcher.`,
    icon: "trash-2",
    confirmText: "Remove Account",
    cancelText: "Cancel",
    isDanger: true
  });
  if (!confirmed) return;

  STATE.accounts = STATE.accounts.filter(a => a.name !== name);
  if (STATE.activeAccountName === name) {
    STATE.activeAccountName = STATE.accounts.length > 0 ? STATE.accounts[0].name : 'No account';
    STATE.activeAccount = STATE.accounts.length > 0 ? STATE.accounts[0] : null;
  }

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.remove_account(name);
    } catch {}
  }

  renderAccounts();
  renderSettingsAccountsList();
  renderLaunchpad();
  showToast(`✓ Removed account @${name}`, 'success');
}

async function refreshOfficialAccounts() {
  await loadAccounts();
  showToast("✓ Synchronized accounts from SIR / IAS profile database!", "success");
}

let _currentMsUserCode = '';
let _currentMsAuthUri = 'https://microsoft.com/link';

function submitMicrosoftBrowserAccount() {
  return submitMicrosoftAccount();
}

function submitMicrosoftDeviceAccount() {
  return submitMicrosoftAccount();
}

async function submitMicrosoftAccount() {
  closeModal('add-ms-account-modal');
  openModal('ms-browser-auth-modal');
  const statusEl = document.getElementById('ms-auth-status');
  const spinnerEl = document.getElementById('ms-auth-spinner');

  if (statusEl) statusEl.textContent = 'Opening Microsoft sign-in in your browser...';
  if (spinnerEl) spinnerEl.style.display = 'block';

  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.start_microsoft_browser_auth();
      if (!res || !res.success) {
        if (statusEl) statusEl.textContent = '✗ ' + (res?.error || 'Failed to start browser login');
        if (spinnerEl) spinnerEl.style.display = 'none';
        return;
      }

      if (statusEl) statusEl.textContent = 'Waiting for your sign-in in browser...';
      showToast('Opening Microsoft sign-in in your browser...', 'info');

      // Poll until Microsoft authorization completes via local loopback server
      STATE._msAuthPolling = true;
      let attempts = 0;
      const maxAttempts = 200; // 5 mins
      const poll = async () => {
        if (!STATE._msAuthPolling) return;
        attempts++;
        if (attempts > maxAttempts) {
          if (statusEl) statusEl.textContent = '✗ Sign-in timed out. Click Cancel and try again.';
          if (spinnerEl) spinnerEl.style.display = 'none';
          return;
        }
        try {
          const pollRes = await window.pywebview.api.poll_microsoft_browser_auth();
          if (pollRes?.success) {
            if (statusEl) statusEl.textContent = '✓ Welcome, ' + (pollRes.name || '') + '!';
            if (spinnerEl) spinnerEl.style.display = 'none';
            setTimeout(async () => {
              closeModal('ms-browser-auth-modal');
              await loadAccounts();
              showToast('✓ Microsoft account @' + (pollRes.name || '') + ' successfully connected!', 'success');
            }, 1200);
            return;
          } else if (pollRes?.pending) {
            setTimeout(poll, 1200);
          } else {
            if (statusEl) statusEl.textContent = '✗ ' + (pollRes?.error || 'Sign-in failed');
            if (spinnerEl) spinnerEl.style.display = 'none';
          }
        } catch {
          setTimeout(poll, 1500);
        }
      };
      setTimeout(poll, 1200);
    } catch (e) {
      if (statusEl) statusEl.textContent = '✗ Error: ' + (e.message || e);
      if (spinnerEl) spinnerEl.style.display = 'none';
    }
  } else {
    if (statusEl) statusEl.textContent = '[Simulation] Web Browser Login opened.';
    if (spinnerEl) spinnerEl.style.display = 'none';
  }
}

function cancelMicrosoftAuth() {
  STATE._msAuthPolling = false;
  closeModal('ms-browser-auth-modal');
}


// --- ADD OFFLINE ACCOUNT ---
async function addOfflineAccount() {
  const nameInput = document.getElementById('new-offline-name');
  const name = nameInput ? nameInput.value.trim() : '';
  if (!name || name.length < 2) {
    showToast('Please enter a valid username (at least 2 characters).', 'error'); return;
    return;
  }
  // Check for duplicates
  if (STATE.accounts.find(a => a.name.toLowerCase() === name.toLowerCase())) {
    showToast(`Account @${name} already exists.`, 'error'); return;
    return;
  }

  const newAcc = { name, type: 'offline', active: false, skinUrl: `https://mc-heads.net/avatar/${encodeURIComponent(name)}/32` };
  STATE.accounts.push(newAcc);

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.add_offline_account(name);
    } catch (e) {
      console.warn('addOfflineAccount bridge failed', e);
    }
  }

  if (nameInput) nameInput.value = '';
  renderAccounts();
  showToast(`✓ Added offline account @${name}`, 'success');
}


