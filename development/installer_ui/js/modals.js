function openCleanerModal() {
  document.getElementById('modal-cleaner').classList.remove('hidden');
}

function showInAppModal(title, body, iconType = 'info') {
  const modal = document.getElementById('modal-notification');
  const titleEl = document.getElementById('modal-notif-title-text');
  const bodyEl = document.getElementById('modal-notif-body');
  const iconEl = document.getElementById('modal-notif-icon');
  
  if (titleEl) titleEl.innerText = title;
  if (bodyEl) {
    if (typeof body === 'string' && body.includes('\n')) {
      bodyEl.innerHTML = body.replace(/\n/g, '<br>');
    } else {
      bodyEl.innerText = body;
    }
  }
  if (iconEl) {
    iconEl.setAttribute('data-lucide', iconType);
    if (window.lucide) lucide.createIcons();
  }
  if (modal) modal.classList.remove('hidden');
}

function showToast(msg, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = 'px-4 py-3 rounded-xl bg-slate-900/90 border border-slate-700/80 text-xs font-bold text-slate-100 shadow-2xl backdrop-blur-xl flex items-center gap-2.5 transition-all duration-300 transform translate-y-2 opacity-0';
  const iconName = type === 'success' ? 'check-circle' : (type === 'error' ? 'alert-triangle' : 'info');
  const colorClass = type === 'success' ? 'text-emerald-400' : (type === 'error' ? 'text-rose-400' : 'text-cyan-400');
  toast.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4 ${colorClass}"></i><span>${msg}</span>`;
  container.appendChild(toast);
  if (window.lucide) lucide.createIcons();

  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('translate-y-2', 'opacity-0');
    setTimeout(() => toast.remove(), 300);
