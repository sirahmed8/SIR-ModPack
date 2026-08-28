"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Search, 
  Package, 
  Sparkles, 
  Layers, 
  Shirt, 
  Globe, 
  Trophy, 
  HelpCircle, 
  Download, 
  Swords, 
  Sliders, 
  Music, 
  Compass, 
  Activity,
  X,
  ExternalLink,
  ChevronRight
} from "lucide-react";
import { useEcosystem } from "@/lib/context";

interface NavCommand {
  id: string;
  name: string;
  nameAr: string;
  category: string;
  categoryAr: string;
  path: string;
  icon: React.ReactNode;
  badge?: string;
}

export function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const router = useRouter();
  const { lang } = useEcosystem();
  const isAr = lang === "ar";

  const commands: NavCommand[] = [
    { id: "mods", name: "240+ Mods Catalog", nameAr: "كتالوج 240+ مود", category: "Core", categoryAr: "الأساسية", path: "/mods", icon: <Package className="w-4 h-4 text-cyan-400" />, badge: "240 Mods" },
    { id: "shaders", name: "SIR Shaders Optical Lab", nameAr: "مختبر ضبط الشيدرز الضوئي", category: "Visuals", categoryAr: "الرسوميات", path: "/shaders", icon: <Sparkles className="w-4 h-4 text-amber-400" />, badge: "Lab" },
    { id: "packs", name: "3D POM Resource Packs", nameAr: "حزم الموارد ثلاثية الأبعاد", category: "Visuals", categoryAr: "الرسوميات", path: "/packs", icon: <Layers className="w-4 h-4 text-emerald-400" /> },
    { id: "profiles", name: "8-Tier Profile Matrix", nameAr: "مصفوفة البروفايلات والنسخ", category: "Profiles", categoryAr: "البروفايلات", path: "/profiles", icon: <Sliders className="w-4 h-4 text-purple-400" /> },
    { id: "skins", name: "3D Skin & Capes Studio", nameAr: "ستوديو السكنات والكيبات 3D", category: "Customization", categoryAr: "التخصيص", path: "/skins", icon: <Shirt className="w-4 h-4 text-pink-400" /> },
    { id: "servers", name: "Multiplayer Servers (100+)", nameAr: "سيرفرات اللعب الجماعي (100+)", category: "Multiplayer", categoryAr: "اللعب الجماعي", path: "/servers", icon: <Globe className="w-4 h-4 text-blue-400" /> },
    { id: "server-guide", name: "Server Setup & Cloud Tunnel Guide", nameAr: "دليل إنشاء السيرفر بدون بورت فورورد", category: "Servers", categoryAr: "السيرفرات", path: "/server-guide", icon: <Activity className="w-4 h-4 text-cyan-400" />, badge: "Guide" },
    { id: "benchmarks", name: "Hardware Benchmarks & FPS Labs", nameAr: "اختبارات الأداء وقياس الفريمات", category: "Performance", categoryAr: "الأداء", path: "/benchmarks", icon: <Activity className="w-4 h-4 text-emerald-400" /> },
    { id: "leaderboards", name: "Global PvP Leaderboards", nameAr: "لوحة صدارة المبارزات العالمية", category: "Competitive", categoryAr: "التنافسي", path: "/leaderboards", icon: <Trophy className="w-4 h-4 text-amber-400" /> },
    { id: "trainer", name: "PvP CPS & Aim Trainer", nameAr: "مدرب سرعة النقر والتصويب", category: "Competitive", categoryAr: "التنافسي", path: "/trainer", icon: <Swords className="w-4 h-4 text-red-400" /> },
    { id: "seeds", name: "World Seeds & Shaders Showcase", nameAr: "سيدات وبذور العوالم الخرافية", category: "Discovery", categoryAr: "الاستكشاف", path: "/seeds", icon: <Compass className="w-4 h-4 text-amber-500" /> },
    { id: "faq", name: "Knowledge Base & Troubleshooting FAQ", nameAr: "الأسئلة الشائعة وحلول المشاكل", category: "Support", categoryAr: "الدعم", path: "/faq", icon: <HelpCircle className="w-4 h-4 text-cyan-400" /> },
    { id: "changelog", name: "Master Changelog Releases", nameAr: "سجل التحديثات والإصدارات", category: "Updates", categoryAr: "التحديثات", path: "/changelog", icon: <Package className="w-4 h-4 text-slate-400" /> }
  ];

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      setIsOpen((prev) => !prev);
    }
    if (e.key === "Escape") {
      setIsOpen(false);
    }
  }, []);

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const filteredCommands = commands.filter((c) => {
    const term = query.toLowerCase();
    return (
      c.name.toLowerCase().includes(term) ||
      c.nameAr.toLowerCase().includes(term) ||
      c.category.toLowerCase().includes(term) ||
      c.path.toLowerCase().includes(term)
    );
  });

  const handleSelect = (path: string) => {
    setIsOpen(false);
    setQuery("");
    router.push(path);
  };

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ duration: 0.15 }}
              className="w-full max-w-2xl bg-white dark:bg-[#0c101a] border border-slate-200 dark:border-cyan-500/30 rounded-3xl shadow-2xl shadow-slate-900/10 dark:shadow-cyan-500/10 overflow-hidden flex flex-col transition-colors duration-200"
            >
              {/* Search Bar */}
              <div className="flex items-center px-5 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50/90 dark:bg-[#070a10]">
                <Search className="w-5 h-5 text-cyan-600 dark:text-cyan-400 mr-3 shrink-0" />
                <input
                  type="text"
                  placeholder={isAr ? "ابحث عن أي قسم، مود، شيدر، أو أداة... (أو اضغط ESC للإغلاق)" : "Search any page, mod, shader, or tool... (or press ESC to close)"}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  autoFocus
                  className="command-input no-ring flex-1 bg-transparent border-0 outline-none focus:outline-none focus:ring-0 focus:border-transparent text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 font-medium !shadow-none !ring-0"
                />
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 rounded-xl bg-slate-200/60 hover:bg-slate-200 dark:bg-slate-800/80 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-all cursor-pointer"
                  title="Close (ESC)"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Results List */}
              <div className="max-h-[380px] overflow-y-auto p-3 space-y-1.5 scrollbar-thin bg-white dark:bg-[#0c101a]">
                {filteredCommands.map((cmd) => (
                  <div
                    key={cmd.id}
                    onClick={() => handleSelect(cmd.path)}
                    className="flex items-center justify-between p-3 rounded-2xl bg-slate-50/50 hover:bg-cyan-50/80 dark:bg-transparent dark:hover:bg-cyan-500/10 border border-slate-100 hover:border-cyan-300 dark:border-transparent dark:hover:border-cyan-500/30 cursor-pointer transition-all group shadow-xs dark:shadow-none"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 group-hover:border-cyan-400/50 shadow-xs">
                        {cmd.icon}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 group-hover:text-cyan-600 dark:group-hover:text-cyan-300">
                          {isAr ? cmd.nameAr : cmd.name}
                        </h4>
                        <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                          {cmd.path}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {cmd.badge && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
                          {cmd.badge}
                        </span>
                      )}
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </div>
                ))}

                {filteredCommands.length === 0 && (
                  <div className="text-center py-10 text-slate-400 dark:text-slate-500 text-sm">
                    {isAr ? "لم يتم العثور على نتائج مطابقة." : "No matching routes found."}
                  </div>
                )}
              </div>

              {/* Footer Hint */}
              <div className="px-5 py-3 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50/90 dark:bg-[#070a10] flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
                <span>{isAr ? "استخدم الأسهم للتنقل • Enter للفتح" : "Use arrow keys to navigate • Enter to select"}</span>
                <span className="font-mono bg-slate-200 dark:bg-slate-900 px-2 py-0.5 rounded border border-slate-300 dark:border-slate-800 text-cyan-700 dark:text-cyan-400 font-bold">Ctrl + K</span>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
