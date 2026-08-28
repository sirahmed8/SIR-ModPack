"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useEcosystem } from "@/lib/context";
import { signInWithGoogle } from "@/lib/firebase";
import { Sparkles, Shield, ArrowRight, X, Zap, Swords, Layers, Globe } from "lucide-react";

export function WelcomeModal() {
  const { welcomeOpen, setWelcomeOpen, t, dir, lang } = useEcosystem();
  const isAr = lang === "ar";

  if (!welcomeOpen) return null;

  const handleGoogleSignIn = async () => {
    try {
      await signInWithGoogle();
      setWelcomeOpen(false);
    } catch (err) {
      console.error("Google sign-in error:", err);
      setWelcomeOpen(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
        {/* Backdrop with Blur */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setWelcomeOpen(false)}
          className="fixed inset-0 bg-black/80 backdrop-blur-xl transition-all"
        />

        {/* Modal Window Container */}
        <motion.div
          initial={{ scale: 0.92, opacity: 0, y: 24 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.92, opacity: 0, y: 24 }}
          transition={{ type: "spring", damping: 26, stiffness: 320 }}
          className="relative w-full max-w-2xl my-auto rounded-3xl bg-white dark:bg-[#090d16] border border-slate-200 dark:border-slate-800 shadow-[0_25px_60px_-15px_rgba(0,229,255,0.15)] p-5 sm:p-8 z-10 overflow-hidden"
        >
          {/* Subtle Ambient Radial Glow */}
          <div className="absolute -top-24 -right-24 w-60 h-60 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-60 h-60 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

          {/* Close Button */}
          <button
            onClick={() => setWelcomeOpen(false)}
            className="absolute top-4 right-4 sm:top-6 sm:right-6 p-2 rounded-2xl bg-slate-100 dark:bg-slate-800/80 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-700/60 transition-all cursor-pointer shadow-sm hover:scale-105 active:scale-95 z-20"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>

          {/* Header Badge */}
          <div className="flex items-center gap-2 mb-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-black rounded-full bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-[#00e5ff] border border-cyan-200 dark:border-cyan-500/30 shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-cyan-500 dark:text-[#00e5ff]" />
              <span>{t.welcome?.tag || (isAr ? "منظومة SIR الرسمية v1.0.0" : "Official SIR Ecosystem v1.0.0")}</span>
            </span>
          </div>

          {/* Title & Subtitle */}
          <h2 className="text-xl sm:text-3xl font-black tracking-tight text-slate-900 dark:text-white mb-2 leading-snug">
            {t.welcome?.title || (isAr ? "مرحباً بك في تجربة ماين كرافت القصوى" : "Welcome to the Ultimate Minecraft Experience")}
          </h2>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 mb-6 leading-relaxed">
            {t.welcome?.subtitle || (isAr ? "محرك ثنائي متقدم يجمع بين أحدث رسوميات 26.2 وسرعة استجابة 1.8.9 التنافسية مع شيدرز فائقة وتوافق تام." : "Dual-engine Minecraft platform combining 26.2 ultra graphics and 1.8.9 zero-latency esports performance with master shaders.")}
          </p>

          {/* Feature Highlights Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-6">
            <div className="p-3 rounded-2xl bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800/80 flex items-center gap-3">
              <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-500 border border-cyan-500/20 shrink-0">
                <Zap className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {t.welcome?.features?.f1 || (isAr ? "240+ مود مسرّع ومضبوط بعناية" : "240+ Calibrated High-FPS Mods")}
              </span>
            </div>

            <div className="p-3 rounded-2xl bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800/80 flex items-center gap-3">
              <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20 shrink-0">
                <Sparkles className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {t.welcome?.features?.f2 || (isAr ? "شيدرز SIR 2.0 (Extreme & Balanced)" : "Master SIR Shaders 2.0 Optical Lab")}
              </span>
            </div>

            <div className="p-3 rounded-2xl bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800/80 flex items-center gap-3">
              <div className="p-2 rounded-xl bg-purple-500/10 text-purple-500 border border-purple-500/20 shrink-0">
                <Swords className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {t.welcome?.features?.f3 || (isAr ? "محرك PvP 1.8.9 بأقصى استجابة" : "1.8.9 PvP Engine for Hypixel")}
              </span>
            </div>

            <div className="p-3 rounded-2xl bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800/80 flex items-center gap-3">
              <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shrink-0">
                <Globe className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {t.welcome?.features?.f4 || (isAr ? "دعم كامل للحسابات الرسمية والمكركة" : "Official Microsoft & Offline Skins Hub")}
              </span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
            <button
              onClick={handleGoogleSignIn}
              className="w-full sm:flex-1 flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 dark:bg-[#00e5ff] dark:hover:bg-[#38efff] text-white dark:text-[#06090e] font-black text-xs sm:text-sm shadow-lg shadow-cyan-500/20 active:scale-95 transition-all cursor-pointer"
            >
              <Shield className="w-4 h-4" />
              <span>{t.welcome?.googleCta || (isAr ? "تسجيل الدخول عبر Google" : "Continue with Google")}</span>
              <ArrowRight className={`w-4 h-4 ${dir === "rtl" ? "rotate-180" : ""}`} />
            </button>

            <button
              onClick={() => setWelcomeOpen(false)}
              className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:text-slate-900 dark:hover:text-white font-bold text-xs sm:text-sm active:scale-95 transition-all cursor-pointer"
            >
              {t.welcome?.guestCta || (isAr ? "المتابعة كزائر" : "Explore as Guest")}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
