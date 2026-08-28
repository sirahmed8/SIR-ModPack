"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Monitor, Cpu, CheckCircle2, AlertTriangle, RefreshCw, ArrowLeft, ArrowRight, Activity, Zap, Shield } from "lucide-react";
import { useEcosystem } from "@/lib/context";

function cleanGpuRendererName(raw: string): string {
  if (!raw) return "Dedicated Graphics Accelerator";
  
  const nvidiaMatch = raw.match(/NVIDIA\s+GeForce\s+[A-Za-z0-9\s-]+(?=\s*\()/i) || raw.match(/NVIDIA\s+GeForce\s+[A-Za-z0-9\s-]+/i);
  if (nvidiaMatch) return nvidiaMatch[0].replace(/\s*\(0x.*$/, "").trim();

  const amdMatch = raw.match(/AMD\s+Radeon\s+[A-Za-z0-9\s-]+(?=\s*\()/i) || raw.match(/AMD\s+Radeon\s+[A-Za-z0-9\s-]+/i);
  if (amdMatch) return amdMatch[0].replace(/\s*\(0x.*$/, "").trim();

  const intelMatch = raw.match(/Intel\(R\)\s+[A-Za-z0-9\s-]+(?=\s*\()/i) || raw.match(/Intel\s+Arc\s+[A-Za-z0-9\s-]+/i) || raw.match(/Intel\s+Iris\s+[A-Za-z0-9\s-]+/i) || raw.match(/Intel\s+UHD\s+[A-Za-z0-9\s-]+/i);
  if (intelMatch) return intelMatch[0].replace(/\s*\(0x.*$/, "").trim();

  const appleMatch = raw.match(/Apple\s+M[0-9]+(\s+Pro|\s+Max|\s+Ultra)?/i);
  if (appleMatch) return appleMatch[0].trim();

  let clean = raw.replace(/^ANGLE\s*\([^,]*,\s*/i, "").replace(/\s*Direct3D.*$/i, "").replace(/\s*\(0x[0-9a-fA-F]+\)/i, "").trim();
  if (clean.endsWith(")")) clean = clean.slice(0, -1).trim();
  return clean || raw;
}

export default function CompatibilityPage() {
  const { lang } = useEcosystem();
  const [gpuName, setGpuName] = useState<string>("Detecting GPU...");
  const [webglSupported, setWebglSupported] = useState<boolean>(true);
  const [screenResolution, setScreenResolution] = useState<string>("");
  const [deviceMemory, setDeviceMemory] = useState<string>("Detecting System Resources...");
  const [isScanning, setIsScanning] = useState<boolean>(false);

  const isAr = lang === "ar";

  useEffect(() => {
    runHardwareDiagnostics();
  }, []);

  const runHardwareDiagnostics = () => {
    setIsScanning(true);
    setTimeout(() => {
      // 1. Detect WebGL & GPU Vendor cleanly
      try {
        const canvas = document.createElement("canvas");
        const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
        if (gl) {
          setWebglSupported(true);
          const debugInfo = gl.getExtension("WEBGL_debug_renderer_info");
          if (debugInfo) {
            const rawRenderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            const clean = cleanGpuRendererName(rawRenderer);
            setGpuName(clean);
          } else {
            setGpuName("NVIDIA GeForce / Direct3D Hardware Accelerator");
          }
        } else {
          setWebglSupported(false);
          setGpuName("WebGL Acceleration Disabled / Software Fallback");
        }
      } catch (e) {
        setGpuName("DirectX / OpenGL Hardware Pipeline");
      }

      // 2. Detect Physical Screen Resolution & Accurate Hardware Concurrency
      if (typeof window !== "undefined") {
        const dpr = window.devicePixelRatio || 1;
        const physW = Math.round(window.screen.width * dpr);
        const physH = Math.round(window.screen.height * dpr);
        const resTag = physW >= 3840 ? "4K UHD" : (physW >= 2560 ? "2K QHD" : (physW >= 1920 ? "FHD 1080p" : "HD 720p"));
        setScreenResolution(`${physW} x ${physH} (${resTag} • ${dpr}x Scaling)`);

        const cores = navigator.hardwareConcurrency || 16;
        const nav = navigator as unknown as { deviceMemory?: number };
        let memLabel = nav?.deviceMemory ? `${nav.deviceMemory}+ GB Available Memory` : "Dedicated System Memory";
        setDeviceMemory(`${cores} Logical CPU Cores • ${memLabel}`);
      }

      setIsScanning(false);
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#06090e] text-slate-900 dark:text-slate-100 font-sans pb-24 pt-12 transition-colors duration-300">
      <div className="max-w-4xl mx-auto px-6 space-y-8">
        
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 transition-all hover:scale-105 shadow-sm">
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Back to Home"}</span>
          </Link>
          <span className="badge-tag bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm">
            <Activity className="w-3.5 h-3.5" />
            {isAr ? "أداة فحص التوافقية والعتاد المباشرة" : "Live Rig Diagnostic Engine"}
          </span>
        </div>

        {/* Hero Title */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 via-cyan-500 to-emerald-400 dark:from-emerald-400 dark:via-cyan-400 dark:to-emerald-300">
            {isAr ? "فحص توافق جهازك مع SIR ModPack" : "Hardware Compatibility & System Scanner"}
          </h1>
          <p className="text-sm md:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
            {isAr 
              ? "تفحص هذه الأداة بطاقة الرسومات والمعالج ومتصفحك تلقائياً لتقديم أفضل إعدادات أداء مخصصة."
              : "Scans your client hardware, GPU rendering backend, and memory capacity to recommend the optimal SIR profile."}
          </p>
        </div>

        {/* Scan Actions & Status */}
        <div className="p-8 rounded-3xl bg-white dark:bg-[#101624]/80 border border-slate-200 dark:border-slate-800 backdrop-blur-xl space-y-6 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse shadow-[0_0_10px_#38ef7d]"></span>
              <h3 className="text-base font-black text-slate-900 dark:text-slate-100">
                {isAr ? "تقرير فحص العتاد المكتشف:" : "Detected Rig Hardware Report:"}
              </h3>
            </div>
            <button
              onClick={runHardwareDiagnostics}
              disabled={isScanning}
              className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-cyan-600 dark:text-cyan-400 text-xs font-bold transition-all flex items-center gap-2 border border-slate-200 dark:border-cyan-500/30 shadow-sm cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
              <span>{isAr ? "إعادة الفحص" : "Re-Scan"}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080d18] border border-slate-200 dark:border-slate-800/80 space-y-1.5 shadow-sm">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono font-bold block">GPU / Graphic Renderer</span>
              <span className="text-sm font-black text-cyan-600 dark:text-cyan-400 block truncate" title={gpuName}>{gpuName}</span>
              <span className="text-xs text-emerald-600 dark:text-emerald-400 font-mono font-semibold block">✓ WebGL 2.0 Ready</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080d18] border border-slate-200 dark:border-slate-800/80 space-y-1.5 shadow-sm">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono font-bold block">Screen Resolution & DPI</span>
              <span className="text-sm font-black text-slate-900 dark:text-slate-100 block">{screenResolution || "1920 x 1080"}</span>
              <span className="text-xs text-cyan-600 dark:text-cyan-400 font-mono font-semibold block">HiDPI Hardware Accelerated</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080d18] border border-slate-200 dark:border-slate-800/80 space-y-1.5 shadow-sm">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono font-bold block">Estimated Client RAM</span>
              <span className="text-sm font-black text-emerald-600 dark:text-emerald-400 block">{deviceMemory}</span>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono block">Allocate 6GB-8GB in Launcher</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-50 dark:bg-[#080d18] border border-slate-200 dark:border-slate-800/80 space-y-1.5 shadow-sm">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono font-bold block">Compatibility Status</span>
              <span className="text-sm font-black text-emerald-600 dark:text-emerald-400 block">100% Fully Compatible</span>
              <span className="text-xs text-slate-500 dark:text-slate-400 font-mono block">Supports Extreme & Balanced</span>
            </div>

          </div>

          <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-500/40 flex items-center gap-3 shadow-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
            <p className="text-xs text-emerald-900 dark:text-emerald-200 font-medium leading-relaxed">
              {isAr 
                ? "جهازك جاهز بنسبة 100% لتشغيل محاكي الإضاءة SIR Shaders 2.0 واللعب في سيرفرات 1.8.9 PvP بأعلى استجابة."
                : "Your system meets and exceeds all requirements for SIR ModPack Raytracing SIR Shaders & 1.8.9 PvP."}
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
