"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Menu, 
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
  Trophy, 
  Globe, 
  Activity, 
  HelpCircle, 
  Flame, 
  History, 
  Radio,
  Server
} from "lucide-react";
import { useEcosystem } from "@/lib/context";
import { signInWithGoogle, signOutUser, onAuthStateChanged, auth } from "@/lib/firebase";
import { BroadcastBanner } from "./navbar/BroadcastBanner";
import { NotificationsPanel, NotificationItem } from "./navbar/NotificationsPanel";
import { UserAccountDropdown } from "./navbar/UserAccountDropdown";
import { NavLinks, NavLinkItem } from "./navbar/NavLinks";
import { soundFx } from "@/lib/sound";

export function Navbar() {
  const { lang, setLang, themeMode, setThemeMode, t } = useEcosystem();
  const isAr = lang === "ar";

  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [authLoading, setAuthLoading] = useState(false);
  const [readNotifIds, setReadNotifIds] = useState<string[]>([]);
  const [broadcast, setBroadcast] = useState<any>(null);

  // Listen to Auth State
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser: any) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  // Fetch read notifications from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem("sir_read_notif_ids");
      if (stored) setReadNotifIds(JSON.parse(stored));
    } catch {}
  }, []);

  // Fetch real-time broadcast and notifications from Firebase Realtime Database
  useEffect(() => {
    async function fetchRTDBUpdates() {
      try {
        const res = await fetch("https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/broadcast.json");
        if (res.ok) {
          const data = await res.json();
          if (data && data.active) {
            setBroadcast(data);
          }
        }
      } catch {}
    }
    fetchRTDBUpdates();
  }, []);

  const rawNotifications: NotificationItem[] = [
    {
      id: "notif-v100",
      type: "update",
      title: isAr ? "إطلاق المنظومة الرسمي v1.0.0" : "Official Ecosystem Launch v1.0.0",
      message: isAr 
        ? "تم إطلاق النسخة الرسمية 1.0.0 مع شيدرز Bliss 2048 ومحرك Power Governor!"
        : "Official v1.0.0 released with Bliss 2048 Shaders and Hardware Power Governor!",
      time: "2026",
      read: readNotifIds.includes("notif-v100"),
      actionLabel: isAr ? "تحميل الآن" : "Download Now",
      actionUrl: "/#downloads"
    },
    {
      id: "notif-fabric",
      type: "cloud",
      title: isAr ? "تحديث مودات Fabric 26.2" : "Fabric 26.2 Mods Sync",
      message: isAr
        ? "تحديث فوري لمكتبات Sodium و Iris و FerriteCore لأقصى إطارات."
        : "Live synchronization for Sodium, Iris & FerriteCore for maximum FPS.",
      time: "10m ago",
      read: readNotifIds.includes("notif-fabric"),
      actionLabel: isAr ? "عرض المودات" : "View Mods",
      actionUrl: "/mods"
    }
  ];

  const unreadCount = rawNotifications.filter(n => !n.read).length;

  const markNotificationAsRead = (id: string) => {
    if (!readNotifIds.includes(id)) {
      const updated = [...readNotifIds, id];
      setReadNotifIds(updated);
      try {
        localStorage.setItem("sir_read_notif_ids", JSON.stringify(updated));
      } catch {}
    }
  };

  const markAllAsRead = () => {
    const allIds = rawNotifications.map(n => n.id);
    setReadNotifIds(allIds);
    try {
      localStorage.setItem("sir_read_notif_ids", JSON.stringify(allIds));
    } catch {}
  };

  const handleSignIn = async () => {
    setAuthLoading(true);
    try {
      await signInWithGoogle();
      setUserDropdownOpen(false);
      soundFx.playSuccess();
    } catch (error) {
      console.error("Sign in failed:", error);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signOutUser();
      setUserDropdownOpen(false);
      soundFx.playClick();
    } catch (error) {
      console.error("Sign out failed:", error);
    }
  };

  const openSidemenu = () => {
    soundFx.playClick();
    window.dispatchEvent(new CustomEvent("sir_open_sidemenu"));
  };

  const navLinks: NavLinkItem[] = [
    { label: t.nav.downloads, href: "/#downloads", icon: Download },
    { label: t.nav.profiles, href: "/#profiles", icon: Layers },
    { label: isAr ? "كتالوج المودات" : "Mods Suite", href: "/mods", icon: Package },
    { label: isAr ? "مختبر الشيدرز" : "Shaders Lab", href: "/shaders", icon: Sparkles },
    { label: isAr ? "استوديو الأوشحة" : "Capes Studio", href: "/capes", icon: ShieldCheck },
    { label: isAr ? "استوديو السكنات" : "Skin Studio", href: "/skins", icon: Shirt },
    { label: isAr ? "سيرفرات اللعب" : "Servers Hub", href: "/servers", icon: Globe },
    { label: isAr ? "غرفة عمليات الأدمن" : "Admin Control", href: "/admin", icon: Radio, highlight: true }
  ];

  return (
    <>
      <header className="sticky top-0 z-50 w-full backdrop-blur-xl bg-white/95 dark:bg-[#090b10]/95 border-b border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
        <BroadcastBanner broadcast={broadcast} lang={lang} />

        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between gap-2">
          {/* Left: Sidemenu Trigger + Brand Logo */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            <button
              onClick={openSidemenu}
              className="p-2 sm:p-2.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 hover:border-cyan-500 text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-all cursor-pointer shadow-sm active:scale-95 flex items-center gap-1.5 shrink-0"
              title={isAr ? "القائمة الرئيسية" : "Main Navigation Menu"}
              aria-label="Open main menu"
            >
              <Menu className="w-5 h-5 text-cyan-500 dark:text-cyan-400" />
            </button>

            <Link href="/" onClick={() => soundFx.playTab()} className="flex items-center gap-2.5 sm:gap-3 group shrink-0">
              <div className="relative flex items-center justify-center w-9 h-9 sm:w-11 sm:h-11 rounded-2xl bg-slate-900 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-1 transition-transform duration-200 group-hover:scale-105 shadow-sm overflow-hidden shrink-0">
                <img
                  src="/sir-logo.png"
                  alt="SIR Logo"
                  className="w-full h-full object-contain rounded-xl"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <span className="font-black text-base sm:text-xl tracking-tight text-slate-900 dark:text-white">
                    SIR
                  </span>
                  <span className="font-bold text-xs sm:text-sm text-cyan-600 dark:text-[#00e5ff] hidden xs:inline">
                    ModPack
                  </span>
                  <span className="px-1.5 py-0.5 text-[9px] sm:text-[10px] font-black tracking-wide uppercase rounded-full bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-[#00e5ff] border border-cyan-200 dark:border-cyan-500/30 font-mono">
                    v1.0.0
                  </span>
                </div>
              </div>
            </Link>
          </div>

          {/* Right Action Controls: Search, Notifications, Profile/Settings */}
          <div className="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
            <button
              onClick={() => {
                soundFx.playClick();
                window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", ctrlKey: true }));
              }}
              className="p-2 sm:px-3 sm:py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 hover:border-cyan-500/50 text-slate-500 dark:text-slate-400 hover:text-cyan-500 dark:hover:text-cyan-400 transition-all text-xs font-semibold cursor-pointer shadow-sm active:scale-95 flex items-center gap-2"
              title="Search (Ctrl+K)"
              aria-label="Open search palette"
            >
              <Search className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
              <span className="hidden sm:inline">Search...</span>
              <kbd className="hidden sm:inline font-mono text-[10px] px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400">Ctrl K</kbd>
            </button>

            <NotificationsPanel
              isOpen={notifOpen}
              onToggle={() => {
                setNotifOpen(!notifOpen);
                setUserDropdownOpen(false);
              }}
              onClose={() => setNotifOpen(false)}
              notifications={rawNotifications}
              unreadCount={unreadCount}
              onMarkRead={markNotificationAsRead}
              onMarkAllRead={markAllAsRead}
            />

            <UserAccountDropdown
              isOpen={userDropdownOpen}
              onToggle={() => {
                setUserDropdownOpen(!userDropdownOpen);
                setNotifOpen(false);
              }}
              onClose={() => setUserDropdownOpen(false)}
              user={user}
              themeMode={themeMode}
              setThemeMode={setThemeMode}
              lang={lang}
              setLang={setLang}
              onSignIn={handleSignIn}
              onSignOut={handleSignOut}
              authLoading={authLoading}
            />
          </div>
        </div>
      </header>
    </>
  );
}
