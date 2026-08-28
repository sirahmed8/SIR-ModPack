"use client";

import React, { useState } from "react";
import Link from "next/link";
import { 
  Sparkles, 
  Sliders, 
  Download, 
  Copy, 
  Check, 
  ArrowLeft, 
  ArrowRight, 
  Sun, 
  Droplet, 
  Eye, 
  Zap, 
  Layers,
  HelpCircle,
  X,
  FolderOpen,
  Monitor,
  CheckCircle2
} from "lucide-react";
import { ConnectedFeaturesHub } from "@/components/ConnectedFeaturesHub";
import { useEcosystem } from "@/lib/context";
import { soundFx } from "@/lib/sound";

export default function ShadersConfiguratorPage() {
  const { lang } = useEcosystem();
  const [waveIntensity, setWaveIntensity] = useState<"Low" | "Medium" | "High">("Medium");
  const [sunGlowScale, setSunGlowScale] = useState(1.5);
  const [cloudDensity, setCloudDensity] = useState(1.0);
  const [ssr, setSsr] = useState(true);
  const [sss, setSss] = useState(true);
  const [motionBlur, setMotionBlur] = useState(false);
  const [copied, setCopied] = useState(false);
  const [downloadedTarget, setDownloadedTarget] = useState<string | null>(null);
  const [showHowToModal, setShowHowToModal] = useState(false);
  const [copiedPath, setCopiedPath] = useState(false);

  const isAr = lang === "ar";

  const waveNumericValue = waveIntensity === "Low" ? "0" : waveIntensity === "Medium" ? "1" : "2";

  const generateConfigText = () => {
    return `# SIR ModPack — SIR Shaders 2.0 Optical Profile
# Generated via https://sir-modpack.web.app/shaders
# Compatible with Iris 1.7+, Oculus & OptiFine
MOTION_BLUR=${motionBlur ? "true" : "false"}
SUN_GLOW_SCALE=${sunGlowScale.toFixed(2)}
WAVING_WATER=true
WATER_WAVE_INTENSITY=${waveNumericValue}
SSR=${ssr ? "true" : "false"}
SSS=${sss ? "true" : "false"}
VOLUMETRIC_CLOUDS=true
VOLUMETRIC_CLOUDS_DENSITY=${cloudDensity.toFixed(2)}
SHADOW_RESOLUTION=2048
ATMOSPHERE_RAYLEIGH=1.00
BLOOM_INTENSITY=0.85
`;
  };

  const handleCopy = () => {
    soundFx.playClick();
    navigator.clipboard.writeText(generateConfigText());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (filename: string) => {
    soundFx.playClick();
    const text = generateConfigText();
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    setDownloadedTarget(filename);
    setTimeout(() => setDownloadedTarget(null), 2500);
  };

  const handleCopyShaderPath = () => {
    soundFx.playClick();
    navigator.clipboard.writeText("%appdata%\\.minecraft\\shaderpacks");
    setCopiedPath(true);
    setTimeout(() => setCopiedPath(false), 2000);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-5xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-xs">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={() => { soundFx.playClick(); setShowHowToModal(true); }}
              className="badge-tag bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs px-3.5 py-1.5 rounded-full flex items-center gap-1.5 transition-all shadow-lg shadow-cyan-500/20 cursor-pointer"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>{isAr ? "📖 كيف تطبق الإعدادات في اللعبة؟" : "📖 How to Apply in Game"}</span>
            </button>
          </div>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-emerald-500 to-cyan-400 dark:from-cyan-400 dark:via-emerald-400 dark:to-cyan-300">
            {isAr ? "مختبر ضبط الشيدرز والمحاكاة الضوئية أونلاين" : "SIR Shader Optical Engine Lab"}
          </h1>
          <p className="text-sm md:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "خصص تأثيرات المياه والغيوم وتوهج قرص الشمس وانعكاسات SSR، ثم حمّل ملف الضبط التلقائي وطبقه في ماين كرافت بثوانٍ."
              : "Fine-tune water physics, volumetric clouds, sun disc glow, and SSR reflections, then download the config file and apply it in seconds."}
          </p>
        </div>

        {/* Stage Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Controls Column (Col 1 & 2) */}
          <div className="md:col-span-2 space-y-4">
            
            {/* Water Waves */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-2.5 shadow-sm">
              <label className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <Droplet className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
                <span>{isAr ? "شدة أمواج المياه الفيزيائية" : "Water Wave Intensity"}</span>
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(["Low", "Medium", "High"] as const).map(w => (
                  <button
                    key={w}
                    onClick={() => { soundFx.playClick(); setWaveIntensity(w); }}
                    className={`py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${waveIntensity === w ? 'bg-cyan-500 text-slate-950 font-black shadow-md shadow-cyan-500/20' : 'bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:border-slate-400 dark:hover:border-slate-700'}`}
                  >
                    {w}
                  </button>
                ))}
              </div>
            </div>

            {/* Sun Glow Slider */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-3 shadow-sm">
              <div className="flex justify-between items-center text-xs font-bold">
                <span className="text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Sun className="w-4 h-4 text-amber-500 dark:text-amber-400" />
                  <span>{isAr ? "حجم توهج قرص الشمس (Physics Glow)" : "Sun Glow Disk Radius"}</span>
                </span>
                <span className="font-mono text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-50 dark:bg-cyan-950 px-2 py-0.5 rounded border border-cyan-200 dark:border-cyan-800">{sunGlowScale.toFixed(2)}x</span>
              </div>
              <input 
                type="range" 
                min="1.0" 
                max="3.0" 
                step="0.05" 
                value={sunGlowScale}
                onChange={e => setSunGlowScale(parseFloat(e.target.value))}
                className="w-full h-3 bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700/80 rounded-full appearance-none cursor-pointer accent-cyan-500 dark:accent-cyan-400 shadow-inner"
              />
            </div>

            {/* Cloud Density Slider */}
            <div className="p-5 rounded-2xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-3 shadow-sm">
              <div className="flex justify-between items-center text-xs font-bold">
                <span className="text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
                  <span>{isAr ? "كثافة السحب الحجمية (Volumetric Clouds)" : "Volumetric Cloud Density"}</span>
                </span>
                <span className="font-mono text-emerald-600 dark:text-emerald-400 font-bold bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">{cloudDensity.toFixed(2)}x</span>
              </div>
              <input 
                type="range" 
                min="0.5" 
                max="2.5" 
                step="0.05" 
                value={cloudDensity}
                onChange={e => setCloudDensity(parseFloat(e.target.value))}
                className="w-full h-3 bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700/80 rounded-full appearance-none cursor-pointer accent-emerald-500 dark:accent-emerald-400 shadow-inner"
              />
            </div>

            {/* Toggles */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div 
                onClick={() => { soundFx.playClick(); setSsr(!ssr); }}
                className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center justify-between shadow-sm ${ssr ? 'border-cyan-400 bg-cyan-50 dark:bg-cyan-950/30 text-cyan-800 dark:text-cyan-200 ring-1 ring-cyan-400/40' : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070a10] text-slate-600 dark:text-slate-400'}`}
              >
                <span className="text-xs font-bold">{isAr ? "انعكاسات SSR" : "SSR Reflections"}</span>
                <div className={`w-4 h-4 rounded flex items-center justify-center ${ssr ? 'bg-cyan-400 text-slate-950 font-black' : 'border border-slate-300 dark:border-slate-700'}`}>
                  {ssr && <Check className="w-3 h-3" />}
                </div>
              </div>

              <div 
                onClick={() => { soundFx.playClick(); setSss(!sss); }}
                className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center justify-between shadow-sm ${sss ? 'border-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-800 dark:text-emerald-200 ring-1 ring-emerald-400/40' : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070a10] text-slate-600 dark:text-slate-400'}`}
              >
                <span className="text-xs font-bold">{isAr ? "إضاءة SSS" : "SSS Scattering"}</span>
                <div className={`w-4 h-4 rounded flex items-center justify-center ${sss ? 'bg-emerald-400 text-slate-950 font-black' : 'border border-slate-300 dark:border-slate-700'}`}>
                  {sss && <Check className="w-3 h-3" />}
                </div>
              </div>

              <div 
                onClick={() => { soundFx.playClick(); setMotionBlur(!motionBlur); }}
                className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center justify-between shadow-sm ${motionBlur ? 'border-amber-400 bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 ring-1 ring-amber-400/40' : 'border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#070a10] text-slate-600 dark:text-slate-400'}`}
              >
                <span className="text-xs font-bold">{isAr ? "ضبابية الحركة" : "Motion Blur"}</span>
                <div className={`w-4 h-4 rounded flex items-center justify-center ${motionBlur ? 'bg-amber-400 text-slate-950 font-black' : 'border border-slate-300 dark:border-slate-700'}`}>
                  {motionBlur && <Check className="w-3 h-3" />}
                </div>
              </div>
            </div>

          </div>

          {/* Export Output Card (Col 3) */}
          <div className="md:col-span-1 p-6 rounded-3xl bg-white dark:bg-gradient-to-b dark:from-[#101624] dark:to-[#070a10] border border-slate-200 dark:border-cyan-500/40 space-y-4 shadow-2xl h-fit">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
                <span>{isAr ? "كود الضبط المولد" : "Generated Config"}</span>
              </h3>
              <span className="text-[10px] font-mono text-cyan-700 dark:text-cyan-400 bg-cyan-100 dark:bg-cyan-950 px-2 py-0.5 rounded border border-cyan-300 dark:border-cyan-800">
                Iris Ready
              </span>
            </div>

            <pre className="p-3.5 rounded-xl bg-slate-900 text-[10px] font-mono text-cyan-300 overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-48 select-all">
              {generateConfigText()}
            </pre>

            <div className="space-y-2 pt-2">
              <button
                onClick={() => handleDownload("SIR_Extreme_Shader.zip.txt")}
                className="w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 cursor-pointer"
              >
                {downloadedTarget === "SIR_Extreme_Shader.zip.txt" ? <Check className="w-4 h-4" /> : <Download className="w-4 h-4" />}
                <span>{downloadedTarget === "SIR_Extreme_Shader.zip.txt" ? (isAr ? "تم التحميل!" : "Downloaded!") : (isAr ? "تحميل لـ SIR Extreme Shader" : "Download for SIR Extreme")}</span>
              </button>

              <button
                onClick={() => handleDownload("SIR_Balanced_Shader.zip.txt")}
                className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 cursor-pointer"
              >
                {downloadedTarget === "SIR_Balanced_Shader.zip.txt" ? <Check className="w-4 h-4" /> : <Download className="w-4 h-4" />}
                <span>{downloadedTarget === "SIR_Balanced_Shader.zip.txt" ? (isAr ? "تم التحميل!" : "Downloaded!") : (isAr ? "تحميل لـ SIR Balanced Shader" : "Download for SIR Balanced")}</span>
              </button>

              <button
                onClick={handleCopy}
                className="w-full py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-cyan-400 font-bold text-xs transition-all flex items-center justify-center gap-2 border border-slate-300 dark:border-cyan-500/30 cursor-pointer"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? (isAr ? "تم النسخ للحافظة!" : "Copied to Clipboard!") : (isAr ? "نسخ الكود" : "Copy Raw Code")}</span>
              </button>
            </div>
          </div>

        </div>

        <ConnectedFeaturesHub currentPath="/shaders" />

      </div>

      {/* HOW TO APPLY MODAL */}
      {showHowToModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-lg p-6 rounded-3xl bg-gradient-to-b from-[#121826] to-[#0a0e17] border border-cyan-500/50 shadow-2xl space-y-5 animate-pop">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
                  <Monitor className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">
                    {isAr ? "كيفية تطبيق إعدادات الشيدر في اللعبة" : "How to Apply Custom Shader Settings"}
                  </h3>
                  <p className="text-[11px] text-slate-400 font-mono">
                    Iris / Sodium / Oculus / OptiFine
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setShowHowToModal(false)}
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 transition-all cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Steps List */}
            <div className="space-y-3 text-xs leading-relaxed">
              
              <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center gap-2 text-cyan-400 font-bold">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{isAr ? "الخطوة 1: حمّل ملف الإعدادات" : "Step 1: Download Configuration"}</span>
                </div>
                <p className="text-slate-300 pl-6">
                  {isAr 
                    ? "اضغط على زر (تحميل لـ SIR Extreme) أو (تحميل لـ SIR Balanced) لحفظ ملف .txt المخصص."
                    : "Click 'Download for SIR Extreme' or 'Download for SIR Balanced' to get your tailored .txt file."}
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center gap-2 text-emerald-400 font-bold">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{isAr ? "الخطوة 2: افتح مجلد الشيدرز في ماين كرافت" : "Step 2: Open Shader Packs Folder"}</span>
                </div>
                <p className="text-slate-300 pl-6">
                  {isAr 
                    ? "داخل ماين كرافت، اذهب إلى: Options -> Video Settings -> Shader Packs -> واضغط 'Open Shader Pack Folder'."
                    : "In Minecraft, navigate to: Options -> Video Settings -> Shader Packs -> click 'Open Shader Pack Folder'."}
                </p>
                <div className="pl-6 pt-1 flex items-center gap-2">
                  <span className="font-mono text-[10px] bg-[#070a10] px-2 py-1 rounded text-slate-400 border border-slate-800 truncate flex-1">
                    %appdata%\.minecraft\shaderpacks
                  </span>
                  <button 
                    onClick={handleCopyShaderPath}
                    className="p-1.5 rounded bg-slate-800 text-cyan-400 hover:bg-slate-700 text-[10px] font-bold shrink-0 cursor-pointer flex items-center gap-1"
                  >
                    {copiedPath ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedPath ? "Copied" : "Copy Path"}</span>
                  </button>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center gap-2 text-amber-400 font-bold">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{isAr ? "الخطوة 3: ضع الملف بجوار ملف الشيدر المضغوط" : "Step 3: Place .txt Next to Shader ZIP"}</span>
                </div>
                <p className="text-slate-300 pl-6">
                  {isAr 
                    ? "ضع ملف SIR_Extreme_Shader.zip.txt داخل مجلد shaderpacks بجانب SIR_Extreme_Shader.zip."
                    : "Place SIR_Extreme_Shader.zip.txt inside the shaderpacks folder right next to SIR_Extreme_Shader.zip."}
                </p>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center gap-2 text-cyan-300 font-bold">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{isAr ? "الخطوة 4: اضغط Apply في اللعبة" : "Step 4: Click Apply & Enjoy!"}</span>
                </div>
                <p className="text-slate-300 pl-6">
                  {isAr 
                    ? "اختر الشيدر في اللعبة واضغط Apply، وستتحدث الإضاءة وأمواج المياه والسحب فورياً!"
                    : "Select the shader in-game and click Apply. Your custom lighting and water physics will load instantly!"}
                </p>
              </div>

            </div>

            {/* Close Modal Button */}
            <button
              onClick={() => setShowHowToModal(false)}
              className="w-full py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all shadow-lg shadow-cyan-500/20 cursor-pointer"
            >
              {isAr ? "فهمت، جاهز للتطبيق!" : "Got it, Ready to Play!"}
            </button>

          </div>
        </div>
      )}

    </div>
  );
}
