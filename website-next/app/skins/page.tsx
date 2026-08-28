"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  User, 
  Sparkles, 
  Download, 
  Check, 
  ArrowLeft, 
  ArrowRight, 
  RefreshCw, 
  Shirt, 
  ShieldCheck, 
  Zap,
  X
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { Skin3DViewer } from "@/components/Skin3DViewer";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";
import { saveClaimedAccountToCloud, ClaimedAccountItem } from "@/lib/multiAccounts";

const PRESET_SKINS = [

  {
    id: "technoblade",
    name: "Technoblade (The Blade)",
    nameAr: "تكنوبليد (ملك الـ PvP)",
    category: "Legendary / PvP",
    username: "Technoblade",
    preview: "https://minotar.net/armor/body/Technoblade/300.png",
    skinUrl: "https://minotar.net/skin/Technoblade"
  },
  {
    id: "dream",
    name: "Dream (Speedrun Legend)",
    nameAr: "دريم (بطل السبيد رن)",
    category: "Speedrun / Competitive",
    username: "Dream",
    preview: "https://minotar.net/armor/body/Dream/300.png",
    skinUrl: "https://minotar.net/skin/Dream"
  },
  {
    id: "skeppy",
    name: "Skeppy (Diamond Skeppy)",
    nameAr: "سكيبي (الدايموند)",
    category: "Content / Trolling",
    username: "Skeppy",
    preview: "https://minotar.net/armor/body/Skeppy/300.png",
    skinUrl: "https://minotar.net/skin/Skeppy"
  },
  {
    id: "sparklez",
    name: "CaptainSparklez (Jordan)",
    nameAr: "كابتن سباركلز (جوردان)",
    category: "OG Veteran / Music",
    username: "CaptainSparklez",
    preview: "https://minotar.net/armor/body/CaptainSparklez/300.png",
    skinUrl: "https://minotar.net/skin/CaptainSparklez"
  },
  {
    id: "illumina",
    name: "Illumina (Speedrun Master)",
    nameAr: "إلومينا (أسطورة الفويد)",
    category: "Speedrun / Fantasy",
    username: "Illumina",
    preview: "https://minotar.net/armor/body/Illumina/300.png",
    skinUrl: "https://minotar.net/skin/Illumina"
  },
  {
    id: "grian",
    name: "Grian (Master Builder)",
    nameAr: "غريان (معمار الهيرمت كرافت)",
    category: "Creative / Builder",
    username: "Grian",
    preview: "https://minotar.net/armor/body/Grian/300.png",
    skinUrl: "https://minotar.net/skin/Grian"
  },
  {
    id: "mumbo",
    name: "Mumbo Jumbo (Redstone Master)",
    nameAr: "مامبو جامبو (عبقري الردستون)",
    category: "Redstone / Engineering",
    username: "Mumbo",
    preview: "https://minotar.net/armor/body/Mumbo/300.png",
    skinUrl: "https://minotar.net/skin/Mumbo"
  }
];

export default function SkinsStudioPage() {
  const { lang, user } = useEcosystem();
  const [customUsername, setCustomUsername] = useState("");
  const [activeSkin, setActiveSkin] = useState(PRESET_SKINS[0]);
  const [loading, setLoading] = useState(false);

  // Direct Account Sync Modal State
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [syncSuccessMsg, setSyncSuccessMsg] = useState<string | null>(null);
  const [savedAccounts, setSavedAccounts] = useState<ClaimedAccountItem[]>([]);
  const [offlineInputIgn, setOfflineInputIgn] = useState<string>("");

  const isAr = lang === "ar";

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

  const handleFetchCustomUser = () => {
    if (!customUsername.trim()) return;
    const clean = customUsername.trim();
    setLoading(true);
    soundFx.playClick();

    const newSkin = {
      id: `custom_${clean.toLowerCase()}`,
      name: `${clean} (Custom IGN)`,
      nameAr: `${clean} (حساب مخصص)`,
      category: "Custom Player IGN",
      username: clean,
      preview: `https://minotar.net/armor/body/${clean}/300.png`,
      skinUrl: `https://minotar.net/skin/${clean}`
    };

    setActiveSkin(newSkin);
    setTimeout(() => setLoading(false), 200);
  };

  const handleStartSync = () => {
    soundFx.playClick();
    if (savedAccounts.length > 1) {
      setShowAccountModal(true);
    } else if (savedAccounts.length === 1) {
      executeSyncToAccount(savedAccounts[0].ign);
    } else {
      setOfflineInputIgn(activeSkin.username || "SirAhmed");
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
        localStorage.setItem(`sir_active_skin_${cleanIgn.toLowerCase()}`, JSON.stringify(activeSkin));
        const updatedAccounts = savedAccounts.some(a => a.ign.toLowerCase() === cleanIgn.toLowerCase())
          ? savedAccounts
          : [...savedAccounts, { ign: cleanIgn, skinUrl: activeSkin.skinUrl, model: "classic" as const }];
        localStorage.setItem("sir_claimed_accounts", JSON.stringify(updatedAccounts));
        setSavedAccounts(updatedAccounts);
      } catch {}
    }

    // 2. Push to Firestore if logged in
    if (user?.uid) {
      try {
        await saveClaimedAccountToCloud(user.uid, user.email, {
          ign: cleanIgn,
          skinUrl: activeSkin.skinUrl,
          model: "classic"
        });
      } catch (e) {
        console.warn("Cloud sync skin notice:", e);
      }
    }

    setShowAccountModal(false);
    setSyncSuccessMsg(
      isAr 
        ? `🎉 تم تطبيق ومزامنة سكن (${activeSkin.nameAr}) بنجاح لحساب @${cleanIgn}!`
        : `🎉 Skin (${activeSkin.name}) has been equipped & synced to account @${cleanIgn}!`
    );
    setTimeout(() => setSyncSuccessMsg(null), 4500);
  };

  return (
    <AuthGate featureName="HD Skins Studio" featureNameAr="استوديو السكنات ثلاثية الأبعاد">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-6xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-xs">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-xs">
            <Shirt className="w-3.5 h-3.5" />
            {isAr ? "استوديو السكنات والمزامنة المباشرة" : "3D Skin Studio & Live Sync"}
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "استوديو السكنات ومزامنة الحسابات السحابية" : "Minecraft Skin Studio & Cloud Sync"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "استعرض سكنات مشاهير ومطوري اللعبة أو اكتب اسم حسابك لمعاينته ثلاثي الأبعاد وتحميله وربطه بحسابك بنقرة واحدة."
              : "Browse verified player skins or preview your own Minecraft IGN in full 3D, download textures, and sync directly to your account."}
          </p>
        </div>

        {/* Sync Success Alert Notification */}
        {syncSuccessMsg && (
          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-500/50 text-emerald-800 dark:text-emerald-300 text-xs sm:text-sm font-bold flex items-center gap-3 shadow-lg shadow-emerald-500/10 animate-pop">
            <Check className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 stroke-[3]" />
            <span className="flex-1">{syncSuccessMsg}</span>
          </div>
        )}

        {/* Custom Username Bar */}
        <div className="p-4 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xl">
          <div className="relative w-full sm:flex-1">
            <input 
              type="text" 
              value={customUsername}
              onChange={e => setCustomUsername(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleFetchCustomUser()}
              placeholder={isAr ? "اكتب اسم حساب ماين كرافت لجلب سكنه (مثال: SirAhmed, Notch, Dream)..." : "Type any Minecraft IGN to preview their skin (e.g. SirAhmed, Notch, Dream)..."}
              className="w-full pl-4 pr-4 py-3 rounded-2xl bg-slate-50 dark:bg-[#070a10] border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 text-xs outline-none focus:border-cyan-500 transition-all font-mono placeholder-slate-400"
            />
          </div>
          <button 
            onClick={handleFetchCustomUser}
            className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            <span>{isAr ? "جلب السكن ومعاينته" : "Load Skin"}</span>
          </button>
        </div>

        {/* Main 3D Skin Stage Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          
          {/* Active Skin Showcase Card */}
          <div className="md:col-span-1 p-6 rounded-3xl bg-white dark:bg-[#101624] border border-slate-200 dark:border-cyan-500/40 text-center space-y-4 shadow-xl">
            <div className="flex justify-center pt-1 pb-1">
              <span className="inline-flex items-center gap-1.5 text-xs font-mono font-bold px-3.5 py-1.5 rounded-full bg-cyan-100 dark:bg-cyan-950/90 text-cyan-800 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-700 shadow-xs">
                <Sparkles className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
                <span>{activeSkin.category}</span>
              </span>
            </div>

            {/* 3D WebGL Skin Render Box */}
            <div className="w-full h-84 rounded-2xl overflow-hidden relative border border-slate-200 dark:border-slate-800 flex items-center justify-center bg-slate-100 dark:bg-[#070a10] shadow-inner">
              <Skin3DViewer
                skinUrl={activeSkin.skinUrl}
                width={260}
                height={320}
                enableAnimation={true}
              />
              <div className="absolute top-2 right-2 flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-[10px] font-mono text-slate-800 dark:text-cyan-400 shadow-md">
                <User className="w-3 h-3" />
                <span>@{activeSkin.username}</span>
              </div>
            </div>

            <div className="space-y-1">
              <h3 className="text-base font-black text-slate-900 dark:text-slate-100">{isAr ? activeSkin.nameAr : activeSkin.name}</h3>
              <p className="text-xs text-slate-500 font-mono">@{activeSkin.username}</p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-2.5 pt-3 border-t border-slate-200 dark:border-slate-800">
              <button
                onClick={handleStartSync}
                className="w-full py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
              >
                <Zap className="w-4 h-4 fill-slate-950" />
                <span>{isAr ? "⚡ مزامنة السكن مع حسابك" : "⚡ Sync Skin to Account"}</span>
              </button>

              <a 
                href={activeSkin.skinUrl}
                target="_blank" 
                rel="noreferrer"
                download={`${activeSkin.username}_skin.png`}
                className="w-full py-2.5 rounded-2xl bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs transition-all flex items-center justify-center gap-2 border border-slate-200 dark:border-slate-700 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>{isAr ? "تحميل ملف السكن (.png)" : "Download Skin Texture (.png)"}</span>
              </a>
            </div>

          </div>

          {/* Curated Presets Matrix */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-black text-slate-900 dark:text-slate-200 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
                <span>{isAr ? "سكنات المطورين والمشاهير المعتمدة" : "Curated Player & Creator Skins"}</span>
              </h3>
              <span className="text-[10px] font-mono text-cyan-800 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-950 px-2.5 py-0.5 rounded-full border border-cyan-300 dark:border-cyan-800 font-bold shadow-xs">
                {PRESET_SKINS.length} Verified Skins
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {PRESET_SKINS.map(skin => (
                <div
                  key={skin.id}
                  onClick={() => { 
                    soundFx.playClick();
                    setActiveSkin(skin); 
                  }}
                  className={`p-4 rounded-2xl border text-left cursor-pointer transition-all flex items-center gap-4 shadow-xs ${
                    activeSkin.id === skin.id 
                      ? 'border-cyan-500 dark:border-cyan-400 bg-cyan-50/80 dark:bg-cyan-950/40 shadow-md ring-2 ring-cyan-500/50 dark:ring-cyan-400/50' 
                      : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-[#101624] hover:border-cyan-400 dark:hover:border-cyan-500/40 hover:bg-slate-50 dark:hover:bg-[#141b2d]'
                  }`}
                >
                  <img 
                    src={`https://mc-heads.net/avatar/${skin.username}/48`}
                    alt={skin.name}
                    className="w-12 h-12 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-900 object-cover shadow-xs"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "https://minotar.net/avatar/Steve/48.png";
                    }}
                  />
                  <div className="min-w-0 flex-1 space-y-1">
                    <h4 className="text-xs font-black text-slate-900 dark:text-slate-100 truncate">
                      {isAr ? skin.nameAr : skin.name}
                    </h4>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                      @{skin.username}
                    </p>
                    <span className="inline-block text-[9px] font-mono text-cyan-700 dark:text-cyan-400 font-bold">
                      {skin.category}
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
                  <span>{isAr ? "اختر الحساب لتطبيق السكن عليه" : "Select Account to Equip Skin"}</span>
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
                          {isAr ? "تطبيق ←" : "Equip →"}
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
        <ConnectedFeaturesHub currentPath="/skins" />

      </div>
    </div>
    </AuthGate>);
}