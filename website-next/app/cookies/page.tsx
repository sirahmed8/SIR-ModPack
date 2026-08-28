"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Cookie, ArrowLeft, ArrowRight, HardDrive, Trash2, Zap, Shield, CheckCircle2, Sparkles, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";
import { getStorageUsage, pruneExpiredCaches, CookieConsentState } from "@/lib/storage";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";

export default function CookiePolicyPage() {
  const { lang, perfMode, togglePerfMode, cookieConsent, setConsent } = useEcosystem();
  const isAr = lang === "ar";

  const [usage, setUsage] = useState({ usedKb: 0, itemsCount: 0, cacheRatio: "0%" });
  const [prunedMsg, setPrunedMsg] = useState<string | null>(null);

  const refreshUsage = () => {
    setUsage(getStorageUsage());
  };

  useEffect(() => {
    refreshUsage();
  }, []);

  const handlePrune = () => {
    const count = pruneExpiredCaches();
    refreshUsage();
    setPrunedMsg(isAr ? `✓ تم تنظيف ${count} عناصر منتهية الصلاحية بنجاح!` : `✓ Pruned ${count} expired cache items!`);
    setTimeout(() => setPrunedMsg(null), 3000);
  };

  const handleClearAll = () => {
    if (confirm(isAr ? "هل أنت متأكد من مسح جميع بيانات التخزين المؤقت والذاكرة المحلية؟" : "Are you sure you want to clear all local storage and cache?")) {
      localStorage.clear();
      refreshUsage();
      alert(isAr ? "تم مسح الذاكرة المحلية بنجاح." : "Local storage cleared successfully.");
      window.location.reload();
    }
  };

  const toggleConsentKey = (key: keyof CookieConsentState) => {
    if (key === "essential" || key === "timestamp") return;
    const next: CookieConsentState = {
      ...cookieConsent,
      [key]: !cookieConsent[key],
      timestamp: Date.now()
    };
    setConsent(next);
  };

  const storageMatrix = [
    {
      key: "sir_lang",
      type: "Cookie / LocalStorage",
      purpose: isAr ? "حفظ لغة العرض المختارة (العربية / الإنجليزية)" : "Stores selected interface language (ar/en)",
      lifespan: isAr ? "365 يوماً" : "365 Days"
    },
    {
      key: "sir_theme",
      type: "Cookie / LocalStorage",
      purpose: isAr ? "تفضيل الوضع المظلم أو الفاتح" : "Stores visual dark/light theme preference",
      lifespan: isAr ? "365 يوماً" : "365 Days"
    },
    {
      key: "sir_perf_mode",
      type: "Cookie / LocalStorage",
      purpose: isAr ? "تفعيل وضع توفير الموارد (Eco Mode) أو السينمائي" : "Hardware Eco Performance / Cinematic Mode",
      lifespan: isAr ? "365 يوماً" : "365 Days"
    },
    {
      key: "sir_linked_minecraft_user",
      type: "LocalStorage",
      purpose: isAr ? "تخزين اسم اللاعب وسكن الـ 3D محلياً لسرعة 0ms" : "Local cache for player IGN & 3D avatar",
      lifespan: isAr ? "دائم حتى الحذف" : "Persistent"
    },
    {
      key: "sir_cache_*",
      type: "LocalStorage (TTL SWR)",
      purpose: isAr ? "الذاكرة المؤقتة للمودات والأخبار وحالة الخوادم" : "Stale-While-Revalidate cache for mods, news, server status",
      lifespan: isAr ? "5 - 30 دقيقة" : "5 - 30 Minutes"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#070a10] text-slate-900 dark:text-white pt-14 pb-24 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs font-bold text-slate-700 dark:text-zinc-300 hover:text-cyan-600 dark:hover:text-white hover:border-cyan-500/50 transition-all shadow-sm cursor-pointer"
          >
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-400 border border-amber-300 dark:border-amber-500/30 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-xs">
            <Cookie className="w-3.5 h-3.5" />
            <span>{isAr ? "إدارة التخزين والكوكيز" : "Storage & Cookies"}</span>
          </span>
        </div>

        {/* Header Hero */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 dark:text-white">
            {isAr ? "الشفافية الكاملة والتحكم في التخزين" : "Local Storage Transparency & Cookie Controls"}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
            {isAr
              ? "نستخدم الذاكرة المحلية والملفات التقنية لتسريع تصفحك وتخصيص تجربتك بدون أي تتبع إعلاني أو بيع للبيانات."
              : "Zero ad tracking. We leverage high-speed local caching to achieve instantaneous 0ms page transitions."}
          </p>
        </div>

        {/* Live Storage Usage Diagnostic Card */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#0d131f] border border-slate-200 dark:border-slate-800 shadow-xl space-y-6 relative overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-cyan-100 dark:bg-cyan-500/10 border border-cyan-300 dark:border-cyan-500/30 flex items-center justify-center text-cyan-600 dark:text-cyan-400 shadow-xs">
                <HardDrive className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span>{isAr ? "مؤشر استخدام الذاكرة المحلية" : "Live LocalStorage Usage"}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border border-emerald-300 dark:border-emerald-800/40 font-mono font-bold">Optimal</span>
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  {isAr ? "تحليل مباشر لاستهلاك المتصفح والذاكرة المؤقتة" : "Real-time client cache telemetry"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handlePrune}
                className="px-4 py-2 rounded-xl bg-cyan-50 dark:bg-cyan-500/15 hover:bg-cyan-100 dark:hover:bg-cyan-500/25 text-cyan-700 dark:text-cyan-400 border border-cyan-300 dark:border-cyan-500/40 text-xs font-bold flex items-center gap-1.5 transition-all active:scale-95 cursor-pointer shadow-xs"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>{isAr ? "تنظيف المنتهي" : "Prune Expired"}</span>
              </button>

              <button
                onClick={handleClearAll}
                className="px-4 py-2 rounded-xl bg-rose-50 dark:bg-rose-500/15 hover:bg-rose-100 dark:hover:bg-rose-500/25 text-rose-700 dark:text-rose-400 border border-rose-300 dark:border-rose-500/40 text-xs font-bold flex items-center gap-1.5 transition-all active:scale-95 cursor-pointer shadow-xs"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>{isAr ? "مسح الكل" : "Clear All"}</span>
              </button>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-xs text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "المساحة المستخدمة" : "Storage Consumed"}</span>
              <span className="text-2xl font-black text-cyan-600 dark:text-cyan-400 font-mono mt-1 block">{usage.usedKb} KB</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-xs text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "عدد العناصر المخزنة" : "Stored Keys"}</span>
              <span className="text-2xl font-black text-amber-600 dark:text-amber-400 font-mono mt-1 block">{usage.itemsCount} Keys</span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 shadow-xs">
              <span className="text-xs text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "نسبة الذاكرة المؤقتة" : "Cache Ratio"}</span>
              <span className="text-2xl font-black text-emerald-600 dark:text-emerald-400 font-mono mt-1 block">{usage.cacheRatio}</span>
            </div>
          </div>

          {prunedMsg && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 rounded-xl bg-emerald-100 dark:bg-emerald-950/40 border border-emerald-300 dark:border-emerald-500/40 text-xs text-emerald-800 dark:text-emerald-300 text-center font-bold"
            >
              {prunedMsg}
            </motion.div>
          )}
        </div>

        {/* Interactive Personalization & Storage Controls */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#0d131f] border border-slate-200 dark:border-slate-800 shadow-xl space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-amber-100 dark:bg-amber-500/10 border border-amber-300 dark:border-amber-500/30 flex items-center justify-center text-amber-600 dark:text-amber-400 shadow-xs">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">{isAr ? "تخصيص الذاكرة والتجربة الشخصية" : "Interactive Personalization Matrix"}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">{isAr ? "تحكم في الميزات المخزنة على جهازك" : "Toggle active client-side features"}</p>
            </div>
          </div>

          <div className="space-y-3">
            {/* Toggle 1: High Speed Cache */}
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-4 shadow-xs">
              <div className="flex items-center gap-3">
                <HardDrive className="w-5 h-5 text-cyan-600 dark:text-cyan-400 shrink-0" />
                <div>
                  <span className="text-sm font-bold text-slate-900 dark:text-slate-100 block">{isAr ? "الذاكرة المؤقتة فائقة السرعة (SWR Cache)" : "High-Speed Stale-While-Revalidate Cache"}</span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">{isAr ? "تسريع تصفح المودات والشيدرات إلى 0ms بدون استهلاك إنترنت" : "Pre-caches catalog and static stats to eliminate server wait times"}</span>
                </div>
              </div>
              <button
                onClick={() => toggleConsentKey("cache")}
                className={`px-4 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  cookieConsent.cache 
                    ? "bg-cyan-500 text-slate-950 font-black shadow-md shadow-cyan-500/20" 
                    : "bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-400 border border-slate-200 dark:border-slate-700"
                }`}
              >
                {cookieConsent.cache ? (isAr ? "مفعل" : "Enabled") : (isAr ? "معطل" : "Disabled")}
              </button>
            </div>

            {/* Toggle 2: Eco Performance Mode */}
            <div className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-4 shadow-xs">
              <div className="flex items-center gap-3">
                <Zap className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                <div>
                  <span className="text-sm font-bold text-slate-900 dark:text-slate-100 block">{isAr ? "وضع الأداء الاقتصادي (Eco Mode)" : "Hardware Eco Performance Mode"}</span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">{isAr ? "تقليل تأثيرات الزجاج والبلور للأجهزة الضعيفة لتوفير الطاقة" : "Reduces GPU blur shaders and floating effects for high 120+ FPS responsiveness"}</span>
                </div>
              </div>
              <button
                onClick={togglePerfMode}
                className={`px-4 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  perfMode === 'eco' 
                    ? "bg-emerald-500 text-slate-950 font-black shadow-md shadow-emerald-500/20" 
                    : "bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
                }`}
              >
                {perfMode === 'eco' ? (isAr ? "مفعل (Eco)" : "Active (Eco)") : (isAr ? "سينمائي" : "Cinematic")}
              </button>
            </div>

          </div>
        </div>

        {/* Detailed Storage Keys Table */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#0d131f] border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
            <span>{isAr ? "جدول المفاتيح المستخدمة في التخزين" : "Complete Storage Matrix"}</span>
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 font-mono font-bold">
                  <th className="py-3 px-4">Storage Key</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Purpose</th>
                  <th className="py-3 px-4">Lifespan</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
                {storageMatrix.map((item) => (
                  <tr key={item.key} className="hover:bg-cyan-50/80 dark:hover:bg-slate-800/50 transition-colors group">
                    <td className="py-3.5 px-4 font-mono font-bold text-cyan-700 dark:text-cyan-400">{item.key}</td>
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300 font-mono text-[11px]">{item.type}</td>
                    <td className="py-3.5 px-4 text-slate-800 dark:text-slate-200 font-medium">{item.purpose}</td>
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-400 font-mono font-bold">{item.lifespan}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Connected Ecosystem Hub */}
        <ConnectedFeaturesHub currentPath="/cookies" />

      </div>
    </div>
  );
}

