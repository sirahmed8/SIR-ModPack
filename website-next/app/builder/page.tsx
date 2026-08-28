"use client";

import { AuthGate } from "@/components/AuthGate";
import React, { useState } from "react";
import Link from "next/link";
import { Package, Download, Check, Sparkles, Sliders, ArrowLeft, ArrowRight, Layers, Cpu, Shield, FileCode } from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";

const MOD_OPTIONS = [
  { id: "sodium", name: "Sodium / Embeddium", category: "Performance", ramMb: 120, desc: "400% FPS boost modern rendering engine", descAr: "محرك الريندر الحديث لزيادة الإطارات حتى 400%" },
  { id: "iris", name: "Iris Shaders Pipeline", category: "Visuals", ramMb: 250, desc: "Modern shader engine with SIR Shaders 2.0 & POM", descAr: "محرك الشيدرز لتشغيل شيدر SIR وانعكاسات الماء" },
  { id: "lithium", name: "Lithium Physics Optimizer", category: "Performance", ramMb: 80, desc: "Optimizes mob AI, chunk loading & physics", descAr: "تحسين فيزياء اللعبة وحركة الوحوش" },
  { id: "ferritecore", name: "FerriteCore Memory Saver", category: "Performance", ramMb: -200, desc: "Reduces total RAM usage by up to 50%", descAr: "تقليل استهلاك الرامات للنصف" },
  { id: "emf", name: "Entity Model Features (EMF)", category: "Visuals", ramMb: 150, desc: "Custom entity models & Fresh Animations", descAr: "حركات وانيميشن الوحوش الواقعية" },
  { id: "ias", name: "InGameAccountSwitcher (IAS)", category: "Utility", ramMb: 40, desc: "Switch offline/Microsoft accounts in title screen", descAr: "تبديل الحسابات من داخل اللعبة" },
  { id: "sound_physics", name: "Sound Physics Remastered", category: "Audio", ramMb: 60, desc: "Cave reverbs, realistic sound dampening", descAr: "صدى الكهوف والصوتيات الواقعية" }
];

export default function BuilderPage() {
  const { lang } = useEcosystem();
  const [version, setVersion] = useState("26.2");
  const [tier, setTier] = useState("Balanced");
  const [selectedMods, setSelectedMods] = useState<string[]>(["sodium", "iris", "lithium", "ferritecore", "emf", "ias"]);
  const [downloaded, setDownloaded] = useState(false);

  const isAr = lang === "ar";

  const toggleMod = (id: string) => {
    soundFx.playClick();
    setSelectedMods(prev => 
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const calculatedRam = Math.max(2, Math.round(selectedMods.reduce((acc, mId) => {
    const mod = MOD_OPTIONS.find(m => m.id === mId);
    return acc + (mod ? mod.ramMb : 0);
  }, 3500) / 1024 * 10) / 10);

  const handleDownloadProfile = () => {
    soundFx.playClick();
    const profile = {
      name: `SIR Custom Profile (${version})`,
      version: version,
      tier: tier,
      recommended_ram_gb: Math.ceil(calculatedRam),
      mods: selectedMods,
      created_at: new Date().toISOString(),
      creator: "SIR ModPack Web Studio"
    };

    const blob = new Blob([JSON.stringify(profile, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sir_profile_${version.replace(".", "_")}.json`;
    a.click();
    setDownloaded(true);
    setTimeout(() => setDownloaded(false), 3000);
  };

  const getCategoryBadgeClass = (category: string, isChecked: boolean) => {
    if (!isChecked) {
      return "bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-400 border border-slate-300 dark:border-slate-700";
    }
    switch (category) {
      case "Performance":
        return "bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800";
      case "Visuals":
        return "bg-cyan-100 dark:bg-cyan-950/80 text-cyan-800 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-800";
      case "Utility":
        return "bg-purple-100 dark:bg-purple-950/80 text-purple-800 dark:text-purple-300 border border-purple-300 dark:border-purple-800";
      case "Audio":
        return "bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800";
      default:
        return "bg-cyan-100 dark:bg-cyan-950/80 text-cyan-800 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-800";
    }
  };

  return (
    <AuthGate featureName="Modpack Builder Studio" featureNameAr="استوديو بناء وتخصيص التجميعات">
      <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-sm">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-cyan-100 dark:bg-cyan-950 text-cyan-800 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <Sliders className="w-3.5 h-3.5" />
            {isAr ? "أداة تخصيص وتجميع حزمة المودات" : "Custom Modpack Profile Studio"}
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "أداة بناء الحزم والتعديلات المخصصة أونلاين" : "Custom Modpack Profile Builder"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "اختر إصدار ماين كرافت، والمودات المطلوبة، وحمّل ملف التهيئة (JSON) لاستيراده مباشرة إلى لانشر SIR."
              : "Customize your Minecraft edition, toggle specific performance/visual mods, and export a ready-to-launch profile.json."}
          </p>
        </div>

        {/* Builder Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Controls Form (Col 1 & 2) */}
          <div className="md:col-span-2 space-y-6">
            
            {/* Version Picker */}
            <div className="p-6 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-3 shadow-xl">
              <h3 className="text-sm font-black text-slate-900 dark:text-slate-200">1. {isAr ? "اختر إصدار اللعبة" : "Select Minecraft Edition"}</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { id: "26.2", label: "Modern 26.2 (Fabric)", tag: "✨ Master Raytracing" },
                  { id: "1.20.1", label: "1.20.1 Fabric", tag: "⚡ Stable Longplay" },
                  { id: "1.8.9", label: "Legacy 1.8.9 PvP", tag: "⚔️ Hypixel Combat" }
                ].map(v => (
                  <button
                    key={v.id}
                    onClick={() => { soundFx.playClick(); setVersion(v.id); }}
                    className={`p-3.5 rounded-2xl border text-left transition-all shadow-sm cursor-pointer ${
                      version === v.id 
                        ? 'border-cyan-500 dark:border-cyan-400 bg-cyan-50 dark:bg-cyan-950/40 ring-1 ring-cyan-500/40 shadow-md' 
                        : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070a10] hover:bg-white dark:hover:bg-slate-900'
                    }`}
                  >
                    <span className="text-xs font-black text-slate-900 dark:text-slate-100 block">{v.label}</span>
                    <span className="text-[10px] text-cyan-600 dark:text-cyan-400 block mt-0.5 font-bold">{v.tag}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Mods Checklist */}
            <div className="p-6 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-3 shadow-xl">
              <h3 className="text-sm font-black text-slate-900 dark:text-slate-200">2. {isAr ? "تخصيص المودات المضمنة" : "Customize Included Mods"}</h3>
              <div className="space-y-2.5">
                {MOD_OPTIONS.map(mod => {
                  const isChecked = selectedMods.includes(mod.id);
                  return (
                    <div
                      key={mod.id}
                      onClick={() => toggleMod(mod.id)}
                      className={`p-4 rounded-2xl border cursor-pointer flex items-center justify-between transition-all shadow-sm ${
                        isChecked 
                          ? 'border-emerald-500 dark:border-emerald-500/50 bg-emerald-50/80 dark:bg-[#080e1a] ring-1 ring-emerald-500/30' 
                          : 'border-slate-200 dark:border-slate-800/80 bg-slate-50/70 dark:bg-[#070a10] hover:border-slate-300 dark:hover:border-slate-700 hover:bg-white dark:hover:bg-[#0d121d] opacity-75'
                      }`}
                    >
                      <div className="pr-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className={`text-xs ${isChecked ? 'font-black text-slate-900 dark:text-slate-100' : 'font-bold text-slate-600 dark:text-slate-400'}`}>
                            {mod.name}
                          </h4>
                          <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-md ${getCategoryBadgeClass(mod.category, isChecked)}`}>
                            {mod.category}
                          </span>
                        </div>
                        <p className={`text-xs mt-1 font-mono ${isChecked ? 'text-slate-600 dark:text-slate-400 font-medium' : 'text-slate-500 dark:text-slate-500'}`}>
                          {isAr ? mod.descAr : mod.desc}
                        </p>
                      </div>
                      <div className={`w-5 h-5 rounded-lg flex items-center justify-center border shrink-0 transition-all ${isChecked ? 'bg-emerald-500 border-emerald-400 text-slate-950 shadow-sm' : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900'}`}>
                        {isChecked && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

          </div>

          {/* Live Summary Card (Col 3) */}
          <div className="md:col-span-1 p-6 rounded-3xl bg-white dark:bg-gradient-to-b dark:from-[#101624] dark:to-[#070a10] border border-slate-200 dark:border-cyan-500/40 space-y-6 shadow-xl h-fit">
            <h3 className="text-sm font-black text-slate-900 dark:text-slate-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
              <span>{isAr ? "ملخص الحزمة المخصصة" : "Profile Summary"}</span>
            </h3>

            <div className="space-y-3 text-xs font-mono">
              <div className="flex justify-between py-2 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400 font-bold">{isAr ? "الإصدار:" : "Version:"}</span>
                <span className="text-cyan-700 dark:text-cyan-400 font-black">{version}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400 font-bold">{isAr ? "المودات المحددة:" : "Active Mods:"}</span>
                <span className="text-emerald-700 dark:text-emerald-400 font-black">{selectedMods.length} Mods</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-200 dark:border-slate-800">
                <span className="text-slate-500 dark:text-slate-400 font-bold">{isAr ? "الرام المقترح:" : "Target RAM:"}</span>
                <span className="text-amber-700 dark:text-amber-400 font-black">{calculatedRam} GB Dedicated</span>
              </div>
            </div>

            <button
              onClick={handleDownloadProfile}
              className="w-full py-3 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
            >
              {downloaded ? <Check className="w-4 h-4 stroke-[3]" /> : <Download className="w-4 h-4" />}
              <span>{downloaded ? (isAr ? "تم التحميل بنجاح!" : "Profile Exported!") : (isAr ? "تحميل ملف التهيئة (JSON)" : "Export Profile.json")}</span>
            </button>
          </div>

        </div>

        {/* Interconnected Ecosystem Launchpad */}
        <ConnectedFeaturesHub currentPath="/builder" />

      </div>
    </div>
    </AuthGate>);
}