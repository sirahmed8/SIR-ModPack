// --- THEME ENGINE ---
function getSystemTheme() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getEffectiveTheme(mode) {
  if (mode === 'auto') return getSystemTheme();
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
  applyResolvedTheme(getEffectiveTheme(STATE.themeMode));
}

