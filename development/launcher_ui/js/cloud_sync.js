/**
 * cloud_sync.js — Google Cloud Authentication & Firebase Persistence UI Integration.
 */

window.CLOUD_STATE = {
  authenticated: false,
  email: '',
  displayName: '',
  photoURL: '',
  lastSync: 0
};

// Frame-0 Pre-Hydration
try {
  const cachedSession = window.__SIR_CLOUD_BOOTSTRAP__ || JSON.parse(localStorage.getItem('sir_cloud_session') || 'null');
  if (cachedSession && cachedSession.authenticated) {
    window.CLOUD_STATE = { ...window.CLOUD_STATE, ...cachedSession };
  }
} catch(e) {}

window.onCloudAuthSuccess = function(profile) {
  if (!profile) return;
  updateCloudState(profile);
  try {
    localStorage.setItem('sir_cloud_session', JSON.stringify(profile));
  } catch(e) {}
  if (window.STATE) {
    window.STATE.cloudUser = profile;
  }
  if (typeof renderGoogleCloudAccountCard === 'function') renderGoogleCloudAccountCard();
  if (typeof renderAccountMenuGoogleCard === 'function') renderAccountMenuGoogleCard();
  if (typeof loadAccounts === 'function') loadAccounts();
  if (typeof renderAccounts === 'function') renderAccounts();
  if (typeof renderLaunchpad === 'function') renderLaunchpad();
  if (profile.authenticated) {
    const name = profile.displayName || profile.email || 'User';
    if (typeof showToast === 'function') {
      showToast(`✓ Connected as ${name}! Synchronized across SIR ecosystem.`, 'success');
    }
  }
};

window.fetchLatestCloudStatus = async function() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const getFn = window.pywebview.api.get_cloud_status || window.pywebview.api.cloud_get_status;
      if (typeof getFn === 'function') {
        const status = await getFn();
        if (status) {
          const changed = status.authenticated !== window.CLOUD_STATE.authenticated || status.email !== window.CLOUD_STATE.email;
          updateCloudState(status);
          if (changed) {
            if (window.STATE) {
              window.STATE.cloudUser = status;
            }
            if (typeof loadAccounts === 'function') {
              await loadAccounts();
            }
            if (typeof renderLaunchpad === 'function') {
              renderLaunchpad();
            }
          }
        }
      }
    } catch (e) {
      console.warn('[CloudSync] Failed to fetch status:', e);
    }
  }
};

window.addEventListener('pywebviewready', () => {
  if (typeof window.fetchLatestCloudStatus === 'function') {
    window.fetchLatestCloudStatus();
  }
});

async function initCloudSyncUI() {
  if (typeof window.fetchLatestCloudStatus === 'function') {
    await window.fetchLatestCloudStatus();
  }

  // Directive 26: Cross-App Google Cloud Session Sync on window focus and visibility change
  window.addEventListener('focus', () => {
    if (typeof window.fetchLatestCloudStatus === 'function') window.fetchLatestCloudStatus();
  });
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && typeof window.fetchLatestCloudStatus === 'function') {
      window.fetchLatestCloudStatus();
    }
  });

  // Listen for real-time auth change events from backend
  window.addEventListener('sir_cloud_auth_changed', async (evt) => {
    if (evt.detail) {
      updateCloudState(evt.detail);
      if (window.STATE) {
        window.STATE.cloudUser = evt.detail;
      }
      if (typeof loadAccounts === 'function') {
        await loadAccounts();
      }
      if (typeof renderLaunchpad === 'function') {
        renderLaunchpad();
      }
      if (evt.detail.authenticated) {
        const name = evt.detail.displayName || evt.detail.email || 'User';
        if (typeof showToast === 'function') {
          showToast(`✓ Connected as ${name}! Synchronized across SIR ecosystem.`, 'success');
        }
      }
    }
  });
}

function updateCloudState(profile) {
  window.CLOUD_STATE = {
    ...window.CLOUD_STATE,
    ...profile
  };

  const isAuth = !!window.CLOUD_STATE.authenticated;
  
  // Update all Google sign-in buttons & banners across launcher UI
  document.querySelectorAll('.google-login-btn').forEach(btn => {
    if (isAuth) {
      btn.innerHTML = `
        <div class="flex items-center gap-2">
          ${window.CLOUD_STATE.photoURL ? `<img src="${window.CLOUD_STATE.photoURL}" class="w-4 h-4 rounded-full border border-cyan-400" />` : `<div class="w-4 h-4 rounded-full bg-cyan-400 flex items-center justify-center text-slate-950 text-[10px] font-bold">G</div>`}
          <span class="truncate max-w-[140px] text-xs font-semibold text-cyan-300">${window.CLOUD_STATE.displayName || window.CLOUD_STATE.email}</span>
        </div>
      `;
      btn.title = `Connected to Google (${window.CLOUD_STATE.email})`;
      btn.classList.add('border-cyan-500/40', 'bg-cyan-500/10');
    } else {
      btn.innerHTML = `
        <svg class="w-4 h-4 text-white" viewBox="0 0 24 24">
          <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
          <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
        </svg>
        <span class="text-xs font-semibold text-white">Sign in with Google</span>
      `;
      btn.title = "Sign in with Google to enable Cloud Sync";
      btn.classList.remove('border-cyan-500/40', 'bg-cyan-500/10');
    }
  });

  // Update cloud sync badge in status bar
  const cloudBadge = document.getElementById('cloud-sync-status-badge');
  if (cloudBadge) {
    if (isAuth) {
      cloudBadge.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-[10px] font-mono text-emerald-300">CLOUD SYNC ACTIVE</span>
      `;
    } else {
      cloudBadge.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-slate-500"></span>
        <span class="text-[10px] font-mono text-slate-400">LOCAL MODE</span>
      `;
    }
  }

  renderGoogleCloudAccountCard();
  renderAccountMenuGoogleCard();
}

function renderGoogleCloudAccountCard() {
  const card = document.getElementById('google-cloud-account-card');
  if (!card) return;

  const isAuth = !!window.CLOUD_STATE.authenticated;
  if (isAuth) {
    const avatar = window.CLOUD_STATE.photoURL 
      ? `<img src="${window.CLOUD_STATE.photoURL}" class="w-10 h-10 rounded-full border-2 border-cyan-400 shadow-md shadow-cyan-500/20 object-cover" />`
      : `<div class="w-10 h-10 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center text-cyan-300 font-bold text-base">G</div>`;
    const name = escapeHtml(window.CLOUD_STATE.displayName || 'Google Account');
    const email = escapeHtml(window.CLOUD_STATE.email || '');

    card.innerHTML = `
      <div class="p-4 rounded-2xl bg-[#09101d] border border-cyan-500/40 shadow-lg shadow-cyan-500/10 space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-3">
          <div class="flex items-center gap-3">
            ${avatar}
            <div>
              <div class="flex items-center gap-2">
                <span class="text-sm font-black text-white">${name}</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>Firebase Cloud Connected</span>
                </span>
              </div>
              <p class="text-xs text-slate-400 font-mono mt-0.5">${email}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="triggerCloudBackup()" class="px-3.5 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 font-bold text-xs border border-cyan-500/40 flex items-center gap-1.5 transition-all cursor-pointer active:scale-95 shadow-sm">
              <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i>
              <span>Sync Now</span>
            </button>
            <button onclick="triggerGoogleLogin()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-rose-500/20 hover:text-rose-300 text-slate-400 font-bold text-xs border border-slate-700 transition-all cursor-pointer active:scale-95">
              <span>Disconnect / Switch</span>
            </button>
          </div>
        </div>
      </div>
    `;
  } else {
    card.innerHTML = `
      <div class="p-4 rounded-2xl bg-[#09101d] border border-cyan-500/30 shadow-lg shadow-cyan-500/5 space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center shrink-0 shadow-md">
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
              </svg>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-black text-white">Google Cloud Identity &amp; Sync</span>
                <span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-slate-800 text-slate-400 border border-slate-700">Offline / Disconnected</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-0.5">Connect your Google account to automatically sync Minecraft profiles, IAS alts, and settings.</p>
            </div>
          </div>
          <button onclick="triggerGoogleLogin()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20 active:scale-95 cursor-pointer">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            <span>Sign in with Google</span>
          </button>
        </div>
      </div>
    `;
  }
  if (typeof refreshLucideIcons === 'function') {
    refreshLucideIcons();
  }
}

function renderAccountMenuGoogleCard() {
  const card = document.getElementById('account-menu-google-card');
  if (!card) return;

  const isAuth = !!window.CLOUD_STATE.authenticated;
  if (isAuth) {
    const avatar = window.CLOUD_STATE.photoURL 
      ? `<img src="${window.CLOUD_STATE.photoURL}" class="w-8 h-8 rounded-full border border-cyan-400 shadow-sm object-cover shrink-0" />`
      : `<div class="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center text-cyan-300 font-bold text-xs shrink-0">G</div>`;
    const name = escapeHtml(window.CLOUD_STATE.displayName || 'Google Account');
    const email = escapeHtml(window.CLOUD_STATE.email || '');

    card.innerHTML = `
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2 min-w-0">
          ${avatar}
          <div class="min-w-0">
            <span class="text-xs font-bold text-slate-100 block truncate">${name}</span>
            <div class="flex items-center gap-1.5 mt-0.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0"></span>
              <span class="text-[9px] font-mono text-emerald-400 font-bold">Cloud Connected</span>
            </div>
          </div>
        </div>
        <button onclick="triggerGoogleLogin()" class="px-2 py-1 rounded-lg bg-slate-800 hover:bg-rose-500/20 hover:text-rose-300 text-slate-400 text-[10px] font-bold border border-slate-700 transition-all cursor-pointer shrink-0" title="${email}">
          Disconnect
        </button>
      </div>
    `;
  } else {
    card.innerHTML = `
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 shrink-0">
            <svg class="w-4 h-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
          </div>
          <div class="min-w-0">
            <span class="text-xs font-bold text-slate-200 block truncate">Google Cloud</span>
            <span class="text-[10px] text-slate-500 font-mono block">Sync Across Devices</span>
          </div>
        </div>
        <button onclick="event.stopPropagation(); triggerGoogleLogin();" class="px-2.5 py-1 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-[11px] font-black transition-all cursor-pointer shadow-sm active:scale-95 shrink-0">
          Connect
        </button>
      </div>
    `;
  }
}

function openDisconnectConfirmModal() {
  const modal = document.getElementById('disconnect-confirm-modal');
  const emailEl = document.getElementById('disconnect-modal-email');
  if (emailEl && window.CLOUD_STATE) {
    emailEl.textContent = window.CLOUD_STATE.email || 'user@gmail.com';
  }
  if (modal) {
    modal.classList.remove('hidden');
    if (typeof refreshLucideIcons === 'function') refreshLucideIcons();
  }
}
window.openDisconnectConfirmModal = openDisconnectConfirmModal;

function closeDisconnectConfirmModal() {
  const modal = document.getElementById('disconnect-confirm-modal');
  if (modal) modal.classList.add('hidden');
}
window.closeDisconnectConfirmModal = closeDisconnectConfirmModal;

async function confirmDisconnectGoogle() {
  closeDisconnectConfirmModal();
  if (window.pywebview && window.pywebview.api && window.pywebview.api.logout_google) {
    try {
      await window.pywebview.api.logout_google();
    } catch (e) {
      console.warn('[CloudSync] logout_google error:', e);
    }
  }
  updateCloudState({ authenticated: false, email: '', displayName: '', photoURL: '' });
  try {
    localStorage.removeItem('sir_cloud_session');
  } catch(e) {}
  if (window.STATE) {
    window.STATE.cloudUser = null;
  }
  if (typeof loadAccounts === 'function') await loadAccounts();
  if (typeof renderLaunchpad === 'function') renderLaunchpad();
  if (typeof showToast === 'function') {
    showToast('✓ Disconnected from Google Cloud Sync safely.', 'info');
  }
}
window.confirmDisconnectGoogle = confirmDisconnectGoogle;

async function triggerGoogleLogin() {
  if (window.CLOUD_STATE && window.CLOUD_STATE.authenticated) {
    openDisconnectConfirmModal();
    return;
  }

  if (window.pywebview && window.pywebview.api && window.pywebview.api.start_google_login) {
    try {
      if (typeof showToast === 'function') {
        showToast('Opening browser for Google Authentication...', 'info');
      }
      const res = await window.pywebview.api.start_google_login(49152);
      if (!res.success && res.error) {
        if (typeof showToast === 'function') showToast(`Auth error: ${res.error}`, 'error');
      }
    } catch (e) {
      console.error('[CloudSync] Error initiating login:', e);
    }
  } else {
    // Fallback direct browser open
    window.open('https://sir-modpack.web.app/auth/desktop?port=49152', '_blank');
  }
}

async function promptEnterSyncCode() {
  const code = prompt('Enter your 6-digit Sync Code from the SIR Web Portal:');
  if (!code || !code.trim()) return;
  await linkWithSyncCode(code.trim());
}

async function linkWithSyncCode(code) {
  if (typeof showToast === 'function') showToast('Connecting to Cloud Sync Code...', 'info');
  if (window.pywebview && window.pywebview.api && window.pywebview.api.link_sync_code) {
    try {
      const res = await window.pywebview.api.link_sync_code(code);
      if (res && res.success) {
        if (typeof showToast === 'function') showToast('✓ Google Cloud Linked successfully!', 'success');
        updateCloudState(res.profile || { authenticated: true });
        if (typeof autoSyncAccountsSilent === 'function') autoSyncAccountsSilent();
      } else {
        if (typeof showToast === 'function') showToast(res.error || 'Invalid or expired code.', 'error');
      }
    } catch (e) {
      console.error('[CloudSync] Link code error:', e);
      if (typeof showToast === 'function') showToast(`Link error: ${e}`, 'error');
    }
  } else {
    try {
      const resp = await fetch(`https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/launcherSyncCodes/${code}.json`);
      if (resp.ok) {
        const data = await resp.json();
        if (data && data.uid) {
          if (typeof window.onCloudAuthSuccess === 'function') {
            window.onCloudAuthSuccess(data);
          } else {
            updateCloudState({ authenticated: true, ...data });
          }
          if (typeof showToast === 'function') showToast('✓ Linked with Google Cloud!', 'success');
          return;
        }
      }
      if (typeof showToast === 'function') showToast('Code not found or expired.', 'error');
    } catch (err) {
      if (typeof showToast === 'function') showToast('Failed to connect to Firebase RTDB.', 'error');
    }
  }
}
window.promptEnterSyncCode = promptEnterSyncCode;
window.linkWithSyncCode = linkWithSyncCode;

async function triggerCloudBackup() {
  if (!window.CLOUD_STATE.authenticated) {
    triggerGoogleLogin();
    return;
  }
  if (window.pywebview && window.pywebview.api && window.pywebview.api.backup_to_cloud) {
    try {
      if (typeof showToast === 'function') showToast('Backing up data to Firebase Cloud...', 'info');
      const res = await window.pywebview.api.backup_to_cloud();
      if (res.success) {
        if (typeof showToast === 'function') showToast('Cloud backup completed successfully!', 'success');
      } else {
        if (typeof showToast === 'function') showToast(`Backup failed: ${res.error}`, 'error');
      }
    } catch (e) {
      console.error('[CloudSync] Backup error:', e);
    }
  }
}

async function triggerCloudRestore() {
  if (!window.CLOUD_STATE.authenticated) {
    triggerGoogleLogin();
    return;
  }
  if (window.pywebview && window.pywebview.api && window.pywebview.api.restore_from_cloud) {
    try {
      if (typeof showToast === 'function') showToast('Restoring accounts and settings from cloud...', 'info');
      const res = await window.pywebview.api.restore_from_cloud();
      if (res.success) {
        if (typeof showToast === 'function') showToast('Restored from cloud! Reloading accounts...', 'success');
        if (typeof loadAccounts === 'function') await loadAccounts();
        if (typeof renderLaunchpad === 'function') renderLaunchpad();
      } else {
        if (typeof showToast === 'function') showToast(res.message || res.error || 'Restore failed', 'warning');
      }
    } catch (e) {
      console.error('[CloudSync] Restore error:', e);
    }
  }
}

window.initCloudSyncUI = initCloudSyncUI;
window.triggerGoogleLogin = triggerGoogleLogin;
window.triggerCloudBackup = triggerCloudBackup;
window.triggerCloudRestore = triggerCloudRestore;
window.renderAccountMenuGoogleCard = renderAccountMenuGoogleCard;
window.renderGoogleCloudAccountCard = renderGoogleCloudAccountCard;
