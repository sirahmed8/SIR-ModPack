"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  CheckCircle2, 
  Activity, 
  Sparkles, 
  Zap, 
  Layers, 
  ShieldCheck, 
  Globe, 
  ChevronUp, 
  ChevronDown,
  X,
  Server,
  Package
} from "lucide-react";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";

export function EcosystemLiveBar() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";
  const [expanded, setExpanded] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  const items = [
    { icon: <Zap className="w-3.5 h-3.5 text-cyan-400" />, label: isAr ? "المشغل المكتبي" : "SIR Launcher", val: "1.0.0" },
    { icon: <Layers className="w-3.5 h-3.5 text-emerald-400" />, label: isAr ? "المودات النشطة" : "Active Mods", val: "240 Verified" },
    { icon: <Sparkles className="w-3.5 h-3.5 text-amber-400" />, label: isAr ? "شيدرز بليس 2.0" : "SIR Shaders", val: "2 Master Profiles" },
    { icon: <Package className="w-3.5 h-3.5 text-purple-400" />, label: isAr ? "حزم الموارد 3D" : "Resource Packs", val: "3D POM Active" },
    { icon: <Globe className="w-3.5 h-3.5 text-blue-400" />, label: isAr ? "سيرفرات اللعب" : "Multiplayer", val: "100+ Live Nodes" },
    { icon: <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />, label: isAr ? "حالة المنظومة" : "System Status", val: "100% Operational" }
  ];

  return (
    /* Placed horizontally centered at the bottom to NEVER conflict with left sidebar or right chatbot */
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center pointer-events-auto">
      <AnimatePresence>
        {expanded ? (
          /* Expanded Centered Modal/Flyout Card */
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.95 }}
            transition={{ type: "spring", stiffness: 350, damping: 28 }}
            className="w-[92vw] max-w-lg p-4 rounded-3xl bg-[#090d16]/95 border border-cyan-500/30 shadow-[0_20px_60px_rgba(0,0,0,0.8),0_0_30px_rgba(0,229,255,0.15)] backdrop-blur-2xl flex flex-col gap-3"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5 px-1">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#38ef7d]" />
                <span className="text-xs font-black uppercase tracking-wider text-white">
                  {isAr ? "مركز نبض المنظومة الشاملة" : "SIR Universal Ecosystem Heartbeat"}
                </span>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  100% HEALTHY
                </span>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => {
                    soundFx.playClick();
                    setExpanded(false);
                  }}
                  className="p-1.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-all cursor-pointer"
                  title="Minimize"
                >
                  <ChevronDown className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    soundFx.playClick();
                    setDismissed(true);
                  }}
                  className="p-1.5 rounded-xl hover:bg-slate-800 text-slate-400 hover:text-white transition-all cursor-pointer"
                  title="Close"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* 6 Tiles Status Matrix */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-1">
              {items.map((it, idx) => (
                <div 
                  key={idx} 
                  className="p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800/80 hover:border-cyan-500/30 flex items-center gap-2.5 transition-all shadow-inner"
                >
                  <div className="p-1.5 rounded-xl bg-slate-800/80 border border-slate-700/50 shrink-0">
                    {it.icon}
                  </div>
                  <div className="flex flex-col min-w-0">
                    <span className="text-[10px] text-slate-400 font-medium truncate">{it.label}</span>
                    <span className="text-xs text-white font-bold truncate mt-0.5">{it.val}</span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        ) : (
          /* Slim Non-Intrusive Bottom-Center Floating Status Pill */
          <motion.button
            initial={{ opacity: 0, y: 15, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => {
              soundFx.playClick();
              setExpanded(true);
            }}
            className="flex items-center gap-2.5 px-4 py-2 rounded-full bg-[#080d16]/90 hover:bg-[#0c1424] border border-cyan-500/30 hover:border-cyan-400 shadow-[0_8px_30px_rgba(0,0,0,0.5),0_0_20px_rgba(0,229,255,0.12)] backdrop-blur-xl text-xs font-bold text-slate-200 hover:text-cyan-300 transition-all cursor-pointer group"
            title="Click to view live ecosystem health"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_#38ef7d]" />
            <span className="text-[11px] font-bold text-slate-300 group-hover:text-white">
              {isAr ? "حالة المنظومة (100% سليمة)" : "Ecosystem: 100% Healthy"}
            </span>
            <span className="text-[10px] font-mono text-cyan-400 font-black px-1.5 py-0.2 rounded bg-cyan-500/10 border border-cyan-500/20">
              1.0.0
            </span>
            <ChevronUp className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 group-hover:-translate-y-0.5 transition-transform" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
