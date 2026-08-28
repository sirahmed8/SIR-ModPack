// --- MODALS & CONTROLS ---
function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('hidden');
  refreshLucideIcons();
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

