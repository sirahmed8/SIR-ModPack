"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useEcosystem } from "@/lib/context";
import { 
  Menu, 
  X, 
  Search, 
  Download, 
  Layers, 
  Package, 
  Sparkles, 
  ShieldCheck, 
  Shirt, 
  Compass, 
  Monitor, 
  Swords, 
  Music, 
  Eye, 
  Trophy, 
  Globe, 
  Activity, 
  HelpCircle, 
  Server, 
  Flame, 
  History, 
  Radio, 
  Lock, 
  FileText, 
  Cookie, 
  Wrench,
  Zap,
  ExternalLink,
  ChevronRight
} from "lucide-react";

interface NavItem {
  labelEn: string;
  labelAr: string;
  descEn?: string;
  descAr?: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
  color: string;
  highlight?: boolean;
}

interface CategoryGroup {
  id: string;
  titleEn: string;
  titleAr: string;
  icon: React.ElementType;
  accentColor: string;
  items: NavItem[];
}

const ORGANIZED_CATEGORIES: CategoryGroup[] = [
  {
    id: "customization",
    titleEn: "Customization & Visuals Studio",
    titleAr: "استوديو التخصيص والمظهر",
    icon: Sparkles,
    accentColor: "text-purple-400 bg-purple-500/10 border-purple-500/30",
    items: [
      {
        labelEn: "Master Shaders 2.0 Optical Lab",
        labelAr: "مختبر شيدرز SIR 2.0 الفائق",
        descEn: "SIR Extreme & Balanced Shaders with 3D POM",
        descAr: "شيدرز Extreme و Balanced مع تجسيم 3D POM",
        href: "/shaders",
        icon: Sparkles,
        badge: "3D POM",
        color: "text-amber-400"
      },
      {
        labelEn: "Mods Suite (240+ Verified)",
        labelAr: "كتالوج المودات (240+ مود)",
        descEn: "Live Modrinth & CurseForge Explorer",
        descAr: "استكشف مودات التحسين والرسوميات والـ PvP",
        href: "/mods",
        icon: Package,
        badge: "240+ Mods",
        color: "text-cyan-400"
      },
      {
        labelEn: "Resource Packs & 3D Textures",
        labelAr: "حزم الموارد وتجسيم البلوكات",
        descEn: "SIR Ultimate Pack 3D & Legacy 32x Faithful",
        descAr: "حزمة SIR ثلاثية الأبعاد وحزمة 1.8.9 الكلاسيكية",
        href: "/packs",
        icon: Layers,
        badge: "3D POM",
        color: "text-pink-400"
      },
      {
        labelEn: "Capes Studio & Optics",
        labelAr: "استوديو الأوشحة المخصصة",
        descEn: "Upload & Preview Animated/Static Capes in 3D",
        descAr: "معاينة وتصميم الأوشحة المتحركة ثلاثية الأبعاد",
        href: "/capes",
        icon: ShieldCheck,
        badge: "3D View",
        color: "text-purple-400"
      },
      {
        labelEn: "Skin Studio & Avatar 3D",
        labelAr: "استوديو السكنات والمجسمات",
        descEn: "Interactive 3D Minecraft Skin Inspector",
        descAr: "فحص وتعديل وتحميل سكنات اللاعبين",
        href: "/skins",
        icon: Shirt,
        color: "text-blue-400"
      }
    ]
  },
  {
    id: "gaming",
    titleEn: "Gaming, Performance & Tools",
    titleAr: "الأداء والأدوات التنافسية",
    icon: Swords,
    accentColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
    items: [
      {
        labelEn: "PvP CPS & Reaction Trainer",
        labelAr: "مختبر النقر وسرعة الاستجابة",
        descEn: "Butterfly/Jitter CPS & Visual Aim Reflex Test",
        descAr: "اختبار سرعة النقر وردة الفعل لمقاتلي الـ PvP",
        href: "/trainer",
        icon: Swords,
        badge: "1000Hz",
        color: "text-rose-400"
      },
      {
        labelEn: "Hardware FPS Calculator",
        labelAr: "حاسبة الأداء والفريمات (FPS)",
        descEn: "Simulate FPS across GPU/CPU & Shader Presets",
        descAr: "حساب دقيق للفريمات بحسب مواصفات جهازك",
        href: "/benchmarks",
        icon: Activity,
        badge: "FPS Sim",
        color: "text-emerald-400"
      },
      {
        labelEn: "System Scanner & Java Doctor",
        labelAr: "فاحص توافق النظام و Java",
        descEn: "RAM Allocation, Driver Check & Integrity Scan",
        descAr: "فحص توافق عتاد الحاسوب وإصدارات الجافا",
        href: "/compatibility",
        icon: Monitor,
        color: "text-cyan-400"
      },
      {
        labelEn: "Curated World Seeds Explorer",
        labelAr: "دليل السيدات والعوالم الأسطورية",
        descEn: "1-Click Copy Spectacular Spawn & Survival Seeds",
        descAr: "استكشف وانسخ أفضل بذور عوالم ماين كرافت",
        href: "/seeds",
        icon: Compass,
        badge: "Top Seeds",
        color: "text-amber-400"
      },
      {
        labelEn: "Universal Servers Hub",
        labelAr: "سيرفرات اللعب والـ PvP",
        descEn: "Hypixel, Minemen, BlockMC & Server Pinger",
        descAr: "قائمة السيرفرات المعتمدة وفحص حالة الاتصال",
        href: "/servers",
        icon: Globe,
        color: "text-indigo-400"
      },
      {
        labelEn: "Global Hall of Fame & Leaderboards",
        labelAr: "لوحة الشرف والصدارة العالمية",
        descEn: "Top PvP, Speedrun & Contribution Rankings",
        descAr: "تصنيفات اللاعبين والمطورين في المنظومة",
        href: "/leaderboards",
        icon: Trophy,
        color: "text-yellow-400"
      }
    ]
  },
  {
    id: "support",
    titleEn: "Support & Deployment Guides",
    titleAr: "الدعم وقاعدة المعرفة",
    icon: HelpCircle,
    accentColor: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
    items: [
      {
        labelEn: "Dedicated Server Deployment Guide",
        labelAr: "دليل تشغيل سيرفرك الخاص",
        descEn: "Free In-Game WAN & 24/7 Dedicated Server Guide",
        descAr: "شرح شامل لتشغيل السيرفر بأعلى سرعة وبدون لاغ",
        href: "/server-guide",
        icon: Server,
        badge: "Hosting",
        color: "text-emerald-400"
      },
      {
        labelEn: "Frequently Asked Questions (FAQ)",
        labelAr: "الأسئلة الشائعة وحلول المشاكل",
        descEn: "Comprehensive Knowledgebase & Quick Fixes",
        descAr: "إجابات وحلول سريعة لأهم الاستفسارات التقنية",
        href: "/faq",
        icon: HelpCircle,
        color: "text-cyan-400"
      },
      {
        labelEn: "Privacy Policy & Zero-Telemetry",
        labelAr: "سياسة الخصوصية وانعدام التتبع",
        descEn: "100% Client-Side Privacy Guarantee",
        descAr: "ضمان الخصوصية التامة وعدم جمع أي بيانات",
        href: "/privacy",
        icon: Lock,
        color: "text-blue-400"
      },
      {
        labelEn: "Terms of Service & Open-Source EULA",
        labelAr: "شروط الخدمة واتفاقية الاستخدام",
        descEn: "Free Open-Source Software Agreement",
        descAr: "ترخيص الاستخدام المجاني والمفتوح المصدر",
        href: "/terms",
        icon: FileText,
        color: "text-slate-400"
      },
      {
        labelEn: "Cookie Policy & Local Storage",
        labelAr: "سياسة الكوكيز والتخزين المحلي",
        descEn: "Zero-Tracking Local Preference Storage",
        descAr: "تخزين التفضيلات محلياً على جهازك فقط",
        href: "/cookies",
        icon: Cookie,
        color: "text-amber-400"
      }
    ]
  }
];

export function SidebarNavigation() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";
  const pathname = usePathname();

  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const activeItemRef = useRef<HTMLAnchorElement>(null);

  // Close on route change & notify quick dock
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  useEffect(() => {
    window.dispatchEvent(new CustomEvent("sir_sidemenu_state", { detail: { open: isOpen } }));
  }, [isOpen]);

  // Listen to custom open event from Navbar or anywhere
  useEffect(() => {
    const handleOpen = () => setIsOpen(true);
    window.addEventListener("sir_open_sidemenu", handleOpen);
    return () => window.removeEventListener("sir_open_sidemenu", handleOpen);
  }, []);

  // Auto-scroll to active tab when sidebar opens
  useEffect(() => {
    if (isOpen && activeItemRef.current) {
      const timer = setTimeout(() => {
        activeItemRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "center"
        });
      }, 180);
      return () => clearTimeout(timer);
    }
  }, [isOpen, pathname]);

  // Real-time search filter
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return ORGANIZED_CATEGORIES;
    const q = searchQuery.toLowerCase().trim();
    
    return ORGANIZED_CATEGORIES.map(cat => {
      const matchingItems = cat.items.filter(item => 
        item.labelEn.toLowerCase().includes(q) ||
        item.labelAr.toLowerCase().includes(q) ||
        item.href.toLowerCase().includes(q) ||
        (item.descEn && item.descEn.toLowerCase().includes(q)) ||
        (item.descAr && item.descAr.toLowerCase().includes(q))
      );
      return {
        ...cat,
        items: matchingItems
      };
    }).filter(cat => cat.items.length > 0);
  }, [searchQuery]);

  const totalRoutesCount = useMemo(() => {
    return ORGANIZED_CATEGORIES.reduce((acc, c) => acc + c.items.length, 0);
  }, []);

  return (
    <>



      {/* Slide-out Full Modern Sidebar Drawer */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 overflow-hidden">
            {/* Backdrop Blur */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="absolute inset-0 bg-black/75 backdrop-blur-md"
            />

            {/* Sidebar Panel */}
            <motion.aside
              initial={{ x: isAr ? "100%" : "-100%", opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: isAr ? "100%" : "-100%", opacity: 0 }}
              transition={{ type: "spring", stiffness: 320, damping: 30 }}
              className={`absolute top-0 ${isAr ? "right-0" : "left-0"} h-full w-[88vw] max-w-[380px] sm:w-96 bg-white dark:bg-[#080c14]/98 border-r border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col z-10 backdrop-blur-2xl`}
            >
              {/* Drawer Header */}
              <div className="p-4 sm:p-5 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between bg-slate-50/90 dark:bg-[#05080e]/95 shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-500 p-0.5 flex items-center justify-center shadow-lg">
                    <div className="w-full h-full bg-white dark:bg-[#080c14] rounded-[14px] flex items-center justify-center p-1 overflow-hidden">
                      <img src="/sir-logo.png" alt="SIR Logo" className="w-full h-full object-contain" />
                    </div>
                  </div>
                  <div>
                    <h2 className="text-xs sm:text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                      <span>SIR ECOSYSTEM</span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 border border-cyan-500/30">
                        v1.0.0
                      </span>
                    </h2>
                    <p className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                      {isAr ? "دليل التنقل الشامل للمنظومة" : "Universal Ecosystem Navigation"}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 rounded-xl bg-slate-200/80 dark:bg-slate-800/60 hover:bg-slate-300 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-300/60 dark:border-slate-700/40 transition-all cursor-pointer shadow-sm"
                  title="Close Sidebar"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Quick Route Search Bar */}
              <div className="px-4 pt-3 pb-1 shrink-0 bg-slate-50/50 dark:bg-transparent">
                <div className="relative">
                  <Search className={`w-3.5 h-3.5 text-slate-500 dark:text-slate-400 absolute ${isAr ? "right-3" : "left-3"} top-1/2 -translate-y-1/2 pointer-events-none z-10`} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder={isAr ? "ابحث عن أي قسم أو صفحة..." : "Quick filter 20+ ecosystem routes..."}
                    className={`w-full ${isAr ? "pr-8 pl-7" : "pl-8 pr-7"} py-2 rounded-xl bg-slate-100 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200 text-xs outline-none focus:border-cyan-500 dark:focus:border-cyan-400 font-mono transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600`}
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery("")}
                      className={`absolute ${isAr ? "left-2.5" : "right-2.5"} top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500 hover:text-slate-800 dark:hover:text-white text-xs`}
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>

              {/* Scrollable Categories & Organized Links */}
              <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-5 custom-scrollbar scroll-smooth">
                {filteredCategories.map((cat) => {
                  const CatIcon = cat.icon;
                  return (
                    <div key={cat.id} className="space-y-2">
                      
                      {/* Organized Category Header */}
                      <div className="px-2 py-1 flex items-center justify-between border-b border-slate-200 dark:border-slate-800/60 pb-1.5">
                        <div className="flex items-center gap-2">
                          <div className={`p-1 rounded-lg border ${cat.accentColor}`}>
                            <CatIcon className="w-3 h-3" />
                          </div>
                          <span className="text-[10px] font-black tracking-wider uppercase text-slate-500 dark:text-slate-400">
                            {isAr ? cat.titleAr : cat.titleEn}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-slate-400 dark:text-slate-600 font-bold">
                          {cat.items.length}
                        </span>
                      </div>

                      {/* Category Links */}
                      <div className="space-y-1">
                        {cat.items.map((item, itemIdx) => {
                          const Icon = item.icon;
                          const isActive = pathname === item.href || (item.href !== "/" && item.href !== "/#downloads" && pathname.startsWith(item.href));

                          return (
                            <Link
                              key={itemIdx}
                              ref={isActive ? activeItemRef : undefined}
                              href={item.href}
                              onClick={() => setIsOpen(false)}
                              className={`flex items-center justify-between px-3 py-2.5 rounded-2xl text-xs font-bold transition-all group ${
                                isActive
                                  ? "bg-cyan-50 dark:bg-cyan-950/50 border border-cyan-400 dark:border-cyan-500/60 shadow-md dark:shadow-[0_0_20px_rgba(0,229,255,0.15)] ring-1 ring-cyan-400/40"
                                  : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white border border-transparent"
                              }`}
                            >
                              <div className="flex items-center gap-2.5 min-w-0">
                                <div className={`p-1.5 rounded-xl border transition-transform shrink-0 ${
                                  isActive
                                    ? "bg-cyan-500 text-slate-950 border-cyan-400 shadow-sm"
                                    : `bg-slate-100 dark:bg-[#0b101c] border-slate-200 dark:border-slate-800 ${item.color} group-hover:scale-105`
                                }`}>
                                  <Icon className="w-3.5 h-3.5" />
                                </div>
                                <div className="truncate">
                                  <span className={`block truncate text-xs font-black tracking-tight ${
                                    isActive
                                      ? "text-slate-950 dark:text-cyan-200 drop-shadow-[0_0_8px_rgba(0,229,255,0.2)]"
                                      : "text-slate-700 dark:text-slate-200 group-hover:text-slate-950 dark:group-hover:text-white"
                                  }`}>
                                    {isAr ? item.labelAr : item.labelEn}
                                  </span>
                                  {(item.descEn || item.descAr) && (
                                    <span className={`text-[10px] block truncate font-medium ${
                                      isActive
                                        ? "text-slate-700 dark:text-slate-300"
                                        : "text-slate-500 dark:text-slate-400 group-hover:text-slate-700 dark:group-hover:text-slate-300"
                                    }`}>
                                      {isAr ? item.descAr : item.descEn}
                                    </span>
                                  )}
                                </div>
                              </div>

                              {item.badge && (
                                <span className={`text-[10px] font-mono font-black px-2.5 py-0.5 rounded-full transition-all shrink-0 ml-2 shadow-sm ${
                                  isActive 
                                    ? "bg-cyan-500 text-slate-950 border border-cyan-300 shadow-[0_0_10px_rgba(0,229,255,0.4)]" 
                                    : "bg-slate-200 dark:bg-[#070b14] text-slate-700 dark:text-cyan-400 border border-slate-300 dark:border-slate-800 group-hover:bg-cyan-500 group-hover:text-slate-950 group-hover:border-cyan-400 group-hover:shadow-[0_0_10px_rgba(0,229,255,0.35)]"
                                }`}>
                                  {item.badge}
                                </span>
                              )}
                            </Link>
                          );
                        })}
                      </div>

                    </div>
                  );
                })}

                {filteredCategories.length === 0 && (
                  <div className="py-12 text-center text-slate-400 dark:text-slate-500 space-y-2">
                    <Search className="w-8 h-8 text-slate-400 dark:text-slate-600 mx-auto" />
                    <p className="text-xs font-mono">{isAr ? "لا توجد نتائج مطابقة لبحثك" : "No matching routes found"}</p>
                  </div>
                )}
              </div>

              {/* Drawer Footer */}
              <div className="p-3 sm:p-4 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#05080e]/95 shrink-0 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
                <a
                  href="https://linktr.ee/sir.ahmed"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-cyan-600 dark:text-cyan-400 hover:underline font-bold"
                >
                  <span>SIR Ahmed</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
                <span className="text-[10px] font-mono text-slate-400 dark:text-slate-500">{totalRoutesCount} Verified Routes</span>
              </div>
            </motion.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
