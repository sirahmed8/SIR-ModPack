"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  Layers, 
  Sparkles, 
  Zap, 
  Swords, 
  Cpu, 
  CheckCircle2, 
  ArrowRight,
  ArrowLeft,
  Sliders,
  ShieldCheck,
  Flame,
  Activity,
  HardDrive
} from "lucide-react";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";

export default function ProfilesMatrixPage() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";
  const [activeTab, setActiveTab] = useState<"modern" | "legacy">("modern");

  const modernProfiles = [
    {
      id: "ultra",
      name: "SIR 26 Ultra Fidelity",
      badge: "✨ 4K Raytracing",
      badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
      fps: "144+ FPS",
      ram: "8 GB RAM",
      shader: "SIR_Extreme_Shader.zip",
      pack: "SIR_Ultimate_Pack.zip (3D POM)",
      desc: isAr 
        ? "أعلى مستوى من الجمالية البصرية: غلاف جوي حجمي، انعكاسات SSR فيزيائية، مياه كريستالية، ومجسمات كتل ثلاثية الأبعاد."
        : "The ultimate visual feast: volumetric atmosphere, raymarched SSR reflections, crystal transparent water, and full 3D POM relief."
    },
    {
      id: "balanced",
      name: "SIR 26 Balanced 144Hz",
      badge: "⚡ High-Refresh Lock",
      badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      fps: "180+ FPS",
      ram: "6-8 GB RAM",
      shader: "SIR_Balanced_Shader.zip",
      pack: "SIR_Ultimate_Pack.zip",
      desc: isAr
        ? "معدل إطارات مرتفع وثابت مع الحفاظ على نفس جمالية الشمس الدائرية المتوهجة والمياه الكريستالية."
        : "Rock-solid 180+ FPS lock on high-refresh monitors while preserving the exact same glowing circular sun and crystal water."
    },
    {
      id: "performance",
      name: "SIR 26 Competitive Speed",
      badge: "🏆 0ms Latency",
      badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/40",
      fps: "350+ FPS",
      ram: "4-6 GB RAM",
      shader: "OFF (Pure Sodium Engine)",
      pack: "SIR_Ultimate_Pack.zip",
      desc: isAr
        ? "محرك رندر فائق السرعة بدون شيدرز للمبارزات التنافسية الحديثة وسرعة تسجيل الضربات الفورية."
        : "Ultra-low render latency pipeline tuned for competitive modern PvP and instantaneous hit registration."
    }
  ];

  const legacyProfiles = [
    {
      id: "189-ultra",
      name: "Legacy 1.8.9 Cinematic",
      badge: "🌟 Visuals & Shaders",
      badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
      fps: "240+ FPS",
      ram: "6 GB RAM",
      shader: "OptiFine Shaders",
      pack: "SIR_Legacy_32x.zip",
      desc: isAr
        ? "أعلى تجربة بصرية على 1.8.9 مع إضاءات وظلال OptiFine المخصصة والسماء المتحركة ودعم الكيبات وسكنات 3D."
        : "Rich visual experience on 1.8.9 with customized OptiFine lighting, smooth shadows, dynamic skybox, and 3D skin layers."
    },
    {
      id: "189-balanced",
      name: "Legacy 1.8.9 Balanced PvP",
      badge: "⚡ 500+ FPS Balanced",
      badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
      fps: "500+ FPS",
      ram: "4-6 GB RAM",
      shader: "OFF (BetterFPS)",
      pack: "SIR_Legacy_32x.zip",
      desc: isAr
        ? "المزيج المثالي للمبارزات: حركات 1.7 السلسة، تحسين ذاكرة BetterFPS، مؤشرات دروع مخصصة، وثبات الإطارات الكامل."
        : "The ideal PvP balance: 1.7 fluid animations, BetterFPS memory optimization, custom HUD, and locked high framerates."
    },
    {
      id: "189-pvp",
      name: "Legacy 1.8.9 PvP Battle Suite",
      badge: "⚔️ Hypixel Master",
      badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/40",
      fps: "1000+ FPS",
      ram: "4 GB RAM",
      shader: "OFF",
      pack: "SIR_Legacy_32x.zip",
      desc: isAr
        ? "التجهيز التنافسي المعتمد لسيرفر Hypixel: حركات سيوف 1.7، عداد نقرات CPS، مؤشر الدروع، وسيوف قصيرة وانعدام بطء الماوس."
        : "The definitive 1.8.9 tournament suite: 1.7 block-hit animations, CPS counter, Armor HUD, short swords, and 0ms RawInput mouse tracking."
    }
  ];

  const currentProfiles = activeTab === "modern" ? modernProfiles : legacyProfiles;

  return (
    <AuthGate featureName="Account Linking Hub" featureNameAr="ربط الحسابات وإدارة البروفايلات">
      <div className="min-h-screen bg-[#070a10] text-white pt-24 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-12">
        
        {/* Header Hero */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-semibold backdrop-blur-md"
          >
            <Layers className="w-4 h-4" />
            <span>{isAr ? "مصفوفة البروفايلات والنسخ المتوافقة" : "8-Tier Profile & Instance Architecture"}</span>
          </motion.div>
          
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
            {isAr ? "اختر البروفايل المثالي لجهازك" : "Engineered for Every Playstyle & Rig"}
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto text-base sm:text-lg">
            {isAr
              ? "سواء كنت تبحث عن رسوميات 4K خرافية أو سرعة خارقة تفوق 500 إطار في الثانية، كل بروفايل مجهز ومضبوط مسبقاً."
              : "Whether you want cinematic 4K raytracing or 500+ FPS Hypixel competitive speed, every profile is pre-configured out-of-the-box."}
          </p>
        </div>

        {/* Modern vs Legacy Switcher */}
        <div className="flex justify-center">
          <div className="p-1.5 rounded-2xl bg-[#0d121d] border border-slate-800 flex items-center gap-2">
            <button
              onClick={() => setActiveTab("modern")}
              className={`px-6 py-2.5 rounded-xl text-xs font-black transition-all ${
                activeTab === "modern"
                  ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              🌟 Modern 26.2 (Fabric 1.21.4)
            </button>
            <button
              onClick={() => setActiveTab("legacy")}
              className={`px-6 py-2.5 rounded-xl text-xs font-black transition-all ${
                activeTab === "legacy"
                  ? "bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              ⚔️ Legacy 1.8.9 (Forge PvP)
            </button>
          </div>
        </div>

        {/* Profiles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {currentProfiles.map((p) => (
            <div
              key={p.id}
              className="p-6 rounded-3xl bg-[#0d121d]/90 border border-slate-800 hover:border-cyan-500/50 transition-all flex flex-col justify-between hover:shadow-2xl hover:shadow-cyan-500/5"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-full border ${p.badgeColor}`}>
                    {p.badge}
                  </span>
                  <span className="text-xs font-mono font-bold text-cyan-400">{p.fps}</span>
                </div>

                <h3 className="text-xl font-bold text-white mt-4">{p.name}</h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">{p.desc}</p>

                <div className="mt-6 space-y-2 border-t border-slate-800/80 pt-4 text-xs font-mono">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>RAM Requirement:</span>
                    <span className="text-slate-200 font-bold">{p.ram}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Active Shaders:</span>
                    <span className="text-cyan-400 font-bold truncate max-w-[150px]">{p.shader}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Resource Pack:</span>
                    <span className="text-emerald-400 font-bold truncate max-w-[150px]">{p.pack}</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800/80">
                <span className="flex items-center justify-center gap-1.5 text-xs text-emerald-400 font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Pre-Configured & Installed</span>
                </span>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
    </AuthGate>);
}