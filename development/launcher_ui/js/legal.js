// --- LEGAL EULA GATEWAY ---
async function openLegalModal(force = false) {
  if (!force) {
    if (localStorage.getItem('sir_legal_accepted') || localStorage.getItem('sir_eula_accepted')) {
      return;
    }
    if (window.pywebview && window.pywebview.api) {
      try {
        const st = await window.pywebview.api.get_legal_status();
        if (st && st.agreed) {
          localStorage.setItem('sir_legal_accepted', '2026.1');
          localStorage.setItem('sir_eula_accepted', '2026.1');
          return;
        }
      } catch {}
    }
  }

  const cb = document.getElementById('legal-agreement-checkbox');
  const btn = document.getElementById('btn-legal-accept');
  if (localStorage.getItem('sir_legal_accepted') || localStorage.getItem('sir_eula_accepted') || force) {
    if (cb) cb.checked = true;
    if (btn) {
      btn.disabled = false;
      btn.style.opacity = '1';
      btn.style.background = '#f59e0b';
      btn.style.color = '#1c1917';
      btn.style.cursor = 'pointer';
    }
  }

  openModal('legal-eula-modal');
  switchLegalDoc('terms');
}
window.openLegalModal = openLegalModal;

function switchLegalDoc(doc) {
  const LEGAL_CONTENT = {
    terms: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider">1. Acceptance of Ecosystem Terms</h4>
        <p>By downloading, installing, launching, or connecting through the SIR ModPack Desktop Suite (including SIR Launcher, SIR Installer, and SIR Server Manager), you agree to be bound by these Terms of Service. SIR ModPack is an independent client and server ecosystem designed for optimal Minecraft performance, shader fidelity, and multiplayer collaboration.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">2. User Responsibility & Mod Integrity</h4>
        <p>All mods, shaders, and resource packs provided in SIR ModPack are curated for stability, safety, and security. You agree not to use the suite for malicious network disruption, unauthorized server exploits, piracy, or commercial resale.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">3. Mod Compatibility & Local Bytecode Processing</h4>
        <p>The SIR Launcher performs automated local-only ASM bytecode compatibility processing on installed mod JAR files to ensure compatibility with Minecraft 26.2's official namespace. This processing occurs entirely on your local machine — zero bytecode, class data, or transformation results are ever transmitted externally.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">4. Disclaimer & Limitation of Liability</h4>
        <p>SIR Launcher is provided on an "AS-IS" and "AS-AVAILABLE" basis without warranties of any kind. The developers shall not be liable for any server penalties, third-party mod conflicts, or hardware instability resulting from extreme overclocks.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">5. Governance & Legal Contact</h4>
        <p>For inquiries, legal notices, or compliance questions, contact the support team at <a href="mailto:a7medorabe7@gmail.com" class="text-amber-300 underline font-mono">a7medorabe7@gmail.com</a>.</p>
      </div>
    `,
    privacy: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider">1. Local-First Zero-Telemetry Architecture</h4>
        <p>SIR Launcher adheres to a strict zero-telemetry, local-first privacy standard. All account tokens, game configurations, offline player profiles, and custom keybindings are stored strictly on your local disk in <code>%APPDATA%\\SIR ModPack</code>.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">2. Authentication & Credentials</h4>
        <p>When authenticating with an Official Microsoft account, your credentials are processed directly through Microsoft's official OAuth 2.0 endpoints. When using optional Google Cloud Sync, authentication runs via a local loopback server directly with Google identity servers. SIR Launcher never sees, logs, or transmits your passwords to third parties.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">3. Cloud Backup & Synchronization</h4>
        <p>If you connect a Google account, your profile preferences, launcher configurations, and server definitions are backed up to Firebase Realtime Database (<code>users/{uid}/cloud_backup.json</code>) with TLS 1.3 encryption, allowing instant 1-click restoration if local files are cleared.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">4. Hardware Diagnostics</h4>
        <p>Hardware diagnostics (CPU thread count, GPU model, and RAM usage) are queried locally via Windows Win32 OS APIs solely to calibrate JVM memory allocation, Generational ZGC, and video presets, and are never uploaded or tracked.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">5. Privacy Contact & Data Rights</h4>
        <p>You retain 100% ownership and deletion rights over your local and cloud data. Contact <a href="mailto:a7medorabe7@gmail.com" class="text-cyan-300 underline font-mono">a7medorabe7@gmail.com</a> for privacy inquiries.</p>
      </div>
    `,
    cookies: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider">1. Local Storage & Preferences</h4>
        <p>SIR Launcher uses HTML5 <code>localStorage</code> and JSON configuration files (<code>launcher_settings.json</code>) strictly to preserve your preferred theme (Dark/Light mode), UI language (Arabic/English), allocated RAM amount, and active instance selection.</p>
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider mt-3">2. Zero Tracking & Third-Party Cookies</h4>
        <p>No tracking cookies, marketing pixels, or third-party analytics are embedded in the desktop applications or offline payloads.</p>
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider mt-3">3. Cache Management</h4>
        <p>Downloaded version manifests, mod icons, and skin previews are cached locally on disk to minimize bandwidth consumption and provide instantaneous offline navigation.</p>
      </div>
    `,
    mojang: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-purple-300 text-xs uppercase tracking-wider">1. Mojang Studios Brand & EULA Compliance</h4>
        <p>SIR Launcher and SIR ModPack are NOT official Minecraft products and are NOT approved by or associated with Mojang Studios or Microsoft Corporation. All Minecraft assets, textures, sounds, and trademarks belong to Mojang Studios and Microsoft Corporation.</p>
        <h4 class="font-bold text-purple-300 text-xs uppercase tracking-wider mt-3">2. Commercial & Account Usage</h4>
        <p>In full compliance with Mojang's Commercial Usage Guidelines and End User License Agreement (<a href="https://minecraft.net/eula" target="_blank" class="text-cyan-400 underline">minecraft.net/eula</a>), SIR ModPack does not monetize game binaries or charge for core game access. Connecting to official multiplayer networks requires a valid Minecraft license.</p>
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

async function submitLegalAcceptance() {
  localStorage.setItem('sir_legal_accepted', '2026.1');
  localStorage.setItem('sir_eula_accepted', '2026.1');
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.accept_legal_terms('2026.1');
    } catch {}
  }
  closeModal('legal-eula-modal');
  showToast('✓ Welcome to SIR Launcher 2026.1!', 'success');
}
window.submitLegalAcceptance = submitLegalAcceptance;

async function declineAndExitLauncher() {
  localStorage.removeItem('sir_legal_accepted');
  localStorage.removeItem('sir_eula_accepted');
  if (window.pywebview && window.pywebview.api) {
    try {
      await window.pywebview.api.close_app();
      return;
    } catch {}
  }
  window.close();
}
window.declineAndExitLauncher = declineAndExitLauncher;


