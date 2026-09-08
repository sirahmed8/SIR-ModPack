// =============================================================================
//   SIR LAUNCHER 2026.1 — HIGH-PERFORMANCE PRESENTATION CONTROLLER
// =============================================================================

const STATE = {
  activeTab: 'launchpad',
  currentLang: 'en',
  currentTheme: 'dark',
  themeMode: 'dark',
  accounts: [],
  activeAccount: null,
  activeAccountName: 'No account',
  instances: [
    { id: '26.2-ultra', name: 'SIR 26 Visuals', version: '26.2', loader: 'Fabric', mods_count: 225, ram_gb: 8, category: 'modern', active: true },
    { id: '26.2-balanced', name: 'SIR 26 Balanced', version: '26.2', loader: 'Fabric', mods_count: 225, ram_gb: 6, category: 'modern', active: false },
    { id: '26.2-performance', name: 'SIR 26 Performance', version: '26.2', loader: 'Fabric', mods_count: 220, ram_gb: 4, category: 'modern', active: false },
    { id: '1.8.9-ultra', name: 'SIR 1.8.9 Visuals', version: '1.8.9', loader: 'Forge', mods_count: 27, ram_gb: 4, category: 'legacy', active: false },
    { id: '1.8.9-balanced', name: 'SIR 1.8.9 Balanced', version: '1.8.9', loader: 'Forge', mods_count: 27, ram_gb: 4, category: 'legacy', active: false },
    { id: '1.8.9-performance', name: 'SIR 1.8.9 Performance', version: '1.8.9', loader: 'Forge', mods_count: 27, ram_gb: 3, category: 'legacy', active: false }
  ],
  selectedInstanceId: '26.2-ultra',
  userStatus: 'Online',
  ramGb: 8,
  powerGovernor: 'turbo',
  servers: [],
  serverFilter: 'All',
  serverSortOrder: 'ping',
  mods: [],
  modCategory: 'All',
  modSearchQuery: '',
  modsSubTab: 'installed',
  storeSearchQuery: '',
  storeProvider: 'modrinth',
  storeType: 'mods',
  storeSort: 'downloads',
  screenshots: [],
  isLaunching: false
};

const I18N = {
  en: {
    onlineBadge: "Live • SIR Ecosystem",
    cloudSync: "Cloud Sync",
    satellite: "Satellite",
    welcome: "Welcome Back,",
    launchBtn: "LAUNCH GAME",
    launchingBtn: "LAUNCHING SIR ENGINE...",
    editSuite: "Edit Suite",
    quickPresets: "Quick Presets:",
    switchAccount: "SWITCH ACCOUNT",
    addAccount: "Add Offline Profile"
  },
  ar: {
    onlineBadge: "مباشر • نظام SIR الموحد",
    cloudSync: "المزامنة السحابية",
    satellite: "الأقمار الصناعية",
    welcome: "مرحباً بعودتك،",
    launchBtn: "تشغيل اللعبة",
    launchingBtn: "جاري تشغيل محرك SIR...",
    editSuite: "تعديل الحزمة",
    quickPresets: "الإعدادات السريعة:",
    switchAccount: "تبديل الحساب",
    addAccount: "إضافة حساب أوفلاين"
  }
};



function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

// Synchronous Instant Cache Hydration: guarantees accounts render with 0ms delay on startup
try {
  if (window.__SIR_BOOTSTRAP__ && Array.isArray(window.__SIR_BOOTSTRAP__.accounts) && window.__SIR_BOOTSTRAP__.accounts.length > 0) {
    STATE.accounts = window.__SIR_BOOTSTRAP__.accounts.map(a => ({
      name: a.displayName || a.name || a.username || 'SirPlayer',
      type: a.accountType || a.type || 'offline',
      skinUrl: a.skinUrl || `https://mc-heads.net/avatar/${encodeURIComponent(a.displayName || a.name || 'Steve')}/32`
    }));
    STATE.activeAccountName = window.__SIR_BOOTSTRAP__.active || STATE.accounts[0].name;
    STATE.activeAccount = STATE.accounts.find(a => a.name === STATE.activeAccountName) || STATE.accounts[0];
  } else {
    const _cachedAccs = localStorage.getItem('sir_cached_accounts');
    const _cachedAct = localStorage.getItem('sir_active_account');
    if (_cachedAccs) {
      const _parsed = JSON.parse(_cachedAccs);
      if (Array.isArray(_parsed) && _parsed.length > 0) {
        STATE.accounts = _parsed;
        STATE.activeAccountName = _cachedAct || _parsed[0].name || _parsed[0].displayName || 'SirPlayer';
        STATE.activeAccount = _parsed.find(a => a.name === STATE.activeAccountName) || _parsed[0];
      }
    }
  }
} catch (e) {
  console.warn("Account cache pre-hydration notice:", e);
}

