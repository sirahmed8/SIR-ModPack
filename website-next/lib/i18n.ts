export type Language = "en" | "ar";

export const translations = {
  en: {
    // Navigation
    nav: {
      brand: "SIR ECOSYSTEM",
      versionBadge: "v1.0.0",
      features: "Features",
      profiles: "Profiles",
      downloads: "Downloads",
      serverHosting: "Cloud Servers",
      havoc: "HAVOC PvP",
      account: "Link Account",
      changelog: "Changelog",
      admin: "Admin",
      signIn: "Sign In with Google",
      signOut: "Sign Out",
      guestMode: "Guest Mode",
      themeDark: "Dark Mode",
      themeLight: "Light Mode",
      switchLang: "العربية"
    },
    // Welcome Screen
    welcome: {
      tag: "NEXT-GEN MINECRAFT PLATFORM",
      title: "Elevate Your Minecraft Experience to Extreme Fidelity",
      subtitle: "Unifying Modern 26.2 (Fabric) & Legacy 1.8.9 (Forge) with ray-traced shaders, 3D PBR POM textures, hardware power governor, and zero-lag performance.",
      googleCta: "Sign In with Google & Sync",
      guestCta: "Explore as Guest",
      features: {
        f1: "⚡ 1-Click Adaptive Installer",
        f2: "🎨 2048 Volumetric SIR Shaders",
        f3: "🛡️ IAS Cracked & Microsoft Alt Switcher",
        f4: "🚀 144+ to 1000+ FPS Engine"
      }
    },
    // Hero & Downloads
    hero: {
      badge: "OFFICIAL RELEASE v1.0.0",
      headline: "The Ultimate Minecraft Ecosystem",
      subheadline: "Engineered for maximum FPS, ultra visual realism, and seamless cross-version account switching. Download in one click.",
      downloadInstallerTitle: "Download SIR Apps Suite",
      downloadInstallerSub: "Standalone SIR Launcher, SIR Server Manager & SIR Installer (Native 64-bit Windows)",
      downloadBundleTitle: "Download Full Offline Bundle",
      downloadBundleSub: "Full Standalone • Complete pre-extracted instances, master shaders, & 3D POM packs",
      downloadsCount: "Downloads & Active Players",
      requirements: "Native Windows 10/11 (64-bit) • Java 8 & Java 21 Included • macOS & Linux Coming Soon",
      powerGovernorNotice: "Includes Hardware Power Governor: Switch between Max Speed & Smooth/Eco Mode"
    },
    // Profiles Matrix
    profiles: {
      title: "Adaptive Engine Profiles",
      subtitle: "Tailored runtime instances pre-configured for every playstyle, from cinematic 4K raytracing to competitive 1000+ FPS PvP.",
      tabModern: "Modern 26.2 (Fabric)",
      tabLegacy: "Legacy 1.8.9 (Forge)",
      modernTag: "Fabric Architecture • Iris + Sodium • 3D PBR POM Textures",
      legacyTag: "Forge Architecture • Hypixel PvP • In-Game Account Switcher (IAS)",
      modernExtreme: {
        title: "Modern 26.2 Ultra Extreme",
        desc: "Master SIR Shader 2048 Shader Engine with Solas crystal transparent water, circular glowing sun, HD Lunar moon phases, 3D POM relief, and Distant Horizons depth fix.",
        fps: "90 - 180+ FPS",
        specs: "RTX 3060 / RX 6600 or higher"
      },
      modernBalanced: {
        title: "Modern 26.2 Balanced FPS",
        desc: "Optimized SIR Balanced Shader with identical clear water & circular sun, combined with Lithium, FerriteCore, ImmediatelyFast, and C2ME chunk speed.",
        fps: "144 - 280+ FPS",
        specs: "GTX 1650 / RX 580 or higher"
      },
      legacyPvp: {
        title: "Legacy 1.8.9 Competitive PvP",
        desc: "OptiFine Ultra + Patcher + Essential + IAS. Clean motion blur, 1.7 fluid animations, instant keystrokes, and ultra low frame latency tailored for Hypixel & BedWars.",
        fps: "500 - 1000+ FPS",
        specs: "Any GPU / 1000+ FPS"
      }
    },
    // Account Linking Hub
    accountHub: {
      title: "Minecraft Account Hub",
      subtitle: "Connect your official Microsoft Gamertag or custom Offline / Cracked username with real-time 3D skin rendering.",
      officialTab: "Official Microsoft",
      crackedTab: "Cracked / Offline",
      inputLabel: "Minecraft Username / Gamertag",
      inputPlaceholder: "e.g. Notch, Ahmed_PvP, Alex",
      saveBtn: "Link & Sync Avatar",
      statusLinked: "Account Linked Successfully",
      skinPreviewTitle: "3D Skin Visualizer",
      iasInfoTitle: "InGameAccountSwitcher (IAS) Active",
      iasInfoDesc: "You can switch between unlimited offline and official accounts right inside the Minecraft main menu without restarting the game."
    },
    // Multiplayer & Server Hosting Suite
    serverHosting: {
      badge: "MULTIPLAYER & HOSTING",
      title: "Play With Friends: In-Game World Host & Dedicated Server Studio",
      subtitle: "Two effortless ways to play with your friends on cracked or official accounts — with zero port-forwarding and zero lag.",
      ramSliderLabel: "Dedicated Memory Allocation",
      cpuLabel: "Dedicated vCPU Cores",
      slotsLabel: "Player Capacity",
      inGameTitle: "🎮 In-Game 1-Click World Host",
      inGameDesc: "Host your singleplayer world publicly in 2 seconds. Pause the game, click Open to LAN, and share your instant join link with friends!",
      serverAppTitle: "⚡ SIR Server Host Studio App",
      serverAppDesc: "Optional 1-click standalone server manager included in the SIR Installer. Run dedicated 20+ player Fabric & Purpur servers with Aikar's performance flags.",
      installerFeatureNotice: "The SIR Installer allows you to optionally install the Server Host Studio alongside the launcher with one click.",
      soonBadge: "COMING SOON",
      proTierTitle: "SIR Enterprise Cloud Node",
      proTierDesc: "Ultra-low ping NVMe cloud nodes with pre-installed SIR server-side optimizations, auto-backups, and Cloudflare Tunnel integration.",
      notifyBtn: "Join Priority Waitlist"
    },
    // HAVOC PvP Injector Portal
    havoc: {
      badge: "PROJECT SPOTLIGHT",
      soonBadge: "COMING SOON",
      title: "HAVOC PvP Enhancement Engine",
      subtitle: "Next-generation combat injector engineered for competitive Minecraft PvP dominance.",
      feature1: "⚡ Micro-Latency Hit-Registration Optimization",
      feature2: "🎯 Adaptive Reach & Velocity Physics Stabilizer",
      feature3: "🛡️ Undetected Lightweight Injection Framework",
      feature4: "📊 Live Combat Analytics & CPS Display",
      actionBtn: "Explore HAVOC Portal (Soon)",
      authorNote: "Proprietary Combat Enhancement Engine"
    },
    // AI Chatbot
    ai: {
      widgetTitle: "SIR AI Assistant",
      onlineStatus: "Online • AI Assistant",
      welcomeMsg: "Hello! I am the SIR Ecosystem AI. Ask me anything about installing, shader presets, cracked accounts, or server hosting!",
      inputPlaceholder: "Ask a question about SIR ModPack...",
      sendBtn: "Send",
      thinking: "Computing response...",
      promptSuggestions: [
        "How do I use offline / cracked accounts?",
        "What is the difference between Extreme & Balanced shaders?",
        "How does the Hardware Power Governor work?"
      ]
    },
    // Error Handling & Diagnostics
    errors: {
      modalTitle: "Submit System Diagnostics",
      modalSubtitle: "Encountered an issue? Send a direct telemetry report to the SIR developer team.",
      errorDescLabel: "Describe what happened",
      errorDescPlaceholder: "e.g. Installer crashed during shader extraction, skin preview not loading...",
      submitBtn: "Submit Telemetry Report",
      submitting: "Transmitting...",
      successTitle: "Report Transmitted!",
      successDesc: "Your diagnostics report was securely logged to Firestore. Reference ID: ",
      closeBtn: "Close",
      notFoundTitle: "404 - Dimension Not Found",
      notFoundSubtitle: "The cyber coordinates you requested do not exist in the SIR Ecosystem.",
      returnHomeBtn: "Return to Nexus",
      reportErrorBtn: "Report this Issue"
    },
    // Admin Dashboard
    admin: {
      title: "Owner Analytics & Telemetry Nexus",
      subtitle: "Real-time metrics, active download pipelines, error streams, and cloud infrastructure health.",
      stats: {
        activePlayers: "Active Players",
        totalDownloads: "Installer Downloads",
        bundleDownloads: "Offline Bundle (1.1 GB)",
        errorCount: "Error Reports Logged"
      },
      systemHealth: "Cloud Node Status: 100% OPERATIONAL",
      recentErrorsTitle: "Live Firestore Error Stream",
      noErrors: "No critical errors reported in the last 24 hours. Systems running flawlessly.",
      clearBtn: "Refresh Telemetry"
    },
    // Footer & Trust
    footer: {
      tagline: "The premier high-performance Minecraft ecosystem. Built with passion for gamers worldwide.",
      devLink: "Developer Linktree",
      privacy: "Privacy Policy",
      terms: "Terms of Service",
      cookies: "Cookie Policy",
      copyright: "© 2026 SIR ModPack. All rights reserved.",
      trustBadges: "100% Secure • Private • Encrypted • Mojang Commercial Compliant"
    }
  },
  ar: {
    // Navigation
    nav: {
      brand: "منظومة سير | SIR",
      versionBadge: "الإصدار v1.0.0",
      features: "المميزات",
      profiles: "البروفايلات",
      downloads: "التحميل",
      serverHosting: "سيرفرات سحابية",
      havoc: "مشروع HAVOC",
      account: "ربط الحساب",
      changelog: "سجل التحديثات",
      admin: "لوحة التحكم",
      signIn: "تسجيل الدخول عبر Google",
      signOut: "تسجيل الخروج",
      guestMode: "تصفح كزائر",
      themeDark: "الوضع الليلي",
      themeLight: "الوضع النهاري",
      switchLang: "English"
    },
    // Welcome Screen
    welcome: {
      tag: "منصة ماينكرافت فائقة التطور",
      title: "ارتقِ بتجربة ماينكرافت إلى أقصى درجات الواقعية والسرعة",
      subtitle: "توحيد إصدارات Modern 26.2 (Fabric) و Legacy 1.8.9 (Forge) مع شيدرز تتبع الأشعة، وتكستشر PBR ثلاثي الأبعاد، ونظام توفير المعالج، وبدون أي لاج.",
      googleCta: "تسجيل الدخول عبر Google ومزامنة الحساب",
      guestCta: "تصفح كزائر",
      features: {
        f1: "⚡ مثبت ذكي بضغطة زر واحدة",
        f2: "🎨 شيدر 2048 واقعي مع سحب ديناميكية",
        f3: "🛡️ محول حسابات مكركة وأصلية داخل اللعبة",
        f4: "🚀 محرك فائق السرعة من 144 حتى 1000+ إطار"
      }
    },
    // Hero & Downloads
    hero: {
      badge: "الإصدار الرسمي v1.0.0",
      headline: "منظومة SIR المتكاملة لماينكرافت",
      subheadline: "مصممة لأعلى معدل إطارات (FPS)، ورسوميات واقعية فائقة، وتبديل فوري بين الحسابات. حمّل بضغطة زر واحدة.",
      downloadInstallerTitle: "تحميل حزمة تطبيقات SIR",
      downloadInstallerSub: "تطبيقات مستقلة: مشغل SIR ومثبت SIR ومدير السيرفرات (لويندوز 64-بت)",
      downloadBundleTitle: "تحميل الحزمة الكاملة Offline Bundle",
      downloadBundleSub: "مستقلة بالكامل • تتضمن جميع المودات والشيدرز الاحترافية والتكستشرات ثلاثية الأبعاد",
      downloadsCount: "مرات التحميل واللاعبين النشطين",
      requirements: "ويندوز 10 / 11 (64-بت) • يتضمن جافا 8 وجافا 21 تلقائياً • قريباً لنظامي ماك ولينكس",
      powerGovernorNotice: "يتضمن نظام إدارة استهلاك المعالج: اختر بين الأداء الأقصى والوضع السلس"
    },
    // Profiles Matrix
    profiles: {
      title: "بروفايلات المحرك المتكيفة",
      subtitle: "إعدادات تشغيل جاهزة مخصصة لكل أسلوب لعب، من الواقعية السينمائية 4K إلى معارك الـ PvP بأكثر من 1000 إطار/ثانية.",
      tabModern: "إصدار الحديث 26.2 (Fabric)",
      tabLegacy: "إصدار الكلاسيكي 1.8.9 (Forge)",
      modernTag: "محرك Fabric • تقنيات Iris + Sodium • تكستشرات PBR ثلاثية الأبعاد",
      legacyTag: "محرك Forge • مخصص لمعارك Hypixel • محول الحسابات المدمج (IAS)",
      modernExtreme: {
        title: "Modern 26.2 Ultra Extreme",
        desc: "محرك SIR Shader 2048 مع مياه Solas الشفافة الكريستالية، وشمس دائرية متوهجة، وأطوار قمر HD حقيقية، وبروز 3D POM، وإصلاح تمدد ضباب Distant Horizons.",
        fps: "90 - 180+ إطار/ثانية",
        specs: "RTX 3060 / RX 6600 أو أحدث"
      },
      modernBalanced: {
        title: "Modern 26.2 Balanced FPS",
        desc: "شيدر SIR المتوازن مع نفس نقاء المياه والشمس الفيزيائية، مدعوم بمودات تسريع الأداء Lithium و FerriteCore و ImmediatelyFast و C2ME.",
        fps: "144 - 280+ إطار/ثانية",
        specs: "GTX 1650 / RX 580 أو أحدث"
      },
      legacyPvp: {
        title: "Legacy 1.8.9 Competitive PvP",
        desc: "دمج OptiFine Ultra مع Patcher ومحول الحسابات IAS. حركات 1.7 السلسة، واستجابة نقرات فورية، وأقل زمن تأخير ممكن مخصص لـ Hypixel و BedWars.",
        fps: "500 - 1000+ إطار/ثانية",
        specs: "أي كرت شاشة / أكثر من 1000 إطار"
      }
    },
    // Account Linking Hub
    accountHub: {
      title: "مركز ربط حسابات ماينكرافت",
      subtitle: "اربط اسم حسابك الرسمي (Microsoft) أو حسابك المكرك (Offline) مع عرض مباشر وثلاثي الأبعاد للسكن الخاص بك.",
      officialTab: "حساب مايكروسوفت رسمي",
      crackedTab: "حساب مكرك / أوفلاين",
      inputLabel: "اسم اللاعب في ماينكرافت",
      inputPlaceholder: "مثال: Notch, Ahmed_PvP, Alex",
      saveBtn: "ربط ومزامنة السكن",
      statusLinked: "تم ربط الحساب بنجاح!",
      skinPreviewTitle: "معاينة السكن المباشرة",
      iasInfoTitle: "نظام التبديل السريع IAS مفعّل",
      iasInfoDesc: "يمكنك التبديل بين عدد غير محدود من الحسابات المكركة والأصلية مباشرة من القائمة الرئيسية للعبة دون الحاجة لإعادة تشغيل اللعبة."
    },
    // Multiplayer & Server Hosting Suite
    serverHosting: {
      badge: "اللعب الجماعي والاستضافة",
      title: "استضافة العوالم والسيرفرات: العب مع أصدقائك بضغطة زر واحدة",
      subtitle: "طريقتان فائقتان السهولة للعب مع أصدقائك على الحسابات المكركة والأصلية دون الحاجة لفتح بورتات وبدون أي لاغ.",
      ramSliderLabel: "تخصيص الذاكرة العشوائية (RAM)",
      cpuLabel: "أنوية المعالج المخصصة (vCPU)",
      slotsLabel: "عدد اللاعبين",
      inGameTitle: "🎮 استضافة العوالم من داخل اللعبة (1-Click)",
      inGameDesc: "افتح عالم السنجل بلاير الخاص بك للعامة في ثانيتين فقط! اضغط Esc ثم Open to LAN وشارك الرابط مع أصدقائك فوراً.",
      serverAppTitle: "⚡ تطبيق استوديو السيرفرات SIR Server Host",
      serverAppDesc: "تطبيق استضافة سيرفرات مستقل مدمج واختياري في مثبت SIR Installer لإدارة سيرفرات فابريك وبيربر المخصصة مع أعلام تحسين Aikar's.",
      installerFeatureNotice: "يدعم مثبت SIR Installer تثبيت تطبيق السيرفرات اختيارياً بجانب المشغل بضغطة زر واحدة.",
      soonBadge: "قريباً",
      proTierTitle: "سيرفرات SIR الاحترافية فائقة السرعة",
      proTierDesc: "أقراص NVMe فائقة السرعة مع تحسينات SIR المثبتة مسبقاً، ونظام النسخ الاحتياطي، ونفق Cloudflare الآمن.",
      notifyBtn: "انضم لقائمة الانتظار"
    },
    // HAVOC PvP Injector Portal
    havoc: {
      badge: "مشروع مميز",
      soonBadge: "قريباً",
      title: "محرك HAVOC لاحتراف الـ PvP",
      subtitle: "إنجكتر القتال من الجيل القادم مصمم للهيمنة في سيرفرات المعارك التنافسية.",
      feature1: "⚡ تحسين فائق لزمن استجابة الضربات (Hit-Reg)",
      feature2: "🎯 مثبت فيزياء الوصول وسرعة الارتداد التكيفي",
      feature3: "🛡️ محرك حقن خفيف غير قابل للكشف",
      feature4: "📊 إحصائيات معركة مباشرة ومعدل نقرات CPS",
      actionBtn: "تصفح بوابة HAVOC (قريباً)",
      authorNote: "محرك قتالي متطور وحصري"
    },
    // AI Chatbot
    ai: {
      widgetTitle: "مساعد SIR الذكي",
      onlineStatus: "متصل • المساعد الذكي",
      welcomeMsg: "مرحباً بك! أنا المساعد الذكي لمنظومة SIR. اسألني أي شيء حول التثبيت، إعدادات الشيدر، الحسابات المكركة، أو استضافة السيرفرات!",
      inputPlaceholder: "اكتب سؤالك هنا عن مودباك SIR...",
      sendBtn: "إرسال",
      thinking: "جاري التفكير...",
      promptSuggestions: [
        "كيف أستخدم الحسابات المكركة؟",
        "ما الفرق بين شيدر Extreme وشيدر Balanced؟",
        "كيف يعمل نظام إدارة استهلاك المعالج في المثبت؟"
      ]
    },
    // Error Handling & Diagnostics
    errors: {
      modalTitle: "إرسال تقرير تشخيص النظام",
      modalSubtitle: "واجهت مشكلة ما؟ أرسل تقريراً تقنياً مباشراً إلى فريق تطوير SIR لإصلاحه فوراً.",
      errorDescLabel: "اشرح المشكلة التي واجهتك",
      errorDescPlaceholder: "مثال: توقف المثبت عند استخراج الشيدرز، عدم تحميل صورة السكن...",
      submitBtn: "إرسال التقرير التقني",
      submitting: "جاري الإرسال...",
      successTitle: "تم إرسال التقرير بنجاح!",
      successDesc: "تم تسجيل بيانات الخطأ في قاعدة بيانات Firestore بأمان. رقم المرجع: ",
      closeBtn: "إغلاق",
      notFoundTitle: "404 - الإحداثيات غير موجودة",
      notFoundSubtitle: "الصفحة أو المسار المطلوب غير متاح داخل شبكة SIR.",
      returnHomeBtn: "العودة للرئيسية",
      reportErrorBtn: "الإبلاغ عن المشكلة"
    },
    // Admin Dashboard
    admin: {
      title: "لوحة تحكم وتحليلات المالك",
      subtitle: "مؤشرات حية، وإحصائيات التحميل، وسجلات الأخطاء، وحالة الخوادم السحابية.",
      stats: {
        activePlayers: "اللاعبين النشطين",
        totalDownloads: "تحميلات المثبت",
        bundleDownloads: "الحزمة الكاملة (1.1 GB)",
        errorCount: "تقارير الأخطاء المسجلة"
      },
      systemHealth: "حالة الخوادم: تعمل بنسبة 100% بكفاءة",
      recentErrorsTitle: "سجل أخطاء Firestore المباشر",
      noErrors: "لا توجد أخطاء حرجة خلال الـ 24 ساعة الماضية. جميع الأنظمة تعمل بامتياز.",
      clearBtn: "تحديث الإحصائيات"
    },
    // Footer & Trust
    footer: {
      tagline: "المنظومة الأولى عالية الأداء لماينكرافت. صُنعت بشغف لعشاق الألعاب حول العالم.",
      devLink: "رابط Linktree المطور",
      privacy: "سياسة الخصوصية",
      terms: "شروط الاستخدام",
      cookies: "سياسة ملفات تعريف الارتباط",
      copyright: "© 2026 SIR ModPack. جميع الحقوق محفوظة.",
      trustBadges: "آمن 100% • مشفر بالكامل • خاص • متوافق مع إرشادات Mojang التجارية"
    }
  }
};
