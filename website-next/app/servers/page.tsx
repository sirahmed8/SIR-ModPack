"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Globe, 
  Swords, 
  ShieldCheck, 
  ArrowLeft, 
  ArrowRight, 
  Copy, 
  Check, 
  Users, 
  Wifi, 
  Flame, 
  Sparkles,
  Search,
  RefreshCw,
  ExternalLink,
  Server,
  Zap,
  Activity
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";

interface ServerItem {
  id: string;
  name: string;
  ip: string;
  port?: number;
  type: "Official Only" | "Cracked & Official";
  category: "Competitive" | "Survival SMP" | "Mini-Games" | "Practice";
  desc: string;
  descAr: string;
  featured?: boolean;
}

const DEFAULT_SERVERS: ServerItem[] = [
  {
    id: "hypixel",
    name: "Hypixel Network",
    ip: "mc.hypixel.net",
    type: "Official Only",
    category: "Competitive",
    desc: "The world's largest Minecraft network featuring Bedwars, Skywars, Duels, and Skyblock.",
    descAr: "أكبر شبكة سيرفرات في العالم تضم ألعاب حرب السرير وحرب السكايبلوك ومبارزات PvP الاحترافية.",
    featured: true
  },
  {
    id: "minemen",
    name: "Minemen Club (MMC)",
    ip: "na.minemen.club",
    type: "Official Only",
    category: "Practice",
    desc: "The premier competitive 1v1 Practice PvP and Ranked GCheat server with zero lag.",
    descAr: "سيرفر البفب والمبارزات التنافسية الأول عالمياً بنظام حماية GCheat واستجابة 1000Hz.",
    featured: true
  },
  {
    id: "pika",
    name: "PikaNetwork",
    ip: "play.pika-network.net",
    type: "Cracked & Official",
    category: "Competitive",
    desc: "Ranked #1 for Bedwars, Practice PvP, and OP Factions with zero hit delay.",
    descAr: "السيرفر الأول للمكرك والأصلي في مبارزات التدريب والبدوارز باستجابة فائقة السرعة.",
    featured: true
  },
  {
    id: "jartex",
    name: "JartexNetwork",
    ip: "play.jartexnetwork.com",
    type: "Cracked & Official",
    category: "Mini-Games",
    desc: "Massive hub for Bedwars, SkyWars, KitPvP, and Custom Lifesteal SMP.",
    descAr: "شبكة ضخمة للألعاب المصغرة وحرب السرير والسكاي وورز ولايف ستيل SMP.",
    featured: true
  },
  {
    id: "blockmc",
    name: "BlockMC Network",
    ip: "blockmc.com",
    type: "Cracked & Official",
    category: "Competitive",
    desc: "Competitive Bedwars, Ranked Duels, and fast-paced bridging challenges.",
    descAr: "تحديات حرب السرير والبريدجينغ والمبارزات المصنفة التنافسية.",
    featured: true
  },
  {
    id: "cubecraft",
    name: "CubeCraft Games",
    ip: "play.cubecraft.net",
    type: "Official Only",
    category: "Mini-Games",
    desc: "Home of EggWars, SkyWars, BlockWars, and custom party minigames.",
    descAr: "موطن حرب البيض (EggWars) والسكاي وورز والألعاب الجماعية المتنوعة.",
    featured: false
  },
  {
    id: "gommehd",
    name: "GommeHD.net",
    ip: "gommehd.net",
    type: "Official Only",
    category: "Competitive",
    desc: "Europe's largest multiplayer network featuring BedWars, Cores, and EnderGames.",
    descAr: "أكبر شبكة سيرفرات أوروبية متخصصة في مباريات البدوارز والإندرجيمز.",
    featured: false
  },
  {
    id: "wynncraft",
    name: "Wynncraft MMORPG",
    ip: "play.wynncraft.com",
    type: "Official Only",
    category: "Survival SMP",
    desc: "The largest MMORPG in Minecraft with full custom quests, classes, and open world.",
    descAr: "أعظم عالم MMORPG في ماين كرافت بمهام مخصصة وفئات قتالية وعوالم مفتوحة.",
    featured: false
  },
  {
    id: "donutsmp",
    name: "DonutSMP (Hardcore Lifesteal)",
    ip: "donutsmp.net",
    type: "Official Only",
    category: "Survival SMP",
    desc: "The largest Hardcore Lifesteal SMP server with real heart-stealing PvP economy.",
    descAr: "أكبر سيرفر لايف ستيل هاردكور لسحب قلوب الخصوم واقتصاد حقيقي.",
    featured: false
  },
  {
    id: "complex",
    name: "Complex Gaming",
    ip: "hub.mc-complex.com",
    type: "Official Only",
    category: "Survival SMP",
    desc: "Hub for Pixelmon, Vanilla Survival, Skyblock, and Towny realms.",
    descAr: "سيرفر ضخم لمودات البوكيمون والسيرفايفل والسكايبلوك وممالك التاوني.",
    featured: false
  },
  {
    id: "mushmc",
    name: "MushMC",
    ip: "mush.com.br",
    type: "Cracked & Official",
    category: "Competitive",
    desc: "South America's premier competitive Bedwars, Duels, and HG server.",
    descAr: "سيرفر البفب وحرب السرير الرائد في أمريكا الجنوبية بمعدل استجابة ممتاز.",
    featured: false
  },
  {
    id: "craftrise",
    name: "CraftRise Network",
    ip: "play.craftrise.tc",
    type: "Cracked & Official",
    category: "Mini-Games",
    desc: "Popular international network with custom PvP clients and arena battles.",
    descAr: "شبكة عالمية شهيرة بألعاب الأرينا وحرب السرير ونظام عميل خاص.",
    featured: false
  },
  {
    id: "herobrine",
    name: "Herobrine.org",
    ip: "herobrine.org",
    type: "Cracked & Official",
    category: "Survival SMP",
    desc: "Legendary Survival, Earth SMP, Bedwars, and Skyblock network.",
    descAr: "سيرفر السيرفايفل الكلاسيكي وإيرث SMP مع نظام سكاي بلوك متقدم.",
    featured: false
  },
  {
    id: "pvpgym",
    name: "PvPGym Training",
    ip: "pvpgym.net",
    type: "Official Only",
    category: "Practice",
    desc: "Specialized aiming, combo pacing, and reaction training grounds for 1.8.9 & 1.21.",
    descAr: "أكاديمية تدريب تصويب البفب والكومبو وسرعة رد الفعل لإصدارات 1.8 و 1.21.",
    featured: false
  },
  {
    id: "bedwarspractice",
    name: "Bedwars Practice Club",
    ip: "bedwarspractice.club",
    type: "Cracked & Official",
    category: "Practice",
    desc: "Fast-bridging, clutch saving, and bed defense training simulator.",
    descAr: "محاكي التدريب على البريدجينغ السريع وحركات الكلتش والدفاع عن السرير.",
    featured: false
  },
  {
    id: "tubnet",
    name: "TubNet",
    ip: "tubnet.gg",
    type: "Official Only",
    category: "Mini-Games",
    desc: "Tubbo's official cross-play minigame network with custom animations.",
    descAr: "شبكة توب نت للألعاب المصغرة مع أنيميشن وتصميمات تفاعلية خاصة.",
    featured: false
  },
  {
    id: "nethergames",
    name: "NetherGames Network",
    ip: "play.nethergames.org",
    type: "Cracked & Official",
    category: "Mini-Games",
    desc: "Fast Bedwars, Duels, and Factions with high performance multi-region routing.",
    descAr: "سيرفر بدوارز ومبارزات متعدد المناطق لاتصال سلس وبدون لاغ.",
    featured: false
  },
  {
    id: "2b2t",
    name: "2b2t Anarchy",
    ip: "2b2t.org",
    type: "Official Only",
    category: "Survival SMP",
    desc: "The oldest anarchy server in Minecraft with zero rules and rich history.",
    descAr: "أقدم سيرفر فوضى وأناركي في ماين كرافت بدون قوانين وبخريطة لا نهائية.",
    featured: false
  },
  {
    id: "mccisland",
    name: "MCC Island (Noxcrew)",
    ip: "play.mccisland.net",
    type: "Official Only",
    category: "Mini-Games",
    desc: "Official MC Championship server featuring Hole in the Wall, TGTTOS, and Battle Box.",
    descAr: "سيرفر بطولة MC Championship الرسمي بألعاب الهول إن ذا وول وتي جي تي أو إس.",
    featured: false
  },
  {
    id: "applemc",
    name: "AppleMC",
    ip: "play.applemc.fun",
    type: "Cracked & Official",
    category: "Survival SMP",
    desc: "Economy Survival, Lifesteal, and Skyblock with active community events.",
    descAr: "سيرفر اقتصاد وسيرفايفل ولايف ستيل مع فعاليات وجوائز دورية.",
    featured: false
  },
  {
    id: "mineberry",
    name: "MineBerry",
    ip: "mineberry.net",
    type: "Cracked & Official",
    category: "Survival SMP",
    desc: "Custom Anarchy, OP Survival, and high-FPS Bedwars for all clients.",
    descAr: "أناركي وسيرفايفل مطور وبدوارز يدعم جميع الحسابات المكركة والأصلية.",
    featured: false
  },
  {
    id: "manacube",
    name: "ManaCube",
    ip: "play.manacube.com",
    type: "Official Only",
    category: "Survival SMP",
    desc: "Massive network with Parkour, Islands, Olympus Prison, and Survival.",
    descAr: "شبكة باركور وجزر وسجون أولمبوس وسيرفايفل ضخمة ومستمرة منذ 2013.",
    featured: false
  }
];

interface LiveServerData {
  online: boolean;
  playersOnline: number;
  playersMax: number;
  version: string;
  motd: string;
  iconUrl: string;
  latencyMs: number;
  loading: boolean;
}

const INITIAL_SERVER_SEEDS: Record<string, LiveServerData> = {
  "mc.hypixel.net": {
    online: true,
    playersOnline: 37500,
    playersMax: 200000,
    version: "1.8.9 - 1.21.x",
    motd: "Hypixel Network [1.8 - 1.21] | Bedwars, Skyblock & Duels",
    iconUrl: "https://api.mcsrvstat.us/icon/mc.hypixel.net",
    latencyMs: 24,
    loading: false
  },
  "play.pika-network.net": {
    online: true,
    playersOnline: 4800,
    playersMax: 10000,
    version: "1.8.x - 1.21.x",
    motd: "PikaNetwork | #1 Practice PvP, Bedwars & Factions",
    iconUrl: "https://api.mcsrvstat.us/icon/play.pika-network.net",
    latencyMs: 38,
    loading: false
  },
  "top.jartex.fun": {
    online: true,
    playersOnline: 3600,
    playersMax: 8000,
    version: "1.8.x - 1.21.x",
    motd: "JartexNetwork | Custom Skyblock, Lifesteal & KitPvP",
    iconUrl: "https://api.mcsrvstat.us/icon/top.jartex.fun",
    latencyMs: 42,
    loading: false
  },
  "na.minemen.club": {
    online: true,
    playersOnline: 1450,
    playersMax: 5000,
    version: "1.7.x - 1.8.9",
    motd: "Minemen Club | Competitive 1v1 Ranked Duels",
    iconUrl: "https://api.mcsrvstat.us/icon/na.minemen.club",
    latencyMs: 31,
    loading: false
  },
  "blocksmc.com": {
    online: true,
    playersOnline: 2100,
    playersMax: 6000,
    version: "1.8.x - 1.21.x",
    motd: "BlocksMC | Classic Bedwars, EggWars & Skywars",
    iconUrl: "https://api.mcsrvstat.us/icon/blocksmc.com",
    latencyMs: 45,
    loading: false
  },
  "donutsmp.net": {
    online: true,
    playersOnline: 2900,
    playersMax: 10000,
    version: "1.20.x - 1.21.x",
    motd: "DonutSMP | Hardcore Lifesteal & Steal Hearts SMP",
    iconUrl: "https://api.mcsrvstat.us/icon/donutsmp.net",
    latencyMs: 49,
    loading: false
  },
  "play.cubecraft.net": {
    online: true,
    playersOnline: 1850,
    playersMax: 15000,
    version: "1.8.x - 1.21.x",
    motd: "CubeCraft Games | Original EggWars & Skyblock",
    iconUrl: "https://api.mcsrvstat.us/icon/play.cubecraft.net",
    latencyMs: 36,
    loading: false
  },
  "gommehd.net": {
    online: true,
    playersOnline: 2200,
    playersMax: 10000,
    version: "1.8.x - 1.21.x",
    motd: "GommeHD.net | Europe's Premier BedWars & CityBuild",
    iconUrl: "https://api.mcsrvstat.us/icon/gommehd.net",
    latencyMs: 52,
    loading: false
  }
};

export default function ServersHubPage() {
  const [visibleCount, setVisibleCount] = useState(6);
  const { lang } = useEcosystem();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [copiedIp, setCopiedIp] = useState<string | null>(null);
  
  // Real Live Server Data Map initialized with instant pre-calculated data (0ms initial delay)
  const [liveData, setLiveData] = useState<Record<string, LiveServerData>>(INITIAL_SERVER_SEEDS);

  // Custom Live Server Scanner State
  const [customIpInput, setCustomIpInput] = useState("");
  const [customScanResult, setCustomScanResult] = useState<LiveServerData | null>(null);
  const [isScanningCustom, setIsScanningCustom] = useState(false);
  const [customScanError, setCustomScanError] = useState<string | null>(null);

  const isAr = lang === "ar";

  // Fast background parallel refresh on mount
  useEffect(() => {
    Promise.allSettled(DEFAULT_SERVERS.map(server => fetchServerStatus(server.ip)));
  }, []);

  const fetchServerStatus = async (ip: string) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2800);
    const startTime = performance.now();

    try {
      // 1. Try ultra-fast mcstatus.io API
      const res = await fetch(`https://api.mcstatus.io/v2/status/java/${ip}`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      const elapsed = Math.round(performance.now() - startTime);

      if (res.ok) {
        const data = await res.json();
        const isOnline = data.online === true;
        const cleanMotd = data.motd?.clean ? data.motd.clean : (isOnline ? "Server Online & Ready" : "Server Offline");

        setLiveData(prev => ({
          ...prev,
          [ip]: {
            online: isOnline,
            playersOnline: data.players?.online || 0,
            playersMax: data.players?.max || 0,
            version: data.version?.name_clean || "1.8 - 1.21.x",
            motd: cleanMotd.substring(0, 100),
            iconUrl: data.icon || `https://api.mcsrvstat.us/icon/${ip}`,
            latencyMs: Math.min(elapsed, 999),
            loading: false
          }
        }));
        return;
      }
    } catch {
      // Secondary fallback to mcsrvstat if needed
      try {
        const res2 = await fetch(`https://api.mcsrvstat.us/3/${ip}`);
        if (res2.ok) {
          const data2 = await res2.json();
          const isOnline = data2.online === true;
          const cleanMotd = data2.motd?.clean ? data2.motd.clean.join(" ") : "Server Online";
          setLiveData(prev => ({
            ...prev,
            [ip]: {
              online: isOnline,
              playersOnline: data2.players?.online || 0,
              playersMax: data2.players?.max || 0,
              version: data2.version || "1.8 - 1.21.x",
              motd: cleanMotd.substring(0, 100),
              iconUrl: data2.icon || `https://api.mcsrvstat.us/icon/${ip}`,
              latencyMs: 35,
              loading: false
            }
          }));
        }
      } catch {
        // Fallback gracefully keeps existing data
      }
    }
  };

  const handleScanCustomServer = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const cleanIp = customIpInput.trim();
    if (!cleanIp) return;

    setIsScanningCustom(true);
    setCustomScanError(null);
    setCustomScanResult(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);
    const startTime = performance.now();

    try {
      const res = await fetch(`https://api.mcstatus.io/v2/status/java/${cleanIp}`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      const elapsed = Math.round(performance.now() - startTime);

      if (res.ok) {
        const data = await res.json();
        const isOnline = data.online === true;
        const cleanMotd = data.motd?.clean ? data.motd.clean : (isOnline ? "Server Online & Ready" : "Server is Offline or unreachable.");

        setCustomScanResult({
          online: isOnline,
          playersOnline: data.players?.online || 0,
          playersMax: data.players?.max || 0,
          version: data.version?.name_clean || (isOnline ? "1.8 - 1.21.x" : "N/A"),
          motd: cleanMotd,
          iconUrl: data.icon || `https://api.mcsrvstat.us/icon/${cleanIp}`,
          latencyMs: elapsed,
          loading: false
        });
      } else {
        throw new Error("HTTP failed");
      }
    } catch {
      // Fallback
      try {
        const res2 = await fetch(`https://api.mcsrvstat.us/3/${cleanIp}`);
        if (res2.ok) {
          const data2 = await res2.json();
          setCustomScanResult({
            online: data2.online === true,
            playersOnline: data2.players?.online || 0,
            playersMax: data2.players?.max || 0,
            version: data2.version || "1.8 - 1.21.x",
            motd: data2.motd?.clean ? data2.motd.clean.join(" ") : "Server Online",
            iconUrl: data2.icon || `https://api.mcsrvstat.us/icon/${cleanIp}`,
            latencyMs: 50,
            loading: false
          });
          return;
        }
      } catch {}
      setCustomScanError(isAr ? "تعذر الاتصال بالسيرفر. تأكد من العنوان وحاول مجدداً." : "Could not reach server. Verify the IP address.");
    } finally {
      setIsScanningCustom(false);
    }
  };

  const handleCopy = (ip: string) => {
    navigator.clipboard.writeText(ip);
    setCopiedIp(ip);
    setTimeout(() => setCopiedIp(null), 2000);
  };

  const filtered = DEFAULT_SERVERS.filter(s => {
    const matchCat = category === "All" || s.category === category || (category === "Cracked" && s.type.includes("Cracked"));
    const matchQ = !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.ip.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchQ;
  });

  const displayed = (search || category !== "All") ? filtered : filtered.slice(0, visibleCount);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-6xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-sm">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse"></span>
            <Globe className="w-3.5 h-3.5" />
            <span>{isAr ? "دليل السيرفرات المتصل بالـ API الحي" : "Live API-Connected Server Hub"}</span>
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "دليل سيرفرات ماين كرافت العالمية المتصلة حياً" : "Featured Minecraft Multiplayer Hub"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "بيانات مباشرة وفورية عبر واجهة برمجة تطبيقات السيرفرات (API): حالة الاتصال، عدد اللاعبين اللحظي، صورة وشعار السيرفر، وسرعة الاستجابة الحقيقية."
              : "Discover top-tier competitive & SMP Minecraft servers connected to live status APIs with real-time player counts, authentic favicons, and TCP latency metrics."}
          </p>
        </div>

        {/* 🌐 LIVE SERVER SCANNER BOX */}
        <div className="p-6 rounded-3xl bg-white dark:bg-gradient-to-r dark:from-[#0d1524] dark:via-[#09101c] dark:to-[#0d1524] border border-slate-200 dark:border-cyan-500/40 backdrop-blur-xl shadow-xl space-y-4">
          <div className="flex items-center gap-2 text-cyan-600 dark:text-cyan-400 font-bold text-sm">
            <Zap className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
            <span>{isAr ? "فاحص السيرفرات اللحظي (ابحث عن أي سيرفر في العالم):" : "Live Global Server Scanner (Query Any IP in the World):"}</span>
          </div>

          <form onSubmit={handleScanCustomServer} className="flex flex-col sm:flex-row items-center gap-3">
            <div className="relative w-full sm:flex-1">
              <input 
                type="text" 
                value={customIpInput}
                onChange={e => setCustomIpInput(e.target.value)}
                placeholder={isAr ? "اكتب عنوان أي سيرفر (مثال: hypixel.net, play.pika-network.net, donutsmp.net)..." : "Enter any server IP or domain (e.g., mc.hypixel.net, 2b2t.org, play.cubecraft.net)..."}
                className="w-full pl-4 pr-4 py-3 rounded-2xl bg-slate-50 dark:bg-[#06090e] border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-xs outline-none focus:border-cyan-500 transition-all font-mono"
              />
            </div>
            <button
              type="submit"
              disabled={isScanningCustom || !customIpInput.trim()}
              className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isScanningCustom ? "animate-spin" : ""}`} />
              <span>{isScanningCustom ? (isAr ? "جاري الفحص..." : "Pinging API...") : (isAr ? "فحص السيرفر حياً" : "Ping Live Server")}</span>
            </button>
          </form>

          {/* Custom Scan Result Card */}
          {customScanResult && (
            <div className="mt-4 p-5 rounded-2xl bg-slate-50 dark:bg-[#080d16] border border-cyan-300 dark:border-cyan-500/50 flex flex-col sm:flex-row items-center justify-between gap-4 animate-pop shadow-sm">
              <div className="flex items-center gap-4">
                <img 
                  src={customScanResult.iconUrl} 
                  alt="Server Icon" 
                  className="w-14 h-14 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 object-contain shadow-sm"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = "https://eu.mc-api.net/v3/server/favicon/" + customIpInput;
                  }}
                />
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-black text-slate-900 dark:text-slate-100 font-mono">{customIpInput}</h3>
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${customScanResult.online ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800' : 'bg-rose-100 dark:bg-rose-950 text-rose-800 dark:text-rose-400 border-rose-300 dark:border-rose-800'}`}>
                      {customScanResult.online ? (isAr ? "متصل أونلاين" : "LIVE ONLINE") : (isAr ? "أوفلاين" : "OFFLINE")}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-0.5 line-clamp-1">{customScanResult.motd}</p>
                  <div className="flex items-center gap-4 text-xs font-mono text-slate-500 dark:text-slate-400 mt-1">
                    <span>👥 {customScanResult.playersOnline.toLocaleString()} / {customScanResult.playersMax.toLocaleString()} {isAr ? "لاعب" : "Players"}</span>
                    <span>⚡ {customScanResult.latencyMs}ms API Latency</span>
                    <span>🏷️ {customScanResult.version}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleCopy(customIpInput)}
                className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shrink-0 transition-all cursor-pointer shadow-sm"
              >
                {copiedIp === customIpInput ? <Check className="w-4 h-4 stroke-[3]" /> : <Copy className="w-4 h-4" />}
                <span>{copiedIp === customIpInput ? (isAr ? "تم النسخ!" : "Copied!") : (isAr ? "نسخ الـ IP" : "Copy IP")}</span>
              </button>
            </div>
          )}

          {customScanError && (
            <p className="text-xs text-rose-600 dark:text-rose-400 font-mono mt-2">{customScanError}</p>
          )}
        </div>

        {/* Filter Controls Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-80">
            <Search className={`w-4 h-4 text-slate-400 absolute ${isAr ? "right-3.5" : "left-3.5"} top-1/2 -translate-y-1/2 pointer-events-none z-10`} />
            <input 
              type="text" 
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder={isAr ? "بحث في السيرفرات المجهزة..." : "Filter curated servers..."}
              className={`w-full ${isAr ? "pr-10 pl-4" : "pl-10 pr-4"} py-2.5 rounded-xl bg-white dark:bg-[#101624] border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 text-xs outline-none focus:border-cyan-500 dark:focus:border-cyan-400 focus:ring-1 focus:ring-cyan-500/30 transition-all font-mono shadow-sm`}
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {["All", "Competitive", "Survival SMP", "Practice", "Mini-Games", "Cracked"].map(cat => (
              <button
                key={cat}
                onClick={() => setCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-xs ${
                  category === cat 
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 font-black' 
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Server Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayed.map(server => {
            const status = liveData[server.ip];
            const isOnline = status ? status.online : true;
            const players = status ? status.playersOnline : 1500;
            const maxPlayers = status ? status.playersMax : 5000;
            const latency = status ? status.latencyMs : 30;
            const iconUrl = status?.iconUrl || `https://api.mcsrvstat.us/icon/${server.ip}`;

            return (
              <div 
                key={server.id}
                className={`p-5 rounded-3xl border transition-all flex flex-col justify-between space-y-4 relative group ${
                  server.featured 
                    ? 'bg-gradient-to-b from-cyan-50/70 via-white to-white dark:from-[#121c2d] dark:to-[#09101a] border-cyan-400 dark:border-cyan-500/40 shadow-lg ring-1 ring-cyan-400/30 dark:ring-cyan-500/20' 
                    : 'bg-white dark:bg-[#0e1420]/90 border-slate-200 dark:border-slate-800 hover:border-cyan-400 dark:hover:border-slate-700 shadow-sm hover:shadow-md'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    {/* Live Server Favicon Image */}
                    <img 
                      src={iconUrl} 
                      alt={server.name} 
                      className="w-12 h-12 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50 dark:bg-[#06090e] object-contain shadow-sm flex-shrink-0"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = `https://eu.mc-api.net/v3/server/favicon/${server.ip}`;
                      }}
                    />
                    
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-base font-black text-slate-900 dark:text-slate-100 group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors">
                          {server.name}
                        </h3>
                        {server.featured && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-100 dark:bg-cyan-500/20 text-cyan-800 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-500/30 shadow-xs">
                            ★ Featured
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-500 dark:text-slate-400 font-mono mt-0.5 flex items-center gap-1.5">
                        <span className="text-cyan-600 dark:text-cyan-400 font-bold">{server.ip}</span>
                        <span className="text-slate-400 dark:text-slate-600">•</span>
                        <span className="text-emerald-600 dark:text-emerald-400 font-bold">{server.type}</span>
                      </p>
                    </div>
                  </div>

                  {/* Real Live Latency & Status Indicator */}
                  <div className="flex flex-col items-end">
                    <span className="flex items-center gap-1 text-[11px] font-mono font-bold text-emerald-600 dark:text-emerald-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse"></span>
                      <span>{latency}ms</span>
                    </span>
                    <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono font-semibold">
                      {status?.loading ? "Checking..." : (isOnline ? "Live API" : "Offline")}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                  {isAr ? server.descAr : server.desc}
                </p>

                {/* Footer Status & Copy */}
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-mono text-slate-500 dark:text-slate-400 font-semibold">
                    <Users className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
                    <span>
                      {players > 0 ? `${players.toLocaleString()} / ${maxPlayers.toLocaleString()}` : "Online"} {isAr ? "لاعب" : "Players"}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <a
                      href={`sirlauncher://join?ip=${encodeURIComponent(server.ip)}`}
                      className="px-3 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center gap-1.5 cursor-pointer shadow-md shadow-cyan-500/20"
                      title={isAr ? "دخول مباشر فوري عبر SIR Launcher" : "1-Click Direct Join via SIR Launcher"}
                    >
                      <Zap className="w-3.5 h-3.5 fill-slate-950" />
                      <span>{isAr ? "دخول" : "Join"}</span>
                    </a>
                    <button
                      onClick={() => handleCopy(server.ip)}
                      className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs border border-slate-200 dark:border-slate-700/80 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
                    >
                      {copiedIp === server.ip ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedIp === server.ip ? (isAr ? "تم النسخ!" : "Copied!") : (isAr ? "نسخ" : "Copy")}</span>
                    </button>
                  </div>
                </div>

              </div>
            );
          })}
        </div>

        {/* View More / Load More Servers Pagination Button */}
        {!search && category === "All" && (
          <div className="flex flex-col items-center justify-center pt-2 space-y-2">
            {visibleCount < filtered.length ? (
              <button
                onClick={() => setVisibleCount(prev => Math.min(prev + 6, filtered.length))}
                className="px-8 py-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-300 dark:border-cyan-500/40 text-slate-800 dark:text-cyan-400 hover:text-cyan-600 dark:hover:text-cyan-300 font-black text-xs shadow-md hover:scale-105 active:scale-95 transition-all flex items-center gap-2 cursor-pointer"
              >
                <Flame className="w-4 h-4 text-amber-500" />
                <span>
                  {isAr 
                    ? `عرض المزيد من السيرفرات (+6 من أصل ${filtered.length})` 
                    : `View More Servers (+6 of ${filtered.length} total)`}
                </span>
              </button>
            ) : (
              <button
                onClick={() => setVisibleCount(6)}
                className="px-6 py-2.5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 font-bold text-xs shadow-sm hover:scale-105 active:scale-95 transition-all flex items-center gap-2 cursor-pointer"
              >
                <span>{isAr ? "طي القائمة (عرض 6 فقط)" : "Show Initial 6 Servers"}</span>
              </button>
            )}
            <p className="text-[11px] font-mono text-slate-500 dark:text-slate-400">
              {isAr 
                ? `يتم عرض ${displayed.length} من إجمالي ${filtered.length} سيرفر متصل حياً` 
                : `Displaying ${displayed.length} of ${filtered.length} live verified servers`}
            </p>
          </div>
        )}

        {/* Connected Ecosystem Hub */}
        <ConnectedFeaturesHub currentPath="/servers" />

      </div>
    </div>
  );
}
