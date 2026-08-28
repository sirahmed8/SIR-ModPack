// --- LEGAL EULA GATEWAY ---
function openLegalModal() {
  openModal('legal-eula-modal');
  switchLegalDoc('terms');
}

function switchLegalDoc(doc) {
  const LEGAL_CONTENT = {
    terms: `
      <div class="space-y-2">
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider">1. Acceptance of Ecosystem Terms</h4>
        <p>By downloading, installing, or launching SIR Launcher, you agree to be bound by these Terms of Service. SIR Launcher is a free, non-commercial, open-architecture client ecosystem designed for optimal Minecraft performance, shader fidelity, and multiplayer collaboration.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">2. User Responsibility & Mod Integrity</h4>
        <p>All mods, shaders, and resource packs provided in SIR ModPack are curated for stability and security. You agree not to use the launcher for malicious network disruption, unauthorized server exploits, or commercial resale.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">3. Disclaimer & Limitation of Liability</h4>
        <p>SIR Launcher is provided on an "AS-IS" and "AS-AVAILABLE" basis without warranties of any kind. The developers shall not be liable for any server penalties, third-party mod conflicts, or hardware instability resulting from extreme overclocks.</p>
      </div>
    `,
    privacy: `
      <div class="space-y-2">
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider">1. Local-First Privacy Architecture</h4>
        <p>SIR Launcher adheres to a strict zero-telemetry, local-first privacy standard. All account tokens, game configurations, offline player profiles, and custom keybindings are stored strictly on your local disk in <code>%APPDATA%\\SIR ModPack</code>.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">2. Authentication & Credentials</h4>
        <p>When authenticating with an Official Microsoft account, your credentials are processed directly through Microsoft's official OAuth 2.0 endpoints. SIR Launcher never sees, logs, or transmits your passwords to any remote server.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">3. Hardware Telemetry</h4>
        <p>Hardware diagnostics (CPU thread count, GPU model, and RAM usage) are queried locally via Windows Win32 OS APIs to calibrate G1GC memory allocation and are never uploaded or tracked.</p>
      </div>
    `,
    cookies: `
      <div class="space-y-2">
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider">1. Local Storage & Preferences</h4>
        <p>SIR Launcher uses HTML5 <code>localStorage</code> and JSON configuration files (<code>launcher_settings.json</code>) to preserve your preferred theme (Dark/Light mode), UI language (Arabic/English), allocated RAM amount, and active instance selection.</p>
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider mt-3">2. Temporary Cache Management</h4>
        <p>Downloaded version manifests, mod icons, and skin previews are cached locally in memory and disk to minimize bandwidth consumption and provide instantaneous offline navigation.</p>
      </div>
    `,
    mojang: `
      <div class="space-y-2">
        <h4 class="font-bold text-purple-300 text-xs uppercase tracking-wider">1. Minecraft Brand & EULA Compliance</h4>
        <p>SIR Launcher is NOT an official Minecraft product and is NOT approved by or associated with Mojang Studios or Microsoft Corporation. All Minecraft assets, trademarks, and copyright belong to Mojang Studios.</p>
        <h4 class="font-bold text-purple-300 text-xs uppercase tracking-wider mt-3">2. Commercial & Account Usage</h4>
        <p>In full compliance with Mojang's Commercial Usage Guidelines and End User License Agreement (<a href="https://minecraft.net/eula" target="_blank" class="text-cyan-400 underline">minecraft.net/eula</a>), SIR Launcher does not monetize game JARs or charge for core game access. Official multiplayer networks require a valid Minecraft license.</p>
      </div>
    `
  };
  const content = document.getElementById('legal-doc-content');
  if (content) content.innerHTML = LEGAL_CONTENT[doc] || '';

  ['terms', 'privacy', 'cookies', 'mojang'].forEach(d => {
    const btn = document.getElementById('tab-legal-' + d);
    if (!btn) return;
    if (d === doc) {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 transition-all';
    } else {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-800/80 text-slate-400 border border-transparent hover:text-slate-200 transition-all';
    }
  });
}

function toggleLegalAgreeBtn() {
  const checkbox = document.getElementById('legal-agreement-checkbox');
  const btn = document.getElementById('btn-legal-accept');
  if (!btn) return;
  if (checkbox && checkbox.checked) {
    btn.disabled = false;
    btn.className = btn.className.replace('opacity-50 cursor-not-allowed', '').trim() + ' cursor-pointer';
    btn.style.opacity = '1';
    btn.style.background = '#f59e0b';
    btn.style.color = '#1c1917';
  } else {
    btn.disabled = true;
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
    btn.style.background = '';
  }
}

function submitLegalAcceptance() {
  localStorage.setItem('sir_legal_accepted', '2026.1');
  if (window.pywebview && window.pywebview.api) {
    try {
      window.pywebview.api.accept_legal_terms('2026.1');
    } catch {}
  }
  closeModal('legal-eula-modal');
  showToast('✓ Welcome to SIR Launcher 2026.1!', 'success');
}

async function declineAndExitLauncher() {
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.close_app();
      return;
    } catch {}
  }
  window.close();
}


