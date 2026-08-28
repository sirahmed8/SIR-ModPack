"use client";

import React from "react";
import { useEcosystem } from "@/lib/context";
import { 
  Zap, 
  Crosshair, 
  ShieldAlert, 
  BarChart3, 
  Sparkles, 
  ExternalLink,
  Flame
} from "lucide-react";
import { motion } from "framer-motion";

export function HavocPortal() {
  const { t, dir } = useEcosystem();

  return (
    <section id="havoc" className="py-20 lg:py-28 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Spotlight Container */}
        <motion.div 
          whileHover={{ scale: 1.005 }}
          transition={{ duration: 0.3 }}
          className="relative rounded-3xl overflow-hidden bg-white dark:bg-[#120d24] p-8 sm:p-12 lg:p-16 border border-purple-200 dark:border-purple-900/60 shadow-2xl backdrop-blur-xl"
        >
          <div className="relative z-10 max-w-4xl mx-auto">
            
            {/* Badges */}
            <div className="flex flex-wrap items-center gap-3 mb-6">
              <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-purple-50 dark:bg-purple-950/40 border border-purple-200 dark:border-purple-800/60 text-purple-800 dark:text-purple-300 text-xs font-black uppercase tracking-widest shadow-sm">
                <Flame className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
                {t.havoc?.badge || "Project Spotlight"}
              </span>
              <span className="px-3.5 py-1.5 text-xs font-black uppercase rounded-full bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800/60 shadow-sm">
                {t.havoc?.soonBadge || "Coming Soon"}
              </span>
            </div>

            {/* Headline */}
            <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white mb-6 tracking-tight">
              {t.havoc?.title || "HAVOC PvP Enhancement Engine"}
            </h2>
            <p className="text-base sm:text-lg text-slate-600 dark:text-gray-300 mb-10 leading-relaxed max-w-3xl font-medium">
              {t.havoc?.subtitle || "Next-generation combat injector engineered for competitive Minecraft PvP dominance."}
            </p>

            {/* Feature Bullets with Hover Lift */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">
              {[
                { icon: Zap, text: t.havoc?.feature1 || "Micro-Latency Hit-Registration Optimization" },
                { icon: Crosshair, text: t.havoc?.feature2 || "Adaptive Reach & Velocity Physics Stabilizer" },
                { icon: ShieldAlert, text: t.havoc?.feature3 || "Undetected Lightweight Injection Framework" },
                { icon: BarChart3, text: t.havoc?.feature4 || "Live Real-Time Telemetry & Combat HUD" }
              ].map((feat, idx) => (
                <motion.div 
                  key={idx}
                  whileHover={{ y: -3, scale: 1.01 }}
                  className="p-4 rounded-2xl bg-slate-50 dark:bg-[#1a1433] border border-purple-100 dark:border-purple-900/40 flex items-center gap-3 shadow-sm"
                >
                  <div className="p-2.5 rounded-xl bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300">
                    <feat.icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs sm:text-sm font-black text-slate-900 dark:text-white">
                    {feat.text}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Footer / CTA in card */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-slate-200 dark:border-purple-900/40">
              <span className="text-xs text-purple-700 dark:text-purple-300 font-mono font-medium">
                {t.havoc?.authorNote || "Architected & Developed by Sir Ahmed's Brother"}
              </span>

              <button
                disabled
                className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-purple-600 dark:bg-purple-700 text-white font-bold text-xs cursor-not-allowed flex items-center justify-center gap-2 shadow-md opacity-90"
              >
                <span>{t.havoc?.actionBtn || "Request Early Access (Soon)"}</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>

          </div>
        </motion.div>

      </div>
    </section>
  );
}
