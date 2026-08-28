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
    { id: 'sir-26-ultra', name: 'SIR 26 (Ultra Visuals)', version: '26.2', loader: 'Fabric', mods_count: 242, ram_gb: 8, active: true },
    { id: 'sir-26-balanced', name: 'SIR 26 (Balanced 144+ FPS)', version: '26.2', loader: 'Fabric', mods_count: 242, ram_gb: 6, active: false },
    { id: 'sir-26-comp', name: 'SIR 26 (Competitive Speed)', version: '26.2', loader: 'Fabric', mods_count: 242, ram_gb: 4, active: false },
    { id: 'sir-legacy-pvp', name: 'SIR Legacy 1.8.9 (Hypixel PvP)', version: '1.8.9', loader: 'Forge', mods_count: 48, ram_gb: 3, active: false }
  ],
  selectedInstanceId: 'sir-26-ultra',
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

