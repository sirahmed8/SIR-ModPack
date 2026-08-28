
// --- 3-STATE UNIVERSAL THEME ENGINE ---
function getSystemTheme() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getEffectiveTheme(mode) {
  if (mode === 'auto') {
    return getSystemTheme();
  }
  return mode === 'light' ? 'light' : 'dark';
}

function applyResolvedTheme(resolvedTheme) {
  STATE.currentTheme = resolvedTheme;
  if (resolvedTheme === 'light') {
    document.documentElement.classList.remove('dark');
    document.documentElement.classList.add('light');
    document.body.classList.remove('dark');
    document.body.classList.add('light');
  } else {
    document.documentElement.classList.remove('light');
    document.documentElement.classList.add('dark');
    document.body.classList.remove('light');
    document.body.classList.add('dark');
  }
}

function updateThemeSelectorUI(mode) {
  ['dark', 'auto', 'light'].forEach(m => {
    const btn = document.getElementById(`theme-btn-${m}`);
    if (btn) {
      if (m === mode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    }
  });
}

function setThemeMode(mode) {
  STATE.themeMode = mode || 'auto';
  localStorage.setItem('sir_theme_mode', STATE.themeMode);
  updateThemeSelectorUI(STATE.themeMode);
  const resolved = getEffectiveTheme(STATE.themeMode);
  applyResolvedTheme(resolved);
}

function applyTheme(theme) {
  setThemeMode(theme || 'auto');
}

function toggleTheme() {
  const current = STATE.themeMode || 'auto';
  const next = current === 'dark' ? 'light' : current === 'light' ? 'auto' : 'dark';
  setThemeMode(next);
}

if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (STATE.themeMode === 'auto') {
      applyResolvedTheme(e.matches ? 'dark' : 'light');
    }
  });
}

function changeLanguage(lang) {
  STATE.currentLang = lang === 'ar' ? 'ar' : 'en';
  localStorage.setItem('sir_lang', STATE.currentLang);
  document.documentElement.setAttribute('dir', STATE.currentLang === 'ar' ? 'rtl' : 'ltr');
  document.documentElement.setAttribute('lang', STATE.currentLang);
  const select = document.getElementById('server-lang-select');
  if (select) select.value = STATE.currentLang;
  applyTranslations();
}

// =============================================================================
// SIR SERVER ORCHESTRATOR PRO — CLIENT CONTROLLER & HARDWARE ENGINE
// =============================================================================

const STATE = {
  currentView: 'dashboard',
  currentLang: 'en',
  currentTheme: 'dark',
  isRunning: false,
  activeVersion: '26.2',
  publicIp: '127.0.0.1:25565',
  customDomain: '127.0.0.1:25565',
  hostMode: 'laptop_host',
  allocatedRam: 6,
  totalPhysicalRam: 24,
  isTunnelRunning: false,
  localWlanIp: '127.0.0.1:25565',
  pollInterval: null
};

const I18N = {
  en: {
    appTitle: "SIR Server Orchestrator",
    appSubtitle: "Dedicated Multi-Threaded Host • PC / Laptop Host & Playit.gg",
    directJoin: "Direct Join in Launcher",
    navDashboard: "Dashboard & Controls",
    navTunnel: "Playit.gg Zero-Port Tunnel",
    navHostMode: "PC / Laptop Host Settings",
    navConsole: "Live Terminal & Logs",
    navPlayers: "Players & Whitelist",
    navProperties: "Server Properties",
    navBackups: "Automated Backups",
    startServer: "START SERVER",
    stopServer: "STOP SERVER",
    serverOnline: "Server Online",
    serverOffline: "Server Offline",
    heroTitle: "Dedicated World Server Station",
    heroDesc: "Host your private or community Minecraft world directly on your PC/Laptop with zero port-forwarding or link your free Playit.gg domain.",
    tpsLabel: "Tick Rate (TPS)",
    playersLabel: "Active Players",
    ramCardTitle: "RAM Allocation",
    uptimeLabel: "Server Uptime",
    sidebarRamTitle: "Allocated RAM",
    playitHeader: "Playit.gg Zero Port-Forwarding Cloud Tunnel",
    playitSub: "Connect players across the world without changing router settings or revealing your private IP."
  },
  ar: {
    appTitle: "مدير خوادم SIR الاحترافي",
    appSubtitle: "محرك الاستضافة المباشر متعدد الأنوية • استضافة الحاسوب / اللابتوب ونفق Playit.gg",
    directJoin: "دخول مباشر عبر اللانشر",
    navDashboard: "لوحة التحكم الرئيسية",
    navTunnel: "الربط السحابي Playit.gg",
    navHostMode: "إعدادات استضافة اللابتوب / PC",
    navConsole: "الشاشة الحية والأوامر",
    navPlayers: "إدارة اللاعبين والتصاريح",
    navProperties: "إعدادات السيرفر",
    navBackups: "النسخ الاحتياطي التلقائي",
    startServer: "تشغيل السيرفر",
    stopServer: "إيقاف السيرفر",
    serverOnline: "السيرفر متصل ويعمل",
    serverOffline: "السيرفر متوقف",
    heroTitle: "محطة تشغيل واستضافة الخادم المحلي",
    heroDesc: "استضف عالم ماين كرافت الخاص بك مباشرة من جهازك أو لابتوبك بدون فتح بورتات في الراوتر مع دعم كامل لخدمة Playit.gg.",
    tpsLabel: "معدل التكات (TPS)",
    playersLabel: "اللاعبين المتصلين",
    ramCardTitle: "تخصيص الرام والذاكرة",
    uptimeLabel: "مدة تشغيل السيرفر",
    sidebarRamTitle: "الرام المخصص",
    playitHeader: "الربط السحابي ونفق Playit.gg بدون بورتات",
    playitSub: "شارك سيرفرك مع أصدقائك في أي مكان بالعالم بدون كشف الآي بي الحقيقي وبدون تعديل إعدادات الراوتر."
  }
};

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-white text-xs font-bold shadow-2xl flex items-center gap-2 pointer-events-auto transition-all";
  toast.innerHTML = `
    <i data-lucide="${type === 'success' ? 'check-circle' : 'info'}" class="w-4 h-4 text-cyan-400"></i>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  if (window.lucide) lucide.createIcons();

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(20px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// --- THEME TOGGLE (LIGHT / DARK) ---
function toggleTheme() {
  const html = document.documentElement;
  const body = document.body;
  const isDark = html.classList.contains('dark');
  
  if (isDark) {
    html.classList.remove('dark');
    html.classList.add('light');
    body.classList.remove('dark');
    body.classList.add('light');
    STATE.currentTheme = 'light';
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    if (sunIcon) sunIcon.classList.remove('hidden');
    if (moonIcon) moonIcon.classList.add('hidden');
  } else {
    html.classList.remove('light');
    html.classList.add('dark');
    body.classList.remove('light');
    body.classList.add('dark');
    STATE.currentTheme = 'dark';
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');
    if (sunIcon) sunIcon.classList.add('hidden');
    if (moonIcon) moonIcon.classList.remove('hidden');
  }
}

// --- VIEW NAVIGATION ---
function switchView(viewId) {
  STATE.currentView = viewId;

  document.querySelectorAll('.view-panel').forEach(el => el.classList.remove('active'));
  const target = document.getElementById(`view-${viewId}`);
  if (target) target.classList.add('active');

  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const navBtn = document.getElementById(`nav-${viewId}`);
  if (navBtn) navBtn.classList.add('active');

  if (viewId === 'properties') loadProperties();
  if (viewId === 'backups') loadBackups();
  if (viewId === 'console') fetchLatestLogs();
  if (window.lucide) lucide.createIcons();
}

// --- SERVER LIFECYCLE & POLLING ---
async function toggleServerPower() {
  if (STATE.isRunning) {
    if (window.pywebview && window.pywebview.api) {
      await window.pywebview.api.stop_server();
      showToast("Server stopping gracefully...", "info");
    }
  } else {
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.start_server(STATE.activeVersion);
      if (res.success) {
        showToast(`Server launched on port 25565!`, "success");
      } else {
        showToast(`Launch failed: ${res.error}`, "error");
      }
    }
  }
}

async function restartServerInstance() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.restart_server();
    showToast("Server rebooting...", "info");
  }
}

function selectServerVersion(ver) {
  STATE.activeVersion = ver;
  const btn26 = document.getElementById('btn-ver-26');
  const btn18 = document.getElementById('btn-ver-18');
  const badge = document.getElementById('dashboard-version-badge');

  if (ver === '26.2') {
    btn26.className = "px-4 py-1.5 rounded-xl text-xs font-bold bg-cyan-500 text-slate-950 shadow-md";
    btn18.className = "px-4 py-1.5 rounded-xl text-xs font-bold btn-secondary";
    if (badge) badge.innerText = "Fabric 1.21.4 (Modern 26.2)";
  } else {
    btn18.className = "px-4 py-1.5 rounded-xl text-xs font-bold bg-cyan-500 text-slate-950 shadow-md";
    btn26.className = "px-4 py-1.5 rounded-xl text-xs font-bold btn-secondary";
    if (badge) badge.innerText = "Paper 1.8.9 (Legacy PvP)";
  }
}

// --- REALTIME TELEMETRY & HARDWARE REFRESH ---
async function pollServerStatus() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const status = await window.pywebview.api.get_server_status();
      STATE.isRunning = status.is_running;
      STATE.allocatedRam = status.allocated_ram_gb || 6;
      STATE.totalPhysicalRam = status.total_ram_gb || 24;
      STATE.publicIp = status.public_ip || "127.0.0.1:25565";
      STATE.customDomain = status.custom_domain || "127.0.0.1:25565";
      STATE.localWlanIp = status.local_wlan_ip || "127.0.0.1:25565";
      STATE.isTunnelRunning = status.is_tunnel_running || false;

      // Update Power Button & Header Status
      const pwrBtn = document.getElementById('btn-master-power');
      const pwrText = document.getElementById('btn-master-power-text');
      const topDot = document.getElementById('top-status-dot');
      const topText = document.getElementById('top-status-text');
      const topUptime = document.getElementById('top-uptime-ticker');
      const topIpLabel = document.getElementById('top-public-ip-label');
      const wlanBadge = document.getElementById('wlan-active-ip-badge');

      if (topIpLabel) topIpLabel.innerText = STATE.publicIp;
      if (wlanBadge) wlanBadge.innerText = `${STATE.localWlanIp}`;

      if (status.is_running) {
        if (pwrBtn) pwrBtn.className = "px-8 py-4 rounded-2xl bg-rose-500 hover:bg-rose-400 text-white text-base font-black shadow-xl shadow-rose-500/25 flex items-center gap-3 active:scale-95 transition-all";
        if (pwrText) pwrText.innerText = I18N[STATE.currentLang].stopServer;
        if (topDot) topDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 pulse-emerald";
        if (topText) topText.innerText = I18N[STATE.currentLang].serverOnline;
        if (topUptime) topUptime.innerText = status.uptime;
      } else {
        if (pwrBtn) pwrBtn.className = "px-8 py-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-base font-black shadow-xl shadow-emerald-500/25 flex items-center gap-3 active:scale-95 transition-all";
        if (pwrText) pwrText.innerText = I18N[STATE.currentLang].startServer;
        if (topDot) topDot.className = "w-2.5 h-2.5 rounded-full bg-rose-500 pulse-rose";
        if (topText) topText.innerText = I18N[STATE.currentLang].serverOffline;
        if (topUptime) topUptime.innerText = "00:00:00";
      }

      // Update Telemetry Metrics (REAL LIVE PROCESS VALUES)
      const tpsEl = document.getElementById('gauge-tps');
      if (tpsEl) tpsEl.innerText = status.tps.toFixed(1);

      const tpsHint = document.getElementById('gauge-tps-hint');
      if (tpsHint) tpsHint.innerText = status.is_running ? "Running smoothly at 20.0 TPS" : "Server offline";

      const playersEl = document.getElementById('gauge-players');
      if (playersEl) playersEl.innerText = status.players_count;

      const uptimeEl = document.getElementById('gauge-uptime');
      if (uptimeEl) uptimeEl.innerText = status.uptime;

      // RAM Allocation & Used Gauges (REAL ACCURATE VALUES)
      const ramUsedEl = document.getElementById('gauge-ram-used');
      const ramAllocEl = document.getElementById('gauge-ram-allocated');
      const ramTotalHint = document.getElementById('gauge-ram-total-hint');
      
      if (ramUsedEl) ramUsedEl.innerText = status.is_running ? status.used_ram_gb.toFixed(1) : "0.0";
      if (ramAllocEl) ramAllocEl.innerText = `/ ${STATE.allocatedRam}.0 GB`;
      if (ramTotalHint) ramTotalHint.innerText = `Total Physical: ${STATE.totalPhysicalRam} GB RAM`;

      // Sidebar Footer Card
      const sidebarRamLabel = document.getElementById('sidebar-ram-label');
      const sidebarRamBar = document.getElementById('sidebar-ram-bar');
      const sidebarHwCpu = document.getElementById('sidebar-hw-cpu');

      if (sidebarRamLabel) sidebarRamLabel.innerText = `${STATE.allocatedRam} GB / ${STATE.totalPhysicalRam} GB`;
      if (sidebarRamBar) {
        const pct = Math.min(100, Math.round((STATE.allocatedRam / STATE.totalPhysicalRam) * 100));
        sidebarRamBar.style.width = `${pct}%`;
      }
      if (sidebarHwCpu && status.cpu_name) {
        sidebarHwCpu.innerText = `${status.cpu_name.split('@')[0].trim()} (${status.cpu_cores} Cores)`;
      }

      // Host Tab Tuning
      const hostRamVal = document.getElementById('host-ram-val-badge');
      const hostRamSlider = document.getElementById('host-ram-slider');
      const hostRamMax = document.getElementById('host-ram-max-hint');
      if (hostRamVal) hostRamVal.innerText = `${STATE.allocatedRam} GB`;
      if (hostRamMax) hostRamMax.innerText = `${STATE.totalPhysicalRam} GB Total Physical RAM`;
      if (hostRamSlider && !hostRamSlider.matches(':active')) {
        hostRamSlider.max = STATE.totalPhysicalRam;
        hostRamSlider.value = STATE.allocatedRam;
      }

      // Playit input domain
      const playitInput = document.getElementById('input-playit-domain');
      if (playitInput && !playitInput.matches(':focus') && STATE.customDomain) {
        if (!playitInput.value) playitInput.value = STATE.customDomain;
      }

      // Update Player List Grid
      renderPlayersList(status.players);

    } catch (e) {
      console.warn("Poll failed:", e);
    }
  }
}

function formatLogLine(line) {
  if (!line || typeof line !== 'string') return '';
  let escaped = line.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  escaped = escaped.replace(/^(\[\d{2}:\d{2}:\d{2}\])/, '<span class="text-slate-500 font-mono select-none">$1</span>');
  
  if (escaped.includes('[Server thread/INFO]') || escaped.includes('/INFO]')) {
    escaped = escaped.replace(/\[([^\]]*\/INFO)\]/, '<span class="text-emerald-500 dark:text-emerald-400 font-semibold font-mono">[$1]</span>');
  } else if (escaped.includes('/WARN]') || escaped.includes('/WARNING]')) {
    escaped = escaped.replace(/\[([^\]]*(?:WARN|WARNING))\]/, '<span class="text-amber-500 font-bold font-mono">[$1]</span>');
  } else if (escaped.includes('/ERROR]') || escaped.includes('/FATAL]')) {
    escaped = escaped.replace(/\[([^\]]*(?:ERROR|FATAL))\]/, '<span class="text-rose-500 font-bold font-mono">[$1]</span>');
  } else if (escaped.includes('Terminal/COMMAND')) {
    escaped = escaped.replace(/\[Terminal\/COMMAND\]/, '<span class="text-cyan-500 font-bold font-mono">[COMMAND]</span>');
  }

  escaped = escaped.replace(/(joined the game|left the game|logged in with entity)/g, '<span class="text-cyan-500 dark:text-cyan-400 font-semibold">$1</span>');
  return escaped;
}

async function fetchLatestLogs() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.get_latest_logs(200);
      if (res.success && res.lines) {
        const formatted = res.lines.map(l => `<div class="py-0.5 hover:bg-slate-500/10 rounded px-1">${formatLogLine(l)}</div>`).join('');
        
        const fullStream = document.getElementById('full-logs-stream');
        if (fullStream) {
          fullStream.innerHTML = formatted;
          fullStream.scrollTop = fullStream.scrollHeight;
        }

        const dashStream = document.getElementById('dashboard-logs-stream');
        if (dashStream) {
          dashStream.innerHTML = formatted;
          dashStream.scrollTop = dashStream.scrollHeight;
        }
      }
    } catch (e) {}
  }
}

// --- TERMINAL COMMAND DISPATCH ---
async function sendTerminalCommand() {
  const input = document.getElementById('terminal-cmd-input');
  if (!input || !input.value.trim()) return;

  const cmd = input.value.trim();
  input.value = '';

  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.send_command(cmd);
    fetchLatestLogs();
  }
}

function clearConsoleLog() {
  const full = document.getElementById('full-logs-stream');
  if (full) full.innerHTML = '<div class="text-muted italic p-4">Console cleared.</div>';
}

// --- PLAYERS MANAGER ---
function renderPlayersList(players) {
  const grid = document.getElementById('players-list-grid');
  if (!grid) return;

  if (!players || players.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full feature-card p-8 text-center space-y-2">
        <i data-lucide="users" class="w-8 h-8 text-muted mx-auto"></i>
        <h4 class="text-sm font-bold text-title">No Players Currently Connected</h4>
        <p class="text-xs text-muted">Join via 127.0.0.1:25565 or your Playit.gg address to see live player heads and management actions.</p>
      </div>
    `;
    if (window.lucide) lucide.createIcons();
    return;
  }

  grid.innerHTML = players.map(p => `
    <div class="feature-card p-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <img src="https://mc-heads.net/avatar/${p}/48" class="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 shadow-md">
        <div>
          <h4 class="text-sm font-extrabold text-title">${p}</h4>
          <span class="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold font-mono">● Online</span>
        </div>
      </div>
      <div class="flex items-center gap-1.5">
        <button onclick="sendQuickCommand('op ${p}')" class="p-2 rounded-xl btn-secondary text-amber-500" title="Grant OP"><i data-lucide="shield" class="w-3.5 h-3.5"></i></button>
        <button onclick="sendQuickCommand('kick ${p}')" class="p-2 rounded-xl btn-secondary text-rose-500" title="Kick"><i data-lucide="user-x" class="w-3.5 h-3.5"></i></button>
      </div>
    </div>
  `).join('');
  if (window.lucide) lucide.createIcons();
}

function sendQuickCommand(cmd) {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.send_command(cmd);
    fetchLatestLogs();
  }
}

// --- PLAYIT.GG ACTIONS ---
async function openPlayitWebsite() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.open_playit_portal();
  }
}

async function openPlayitTunnelsDashboard() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.open_playit_tunnels();
  }
}

async function openServerGuideSite() {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.open_server_guide_site();
  }
}

async function savePlayitCustomDomain() {
  const input = document.getElementById('input-playit-domain');
  if (!input || !input.value.trim()) return;

  const domain = input.value.trim();
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.save_custom_domain(domain);
    if (res.success) {
      showToast(`Saved active Playit domain: ${domain}`, "success");
      pollServerStatus();
    }
  }
}

async function togglePlayitLocalTunnel() {
  if (window.pywebview && window.pywebview.api) {
    if (STATE.isTunnelRunning) {
      await window.pywebview.api.stop_playit_tunnel();
      showToast("Playit tunnel stopped.", "info");
    } else {
      const res = await window.pywebview.api.start_playit_tunnel();
      showToast(res.message, "success");
    }
    pollServerStatus();
  }
}

function copyPublicIp() {
  navigator.clipboard.writeText(STATE.publicIp);
  showToast(`Copied ${STATE.publicIp} to clipboard!`, "success");
}

function launchWithLauncher() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.launch_minecraft_client_join(STATE.publicIp);
  }
}

// --- HOST MODE & RAM SLIDER ---
async function onHostRamSliderChange(val) {
  STATE.allocatedRam = parseInt(val);
  const badge = document.getElementById('host-ram-val-badge');
  if (badge) badge.innerText = `${val} GB`;

  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.save_settings(JSON.stringify({ allocated_ram_gb: STATE.allocatedRam }));
  }
}

async function selectHostMode(mode) {
  STATE.hostMode = mode;
  const btnSir = document.getElementById('mode-btn-sir');
  const btnPlayit = document.getElementById('mode-btn-playit');
  const btnBoth = document.getElementById('mode-btn-both');
  const hostBadge = document.getElementById('dashboard-hostmode-badge');

  [btnSir, btnPlayit, btnBoth].forEach(b => {
    if (b) b.className = "px-3 py-2 rounded-xl text-xs font-bold border flex items-center justify-center gap-1.5 transition-all btn-secondary text-body";
  });

  if (mode === 'sir_host' && btnSir) {
    btnSir.className = "px-3 py-2 rounded-xl text-xs font-bold border flex items-center justify-center gap-1.5 transition-all bg-emerald-500/15 border-emerald-500/50 text-emerald-600 dark:text-emerald-400 shadow-sm";
    if (hostBadge) hostBadge.innerText = "⚡ SIR HOST (WLAN) ACTIVE";
  } else if (mode === 'playit_tunnel' && btnPlayit) {
    btnPlayit.className = "px-3 py-2 rounded-xl text-xs font-bold border flex items-center justify-center gap-1.5 transition-all bg-cyan-500/15 border-cyan-500/50 text-cyan-600 dark:text-cyan-400 shadow-sm";
    if (hostBadge) hostBadge.innerText = "🌐 PLAYIT.GG TUNNEL ACTIVE";
  } else if (mode === 'both' && btnBoth) {
    btnBoth.className = "px-3 py-2 rounded-xl text-xs font-bold border flex items-center justify-center gap-1.5 transition-all bg-amber-500/15 border-amber-500/50 text-amber-600 dark:text-amber-400 shadow-sm";
    if (hostBadge) hostBadge.innerText = "⚡ DUAL HOST (BOTH) ACTIVE";
  }

  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.save_settings(JSON.stringify({ host_mode: mode }));
  }
}

function copyWlanIp() {
  const ip = STATE.localWlanIp || STATE.publicIp;
  navigator.clipboard.writeText(ip);
  showToast(`Copied WLAN IP: ${ip}`, "success");
}

async function downloadServerCore() {
  const btn = document.getElementById('btn-download-core');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Downloading Core...</span>`;
    if (window.lucide) lucide.createIcons();
  }

  if (window.pywebview && window.pywebview.api) {
    showToast("Downloading Fabric 1.21.4 server core...", "info");
    const res = await window.pywebview.api.download_server_core(STATE.activeVersion);
    if (res.success) {
      showToast("Dedicated server core installed successfully!", "success");
    } else {
      showToast(`Download failed: ${res.error}`, "info");
    }
  }

  if (btn) {
    btn.disabled = false;
    btn.innerHTML = `<i data-lucide="download" class="w-3.5 h-3.5"></i><span>Download Dedicated Server Core</span>`;
    if (window.lucide) lucide.createIcons();
  }
  fetchLatestLogs();
}

// --- SLIDERS (VIEW DISTANCE & MAX PLAYERS 100x BETTER) ---
function onViewDistanceChange(val) {
  const chunks = parseInt(val);
  const valEl = document.getElementById('val-prop-view-dist');
  const hintEl = document.getElementById('hint-prop-view-dist');

  if (valEl) valEl.innerText = `${chunks} Chunks`;
  if (hintEl) {
    if (chunks <= 8) {
      hintEl.innerText = `⚡ Fast Performance (${chunks} Chunks - Low CPU)`;
      hintEl.className = "text-[10px] text-emerald-400 font-mono";
    } else if (chunks <= 14) {
      hintEl.innerText = `✨ Balanced (${chunks} Chunks - Recommended)`;
      hintEl.className = "text-[10px] text-cyan-400 font-mono";
    } else if (chunks <= 22) {
      hintEl.innerText = `🌟 High Render Radius (${chunks} Chunks)`;
      hintEl.className = "text-[10px] text-purple-400 font-mono";
    } else {
      hintEl.innerText = `🚀 Ultra Extreme Radius (${chunks} Chunks - High RAM)`;
      hintEl.className = "text-[10px] text-amber-400 font-mono";
    }
  }
}

function onMaxPlayersChange(val) {
  const count = parseInt(val);
  const valEl = document.getElementById('val-prop-max-players');
  const hintEl = document.getElementById('hint-prop-max-players');

  if (valEl) valEl.innerText = `${count} Players`;
  if (hintEl) {
    if (count <= 4) {
      hintEl.innerText = `👥 Duo & Small Co-op (${count} Max Players)`;
      hintEl.className = "text-[10px] text-cyan-400 font-mono";
    } else if (count <= 10) {
      hintEl.innerText = `⚔️ Party Squad & Friends SMP (${count} Max Players)`;
      hintEl.className = "text-[10px] text-emerald-400 font-mono";
    } else if (count <= 30) {
      hintEl.innerText = `🏰 Standard SMP Server (${count} Max Players)`;
      hintEl.className = "text-[10px] text-purple-400 font-mono";
    } else {
      hintEl.innerText = `🌐 Mega Multiplayer Network (${count} Max Players)`;
      hintEl.className = "text-[10px] text-amber-400 font-mono";
    }
  }
}

// --- PROPERTIES STUDIO ---
async function loadProperties() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const props = await window.pywebview.api.get_server_properties(STATE.activeVersion);
      if (props.motd) {
        let motdStr = props.motd;
        try {
          if (motdStr.includes('\\u00a7')) {
            motdStr = motdStr.replace(/\\u00a7([0-9a-fk-or])/gi, '§$1');
          }
        } catch {}
        document.getElementById('prop-motd').value = motdStr;
      }
      if (props.difficulty) {
        const diffLabels = { peaceful: 'Peaceful', easy: 'Easy', normal: 'Normal', hard: 'Hard' };
        selectDropdownOption('prop-difficulty', props.difficulty, diffLabels[props.difficulty] || props.difficulty);
      }
      if (props.gamemode) {
        const gmLabels = { survival: 'Survival', creative: 'Creative', adventure: 'Adventure', spectator: 'Spectator' };
        selectDropdownOption('prop-gamemode', props.gamemode, gmLabels[props.gamemode] || props.gamemode);
      }
      if (props['online-mode'] !== undefined) {
        const val = String(props['online-mode']);
        const label = val === 'true' ? 'Official Microsoft Accounts Only' : 'Cracked & Offline Allowed (Recommended)';
        selectDropdownOption('prop-online-mode', val, label);
      }
      if (props['view-distance']) {
        document.getElementById('prop-view-distance').value = props['view-distance'];
        onViewDistanceChange(props['view-distance']);
      }
      if (props['max-players']) {
        document.getElementById('prop-max-players').value = props['max-players'];
        onMaxPlayersChange(props['max-players']);
      }
    } catch (e) {}
  }
}

async function saveProperties() {
  const dict = {
    motd: document.getElementById('prop-motd').value,
    difficulty: document.getElementById('prop-difficulty').value,
    gamemode: document.getElementById('prop-gamemode').value,
    'online-mode': document.getElementById('prop-online-mode').value === 'true',
    'view-distance': document.getElementById('prop-view-distance').value,
    'max-players': document.getElementById('prop-max-players').value
  };

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.save_server_properties(dict, STATE.activeVersion);
    if (res.success) showToast("Properties saved successfully!", "success");
  }
}

// --- BACKUPS ---
async function loadBackups() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const items = await window.pywebview.api.get_backups();
      const container = document.getElementById('backups-list-container');
      if (!container) return;

      if (!items || items.length === 0) {
        container.innerHTML = `
          <div class="feature-card p-8 text-center space-y-2">
            <i data-lucide="archive" class="w-8 h-8 text-muted mx-auto"></i>
            <h4 class="text-sm font-bold text-title">No Backups Yet</h4>
            <p class="text-xs text-muted">Click 'Create Snapshot Now' to compress and archive your world data.</p>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
      }

      container.innerHTML = items.map(b => `
        <div class="feature-card p-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="p-2.5 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
              <i data-lucide="file-archive" class="w-5 h-5"></i>
            </div>
            <div>
              <h4 class="text-xs font-mono font-bold text-title">${b.filename}</h4>
              <p class="text-[10px] text-muted">${b.date} • ${b.size_mb} MB Compressed Archive</p>
            </div>
          </div>
          <button onclick="openBackupsFolder()" class="px-3 py-1.5 rounded-xl btn-secondary text-xs font-bold">
            Show in Folder
          </button>
        </div>
      `).join('');
      if (window.lucide) lucide.createIcons();
    } catch (e) {}
  }
}

async function triggerNewBackup() {
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.create_backup(STATE.activeVersion);
    if (res.success) {
      showToast(`Snapshot created: ${res.filename} (${res.size_mb} MB)`, "success");
      loadBackups();
    }
  }
}

async function openBackupsFolder() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.open_folder("server_backups");
  }
}

// --- LANGUAGE TOGGLE ---
function toggleLanguage() {
  STATE.currentLang = STATE.currentLang === 'en' ? 'ar' : 'en';
  document.documentElement.dir = STATE.currentLang === 'ar' ? 'rtl' : 'ltr';
  const ind = document.getElementById('lang-indicator');
  if (ind) ind.innerText = STATE.currentLang === 'ar' ? 'English' : 'عربي';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (I18N[STATE.currentLang] && I18N[STATE.currentLang][key]) {
      el.innerText = I18N[STATE.currentLang][key];
    }
  });
}

function changeLanguage(lang) {
  STATE.currentLang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  const ind = document.getElementById('lang-indicator');
  if (ind) ind.innerText = lang === 'ar' ? 'English' : 'عربي';

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (I18N[lang] && I18N[lang][key]) {
      el.innerText = I18N[lang][key];
    }
  });
}

// --- CUSTOM CYBERSELECT DROPDOWN HANDLERS ---
function toggleDropdown(id) {
  const menu = document.getElementById(`menu-${id}`);
  const trigger = document.querySelector(`#dropdown-${id} .custom-dropdown-trigger`);
  if (!menu) return;
  const isOpen = menu.classList.contains('active');
  
  // Close all other open menus
  document.querySelectorAll('.custom-dropdown-menu.active').forEach(m => {
    if (m !== menu) m.classList.remove('active');
  });
  document.querySelectorAll('.custom-dropdown-trigger.open').forEach(t => {
    if (t !== trigger) t.classList.remove('open');
  });

  if (isOpen) {
    menu.classList.remove('active');
    if (trigger) trigger.classList.remove('open');
  } else {
    menu.classList.add('active');
    if (trigger) trigger.classList.add('open');
  }
}

function selectDropdownOption(id, value, label) {
  const hiddenInput = document.getElementById(id);
  const labelEl = document.getElementById(`label-${id}`);
  const menu = document.getElementById(`menu-${id}`);
  const trigger = document.querySelector(`#dropdown-${id} .custom-dropdown-trigger`);

  if (hiddenInput) {
    hiddenInput.value = value;
    hiddenInput.dispatchEvent(new Event('change'));
  }
  if (labelEl) labelEl.innerText = label;

  if (menu) {
    menu.querySelectorAll('.custom-dropdown-option').forEach(opt => {
      opt.classList.remove('selected');
      const check = opt.querySelector('i[data-lucide="check"]');
      if (check) check.remove();
      if (opt.innerText.trim().startsWith(label.trim())) {
        opt.classList.add('selected');
        const icon = document.createElement('i');
        icon.setAttribute('data-lucide', 'check');
        icon.className = 'w-3.5 h-3.5 text-cyan-400';
        opt.appendChild(icon);
      }
    });
    menu.classList.remove('active');
  }
  if (trigger) trigger.classList.remove('open');
  if (window.lucide) lucide.createIcons();
}

// Global click-outside closer for custom dropdowns
document.addEventListener('click', (e) => {
  if (!e.target.closest('.custom-dropdown-container')) {
    document.querySelectorAll('.custom-dropdown-menu.active').forEach(m => m.classList.remove('active'));
    document.querySelectorAll('.custom-dropdown-trigger.open').forEach(t => t.classList.remove('open'));
  }
});

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();
  
  // Start 1s telemetry poller
  pollServerStatus();
  fetchLatestLogs();
  setInterval(pollServerStatus, 1000);
  setInterval(fetchLatestLogs, 1500);
});
