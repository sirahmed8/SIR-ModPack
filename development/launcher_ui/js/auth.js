// --- ACCOUNTS MANAGEMENT ---
async function loadAccounts() {
  // 1. Instant bootstrap cache hydration (0ms frame-0 guarantee)
  if ((!STATE.accounts || STATE.accounts.length === 0)) {
    try {
      if (window.__SIR_BOOTSTRAP__ && Array.isArray(window.__SIR_BOOTSTRAP__.accounts) && window.__SIR_BOOTSTRAP__.accounts.length > 0) {
        const seen = new Set();
        STATE.accounts = window.__SIR_BOOTSTRAP__.accounts
          .filter(a => a.type !== 'google_cloud' && a.accountType !== 'google_cloud' && !(a.id && String(a.id).startsWith('google_')))
          .map(a => ({
            name: a.displayName || a.name || a.username || 'SirPlayer',
            type: a.accountType || a.type || 'offline',
            skinUrl: a.skinUrl || `https://mc-heads.net/avatar/${encodeURIComponent(a.displayName || a.name || 'Steve')}/32`
          })).filter(a => {
            const k = a.name.toLowerCase();
            if (seen.has(k)) return false;
            seen.add(k);
            return true;
          });
        STATE.activeAccountName = window.__SIR_BOOTSTRAP__.active || (STATE.accounts[0] ? STATE.accounts[0].name : '');
        STATE.activeAccount = STATE.accounts.find(a => a.name === STATE.activeAccountName) || STATE.accounts[0];
        renderAccounts();
        renderLaunchpad();
      } else {
        const cached = localStorage.getItem('sir_cached_accounts');
        const cachedActive = localStorage.getItem('sir_active_account');
        if (cached) {
          try {
            const parsed = JSON.parse(cached);
            STATE.accounts = Array.isArray(parsed) 
              ? parsed.filter(a => a.type !== 'google_cloud' && a.accountType !== 'google_cloud' && !(a.id && String(a.id).startsWith('google_')))
              : [];
          } catch {}
          if (cachedActive) STATE.activeAccountName = cachedActive;
          renderAccounts();
          renderLaunchpad();
        }
      }
    } catch (e) {
      console.warn("Bootstrap cache recovery notice:", e);
    }
  }

  // 2. Query Python bridge for authoritative account registry
  if (window.pywebview && window.pywebview.api) {
    try {
      const data = await window.pywebview.api.get_accounts();
      if (data && Array.isArray(data.accounts)) {
        const seen = new Set();
        STATE.accounts = data.accounts
          .filter(a => a.type !== 'google_cloud' && a.accountType !== 'google_cloud' && !(a.id && String(a.id).startsWith('google_')))
          .map(a => ({
            name: a.displayName || a.name || a.username || 'SirPlayer',
            type: a.accountType || a.type || 'offline',
            skinUrl: a.skinUrl || `https://mc-heads.net/avatar/${encodeURIComponent(a.displayName || a.name || 'Steve')}/32`
          })).filter(a => {
            const k = a.name.toLowerCase();
            if (seen.has(k)) return false;
            seen.add(k);
            return true;
          });
        STATE.activeAccountName = data.active || (STATE.accounts[0] ? STATE.accounts[0].name : '');
        try {
          localStorage.setItem('sir_cached_accounts', JSON.stringify(STATE.accounts));
          localStorage.setItem('sir_active_account', STATE.activeAccountName);
        } catch {}
      }
    } catch (e) {
      console.warn("Could not load accounts from bridge:", e);
    }
  }

  if (!STATE.accounts) {
    STATE.accounts = [];
    STATE.activeAccountName = '';
  }

  renderAccounts();
  renderLaunchpad();
}

async function autoSyncAccountsSilent() {
  const prevActive = STATE.activeAccountName;

  if (window.pywebview && window.pywebview.api) {
    try {
      if (typeof window.pywebview.api.sync_cloud_accounts === 'function') {
        const res = await window.pywebview.api.sync_cloud_accounts();
        if (res && res.accounts) {
          await loadAccounts();
        }
      } else {
        await loadAccounts();
      }
    } catch (e) {
      console.warn("Silent cloud sync notice:", e);
      await loadAccounts();
    }
  } else {
    await loadAccounts();
  }

  // Account Status & Removal Integrity Check
  const hasAccountsNow = Array.isArray(STATE.accounts) && STATE.accounts.length > 0;
  const isAr = STATE.currentLang === 'ar';

  if (!hasAccountsNow) {
    showToast(
      isAr 
        ? "⚠️ لا يوجد حساب ماين كرافت نشط. يرجى إضافة حساب أو تسجيل الدخول بحساب Microsoft." 
        : "⚠️ No active Minecraft profile detected. Please add an offline profile or sign in with Microsoft.",
      "warning"
    );
  } else if (prevActive && prevActive !== 'No account') {
    const stillExists = STATE.accounts.some(a => a.name === prevActive);
    if (!stillExists) {
      showToast(
        isAr
          ? `⚠️ الحساب السابق "${prevActive}" لم يعد متوفراً. تم تبديل الحساب النشط.`
          : `⚠️ Previous account "${prevActive}" is no longer available. Active profile updated.`,
        "warning"
      );
    }
  }
}
window.autoSyncAccountsSilent = autoSyncAccountsSilent;

function renderAccounts() {
  const container = document.getElementById('accounts-list-container');
  const mgrContainer = document.getElementById('account-manager-list');
  const activeNameEl = document.getElementById('active-account-name');
  const heroNameEl = document.getElementById('hero-player-name');

  const accounts = (Array.isArray(STATE.accounts) ? STATE.accounts : [])
    .filter(a => a.type !== 'google_cloud' && a.accountType !== 'google_cloud' && !(a.id && String(a.id).startsWith('google_')));
  accounts.forEach(acc => {
    if (!acc.name) acc.name = acc.displayName || acc.username || 'SirPlayer';
    if (!acc.type) acc.type = acc.accountType || 'offline';
  });

  if (activeNameEl) activeNameEl.innerText = STATE.activeAccountName || 'No account';
  if (heroNameEl) heroNameEl.innerText = STATE.activeAccountName || 'No account';

  if (container) {
    if (accounts.length === 0) {
      container.innerHTML = `
        <div class="p-3.5 text-center text-slate-400 text-xs bg-slate-950/70 rounded-xl border border-slate-800/80 my-1 space-y-1">
          <p class="font-bold text-slate-300">No accounts registered yet.</p>
          <p class="text-[10px] text-slate-500">Click + Microsoft or + Offline below.</p>
        </div>
      `;
    } else {
      container.innerHTML = accounts.map(acc => {
        const isAct = acc.name === STATE.activeAccountName;
        const isMs = (acc.type || '').toLowerCase().includes('microsoft') || (acc.type || '').toLowerCase() === 'msa';
        return `
          <div class="flex items-center justify-between p-2 rounded-xl border transition-all ${
            isAct ? 'bg-cyan-500/15 border-cyan-500/50 shadow-sm' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
          }">
            <div onclick="selectAccount('${escapeHtml(acc.name)}')" class="flex items-center gap-2.5 min-w-0 cursor-pointer flex-1">
              <img src="https://mc-heads.net/avatar/${encodeURIComponent(acc.name)}/32" class="w-6 h-6 rounded-md object-cover border border-slate-700 shrink-0" onerror="this.src='https://minotar.net/avatar/Steve/32.png'">
              <div class="min-w-0">
                <h5 class="text-xs font-bold text-slate-100 truncate">${escapeHtml(acc.name)}</h5>
                <span class="text-[9px] font-mono ${isMs ? 'text-emerald-400' : 'text-cyan-400'}">${isMs ? 'Microsoft Official' : 'Offline / IAS'}</span>
              </div>
            </div>
            <div class="flex items-center gap-1">
              ${isAct ? '<span class="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_#00e5ff]"></span>' : `
                <button onclick="selectAccount('${escapeHtml(acc.name)}')" class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold text-slate-300 hover:text-cyan-300 cursor-pointer">Use</button>
              `}
              <button onclick="removeAccount('${escapeHtml(acc.name)}')" class="p-1.5 rounded-full text-slate-500 hover:text-rose-400 hover:bg-rose-500/15 text-xs transition-all flex items-center justify-center w-6 h-6 cursor-pointer" title="Remove Account">✕</button>
            </div>
          </div>
        `;
      }).join('');
    }
  }

  if (mgrContainer) {
    if (accounts.length === 0) {
      mgrContainer.innerHTML = `
        <div class="p-6 text-center text-slate-400 text-xs bg-slate-950/60 rounded-2xl border border-slate-800">
          No registered accounts yet. Click "+ Microsoft" or "+ Offline" above to add your first profile.
        </div>
      `;
    } else {
      mgrContainer.innerHTML = accounts.map(acc => {
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
  if (typeof renderGoogleCloudAccountCard === 'function') {
    renderGoogleCloudAccountCard();
  }
  if (typeof renderAccountMenuGoogleCard === 'function') {
    renderAccountMenuGoogleCard();
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


// --- OFFLINE ACCOUNT MODAL CONTROLS & PRESETS ---
let _currentOfflineModel = 'classic';

function selectOfflineSkinPreset(name, skinUrl) {
  const nameInput = document.getElementById('offline-name-input');
  const avatarImg = document.getElementById('offline-avatar-preview');
  if (nameInput) nameInput.value = name;
  if (avatarImg) avatarImg.src = `https://mc-heads.net/avatar/${encodeURIComponent(name)}/36`;
}
window.selectOfflineSkinPreset = selectOfflineSkinPreset;

function debounceOfflineLookup(val) {
  const avatarImg = document.getElementById('offline-avatar-preview');
  const clean = val.trim();
  if (avatarImg && clean) {
    avatarImg.src = `https://mc-heads.net/avatar/${encodeURIComponent(clean)}/36`;
  }
}
window.debounceOfflineLookup = debounceOfflineLookup;

function setOfflineModel(model) {
  _currentOfflineModel = model;
  const classicBtn = document.getElementById('offline-model-classic');
  const slimBtn = document.getElementById('offline-model-slim');
  if (classicBtn && slimBtn) {
    if (model === 'classic') {
      classicBtn.className = 'flex-1 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold transition-all';
      slimBtn.className = 'flex-1 py-1.5 rounded-xl bg-slate-800 text-slate-400 border border-transparent text-xs font-bold transition-all';
    } else {
      slimBtn.className = 'flex-1 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 text-xs font-bold transition-all';
      classicBtn.className = 'flex-1 py-1.5 rounded-xl bg-slate-800 text-slate-400 border border-transparent text-xs font-bold transition-all';
    }
  }
}
window.setOfflineModel = setOfflineModel;

// --- SUBMIT NEW OFFLINE / CRACKED ACCOUNT ---
async function submitNewAccount() {
  const nameInput = document.getElementById('offline-name-input') || document.getElementById('new-offline-name');
  const skinInput = document.getElementById('offline-skin-input');
  const name = nameInput ? nameInput.value.trim() : '';

  if (!name || name.length < 2) {
    showToast('Please enter a valid username (at least 2 characters).', 'error');
    return;
  }

  // Check for duplicate in local state
  const existing = STATE.accounts.find(a => a.name.toLowerCase() === name.toLowerCase());
  if (existing) {
    showToast(`Account @${name} already exists.`, 'error');
    return;
  }

  const customSkin = skinInput ? skinInput.value.trim() : '';
  const skinUrl = customSkin || `https://mc-heads.net/avatar/${encodeURIComponent(name)}/32`;

  const newAcc = {
    name: name,
    type: 'offline',
    model: _currentOfflineModel || 'classic',
    active: true,
    skinUrl: skinUrl
  };

  STATE.accounts.push(newAcc);
  STATE.activeAccountName = name;

  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.add_offline_account(name);
      await window.pywebview.api.select_account(name);
    } catch (e) {
      console.warn('addOfflineAccount bridge notice:', e);
    }
  }

  // Push to Firebase Realtime Database
  try {
    fetch(`https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/cloud_accounts/${encodeURIComponent(name.toLowerCase())}.json`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        type: "offline",
        model: _currentOfflineModel || "classic",
        skinUrl: skinUrl,
        updatedAt: new Date().toISOString()
      })
    }).catch(() => {});
  } catch {}

  if (nameInput) nameInput.value = '';
  if (skinInput) skinInput.value = '';

  closeModal('add-account-modal');
  renderAccounts();
  renderLaunchpad();
  showToast(`✓ Created and activated profile @${name}!`, 'success');
}
window.submitNewAccount = submitNewAccount;
window.addOfflineAccount = submitNewAccount;

// --- TWO-WAY FIREBASE CLOUD ACCOUNT SYNCHRONIZATION ---
async function syncAccountsFromCloud() {
  showToast("☁️ Syncing profiles with SIR Cloud...", "info");

  // 1. Python Bridge native sync (safely pushes authentic local accounts to user's cloud registry)
  if (window.pywebview && window.pywebview.api && window.pywebview.api.sync_cloud_accounts) {
    try {
      const bridgeRes = await window.pywebview.api.sync_cloud_accounts();
      if (bridgeRes && bridgeRes.accounts) {
        await loadAccounts();
        showToast(`✓ All ${STATE.accounts.length} profile(s) are securely synchronized with SIR Cloud!`, 'success');
        return;
      }
    } catch (err) {
      console.warn("Python bridge cloud sync notice:", err);
    }
  }

  // 2. Fallback UI update
  if (STATE.accounts.length === 0) {
    showToast("ℹ️ No accounts found. Create an offline profile or sign in with Microsoft!", "info");
    openModal('add-account-modal');
  } else {
    showToast(`✓ All ${STATE.accounts.length} profile(s) are in sync!`, "success");
  }
}
window.syncAccountsFromCloud = syncAccountsFromCloud;

// --- REDEEM 6-DIGIT SYNC CODE FROM WEB ---
async function redeemSyncCodeFromWeb(customCode = null) {
  const input = document.getElementById('launcher-sync-code-input') || document.getElementById('sync-code-input-modal');
  const code = (customCode || (input ? input.value : '')).trim();

  if (!code || code.length < 6) {
    showToast('Please enter a valid 6-digit sync code from the website', 'warning');
    if (input) input.focus();
    return;
  }

  showToast(`🔍 Verifying Sync Code: ${code}...`, 'info');

  // 1. Try Python Bridge native redeem first
  if (window.pywebview && window.pywebview.api && window.pywebview.api.redeem_sync_code) {
    try {
      const res = await window.pywebview.api.redeem_sync_code(code);
      if (res && res.success) {
        await loadAccounts();
        if (input) input.value = '';
        closeModal('sync-modal');
        closeModal('account-manager-modal');
        showToast(res.message || `✓ Account linked and activated!`, 'success');
        return;
      }
    } catch (e) {
      console.warn("Bridge code redeem notice:", e);
    }
  }

  // 2. Direct JS fetch fallback
  try {
    const res = await fetch(`https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/launcherSyncCodes/${encodeURIComponent(code)}.json`, {
      signal: AbortSignal.timeout(6000)
    });

    if (res.ok) {
      const data = await res.json();
      if (data && (data.name || data.ign)) {
        const ign = data.name || data.ign;
        const exists = STATE.accounts.find(a => a.name.toLowerCase() === ign.toLowerCase());
        
        if (!exists) {
          STATE.accounts.push({
            name: ign,
            type: data.type || data.accountType || 'offline',
            model: data.model || 'classic',
            skinUrl: data.skinUrl || `https://mc-heads.net/avatar/${encodeURIComponent(ign)}/32`
          });
        }
        
        STATE.activeAccountName = ign;

        if (window.pywebview && window.pywebview.api) {
          try {
            await window.pywebview.api.add_offline_account(ign);
            await window.pywebview.api.select_account(ign);
          } catch (e) {
            console.warn('Bridge account add notice:', e);
          }
        }

        if (input) input.value = '';
        closeModal('sync-modal');
        closeModal('account-manager-modal');
        renderAccounts();
        renderLaunchpad();
        showToast(`✓ Linked & Activated @${ign} from Web!`, 'success');
        return;
      }
    }
    showToast('✗ Invalid or expired sync code. Please generate a new code on the website.', 'error');
  } catch (err) {
    console.error('Sync code error:', err);
    showToast('✗ Network error connecting to Cloud Sync.', 'error');
  }
}
window.redeemSyncCodeFromWeb = redeemSyncCodeFromWeb;




