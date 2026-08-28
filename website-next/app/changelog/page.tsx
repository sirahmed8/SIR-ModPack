"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { 
  History, 
  ArrowLeft, 
  Sparkles, 
  ExternalLink, 
  Loader2, 
  Tag, 
  Download, 
  Search, 
  SlidersHorizontal, 
  ChevronDown, 
  ChevronUp, 
  Check, 
  Copy, 
  Share2, 
  Layers, 
  Cpu, 
  Flame, 
  Radio 
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useEcosystem } from "@/lib/context";
import { fetchChangelogEntries, ChangelogEntry, DEFAULT_MASTER_CHANGELOG } from "@/lib/firebase";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";

const FILTER_TAGS = ["All", "Launcher", "Shaders", "Packs", "Cloud", "PvP"];

export default function ChangelogPage() {
  const { t, dir, lang } = useEcosystem();
  const [releases, setReleases] = useState<ChangelogEntry[]>(DEFAULT_MASTER_CHANGELOG);
  const [loading, setLoading] = useState(true);
  
  // 100x Search & Filter State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTag, setSelectedTag] = useState("All");
  const [expandedReleases, setExpandedReleases] = useState<Record<string, boolean>>({});
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    async function loadChangelogs() {
      try {
        const data = await fetchChangelogEntries();
        setReleases(data);
        // Expand all by default
        const initialExpanded: Record<string, boolean> = {};
        data.forEach((r, idx) => {
          initialExpanded[r.id || `rel_${idx}`] = true;
        });
        setExpandedReleases(initialExpanded);
      } catch (e) {
        console.error("Failed to load changelogs:", e);
      } finally {
        setLoading(false);
      }
    }
    loadChangelogs();
  }, []);

  const toggleExpand = (id: string) => {
    setExpandedReleases(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleExpandAll = (expand: boolean) => {
    const updated: Record<string, boolean> = {};
    releases.forEach((r, idx) => {
      updated[r.id || `rel_${idx}`] = expand;
    });
    setExpandedReleases(updated);
  };

  const handleCopyLink = (version: string) => {
    if (typeof window !== "undefined") {
      const url = `${window.location.origin}/changelog#${encodeURIComponent(version)}`;
      navigator.clipboard.writeText(url);
      setCopiedId(version);
      setTimeout(() => setCopiedId(null), 2500);
    }
  };

  // 100x Filtered Releases
  const filteredReleases = useMemo(() => {
    return releases.filter((rel) => {
      const q = searchQuery.toLowerCase().trim();
      const headline = ((lang === "ar" && rel.headlineAr) ? rel.headlineAr : rel.headline).toLowerCase();
      const version = rel.version.toLowerCase();
      const tag = ((lang === "ar" && rel.tagAr) ? rel.tagAr : (rel.tag || "")).toLowerCase();
      
      const itemsMatch = rel.categories.some(cat => {
        const catTitle = ((lang === "ar" && cat.titleAr) ? cat.titleAr : cat.title).toLowerCase();
        const itemsText = ((lang === "ar" && cat.itemsAr && cat.itemsAr.length > 0) ? cat.itemsAr : cat.items).join(" ").toLowerCase();
        return catTitle.includes(q) || itemsText.includes(q);
      });

      const matchesSearch = !q || version.includes(q) || headline.includes(q) || tag.includes(q) || itemsMatch;

      if (!matchesSearch) return false;

      if (selectedTag === "All") return true;
      if (selectedTag === "Launcher") return rel.categories.some(c => c.title.toLowerCase().includes("launcher") || (c.titleAr && c.titleAr.includes("المشغل")));
      if (selectedTag === "Shaders") return rel.categories.some(c => c.title.toLowerCase().includes("shader") || (c.titleAr && c.titleAr.includes("شيدرز")));
      if (selectedTag === "Packs") return rel.categories.some(c => c.title.toLowerCase().includes("pack") || (c.titleAr && c.titleAr.includes("حزمة") || c.titleAr?.includes("ريسورس")));
      if (selectedTag === "Cloud") return rel.categories.some(c => c.title.toLowerCase().includes("cloud") || (c.titleAr && c.titleAr.includes("سحابي")));
      if (selectedTag === "PvP") return rel.categories.some(c => c.title.toLowerCase().includes("pvp") || (c.titleAr && c.titleAr.includes("بفب")));

      return true;
    });
  }, [releases, searchQuery, selectedTag, lang]);

  // Statistics
  const totalFeatures = useMemo(() => {
    return releases.reduce((acc, rel) => {
      return acc + rel.categories.reduce((cAcc, cat) => cAcc + cat.items.length, 0);
    }, 0);
  }, [releases]);

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-[#07090e] text-slate-900 dark:text-zinc-100 py-12 px-4 sm:px-6 lg:px-8 font-sans transition-colors duration-300">
      <div className="max-w-5xl mx-auto space-y-8">

        {/* Top Navigation & Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs font-bold text-slate-700 dark:text-zinc-300 hover:text-cyan-600 dark:hover:text-white hover:border-cyan-500/50 transition-all shadow-sm cursor-pointer"
          >
            <ArrowLeft className={`w-4 h-4 ${dir === "rtl" ? "rotate-180" : ""}`} />
            <span>{lang === "ar" ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>

          {/* Quick Metrics Badge */}
          <div className="flex items-center gap-3 text-xs font-mono">
            <span className="px-3 py-1 rounded-xl bg-cyan-100 dark:bg-cyan-500/10 border border-cyan-300 dark:border-cyan-500/30 text-cyan-800 dark:text-cyan-400 font-bold shadow-xs">
              {releases.length} {lang === "ar" ? "إصدارات منشورة" : "Releases"}
            </span>
            <span className="hidden sm:inline-flex px-3 py-1 rounded-xl bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/30 text-emerald-800 dark:text-emerald-400 font-bold shadow-xs">
              {totalFeatures}+ {lang === "ar" ? "ميزة وتقنية مدمجة" : "Shipped Modules"}
            </span>
          </div>
        </div>

        {/* Header Title & Subtitle */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-100 dark:bg-cyan-500/10 border border-cyan-300 dark:border-cyan-500/30 text-cyan-800 dark:text-cyan-400 text-xs font-bold uppercase tracking-wider shadow-xs">
            <History className="w-3.5 h-3.5" />
            <span>{lang === "ar" ? "أرشيف الإصدارات التأسيسية" : "Genesis Release Archives"}</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white tracking-tight">
            {lang === "ar" ? "سجل تحديثات المنظومة الشامل" : "Ecosystem Master Changelog"}
          </h1>
          <p className="text-sm sm:text-base text-slate-600 dark:text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            {lang === "ar" 
              ? "سجل تقني فوري ومحدث لجميع ميزات المحرك، الشيدرز الضوئية، المودات، والتحسينات السحابية لمنظومة SIR." 
              : "Live technical timeline of all features, shaders, mods, binaries, and cloud integrations across the SIR Ecosystem."}
          </p>
        </div>

        {/* 🌟 100x SEARCH BAR & FILTER PILLS */}
        <div className="p-5 rounded-3xl bg-white dark:bg-zinc-950/80 border border-slate-200 dark:border-zinc-800 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row items-center gap-3">
            {/* Search Input */}
            <div className="relative flex-1 w-full">
              <Search className={`w-4 h-4 text-slate-400 absolute ${lang === "ar" ? "right-4" : "left-4"} top-1/2 -translate-y-1/2 pointer-events-none z-10`} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={lang === "ar" ? "بحث في التحديثات والميزات والشيدرز والمودات..." : "Search releases, shaders, mods, features, and fixes..."}
                className={`w-full ${lang === "ar" ? "pr-11 pl-10" : "pl-11 pr-10"} py-3 rounded-2xl bg-slate-50 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-cyan-500 dark:focus:border-cyan-400 transition-colors shadow-sm`}
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className={`absolute ${lang === "ar" ? "left-3" : "right-3"} top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-900 dark:hover:text-white p-1`}
                >
                  ✕
                </button>
              )}
            </div>

            {/* Expand / Collapse All */}
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => handleExpandAll(true)}
                className="px-3 py-2.5 rounded-xl bg-slate-100 dark:bg-zinc-900 hover:bg-slate-200 dark:hover:bg-zinc-800 border border-slate-200 dark:border-zinc-800 text-xs text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white font-bold transition-all cursor-pointer shadow-xs"
              >
                {lang === "ar" ? "توسيع الكل" : "Expand All"}
              </button>
              <button
                type="button"
                onClick={() => handleExpandAll(false)}
                className="px-3 py-2.5 rounded-xl bg-slate-100 dark:bg-zinc-900 hover:bg-slate-200 dark:hover:bg-zinc-800 border border-slate-200 dark:border-zinc-800 text-xs text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white font-bold transition-all cursor-pointer shadow-xs"
              >
                {lang === "ar" ? "طي الكل" : "Collapse All"}
              </button>
            </div>
          </div>

          {/* Filter Category Pills */}
          <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-200 dark:border-zinc-800/60">
            <span className="text-[11px] font-mono text-slate-500 dark:text-zinc-500 uppercase mr-1 font-bold">
              {lang === "ar" ? "التصنيف:" : "Filter:"}
            </span>
            {FILTER_TAGS.map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => setSelectedTag(tag)}
                className={`px-3 py-1 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs ${
                  selectedTag === tag
                    ? "bg-cyan-500 text-slate-950 font-black shadow-sm"
                    : "bg-slate-100 dark:bg-zinc-900 text-slate-700 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-zinc-800"
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3 text-slate-500 dark:text-zinc-500">
            <Loader2 className="w-7 h-7 animate-spin text-cyan-500 dark:text-cyan-400" />
            <span className="text-xs font-mono">{lang === "ar" ? "جاري مزامنة أرشيف التحديثات..." : "Syncing latest release archives..."}</span>
          </div>
        ) : filteredReleases.length === 0 ? (
          <div className="py-16 text-center rounded-3xl bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 p-8 space-y-3 shadow-sm">
            <Search className="w-8 h-8 text-slate-400 dark:text-zinc-600 mx-auto" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              {lang === "ar" ? "لم يتم العثور على نتائج مطابقة" : "No matching changelogs found"}
            </h3>
            <p className="text-xs text-slate-500 dark:text-zinc-400">
              {lang === "ar" ? "جرب البحث بكلمة مفتاحية مختلفة." : "Try adjusting your search terms or filter selection."}
            </p>
          </div>
        ) : (
          /* Timeline */
          <div className="relative border-l-2 border-cyan-400/40 dark:border-cyan-500/20 ml-4 sm:ml-6 space-y-12">
            {filteredReleases.map((rel, idx) => {
              const relKey = rel.id || `rel_${idx}`;
              const isExpanded = expandedReleases[relKey] !== false;
              const headline = (lang === "ar" && rel.headlineAr) ? rel.headlineAr : rel.headline;
              const tag = (lang === "ar" && rel.tagAr) ? rel.tagAr : rel.tag;
              const date = (lang === "ar" && rel.dateAr) ? rel.dateAr : rel.date;
              const buttonLabel = (lang === "ar" && rel.buttonLabelAr) ? rel.buttonLabelAr : rel.buttonLabel;

              return (
                <div key={relKey} id={rel.version} className="relative pl-6 sm:pl-8">
                  {/* Timeline Node */}
                  <div className="absolute -left-[9px] top-2.5 w-4 h-4 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(0,229,255,0.8)] border-2 border-white dark:border-black" />

                  {/* Content Box */}
                  <div className="bg-white dark:bg-zinc-950/90 rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-zinc-800 hover:border-cyan-400 dark:hover:border-cyan-500/40 shadow-xl backdrop-blur-xl space-y-6 transition-colors">
                    
                    {/* Header Row */}
                    <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-zinc-800">
                      <div>
                        <div className="flex items-center gap-3 flex-wrap">
                          <span className="text-2xl font-black text-slate-900 dark:text-white tracking-tight">{rel.version}</span>
                          {tag && (
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-300 dark:border-emerald-500/30 text-emerald-800 dark:text-emerald-400 shadow-xs">
                              {tag}
                            </span>
                          )}
                          <span className="text-xs font-mono text-slate-500 dark:text-zinc-500 font-bold">{date}</span>
                        </div>
                        <h3 className="text-sm font-black text-cyan-600 dark:text-cyan-400 mt-1">{headline}</h3>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center gap-2">
                        {/* Copy Link */}
                        <button
                          type="button"
                          onClick={() => handleCopyLink(rel.version)}
                          className="p-2 rounded-xl bg-slate-100 dark:bg-zinc-900 hover:bg-slate-200 dark:hover:bg-zinc-800 border border-slate-200 dark:border-zinc-800 text-slate-700 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer shadow-xs"
                          title="Copy Release Link"
                        >
                          {copiedId === rel.version ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 stroke-[3]" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>

                        {/* Expand/Collapse Toggle */}
                        <button
                          type="button"
                          onClick={() => toggleExpand(relKey)}
                          className="p-2 rounded-xl bg-slate-100 dark:bg-zinc-900 hover:bg-slate-200 dark:hover:bg-zinc-800 border border-slate-200 dark:border-zinc-800 text-slate-700 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer shadow-xs"
                          title={isExpanded ? "Collapse" : "Expand"}
                        >
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </button>

                        {/* Download CTA Button */}
                        {buttonLabel && rel.buttonUrl && (
                          <a
                            href={rel.buttonUrl}
                            target={rel.buttonUrl.startsWith("http") ? "_blank" : undefined}
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-black text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer"
                          >
                            <span>{buttonLabel}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Categorized Features with Smooth Accordion */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="space-y-4 overflow-hidden"
                        >
                          {rel.categories.map((cat, cIdx) => {
                            const catTitle = (lang === "ar" && cat.titleAr) ? cat.titleAr : cat.title;
                            const catItems = (lang === "ar" && cat.itemsAr && cat.itemsAr.length > 0) ? cat.itemsAr : cat.items;

                            return (
                              <div key={cIdx} className="p-4.5 rounded-2xl bg-slate-50/80 dark:bg-zinc-900/60 border border-slate-200/90 dark:border-zinc-800/80 space-y-2.5 shadow-xs">
                                <h4 className="text-xs sm:text-sm font-black text-slate-900 dark:text-white flex items-center gap-2">
                                  <span>{catTitle}</span>
                                  <span className="text-[10px] text-slate-500 dark:text-zinc-500 font-mono font-bold">({catItems.length})</span>
                                </h4>
                                <ul className="space-y-2">
                                  {catItems.map((item, iIdx) => (
                                    <li key={iIdx} className="flex items-start gap-2.5 text-xs text-slate-700 dark:text-zinc-300 leading-relaxed font-medium">
                                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 dark:bg-cyan-400 mt-1.5 shrink-0" />
                                      <span>{item}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            );
                          })}
                        </motion.div>
                      )}
                    </AnimatePresence>

                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Connected Ecosystem Hub */}
        <ConnectedFeaturesHub currentPath="/changelog" />

      </div>
    </main>
  );
}
