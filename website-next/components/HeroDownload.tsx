"use client";

import React, { useState, useEffect } from "react";
import { useEcosystem } from "@/lib/context";
import { recordDownloadMetric, signInWithGoogle, subscribeToDownloads } from "@/lib/firebase";
import { 
  Download, 
  Zap, 
  Package, 
  Lock,
  LogIn,
  Copy,
  Check,
  ShieldCheck,
  ChevronDown,
  Sparkles,
  ArrowRight,
  HardDrive,
  Cpu
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";

export function HeroDownload() {
  const { t, dir, user } = useEcosystem();
  const [downloads, setDownloads] = useState<{ installer: number; bundle: number }>({ installer: 120, bundle: 45 });
  const [downloading, setDownloading] = useState<string | null>(null);
  const [copiedHash, setCopiedHash] = useState(false);
  
  useEffect(() => {
    const unsub = subscribeToDownloads((data) => {
      if (data) setDownloads(data);
    });
    return () => unsub();
  }, []);

  const installerUrl = process.env.NEXT_PUBLIC_INSTALLER_DOWNLOAD_URL || "https://github.com/sirahmed8/SIR-ModPack/releases/download/v1.0.0/SIR_Installer.exe";
  const bundleUrl = process.env.NEXT_PUBLIC_BUNDLE_DOWNLOAD_URL || "https://github.com/sirahmed8/SIR-ModPack/releases/download/v1.0.0/SIR_Package_v1.0.0.zip";
  const sha256Checksum = "B7CA7EFBBD5A16E7B79BF67E1388EF09ACC480B0DFAC403473DC4CAA1CFD3761";

  const triggerConfetti = () => {
    try {
      // Create an ephemeral canvas that self-destructs after 3s
      const myCanvas = document.createElement("canvas");
      myCanvas.style.position = "fixed";
      myCanvas.style.inset = "0";
      myCanvas.style.width = "100vw";
      myCanvas.style.height = "100vh";
      myCanvas.style.zIndex = "99999";
      myCanvas.style.pointerEvents = "none";
      document.body.appendChild(myCanvas);

      const myConfetti = confetti.create(myCanvas, {
        resize: true,
        useWorker: false
      });

      myConfetti({
        particleCount: 65,
        spread: 75,
        origin: { y: 0.6 },
        colors: ["#00e5ff", "#38ef7d", "#ffffff", "#a855f7"],
        ticks: 180,
        gravity: 1.2
      });

      setTimeout(() => {
        try {
          myConfetti.reset();
          if (myCanvas.parentNode) {
            myCanvas.parentNode.removeChild(myCanvas);
          }
        } catch {}
      }, 3000);
    } catch (err) {
      console.warn("Confetti execution error:", err);
    }
  };

  const copyChecksum = () => {
    navigator.clipboard.writeText(sha256Checksum);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleDownload = async (type: "installer" | "bundle", url: string) => {
    if (!user) {
      try {
        await signInWithGoogle();
      } catch (err) {
        console.warn("Sign in cancelled:", err);
      }
      return;
    }

    setDownloading(type);
    triggerConfetti();
    try {
      await recordDownloadMetric(type, user?.uid);
    } catch (e) {}

    const link = document.createElement("a");
    link.href = url;
    link.download = type === "installer" ? "SIR_Installer.exe" : "SIR_Package_v1.0.0.zip";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      setDownloading(null);
    }, 2500);
  };

  return (
    <section id="welcome" className="relative py-20 lg:py-28 overflow-hidden">
      <div id="downloads" className="absolute top-0" />
      
      {/* Background Animated Gradient Orbs */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-cyan-500/10 via-emerald-500/10 to-purple-500/10 blur-[130px] rounded-full pointer-events-none -z-10 animate-pulse" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Release Pill */}
        <motion.div 
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-center mb-6"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 shadow-[0_0_20px_rgba(0,229,255,0.15)] backdrop-blur-md">
            <span className="w-2.5 h-2.5 rounded-full bg-[#38ef7d] animate-ping absolute" />
            <span className="w-2.5 h-2.5 rounded-full bg-[#38ef7d]" />
            <span className="text-xs font-black tracking-widest text-cyan-600 dark:text-[#00e5ff] uppercase">
              {t.hero.badge}
            </span>
          </div>
        </motion.div>

        {/* Hero Title & Subtitle */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-center max-w-4xl mx-auto mb-12"
        >
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-slate-900 dark:text-white mb-6 leading-tight">
            {dir === "rtl" ? (
              <>
                منظومة <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-emerald-400">SIR</span> المتكاملة لماينكرافت
              </>
            ) : (
              <>
                The Ultimate <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-emerald-400">SIR Minecraft</span> Ecosystem
              </>
            )}
          </h1>
          <p className="text-base sm:text-xl text-slate-600 dark:text-gray-300 font-normal leading-relaxed max-w-3xl mx-auto">
            {t.hero.subheadline}
          </p>
        </motion.div>

        {/* Unauthenticated Prompt */}
        {!user && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-md mx-auto mb-8 p-3.5 rounded-2xl bg-cyan-50 dark:bg-cyan-950/20 border border-cyan-200 dark:border-cyan-500/30 text-center flex items-center justify-center gap-2 text-xs font-bold text-cyan-800 dark:text-cyan-300 shadow-sm"
          >
            <Lock className="w-4 h-4 text-cyan-600 dark:text-[#00e5ff]" />
            <span>Sign In with Google required to unlock 1-click downloads</span>
          </motion.div>
        )}

        {/* Windows-Only Platform Support Hint */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex justify-center mb-10"
        >
          <div className="inline-flex items-center gap-2.5 px-5 py-2.5 rounded-2xl bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm backdrop-blur-md">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs font-black text-slate-800 dark:text-gray-200">
              🪟 Native Windows (10 / 11, 64-bit) Supported
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-[#00e5ff] font-bold border border-cyan-500/20">
              macOS & Linux Coming Soon
            </span>
          </div>
        </motion.div>

        {/* 2-Column Main Download Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          
          {/* Card 1: ⚡ 1-Click Multi-Core Smart Installer */}
          <motion.div 
            whileHover={{ y: -6, scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="rounded-3xl p-8 bg-white dark:bg-slate-900/80 border border-cyan-500/40 hover:border-cyan-400 shadow-2xl backdrop-blur-xl relative overflow-hidden flex flex-col justify-between"
          >
            <div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                <Zap className="w-6 h-6 text-cyan-500 dark:text-[#00e5ff]" />
                <span>{t.hero.downloadInstallerTitle}</span>
              </h3>
              
              <p className="text-xs sm:text-sm text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                {t.hero.downloadInstallerSub}
              </p>

              <div className="space-y-2.5 mb-8">
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                  <span>🌟 3 Dedicated Native Apps: SIR Launcher, SIR Server Manager & SIR Installer</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                  <span>🎮 Centered Glassmorphic Wizard with Lunar-Level Category Settings</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                  <span>🛡️ Smart auto-healing install (only missing or changed assets are copied)</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                  <span>🍃 Hardware Power Governor (Smooth Mode vs Max Performance Threading)</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-cyan-500 dark:text-[#00e5ff] shrink-0" />
                  <span>🧹 Integrated Deep Storage & Cache Deep Cleaner</span>
                </div>
              </div>
            </div>

            <div>
              <button
                onClick={() => handleDownload("installer", installerUrl)}
                disabled={downloading === "installer"}
                className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-black font-black text-sm shadow-lg hover:shadow-cyan-500/25 transition-all cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Download className={`w-4 h-4 ${downloading === "installer" ? "animate-bounce" : ""}`} />
                <span>{downloading === "installer" ? "Starting SIR ModPack..." : t.hero.downloadInstallerTitle}</span>
              </button>
            </div>
          </motion.div>

          {/* Card 2: 📦 Full Standalone Offline Bundle */}
          <motion.div 
            whileHover={{ y: -6, scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            className="rounded-3xl p-8 bg-white dark:bg-slate-900/80 border border-emerald-500/40 hover:border-emerald-400 shadow-2xl backdrop-blur-xl relative overflow-hidden flex flex-col justify-between"
          >
            <div>
              <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                <Package className="w-6 h-6 text-emerald-500 dark:text-[#38ef7d]" />
                <span>{t.hero.downloadBundleTitle}</span>
              </h3>

              <p className="text-xs sm:text-sm text-slate-600 dark:text-gray-300 mb-6 leading-relaxed">
                {t.hero.downloadBundleSub}
              </p>

              <div className="space-y-2.5 mb-8">
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                  <span>🚀 Pre-extracted SIR payload with centered DPI-aware desktop windows</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                  <span>🎨 Complete 240+ Fabric & Forge Mods + SIR Shader 2048 Shaders + 3D POM Packs</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                  <span>👥 Real Firebase RTDB Social Hub & InGameAccountSwitcher (IAS) Pre-Configured</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-gray-300 font-medium">
                  <Check className="w-4 h-4 text-emerald-500 dark:text-[#38ef7d] shrink-0" />
                  <span>🌐 100% Zero-Internet Dependency for Offline Singleplayer, LAN, & Friends</span>
                </div>
              </div>
            </div>

            <div>
              <button
                onClick={() => handleDownload("bundle", bundleUrl)}
                disabled={downloading === "bundle"}
                className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-black font-black text-sm shadow-lg hover:shadow-emerald-500/25 transition-all cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Download className={`w-4 h-4 ${downloading === "bundle" ? "animate-bounce" : ""}`} />
                <span>{downloading === "bundle" ? "Starting Bundle Download..." : t.hero.downloadBundleTitle}</span>
              </button>
            </div>
          </motion.div>

        </div>

        {/* Checksum & Trust Verification with Helpful Explanation */}
        <div className="mt-12 flex flex-col items-center justify-center gap-2.5 text-center">
          <button
            onClick={copyChecksum}
            className="inline-flex items-center gap-2.5 text-xs font-mono text-slate-500 dark:text-gray-400 hover:text-cyan-500 transition-all cursor-pointer px-4 py-2 rounded-2xl bg-slate-100 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 shadow-sm hover:border-cyan-500/40"
            title="Click to copy full SHA-256 Checksum"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span className="font-bold text-slate-700 dark:text-gray-300">File Security Checksum:</span>
            <span className="text-cyan-600 dark:text-[#00e5ff] font-mono">SHA256: {sha256Checksum.substring(0, 16)}...</span>
            {copiedHash ? (
              <span className="flex items-center gap-1 text-emerald-500 font-sans text-[11px] font-bold">
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                Copied!
              </span>
            ) : (
              <Copy className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400" />
            )}
          </button>
          
          <p className="text-[11px] text-slate-500 dark:text-gray-400 max-w-lg leading-relaxed">
            {dir === "rtl" 
              ? "🔒 البصمة الرقمية المشفرة (SHA-256): تستخدم للتحقق من سلامة الملف المحمّل والتأكد 100% من أنه أصلي وغير معدل وخالٍ تماماً من الفيروسات."
              : "🔒 Cryptographic File Integrity Hash: Click to copy the official SHA-256 checksum to verify that your download is 100% authentic, unmodified, and virus-free."
            }
          </p>
        </div>

      </div>
    </section>
  );
}
