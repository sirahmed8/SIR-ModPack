
// --- 3-STATE UNIVERSAL THEME ENGINE ---
function getSystemTheme() {
  return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getEffectiveTheme(mode) {
  if (mode === 'auto') return getSystemTheme();
  return mode === 'light' ? 'light' : 'dark';
}

function applyResolvedTheme(resolvedTheme) {
  STATE.currentTheme = resolvedTheme;
  const html = document.documentElement;
  const body = document.body;
  const sunIcon = document.getElementById('theme-icon-sun');
  const moonIcon = document.getElementById('theme-icon-moon');

  if (resolvedTheme === 'light') {
    html.classList.remove('dark');
    html.classList.add('light');
    body.classList.remove('dark');
    body.classList.add('light');
    if (sunIcon) sunIcon.classList.remove('hidden');
    if (moonIcon) moonIcon.classList.add('hidden');
  } else {
    html.classList.remove('light');
    html.classList.add('dark');
    body.classList.remove('light');
    body.classList.add('dark');
    if (sunIcon) sunIcon.classList.add('hidden');
    if (moonIcon) moonIcon.classList.remove('hidden');
  }
}

function setThemeMode(mode) {
  STATE.themeMode = mode || 'dark';
  localStorage.setItem('sir_theme_mode', STATE.themeMode);
  applyResolvedTheme(getEffectiveTheme(STATE.themeMode));
}

function toggleTheme() {
  const current = STATE.currentTheme || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  setThemeMode(next);
}

if (window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (STATE.themeMode === 'auto') {
      applyResolvedTheme(e.matches ? 'dark' : 'light');
    }
  });
}

window.toggleTheme = toggleTheme;
window.setThemeMode = setThemeMode;

