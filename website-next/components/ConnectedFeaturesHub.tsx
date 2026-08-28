"use client";

import React from "react";
import Link from "next/link";
import { 
  Sparkles, 
  Package, 
  SlidersHorizontal, 
  Shirt, 
  Box, 
  Swords, 
  Server, 
  ArrowRight,
  Zap
} from "lucide-react";
import { useEcosystem } from "@/lib/context";

interface FeaturePill {
  href: string;
  titleEn: string;
  titleAr: string;
  descEn: string;
  descAr: string;
  icon: React.ElementType;
  color: string;
  badge: string;
}

const FEATURE_LINKS: FeaturePill[] = [
  {
    href: "/profiles",
    titleEn: "Profiles Matrix",
    titleAr: "مصفوفة البروفايلات",
    descEn: "8 calibrated performance tiers for Modern & Legacy",
    descAr: "8 مستويات أداء مجهزة للحديث والكلاسيكي",
    icon: SlidersHorizontal,
    color: "from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-400",
    badge: "8 Tiers"
  },
  {
    href: "/shaders",
    titleEn: "SIR Shaders 2.0",
    titleAr: "مختبر الشيدرز الضوئي",
    descEn: "Crystal caustics, sun disk & 3D POM relief",
    descAr: "انكسارات مائية وقرص شمس واقعي وبروز ثلاثي الأبعاد",
    icon: Sparkles,
    color: "from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400",
    badge: "Extreme"
  },
  {
    href: "/packs",
    titleEn: "3D Resource Packs",
    titleAr: "حزم الموارد 3D",
    descEn: "1,261 POM maps & 258 living mob models",
    descAr: "1,261 خريطة بروز و 258 أنيميشن واقعي",
    icon: Package,
    color: "from-purple-500/20 to-pink-500/10 border-purple-500/30 text-purple-400",
    badge: "POM & CEM"
  },
  {
    href: "/skins",
    titleEn: "3D Skin Studio",
    titleAr: "استوديو السكنات 3D",
    descEn: "Interactive WebGL skin renderer & pose studio",
    descAr: "عارض سكنات WebGL تفاعلي ومحرك وضعيات",
    icon: Shirt,
    color: "from-blue-500/20 to-cyan-500/10 border-blue-500/30 text-blue-400",
    badge: "WebGL"
  },
  {
    href: "/benchmarks",
    titleEn: "FPS Rig Benchmark",
    titleAr: "حاسبة توقع الإطارات",
    descEn: "Calculate calibrated FPS across 100+ GPUs & CPUs",
    descAr: "حساب الإطارات المتوقعة لكافة كروت الشاشة والمعالجات",
    icon: Zap,
    color: "from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400",
    badge: "Hardware"
  },
  {
    href: "/trainer",
    titleEn: "PvP & Aim Trainer",
    titleAr: "مدرب البفب والتصويب",
    descEn: "Train CPS, tracking, and rod combos",
    descAr: "تدريب على الكليكات وسرعة التصويب والكومبو",
    icon: Swords,
    color: "from-red-500/20 to-rose-500/10 border-red-500/30 text-red-400",
    badge: "PvP"
  }
];

export function ConnectedFeaturesHub({ currentPath }: { currentPath?: string }) {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";

  const visibleLinks = FEATURE_LINKS.filter(item => item.href !== currentPath);

  return (
    <div className="mt-16 pt-12 border-t border-slate-800/80 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-bold border border-cyan-500/20 mb-1.5">
            <Zap className="w-3.5 h-3.5" />
            <span>{isAr ? "منظومة مترابطة بالكامل" : "Fully Interconnected Ecosystem"}</span>
          </div>
          <h3 className="text-xl font-black text-white">
            {isAr ? "استكشف ميزات واستوديوهات المنظومة" : "Explore Connected Ecosystem Features"}
          </h3>
        </div>
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-cyan-400 transition-colors"
        >
          <span>{isAr ? "العودة للمركز الرئيسي" : "Back to Main Hub"}</span>
          <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {visibleLinks.slice(0, 3).map((item, idx) => {
          const Icon = item.icon;
          return (
            <Link
              key={idx}
              href={item.href}
              className={`p-5 rounded-3xl bg-gradient-to-br ${item.color} border hover:scale-[1.02] transition-all flex flex-col justify-between group shadow-lg`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="p-2.5 rounded-2xl bg-slate-900/80 border border-slate-800/80">
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-900/80 text-slate-300 border border-slate-700/50">
                    {item.badge}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                  {isAr ? item.titleAr : item.titleEn}
                </h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                  {isAr ? item.descAr : item.descEn}
                </p>
              </div>

              <div className="flex items-center gap-1 text-xs font-bold text-cyan-400 mt-4 pt-3 border-t border-slate-800/40 group-hover:translate-x-1 rtl:group-hover:-translate-x-1 transition-transform">
                <span>{isAr ? "فتح الأداة" : "Launch Suite"}</span>
                <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
