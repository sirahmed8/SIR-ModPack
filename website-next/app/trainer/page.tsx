"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState, useEffect, useRef, useCallback } from "react";
import Link from "next/link";
import { 
  Swords, 
  Zap, 
  Timer, 
  Award, 
  RotateCcw, 
  ArrowLeft, 
  ArrowRight, 
  Target, 
  Sparkles,
  Flame,
  Trophy,
  MousePointerClick,
  Crosshair,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";
import { recordBenchmarkScore } from "@/lib/leaderboard";

interface AimTarget {
  id: number;
  x: number; // percentage 10-90
  y: number; // percentage 15-85
  spawnTime: number;
  size: number; // in pixels
}

interface AimLevelConfig {
  level: number;
  name: string;
  nameAr: string;
  totalTargets: number;
  targetSize: number;
  timeWindowSec: number;
  badge: string;
  color: string;
}

const AIM_LEVELS: AimLevelConfig[] = [
  {
    level: 1,
    name: "Novice Duelist",
    nameAr: "مبارز مبتدئ",
    totalTargets: 5,
    targetSize: 56,
    timeWindowSec: 2.5,
    badge: "Level 1 • Warmup",
    color: "from-cyan-500 to-blue-600"
  },
  {
    level: 2,
    name: "Competitive PvP",
    nameAr: "محترف PvP تنافسي",
    totalTargets: 10,
    targetSize: 42,
    timeWindowSec: 1.6,
    badge: "Level 2 • Speed",
    color: "from-emerald-500 to-teal-600"
  },
  {
    level: 3,
    name: "Hypixel Ranked Master",
    nameAr: "ماستر بطولات الـ PvP",
    totalTargets: 15,
    targetSize: 32,
    timeWindowSec: 1.1,
    badge: "Level 3 • Ultra Fast",
    color: "from-amber-500 to-rose-600"
  }
];

export default function TrainerPage() {
  const { lang, user } = useEcosystem();
  const [testMode, setTestMode] = useState<"cps" | "aim" | "reaction">("cps");
  const [autoSaveToast, setAutoSaveToast] = useState<string | null>(null);

  const triggerScoreToast = (msg: string) => {
    setAutoSaveToast(msg);
    setTimeout(() => setAutoSaveToast(null), 3500);
  };
  
  // ==========================================
  // 1. CPS TEST STATE
  // ==========================================
  const [cpsDuration, setCpsDuration] = useState<number>(5);
  const [cpsClicks, setCpsClicks] = useState<number>(0);
  const [cpsTimeLeft, setCpsTimeLeft] = useState<number>(5);
  const [currentCps, setCurrentCps] = useState<number>(0);
  const [isCpsRunning, setIsCpsRunning] = useState<boolean>(false);
  const [isCpsFinished, setIsCpsFinished] = useState<boolean>(false);
  const [bestCps, setBestCps] = useState<number>(0);
  
  const cpsStartTimeRef = useRef<number | null>(null);
  const cpsRafRef = useRef<number | null>(null);
  const cpsClicksRef = useRef<number>(0);
  const cpsDurationRef = useRef<number>(5);
  const isCpsRunningRef = useRef<boolean>(false);

  // ==========================================
  // 2. MULTI-TARGET AIM TRAINER STATE
  // ==========================================
  const [selectedAimLevel, setSelectedAimLevel] = useState<number>(1);
  const [isAimActive, setIsAimActive] = useState<boolean>(false);
  const [isAimFinished, setIsAimFinished] = useState<boolean>(false);
  const [currentTarget, setCurrentTarget] = useState<AimTarget | null>(null);
  const [targetIndex, setTargetIndex] = useState<number>(0);
  const [hitTimes, setHitTimes] = useState<number[]>([]);
  const [missedClicks, setMissedClicks] = useState<number>(0);
  const [totalClicksInAim, setTotalClicksInAim] = useState<number>(0);
  const [bestAimAvgMs, setBestAimAvgMs] = useState<number | null>(null);

  const aimTargetTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentTargetRef = useRef<AimTarget | null>(null);
  const isAimActiveRef = useRef<boolean>(false);
  const hitTimesRef = useRef<number[]>([]);
  const targetIndexRef = useRef<number>(0);

  // ==========================================
  // 3. FLASH REACTION STATE
  // ==========================================
  const [reactionState, setReactionState] = useState<"idle" | "waiting" | "early" | "ready" | "clicked">("idle");
  const [reactionStartTime, setReactionStartTime] = useState<number>(0);
  const [reactionTime, setReactionTime] = useState<number | null>(null);
  const [bestReaction, setBestReaction] = useState<number | null>(null);
  const reactionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isAr = lang === "ar";

  // Clean up all timers on unmount
  useEffect(() => {
    return () => {
      if (cpsRafRef.current) cancelAnimationFrame(cpsRafRef.current);
      if (aimTargetTimeoutRef.current) clearTimeout(aimTargetTimeoutRef.current);
      if (reactionTimeoutRef.current) clearTimeout(reactionTimeoutRef.current);
    };
  }, []);

  // Synchronize duration
  useEffect(() => {
    cpsDurationRef.current = cpsDuration;
    if (!isCpsRunningRef.current) {
      setCpsTimeLeft(cpsDuration);
    }
  }, [cpsDuration]);

  // ==========================================
  // CPS TIMING ENGINE
  // ==========================================
  const updateCpsLoop = useCallback(() => {
    if (!cpsStartTimeRef.current || !isCpsRunningRef.current) return;

    const now = performance.now();
    const elapsedSeconds = (now - cpsStartTimeRef.current) / 1000;
    const remaining = Math.max(0, cpsDurationRef.current - elapsedSeconds);

    setCpsTimeLeft(Number(remaining.toFixed(1)));

    if (elapsedSeconds > 0) {
      setCurrentCps(Number((cpsClicksRef.current / elapsedSeconds).toFixed(1)));
    }

    if (elapsedSeconds >= cpsDurationRef.current) {
      isCpsRunningRef.current = false;
      setIsCpsRunning(false);
      setIsCpsFinished(true);
      setCpsTimeLeft(0);

      const finalScore = Number((cpsClicksRef.current / cpsDurationRef.current).toFixed(2));
      setCurrentCps(finalScore);
      setBestCps(prev => Math.max(prev, finalScore));
      soundFx.playCelebration();

      // Auto-record to Global & Local Leaderboards
      const username = user?.displayName || user?.email?.split('@')[0] || "SirPlayer";
      const rank = finalScore >= 16 ? "👑 S+ GODLIKE" : (finalScore >= 12 ? "⚡ S TIER" : "⚔️ A TIER");
      recordBenchmarkScore(username, "cps", finalScore, 100, rank);
      triggerScoreToast(isAr ? `✓ تم تسجيل ${finalScore} CPS تلقائياً في لوحة الصدارة!` : `✓ Automatically recorded ${finalScore} CPS to Leaderboard!`);
      return;
    }

    cpsRafRef.current = requestAnimationFrame(updateCpsLoop);
  }, [isAr, user]);

  const handleCpsClick = (e: React.MouseEvent | React.TouchEvent) => {
    if (e.type === 'touchstart') e.preventDefault();
    if (isCpsFinished) return;

    soundFx.playClick();

    if (!isCpsRunningRef.current) {
      isCpsRunningRef.current = true;
      setIsCpsRunning(true);
      setIsCpsFinished(false);
      cpsClicksRef.current = 1;
      setCpsClicks(1);
      cpsStartTimeRef.current = performance.now();
      
      if (cpsRafRef.current) cancelAnimationFrame(cpsRafRef.current);
      cpsRafRef.current = requestAnimationFrame(updateCpsLoop);
      return;
    }

    cpsClicksRef.current += 1;
    setCpsClicks(cpsClicksRef.current);
  };

  const handleResetCps = () => {
    soundFx.playClick();
    if (cpsRafRef.current) cancelAnimationFrame(cpsRafRef.current);
    isCpsRunningRef.current = false;
    cpsStartTimeRef.current = null;
    cpsClicksRef.current = 0;
    setIsCpsRunning(false);
    setIsCpsFinished(false);
    setCpsTimeLeft(cpsDuration);
    setCpsClicks(0);
    setCurrentCps(0);
  };

  // ==========================================
  // MULTI-TARGET AIM TRAINER LOGIC
  // ==========================================
  const spawnNextTarget = useCallback((nextIdx: number, levelCfg: AimLevelConfig) => {
    if (nextIdx >= levelCfg.totalTargets) {
      // Completed all targets for this level!
      isAimActiveRef.current = false;
      setIsAimActive(false);
      setIsAimFinished(true);
      setCurrentTarget(null);
      currentTargetRef.current = null;

      const validTimes = hitTimesRef.current;
      if (validTimes.length > 0) {
        const avg = Math.round(validTimes.reduce((a, b) => a + b, 0) / validTimes.length);
        setBestAimAvgMs(prev => (prev === null || avg < prev ? avg : prev));

        // Auto-record to Global & Local Leaderboards
        const accuracy = totalClicksInAim > 0 
          ? Math.round(((totalClicksInAim - missedClicks) / totalClicksInAim) * 100) 
          : 100;
        const rankInfo = getAimRank(avg, accuracy);
        const username = user?.displayName || user?.email?.split('@')[0] || "SirPlayer";
        recordBenchmarkScore(username, "aim", avg, accuracy, rankInfo.rank);
        triggerScoreToast(isAr ? `✓ تم تسجيل ${avg}ms Reflex تلقائياً في لوحة الصدارة!` : `✓ Automatically recorded ${avg}ms Reflex to Leaderboard!`);
      }
      soundFx.playCelebration();
      return;
    }

    // Generate random x (12% - 88%), y (18% - 82%)
    const randomX = Math.floor(Math.random() * 76) + 12;
    const randomY = Math.floor(Math.random() * 64) + 18;

    const newTarget: AimTarget = {
      id: Date.now() + nextIdx,
      x: randomX,
      y: randomY,
      spawnTime: performance.now(),
      size: levelCfg.targetSize
    };

    targetIndexRef.current = nextIdx + 1;
    setTargetIndex(nextIdx + 1);
    currentTargetRef.current = newTarget;
    setCurrentTarget(newTarget);

    // Timeout if user is too slow to hit
    if (aimTargetTimeoutRef.current) clearTimeout(aimTargetTimeoutRef.current);
    aimTargetTimeoutRef.current = setTimeout(() => {
      if (isAimActiveRef.current && currentTargetRef.current?.id === newTarget.id) {
        // Missed target timeout penalty
        hitTimesRef.current.push(Math.round(levelCfg.timeWindowSec * 1000));
        setHitTimes([...hitTimesRef.current]);
        spawnNextTarget(nextIdx + 1, levelCfg);
      }
    }, levelCfg.timeWindowSec * 1000);

  }, []);

  const handleStartAimTest = () => {
    soundFx.playClick();
    const levelCfg = AIM_LEVELS.find(l => l.level === selectedAimLevel) || AIM_LEVELS[0];
    
    if (aimTargetTimeoutRef.current) clearTimeout(aimTargetTimeoutRef.current);
    isAimActiveRef.current = true;
    setIsAimActive(true);
    setIsAimFinished(false);
    setHitTimes([]);
    hitTimesRef.current = [];
    setMissedClicks(0);
    setTotalClicksInAim(0);
    targetIndexRef.current = 0;
    setTargetIndex(0);

    // Brief 300ms ready delay then spawn target 1
    setTimeout(() => {
      spawnNextTarget(0, levelCfg);
    }, 300);
  };

  const handleHitTarget = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isAimActiveRef.current || !currentTargetRef.current) return;

    soundFx.playClick();
    const hitDelta = Math.round(performance.now() - currentTargetRef.current.spawnTime);
    hitTimesRef.current.push(hitDelta);
    setHitTimes([...hitTimesRef.current]);
    setTotalClicksInAim(prev => prev + 1);

    if (aimTargetTimeoutRef.current) clearTimeout(aimTargetTimeoutRef.current);

    const levelCfg = AIM_LEVELS.find(l => l.level === selectedAimLevel) || AIM_LEVELS[0];
    spawnNextTarget(targetIndexRef.current, levelCfg);
  };

  const handleArenaMissClick = () => {
    if (!isAimActiveRef.current) return;
    soundFx.playClick();
    setMissedClicks(prev => prev + 1);
    setTotalClicksInAim(prev => prev + 1);
  };

  // ==========================================
  // FLASH REACTION TIME
  // ==========================================
  const startReactionTest = () => {
    soundFx.playClick();
    setReactionState("waiting");
    setReactionTime(null);
    const delay = Math.floor(Math.random() * 2500) + 1500;
    if (reactionTimeoutRef.current) clearTimeout(reactionTimeoutRef.current);
    reactionTimeoutRef.current = setTimeout(() => {
      setReactionState("ready");
      setReactionStartTime(performance.now());
    }, delay);
  };

  const handleReactionClick = () => {
    if (reactionState === "idle" || reactionState === "early" || reactionState === "clicked") {
      startReactionTest();
    } else if (reactionState === "waiting") {
      if (reactionTimeoutRef.current) clearTimeout(reactionTimeoutRef.current);
      soundFx.playClick();
      setReactionState("early");
    } else if (reactionState === "ready") {
      soundFx.playClick();
      const elapsed = Math.round(performance.now() - reactionStartTime);
      setReactionTime(elapsed);
      setReactionState("clicked");
      if (!bestReaction || elapsed < bestReaction) {
        setBestReaction(elapsed);
      }

      // Auto-record to Global & Local Leaderboards
      const username = user?.displayName || user?.email?.split('@')[0] || "SirPlayer";
      const rank = elapsed < 180 ? "⚡ S+ TIER" : (elapsed < 240 ? "⚡ S TIER" : "⚔️ A TIER");
      recordBenchmarkScore(username, "reaction", elapsed, 100, rank);
      triggerScoreToast(isAr ? `✓ تم تسجيل ${elapsed}ms استجابة تلقائياً في لوحة الصدارة!` : `✓ Automatically recorded ${elapsed}ms to Leaderboard!`);
    }
  };

  // Aim Analytics Calculation
  const averageAimMs = hitTimes.length > 0 ? Math.round(hitTimes.reduce((a, b) => a + b, 0) / hitTimes.length) : 0;
  const currentAimConfig = AIM_LEVELS.find(l => l.level === selectedAimLevel) || AIM_LEVELS[0];
  const aimAccuracy = totalClicksInAim > 0 
    ? Math.round(((totalClicksInAim - missedClicks) / totalClicksInAim) * 100) 
    : 100;

  const getAimRank = (avgMs: number, accuracy: number) => {
    if (avgMs < 250 && accuracy >= 90) return { rank: "S+ TIER (GODLIKE REFLEXES)", color: "text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-500/50 bg-amber-100 dark:bg-amber-950/60 font-black" };
    if (avgMs < 350 && accuracy >= 80) return { rank: "A TIER (COMPETITIVE DUELIST)", color: "text-cyan-800 dark:text-cyan-300 border-cyan-300 dark:border-cyan-500/50 bg-cyan-100 dark:bg-cyan-950/60 font-black" };
    if (avgMs < 480) return { rank: "B TIER (FAST REFLEXES)", color: "text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-500/50 bg-emerald-100 dark:bg-emerald-950/60 font-black" };
    return { rank: "C TIER (WARMUP)", color: "text-blue-800 dark:text-blue-300 border-blue-300 dark:border-blue-500/50 bg-blue-100 dark:bg-blue-950/60 font-black" };
  };

  return (
    <AuthGate featureName="PvP Aim & CPS Trainer" featureNameAr="مدرب التصويب وسرعة النقر">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-4xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-sm">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <Crosshair className="w-3.5 h-3.5" />
            {isAr ? "مختبر تدريب الإيم والسرعة ورد الفعل" : "PvP Aim, CPS & Reflex Trainer"}
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "مركز تدريب الـ PvP: الإيم، السرعة، ورد الفعل" : "PvP Reflex, Aim & Click Trainer"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "طور دقتك وسرعة استجابتك مع الأهداف العشوائية المتحركة، مستويات الصعوبة التصاعدية، واختبار نقرات CPS فائق الدقة."
              : "Sharpen crosshair accuracy with randomized dynamic targets, progressive difficulty tiers, and precision CPS benchmark testing."}
          </p>
        </div>

        {/* Mode Selector Tabs (3 Modes) */}
        <div className="flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => { soundFx.playClick(); setTestMode("cps"); }}
            className={`px-5 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shadow-sm ${testMode === 'cps' ? 'bg-cyan-500 text-slate-950 font-black shadow-md shadow-cyan-500/20' : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400'}`}
          >
            <Zap className="w-4 h-4" />
            <span>{isAr ? "سرعة النقر (CPS Speed)" : "CPS Click Speed"}</span>
          </button>
          
          <button
            onClick={() => { soundFx.playClick(); setTestMode("aim"); }}
            className={`px-5 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shadow-sm ${testMode === 'aim' ? 'bg-emerald-500 text-slate-950 font-black shadow-md shadow-emerald-500/20' : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-emerald-600 dark:hover:text-emerald-400'}`}
          >
            <Target className="w-4 h-4" />
            <span>{isAr ? "تدريب الإيم والأهداف العشوائية (Aim Arena)" : "Random Target Aim Arena"}</span>
          </button>

          <button
            onClick={() => { soundFx.playClick(); setTestMode("reaction"); startReactionTest(); }}
            className={`px-5 py-2.5 rounded-2xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shadow-sm ${testMode === 'reaction' ? 'bg-purple-600 dark:bg-purple-500 text-white font-black shadow-md shadow-purple-500/20' : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-purple-600 dark:hover:text-purple-400'}`}
          >
            <Timer className="w-4 h-4" />
            <span>{isAr ? "اختبار رد الفعل البصري (ms Flash)" : "Visual Reaction (ms)"}</span>
          </button>
        </div>

        {/* ======================================================== */}
        {/* MODE 1: CPS TEST BOX */}
        {/* ======================================================== */}
        {testMode === "cps" && (
          <div className="p-8 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-6 text-center shadow-xl">
            
            {/* Duration Selector */}
            {!isCpsRunning && (
              <div className="flex items-center justify-center gap-2 pb-2">
                <span className="text-xs text-slate-500 dark:text-slate-400 mr-2 font-mono font-bold">
                  {isAr ? "مدة الاختبار:" : "Test Duration:"}
                </span>
                {[1, 5, 10].map(sec => (
                  <button
                    key={sec}
                    onClick={() => {
                      soundFx.playClick();
                      setCpsDuration(sec);
                      setCpsTimeLeft(sec);
                      setIsCpsFinished(false);
                      setCpsClicks(0);
                      setCurrentCps(0);
                    }}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm ${
                      cpsDuration === sec
                        ? "bg-cyan-500 text-slate-950 font-black shadow-md shadow-cyan-500/20"
                        : "bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-400 hover:text-slate-950 dark:hover:text-white"
                    }`}
                  >
                    {sec}s
                  </button>
                ))}
              </div>
            )}

            {/* Metrics Header */}
            <div className="flex items-center justify-around border-b border-slate-200 dark:border-slate-800 pb-4">
              <div>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "الوقت المتبقي" : "Time Left"}</span>
                <span className="text-3xl font-black font-mono text-cyan-600 dark:text-cyan-400">{cpsTimeLeft}s</span>
              </div>
              <div>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "إجمالي النقرات" : "Total Clicks"}</span>
                <span className="text-3xl font-black font-mono text-emerald-600 dark:text-emerald-400">{cpsClicks}</span>
              </div>
              <div>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "معدل الـ CPS الحالي" : "Current CPS"}</span>
                <span className="text-3xl font-black font-mono text-amber-600 dark:text-amber-400">
                  {currentCps.toFixed(1)}
                </span>
              </div>
            </div>

            {/* Click Stage Box */}
            <div 
              onMouseDown={handleCpsClick}
              onTouchStart={handleCpsClick}
              className={`w-full h-64 rounded-3xl border-2 cursor-pointer select-none transition-all flex flex-col items-center justify-center p-6 touch-manipulation ${
                isCpsRunning 
                  ? 'border-cyan-500 dark:border-cyan-400 bg-cyan-50 dark:bg-cyan-950/40 shadow-[0_0_30px_rgba(0,229,255,0.35)] active:scale-[0.99]' 
                  : (isCpsFinished ? 'border-emerald-500 dark:border-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 shadow-md' : 'border-dashed border-cyan-400 dark:border-cyan-500/40 bg-slate-50 dark:bg-slate-900/60 hover:border-cyan-500 hover:bg-slate-100 dark:hover:bg-slate-900/90')
              }`}
            >
              <Zap className={`w-12 h-12 mb-2 transition-transform ${isCpsRunning ? 'text-cyan-500 dark:text-cyan-400 scale-125 animate-pulse' : 'text-slate-400 dark:text-slate-500'}`} />
              <h3 className="text-xl font-black text-slate-900 dark:text-slate-100 tracking-wide">
                {!isCpsRunning && !isCpsFinished && (isAr ? "انقر هنا لبدء الاختبار فوراً!" : "CLICK HERE TO START TEST")}
                {isCpsRunning && (isAr ? "استمر بالنقر بأقصى سرعة ممكنة!" : "CLICK AS FAST AS YOU CAN!")}
                {isCpsFinished && (isAr ? `انتهى الاختبار! نتيجتك: ${currentCps.toFixed(1)} CPS` : `Test Completed! Score: ${currentCps.toFixed(1)} CPS`)}
              </h3>
              
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-mono">
                {!isCpsRunning && !isCpsFinished && (isAr ? "النقرة الأولى ستبدأ الوقت تلقائياً وتُحسب فوراً" : "First click immediately starts the timer and counts as click #1")}
                {isCpsRunning && (isAr ? "الوقت يعمل بسلاسة دون توقف!" : "Keep the clicking pace!")}
                {isCpsFinished && (isAr ? "نتيجة ممتازة! اضغط بالأسفل لإعادة المحاولة" : "Great score! Click below to try again")}
              </p>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2 text-xs font-mono text-slate-500 dark:text-slate-400">
                <Trophy className="w-4 h-4 text-amber-500 dark:text-amber-400" />
                <span className="font-bold">{isAr ? "أفضل نتيجة:" : "Personal Best:"}</span>
                <span className="font-black text-amber-600 dark:text-amber-300 font-mono">{bestCps.toFixed(1)} CPS</span>
              </div>

              {isCpsFinished && (
                <button
                  onClick={handleResetCps}
                  className="px-6 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all inline-flex items-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>{isAr ? "إعادة الاختبار" : "Try Again"}</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* MODE 2: MULTI-TARGET RANDOM AIM ARENA */}
        {/* ======================================================== */}
        {testMode === "aim" && (
          <div className="p-8 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-6 text-center shadow-xl">
            
            {/* Level Selector */}
            {!isAimActive && (
              <div className="space-y-3 pb-2">
                <span className="text-xs text-slate-500 dark:text-slate-400 font-mono block font-bold">
                  {isAr ? "اختر مستوى التدريب والصعوبة:" : "Select Difficulty Level:"}
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {AIM_LEVELS.map(lvl => (
                    <div
                      key={lvl.level}
                      onClick={() => { soundFx.playClick(); setSelectedAimLevel(lvl.level); setIsAimFinished(false); }}
                      className={`p-4 rounded-2xl border text-left cursor-pointer transition-all shadow-sm ${
                        selectedAimLevel === lvl.level
                          ? 'border-emerald-500 dark:border-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 ring-1 ring-emerald-500/50 shadow-md'
                          : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070a10] hover:border-slate-300 dark:hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-slate-900 dark:text-slate-100">{isAr ? lvl.nameAr : lvl.name}</span>
                        <span className="text-[10px] font-mono font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/80 px-2 py-0.5 rounded-md border border-emerald-300 dark:border-emerald-800/60">{lvl.badge}</span>
                      </div>
                      <p className="text-[10px] text-slate-500 dark:text-slate-400 mt-1.5 font-mono">
                        {lvl.totalTargets} {isAr ? "أهداف عشوائية" : "Random Targets"} • {lvl.targetSize}px
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Live Metrics Header */}
            <div className="flex items-center justify-around border-b border-slate-200 dark:border-slate-800 pb-4">
              <div>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "الهدف الحالي" : "Target Progress"}</span>
                <span className="text-2xl font-black font-mono text-emerald-600 dark:text-emerald-400">
                  {targetIndex} / {currentAimConfig.totalTargets}
                </span>
              </div>
              <div>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "متوسط سرعة الإيم" : "Average Reflex"}</span>
                <span className="text-2xl font-black font-mono text-cyan-600 dark:text-cyan-400">
                  {averageAimMs > 0 ? `${averageAimMs} ms` : "--"}
                </span>
              </div>
              <div>
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block font-bold">{isAr ? "الدقة" : "Accuracy"}</span>
                <span className="text-2xl font-black font-mono text-amber-600 dark:text-amber-400">
                  {aimAccuracy}%
                </span>
              </div>
            </div>

            {/* RANDOM TARGET CANVAS / ARENA */}
            <div 
              onClick={handleArenaMissClick}
              className="w-full h-80 rounded-3xl border-2 border-slate-300 dark:border-slate-800 bg-[#080d16] relative overflow-hidden select-none cursor-crosshair shadow-inner"
            >
              {/* Ready / Idle State */}
              {!isAimActive && !isAimFinished && (
                <div className="absolute inset-0 flex flex-col items-center justify-center p-6 bg-slate-950/75 backdrop-blur-sm z-20">
                  <Crosshair className="w-16 h-16 text-emerald-400 mb-3 animate-pulse" />
                  <h3 className="text-2xl font-black text-white">
                    {isAr ? `المستوى ${selectedAimLevel}: ${currentAimConfig.nameAr}` : `Level ${selectedAimLevel}: ${currentAimConfig.name}`}
                  </h3>
                  <p className="text-xs text-slate-300 mt-1 max-w-md font-mono">
                    {isAr 
                      ? "ستظهر لك أهداف دائرية في أماكن عشوائية. اضغط عليها بأقصى سرعة ممكنة لتطوير الإيم ورد الفعل."
                      : "Targets will spawn in random arena coordinates. Click each bullseye as fast as possible!"}
                  </p>
                  <button
                    onClick={handleStartAimTest}
                    className="mt-5 px-8 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all shadow-lg shadow-emerald-500/20 cursor-pointer flex items-center gap-2"
                  >
                    <Target className="w-4 h-4" />
                    <span>{isAr ? "بدء تمرين الإيم الآن" : "Start Aim Training Session"}</span>
                  </button>
                </div>
              )}

              {/* Finished State Summary */}
              {isAimFinished && (
                <div className="absolute inset-0 flex flex-col items-center justify-center p-6 bg-slate-950/85 backdrop-blur-md z-20 animate-fade-in space-y-3">
                  <Trophy className="w-14 h-14 text-amber-400 animate-bounce" />
                  <h3 className="text-2xl font-black text-white">
                    {isAr ? "اكتمل التمرين بنجاح!" : "Aim Training Session Complete!"}
                  </h3>
                  <div className="flex items-center gap-6 font-mono text-sm">
                    <div>
                      <span className="text-slate-300 text-xs block font-bold">{isAr ? "متوسط السرعة:" : "Average Time:"}</span>
                      <span className="text-2xl font-black text-cyan-400">{averageAimMs} ms</span>
                    </div>
                    <div>
                      <span className="text-slate-300 text-xs block font-bold">{isAr ? "دقة النقرات:" : "Accuracy:"}</span>
                      <span className="text-2xl font-black text-emerald-400">{aimAccuracy}%</span>
                    </div>
                  </div>

                  <div className={`px-5 py-2 rounded-full border text-xs font-black uppercase tracking-wider shadow-md ${getAimRank(averageAimMs, aimAccuracy).color}`}>
                    {getAimRank(averageAimMs, aimAccuracy).rank}
                  </div>

                  <button
                    onClick={handleStartAimTest}
                    className="mt-2 px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all shadow-lg shadow-emerald-500/20 cursor-pointer flex items-center gap-2"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>{isAr ? "إعادة التدريب" : "Train Again"}</span>
                  </button>
                </div>
              )}

              {/* Dynamic Random Bullseye Target */}
              {isAimActive && currentTarget && (
                <div
                  key={currentTarget.id}
                  onClick={handleHitTarget}
                  style={{
                    position: "absolute",
                    left: `${currentTarget.x}%`,
                    top: `${currentTarget.y}%`,
                    width: `${currentTarget.size}px`,
                    height: `${currentTarget.size}px`,
                    transform: "translate(-50%, -50%)"
                  }}
                  className="rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400 border-2 border-white shadow-[0_0_25px_rgba(56,239,125,0.8)] cursor-pointer flex items-center justify-center animate-pop active:scale-90 transition-transform"
                >
                  <div className="w-1/2 h-1/2 rounded-full bg-slate-950 border border-white/60 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  </div>
                </div>
              )}
            </div>

            {/* Target Breakdown Log */}
            {hitTimes.length > 0 && (
              <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
                <span className="text-xs font-mono text-slate-500 dark:text-slate-400 block mb-2.5 font-bold">
                  {isAr ? "سجل سرعة الأهداف:" : "Recent Target Hit Log:"}
                </span>
                <div className="flex flex-wrap items-center justify-center gap-2">
                  {hitTimes.map((t, idx) => (
                    <span 
                      key={idx}
                      className={`px-3 py-1.5 rounded-xl text-xs font-mono font-black border shadow-xs transition-all ${
                        t < 300 
                          ? 'bg-emerald-100 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-300 border-emerald-300 dark:border-emerald-800' 
                          : (t < 500 ? 'bg-cyan-100 dark:bg-cyan-950/70 text-cyan-800 dark:text-cyan-300 border-cyan-300 dark:border-cyan-800' : 'bg-rose-100 dark:bg-rose-950/70 text-rose-800 dark:text-rose-300 border-rose-300 dark:border-rose-800')
                      }`}
                    >
                      #{idx + 1}: {t}ms
                    </span>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}

        {/* ======================================================== */}
        {/* MODE 3: FLASH REACTION TEST */}
        {/* ======================================================== */}
        {testMode === "reaction" && (
          <div className="p-8 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-6 text-center shadow-xl">
            <div 
              onMouseDown={handleReactionClick}
              onTouchStart={handleReactionClick}
              className={`w-full h-72 rounded-3xl cursor-pointer select-none transition-all flex flex-col items-center justify-center p-6 shadow-2xl touch-manipulation ${
                reactionState === 'idle'
                  ? 'bg-slate-100 dark:bg-slate-900/80 border-2 border-dashed border-cyan-500/60 text-slate-800 dark:text-cyan-200 hover:border-cyan-500 hover:bg-slate-200/60 dark:hover:bg-slate-900'
                  : (reactionState === 'waiting' 
                    ? 'bg-rose-100 dark:bg-rose-950/90 border-2 border-rose-400 dark:border-rose-500 text-rose-800 dark:text-rose-200 shadow-[0_0_30px_rgba(244,63,94,0.2)]' 
                    : (reactionState === 'early'
                      ? 'bg-amber-100 dark:bg-amber-950/90 border-2 border-amber-400 dark:border-amber-500 text-amber-800 dark:text-amber-200 shadow-[0_0_30px_rgba(245,158,11,0.3)]'
                      : (reactionState === 'ready' 
                        ? 'bg-emerald-500 border-2 border-emerald-300 text-slate-950 shadow-[0_0_40px_rgba(56,239,125,0.7)] animate-pulse' 
                        : 'bg-cyan-100 dark:bg-cyan-950/90 border-2 border-cyan-400 text-cyan-800 dark:text-cyan-200 shadow-[0_0_30px_rgba(0,229,255,0.2)]')))
              }`}
            >
              {reactionState === "idle" && (
                <>
                  <Zap className="w-14 h-14 mb-2 text-cyan-600 dark:text-cyan-400 animate-pulse" />
                  <h3 className="text-2xl font-black text-slate-900 dark:text-white">{isAr ? "انقر هنا لبدء اختبار سرعة رد الفعل!" : "CLICK HERE TO START REACTION TEST"}</h3>
                  <p className="text-xs mt-1 text-slate-500 dark:text-slate-400 font-mono">{isAr ? "عندما يتحول المربع للأخضر، انقر بأقصى سرعة ممكنة." : "When the box turns bright green, click as fast as you can."}</p>
                </>
              )}

              {reactionState === "waiting" && (
                <>
                  <Timer className="w-14 h-14 mb-2 animate-spin text-rose-400" />
                  <h3 className="text-2xl font-black text-white">{isAr ? "انتظر حتى يتحول المربع للأخضر..." : "WAIT FOR GREEN COLOR..."}</h3>
                  <p className="text-xs mt-1 text-rose-200/90 font-mono">{isAr ? "لا تنقر الآن!" : "Hold your click!"}</p>
                </>
              )}

              {reactionState === "early" && (
                <>
                  <AlertTriangle className="w-14 h-14 mb-2 text-amber-400 animate-bounce" />
                  <h3 className="text-2xl font-black text-amber-300">{isAr ? "نقرت مبكراً جداً!" : "TOO EARLY!"}</h3>
                  <p className="text-xs mt-1 text-amber-100 font-medium">
                    {isAr ? "نقرت قبل أن يتحول المربع للأخضر. انقر في أي مكان لإعادة المحاولة فوراً!" : "You clicked before it turned green. Click anywhere to try again!"}
                  </p>
                </>
              )}

              {reactionState === "ready" && (
                <>
                  <Target className="w-16 h-16 mb-2 text-slate-950 animate-ping" />
                  <h3 className="text-3xl font-black text-slate-950">{isAr ? "انقر الآن بأقصى سرعة!" : "CLICK NOW!"}</h3>
                </>
              )}

              {reactionState === "clicked" && (
                <>
                  <Award className="w-12 h-12 mb-2 text-cyan-400" />
                  <h3 className="text-3xl font-black font-mono text-cyan-300">{reactionTime} ms</h3>
                  <p className="text-xs text-slate-200 mt-1 font-mono">{isAr ? "سرعة استجابة بصرية ممتازة لمباريات الـ PvP! انقر للإعادة." : "Great competitive visual reflex time! Click anywhere to test again."}</p>
                </>
              )}
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center gap-2 text-xs font-mono text-slate-500 dark:text-slate-400">
                <Trophy className="w-4 h-4 text-amber-500 dark:text-amber-400" />
                <span className="font-bold">{isAr ? "أسرع استجابة:" : "Best Reaction:"}</span>
                <span className="font-black text-emerald-600 dark:text-emerald-300 font-mono">{bestReaction ? `${bestReaction} ms` : "--"}</span>
              </div>

              {(reactionState === "clicked" || reactionState === "early") && (
                <button
                  onClick={startReactionTest}
                  className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all inline-flex items-center gap-2 shadow-lg shadow-emerald-500/20 cursor-pointer"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>{isAr ? "اختبار جديد" : "Test Again"}</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Floating Auto-Save to Leaderboard Toast (Top Center, No Bouncing, Cyber Glassmorphism) */}
        {autoSaveToast && (
          <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 transition-all duration-300">
            <div className="px-5 py-3 rounded-2xl bg-slate-900/95 dark:bg-[#090d16]/95 backdrop-blur-xl text-white font-bold text-xs shadow-[0_10px_35px_rgba(0,0,0,0.8),0_0_20px_rgba(56,239,125,0.25)] flex items-center gap-3 border border-emerald-500/40">
              <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <span className="text-slate-100">{autoSaveToast}</span>
              <Link 
                href="/leaderboards" 
                className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 hover:text-emerald-300 font-extrabold border border-emerald-500/30 transition-all ml-1"
              >
                {isAr ? "عرض الصدارة" : "View Leaderboard"}
              </Link>
            </div>
          </div>
        )}

        <ConnectedFeaturesHub currentPath="/trainer" />

      </div>
    </div>
    </AuthGate>);
}