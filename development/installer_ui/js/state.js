// =============================================================================
// SIR INSTALLER STUDIO PRO — CLIENT CONTROLLER & WIZARD ENGINE
// =============================================================================

const STATE = {
  currentStage: 1,
  currentLang: 'en',
  currentTheme: 'dark',
  eulaAgreed: false,
  targetType: 'sir_launcher',
  powerGovernor: 'turbo',
  customPath: '',
  defaultPaths: {
    sir_launcher: '',
    vanilla: '',
    lunar: ''
  },
  allocatedRam: 8,
  isInstalling: false,
  pollInterval: null,
  specsFetched: false
};

