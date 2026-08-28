"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";
import { Shield, ExternalLink, Lock, CheckCircle, Heart, X, FileText, ShieldCheck, Cookie, Copy, Check } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function Footer() {
  const { t, dir, triggerErrorReport, triggerSuggestion } = useEcosystem();
  const [legalModal, setLegalModal] = useState<"privacy" | "terms" | "cookies" | null>(null);
  const [copied, setCopied] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const legalSections = {
    privacy: {
      title: dir === "rtl" ? "سياسة الخصوصية الشاملة" : "Universal Privacy Policy",
      subtitle: dir === "rtl" ? "معايير حماية البيانات والخصوصية المحلية المشفرة" : "Privacy-by-Design & Zero-Telemetry Architecture",
      icon: Shield,
      tag: "v1.0.0 Compliant",
      sections: [
        {
          num: "01",
          title: dir === "rtl" ? "جمع البيانات والغرض منها" : "Data Minimization & Purpose",
          body: dir === "rtl" 
            ? "نلتزم في منظومة SIR بمبدأ التقليل من البيانات (Data Minimization). نجمع فقط البيانات الأساسية اللازمة لتشغيل الميزات الحيوية مثل مزامنة الحسابات: اسم اللاعب (IGN)، الرابط المباشر للسكن ثلاثي الأبعاد، والمعرف الرقمي المجهول. لا نقوم إطلاقاً بجمع أي بيانات سرية أو كلمات مرور الحسابات."
            : "We collect only the bare minimum data required to deliver core launcher and account syncing features: your chosen In-Game Name (IGN), 3D skin render URL, and anonymous auth identifier (UID). We NEVER collect, store, or inspect your Minecraft passwords or private Mojang credentials."
        },
        {
          num: "02",
          title: dir === "rtl" ? "المزامنة السحابية وقواعد البيانات" : "Cloud & Realtime Synchronization",
          body: dir === "rtl"
            ? "يتم حفظ بيانات البروفايل المعروضة فقط عبر خوادم Google Cloud Firestore و Firebase Realtime Database المشفرة بالكامل ببروتوكول TLS 1.3 مع شهادات أمان متقدمة. لا يتم تسجيل أو اعتراض أي محادثات داخل اللعبة أو بيانات اللعب الفردية."
            : "Public profile attributes are securely stored in Google Cloud Firestore and Firebase Realtime Database with end-to-end TLS 1.3 encryption. We do not inspect, intercept, log, or harvest private gameplay data, local world saves, or in-game chat messages."
        },
        {
          num: "03",
          title: dir === "rtl" ? "التخزين المحلي وأمان الحسابات" : "Local Storage & IAS Security",
          body: dir === "rtl"
            ? "تفضيلات الواجهة (الوضع الليلي/النهاري، اختيار اللغة) وبيانات تسجيل الدخول عبر محول الحسابات InGameAccountSwitcher (IAS) تحفظ محلياً بالكامل على جهاز المستخدم فقط ولا تُرسل لأي خوادم خارجية."
            : "UI preferences (Dark/Light mode, language selection) and account switching tokens via InGameAccountSwitcher (IAS) are saved strictly inside your local device filesystem and browser localStorage."
        },
        {
          num: "04",
          title: dir === "rtl" ? "انعدام الإعلانات والبيع للطرف الثالث" : "Zero Third-Party Monetization",
          body: dir === "rtl"
            ? "نضمن لك بنسبة 100% أننا لا نبيع أو نؤجر أو نشارك أي بيانات للمستخدمين مع شركات الإعلانات أو الوسطاء التجاريين أو أي جهات خارجية."
            : "We do not sell, rent, monetize, track, or disclose any user information to third-party advertisers, data brokers, or commercial marketing agencies."
        },
        {
          num: "05",
          title: dir === "rtl" ? "حقوق المستخدم ومسح البيانات" : "User Rights & Data Erasure",
          body: dir === "rtl"
            ? "يحق للمستخدم في أي وقت طلب الحذف الفوري والكامل لحسابه أو بيانات البروفايل الخاصة به من خوادم المنظومة عبر مركز الحسابات أو بالتواصل مع الإدارة."
            : "You maintain absolute ownership of your data. You may request total and permanent erasure of your cloud account and linked profile records at any time via the Account Hub."
        },
        {
          num: "06",
          title: dir === "rtl" ? "الحماية والبنية التحتية" : "Infrastructure & DDoS Defense",
          body: dir === "rtl"
            ? "تخضع جميع الاتصالات لحماية متقدمة ضد هجمات DDoS والمسح الآلي عبر Cloudflare Tunnel وقواعد حماية Firebase الصارمة."
            : "All endpoints are protected behind enterprise Firebase Security Rules, CORS restrictions, and Cloudflare Tunnel infrastructure to safeguard against unauthorized access and DDoS attacks."
        }
      ]
    },
    terms: {
      title: dir === "rtl" ? "شروط الخدمة والاستخدام" : "Terms of Service",
      subtitle: dir === "rtl" ? "اتفاقية ترخيص المستخدم والاستخدام العادل" : "End User License Agreement & Fair Play Guidelines",
      icon: FileText,
      tag: "Community Edition",
      sections: [
        {
          num: "01",
          title: dir === "rtl" ? "قبول الشروط" : "Acceptance of Terms",
          body: dir === "rtl"
            ? "باستخدامك أو تحميلك أو تشغيلك لأي جزء من منظومة SIR (بما في ذلك SIR Launcher، مثبت SIR Installer، الشيدرز المخصصة، حزم التكستشر، أو الموقع الإلكتروني)، فإنك توافق على الالتزام الكامل بهذه الشروط."
            : "By downloading, installing, launching, or accessing any component of the SIR Ecosystem (including SIR Launcher, SIR Installer, custom Shaders, 3D Resource Packs, and Web Platform), you acknowledge and agree to be bound by these Terms."
        },
        {
          num: "02",
          title: dir === "rtl" ? "الامتثال لقوانين Mojang Studios و Microsoft" : "Mojang Studios Compliance",
          body: dir === "rtl"
            ? "ماينكرافت علامة تجارية مسجلة لشركة Mojang AB و Microsoft. منظومة SIR هي مشروع مستقل مفتوح المصدر تم تطويره من قِبل مجتمع اللاعبين، وليس منتجاً رسمياً من Mojang أو Microsoft. يلتزم المشروع التزاماً تاماً بإرشادات العلامة التجارية والاستخدام التجاري لموجانج."
            : "Minecraft is a registered trademark of Mojang AB / Microsoft. The SIR Ecosystem is an independent, community-driven open-source project and is NOT an official Minecraft product, nor is it endorsed by, affiliated with, or associated with Mojang AB or Microsoft."
        },
        {
          num: "03",
          title: dir === "rtl" ? "التراخيص والمصادر المفتوحة" : "Open-Source & Attribution",
          body: dir === "rtl"
            ? "كافة الأدوات البرمجية الخاصة بالمشروع (المشغل، المثبت، وبوابة الويب) مرخصة ومحمية برخص المصادر المفتوحة. تظل المودات والشيدرز والتكستشرات الخارجية ملكاً لأصحابها ومطوريها الأصليين مع الحفاظ على كامل حقوقهم الأدبية."
            : "Custom launcher modules, installer utilities, and web source codes are distributed under open-source licenses. Bundled third-party mods, shaders, and textures remain the intellectual property of their respective creators."
        },
        {
          num: "04",
          title: dir === "rtl" ? "النزاهة واللعب العادل" : "Fair Play & Competitive Integrity",
          body: dir === "rtl"
            ? "يتحمل المستخدم المسؤولية الكاملة عن الامتثال لقوانين السيرفرات التي ينضم إليها. ميزات التبديل بين الحسابات وأدوات تسريع الأداء مخصصة لتحسين تجربة اللعب بشكل عادل وقانوني."
            : "Users are expected to utilize the SIR Ecosystem in accordance with standard fair play rules. While the client provides advanced rendering optimizations and account switching tools, server-specific rules regarding modifications and alts must be respected by the user."
        },
        {
          num: "05",
          title: dir === "rtl" ? "إخلاء المسؤولية" : "Disclaimer of Warranties",
          body: dir === "rtl"
            ? "يتم توفير منظومة SIR 'كما هي' دون أي ضمانات صريحة أو ضمنية. لا يتحمل المطورون أي مسؤولية عن أي حظر من سيرفرات خارجية أو تعارض في ملفات الحفظ ناتج عن تعديلات شخصية يقوم بها المستخدم."
            : "The SIR Ecosystem is provided 'AS IS', without warranty of any kind, express or implied. Maintainers shall not be liable for any third-party server sanctions, hardware incompatibilities, or save data corruption resulting from unauthorized user modifications."
        }
      ]
    },
    cookies: {
      title: dir === "rtl" ? "سياسة ملفات تعريف الارتباط" : "Cookie & Storage Policy",
      subtitle: dir === "rtl" ? "الشفافية في استخدام التخزين المحلي والجلسات" : "Local Storage Transparency & Session Management",
      icon: Cookie,
      tag: "100% Non-Tracking",
      sections: [
        {
          num: "01",
          title: dir === "rtl" ? "ما الذي نقوم بتخزينه" : "Essential Storage Keys",
          body: dir === "rtl"
            ? "تستخدم منصة SIR ملفات تعريف ارتباط وتخزين محلي (LocalStorage) فقط وحصرياً للأغراض التشغيلية الأساسية: جلسات تسجيل الدخول عبر Firebase Auth، تفضيلات الواجهة (sir_lang, sir_theme)، والذاكرة المؤقتة لاسم اللاعب والسكن لتسريع التصفح."
            : "The SIR Web Platform utilizes essential local storage entries and session cookies exclusively for core functional requirements: Firebase Auth session tokens, UI preferences (sir_lang, sir_theme), and local caching for your 3D avatar."
        },
        {
          num: "02",
          title: dir === "rtl" ? "انعدام ملفات التتبع الإعلاني" : "Zero Marketing Trackers",
          body: dir === "rtl"
            ? "لا نستخدم نهائياً أي ملفات تعريف ارتباط إعلانية، أو أدوات تتبع عبر المواقع، أو بيكسلات تتبع سلوكي من أي نوع."
            : "We do NOT use invasive cross-site tracking cookies, third-party advertising beacons, or behavioral tracking pixels."
        },
        {
          num: "03",
          title: dir === "rtl" ? "التحكم وإدارة التخزين" : "User Storage Controls",
          body: dir === "rtl"
            ? "يمكنك في أي وقت مسح ملفات الكوكيز والتخزين المحلي من خلال إعدادات المتصفح بكل سهولة وبضغطة زر واحدة."
            : "You can clear your local storage and cookies at any time through your browser's security settings. Clearing storage simply resets your UI preferences to defaults."
        }
      ]
    }
  };

  const copyCurrentPolicy = () => {
    if (!legalModal) return;
    const current = legalSections[legalModal];
    const text = `${current.title} - ${current.subtitle}\n\n` + 
      current.sections.map(s => `${s.num}. ${s.title}:\n${s.body}`).join("\n\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <footer className="bg-slate-50 dark:bg-[#090b10] border-t border-slate-200 dark:border-slate-800 pt-16 pb-12 relative z-10 text-slate-700 dark:text-gray-300 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Top Tier: Brand & Linktree */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-12 border-b border-slate-200 dark:border-slate-800">
          
          {/* Brand Info */}
          <div className="md:col-span-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-2xl bg-slate-900 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-1 shadow-sm overflow-hidden">
                <img
                  src="/sir-logo.png"
                  alt="SIR Logo"
                  className="w-full h-full object-contain rounded-xl"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              </div>
              <span className="font-black text-lg text-slate-900 dark:text-white tracking-tight">
                {t.nav?.brand || "SIR ModPack"}
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-gray-400 max-w-md leading-relaxed">
              {t.footer?.tagline || "The next-generation competitive Minecraft ecosystem designed for performance and PvP dominance."}
            </p>
          </div>

          {/* Quick Links & Developer */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-gray-300">
              Ecosystem
            </h4>
            <ul className="space-y-2 text-xs text-slate-600 dark:text-gray-400">
              <li>
                <a href="/#downloads" className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors">{t.nav?.downloads || "Downloads"}</a>
              </li>
              <li>
                <a href="/#profiles" className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors">{t.nav?.profiles || "Profiles"}</a>
              </li>
              <li>
                <a href="/#hosting" className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors">{t.nav?.serverHosting || "Hosting"}</a>
              </li>
              <li>
                <a href="/#havoc" className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors">{t.nav?.havoc || "HAVOC"}</a>
              </li>
            </ul>
          </div>

          {/* Developer & Legal */}
          <div className="md:col-span-3 space-y-3">
            <h4 className="text-xs font-black uppercase tracking-wider text-slate-900 dark:text-gray-300">
              Developer & Legal
            </h4>
            <ul className="space-y-2 text-xs text-slate-600 dark:text-gray-400">
              <li>
                <a
                  href="https://linktr.ee/sir.ahmed"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-cyan-600 dark:text-[#00e5ff] hover:underline font-bold transition-colors"
                >
                  <span>{t.footer?.devLink || "Developer Linktree (Sir Ahmed)"}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="/admin"
                  className="inline-flex items-center gap-1.5 text-emerald-600 dark:text-[#38ef7d] hover:underline font-bold transition-colors"
                >
                  <span>⚡ Admin Mission Control Studio</span>
                </a>
              </li>
              <li>
                <Link
                  href="/privacy"
                  className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors"
                >
                  {t.footer?.privacy || "Privacy Policy"}
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors"
                >
                  {t.footer?.terms || "Terms of Service"}
                </Link>
              </li>
              <li>
                <Link
                  href="/cookies"
                  className="hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-colors"
                >
                  {t.footer?.cookies || "Cookie Policy"}
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Middle Tier: Trust Badges */}
        <div className="py-8 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-gray-400">
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-2">
              <Lock className="w-3.5 h-3.5 text-cyan-600 dark:text-[#00e5ff]" />
              <span>100% Secure • Encrypted</span>
            </span>
            <span className="flex items-center gap-2">
              <CheckCircle className="w-3.5 h-3.5 text-emerald-600 dark:text-[#38ef7d]" />
              <span>Zero Malware • Open Audited</span>
            </span>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => triggerErrorReport("Manual Issue Report", "User clicked report button in footer.")}
              className="px-3 py-1.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/30 text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-sm"
              title="Report an issue or bug to developers"
            >
              <span>📝 Report an Issue</span>
            </button>

            <button
              onClick={() => triggerSuggestion()}
              className="px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-600 dark:text-[#00e5ff] border border-cyan-500/30 text-[11px] font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-sm"
              title="Send a feature suggestion or mod request"
            >
              <span>💡 Send a Suggestion</span>
            </button>
          </div>
        </div>

        {/* Bottom Tier: Copyright */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-gray-500">
          <div>
            <span>{t.footer?.copyright || "© 2026 SIR ModPack Ecosystem. All rights reserved."}</span>
          </div>
        </div>

      </div>

      {/* Render Portal Directly at document.body at z-[99999] so Navbar never covers it */}
      {mounted && typeof document !== "undefined" && createPortal(
        <AnimatePresence>
          {legalModal && (
            <div className="fixed inset-0 z-[99999] flex items-center justify-center p-4 sm:p-6 sm:pt-20 overflow-y-auto">
              
              {/* Dark Blur Backdrop (Sitting ABOVE Navbar and Whole Page) */}
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setLegalModal(null)} 
                className="fixed inset-0 bg-slate-900/60 dark:bg-black/90 backdrop-blur-md -z-10" 
              />

              {/* Modal Card with Guaranteed Top Clearance and Custom Cyber Scrollbar */}
              <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 25 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 25 }}
                transition={{ type: "spring", stiffness: 350, damping: 28 }}
                className="relative w-full max-w-3xl max-h-[82vh] my-auto flex flex-col rounded-3xl bg-white dark:bg-[#090d16] border border-slate-200 dark:border-cyan-500/40 shadow-2xl z-10 overflow-hidden"
              >
                {/* Header with Navigation Tabs */}
                <div className="px-6 py-5 sm:px-8 border-b border-slate-200 dark:border-slate-800/80 shrink-0 bg-slate-50 dark:bg-[#05080f]">
                  <div className="flex items-center justify-between gap-4 mb-4">
                    
                    {/* Title & Badge */}
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-inner">
                        {React.createElement(legalSections[legalModal].icon, { className: "w-5 h-5" })}
                      </div>
                      <div>
                        <h3 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white leading-tight flex items-center gap-2">
                          <span>{legalSections[legalModal].title}</span>
                        </h3>
                        <p className="text-xs text-cyan-600 dark:text-cyan-400 font-mono mt-0.5">
                          {legalSections[legalModal].subtitle}
                        </p>
                      </div>
                    </div>

                    {/* Top Action Buttons */}
                    <div className="flex items-center gap-2">
                      <button
                        onClick={copyCurrentPolicy}
                        className="p-2 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/60 text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400 hover:border-cyan-500/50 cursor-pointer transition-all flex items-center gap-1.5 text-xs font-mono shadow-sm"
                        title="Copy policy text"
                      >
                        {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                        <span className="hidden sm:inline">{copied ? "Copied!" : "Copy"}</span>
                      </button>

                      <button
                        onClick={() => setLegalModal(null)}
                        className="p-2 rounded-xl bg-white dark:bg-slate-800/80 border border-slate-300 dark:border-slate-700/60 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer transition-colors shadow-sm"
                        aria-label="Close modal"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>

                  </div>

                  {/* Switcher Tabs */}
                  <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1">
                    {(["privacy", "terms", "cookies"] as const).map((key) => {
                      const active = legalModal === key;
                      return (
                        <button
                          key={key}
                          onClick={() => setLegalModal(key)}
                          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap flex items-center gap-1.5 border ${
                            active
                              ? "bg-cyan-100 text-cyan-900 border-cyan-300 dark:bg-cyan-500/20 dark:text-cyan-300 dark:border-cyan-500/50 shadow-sm font-black"
                              : "bg-white text-slate-600 border-slate-200 hover:text-slate-900 hover:border-slate-300 dark:bg-slate-900/60 dark:text-slate-400 dark:border-slate-800 dark:hover:text-slate-200 dark:hover:border-slate-700"
                          }`}
                        >
                          {key === "privacy" && <Shield className="w-3.5 h-3.5" />}
                          {key === "terms" && <FileText className="w-3.5 h-3.5" />}
                          {key === "cookies" && <Cookie className="w-3.5 h-3.5" />}
                          <span>{legalSections[key].title}</span>
                        </button>
                      );
                    })}
                  </div>

                </div>

                {/* Scrollable Content Body with Sleek Cyber Scrollbar */}
                <div className="flex-1 overflow-y-auto px-6 py-6 sm:px-8 space-y-4 [scrollbar-width:thin] [scrollbar-color:rgba(0,229,255,0.4)_transparent] [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-track]:bg-slate-950/40 [&::-webkit-scrollbar-thumb]:bg-cyan-500/30 hover:[&::-webkit-scrollbar-thumb]:bg-cyan-400/60 [&::-webkit-scrollbar-thumb]:rounded-full">
                  {legalSections[legalModal].sections.map((sec, idx) => (
                    <motion.div 
                      key={sec.num}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.25, delay: idx * 0.04 }}
                      className="p-4 sm:p-5 rounded-2xl bg-slate-50 dark:bg-[#060910] border border-slate-200 dark:border-slate-800/80 hover:border-cyan-500/40 dark:hover:border-cyan-500/30 transition-colors space-y-2"
                    >
                      <div className="flex items-center gap-2.5">
                        <span className="px-2.5 py-0.5 rounded-lg text-[10px] font-mono font-black bg-cyan-100 text-cyan-800 border border-cyan-200 dark:bg-cyan-500/10 dark:text-cyan-400 dark:border-cyan-500/20">
                          {sec.num}
                        </span>
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
                          {sec.title}
                        </h4>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed pl-1 sm:pl-2">
                        {sec.body}
                      </p>
                    </motion.div>
                  ))}
                </div>

                {/* Sticky Footer */}
                <div className="flex items-center justify-between px-6 py-4 sm:px-8 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#05080f] shrink-0">
                  <span className="text-xs font-mono text-emerald-700 dark:text-emerald-400 flex items-center gap-2 font-bold">
                    <ShieldCheck className="w-4 h-4" />
                    <span>100% Verified & Compliant • v1.0.0</span>
                  </span>

                  <button
                    onClick={() => setLegalModal(null)}
                    className="px-6 py-2.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-400 hover:from-cyan-400 hover:to-emerald-300 text-black font-black text-xs cursor-pointer shadow-lg hover:shadow-cyan-500/20 transition-all active:scale-95"
                  >
                    {dir === "rtl" ? "إغلاق" : "Close"}
                  </button>
                </div>

              </motion.div>
            </div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </footer>
  );
}
