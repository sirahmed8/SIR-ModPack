"use client";

import React, { useState, useEffect } from "react";
import { useEcosystem } from "@/lib/context";
import { 
  Server, 
  Cpu, 
  Users, 
  HardDrive, 
  Sparkles, 
  Bell, 
  CheckCircle2, 
  Check, 
  Globe, 
  Gamepad2, 
  ShieldCheck, 
  Download, 
  Zap, 
  Layers,
  Cloud,
  ArrowRight
} from "lucide-react";
import { motion } from "framer-motion";

export function ServerHostingPortal() {
  const { t, dir, lang } = useEcosystem();
  const [waitlistJoined, setWaitlistJoined] = useState(false);
  const [notifPermission, setNotifPermission] = useState<NotificationPermission | "unsupported">("default");
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const isAr = lang === "ar";

  useEffect(() => {
    try {
      const saved = localStorage.getItem("sir_hosting_waitlist_joined");
      if (saved) {
        setWaitlistJoined(true);
      }
      if (typeof window !== "undefined" && "Notification" in window) {
        setNotifPermission(Notification.permission);
      } else {
        setNotifPermission("unsupported");
      }
    } catch {}
  }, []);

  const handleJoinWaitlist = async () => {
    setWaitlistJoined(true);
    try {
      localStorage.setItem("sir_hosting_waitlist_joined", "true");
    } catch {}

    if (typeof window !== "undefined" && "Notification" in window) {
      try {
        const permission = await Notification.requestPermission();
        setNotifPermission(permission);

        if (permission === "granted") {
          setStatusMessage(isAr ? "🔔 تم تفعيل الإشعارات! سننبهك فور إطلاق خوادم الكلاود." : "🔔 Push notifications enabled! You will be alerted the moment cloud nodes open.");
          new Notification("🚀 SIR Cloud Hosting Waitlist Confirmed!", {
            body: "You're on the priority waitlist. We will notify you instantly when NVMe Enterprise Cloud Nodes go live!",
            icon: "/sir-logo.png"
          });
        } else {
          setStatusMessage(isAr ? "✓ تم تسجيلك في قائمة الانتظار الأولوية!" : "✓ You are on the priority waitlist!");
        }
      } catch {
        setStatusMessage(isAr ? "✓ تم تسجيلك في قائمة الانتظار الأولوية!" : "✓ You are on the priority waitlist!");
      }
    } else {
      setStatusMessage(isAr ? "✓ تم تسجيلك في قائمة الانتظار الأولوية!" : "✓ You are on the priority waitlist!");
    }
  };

  return (
    <section id="server" className="py-20 lg:py-28 relative overflow-hidden">
      <div id="hosting" className="absolute top-0" />
      
      {/* Ambient Glows */}
      <div className="absolute top-1/3 -left-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/3 -right-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30 text-emerald-700 dark:text-[#38ef7d] text-xs font-bold uppercase tracking-wider mb-4 shadow-sm">
            <Server className="w-3.5 h-3.5" />
            <span>{isAr ? "منظومة استضافة السيرفرات المتكاملة" : "Multiplayer & Dedicated Server Suite"}</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white mb-4 tracking-tight leading-tight">
            {isAr ? "العب مع أصدقائك أو شغل سيرفرك الخاص" : "Host, Play & Provision Dedicated Minecraft Servers"}
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-gray-300 leading-relaxed">
            {isAr 
              ? "حلول استضافة متعددة تناسب اللعب السريع مع الأصدقاء، أو السيرفرات الاحترافية المنفصلة، أو عقد الكلاود السحابية فائقة السرعة."
              : "Complete hosting ecosystem covering instant in-game world sharing, standalone 24/7 dedicated server hosting, and upcoming ultra-fast cloud nodes."
            }
          </p>
        </div>

        {/* 3-Card Side-by-Side Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto mb-8 items-stretch">
          
          {/* ========================================================= */}
          {/* CARD 1: 🎮 IN-GAME 1-CLICK WORLD HOST                     */}
          {/* ========================================================= */}
          <motion.div 
            whileHover={{ y: -6 }}
            className="rounded-3xl p-7 sm:p-8 bg-slate-50/80 dark:bg-slate-900/60 border border-cyan-500/40 hover:border-cyan-400 shadow-xl backdrop-blur-xl flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 rounded-full text-xs font-black bg-cyan-500/10 text-cyan-600 dark:text-[#00e5ff] border border-cyan-500/30">
                  {isAr ? "مدمج داخل اللعبة • فوري" : "Built-in • Zero Setup"}
                </span>
                <span className="text-xs font-mono text-cyan-500 font-bold">1 - 8 {isAr ? "لاعبين" : "Players"}</span>
              </div>

              <h3 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                <Gamepad2 className="w-6 h-6 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                <span>{isAr ? "استضافة العوالم الفورية" : "In-Game 1-Click World Host"}</span>
              </h3>

              <p className="text-xs sm:text-sm text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                {isAr 
                  ? "افتح أي عالم سنجل بلاير لجميع أصدقائك خلال ثانيتين فقط عبر زر Open to LAN، وشارك رابط الدخول المباشر بدون إعدادات معقدة!"
                  : "Host your singleplayer world publicly in 2 seconds. Pause the game, click Open to LAN, and share your instant join link with friends!"
                }
              </p>

              <div className="space-y-3 mb-8">
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0 mt-0.5" />
                  <span>{isAr ? "افتح عالمك فوراً بدون مغادرة اللعبة (Esc ➔ Open to LAN)" : "Host your Singleplayer World instantly (Esc ➔ Open to LAN)"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0 mt-0.5" />
                  <span>{isAr ? "رابط دخول مباشر في الشات بدون فتح بورتات نهائياً" : "Instant direct join link in chat with zero port-forwarding"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0 mt-0.5" />
                  <span>{isAr ? "يدعم دخول الأصدقاء بالحسابات المكركة والرسمية" : "Supports both Cracked and Official Microsoft friends"}</span>
                </div>
              </div>
            </div>

            <div className="p-3.5 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-center mt-auto">
              <span className="text-xs font-black text-cyan-700 dark:text-[#00e5ff]">
                {isAr ? "✓ مفعل وجاهز داخل مودباك SIR Modern 26.2" : "✓ Pre-installed & active in SIR Modern 26.2 Profile"}
              </span>
            </div>
          </motion.div>

          {/* ========================================================= */}
          {/* CARD 2: ⚡ SIR SERVER HOST STUDIO APP                     */}
          {/* ========================================================= */}
          <motion.div 
            whileHover={{ y: -6 }}
            className="rounded-3xl p-7 sm:p-8 bg-slate-50/80 dark:bg-slate-900/60 border border-emerald-500/40 hover:border-emerald-400 shadow-xl backdrop-blur-xl flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 rounded-full text-xs font-black bg-emerald-500/10 text-emerald-600 dark:text-[#38ef7d] border border-emerald-500/30">
                  {isAr ? "تطبيق مثبت السيرفرات • اختياري" : "Standalone App • Optional"}
                </span>
                <span className="text-xs font-mono text-emerald-400 font-bold">20 - 100+ {isAr ? "لاعب" : "Players"}</span>
              </div>

              <h3 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                <Zap className="w-6 h-6 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                <span>{isAr ? "برنامج SIR Server Host Studio" : "SIR Server Host Studio App"}</span>
              </h3>

              <p className="text-xs sm:text-sm text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                {isAr 
                  ? "تطبيق مستقل اختياري مدمج مع مثبت SIR. شغل سيرفرات Fabric و Purpur قوية لأكثر من 20-100 لاعب مع أعلام تسريع الذاكرة Aikar."
                  : "Optional 1-click standalone server manager included in the SIR Installer. Run dedicated 20+ player Fabric & Purpur servers with Aikar's performance flags."
                }
              </p>

              <div className="space-y-3 mb-6">
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0 mt-0.5" />
                  <span>{isAr ? "نفق Playit.gg مدمج (عنوان IP عام دائم بدون فتح بورتات)" : "Integrated Playit.gg Tunnel (Instant permanent public IP with zero port-forwarding)"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0 mt-0.5" />
                  <span>{isAr ? "حفظ دائم لعنوان السيرفر (الصق عنوانك مرة واحدة ويحفظ تلقائياً)" : "Auto-Saved Public Address (Paste domain once, saved in server_config.json)"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0 mt-0.5" />
                  <span>{isAr ? "مدير صلاحيات OP وقواعد اللعبة والنسخ الاحتياطي التلقائي للعوالم" : "Live Player OP Manager, Game Rules Editor & Auto World Backups"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0 mt-0.5" />
                  <span>{isAr ? "أعلام الذاكرة Aikar's High-Performance G1GC مضبوطة مسبقاً" : "Aikar's High-Performance G1GC JVM memory flags pre-tuned"}</span>
                </div>
              </div>
            </div>

            <div className="space-y-3 mt-auto">
              <a
                href="/server-guide"
                className="w-full py-3.5 px-4 rounded-2xl bg-emerald-500 hover:bg-emerald-400 dark:bg-[#38ef7d] dark:hover:bg-[#4ef58f] text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer"
              >
                <span>{isAr ? "📖 دليل تشغيل السيرفر وربط Playit.gg ➔" : "📖 1-Click Server & Playit.gg Setup Guide ➔"}</span>
              </a>

              <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-center">
                <span className="text-[11px] font-bold text-emerald-700 dark:text-[#38ef7d]">
                  {isAr ? "يتيح لك مثبت SIR تثبيت التطبيق اختيارياً بنقرة واحدة" : "The SIR Installer allows you to optionally install Server Host Studio alongside the launcher."}
                </span>
              </div>
            </div>
          </motion.div>

          {/* ========================================================= */}
          {/* CARD 3: ☁️ SIR ENTERPRISE CLOUD NODE                      */}
          {/* ========================================================= */}
          <motion.div 
            whileHover={{ y: -6 }}
            className="rounded-3xl p-7 sm:p-8 bg-slate-50/80 dark:bg-slate-900/60 border border-purple-500/40 hover:border-purple-400 shadow-xl backdrop-blur-xl flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="px-3 py-1 rounded-full text-xs font-black bg-purple-500/10 text-purple-600 dark:text-[#c084fc] border border-purple-500/30">
                  {isAr ? "توفير خوادم الكلاود السحابية" : "Cloud Node Provisioning"}
                </span>
                <span className="text-xs font-mono text-purple-400 font-bold">
                  {isAr ? "قائمة الانتظار مفتوحة" : "Live Waitlist Open"}
                </span>
              </div>

              <h3 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                <Cloud className="w-6 h-6 text-purple-500 dark:text-[#c084fc] shrink-0" />
                <span>{isAr ? "خوادم SIR Enterprise السحابية" : "SIR Enterprise Cloud Node"}</span>
              </h3>

              <p className="text-xs sm:text-sm text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                {isAr 
                  ? "عقد سحابية فائقة السرعة مع أقراص NVMe وبنج منخفض للغاية، مهيأة مسبقاً مع تحسينات SIR للسيرفرات والنسخ الاحتياطي التلقائي وتكامل Cloudflare Tunnel."
                  : "Ultra-low ping NVMe cloud nodes with pre-installed SIR server-side optimizations, auto-backups, and Cloudflare Tunnel integration."
                }
              </p>

              <div className="space-y-3 mb-8">
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-purple-500 dark:text-[#c084fc] shrink-0 mt-0.5" />
                  <span>{isAr ? "تكامل Cloudflare Tunnel بدون الحاجة لفتح أي بورتات" : "Cloudflare Tunnel Zero Port-Forwarding"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-purple-500 dark:text-[#c084fc] shrink-0 mt-0.5" />
                  <span>{isAr ? "سعة تخزين NVMe Gen4 فائقة السرعة مع نسخ احتياطي آلي" : "NVMe Gen4 Storage + Automated Backups"}</span>
                </div>
                <div className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-purple-500 dark:text-[#c084fc] shrink-0 mt-0.5" />
                  <span>{isAr ? "مزامنة مودات وإعدادات سيرفر SIR بنقرة واحدة" : "1-Click SIR Server Modpack Sync"}</span>
                </div>
              </div>
            </div>

            <div className="space-y-3 mt-auto">
              <button
                type="button"
                onClick={handleJoinWaitlist}
                className={`w-full py-3.5 px-4 rounded-2xl font-black text-xs transition-all flex items-center justify-center gap-2 shadow-md cursor-pointer ${
                  waitlistJoined
                    ? "bg-emerald-500 text-slate-950 dark:bg-[#38ef7d] dark:text-[#06090e]"
                    : "bg-purple-500 hover:bg-purple-400 text-white dark:bg-[#a855f7] dark:hover:bg-[#c084fc] dark:text-white"
                }`}
              >
                {waitlistJoined ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{isAr ? "✓ تم الانضمام لقائمة الانتظار الأولوية" : "✓ On Priority Waitlist"}</span>
                  </>
                ) : (
                  <>
                    <Bell className="w-4 h-4" />
                    <span>{isAr ? "الانضمام لقائمة الانتظار الأولوية" : "Join Priority Waitlist"}</span>
                  </>
                )}
              </button>

              {statusMessage && (
                <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-center">
                  <span className="text-[11px] font-bold text-purple-700 dark:text-purple-300">
                    {statusMessage}
                  </span>
                </div>
              )}
            </div>
          </motion.div>

        </div>

      </div>
    </section>
  );
}
