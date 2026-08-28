const I18N = {
  en: {
    appTitle: "SIR ModPack Installer",
    appSubtitle: "Precision Hardware Deployment Engine • Fabric 26.2 & Forge 1.8.9",
    cleaner: "Cleaner",
    repair: "Self-Repair",
    step1: "1. Welcome & Rig",
    step2: "2. Target & Path",
    step3: "3. Performance & Matrix",
    step4: "4. Deploy & Launch",
    hwDetectedBadge: "REAL HARDWARE DETECTED",
    hwDetailsPrefix: "Detected:",
    eulaTitle: "SIR Ecosystem — Terms of Service & EULA Agreement",
    agreeCheck: "I accept the SIR ModPack Terms of Service and EULA (100% Free & Open-Source)",
    targetHeader: "Select Installation Target Platform",
    targetDesc: "Choose how and where to deploy the SIR ModPack ecosystem on your computer.",
    destFolderLabel: "Installation Folder Destination",
    btnBrowse: "Browse...",
    configHeader: "Personalized Tuning & Component Selection",
    configDesc: "Configure dedicated RAM memory allocation and select which packages to include.",
    ramLabel: "Dedicated Memory Allocation (RAM):",
    governorLabel: "Hardware Power Governor (Decompression Threading)",
    govTurbo: "⚡ Turbo Mode (Max Speed)",
    govSmooth: "🍃 Smooth Mode (Zero Lag)",
    componentsLabel: "Selected Installation Components",
    btnBack: "Previous Step",
    nextStep: "Next Step",
    installNow: "🚀 Start Full Installation",
    launchApp: "LAUNCH SIR LAUNCHER",
    openFolder: "Open Folder",
    installSuccessTitle: "🎉 100% SUCCESS: All Components Deployed!",
    installSuccessDesc: "SIR Launcher and all 240+ mods, shaders, and configs have been successfully installed."
  },
  ar: {
    appTitle: "مثبت منظومة SIR الاحترافي",
    appSubtitle: "محرك التثبيت الذكي المتوافق مع عتاد جهازك • فابريك 26.2 وفورج 1.8.9",
    cleaner: "تنظيف الملفات",
    repair: "الفحص والإصلاح",
    step1: "1. فحص العتاد والاتفاقية",
    step2: "2. مسار ومنصة التثبيت",
    step3: "3. التخصيص والأداء",
    step4: "4. التثبيت والتشغيل",
    hwDetectedBadge: "تم فحص عتاد جهازك الفعلي",
    hwDetailsPrefix: "المواصفات الفعلية:",
    eulaTitle: "اتفاقية الاستخدام والشروط الرسمية لمنظومة SIR",
    agreeCheck: "أوافق على شروط الخدمة واتفاقية الترخيص (مجاني 100% وبدون أي جمع بيانات)",
    targetHeader: "اختر منصة التثبيت المستهدفة",
    targetDesc: "حدد طريقة ومسار تثبيت حزمة ماين كرافت وموداتها على حاسوبك.",
    destFolderLabel: "مجلد مسار التثبيت النهائي",
    btnBrowse: "استعراض...",
    configHeader: "التخصيص الذكي وحزم التثبيت",
    configDesc: "اضبط تخصيص الرام (RAM) المناسب واختر الحزم والبروفايلات التي ترغب بتثبيتها.",
    ramLabel: "تخصيص الذاكرة العشوائية (RAM):",
    governorLabel: "منظم استهلاك أنوية المعالج (سرعة فك الضغط)",
    govTurbo: "⚡ الوضع التوربو (أقصى سرعة)",
    govSmooth: "🍃 الوضع السلس (يمنع أي لاغ)",
    componentsLabel: "حزم ومكونات التثبيت المختارة",
    btnBack: "الخطوة السابقة",
    nextStep: "الخطوة التالية",
    installNow: "🚀 بدء التثبيت الشامل متعدد الأنوية",
    launchApp: "تشغيل لانشر SIR الآن",
    openFolder: "فتح مجلد التثبيت",
    installSuccessTitle: "🎉 اكتمل التثبيت بنجاح تام 100%!",
    installSuccessDesc: "تم نشر لانشر SIR وكافة الـ 240+ مود والشيدرز والبروفايلات بدون أي أخطاء."
  }
};

// --- THEME TOGGLE (LIGHT / DARK) ---
function toggleTheme() {
  const html = document.documentElement;
  const body = document.body;
  const isDark = html.classList.contains('dark');
  
  if (isDark) {
    html.classList.remove('dark');
    html.classList.add('light');
    body.classList.remove('dark');
