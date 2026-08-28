"use client";

import React, { useRef, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { 
  User as UserIcon, 
  Settings, 
  Moon, 
  Sun, 
  Laptop, 
  Globe, 
  Radio, 
  LogOut 
} from "lucide-react";
import { Language } from "@/lib/i18n";

interface UserAccountDropdownProps {
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
  user: any;
  themeMode: "system" | "dark" | "light";
  setThemeMode: (mode: "system" | "dark" | "light") => void;
  lang: Language;
  setLang: (lang: Language) => void;
  onSignIn: () => void;
  onSignOut: () => void;
  authLoading: boolean;
}

export function UserAccountDropdown({
  isOpen,
  onToggle,
  onClose,
  user,
  themeMode,
  setThemeMode,
  lang,
  setLang,
  onSignIn,
  onSignOut,
  authLoading,
}: UserAccountDropdownProps) {
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  const isAr = lang === "ar";

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={onToggle}
        className="flex items-center justify-center w-9 h-9 sm:w-10 sm:h-10 rounded-2xl bg-gradient-to-tr from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 border border-slate-200 dark:border-slate-700 hover:border-cyan-500 transition-all cursor-pointer shadow-sm active:scale-95"
        title={user ? (user.displayName || "Account Profile") : (isAr ? "الحساب والإعدادات" : "Profile & Preferences")}
        aria-label="Open profile and settings"
      >
        {user && user.photoURL ? (
          <img
            src={user.photoURL}
            alt={user.displayName || "User"}
            className="w-full h-full rounded-2xl object-cover"
          />
        ) : user ? (
          <div className="w-full h-full rounded-2xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-black text-xs">
            {user.displayName?.charAt(0) || "U"}
          </div>
        ) : (
          <Settings className="w-4 h-4 text-slate-700 dark:text-slate-300" />
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ type: "spring", stiffness: 380, damping: 26 }}
            className="fixed inset-x-3 top-20 max-w-xs mx-auto sm:inset-auto sm:absolute sm:top-full sm:mt-2 sm:w-72 p-3 rounded-3xl bg-white dark:bg-[#0c101c] border border-slate-200 dark:border-slate-800 shadow-2xl z-[60] space-y-3 backdrop-blur-2xl sm-logical-popover-end"
          >
            {/* User Header Info */}
            <div className="p-3 rounded-2xl bg-slate-50 dark:bg-[#06090e] border border-slate-200/80 dark:border-slate-800/80 flex items-center gap-3">
              {user && user.photoURL ? (
                <img
                  src={user.photoURL}
                  alt={user.displayName || "User"}
                  className="w-10 h-10 rounded-xl object-cover shrink-0"
                />
              ) : (
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-500 flex items-center justify-center font-bold text-sm shrink-0">
                  {user ? (user.displayName?.charAt(0) || "U") : <UserIcon className="w-5 h-5" />}
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="text-xs font-black text-slate-900 dark:text-white truncate">
                  {user ? (user.displayName || "Authenticated User") : (isAr ? "مستكشف المنظومة" : "Guest Explorer")}
                </p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">
                  {user ? user.email : (isAr ? "حساب ضيف (أوفلاين)" : "Guest Session (Offline)")}
                </p>
              </div>
            </div>

            {/* Section: Preferences & Appearance */}
            <div className="space-y-2 pt-1 border-t border-slate-100 dark:border-slate-800/80">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-500 font-bold px-1 block">
                {isAr ? "التفضيلات والمظهر" : "Preferences & Appearance"}
              </span>

              {/* Theme Switcher */}
              <div className="space-y-1.5 p-2.5 rounded-2xl bg-slate-50 dark:bg-[#080d18] border border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200">
                    {isAr ? "المظهر البصري" : "Theme Appearance"}
                  </span>
                  <span className="text-[9px] font-mono text-cyan-600 dark:text-[#00e5ff] uppercase">
                    {themeMode === "system" ? (isAr ? "تلقائي" : "Auto") : themeMode === "dark" ? (isAr ? "مظلم" : "Dark") : (isAr ? "مضيء" : "Light")}
                  </span>
                </div>

                <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-200/70 dark:bg-[#06090e] border border-slate-300/80 dark:border-slate-800/80">
                  <button
                    type="button"
                    onClick={() => setThemeMode("dark")}
                    className={`flex-1 py-1 px-2 rounded-lg text-[10px] font-bold flex items-center justify-center gap-1 transition-all ${
                      themeMode === "dark"
                        ? "bg-cyan-500 text-slate-950 shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <Moon className="w-3 h-3" />
                    <span>{isAr ? "مظلم" : "Dark"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setThemeMode("system")}
                    className={`flex-1 py-1 px-2 rounded-lg text-[10px] font-bold flex items-center justify-center gap-1 transition-all ${
                      themeMode === "system"
                        ? "bg-cyan-500 text-slate-950 shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <Laptop className="w-3 h-3" />
                    <span>{isAr ? "النظام" : "Auto"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setThemeMode("light")}
                    className={`flex-1 py-1 px-2 rounded-lg text-[10px] font-bold flex items-center justify-center gap-1 transition-all ${
                      themeMode === "light"
                        ? "bg-cyan-500 text-slate-950 shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <Sun className="w-3 h-3" />
                    <span>{isAr ? "مضيء" : "Light"}</span>
                  </button>
                </div>
              </div>

              {/* Language Switch */}
              <div className="flex items-center justify-between p-2.5 rounded-2xl bg-slate-50 dark:bg-[#080d18] border border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-xl bg-cyan-500/10 text-cyan-500 border border-cyan-500/30">
                    <Globe className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                    {isAr ? "اللغة (عربي)" : "Language (English)"}
                  </span>
                </div>

                <button
                  onClick={() => {
                    setLang(lang === "en" ? "ar" : "en");
                  }}
                  className="px-2.5 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-600 dark:text-[#00e5ff] text-[11px] font-black border border-cyan-500/30 transition-all cursor-pointer active:scale-95"
                  title="Switch Language / تغيير اللغة"
                >
                  {lang === "en" ? "العربية" : "English"}
                </button>
              </div>
            </div>

            {/* Admin & Auth Actions */}
            <div className="space-y-1 pt-1 border-t border-slate-100 dark:border-slate-800/80">
              <Link
                href="/admin"
                onClick={onClose}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-cyan-600 dark:text-[#00e5ff] hover:bg-cyan-50 dark:hover:bg-cyan-950/30 rounded-xl transition-all"
              >
                <Radio className="w-4 h-4 text-cyan-600 dark:text-[#00e5ff] animate-pulse" />
                <span>{isAr ? "غرفة عمليات الأدمن" : "Admin Mission Control"}</span>
              </Link>

              {user ? (
                <button
                  onClick={onSignOut}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-xl transition-all cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                  <span>{isAr ? "تسجيل الخروج" : "Sign Out"}</span>
                </button>
              ) : (
                <button
                  onClick={onSignIn}
                  disabled={authLoading}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 text-xs font-black text-slate-950 bg-gradient-to-r from-[#00e5ff] to-[#38ef7d] hover:brightness-110 rounded-xl transition-all cursor-pointer shadow-md shadow-cyan-500/20 disabled:opacity-50"
                >
                  <span>{authLoading ? (isAr ? "جاري الاتصال..." : "Connecting...") : (isAr ? "تسجيل الدخول عبر Google" : "Sign in with Google")}</span>
                </button>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
