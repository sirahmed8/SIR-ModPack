"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cookie, Zap, Shield, Settings2, Check, X, Sparkles, Volume2, HardDrive } from "lucide-react";
import { useEcosystem } from "@/lib/context";
import { getCookieConsent, saveCookieConsent, CookieConsentState, DEFAULT_CONSENT } from "@/lib/storage";

export function CookieConsent() {
  const { lang, perfMode, togglePerfMode, soundFx, toggleSoundFx } = useEcosystem();
  const isAr = lang === "ar";

  const [visible, setVisible] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState<CookieConsentState>(DEFAULT_CONSENT);

  useEffect(() => {
    const existing = getCookieConsent();
    if (!existing) {
      const timer = setTimeout(() => setVisible(true), 1200);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleAcceptAll = () => {
    saveCookieConsent(DEFAULT_CONSENT);
    setVisible(false);
  };

  const handleEssentialOnly = () => {
    const essentialOnly: CookieConsentState = {
      essential: true,
      preferences: false,
      cache: false,
      analytics: false,
      timestamp: Date.now()
    };
    saveCookieConsent(essentialOnly);
    setVisible(false);
  };

  const handleSaveCustom = () => {
    saveCookieConsent(preferences);
    setVisible(false);
    setShowSettings(false);
  };

  if (!visible) return null;

  return (
    <AnimatePresence>
      <div className="fixed bottom-4 sm:bottom-6 inset-x-4 sm:inset-x-auto sm:right-6 sm:max-w-md z-[9999] pointer-events-auto">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 30, scale: 0.95 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="relative overflow-hidden rounded-3xl bg-white/95 dark:bg-[#0d131f]/95 border border-slate-200 dark:border-slate-700/80 p-5 shadow-2xl backdrop-blur-2xl text-slate-900 dark:text-white space-y-4"
        >
          {/* Neon Glow Accents */}
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

          {/* Header */}
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0 shadow-lg shadow-amber-500/10">
                <Cookie className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <span>{isAr ? "الخصوصية والذاكرة السريعة" : "High-Speed Cache & Storage"}</span>
                  <span className="px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 text-[10px] font-mono border border-cyan-800/40 font-bold">v1.0.0</span>
                </h4>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">
                  {isAr ? "تسريع تصفح المنصة وحفظ تفضيلاتك محلياً" : "Optimizing performance & local personalization"}
                </p>
              </div>
            </div>
            <button
              onClick={handleEssentialOnly}
              className="p-1 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all"
              title={isAr ? "إغلاق" : "Dismiss"}
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Body description */}
          {!showSettings ? (
            <p className="text-xs text-slate-300 leading-relaxed">
              {isAr
                ? "نستخدم التخزين المحلي (LocalStorage) والكوكيز التقنية فقط لتسريع تحميل المنصة إلى 0ms وحفظ الثيم واللغة بدون أي تتبع إعلاني."
                : "We utilize essential cookies & high-speed local caching to achieve 0ms load times and preserve your visual preferences with zero ad tracking."}
            </p>
          ) : (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="space-y-2.5 pt-1 border-t border-slate-800/80"
            >
              {/* Option 1: High-Speed Cache */}
              <div className="flex items-center justify-between p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs">
                <div className="flex items-center gap-2.5">
                  <HardDrive className="w-4 h-4 text-cyan-400 shrink-0" />
                  <div>
                    <span className="font-bold text-slate-200 block">{isAr ? "الذاكرة المؤقتة السريعة (0ms)" : "High-Speed SWR Cache"}</span>
                    <span className="text-[10px] text-slate-400">{isAr ? "تسريع المودات والشيدرات" : "Pre-caches mods & live stats"}</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.cache}
                  onChange={(e) => setPreferences({ ...preferences, cache: e.target.checked })}
                  className="w-4 h-4 rounded accent-cyan-500 cursor-pointer"
                />
              </div>

              {/* Option 2: Visual & Performance Mode */}
              <div className="flex items-center justify-between p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs">
                <div className="flex items-center gap-2.5">
                  <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
                  <div>
                    <span className="font-bold text-slate-200 block">{isAr ? "التخصيص ومظهر الواجهة" : "Visual Theme & Eco Mode"}</span>
                    <span className="text-[10px] text-slate-400">{isAr ? "حفظ الوضع المظلم واللغة" : "Dark/Light & UI smoothness"}</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.preferences}
                  onChange={(e) => setPreferences({ ...preferences, preferences: e.target.checked })}
                  className="w-4 h-4 rounded accent-amber-500 cursor-pointer"
                />
              </div>

              {/* Option 3: Sound FX */}
              <div className="flex items-center justify-between p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs">
                <div className="flex items-center gap-2.5">
                  <Volume2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <div>
                    <span className="font-bold text-slate-200 block">{isAr ? "المؤثرات الصوتية" : "UI Sound Effects"}</span>
                    <span className="text-[10px] text-slate-400">{isAr ? "أصوات النقر التفاعلية" : "Tactile click sound feedback"}</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={soundFx}
                  onChange={() => toggleSoundFx()}
                  className="w-4 h-4 rounded accent-emerald-500 cursor-pointer"
                />
              </div>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-2 pt-1">
            {!showSettings ? (
              <>
                <button
                  onClick={handleAcceptAll}
                  className="flex-1 py-2.5 px-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black flex items-center justify-center gap-1.5 shadow-lg shadow-cyan-500/20 active:scale-95 transition-all"
                >
                  <Zap className="w-3.5 h-3.5 fill-current" />
                  <span>{isAr ? "تفعيل السرعة القصوى" : "Accept & Turbo Cache"}</span>
                </button>
                <button
                  onClick={() => setShowSettings(true)}
                  className="py-2.5 px-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-bold flex items-center justify-center gap-1.5 transition-all"
                >
                  <Settings2 className="w-3.5 h-3.5" />
                  <span>{isAr ? "تخصيص" : "Customize"}</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleSaveCustom}
                  className="flex-1 py-2.5 px-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-500/20 active:scale-95 transition-all"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>{isAr ? "حفظ التفضيلات" : "Save Preferences"}</span>
                </button>
                <button
                  onClick={() => setShowSettings(false)}
                  className="py-2.5 px-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold transition-all"
                >
                  {isAr ? "رجوع" : "Back"}
                </button>
              </>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
