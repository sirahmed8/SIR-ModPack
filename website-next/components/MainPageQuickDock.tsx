"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Download, 
  Layers, 
  ShieldCheck, 
  Server, 
  Flame, 
  History 
} from "lucide-react";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";

interface DockItem {
  id: string;
  labelEn: string;
  labelAr: string;
  icon: React.ElementType;
  targetId: string;
  accentClass: string;
}

const MAIN_PAGE_SUBJECTS: DockItem[] = [
  { id: "downloads", labelEn: "Downloads Matrix", labelAr: "تحميل اللانشر", icon: Download, targetId: "downloads", accentClass: "text-emerald-400" },
  { id: "profiles", labelEn: "Profiles Matrix", labelAr: "البروفايلات", icon: Layers, targetId: "profiles", accentClass: "text-purple-400" },
  { id: "account", labelEn: "Account Hub", labelAr: "ربط الحسابات", icon: ShieldCheck, targetId: "account", accentClass: "text-blue-400" },
  { id: "server", labelEn: "Server Hosting", labelAr: "استضافة السيرفر", icon: Server, targetId: "server", accentClass: "text-amber-400" },
  { id: "havoc", labelEn: "HAVOC PvP", labelAr: "مشروع HAVOC", icon: Flame, targetId: "havoc", accentClass: "text-orange-400" },
  { id: "changelog", labelEn: "Changelog", labelAr: "سجل التحديثات", icon: History, targetId: "changelog", accentClass: "text-slate-400" }
];

export function MainPageQuickDock() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";
  const [activeSection, setActiveSection] = useState<string>("downloads");
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const isManualScrolling = useRef(false);
  const scrollTimeout = useRef<NodeJS.Timeout | null>(null);

  const scrollToSubject = (targetId: string, itemId: string) => {
    soundFx.playClick();
    
    // Lock manual scrolling so scroll listener does NOT fight/flicker the active state
    isManualScrolling.current = true;
    setActiveSection(itemId);
    
    if (scrollTimeout.current) clearTimeout(scrollTimeout.current);
    scrollTimeout.current = setTimeout(() => {
      isManualScrolling.current = false;
    }, 850);

    const element = document.getElementById(targetId);
    if (element) {
      const navOffset = 90;
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - navOffset;
      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth"
      });
    }
  };

  // Listen to drawer open/close to hide dock when side drawer is active
  useEffect(() => {
    const handleDrawerState = (e: any) => {
      if (e?.detail) {
        setIsDrawerOpen(!!e.detail.open);
      }
    };
    window.addEventListener("sir_sidemenu_state", handleDrawerState);
    return () => window.removeEventListener("sir_sidemenu_state", handleDrawerState);
  }, []);

  // Update active section on scroll (only when not manually smooth scrolling)
  useEffect(() => {
    const handleScroll = () => {
      if (isManualScrolling.current) return;

      const scrollPos = window.scrollY + 280;
      for (let i = MAIN_PAGE_SUBJECTS.length - 1; i >= 0; i--) {
        const item = MAIN_PAGE_SUBJECTS[i];
        const el = document.getElementById(item.targetId);
        if (el && el.offsetTop <= scrollPos) {
          setActiveSection(item.id);
          break;
        }
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (scrollTimeout.current) clearTimeout(scrollTimeout.current);
    };
  }, []);

  if (isDrawerOpen) return null;

  return (
    <aside 
      aria-label="Main Page Navigation Dock"
      className={`fixed ${isAr ? "right-3 sm:right-6" : "left-3 sm:left-6"} top-1/2 -translate-y-1/2 z-30 flex flex-col items-center gap-2 p-1.5 sm:p-2 rounded-2xl sm:rounded-3xl bg-white/95 dark:bg-[#070a12]/90 backdrop-blur-2xl border border-slate-200/90 dark:border-slate-800/90 shadow-2xl shadow-slate-900/10 dark:shadow-cyan-500/10 transition-all duration-300`}
    >
      {MAIN_PAGE_SUBJECTS.map((item) => {
        const Icon = item.icon;
        const isActive = activeSection === item.id;
        const isHovered = hoveredItem === item.id;

        return (
          <div key={item.id} className="relative group">
            <button
              onClick={() => scrollToSubject(item.targetId, item.id)}
              onMouseEnter={() => setHoveredItem(item.id)}
              onMouseLeave={() => setHoveredItem(null)}
              className={`relative w-9 h-9 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl flex items-center justify-center transition-colors duration-200 cursor-pointer ${
                isActive
                  ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/40 font-bold"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/80"
              }`}
              title={isAr ? item.labelAr : item.labelEn}
              aria-label={isAr ? item.labelAr : item.labelEn}
            >
              <Icon className="w-4 h-4 sm:w-4.5 sm:h-4.5" />
            </button>

            {/* Tooltip Label (Opens right in English, left in Arabic) */}
            {isHovered && (
              <div 
                className={`hidden md:flex absolute ${
                  isAr ? "right-full mr-3" : "left-full ml-3"
                } top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-xl bg-slate-900/95 text-white text-[11px] font-bold whitespace-nowrap shadow-xl border border-slate-700/80 z-50 pointer-events-none items-center gap-1.5 animate-in fade-in duration-150`}
              >
                <span>{isAr ? item.labelAr : item.labelEn}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              </div>
            )}
          </div>
        );
      })}
    </aside>
  );
}
