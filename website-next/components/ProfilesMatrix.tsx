"use client";

import React, { useState } from "react";
import { useEcosystem } from "@/lib/context";
import { 
  Layers, 
  Sparkles, 
  Swords, 
  Check, 
  Sliders,
  Cpu,
  Monitor,
  Zap,
  ShieldCheck,
  Globe,
  Flame
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function ProfilesMatrix() {
  const { t, dir } = useEcosystem();
  const [activeTab, setActiveTab] = useState<"modern" | "legacy" | "vanilla">("modern");

  return (
    <section id="profiles" className="py-20 lg:py-28 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/30 text-cyan-700 dark:text-[#00e5ff] text-xs font-bold uppercase tracking-wider mb-4 shadow-sm">
            <Layers className="w-3.5 h-3.5" />
            <span>Multi-Engine Architecture</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white mb-4 tracking-tight">
            {t.profiles.title}
          </h2>
          <p className="text-sm sm:text-base text-slate-600 dark:text-gray-300">
            {t.profiles.subtitle}
          </p>
        </div>

        {/* Tab Selector: 3 Tabs (Modern, Legacy, Vanilla+) */}
        <div className="flex justify-center mb-12">
          <div className="p-1.5 rounded-2xl bg-slate-100 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex flex-wrap sm:flex-nowrap items-center gap-2 max-w-xl w-full shadow-inner">
            
            <button
              onClick={() => setActiveTab("modern")}
              className={`relative flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                activeTab === "modern" ? "text-black font-black" : "text-slate-600 dark:text-gray-400 hover:text-white"
              }`}
            >
              {activeTab === "modern" && (
                <motion.div layoutId="profile-tab-bg" className="absolute inset-0 bg-cyan-400 rounded-xl shadow-md" transition={{ type: "spring", stiffness: 350, damping: 25 }} />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                <Sparkles className="w-4 h-4" />
                <span>{t.profiles.tabModern}</span>
              </span>
            </button>

            <button
              onClick={() => setActiveTab("legacy")}
              className={`relative flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                activeTab === "legacy" ? "text-black font-black" : "text-slate-600 dark:text-gray-400 hover:text-white"
              }`}
            >
              {activeTab === "legacy" && (
                <motion.div layoutId="profile-tab-bg" className="absolute inset-0 bg-emerald-400 rounded-xl shadow-md" transition={{ type: "spring", stiffness: 350, damping: 25 }} />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                <Swords className="w-4 h-4" />
                <span>{t.profiles.tabLegacy}</span>
              </span>
            </button>

            <button
              onClick={() => setActiveTab("vanilla")}
              className={`relative flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                activeTab === "vanilla" ? "text-white font-black" : "text-slate-600 dark:text-gray-400 hover:text-white"
              }`}
            >
              {activeTab === "vanilla" && (
                <motion.div layoutId="profile-tab-bg" className="absolute inset-0 bg-purple-500 rounded-xl shadow-md" transition={{ type: "spring", stiffness: 350, damping: 25 }} />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                <Sliders className="w-4 h-4" />
                <span>Vanilla+ (Modular)</span>
              </span>
            </button>

          </div>
        </div>

        {/* Animated Viewport Switcher */}
        <AnimatePresence mode="wait">
          {activeTab === "modern" && (
            <motion.div
              key="modern"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <span className="text-xs text-cyan-600 dark:text-cyan-400 font-mono font-bold tracking-wider uppercase">
                  Fabric Architecture • Iris + Sodium • 3D PBR POM Textures
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* 1. Modern Extreme */}
                <motion.div whileHover={{ y: -5 }} className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-cyan-500 transition-all shadow-xl backdrop-blur-xl">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 text-xs font-black border border-cyan-200 dark:border-cyan-500/30">
                        🌟 Ultra Visuals
                      </span>
                      <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 font-bold">90 - 180+ FPS</span>
                    </div>
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Modern 26.2 Ultra Extreme</h3>
                    <p className="text-xs text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                      Master SIR Shader 2048 Shader Engine with Solas crystal transparent water, circular glowing sun, HD Lunar moon phases, 3D POM relief, and Distant Horizons LOD smearing fix.
                    </p>
                    <div className="space-y-2.5 mb-6">
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>Crystal Transparent Water & Physics Sun</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>3D Parallax Occlusion (POM) Textures</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>Fresh Animations CEM & Swimming Physics</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-gray-400 font-medium">
                    <span>Hardware:</span>
                    <span className="font-bold text-slate-800 dark:text-gray-200">RTX 3060 / RX 6600+</span>
                  </div>
                </motion.div>

                {/* 2. Modern Balanced (Recommended) */}
                <motion.div whileHover={{ y: -5 }} className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-emerald-300 dark:border-emerald-500/40 flex flex-col justify-between hover:border-emerald-500 transition-all shadow-xl backdrop-blur-xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-emerald-500 text-black text-[10px] font-black uppercase px-3 py-1 rounded-bl-xl tracking-wider shadow-sm">
                    ✨ Recommended
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-xs font-black border border-emerald-200 dark:border-emerald-500/30">
                        ⚡ 144+ FPS Balanced
                      </span>
                      <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold">144 - 280+ FPS</span>
                    </div>
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Modern 26.2 Balanced FPS</h3>
                    <p className="text-xs text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                      Optimized SIR Balanced Shader with identical clear water & circular sun, combined with Lithium, FerriteCore, ImmediatelyFast, and C2ME chunk optimization.
                    </p>
                    <div className="space-y-2.5 mb-6">
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>Identical Transparent Water & Sun Physics</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>Lithium + FerriteCore + C2ME Speed Stack</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>InGameAccountSwitcher (IAS) & 1-Click World Host</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-gray-400 font-medium">
                    <span>Hardware:</span>
                    <span className="font-bold text-slate-800 dark:text-gray-200">GTX 1650 / RX 580+</span>
                  </div>
                </motion.div>

                {/* 3. Modern Competitive (Max FPS) */}
                <motion.div whileHover={{ y: -5 }} className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-cyan-500 transition-all shadow-xl backdrop-blur-xl">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 text-xs font-black border border-cyan-200 dark:border-cyan-500/30">
                        🚀 Competitive 240+ FPS
                      </span>
                      <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 font-bold">240 - 600+ FPS</span>
                    </div>
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Modern 26.2 Competitive FPS</h3>
                    <p className="text-xs text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                      Zero-shader ultra performance engine with full Sodium rendering, dynamic memory purges, and minimal frame latency for competitive play and laptops.
                    </p>
                    <div className="space-y-2.5 mb-6">
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>Zero Visual Stutter & Instant Frametimes</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>Dynamic Memory Purge & Eco RAM Footprint</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>Generational ZGC Garbage Collection</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-gray-400 font-medium">
                    <span>Hardware:</span>
                    <span className="font-bold text-slate-800 dark:text-gray-200">Intel UHD / Integrated / Low-End</span>
                  </div>
                </motion.div>

              </div>
            </motion.div>
          )}

          {activeTab === "legacy" && (
            <motion.div
              key="legacy"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="text-center mb-6">
                <span className="text-xs text-emerald-600 dark:text-emerald-400 font-mono font-bold tracking-wider uppercase">
                  Forge Architecture • Hypixel PvP • In-Game Account Switcher (IAS)
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* 1. Legacy 1.8.9 Ultra Cinematic */}
                <motion.div whileHover={{ y: -5 }} className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-emerald-500 transition-all shadow-xl backdrop-blur-xl">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 text-xs font-black border border-cyan-200 dark:border-cyan-500/30">
                        🌟 Ultra Cinematic
                      </span>
                      <span className="text-xs font-mono text-cyan-600 dark:text-cyan-400 font-bold">240+ FPS</span>
                    </div>
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Legacy 1.8.9 Cinematic</h3>
                    <p className="text-xs text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                      Rich OptiFine shader lighting, dynamic skybox, cinematic depth-of-field, 3D animated skins, custom capes, and ultra fluid visuals on 1.8.9.
                    </p>
                    <div className="space-y-2.5 mb-6">
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>OptiFine Shader Engine & Dynamic Shadows</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>SIR Legacy 32x HD Texture Clarity</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                        <span>3D Skin Layers & Custom Cape Support</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-gray-400 font-medium">
                    <span>Hardware:</span>
                    <span className="font-bold text-slate-800 dark:text-gray-200">GTX 1050 / RX 560+</span>
                  </div>
                </motion.div>

                {/* 2. Legacy 1.8.9 Balanced PvP (Recommended) */}
                <motion.div whileHover={{ y: -5 }} className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-emerald-300 dark:border-emerald-500/40 flex flex-col justify-between hover:border-emerald-500 transition-all shadow-xl backdrop-blur-xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 bg-emerald-500 text-black text-[10px] font-black uppercase px-3 py-1 rounded-bl-xl tracking-wider shadow-sm">
                    ✨ Recommended
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 text-xs font-black border border-emerald-200 dark:border-emerald-500/30">
                        ⚡ 500+ FPS Balanced
                      </span>
                      <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold">500+ FPS</span>
                    </div>
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Legacy 1.8.9 Balanced PvP</h3>
                    <p className="text-xs text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                      Balanced competitive suite with 1.7 fluid animations, custom HUD, 32x Faithful texture clarity, low fire, BetterFPS memory caching, and zero micro-stutters.
                    </p>
                    <div className="space-y-2.5 mb-6">
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>1.7 Block-Hitting & Fluid Animations</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>BetterFPS + FoamFix Memory Engine</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>InGameAccountSwitcher (IAS) & Custom HUD</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-gray-400 font-medium">
                    <span>Hardware:</span>
                    <span className="font-bold text-slate-800 dark:text-gray-200">Any PC / 500+ FPS</span>
                  </div>
                </motion.div>

                {/* 3. Legacy 1.8.9 Competitive Battle Suite */}
                <motion.div whileHover={{ y: -5 }} className="rounded-3xl p-7 bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 flex flex-col justify-between hover:border-emerald-500 transition-all shadow-xl backdrop-blur-xl">
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <span className="px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-300 text-xs font-black border border-amber-200 dark:border-amber-500/30">
                        ⚔️ Hypixel Master
                      </span>
                      <span className="text-xs font-mono text-emerald-400 font-bold">1000+ FPS</span>
                    </div>
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Legacy 1.8.9 PvP Battle Suite</h3>
                    <p className="text-xs text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                      Pure Hypixel / Ranked BedWars tournament speed: 0ms RawInput mouse polling, instant keystrokes, short swords, low fire, and sub-millisecond frametimes.
                    </p>
                    <div className="space-y-2.5 mb-6">
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>1000Hz RawInput Mouse Precision & Keystrokes</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>SIR 32x Short Swords & Ultra Low Fire</span>
                      </div>
                      <div className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-gray-200 font-medium">
                        <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                        <span>Zero Delay Sprint, Rod & Hit Registration</span>
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-gray-400 font-medium">
                    <span>Hardware:</span>
                    <span className="font-bold text-slate-800 dark:text-gray-200">Any PC / Max FPS</span>
                  </div>
                </motion.div>

              </div>
            </motion.div>
          )}

          {activeTab === "vanilla" && (
            <motion.div
              key="vanilla"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3 }}
              className="p-8 rounded-3xl bg-white dark:bg-slate-900/80 border border-purple-200 dark:border-purple-500/40 text-center max-w-2xl mx-auto space-y-4 shadow-2xl backdrop-blur-xl"
            >
              <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mx-auto shadow-inner">
                <Sliders className="w-7 h-7" />
              </div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white">Modular Vanilla+ Engine</h3>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-zinc-300 leading-relaxed max-w-xl mx-auto">
                Directly integrates into your official <code className="text-cyan-400 font-mono">%APPDATA%\.minecraft\versions</code>. Choose any official Minecraft release from 1.21.4 down to 1.7.10 with automatic Java 8 / 21 runtime switching, memory auto-allocation, and Sodium performance pre-applied.
              </p>
              <div className="pt-2 flex flex-wrap items-center justify-center gap-2 text-xs font-mono text-purple-300">
                <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-800 border border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800/60">✓ Multi-Version</span>
                <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-800 border border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800/60">✓ Auto Java 8/21</span>
                <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-800 border border-purple-200 dark:bg-purple-950/60 dark:text-purple-300 dark:border-purple-800/60">✓ Vanilla Launcher Compatible</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </section>
  );
}
