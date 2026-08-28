"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Sparkles, 
  Download, 
  Check, 
  ArrowLeft, 
  ArrowRight, 
  ShieldCheck, 
  Shirt, 
  RefreshCw, 
  Eye, 
  ExternalLink,
  Crown,
  Award,
  Zap,
  User,
  X
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { Skin3DViewer } from "@/components/Skin3DViewer";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";
import { saveClaimedAccountToCloud, ClaimedAccountItem } from "@/lib/multiAccounts";

interface CapePreset {
  id: string;
  name: string;
  nameAr: string;
  tag: string;
  tagAr: string;
  rarity: "Founder" | "Mythic" | "Classic" | "Cosmic" | "Special";
  badgeBg: string;
  gradient: string;
  patternSvg: string;
  glowColor: string;
  accentBorder: string;
  emblem: React.ReactNode;
  emblemText?: string;
  downloadUrl: string;
  desc: string;
  descAr: string;
}

const CAPE_PRESETS: CapePreset[] = [
  {
    id: "sir_founder",
    name: "SIR Founder Obsidian Neon",
    nameAr: "وشاح مؤسس SIR النيون السيبراني",
    tag: "✨ Exclusive Founder",
    tagAr: "✨ حصري للمؤسسين",
    rarity: "Founder",
    badgeBg: "bg-cyan-100 dark:bg-cyan-950 text-cyan-900 dark:text-cyan-300 border-cyan-400/60 font-black",
    gradient: "from-[#0c1f38] via-[#0284c7] to-[#00e5ff]",
    patternSvg: "linear-gradient(180deg, #0a192f 0%, #0369a1 45%, #00e5ff 85%, #38ef7d 100%)",
    glowColor: "rgba(0, 229, 255, 0.4)",
    accentBorder: "border-cyan-400",
    emblem: <Crown className="w-8 h-8 text-amber-300 drop-shadow-[0_2px_8px_rgba(245,158,11,0.6)]" />,
    emblemText: "FOUNDER",
    downloadUrl: "/capes/sir_founder.png",
    desc: "The signature glowing obsidian cape crafted exclusively for SIR ecosystem founders with dynamic cyan circuit geometry.",
    descAr: "الوشاح الرسمي المتوهج لمؤسسي منظومة SIR بتصميم الدوائر السيبرانية والتدرج الضوئي الأزرق."
  },
  {
    id: "ender_dragon",
    name: "Ender Void Dragon Wings",
    nameAr: "أجنحة تنين الإندر والفويد",
    tag: "🐉 Animated Mythic",
    tagAr: "🐉 أسطوري متحرك",
    rarity: "Mythic",
    badgeBg: "bg-purple-100 dark:bg-purple-950 text-purple-900 dark:text-purple-300 border-purple-400/60 font-black",
    gradient: "from-[#240a3e] via-[#7e22ce] to-[#c084fc]",
    patternSvg: "linear-gradient(180deg, #240a3e 0%, #7e22ce 45%, #a855f7 80%, #f0abfc 100%)",
    glowColor: "rgba(168, 85, 247, 0.4)",
    accentBorder: "border-purple-400",
    emblem: <Eye className="w-8 h-8 text-fuchsia-300 drop-shadow-[0_2px_8px_rgba(217,70,239,0.6)]" />,
    emblemText: "VOID DRAGON",
    downloadUrl: "/capes/ender_dragon.png",
    desc: "Mystic animated void particles with the radiant eye of the Ender Dragon glowing in the dark.",
    descAr: "جزيئات الفويد الساحرة مع عين تنين الإندر المتوهجة في الظلام."
  },
  {
    id: "optifine_banner",
    name: "OptiFine Ultra Crimson Banner",
    nameAr: "وشاح أوبتي فاين القرمزي الكلاسيكي",
    tag: "⚡ Classic OF Edition",
    tagAr: "⚡ إصدار أوبتي فاين الكلاسيكي",
    rarity: "Classic",
    badgeBg: "bg-rose-100 dark:bg-rose-950 text-rose-900 dark:text-rose-300 border-rose-400/60 font-black",
    gradient: "from-[#5c0f15] via-[#dc2626] to-[#f87171]",
    patternSvg: "linear-gradient(180deg, #5c0f15 0%, #dc2626 45%, #ef4444 80%, #fca5a5 100%)",
    glowColor: "rgba(239, 68, 68, 0.4)",
    accentBorder: "border-rose-400",
    emblem: <span className="text-2xl font-black font-sans tracking-tight text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)] border-2 border-white/80 px-2 py-0.5 rounded-lg bg-black/30">OF</span>,
    emblemText: "OPTIFINE HD",
    downloadUrl: "/capes/optifine_banner.png",
    desc: "The legendary OptiFine white 'OF' heraldic crest on a vibrant gradient crimson canvas.",
    descAr: "شعار OptiFine الكلاسيكي التاريخي بحروف OF البيضاء على خلفية قرمزية متدرجة."
  },
  {
    id: "lunar_astral",
    name: "Lunar Astral Galaxy",
    nameAr: "أمواج المجرة القمرية السحيقة",
    tag: "🌌 Cosmic Nebula Flow",
    tagAr: "🌌 سديم كوني متدفق",
    rarity: "Cosmic",
    badgeBg: "bg-indigo-100 dark:bg-indigo-950 text-indigo-900 dark:text-indigo-300 border-indigo-400/60 font-black",
    gradient: "from-[#171746] via-[#4338ca] to-[#38bdf8]",
    patternSvg: "linear-gradient(180deg, #171746 0%, #4338ca 45%, #6366f1 80%, #67e8f9 100%)",
    glowColor: "rgba(99, 102, 241, 0.4)",
    accentBorder: "border-indigo-400",
    emblem: <Sparkles className="w-8 h-8 text-sky-200 drop-shadow-[0_2px_8px_rgba(56,189,248,0.6)]" />,
    emblemText: "LUNAR GALAXY",
    downloadUrl: "/capes/lunar_astral.png",
    desc: "Deep space cosmic dust and shooting stars shimmering across an indigo twilight sky.",
    descAr: "غبار كوني متلألئ وشهب فضائية متحركة عبر سماء المجرة البنفسجية."
  },
  {
    id: "cherry_blossom",
    name: "Sakura Cherry Blossom 15th",
    nameAr: "وشاح أزهار الكرز وساكورا 15th",
    tag: "🌸 15th Anniversary",
    tagAr: "🌸 ذكرى 15 عاماً",
    rarity: "Special",
    badgeBg: "bg-pink-100 dark:bg-pink-950 text-pink-900 dark:text-pink-300 border-pink-400/60 font-black",
    gradient: "from-[#500724] via-[#db2777] to-[#fbcfe8]",
    patternSvg: "linear-gradient(180deg, #500724 0%, #db2777 45%, #f472b6 80%, #fce7f3 100%)",
    glowColor: "rgba(244, 114, 182, 0.4)",
    accentBorder: "border-pink-400",
    emblem: <Award className="w-8 h-8 text-rose-200 drop-shadow-[0_2px_8px_rgba(244,114,182,0.6)]" />,
    emblemText: "15TH ANNIV",
    downloadUrl: "/capes/cherry_blossom.png",
    desc: "Pastel pink sakura petals drifting over the official 15th Anniversary commemorative badge.",
    descAr: "بتلات الساكورا الوردية المتساقطة مع الشعار التذكاري الرسمي لـ 15 عاماً."
  },
  {
    id: "diamond_gladiator",
    name: "Gladiator Diamond Shards",
    nameAr: "شظايا الألماس والمبارزات",
    tag: "💎 Ranked Diamond",
    tagAr: "💎 ألماس التصنيف",
    rarity: "Mythic",
    badgeBg: "bg-cyan-100 dark:bg-cyan-950 text-cyan-900 dark:text-cyan-300 border-cyan-400/60 font-black",
    gradient: "from-[#072738] via-[#0284c7] to-[#38bdf8]",
    patternSvg: "linear-gradient(180deg, #072738 0%, #0369a1 40%, #0ea5e9 80%, #bae6fd 100%)",
    glowColor: "rgba(14, 165, 233, 0.4)",
    accentBorder: "border-cyan-400",
    emblem: <Sparkles className="w-8 h-8 text-cyan-200 drop-shadow-[0_2px_8px_rgba(14,165,233,0.6)]" />,
    emblemText: "DIAMOND RANK",
    downloadUrl: "/capes/diamond_gladiator.png",
    desc: "Forged from pure BedWars diamond shards with reflective geometric crystal facets.",
    descAr: "مصنوع من شظايا ألماس البدوورز مع أوجه بلورية عاكسة للضوء."
  }
];

import { AuthGate } from "@/components/AuthGate";

export default function CapesPage() {
  const { lang, user } = useEcosystem();
  const [activeCape, setActiveCape] = useState<CapePreset>(CAPE_PRESETS[0]);
  const [previewUsername, setPreviewUsername] = useState<string>("");
  const [activeUsername, setActiveUsername] = useState<string>("");
  const [loadingSkin, setLoadingSkin] = useState(false);
  const [previewMode, setPreviewMode] = useState<"player" | "cape">("player");

  // Multi-account sync modal state
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState<string | null>(null);
  const [savedAccounts, setSavedAccounts] = useState<ClaimedAccountItem[]>([]);
  const [offlineInputIgn, setOfflineInputIgn] = useState<string>("");

  const isAr = lang === "ar";

  // Load saved accounts from localStorage / Cloud
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const raw = localStorage.getItem("sir_claimed_accounts");
        if (raw) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed) && parsed.length > 0) {
            setSavedAccounts(parsed);
          }
        }
      } catch (e) {
        console.warn("Could not load local claimed accounts:", e);
      }
    }
  }, []);

  const handleUpdateUsername = () => {
    if (!previewUsername.trim()) return;
    soundFx.playClick();
    setLoadingSkin(true);
    const clean = previewUsername.trim();
    setActiveUsername(clean);
    setTimeout(() => setLoadingSkin(false), 300);
  };

  const handleStartSync = () => {
    soundFx.playClick();
    if (savedAccounts.length > 1) {
      // User has multiple accounts -> open selector modal
      setShowAccountModal(true);
    } else if (savedAccounts.length === 1) {
      // Direct sync to single account
      executeSyncToAccount(savedAccounts[0].ign);
    } else {
      // No accounts saved yet -> prompt for username
      setOfflineInputIgn(activeUsername || "Steve");
      setShowAccountModal(true);
    }
  };

  const executeSyncToAccount = async (targetIgn: string) => {
    const cleanIgn = targetIgn.trim();
    if (!cleanIgn) return;
    soundFx.playClick();

    // 1. Update localStorage
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(`sir_active_cape_${cleanIgn.toLowerCase()}`, JSON.stringify(activeCape));
        const updatedAccounts = savedAccounts.some(a => a.ign.toLowerCase() === cleanIgn.toLowerCase())
          ? savedAccounts
          : [...savedAccounts, { ign: cleanIgn, skinUrl: `https://mc-heads.net/skin/${cleanIgn}`, model: "classic" as const }];
        localStorage.setItem("sir_claimed_accounts", JSON.stringify(updatedAccounts));
        setSavedAccounts(updatedAccounts);
      } catch {}
    }

    // 2. Push to Firestore if logged in
    if (user?.uid) {
      try {
        await saveClaimedAccountToCloud(user.uid, user.email, {
          ign: cleanIgn,
          skinUrl: `https://mc-heads.net/skin/${cleanIgn}`,
          model: "classic"
        });
      } catch (e) {
        console.warn("Cloud sync cape notice:", e);
      }
    }

    setShowAccountModal(false);
    setSyncSuccessMsg(
      isAr 
        ? `🎉 تم تجهيز ومزامنة وشاح (${activeCape.nameAr}) بنجاح لحساب @${cleanIgn}!`
        : `🎉 (${activeCape.name}) has been equipped & synced to account @${cleanIgn}!`
    );
    setTimeout(() => setSyncSuccessMsg(null), 4500);
  };

  return (
    <AuthGate featureName="3D Capes Showroom" featureNameAr="معرض الأوشحة ثلاثية الأبعاد">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-6xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-xs">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-xs">
            <ShieldCheck className="w-3.5 h-3.5" />
            {isAr ? "معرض الأوشحة الحصرية والـ Cosmetics" : "3D Animated Capes Showroom"}
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "أوشحة ماين كرافت الحصرية والمتحركة" : "Custom Minecraft Animated Capes"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "اختر من باقة الأوشحة الحصرية ثلاثية الأبعاد، عاينها مباشرة على شخصيتك، واربطها بحسابك المكرك أو الرسمي بنقرة واحدة."
              : "Explore curated HD & animated capes, preview them seamlessly on your Minecraft character in 3D, and sync directly to your account with 1 click."}
          </p>
        </div>

        {/* Sync Success Alert Notification */}
        {syncSuccessMsg && (
          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-500/50 text-emerald-800 dark:text-emerald-300 text-xs sm:text-sm font-bold flex items-center gap-3 shadow-lg shadow-emerald-500/10 animate-pop">
            <Check className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 stroke-[3]" />
            <span className="flex-1">{syncSuccessMsg}</span>
          </div>
        )}

        {/* Username Preview Bar */}
        <div className="p-4 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xl">
          <div className="relative w-full sm:flex-1">
            <input 
              type="text" 
              value={previewUsername}
              onChange={e => setPreviewUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleUpdateUsername()}
              placeholder={isAr ? "اكتب اسم حسابك لمعاينة الوشاح عليه (e.g. SirAhmed)..." : "Enter your Minecraft username to preview cape on your skin (e.g. SirAhmed)..."}
              className="w-full pl-4 pr-4 py-3 rounded-2xl bg-slate-50 dark:bg-[#070a10] border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 text-xs outline-none focus:border-cyan-500 transition-all font-mono placeholder-slate-400"
            />
          </div>
          <button 
            onClick={handleUpdateUsername}
            className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loadingSkin ? "animate-spin" : ""}`} />
            <span>{isAr ? "معاينة على شخصيتي" : "Preview on Player"}</span>
          </button>
        </div>

        {/* Main Stage Grid: 3D Previewer + Capes Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          
          {/* Active Cape 3D Preview Display Card */}
          <div className="md:col-span-1 p-6 rounded-3xl bg-white dark:bg-gradient-to-b dark:from-[#101624] dark:to-[#070a10] border border-slate-200 dark:border-cyan-500/40 text-center space-y-4 shadow-xl relative overflow-hidden group">
            
            {/* Perfectly Rounded Founder Badge */}
            <div className="flex justify-center">
              <span className={`inline-flex items-center gap-1.5 px-3.5 py-1 rounded-full text-xs font-bold font-mono border backdrop-blur-md transition-all shadow-xs ${activeCape.badgeBg}`}>
                <Sparkles className="w-3.5 h-3.5" />
                <span>{isAr ? activeCape.tagAr : activeCape.tag}</span>
              </span>
            </div>

            {/* View Mode Toggle Switcher */}
            <div className="flex items-center justify-center gap-1.5 p-1 rounded-2xl bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
              <button
                type="button"
                onClick={() => setPreviewMode("player")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                  previewMode === "player"
                    ? "bg-cyan-500 text-slate-950 shadow-md font-black"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
                }`}
              >
                <User className="w-3.5 h-3.5" />
                <span>{isAr ? "مجسم اللاعب والوشاح" : "3D Player & Cape"}</span>
              </button>
              <button
                type="button"
                onClick={() => setPreviewMode("cape")}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                  previewMode === "cape"
                    ? "bg-cyan-500 text-slate-950 shadow-md font-black"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100"
                }`}
              >
                <Shirt className="w-3.5 h-3.5" />
                <span>{isAr ? "لوحة الوشاح الفنية" : "Flat Cape Canvas"}</span>
              </button>
            </div>

            {/* Visual Cape & Character Showcase Frame */}
            <div className="w-full h-84 rounded-2xl overflow-hidden relative border border-slate-200 dark:border-slate-800 flex items-center justify-center bg-slate-100 dark:bg-[#070c16] group shadow-inner">
              
              {/* Dynamic Studio Spotlight Glow */}
              <div 
                className="absolute inset-0 transition-all duration-700 pointer-events-none"
                style={{ 
                  background: `radial-gradient(circle at 50% 50%, ${activeCape.glowColor} 0%, transparent 75%)`,
                  opacity: 0.85
                }}
              />

              {previewMode === "player" ? (
                /* Interactive 3D WebGL Player Character & Cape */
                <div className="relative z-10 flex items-center justify-center">
                  <Skin3DViewer
                    skinUrl={activeUsername.trim() ? `https://mc-heads.net/skin/${encodeURIComponent(activeUsername.trim())}` : "/skins/steve.png"}
                    capeUrl={activeCape.downloadUrl}
                    width={260}
                    height={320}
                    enableAnimation={true}
                  />
                </div>
              ) : (
                /* Cape Banner Art Plate */
                <div 
                  className="relative z-10 w-32 h-52 rounded-2xl border-2 border-white/40 shadow-[0_15px_40px_rgba(0,0,0,0.6)] flex flex-col items-center justify-between p-3.5 overflow-hidden transform group-hover:scale-105 transition-transform duration-300"
                  style={{ 
                    background: activeCape.patternSvg,
                    boxShadow: `0 15px 40px rgba(0,0,0,0.5), 0 0 30px ${activeCape.glowColor}`
                  }}
                >
                  {/* Collar Top Bar */}
                  <div className="w-full flex items-center justify-between px-1">
                    <div className="w-2 h-2 rounded-full bg-white/70 shadow-xs" />
                    <div className="flex-1 h-1 bg-white/40 rounded-full mx-1.5" />
                    <div className="w-2 h-2 rounded-full bg-white/70 shadow-xs" />
                  </div>

                  {/* Central Emblem Crest */}
                  <div className="flex flex-col items-center justify-center my-auto space-y-1.5">
                    <div className="p-3 rounded-2xl bg-black/30 border border-white/40 backdrop-blur-md shadow-xl flex items-center justify-center">
                      {activeCape.emblem}
                    </div>
                    {activeCape.emblemText && (
                      <span className="text-[10px] font-black font-mono tracking-widest text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.9)] uppercase">
                        {activeCape.emblemText}
                      </span>
                    )}
                  </div>

                  {/* Bottom Hem */}
                  <div className="w-full flex items-center justify-between pt-1 border-t border-white/30">
                    <span className="text-[8px] font-black font-mono tracking-wider text-white/90">
                      SIR 2026
                    </span>
                    <span className="text-[8px] font-bold font-mono text-white/80">
                      HD CAPE
                    </span>
                  </div>
                </div>
              )}

              {/* Player Overlay Mini Render */}
              <div className="absolute top-3 right-3 z-20 flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-white/90 dark:bg-slate-950/90 border border-slate-200 dark:border-slate-800 text-[10px] font-mono font-bold text-slate-800 dark:text-cyan-400 shadow-md backdrop-blur-md">
                <img 
                  src={activeUsername.trim() ? `https://mc-heads.net/avatar/${encodeURIComponent(activeUsername.trim())}/24` : "https://mc-heads.net/avatar/MHF_Steve/24"} 
                  alt={activeUsername || "Steve"} 
                  className="w-4 h-4 rounded-sm"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = "/skins/steve.png";
                  }}
                />
                <span>@{activeUsername.trim() || "Steve (Default)"}</span>
              </div>

            </div>

            <div className="space-y-1">
              <h3 className="text-base font-black text-slate-900 dark:text-slate-100">{isAr ? activeCape.nameAr : activeCape.name}</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed px-2">
                {isAr ? activeCape.descAr : activeCape.desc}
              </p>
            </div>

            {/* Direct Account Sync Action Buttons */}
            <div className="space-y-2.5 pt-3 border-t border-slate-200 dark:border-slate-800">
              
              <button
                onClick={handleStartSync}
                className="w-full py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
              >
                <Zap className="w-4 h-4 fill-slate-950" />
                <span>{isAr ? "⚡ مزامنة الوشاح مع حسابك" : "⚡ Sync Cape to Account"}</span>
              </button>

              <a
                href={activeCape.downloadUrl}
                target="_blank"
                rel="noreferrer"
                className="w-full py-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs transition-all flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{isAr ? "تحميل ملف الوشاح (.png)" : "Download Cape File (.png)"}</span>
              </a>

            </div>

          </div>

          {/* Curated Capes Showcase Matrix */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-black text-slate-900 dark:text-slate-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
                <span>{isAr ? "تشكيلة الأوشحة الحصرية (HD & Animated)" : "Available HD Cape Collection"}</span>
              </h3>
              <span className="text-[10px] font-mono text-cyan-800 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-950 px-2.5 py-0.5 rounded-full border border-cyan-300 dark:border-cyan-800 font-bold shadow-xs">
                6 Unique Capes
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {CAPE_PRESETS.map(cape => (
                <div
                  key={cape.id}
                  onClick={() => { 
                    soundFx.playClick();
                    setActiveCape(cape); 
                  }}
                  className={`p-4 rounded-2xl border text-left cursor-pointer transition-all flex items-center gap-4 shadow-xs ${
                    activeCape.id === cape.id 
                      ? 'border-cyan-500 dark:border-cyan-400 bg-cyan-50/80 dark:bg-cyan-950/40 shadow-md ring-2 ring-cyan-500/50 dark:ring-cyan-400/50' 
                      : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-[#101624] hover:border-cyan-400 dark:hover:border-cyan-500/40 hover:bg-slate-50 dark:hover:bg-[#141b2d]'
                  }`}
                >
                  <div 
                    className="w-12 h-18 rounded-xl border border-white/30 shadow-md flex items-center justify-center p-1 overflow-hidden shrink-0"
                    style={{ background: cape.patternSvg }}
                  >
                    <div className="transform scale-75">
                      {cape.emblem}
                    </div>
                  </div>

                  <div className="min-w-0 flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-xs font-black text-slate-900 dark:text-slate-100 truncate">
                        {isAr ? cape.nameAr : cape.name}
                      </h4>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-2">
                      {isAr ? cape.descAr : cape.desc}
                    </p>
                    <span className={`inline-block text-[9px] font-mono font-bold px-2 py-0.5 rounded-full ${cape.badgeBg}`}>
                      {isAr ? cape.tagAr : cape.tag}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Interactive Multi-Account Selector Modal */}
        {showAccountModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
            <div className="w-full max-w-md bg-white dark:bg-[#0c121e] border border-slate-200 dark:border-cyan-500/40 rounded-3xl p-6 shadow-2xl space-y-5 animate-pop text-slate-900 dark:text-white">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-cyan-600 dark:text-cyan-400 font-black text-sm">
                  <ShieldCheck className="w-5 h-5" />
                  <span>{isAr ? "اختر الحساب لربط الوشاح به" : "Select Account to Equip Cape"}</span>
                </div>
                <button 
                  onClick={() => setShowAccountModal(false)}
                  className="p-1 rounded-xl text-slate-400 hover:text-slate-900 dark:hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Saved accounts list */}
              {savedAccounts.length > 0 && (
                <div className="space-y-2">
                  <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold block">
                    {isAr ? "الحسابات المحفوظة:" : "Saved Accounts:"}
                  </span>
                  <div className="max-h-48 overflow-y-auto space-y-1.5 custom-scrollbar">
                    {savedAccounts.map((acc) => (
                      <div
                        key={acc.ign}
                        onClick={() => executeSyncToAccount(acc.ign)}
                        className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-cyan-500 hover:bg-cyan-50/50 dark:hover:bg-cyan-950/40 cursor-pointer transition-all group"
                      >
                        <div className="flex items-center gap-3">
                          <img 
                            src={`https://mc-heads.net/avatar/${acc.ign}/32`} 
                            alt={acc.ign} 
                            className="w-8 h-8 rounded-lg"
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = "https://minotar.net/avatar/Steve/32.png";
                            }}
                          />
                          <div>
                            <h4 className="text-xs font-black text-slate-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-400">
                              @{acc.ign}
                            </h4>
                            <span className="text-[10px] font-mono text-slate-500">
                              {acc.accountType || "Offline / Cracked"}
                            </span>
                          </div>
                        </div>
                        <span className="text-[11px] font-bold text-cyan-600 dark:text-cyan-400 group-hover:translate-x-1 transition-transform">
                          {isAr ? "ربط ←" : "Equip →"}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quick Input for new or cracked username */}
              <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-800">
                <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400 font-bold block">
                  {isAr ? "أو اكتب اسم حساب مكرك / أوفلاين جديد:" : "Or Enter New Cracked / Offline IGN:"}
                </span>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={offlineInputIgn}
                    onChange={e => setOfflineInputIgn(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && executeSyncToAccount(offlineInputIgn)}
                    placeholder="Enter IGN (e.g. SirAhmed)..."
                    className="flex-1 px-3.5 py-2.5 rounded-xl bg-slate-100 dark:bg-[#070a10] border border-slate-200 dark:border-slate-800 text-xs font-mono outline-none focus:border-cyan-500"
                  />
                  <button
                    onClick={() => executeSyncToAccount(offlineInputIgn)}
                    className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs cursor-pointer shadow-md"
                  >
                    {isAr ? "مزامنة" : "Sync"}
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* Connected Ecosystem Hub */}
        <ConnectedFeaturesHub currentPath="/capes" />

      </div>
    </div>
    </AuthGate>
  );
}
