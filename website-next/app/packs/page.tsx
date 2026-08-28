"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  Layers, 
  Sparkles, 
  Download, 
  CheckCircle2, 
  ShieldCheck, 
  Flame, 
  Eye, 
  Volume2, 
  Zap, 
  ArrowRight,
  ArrowLeft,
  Sliders
} from "lucide-react";
import Link from "next/link";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";

export default function ResourcePacksPage() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";
  const [selectedPack, setSelectedPack] = useState<"ultimate" | "legacy">("ultimate");

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#070a10] text-slate-900 dark:text-white pt-24 pb-20 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
      <div className="max-w-6xl mx-auto space-y-12">
        
        {/* Header Hero */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-600 dark:text-cyan-400 text-sm font-semibold backdrop-blur-md"
          >
            <Layers className="w-4 h-4" />
            <span>{isAr ? "حزم الموارد ثلاثية الأبعاد والمؤثرات البصرية" : "Master 3D Parallax & 32x PvP Resource Packs"}</span>
          </motion.div>
          
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 via-slate-700 to-cyan-600 dark:from-white dark:via-slate-200 dark:to-cyan-400 bg-clip-text text-transparent">
            {isAr ? "حزم الموارد الأصلية لمجتمع SIR" : "Official SIR Master Resource Packs"}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-base sm:text-lg">
            {isAr
              ? "استمتع بمجسمات بارالاكس ثلاثية الأبعاد، وحركات الكائنات الحية الواقعية، وحزم 32x السريعة المخصصة لحروب الأسرة والمبارزات."
              : "Experience 3D Parallax Occlusion Mapping (POM), fluid entity animations, and ultra-crisp 32x PvP Faithful textures."}
          </p>
        </div>

        {/* Pack Selector Tabs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Ultimate Pack Card */}
          <div
            onClick={() => setSelectedPack("ultimate")}
            className={`cursor-pointer p-6 rounded-3xl border transition-all duration-300 backdrop-blur-xl ${
              selectedPack === "ultimate"
                ? "bg-white dark:bg-cyan-500/10 border-cyan-500/60 shadow-2xl shadow-cyan-500/10 ring-1 ring-cyan-500"
                : "bg-white/80 dark:bg-[#0d121d]/80 border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase font-bold tracking-wider px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 border border-cyan-500/30">
                ✨ Modern 26.2 (Fabric)
              </span>
              <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 font-bold">76.8 MB</span>
            </div>

            <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-4">SIR Ultimate 3D Master Pack</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
              {isAr
                ? "مجهزة بخرائط بارالاكس ثلاثية الأبعاد كاملة، وحركات الكائنات الذكية من Fresh Animations، وإضاءات متوهجة وتأثيرات أكل ثلاثية الأبعاد."
                : "Engineered with 3D Parallax Occlusion Mapping (POM) normal maps, Fresh Animations mob behavior, emissive ores, and custom 3D eating animations."}
            </p>

            <div className="grid grid-cols-2 gap-3 mt-6">
              <div className="p-3 bg-slate-50 dark:bg-[#070a10] rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
                <span className="text-cyan-600 dark:text-cyan-400 font-bold block">3D POM Normal Maps</span>
                <span className="text-slate-500 text-[10px]">Real depth on blocks</span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-[#070a10] rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
                <span className="text-emerald-600 dark:text-emerald-400 font-bold block">Fresh Animations</span>
                <span className="text-slate-500 text-[10px]">Fluid organic mobs</span>
              </div>
            </div>

            <a
              href="/share/resourcepacks/SIR_Ultimate_Pack.zip"
              download
              onClick={(e) => e.stopPropagation()}
              className="mt-6 w-full py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20"
            >
              <Download className="w-4 h-4" />
              <span>{isAr ? "تحميل الحزمة (76.8 MB)" : "Download SIR Ultimate Pack (.zip)"}</span>
            </a>
          </div>

          {/* Legacy 32x PvP Card */}
          <div
            onClick={() => setSelectedPack("legacy")}
            className={`cursor-pointer p-6 rounded-3xl border transition-all duration-300 backdrop-blur-xl ${
              selectedPack === "legacy"
                ? "bg-white dark:bg-emerald-500/10 border-emerald-500/60 shadow-2xl shadow-emerald-500/10 ring-1 ring-emerald-500"
                : "bg-white/80 dark:bg-[#0d121d]/80 border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-700"
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase font-bold tracking-wider px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30">
                ⚔️ Legacy 1.8.9 (Forge PvP)
              </span>
              <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold">39.9 MB</span>
            </div>

            <h3 className="text-2xl font-black text-slate-900 dark:text-white mt-4">SIR Legacy 32x PvP Faithful</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
              {isAr
                ? "مصممة لمبارزات السيرفرات التنافسية (Hypixel): نار منخفضة الرؤية، سيوف قصيرة، زجاج نقي، وواجهات مستخدم شفافة بدون أي لاغ."
                : "Designed for competitive Bedwars & Duels: low-fire visibility, short combat swords, clear seamless glass, and clean transparent HUD."}
            </p>

            <div className="grid grid-cols-2 gap-3 mt-6">
              <div className="p-3 bg-slate-50 dark:bg-[#070a10] rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
                <span className="text-emerald-600 dark:text-emerald-400 font-bold block">32x High Definition</span>
                <span className="text-slate-500 text-[10px]">Crisp sword outlines</span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-[#070a10] rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
                <span className="text-cyan-600 dark:text-cyan-400 font-bold block">Low Fire & Clear Glass</span>
                <span className="text-slate-500 text-[10px]">Maximum combat FOV</span>
              </div>
            </div>

            <a
              href="/share/resourcepacks/SIR_Legacy_32x.zip"
              download
              onClick={(e) => e.stopPropagation()}
              className="mt-6 w-full py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
            >
              <Download className="w-4 h-4" />
              <span>{isAr ? "تحميل الحزمة (39.9 MB)" : "Download Legacy 32x PvP Pack (.zip)"}</span>
            </a>
          </div>
        </div>

        {/* Feature Grid Breakdown */}
        <div className="p-8 rounded-3xl bg-[#0d121d]/90 border border-slate-800 backdrop-blur-xl space-y-6">
          <div className="border-b border-slate-800/80 pb-4">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <span>{isAr ? "المميزات البصرية والصوتية المدمجة" : "Integrated Visual & Audio Features"}</span>
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-[#070a10] border border-slate-800 space-y-2">
              <Eye className="w-5 h-5 text-cyan-400" />
              <h4 className="text-sm font-bold text-slate-200">3D Parallax Occlusion</h4>
              <p className="text-xs text-slate-400">Deep real-time crevices and brick relief mapping.</p>
            </div>

            <div className="p-4 rounded-2xl bg-[#070a10] border border-slate-800 space-y-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              <h4 className="text-sm font-bold text-slate-200">Fresh Mob Animations</h4>
              <p className="text-xs text-slate-400">Blinking eyes, expressive faces, and natural gait.</p>
            </div>

            <div className="p-4 rounded-2xl bg-[#070a10] border border-slate-800 space-y-2">
              <Volume2 className="w-5 h-5 text-purple-400" />
              <h4 className="text-sm font-bold text-slate-200">Spatial Audio Remaster</h4>
              <p className="text-xs text-slate-400">Dynamic footsteps, acoustic echo, and crisp PvP hits.</p>
            </div>

            <div className="p-4 rounded-2xl bg-[#070a10] border border-slate-800 space-y-2">
              <ShieldCheck className="w-5 h-5 text-amber-400" />
              <h4 className="text-sm font-bold text-slate-200">Zero Crash Conflicts</h4>
              <p className="text-xs text-slate-400">Verified against EMF, ETF, Iris Shaders & Sodium.</p>
            </div>
          </div>
        </div>

        <ConnectedFeaturesHub currentPath="/packs" />

      </div>
    </div>
  );
}
