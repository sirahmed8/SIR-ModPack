"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState } from "react";
import { useEcosystem } from "@/lib/context";
import { 
  Server, 
  Globe, 
  Check, 
  Copy, 
  ExternalLink, 
  Terminal, 
  ShieldCheck, 
  Sparkles, 
  Zap, 
  Gamepad2, 
  ArrowRight, 
  ArrowLeft,
  HelpCircle,
  Cpu,
  KeyRound,
  Radio,
  Wifi
} from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";

export default function ServerGuidePage() {
  const { lang } = useEcosystem();
  const [copiedStep, setCopiedStep] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStep(id);
    setTimeout(() => setCopiedStep(null), 2000);
  };

  const isAr = lang === "ar";

  return (
    <AuthGate featureName="Server Hosting Hub" featureNameAr="دليل واستضافة الخوادم">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-sm">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <Server className="w-3.5 h-3.5" />
            <span>{isAr ? "دليل استضافة العوالم والسيرفرات المجانية" : "Official World & Server Hosting Guide"}</span>
          </span>
        </div>

        {/* Header Title */}
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <h1 className="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white tracking-tight leading-tight">
            {isAr ? (
              <>
                طريقتان للعب مع أصدقائك في أي مكان بالعالم عبر <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-cyan-500 dark:from-emerald-400 dark:to-cyan-400">Playit.gg & In-Game WAN</span>
              </>
            ) : (
              <>
                Two Ways to Play with Friends Worldwide via <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-cyan-500 dark:from-emerald-400 dark:to-cyan-400">Playit.gg & In-Game WAN</span>
              </>
            )}
          </h1>
          <p className="text-sm sm:text-base text-slate-600 dark:text-slate-400 leading-relaxed">
            {isAr 
              ? "دليل شامل لاختيار الطريقة الأنسب: استضافة سريعة داخل اللعبة لأي صديق في العالم بنقرة واحدة، أو تشغيل سيرفر مخصص 24/7 بعنوان دائم مجاناً."
              : "Comprehensive guide to playing with friends anywhere in the world: instant 1-click in-game global hosting or 24/7 dedicated server hosting with Playit.gg."
            }
          </p>
        </div>

        {/* Quick Decision Comparison: 1-Click In-Game Global WAN vs 24/7 Dedicated Server */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Method 1: In-Game Global WAN (e4mc) */}
          <div className="p-6 rounded-3xl bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/30 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-700 dark:text-cyan-400 font-black text-sm">
                <Gamepad2 className="w-5 h-5" />
                <span>{isAr ? "1. استضافة مباشرة من داخل اللعبة (WLAN / WAN)" : "1. 1-Click In-Game Global World Host"}</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-cyan-500/20 text-cyan-700 dark:text-cyan-300">NO SETUP NEEDED</span>
            </div>
            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
              {isAr 
                ? "إذا كنت تلعب في عالمك السنجل بلاير وتريد أن يدخل أصدقاؤك (حتى لو كانوا في منازل أو دول أخرى):"
                : "If you are playing in your singleplayer world and want friends anywhere in the world to join you immediately:"
              }
            </p>
            <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-cyan-200 dark:border-cyan-800/60 space-y-2 text-xs font-mono">
              {isAr ? (
                <>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">1. اضغط <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-cyan-600 dark:text-cyan-400">Esc</kbd> داخل اللعبة</div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">2. اختر <strong className="text-emerald-600 dark:text-emerald-400">Open to LAN</strong></div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">3. سيقوم مود <strong className="text-cyan-500">e4mc</strong> المدمج بإنشاء رابط عام فوري في الشات</div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px]">4. ينسخ صديقك الرابط في Direct Connect ويدخل فوراً!</div>
                </>
              ) : (
                <>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">1. Press <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-cyan-600 dark:text-cyan-400">Esc</kbd> in-game</div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">2. Click <strong className="text-emerald-600 dark:text-emerald-400">Open to LAN</strong></div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">3. Built-in <strong className="text-cyan-500">e4mc</strong> engine generates an instant global tunnel in chat</div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px]">4. Your friend pastes the link into Direct Connect and joins!</div>
                </>
              )}
            </div>
          </div>

          {/* Method 2: Dedicated Server Host Studio (Playit.gg) */}
          <div className="p-6 rounded-3xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-black text-sm">
                <Server className="w-5 h-5" />
                <span>{isAr ? "2. تطبيق استضافة سيرفر مخصص 24/7" : "2. Dedicated Server Host Manager 24/7"}</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-500/20 text-emerald-700 dark:text-emerald-300">PERMANENT IP</span>
            </div>
            <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">
              {isAr 
                ? "إذا أردت تشغيل سيرفر دائم ومستقل بمودات أو بلوجينات بدون أن تبقي لعبتك مفتوحة طوال الوقت مع عنوان ثابت دائم:"
                : "If you want to run a dedicated 24/7 server with mods and automated backups without keeping your game client open:"
              }
            </p>
            <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-emerald-200 dark:border-emerald-800/60 space-y-2 text-xs font-mono">
              {isAr ? (
                <>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">1. افتح <strong className="text-cyan-500">SIR ModPack.exe</strong> ثم اختر وضع السيرفر</div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">2. اربط حسابك عبر <strong className="text-emerald-500">Playit.gg</strong></div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">3. احصل على عنوان دائم مثل <code className="text-cyan-400 font-bold">xxx.tun.ply.gg</code></div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px]">4. اضغط Start Server واستمتع بسيرفر 24/7 سريع جداً!</div>
                </>
              ) : (
                <>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">1. Open <strong className="text-cyan-500">SIR ModPack.exe</strong> and select Server Mode</div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">2. Link your free account via <strong className="text-emerald-500">Playit.gg</strong></div>
                  <div className="text-slate-800 dark:text-slate-200 font-bold">3. Receive your permanent custom domain like <code className="text-cyan-400 font-bold">xxx.tun.ply.gg</code></div>
                  <div className="text-slate-600 dark:text-slate-400 text-[11px]">4. Click Start Server and enjoy 24/7 high-speed hosting!</div>
                </>
              )}
            </div>
          </div>
        </div>

        {/* STEP-BY-STEP PLAYIT.GG DEDICATED SERVER GUIDE */}
        <div className="space-y-6">
          
          {/* STEP 1: Launch SIR Server Host Studio */}
          <motion.div initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 text-xs font-black border border-cyan-300 dark:border-cyan-500/30 shadow-xs">
                {isAr ? "الخطوة الأولى" : "Step 1"}
              </span>
              <span className="text-xs font-mono text-slate-500 dark:text-slate-400 font-bold">Desktop App</span>
            </div>
            <h3 className="text-xl font-black text-slate-900 dark:text-white">
              {isAr ? "1. افتح SIR ModPack واختر وضع السيرفر" : "1. Open SIR ModPack and choose Server mode"}
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {isAr 
                ? "افتح SIR ModPack.exe من الاختصار ثم شغّل وضع السيرفر."
                : "Open SIR ModPack.exe from the shortcut and start Server mode."
              }
            </p>
          </motion.div>

          {/* STEP 2: Open Official Playit.gg Portal */}
          <motion.div initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900/80 border border-emerald-300 dark:border-emerald-500/40 ring-1 ring-emerald-400/20 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 text-xs font-black border border-emerald-300 dark:border-emerald-500/30 shadow-xs">
                {isAr ? "الخطوة الثانية" : "Step 2"}
              </span>
              <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold">Official Portal</span>
            </div>
            <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
              <Globe className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <span>{isAr ? "2. سجل دخولك على موقع Playit.gg الرسمي وانسخ عنوانك" : "2. Open Playit.gg & Copy Your Assigned Public Domain"}</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {isAr 
                ? "افتح موقع Playit.gg الرئيسي وسجل دخولك بحسابك المجاني. في تبويب (Tunnels)، ستجد عنوان السيرفر المخصص لك (مثلاً: sir-community.tun.ply.gg:25565 أو myserver.playit.gg:25565):"
                : "Open the official Playit.gg website and sign in with your free account. Under your Tunnels dashboard, you will find your assigned public domain (e.g. sir-community.tun.ply.gg:25565 or myserver.playit.gg:25565):"
              }
            </p>

            <div className="pt-2 flex flex-col sm:flex-row gap-3">
              <a
                href="https://playit.gg"
                target="_blank"
                rel="noreferrer"
                className="py-3 px-6 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-md shadow-emerald-500/20 cursor-pointer"
              >
                <span>{isAr ? "🌐 فتح موقع Playit.gg الرئيسي ↗" : "🌐 Open Official Playit.gg Website ↗"}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>

              <a
                href="https://playit.gg/account/tunnels"
                target="_blank"
                rel="noreferrer"
                className="py-3 px-6 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-md shadow-cyan-500/20 cursor-pointer"
              >
                <span>{isAr ? "🔗 لوحة إدارة العناوين (Tunnels Dashboard) ↗" : "🔗 Open Tunnels Dashboard ↗"}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          </motion.div>

          {/* STEP 3: Paste and Save Address in Server App */}
          <motion.div initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 text-xs font-black border border-cyan-300 dark:border-cyan-500/30 shadow-xs">
                {isAr ? "الخطوة الثالثة" : "Step 3"}
              </span>
              <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 font-bold">Auto-Saved</span>
            </div>
            <h3 className="text-xl font-black text-slate-900 dark:text-white">
              {isAr ? "3. الصق العنوان في خانة الربط داخل التطبيق" : "3. Paste & Save Your Domain in SIR Server Manager"}
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {isAr 
                ? "الصق العنوان الذي نسخته (مثلاً: sir-community.tun.ply.gg:25565) في خانة (Playit Domain) داخل تبويب Playit.gg واضغط حفظ. سيتم اعتماده كعنوان مشاركة دائم!"
                : "Paste your assigned domain (e.g. sir-community.tun.ply.gg:25565) into the Playit domain field inside the app and click Save. It will be remembered forever."
              }
            </p>

            <div className="p-4 rounded-2xl bg-cyan-50/70 dark:bg-slate-950 border border-cyan-300 dark:border-cyan-500/40 font-mono text-xs text-cyan-800 dark:text-cyan-300 flex items-center justify-between shadow-xs">
              <span className="font-bold">Example: sir-community.tun.ply.gg:25565</span>
              <button
                type="button"
                onClick={() => copyToClipboard("sir-community.tun.ply.gg:25565", "example-ip")}
                className="px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black flex items-center gap-1.5 cursor-pointer shadow-sm shadow-cyan-500/20 transition-all"
              >
                {copiedStep === "example-ip" ? <Check className="w-3.5 h-3.5 stroke-[3]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedStep === "example-ip" ? (isAr ? "تم النسخ!" : "Copied!") : (isAr ? "نسخ" : "Copy")}</span>
              </button>
            </div>
          </motion.div>

          {/* STEP 4: Start Server & Invite Friends */}
          <motion.div initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 text-xs font-black border border-emerald-300 dark:border-emerald-500/30 shadow-xs">
                {isAr ? "الخطوة الرابعة" : "Step 4"}
              </span>
              <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold">Ready to Play</span>
            </div>
            <h3 className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              <span>{isAr ? "4. اضغط 🚀 تشغيل السيرفر وشارك العنوان مع أصدقائك" : "4. Click 🚀 Start Server & Share Address with Friends"}</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {isAr 
                ? "اضغط على زر (🚀 Start Server). سيتم تشغيل السيرفر المخصص متعدد الأنوية مع خيارات الذاكرة التي حددتها. يستطيع أصدقاؤك الدخول فوراً عبر العنوان على الحسابات المكركة والرسمية بدون أي لاغ!"
                : "Click '🚀 Start Server'. Your dedicated multi-threaded host will boot with your dedicated RAM settings. Friends can connect instantly from anywhere in the world with zero lag!"
              }
            </p>
          </motion.div>

        </div>

        {/* Connected Ecosystem Hub */}
        <ConnectedFeaturesHub currentPath="/server-guide" />

      </div>
    </div>
    </AuthGate>);
}