"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Package, 
  Search, 
  Filter, 
  Layers, 
  Sparkles, 
  CheckCircle2, 
  Zap, 
  Volume2, 
  Eye, 
  Globe, 
  ShieldCheck,
  Cpu,
  ChevronRight,
  Download,
  ArrowLeft,
  ArrowRight,
  ExternalLink,
  RefreshCw,
  SlidersHorizontal,
  Flame,
  Star
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";
import { CyberSelect } from "@/components/CyberSelect";

interface ModItem {
  filename: string;
  name: string;
  category: string;
  size_kb: number;
  status: string;
  icon_url?: string;
  author?: string;
  downloads?: number;
  modrinth_slug?: string;
}

interface ModManifest {
  modpack: string;
  version: string;
  total_mods: number;
  engine: string;
  mods: ModItem[];
}

interface OnlineProject {
  id: string;
  slug: string;
  title: string;
  description: string;
  author: string;
  icon_url: string;
  downloads: number;
  follows: number;
  date_modified: string;
  categories: string[];
  project_type: string;
  source: string;
}

export default function ModsCatalogPage() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";

  // Navigation tab: 'included' (240+ curated mods) or 'online' (Live Modrinth & CurseForge API)
  const [activeTab, setActiveTab] = useState<"included" | "online">("included");

  // Local 240+ manifest state
  const [manifest, setManifest] = useState<ModManifest | null>(null);
  const [localSearch, setLocalSearch] = useState("");
  const [localCategory, setLocalCategory] = useState("All");
  const [visibleLocalCount, setVisibleLocalCount] = useState(30);

  // Online Store Live Fetch State
  const [onlineQuery, setOnlineQuery] = useState("");
  const [onlineProvider, setOnlineProvider] = useState<"modrinth" | "curseforge">("modrinth");
  const [onlineType, setOnlineType] = useState<"mod" | "shader" | "resourcepack" | "modpack">("mod");
  const [onlineLoader, setOnlineLoader] = useState<string>("fabric");
  const [onlineSort, setOnlineSort] = useState<"downloads" | "follows" | "updated" | "newest">("downloads");
  const [onlineResults, setOnlineResults] = useState<OnlineProject[]>([]);
  const [onlineLoading, setOnlineLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [onlineOffset, setOnlineOffset] = useState(0);
  const [onlineTotal, setOnlineTotal] = useState(0);

  // Load local manifest
  useEffect(() => {
    fetch("/data/mod_manifest.json")
      .then((res) => res.json())
      .then((data: ModManifest) => setManifest(data))
      .catch((err) => console.warn("Failed to load manifest", err));
  }, []);

  // Fetch Live Modrinth API (Initial & Search Filter change)
  const fetchLiveModrinth = useCallback(async () => {
    setOnlineLoading(true);
    setOnlineOffset(0);
    try {
      const facets: string[][] = [[`project_type:${onlineType}`]];
      if (onlineType === "mod" && onlineLoader !== "all") {
        facets.push([`categories:${onlineLoader}`]);
      }

      const params = new URLSearchParams({
        query: onlineQuery.trim(),
        limit: "24",
        offset: "0",
        index: onlineSort,
        facets: JSON.stringify(facets)
      });

      const res = await fetch(`https://api.modrinth.com/v2/search?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setOnlineTotal(data.total_hits || 0);
        const mapped: OnlineProject[] = (data.hits || []).map((h: any) => ({
          id: h.project_id,
          slug: h.slug,
          title: h.title,
          description: h.description || "No description provided.",
          author: h.author || "Creator",
          icon_url: h.icon_url || "https://raw.githubusercontent.com/modrinth/art/master/brand/logo.png",
          downloads: h.downloads || 0,
          follows: h.follows || 0,
          date_modified: (h.date_modified || "").slice(0, 10),
          categories: h.categories || [],
          project_type: h.project_type || onlineType,
          source: onlineProvider === "curseforge" ? "CurseForge" : "Modrinth"
        }));
        setOnlineResults(mapped);
      }
    } catch (err) {
      console.error("Modrinth Live API fetch error:", err);
    } finally {
      setOnlineLoading(false);
    }
  }, [onlineQuery, onlineType, onlineLoader, onlineSort, onlineProvider]);

  // Fetch More pagination
  const fetchMoreOnline = async () => {
    if (loadingMore || onlineResults.length >= onlineTotal) return;
    setLoadingMore(true);
    const nextOffset = onlineOffset + 24;
    try {
      const facets: string[][] = [[`project_type:${onlineType}`]];
      if (onlineType === "mod" && onlineLoader !== "all") {
        facets.push([`categories:${onlineLoader}`]);
      }

      const params = new URLSearchParams({
        query: onlineQuery.trim(),
        limit: "24",
        offset: nextOffset.toString(),
        index: onlineSort,
        facets: JSON.stringify(facets)
      });

      const res = await fetch(`https://api.modrinth.com/v2/search?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        const mapped: OnlineProject[] = (data.hits || []).map((h: any) => ({
          id: h.project_id,
          slug: h.slug,
          title: h.title,
          description: h.description || "No description provided.",
          author: h.author || "Creator",
          icon_url: h.icon_url || "https://raw.githubusercontent.com/modrinth/art/master/brand/logo.png",
          downloads: h.downloads || 0,
          follows: h.follows || 0,
          date_modified: (h.date_modified || "").slice(0, 10),
          categories: h.categories || [],
          project_type: h.project_type || onlineType,
          source: onlineProvider === "curseforge" ? "CurseForge" : "Modrinth"
        }));
        setOnlineResults(prev => [...prev, ...mapped]);
        setOnlineOffset(nextOffset);
      }
    } catch (err) {
      console.error("Fetch more online error:", err);
    } finally {
      setLoadingMore(false);
    }
  };

  // Trigger live search when switching to online tab or changing filters
  useEffect(() => {
    if (activeTab === "online") {
      const timer = setTimeout(() => {
        fetchLiveModrinth();
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [activeTab, fetchLiveModrinth]);

  const categories = [
    { id: "All", en: "All Mods", ar: "جميع المودات" },
    { id: "Optimization", en: "⚡ Optimization", ar: "⚡ تسريع الأداء" },
    { id: "Visuals & Shaders", en: "🎨 Visuals & Shaders", ar: "🎨 الرسوميات والشيدرز" },
    { id: "Audio & Immersion", en: "🔊 Audio & Immersion", ar: "🔊 الصوتيات والواقعية" },
    { id: "Gameplay & Utility", en: "🛠️ Utility & HUD", ar: "🛠️ الواجهة والأدوات" },
    { id: "World Generation", en: "🌍 World Gen & LODs", ar: "🌍 التضاريس والآفاق" },
    { id: "Core & Libraries", en: "⚙️ Core Libraries", ar: "⚙️ المكتبات الأساسية" }
  ];

  const formatDownloads = (num: number) => {
    if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
    if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
    return num.toString();
  };

  const filteredLocalMods = manifest?.mods.filter((mod) => {
    const matchesCat = localCategory === "All" || mod.category.toLowerCase().includes(localCategory.toLowerCase()) || mod.category === localCategory;
    const matchesSearch = !localSearch ||
                          mod.name.toLowerCase().includes(localSearch.toLowerCase()) ||
                          mod.filename.toLowerCase().includes(localSearch.toLowerCase()) ||
                          mod.category.toLowerCase().includes(localSearch.toLowerCase());
    return matchesCat && matchesSearch;
  }) || [];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* Header Navigation */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-sm">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <Layers className="w-3.5 h-3.5" />
            <span>240+ Curated Mods</span>
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "دليل ومكتبة المودات الشاملة (240+ مود)" : "Complete Mod Ecosystem & Live Catalog"}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
            {isAr 
              ? "استعرض الـ 240+ مود المضمنة والمضبوطة بعناية داخل حزمة SIR، أو ابحث مباشرة في ملايين المودات والشيدرز الحية عبر سيرفرات Modrinth و CurseForge."
              : "Explore the 240+ fine-tuned mods bundled with SIR, or search live across millions of mods & shaders directly from official Modrinth & CurseForge APIs."}
          </p>
        </div>

        {/* Master Tab Switcher (Included 240+ vs Live Modrinth/CurseForge) */}
        <div className="flex items-center justify-center px-4">
          <div className="inline-flex items-center gap-2 p-1.5 rounded-2xl bg-slate-200/80 dark:bg-slate-900/90 border border-slate-300 dark:border-slate-800 backdrop-blur-xl shadow-md">
            <button
              onClick={() => setActiveTab("included")}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer whitespace-nowrap ${
                activeTab === "included"
                  ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/25"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
              }`}
            >
              <Package className="w-4 h-4 shrink-0" />
              <span>{isAr ? "المودات المضمنة في SIR (240+ مود)" : "Bundled in SIR (240+ Mods)"}</span>
            </button>
            <button
              onClick={() => setActiveTab("online")}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer whitespace-nowrap ${
                activeTab === "online"
                  ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/25"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
              }`}
            >
              <Globe className="w-4 h-4 shrink-0" />
              <span>{isAr ? "متصفح Modrinth & CurseForge الحي" : "Live Modrinth & CurseForge Explorer"}</span>
            </button>
          </div>
        </div>

        {/* ================= TAB 1: INCLUDED 240+ MODS SUITE ================= */}
        {activeTab === "included" && (
          <div className="space-y-6">
            {/* Search & Category Filter Bar */}
            <div className="flex flex-col md:flex-row items-center gap-4 bg-white dark:bg-[#0d121d]/90 border border-slate-200 dark:border-slate-800/80 p-4 rounded-2xl backdrop-blur-xl shadow-md">
              <div className="relative flex-1 w-full">
                <Search className={`absolute ${isAr ? "right-3.5" : "left-3.5"} top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500 pointer-events-none z-10`} />
                <input
                  type="text"
                  placeholder={isAr ? "ابحث في 240 مود بالاسم أو التصنيف (مثل: sodium, iris, audio, pvp)..." : "Search all 240 mods by name, filename, or category (e.g. sodium, shader, audio, physics)..."}
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                  className={`w-full bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl ${isAr ? "pr-10 pl-4" : "pl-10 pr-4"} py-2.5 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors`}
                />
              </div>

              {/* Category Pills */}
              <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto py-1 px-0.5 scrollbar-none">
                {categories.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setLocalCategory(c.id)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                      localCategory === c.id
                        ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20"
                        : "bg-slate-100 dark:bg-slate-900/60 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-800/80"
                    }`}
                  >
                    {isAr ? c.ar : c.en}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredLocalMods.slice(0, visibleLocalCount).map((mod, idx) => (
                <motion.div
                  key={mod.filename || idx}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: Math.min(idx * 0.015, 0.3) }}
                  className="p-4 rounded-2xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800/80 hover:border-cyan-500/50 hover:shadow-md transition-all flex flex-col justify-between group shadow-sm"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className="w-9 h-9 rounded-xl bg-cyan-50 dark:bg-cyan-950/60 border border-cyan-200 dark:border-cyan-800/40 flex items-center justify-center text-cyan-600 dark:text-cyan-400">
                          {mod.category.includes("Optimization") ? <Zap className="w-4 h-4" /> :
                           mod.category.includes("Visuals") ? <Sparkles className="w-4 h-4" /> :
                           mod.category.includes("Audio") ? <Volume2 className="w-4 h-4" /> :
                           <Package className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />}
                        </div>
                        <div className="min-w-0">
                          <h3 className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors truncate max-w-[170px]" title={mod.name}>
                            {mod.name}
                          </h3>
                          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">{mod.size_kb} KB • Fabric 1.21.4</span>
                        </div>
                      </div>
                      <span className="badge-tag bg-cyan-50 dark:bg-cyan-950/80 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/50 text-[9px] rounded-full px-2 py-0.5 font-bold">
                        {mod.category.split("&")[0].trim()}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono truncate">{mod.filename}</p>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between text-[11px]">
                    <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-bold">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>{isAr ? "مفحوص ومضمّن" : "Verified Bundled"}</span>
                    </span>
                    <a
                      href={`https://modrinth.com/mods?q=${encodeURIComponent(mod.name.replace(/[-_]/g, ' '))}`}
                      target="_blank"
                      rel="noreferrer"
                      className="text-slate-500 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 flex items-center gap-1 transition-colors"
                    >
                      <span>Modrinth</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* View More Mods Button */}
            {filteredLocalMods.length > visibleLocalCount && (
              <div className="flex flex-col items-center justify-center pt-4 pb-2 space-y-2">
                <button
                  onClick={() => setVisibleLocalCount(prev => prev + 30)}
                  className="px-6 py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all shadow-lg shadow-cyan-500/25 active:scale-95 flex items-center gap-2 cursor-pointer"
                >
                  <Package className="w-4 h-4" />
                  <span>{isAr ? `عرض المزيد من المودات (+30)` : `View More Mods (+30)`}</span>
                </button>
                <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                  {isAr ? `عرض ${Math.min(visibleLocalCount, filteredLocalMods.length)} من أصل ${filteredLocalMods.length} مود معتمد` : `Showing ${Math.min(visibleLocalCount, filteredLocalMods.length)} of ${filteredLocalMods.length} verified mods`}
                </span>
              </div>
            )}
          </div>
        )}

        {/* ================= TAB 2: LIVE MODRINTH & CURSEFORGE EXPLORER ================= */}
        {activeTab === "online" && (
          <div className="space-y-6">
            {/* Control Panel */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#0c101a]/95 border border-slate-200 dark:border-slate-800/90 space-y-4 shadow-md">
              <div className="flex flex-col md:flex-row items-center gap-3">
                {/* Search Bar */}
                <div className="relative flex-1 w-full">
                  <Search className={`absolute ${isAr ? "right-3.5" : "left-3.5"} top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 dark:text-slate-500 pointer-events-none z-10`} />
                  <input
                    type="text"
                    placeholder={isAr ? "ابحث في Modrinth & CurseForge (مثال: Sodium, Iris, JEI, Physics Mod, BSL)..." : "Search live Modrinth & CurseForge (e.g. Sodium, Iris, JEI, Distant Horizons, BSL)..."}
                    value={onlineQuery}
                    onChange={(e) => setOnlineQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && fetchLiveModrinth()}
                    className={`w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl ${isAr ? "pr-10 pl-4" : "pl-10 pr-4"} py-2.5 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors`}
                  />
                </div>

                {/* Provider Selector */}
                <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-1 rounded-xl border border-slate-200 dark:border-slate-800">
                  <button
                    onClick={() => { setOnlineProvider("modrinth"); fetchLiveModrinth(); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                      onlineProvider === "modrinth"
                        ? "bg-emerald-500 text-slate-950 shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full bg-emerald-950"></span>
                    <span>Modrinth</span>
                  </button>
                  <button
                    onClick={() => { setOnlineProvider("curseforge"); fetchLiveModrinth(); }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                      onlineProvider === "curseforge"
                        ? "bg-amber-500 text-slate-950 shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full bg-amber-950"></span>
                    <span>CurseForge</span>
                  </button>
                </div>

                <button
                  onClick={fetchLiveModrinth}
                  className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center gap-1.5 shadow-md shadow-cyan-500/20 active:scale-95 cursor-pointer"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${onlineLoading ? "animate-spin" : ""}`} />
                  <span>{isAr ? "تحديث البحث" : "Search Live"}</span>
                </button>
              </div>

              {/* Type, Loader & Sort Filters */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800/80">
                {/* Project Types */}
                <div className="flex items-center gap-2 overflow-x-auto py-2 px-1 scrollbar-none">
                  {[
                    { id: "mod", label: "📦 Mods" },
                    { id: "shader", label: "✨ Shaders" },
                    { id: "resourcepack", label: "🎨 Resource Packs" },
                    { id: "modpack", label: "⚡ Modpacks" }
                  ].map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setOnlineType(t.id as any)}
                      className={`px-3.5 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                        onlineType === t.id
                          ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/25"
                          : "bg-slate-100 dark:bg-slate-900/80 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {/* Mod Loaders & Sorting */}
                <div className="flex items-center gap-3">
                  {onlineType === "mod" && (
                    <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-1 rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
                      {["fabric", "forge", "neoforge", "all"].map((l) => (
                        <button
                          key={l}
                          onClick={() => setOnlineLoader(l)}
                          className={`px-2.5 py-1 rounded-lg font-bold capitalize transition-all cursor-pointer ${
                            onlineLoader === l
                              ? "bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 border border-cyan-300 dark:border-cyan-800/60"
                              : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
                          }`}
                        >
                          {l}
                        </button>
                      ))}
                    </div>
                  )}

                  <CyberSelect
                    accentColor="cyan"
                    value={onlineSort}
                    onChange={(val) => setOnlineSort(val as any)}
                    options={[
                      { value: "downloads", label: isAr ? "الأكثر تحميلاً" : "Most Downloads", badge: "Hot" },
                      { value: "follows", label: isAr ? "الأعلى شعبية" : "Popularity", badge: "Stars" },
                      { value: "updated", label: isAr ? "المحدث حديثاً" : "Recently Updated", badge: "Fresh" },
                      { value: "newest", label: isAr ? "الأحدث إصداراً" : "Newest Release", badge: "New" },
                    ]}
                  />
                </div>
              </div>
            </div>

            {/* Results Status */}
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1 font-mono">
              <span>{isAr ? `تم العثور على ${onlineTotal.toLocaleString()} نتيجة حية` : `Found ${onlineTotal.toLocaleString()} live projects`}</span>
              <span>{isAr ? "مصدر البيانات: Modrinth API v2" : "Data Source: Official Modrinth API v2"}</span>
            </div>

            {/* Live Cards List */}
            {onlineLoading ? (
              <div className="p-16 rounded-2xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 text-center space-y-3 shadow-md">
                <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Fetching verified catalog from {onlineProvider === "modrinth" ? "Modrinth API v2" : "CurseForge"}...</p>
              </div>
            ) : onlineResults.length === 0 ? (
              <div className="p-16 rounded-2xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 text-center space-y-2 shadow-md">
                <Package className="w-10 h-10 text-slate-400 dark:text-slate-500 mx-auto" />
                <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">No Online Projects Found</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400">Try adjusting your query or selecting another project type.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {onlineResults.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-2xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm"
                  >
                    <div className="flex items-center gap-3.5 min-w-0 flex-1">
                      <img
                        src={item.icon_url}
                        alt="Icon"
                        className="w-12 h-12 rounded-2xl object-cover bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shrink-0 shadow-sm"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = "https://raw.githubusercontent.com/modrinth/art/master/brand/logo.png";
                        }}
                      />
                      <div className="min-w-0 space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-sm font-bold text-slate-900 dark:text-white truncate max-w-sm">{item.title}</h3>
                          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">by <span className="text-slate-700 dark:text-slate-300 font-semibold">{item.author}</span></span>
                          <span className={`badge-tag text-[9px] font-bold rounded-full px-2 py-0.5 ${
                            item.source === "CurseForge"
                              ? "bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800/60"
                              : "bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/60"
                          }`}>
                            {item.source}
                          </span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-1">{item.description}</p>
                        <div className="flex items-center gap-3 text-[11px] text-slate-500 font-mono">
                          <span className="flex items-center gap-1 text-slate-700 dark:text-slate-300 font-bold">
                            <Download className="w-3 h-3 text-cyan-500 dark:text-cyan-400" />
                            <span>{formatDownloads(item.downloads)} Downloads</span>
                          </span>
                          <span>• Updated: {item.date_modified}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
                      <a
                        href={item.source === "CurseForge" ? `https://www.curseforge.com/minecraft/mc-mods/${item.slug}` : `https://modrinth.com/${item.project_type}/${item.slug}`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-3.5 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-bold text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400 border border-slate-200 dark:border-slate-700/60 transition-all flex items-center gap-1.5"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        <span>{isAr ? "معاينة" : "View"}</span>
                      </a>
                      <a
                        href={item.source === "CurseForge" ? `https://www.curseforge.com/minecraft/mc-mods/${item.slug}/files` : `https://modrinth.com/${item.project_type}/${item.slug}/versions`}
                        target="_blank"
                        rel="noreferrer"
                        className="px-4 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-black shadow-md shadow-emerald-500/20 active:scale-95 transition-all flex items-center gap-1.5"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>{isAr ? "تحميل" : "Download"}</span>
                      </a>
                    </div>
                  </div>
                ))}
                {/* View More / Load More Pagination Button */}
                {onlineResults.length < onlineTotal && (
                  <div className="pt-4 text-center space-y-2">
                    <button
                      onClick={fetchMoreOnline}
                      disabled={loadingMore}
                      className="px-8 py-3.5 rounded-2xl bg-white dark:bg-[#0c101a] hover:bg-cyan-500/10 border border-slate-300 dark:border-slate-800 hover:border-cyan-500 text-slate-800 dark:text-white hover:text-cyan-600 dark:hover:text-cyan-400 text-xs font-black transition-all shadow-md active:scale-95 inline-flex items-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      {loadingMore ? (
                        <>
                          <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />
                          <span>{isAr ? "جاري جلب المزيد من المشروعات..." : "Fetching More Projects..."}</span>
                        </>
                      ) : (
                        <>
                          <Flame className="w-4 h-4 text-amber-500" />
                          <span>
                            {isAr 
                              ? `عرض المزيد من المشروعات (+24 من أصل ${onlineTotal.toLocaleString()})`
                              : `View More Projects (+24 of ${onlineTotal.toLocaleString()} available)`}
                          </span>
                        </>
                      )}
                    </button>
                    <p className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
                      {isAr
                        ? `يتم عرض ${onlineResults.length} من إجمالي ${onlineTotal.toLocaleString()} مشروع معتمد`
                        : `Displaying ${onlineResults.length} of ${onlineTotal.toLocaleString()} verified community projects`}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Global Ecosystem Connected Hub */}
        <ConnectedFeaturesHub />

      </div>
    </div>
  );
}
