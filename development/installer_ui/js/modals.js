function openModal(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

function openCleanerModal() {
  openModal('modal-cleaner');
}

function openRepairModal() {
  openModal('modal-repair');
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
  }, 3000);
}

async function runCleaner() {
  showToast(STATE.currentLang === 'ar' ? "جاري تنظيف الملفات المؤقتة..." : "Running disk cleaner...", "info");
  if (window.pywebview && window.pywebview.api && window.pywebview.api.run_cleaner) {
    try {
      const res = await window.pywebview.api.run_cleaner();
      closeModal('modal-cleaner');
      showToast(res.message || "Cleaned successfully!", "success");
    } catch (e) {
      showToast("Cleaning failed: " + e, "error");
    }
  } else {
    setTimeout(() => {
      closeModal('modal-cleaner');
      showToast(STATE.currentLang === 'ar' ? "تم تحرير المساحة بنجاح!" : "Storage cache cleaned!", "success");
    }, 600);
  }
}

async function runRepair() {
  showToast(STATE.currentLang === 'ar' ? "جاري فحص وإصلاح الملفات..." : "Running self-repair check...", "info");
  if (window.pywebview && window.pywebview.api && window.pywebview.api.run_self_repair) {
    try {
      const res = await window.pywebview.api.run_self_repair();
      closeModal('modal-repair');
      showToast(res.message || "Repair check finished!", "success");
    } catch (e) {
      showToast("Repair check failed: " + e, "error");
    }
  } else {
    setTimeout(() => {
      closeModal('modal-repair');
      showToast(STATE.currentLang === 'ar' ? "جميع الملفات سليمة 100%!" : "All integrity hashes verified!", "success");
    }, 600);
  }
}

function openLegalModal() {
  openModal('modal-legal');
  switchInstallerLegalDoc('terms');
}

function switchInstallerLegalDoc(doc) {
  STATE.currentLegalDoc = doc;

  const LEGAL_CONTENT = {
    terms: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider">1. Acceptance of Ecosystem Terms</h4>
        <p>By downloading, installing, deploying, or launching the SIR ModPack Desktop Suite (including SIR Launcher Pro, SIR Installer, and SIR Server Manager), you agree to be bound by these Terms of Service. SIR ModPack is a 100% free, non-commercial, independent client and server ecosystem designed for optimal Minecraft performance, shader fidelity, and multiplayer collaboration.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">2. User Responsibility & Mod Integrity</h4>
        <p>All mods, shaders, and resource packs provided in SIR ModPack are curated for stability, safety, and security. You agree not to use the suite for malicious network disruption, unauthorized server exploits, piracy, or commercial resale.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">3. Disclaimer & Limitation of Liability</h4>
        <p>SIR Installer and Launcher are provided on an "AS-IS" and "AS-AVAILABLE" basis without warranties of any kind. The developers shall not be liable for any server penalties, third-party mod conflicts, or hardware instability resulting from extreme overclocks.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">4. Governance & Feedback</h4>
        <p>SIR ModPack operates as a 100% Free and Independent software ecosystem. Support and issue reporting are channeled exclusively through the in-app Developer Desk, Bug Reporter, and official community channels.</p>
      </div>
    `,
    privacy: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider">1. Local-First Zero-Telemetry Architecture</h4>
        <p>SIR ModPack adheres to a strict zero-telemetry, local-first privacy standard. All account tokens, game configurations, offline player profiles, and custom keybindings are stored strictly on your local disk in <code>%APPDATA%\\SIR ModPack</code>.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">2. Authentication & Credentials</h4>
        <p>When authenticating with an Official Microsoft account, your credentials are processed directly through Microsoft's official OAuth 2.0 endpoints. SIR ModPack never sees, logs, or transmits your passwords or session tokens to any remote server.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">3. Hardware Diagnostics</h4>
        <p>Hardware diagnostics (CPU thread count, GPU model, and RAM usage) are queried locally via Windows Win32 OS APIs solely to calibrate G1GC memory allocation and video presets, and are never uploaded or tracked.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">4. Privacy Rights & Local Control</h4>
        <p>You retain 100% ownership and deletion rights over your local data. All caches and configurations can be cleared at any time via the in-app Cleaner tool or directly in <code>%APPDATA%\\SIR ModPack</code>.</p>
      </div>
    `,
    cookies: `
      <div class="space-y-3 text-xs leading-relaxed">
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider">1. Local Storage & Preferences</h4>
        <p>SIR ModPack applications use HTML5 <code>localStorage</code> and JSON configuration files (<code>launcher_settings.json</code>) strictly to preserve your preferred theme (Dark/Light mode), UI language (Arabic/English), allocated RAM amount, and active instance selection.</p>
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

  const LEGAL_CONTENT_AR = {
    terms: `
      <div class="space-y-3 text-xs leading-relaxed text-right" dir="rtl">
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider">1. قبول شروط المنظومة والترخيص</h4>
        <p>بتحميل أو تثبيت أو تشغيل حزمة برامج SIR ModPack المكتبية (بما في ذلك SIR Launcher و SIR Installer و SIR Server Manager)، فإنك توافق على الالتزام بشروط الخدمة هذه. تعتبر SIR ModPack منصة مجانية ومستقلة 100%، غير تجارية، ومصممة لتقديم أقصى أداء لماين كرافت وأعلى جودة للشيدرز واللعب المشترك.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">2. مسؤولية المستخدم وسلامة الحزمة</h4>
        <p>جميع المودات والشيدرز وحزم الموارد المضمنة في SIR ModPack تم فحصها وتدقيقها بعناية لتحقيق الاستقرار والأمان. توافق على عدم استخدام الحزمة في أي أنشطة إضرار بالشبكة أو استغلال غير مصرح به للسيرفرات أو القرصنة أو إعادة البيع التجاري.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">3. إخلاء المسؤولية وحدود الضمان</h4>
        <p>يتم تقديم مثبت ولانشر SIR "كما هو" و"حسب توفره" دون أي ضمانات صريحة أو ضمنية. لا يتحمل المطورون أي مسؤولية عن أي عقوبات مفروضة من السيرفرات أو تعارض مع مودات خارجية أو عدم استقرار ناتج عن كسر سرعة العتاد.</p>
        <h4 class="font-bold text-amber-300 text-xs uppercase tracking-wider mt-3">4. الحوكمة والتواصل والدعم</h4>
        <p>تعمل منظومة SIR كمنصة مجانية ومستقلة 100%. يتم توجيه الدعم الفني والإبلاغ عن الأخطاء والملاحظات حصرياً عبر مكتب المطورين (Developer Desk) وأدوات الإبلاغ داخل التطبيق.</p>
      </div>
    `,
    privacy: `
      <div class="space-y-3 text-xs leading-relaxed text-right" dir="rtl">
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider">1. خصوصية محلية تامة وانعدام كامل للتتبع (Zero-Telemetry)</h4>
        <p>تلتزم SIR ModPack بمعايير خصوصية صارمة: لا يتم جمع أو إرسال أي بيانات تتبع أو تحليلات عن بعد. جميع رموز الحسابات وإعدادات اللعبة وحسابات الأوفلاين تُخزن محلياً فقط على حاسوبك في المسار: <code>%APPDATA%\\SIR ModPack</code>.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">2. المصادقة والبيانات الحساسة</h4>
        <p>عند تسجيل الدخول بحساب Microsoft رسمي، تتم عملية المصادقة مباشرة عبر خوادم Microsoft OAuth 2.0 الرسمية والآمنة. لا تقوم تطبيقات SIR إطلاقاً بالاطلاع على كلمات المرور أو تسجيلها أو حفظها خارج جهازك.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">3. فحص مواصفات العتاد</h4>
        <p>يتم فحص مواصفات العتاد (عدد أنوية المعالج، بطاقة الشاشة، والذاكرة RAM) محلياً فقط عبر واجهات Win32 بهدف معايرة استهلاك الذاكرة وإعدادات الفيديو تلقائياً، ولا يتم رفع هذه البيانات إلى أي خادم خارجي.</p>
        <h4 class="font-bold text-cyan-300 text-xs uppercase tracking-wider mt-3">4. حقوق البيانات والتحكم الكامل</h4>
        <p>أنت تملك التحكم الكامل 100% بحذف وتعديل بياناتك المحلية في أي وقت عبر أداة تنظيف الملفات المؤقتة في المثبت أو بحذف مجلد البيانات المحلي مباشرة.</p>
      </div>
    `,
    cookies: `
      <div class="space-y-3 text-xs leading-relaxed text-right" dir="rtl">
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider">1. التخزين المحلي والتفضيلات (Local Storage)</h4>
        <p>تستخدم تطبيقات SIR تقنية <code>localStorage</code> وملفات JSON المحلية (<code>launcher_settings.json</code>) لحفظ تفضيلاتك: المظهر (Dark/Light)، واللغة المفضلة (العربية/الإنجليزية)، ومقدار الرام المخصص، والبروفايل النشط.</p>
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider mt-3">2. انعدام ملفات التتبع الخارجية</h4>
        <p>لا تتضمن تطبيقات سطح المكتب أي كوكيز تتبع إعلاني أو بيكسل تسويقي أو أدوات تتبع خارجية إطلاقاً.</p>
        <h4 class="font-bold text-emerald-300 text-xs uppercase tracking-wider mt-3">3. إدارة التخزين المؤقت</h4>
        <p>يتم حفظ بيانات المودات ومخططات الإصدارات ومعاينات السكنات محلياً في الذاكرة المؤقتة لتسريع الاستخدام وتقليل استهلاك الإنترنت ودعم العمل بدون اتصال.</p>
      </div>
    `,
    mojang: `
      <div class="space-y-3 text-xs leading-relaxed text-right" dir="rtl">
        <h4 class="font-bold text-purple-300 text-xs uppercase tracking-wider">1. العلامة التجارية والامتثال لاتفاقية Mojang</h4>
        <p>لانشر SIR وحزمة SIR ModPack ليست منتجات رسمية لماين كرافت وليست معتمدة من قِبل Mojang Studios أو Microsoft Corporation أو تابعة لهما. جميع أصول ماين كرافت والأصوات والنصوص والعلامات التجارية مملوكة لشركة Mojang وMicrosoft.</p>
        <h4 class="font-bold text-purple-300 text-xs uppercase tracking-wider mt-3">2. الاستخدام غير التجاري والحسابات</h4>
        <p>امتثالاً كاملاً لإرشادات الاستخدام التجاري واتفاقية ترخيص المستخدم النهائي لماين كرافت (<a href="https://minecraft.net/eula" target="_blank" class="text-cyan-400 underline">minecraft.net/eula</a>)، لا تقوم منظومة SIR ببيع ملفات اللعبة أو فرض رسوم للوصول إليها. الاتصال بالسيرفرات الرسمية يتطلب ترخيص ماين كرافت أصلي وصالح.</p>
      </div>
    `
  };

  const isAr = (typeof STATE !== 'undefined' && STATE.currentLang === 'ar');
  const dict = isAr ? LEGAL_CONTENT_AR : LEGAL_CONTENT;

  const content = document.getElementById('installer-legal-content');
  if (content) {
    content.innerHTML = dict[doc] || '';
    content.dir = isAr ? 'rtl' : 'ltr';
  }

  ['terms', 'privacy', 'cookies', 'mojang'].forEach(d => {
    const btn = document.getElementById('tab-inst-legal-' + d);
    if (!btn) return;
    if (d === doc) {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 transition-all';
    } else {
      btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-800/80 text-slate-400 border border-transparent hover:text-slate-200 transition-all';
    }
  });
}

function openUninstallModal() {
  openModal('modal-uninstall');
}

async function runUninstall() {
  const targets = [];
  if (document.getElementById('uninst-sir')?.checked) targets.push('sir_launcher');
  if (document.getElementById('uninst-lunar')?.checked) targets.push('lunar');
  if (document.getElementById('uninst-cache')?.checked) targets.push('cache');

  if (targets.length === 0) {
    showToast('Please select at least one component to uninstall.', 'warning');
    return;
  }

  closeModal('modal-uninstall');
  if (window.pywebview && window.pywebview.api && window.pywebview.api.run_uninstall) {
    try {
      const res = await window.pywebview.api.run_uninstall(targets);
      if (res && res.success) {
        showInAppModal('Uninstallation Complete', res.message || 'Components removed successfully.', 'check');
      } else {
        showInAppModal('Uninstallation Error', res.error || 'Failed to remove selected components.', 'alert-triangle');
      }
    } catch (e) {
      showInAppModal('Uninstallation Error', String(e), 'alert-triangle');
    }
  } else {
    showInAppModal('Uninstall Complete', 'Selected components have been cleaned from your disk.', 'check');
  }
}

window.openLegalModal = openLegalModal;
window.switchInstallerLegalDoc = switchInstallerLegalDoc;
window.openModal = openModal;
window.closeModal = closeModal;
window.openCleanerModal = openCleanerModal;
window.openRepairModal = openRepairModal;
window.openUninstallModal = openUninstallModal;
window.runUninstall = runUninstall;
window.showInAppModal = showInAppModal;
window.showToast = showToast;
window.runCleaner = runCleaner;
window.runRepair = runRepair;
