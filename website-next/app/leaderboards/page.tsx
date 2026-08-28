"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Trophy, 
  Swords, 
  Shield, 
  Medal, 
  ArrowLeft, 
  ArrowRight, 
  Flame, 
  Target, 
  Zap, 
  Crown,
  Sparkles,
  PlusCircle,
  CheckCircle2,
  RefreshCw,
  Clock,
  UserCheck,
  Award
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";
import { CyberSelect } from "@/components/CyberSelect";
import { 
  BenchmarkRecord, 
  fetchAllLeaderboardRecords 
} from "@/lib/leaderboard";

export default function LeaderboardsPage() {
  const { lang, user } = useEcosystem();
  const [selectedCategory, setSelectedCategory] = useState<"all" | "cps" | "aim" | "reaction">("all");
  const [records, setRecords] = useState<BenchmarkRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const isAr = lang === "ar";

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchAllLeaderboardRecords();
      setRecords(data);
    } catch (err) {
      console.warn("Could not fetch leaderboard records", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // Listen to live benchmark score events from trainer
    const handleSavedScore = () => {
      loadData();
    };
    window.addEventListener("sir_benchmark_saved", handleSavedScore);
    return () => {
      window.removeEventListener("sir_benchmark_saved", handleSavedScore);
    };
  }, []);


  // Sort & Filter
  const filtered = records
    .filter(r => {
      if (selectedCategory === "all") return true;
      return r.category === selectedCategory;
    })
    .sort((a, b) => {
      if (a.category === b.category) {
        if (a.category === "cps") {
          return b.score - a.score; // Highest CPS is #1
        }
        return a.score - b.score; // Lowest ms latency is #1
      }
      return b.timestamp - a.timestamp;
    });

  const getMedalBadge = (index: number) => {
    if (index === 0) {
      return (
        <div className="min-w-[44px] h-9 px-2.5 rounded-xl bg-amber-500/15 border border-amber-500/50 text-amber-300 font-black flex items-center justify-center gap-1 text-xs shadow-[0_0_14px_rgba(245,158,11,0.25)] shrink-0 font-mono">
          <span className="text-sm leading-none">🥇</span>
          <span className="font-black text-[13px] leading-none">#1</span>
        </div>
      );
    }
    if (index === 1) {
      return (
        <div className="min-w-[44px] h-9 px-2.5 rounded-xl bg-slate-300/15 border border-slate-300/50 text-slate-200 font-black flex items-center justify-center gap-1 text-xs shadow-[0_0_14px_rgba(226,232,240,0.2)] shrink-0 font-mono">
          <span className="text-sm leading-none">🥈</span>
          <span className="font-black text-[13px] leading-none">#2</span>
        </div>
      );
    }
    if (index === 2) {
      return (
        <div className="min-w-[44px] h-9 px-2.5 rounded-xl bg-amber-700/20 border border-amber-600/50 text-amber-400 font-black flex items-center justify-center gap-1 text-xs shadow-[0_0_14px_rgba(180,83,9,0.2)] shrink-0 font-mono">
          <span className="text-sm leading-none">🥉</span>
          <span className="font-black text-[13px] leading-none">#3</span>
        </div>
      );
    }
    return (
      <div className="min-w-[44px] h-9 px-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-slate-400 font-bold flex items-center justify-center text-xs shrink-0 font-mono">
        <span className="font-bold text-xs leading-none">#{index + 1}</span>
      </div>
    );
  };

  return (
    <AuthGate featureName="Leaderboards & Rankings" featureNameAr="لوحة المتصدرين والتصنيفات">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="badge-tag bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-400 border border-amber-300 dark:border-amber-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
              <Trophy className="w-3.5 h-3.5" />
              <span>{isAr ? "لوحة الصدارة وقاعدة بيانات الأبطال الحية" : "Live Database Leaderboards"}</span>
            </span>
          </div>
        </div>

        {/* Hero Section */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-500 via-cyan-500 to-emerald-500 dark:from-amber-400 dark:via-cyan-400 dark:to-emerald-400">
            {isAr ? "لوحة الصدارة العالمية والأرقام القياسية" : "Verified Competitive Leaderboards"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "يتم تسجيل درجاتك تلقائياً وبشكل فوري بمجرد اللعب في قسم التدريب (CPS, Aim, Reaction). نافس أفضل اللاعبين وتصدر الترتيب العالمي!"
              : "Your scores in the Trainer (CPS, Aim, Reaction) are automatically recorded and synced in real-time. Benchmark your skills and claim your spot!"}
          </p>
        </div>

        {/* Action Buttons & Category Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 backdrop-blur-xl shadow-lg">
          {/* Category Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
            {[
              { id: "all", labelEn: "All Records", labelAr: "جميع الأرقام" },
              { id: "cps", labelEn: "⚡ CPS Speed", labelAr: "⚡ سرعة النقر CPS" },
              { id: "aim", labelEn: "🎯 Aim Reflex", labelAr: "🎯 سرعة الإيم" },
              { id: "reaction", labelEn: "⏱️ Reaction (ms)", labelAr: "⏱️ رد الفعل" }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedCategory(tab.id as any)}
                className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                  selectedCategory === tab.id
                    ? "bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
                    : "bg-slate-100 dark:bg-slate-900/80 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-800"
                }`}
              >
                {isAr ? tab.labelAr : tab.labelEn}
              </button>
            ))}
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <Link
              href="/trainer"
              className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black transition-all flex items-center gap-1.5 shadow-md shadow-cyan-500/20 active:scale-95"
            >
              <Swords className="w-3.5 h-3.5" />
              <span>{isAr ? "تدرب الآن وسجّل نتيجتك الحقيقية" : "Play in Trainer"}</span>
            </Link>
            <button
              onClick={loadData}
              className="p-2 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-all cursor-pointer"
              title="Refresh Leaderboard"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-cyan-500" : ""}`} />
            </button>
          </div>
        </div>

        {/* Leaderboard Table / Cards */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-2 text-xs text-slate-500 dark:text-slate-400 font-mono">
            <span>{isAr ? "ترتيب قاعدة البيانات العالمية الحية" : "Global Database Rankings Feed"}</span>
            <span>{filtered.length} {isAr ? "أرقام مسجلة" : "Verified Records"}</span>
          </div>

          {loading ? (
            <div className="p-16 rounded-3xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 text-center space-y-3">
              <div className="w-8 h-8 border-2 border-amber-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">{isAr ? "جاري جلب أرقام الصدارة..." : "Loading live leaderboard data..."}</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-16 rounded-3xl bg-white dark:bg-[#0c101a]/90 border border-slate-200 dark:border-slate-800 text-center space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-500 flex items-center justify-center mx-auto shadow-lg shadow-amber-500/10">
                <Trophy className="w-7 h-7" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
                  {isAr ? "لا توجد أرقام مسجلة في هذا التصنيف بعد" : "No Verified Benchmark Records Yet"}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto leading-relaxed">
                  {isAr 
                    ? "النتائج تُسجل تلقائياً وبدقة 100% بمجرد إكمال اختبار (CPS, Aim, Reaction) في قسم التدريب بدون أي أرقام وهمية." 
                    : "Scores are automatically and securely recorded in real-time when completing genuine runs in the PvP Trainer."}
                </p>
              </div>
              <Link
                href="/trainer"
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-black shadow-lg shadow-cyan-500/20 active:scale-95 transition-all"
              >
                <Swords className="w-4 h-4" />
                <span>{isAr ? "ابدأ التدريب وسجّل رقمك" : "Play in PvP Trainer"}</span>
              </Link>
            </div>
          ) : (
            <div className="space-y-2.5">
              {filtered.map((record, index) => (
                <div
                  key={record.id || index}
                  className={`p-4 rounded-2xl border transition-all flex items-center justify-between gap-4 shadow-sm ${
                    record.isUserRun 
                      ? "bg-cyan-50 dark:bg-cyan-950/20 border-cyan-400 dark:border-cyan-500/40 ring-1 ring-cyan-500/30" 
                      : "bg-white dark:bg-[#0c101a]/90 border-slate-200 dark:border-slate-800/80 hover:border-slate-300 dark:hover:border-slate-700"
                  }`}
                >
                  {/* Left Info */}
                  <div className="flex items-center gap-3.5 min-w-0">
                    {getMedalBadge(index)}
                    <img
                      src={record.avatarUrl}
                      alt={record.username}
                      className="w-11 h-11 rounded-2xl object-cover bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shrink-0 shadow-sm"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = "https://mc-heads.net/avatar/Steve/64";
                      }}
                    />
                    <div className="min-w-0 space-y-0.5">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className="text-sm font-bold text-slate-900 dark:text-white truncate">{record.username}</h4>
                        {record.rankTitle && (
                          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-amber-700 dark:text-amber-300">
                            {record.rankTitle}
                          </span>
                        )}
                        {record.isUserRun && (
                          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-400 border border-cyan-300 dark:border-cyan-800/50 text-[9px] font-bold rounded-full px-2 py-0.5">
                            {isAr ? "رقمك الخاص" : "Your Run"}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 font-mono">
                        <span className="capitalize">{record.category.toUpperCase()} Mode</span>
                        <span>•</span>
                        <span>{new Date(record.timestamp).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  {/* Right Score */}
                  <div className="text-right shrink-0">
                    <span className="text-base sm:text-lg font-black font-mono text-emerald-600 dark:text-emerald-400 block">
                      {record.formattedScore}
                    </span>
                    {record.accuracy !== undefined && (
                      <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
                        {record.accuracy}% {isAr ? "دقة" : "Accuracy"}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <ConnectedFeaturesHub currentPath="/leaderboards" />

      </div>
    </div>
    </AuthGate>);
}