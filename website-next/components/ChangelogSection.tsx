"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";
import { fetchChangelogEntries, ChangelogEntry, DEFAULT_MASTER_CHANGELOG } from "@/lib/firebase";
import { History, ArrowRight, Sparkles, ExternalLink, Check } from "lucide-react";
import { motion } from "framer-motion";

export function ChangelogSection() {
  const { t, dir, lang } = useEcosystem();
  const [entries, setEntries] = useState<ChangelogEntry[]>(DEFAULT_MASTER_CHANGELOG);

  useEffect(() => {
    fetchChangelogEntries().then(data => {
      if (data && data.length > 0) {
        setEntries(data.slice(0, 2));
      }
    });
  }, []);

  return (
    <section id="changelog" className="py-20 lg:py-28 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/30 text-cyan-700 dark:text-[#00e5ff] text-xs font-bold uppercase tracking-wider mb-4 shadow-sm">
            <History className="w-3.5 h-3.5" />
            <span>{lang === "ar" ? "سجل التحديثات المباشر" : "Live Release Changelog"}</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white mb-4 tracking-tight">
            {lang === "ar" ? "أحدث التحديثات والتحسينات" : "Ecosystem Changelog Feed"}
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-gray-300">
            {lang === "ar" ? "متابعة حية لجميع الإطلاقات والميزات والشيدرز التي تمت إضافتها للمنظومة." : "Stay up-to-date with technical patch notes, shaders, performance fixes, and release milestones."}
          </p>
        </div>

        {/* Dynamic Changelog Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-10">
          {entries.map((entry, idx) => {
            const headline = (lang === "ar" && entry.headlineAr) ? entry.headlineAr : entry.headline;
            const tag = (lang === "ar" && entry.tagAr) ? entry.tagAr : entry.tag;

            return (
              <motion.div
                key={entry.id || idx}
                whileHover={{ y: -5 }}
                className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 hover:border-cyan-500/40 transition-all shadow-xl backdrop-blur-xl flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xl font-black text-slate-900 dark:text-white">{entry.version}</span>
                    {tag && (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-[#38ef7d]">
                        {tag}
                      </span>
                    )}
                  </div>
                  
                  <h4 className="text-sm font-bold text-cyan-600 dark:text-[#00e5ff] mb-4">{headline}</h4>

                  <div className="space-y-2.5 mb-6">
                    {entry.categories.slice(0, 3).map((cat, cIdx) => {
                      const catTitle = (lang === "ar" && cat.titleAr) ? cat.titleAr : cat.title;
                      const firstItem = (lang === "ar" && cat.itemsAr && cat.itemsAr[0]) ? cat.itemsAr[0] : cat.items[0];

                      return (
                        <div key={cIdx} className="text-xs text-slate-600 dark:text-gray-300">
                          <strong className="text-slate-800 dark:text-white block mb-0.5">{catTitle}</strong>
                          <span className="line-clamp-1">{firstItem}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-400">{entry.date}</span>
                  <Link
                    href="/changelog"
                    className="inline-flex items-center gap-1 text-xs font-bold text-cyan-600 dark:text-[#00e5ff] hover:underline"
                  >
                    <span>{lang === "ar" ? "قراءة التقرير الكامل" : "Read Full Notes"}</span>
                    <ArrowRight className={`w-3.5 h-3.5 ${dir === "rtl" ? "rotate-180" : ""}`} />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* View All Button */}
        <div className="text-center">
          <Link
            href="/changelog"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-white hover:bg-slate-50 dark:bg-slate-900 dark:hover:bg-slate-800 border border-slate-300 dark:border-slate-800 text-slate-900 dark:text-white text-xs font-black transition-all shadow-md hover:shadow-lg cursor-pointer"
          >
            <History className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
            <span>{lang === "ar" ? "عرض أرشيف التحديثات بالكامل (Changelog)" : "View Complete Changelog Archives"}</span>
            <ArrowRight className={`w-4 h-4 text-slate-500 dark:text-gray-400 ${dir === "rtl" ? "rotate-180" : ""}`} />
          </Link>
        </div>

      </div>
    </section>
  );
}
