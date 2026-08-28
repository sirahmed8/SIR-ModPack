"use client";

import React, { useRef, useEffect, useState } from "react";
import { 
  SkinViewer, 
  IdleAnimation, 
  WalkingAnimation, 
  RunningAnimation, 
  FlyingAnimation 
} from "skinview3d";
import { Camera, Play, Pause, RefreshCw, UserCheck } from "lucide-react";
import { soundFx } from "@/lib/sound";

interface SkinViewer3DProps {
  skinUrl: string;
  modelType: "classic" | "slim";
  onModelChange: (model: "classic" | "slim") => void;
}

export function SkinViewer3D({ skinUrl, modelType, onModelChange }: SkinViewer3DProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const viewerRef = useRef<SkinViewer | null>(null);
  const [animationMode, setAnimationMode] = useState<"idle" | "walk" | "run" | "fly" | "none">("idle");
  const [autoRotate, setAutoRotate] = useState(true);

  useEffect(() => {
    if (!canvasRef.current) return;

    if (!viewerRef.current) {
      const viewer = new SkinViewer({
        canvas: canvasRef.current,
        width: 260,
        height: 360,
        skin: skinUrl || "https://mc-heads.net/skin/Steve"
      });

      viewer.camera.position.z = 70;
      viewer.camera.position.y = -5;
      viewer.autoRotate = true;
      viewer.autoRotateSpeed = 0.6;
      viewer.animation = new IdleAnimation();

      viewerRef.current = viewer;
    } else {
      viewerRef.current.loadSkin(skinUrl || "https://mc-heads.net/skin/Steve", {
        model: modelType === "slim" ? "slim" : "default"
      } as any);
    }

    return () => {
      // Keep viewer stable across renders
    };
  }, [skinUrl, modelType]);

  const setAnim = (mode: "idle" | "walk" | "run" | "fly" | "none") => {
    soundFx.playTab();
    setAnimationMode(mode);
    if (!viewerRef.current) return;
    const v = viewerRef.current;
    if (mode === "idle") v.animation = new IdleAnimation();
    else if (mode === "walk") v.animation = new WalkingAnimation();
    else if (mode === "run") v.animation = new RunningAnimation();
    else if (mode === "fly") v.animation = new FlyingAnimation();
    else v.animation = null;
  };

  const toggleRotate = () => {
    soundFx.playClick();
    if (!viewerRef.current) return;
    const next = !autoRotate;
    setAutoRotate(next);
    viewerRef.current.autoRotate = next;
  };

  const captureScreenshot = () => {
    soundFx.playSuccess();
    if (!canvasRef.current) return;
    const image = canvasRef.current.toDataURL("image/png");
    const link = document.createElement("a");
    link.download = `minecraft-skin-render.png`;
    link.href = image;
    link.click();
  };

  return (
    <div className="flex flex-col items-center p-4 rounded-3xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 shadow-xl backdrop-blur-xl transition-colors duration-300">
      {/* 3D Canvas */}
      <div className="relative rounded-2xl overflow-hidden bg-gradient-to-b from-slate-100 to-slate-200 dark:from-slate-800/40 dark:to-slate-950 border border-slate-200 dark:border-slate-700/40 p-2 shadow-inner">
        <canvas ref={canvasRef} className="w-[240px] h-[340px] cursor-grab active:cursor-grabbing" />
        
        {/* Screenshot Overlay Button */}
        <button
          onClick={captureScreenshot}
          className="absolute top-3 right-3 p-2 rounded-xl bg-white/90 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400 shadow-sm transition-all hover:scale-105"
          title="Capture High-Res Render"
        >
          <Camera className="w-4 h-4" />
        </button>
      </div>

      {/* Animation & Rotate Controls */}
      <div className="mt-3 flex items-center gap-1.5 flex-wrap justify-center w-full">
        {(["idle", "walk", "run", "fly", "none"] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setAnim(mode)}
            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all ${
              animationMode === mode
                ? "bg-cyan-500 text-slate-950 shadow-sm font-black"
                : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:text-white border border-slate-200 dark:border-slate-700"
            }`}
          >
            {mode}
          </button>
        ))}

        <button
          onClick={toggleRotate}
          className={`p-1.5 rounded-lg text-xs font-bold transition-all ${
            autoRotate 
              ? "bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/40" 
              : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:text-white border border-slate-200 dark:border-slate-700"
          }`}
          title="Toggle Auto Rotation"
        >
          {autoRotate ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Model Arm Switch (Classic 4px vs Slim 3px) */}
      <div className="mt-3 w-full flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800">
        <span className="text-xs font-bold text-slate-600 dark:text-slate-400 flex items-center gap-1.5">
          <UserCheck className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
          <span>Model Arm Width:</span>
        </span>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              soundFx.playClick();
              onModelChange("classic");
            }}
            className={`px-2.5 py-0.5 rounded-lg text-xs font-bold transition-all ${
              modelType === "classic" 
                ? "bg-cyan-500 text-slate-950 shadow-sm" 
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:text-white"
            }`}
          >
            Classic (4px)
          </button>
          <button
            onClick={() => {
              soundFx.playClick();
              onModelChange("slim");
            }}
            className={`px-2.5 py-0.5 rounded-lg text-xs font-bold transition-all ${
              modelType === "slim" 
                ? "bg-cyan-500 text-slate-950 shadow-sm" 
                : "text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:text-white"
            }`}
          >
            Slim (3px)
          </button>
        </div>
      </div>
    </div>
  );
}
