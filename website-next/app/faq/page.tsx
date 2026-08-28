"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { HelpCircle, ChevronDown, Search, ArrowLeft, ArrowRight } from "lucide-react";
import { useEcosystem } from "@/lib/context";

const FAQ_DATA = [
  {
    category: "Accounts & Alts",
    categoryAr: "الحسابات والأوفلاين",
    q: "Can I play without a paid Microsoft account?",
    qAr: "هل يمكنني اللعب بدون حساب مايكروسوفت مدفوع (مكرك)؟",
    a: "Yes! SIR Launcher natively supports Offline / Cracked accounts with custom usernames and custom skin textures. You can also switch between accounts in-game seamlessly using InGameAccountSwitcher (IAS). Official Microsoft accounts are also fully supported with secure OAuth login.",
    aAr: "نعم! يدعم SIR Launcher الحسابات المكركة والأوفلاين بشكل أصيل وكامل مع تخصيص الأسماء والسكنات، ويمكنك التبديل بين الحسابات من داخل اللعبة عبر InGameAccountSwitcher (IAS). كما تدعم المنظومة الحسابات الأصلية الرسمية عبر تسجيل دخول Microsoft OAuth الآمن.",
    actionLabel: "Open Accounts Studio",
    actionLabelAr: "فتح استوديو الحسابات",
    actionHref: "/skins"
  },
  {
    category: "Accounts & Alts",
    categoryAr: "الحسابات والأوفلاين",
    q: "How do custom skins and capes work on Offline accounts?",
    qAr: "كيف تعمل السكنات والأوشحة المخصصة على حسابات الأوفلاين والمكرك؟",
    a: "SIR Launcher integrates skin resolution via mc-heads and Mojang texture mirrors. When creating an offline account in the launcher, you can choose from curated 3D presets or paste any Minecraft username/skin URL to automatically equip it in-game.",
    aAr: "يدمج SIR Launcher نظام جلب السكنات عبر شبكات mc-heads وسيرفرات Mojang. عند إنشاء حساب أوفلاين، يمكنك اختيار سكن جاهز أو كتابة اسم أي لاعب لجلب سكنه ووشاحه وتطبيقه في اللعبة تلقائياً.",
    actionLabel: "Preview 3D Skins & Capes",
    actionLabelAr: "استعراض السكنات والأوشحة 3D",
    actionHref: "/capes"
  },
  {
    category: "Performance & RAM",
    categoryAr: "الأداء والرامات",
    q: "How much RAM should I allocate to SIR ModPack?",
    qAr: "كم مقدار الرام (RAM) الموصى بتخصيصه لحزمة SIR ModPack؟",
    a: "For Modern 26.2 with SIR Shaders, we recommend 6 GB to 8 GB of RAM. For Legacy 1.8.9 PvP, 2 GB to 4 GB is optimal. Our built-in Smart Hardware Engine automatically detects your total system memory and applies the ideal allocation with Aikar's tuned G1GC memory flags.",
    aAr: "لنسخة Modern 26.2 مع الشيدرز المتطور، نوصي بتخصيص 6 إلى 8 جيجابايت. لنسخة 1.8.9 PvP يكفي 2 إلى 4 جيجابايت. ويقوم محرك العتاد الذكي في اللانشر بفحص رام جهازك وضبط التخصيص الأمثل تلقائياً مع معايير G1GC المتطورة.",
    actionLabel: "Configure Rig & RAM Allocation",
    actionLabelAr: "ضبط ومحاكاة تخصيص الرام",
    actionHref: "/benchmarks"
  },
  {
    category: "Performance & RAM",
    categoryAr: "الأداء والرامات",
    q: "How do I fix stutter or frame drops on low-end PCs?",
    qAr: "كيف أتخلص من التقطيع وهبوط الفريمات على الأجهزة الضعيفة؟",
    a: "1. Switch to the 'SIR 26 (Competitive Speed)' or 'Balanced 144+ FPS' preset in the Launcher.\n2. In Launcher Settings, toggle 'Smooth / Eco Mode' to reduce CPU thread pressure.\n3. Reduce render distance to 8-12 chunks and disable Distant Horizons if using integrated graphics.",
    aAr: "1. اختر نمط Competitive Speed أو Balanced 144+ FPS من اللانشر.\n2. فعّل وضع Smooth / Eco Mode من إعدادات اللانشر لتخفيف العبء على المعالج.\n3. اضبط مسافة الرندر على 8-12 تشك وعطّل Distant Horizons إذا كنت تستخدم كرتاً مدمجاً.",
    actionLabel: "View Performance Presets",
    actionLabelAr: "استعراض أنماط الأداء العالي",
    actionHref: "/profiles"
  },
  {
    category: "SIR Shaders & POM",
    categoryAr: "الشيدرز والبلوكات ثلاثية الأبعاد",
    q: "Why do blocks have 3D relief textures (POM)?",
    qAr: "لماذا تظهر البلوكات مجسمة وبارزة بشكل ثلاثي الأبعاد (POM)؟",
    a: "SIR ModPack integrates custom normal and specular depth maps in SIR_Ultimate_Pack.zip paired with SIR Shaders. Parallax Occlusion Mapping (POM) calculates optical surface depth in real-time, giving bricks, wood, and stones physical 3D relief without slowing down your GPU.",
    aAr: "تدمج حزمة SIR خرائط عمق متطورة في ملف SIR_Ultimate_Pack.zip مقترنة بمحرك الشيدرز. تقنية POM تحسب عمق الأسطح لحظياً لتبدو الأحجار والأخشاب مجسمة وبارزة ثلاثية الأبعاد دون التأثير على سلاسة الإطارات.",
    actionLabel: "Explore 3D Shaders Suite",
    actionLabelAr: "استكشاف حزمة الشيدرز 3D",
    actionHref: "/shaders"
  },
  {
    category: "SIR Shaders & POM",
    categoryAr: "الشيدرز والبلوكات ثلاثية الأبعاد",
    q: "What is the difference between SIR Extreme and SIR Balanced shaders?",
    qAr: "ما الفرق بين شيدر SIR Extreme وشيدر SIR Balanced؟",
    a: "Both shaders feature crystal-clear physics water with caustics and the exact same glowing physics sun and detailed moon. SIR Extreme enables full volumetric fog, screen-space reflections, and high-res shadows for max visual fidelity. SIR Balanced optimizes shadow passes and bloom for esports 144+ FPS.",
    aAr: "كلا الشيدرين يتميزان بنفس المياه الفيزيائية الكريستالية والشمس الدائرية المتوهجة والقمر الواقعي. نمط Extreme يفعّل الضباب الحجمي والانعكاسات الكاملة لأعلى واقعية، بينما نمط Balanced يحسّن الظلال لضمان 144+ إطاراً ثابتاً.",
    actionLabel: "Compare Shaders Features",
    actionLabelAr: "مقارنة مواصفات الشيدرين",
    actionHref: "/shaders"
  },
  {
    category: "Troubleshooting",
    categoryAr: "حل المشكلات والأخطاء",
    q: "Game crashes on launch with error code -1 or Java crash?",
    qAr: "اللعبة تغلق عند التشغيل بسبب خطأ كود -1 أو تعطل جافا؟",
    a: "1. Open SIR Launcher -> Settings -> Self-Repair Studio and click 'Verify All Hashes' to redownload any corrupt library JARs.\n2. Ensure your GPU drivers (NVIDIA / AMD / Intel) are up to date.\n3. Modern 26.2 automatically uses OpenJDK 25 runtime and Legacy 1.8.9 uses Java 8.",
    aAr: "1. افتح اللانشر -> الإعدادات -> استوديو الإصلاح الذاتي واضغط على فحص الملفات لإعادة تحميل أي مكتبة ناقصة.\n2. تأكد من تحديث تعريفات كرت الشاشة لديك.\n3. تستخدم نسخة 26.2 الحديثة جافا 25 (OpenJDK 25) تلقائياً ونسخة 1.8.9 تستخدم جافا 8.",
    actionLabel: "Get OpenJDK 25 Runtime",
    actionLabelAr: "تحميل حزمة OpenJDK 25",
    actionHref: "https://github.com/adoptium/temurin25-binaries/releases"
  },
  {
    category: "Troubleshooting",
    categoryAr: "حل المشكلات والأخطاء",
    q: "Distant Horizons shows vertical smearing or LOD rendering glitches?",
    qAr: "ظهور خطوط عمودية أو تداخل في رندر العوالم البعيدة (Distant Horizons)؟",
    a: "SIR Shaders 2.0 includes a specialized depth-buffer fix for Distant Horizons LOD rendering. Ensure you are using SIR_Extreme_Shader.zip or SIR_Balanced_Shader.zip, and set LOD render distance to 'Medium (128 Chunks)' in DH settings.",
    aAr: "يتضمن شيدر SIR 2.0 معالجة مخصصة للعمق البصري لـ Distant Horizons. تأكد من استخدام شيدر SIR_Extreme أو SIR_Balanced وضبط مسافة رندر العوالم البعيدة على 128 تشك لتجربة خالية من أي تشويش.",
    actionLabel: "View Shaders & LOD Guide",
    actionLabelAr: "دليل ضبط الشيدرز والـ LOD",
    actionHref: "/shaders"
  },
  {
    category: "Multiplayer & Hosting",
    categoryAr: "السيرفرات واللعب الجماعي",
    q: "How does 1-Click World Hosting (Open to LAN) work?",
    qAr: "كيف تعمل ميزة استضافة العالم بنقرة واحدة (Open to LAN)؟",
    a: "While in any singleplayer world in SIR Modern 26.2, press Esc -> Open to LAN. The integrated peer tunneling automatically creates a public join link in chat that you can share with friends (supports both Official and Cracked friends with zero port-forwarding required).",
    aAr: "أثناء اللعب في أي عالم فردي بنسخة 26.2، اضغط Esc ثم Open to LAN. يقوم النفق المدمج بإنشاء رابط مباشر في الشات لمشاركته مع أصدقائك (يدعم المكرك والأصلي وبدون الحاجة لفتح بورتات الراوتر).",
    actionLabel: "Explore Server Hosting Hub",
    actionLabelAr: "استكشاف بوابة السيرفرات",
    actionHref: "/servers"
  },
  {
    category: "Multiplayer & Hosting",
    categoryAr: "السيرفرات واللعب الجماعي",
    q: "How do I host a 24/7 dedicated server with SIR Server Manager?",
    qAr: "كيف أقوم بتشغيل سيرفر مخصص 24/7 عبر تطبيق SIR Server Manager؟",
    a: "Launch 'SIR Server Manager.exe' from the launcher or desktop. Select your preferred engine (Fabric 26.2 or Purpur), click 'Start Server', and click 'Start Playit Tunnel' to obtain a permanent free public IP with zero port-forwarding.",
    aAr: "افتح تطبيق 'SIR Server Manager.exe' من اللانشر أو سطح المكتب، اختر نوع السيرفر (Fabric أو Purpur)، اضغط 'Start Server' ثم شغّل نفق Playit Tunnel للحصول على IP عام مجاني ودائم دون أي إعدادات راوتر معقدة.",
    actionLabel: "Explore Dedicated Server Hosting",
    actionLabelAr: "استكشاف خادم السيرفرات المخصص",
    actionHref: "/servers"
  }
];

export default function FaqPage() {
  const { lang } = useEcosystem();
  const [search, setSearch] = useState("");
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const isAr = lang === "ar";

  const filtered = FAQ_DATA.filter(item => {
    if (!search) return true;
    const q = isAr ? item.qAr : item.q;
    const a = isAr ? item.aAr : item.a;
    return q.toLowerCase().includes(search.toLowerCase()) || a.toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-4xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-400 border border-cyan-300 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5" />
            {isAr ? "قاعدة المعرفة والأسئلة الشائعة" : "Interactive Knowledge Base"}
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "الأسئلة الشائعة وإرشادات الضبط الذاتي" : "Frequently Asked Questions & Help"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "إجابات فورية ومفصلة لجميع استفسارات تخصيص الرام وإصلاح المشاكل وتشغيل الشيدرز بأعلى سلاسة."
              : "Instant answers and optimization guides for RAM tuning, shader configuration, and troubleshooting."}
          </p>
        </div>

        {/* Search Input Bar */}
        <div className="relative">
          <Search className={`w-5 h-5 text-slate-400 absolute ${isAr ? "right-4" : "left-4"} top-1/2 -translate-y-1/2 pointer-events-none z-10`} />
          <input 
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder={isAr ? "ابحث في المشكلات والأسئلة الشائعة..." : "Search questions and solutions..."}
            className={`w-full ${isAr ? "pr-12 pl-4" : "pl-12 pr-4"} py-3.5 rounded-2xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-xs outline-none focus:border-cyan-500 dark:focus:border-cyan-400 shadow-sm transition-all`}
          />
        </div>

        {/* FAQ Accordion List */}
        <div className="space-y-3">
          {filtered.map((item, idx) => {
            const isOpen = openIndex === idx;
            return (
              <div 
                key={idx}
                className={`rounded-2xl border overflow-hidden transition-all duration-200 shadow-sm ${
                  isOpen 
                    ? 'border-cyan-400 dark:border-cyan-500/50 bg-white dark:bg-[#101624] shadow-md' 
                    : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-[#070a10] hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <button 
                  onClick={() => setOpenIndex(isOpen ? null : idx)}
                  className="w-full flex items-center justify-between text-left gap-4 p-5 cursor-pointer"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-mono text-cyan-600 dark:text-cyan-400 px-2 py-0.5 rounded-md bg-cyan-100 dark:bg-cyan-950/60 border border-cyan-300 dark:border-cyan-900 whitespace-nowrap">
                      {isAr ? item.categoryAr : item.category}
                    </span>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100 text-left">{isAr ? item.qAr : item.q}</h3>
                  </div>
                  <ChevronDown className={`w-4 h-4 flex-shrink-0 transition-transform duration-300 ${isOpen ? 'rotate-180 text-cyan-500' : 'text-slate-400 dark:text-slate-500'}`} />
                </button>

                {/* Smooth expand/collapse via max-height CSS transition */}
                <div
                  style={{
                    maxHeight: isOpen ? '400px' : '0px',
                    overflow: 'hidden',
                    transition: 'max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
                  }}
                >
                  <div className="px-5 pb-5 space-y-4 border-t border-slate-100 dark:border-slate-800/80 pt-3">
                    <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-line">
                      {isAr ? item.aAr : item.a}
                    </p>
                    {item.actionHref && (
                      <div className="pt-1">
                        {item.actionHref.startsWith('http') ? (
                          <a 
                            href={item.actionHref} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-100 px-4 py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-700 dark:text-cyan-300 transition-all hover:scale-105"
                          >
                            <span>{isAr ? item.actionLabelAr : item.actionLabel}</span>
                            {isAr ? <ArrowLeft className="w-3.5 h-3.5" /> : <ArrowRight className="w-3.5 h-3.5" />}
                          </a>
                        ) : (
                          <Link 
                            href={item.actionHref}
                            className="inline-flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-100 px-4 py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-700 dark:text-cyan-300 transition-all hover:scale-105"
                          >
                            <span>{isAr ? item.actionLabelAr : item.actionLabel}</span>
                            {isAr ? <ArrowLeft className="w-3.5 h-3.5" /> : <ArrowRight className="w-3.5 h-3.5" />}
                          </Link>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
