"use client";

import React, { useEffect, useRef, useState } from "react";
import { RotateCw, Play, Pause, Shield } from "lucide-react";

interface Skin3DViewerProps {
  skinUrl: string;
  capeUrl?: string;
  width?: number;
  height?: number;
  enableAnimation?: boolean;
  enableElytra?: boolean;
  className?: string;
}

export function Skin3DViewer({
  skinUrl,
  capeUrl,
  width = 260,
  height = 340,
  enableAnimation = true,
  enableElytra = false,
  className = ""
}: Skin3DViewerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const viewerRef = useRef<any>(null);
  const [isRotating, setIsRotating] = useState(true);
  const [isAnimating, setIsAnimating] = useState(true);
  const [hasElytra, setHasElytra] = useState(enableElytra);

  useEffect(() => {
    let viewer: any = null;
    let anim: any = null;

    async function initViewer() {
      if (!canvasRef.current) return;
      try {
        const skinview3d = await import("skinview3d");
        
        if (viewerRef.current) {
          viewerRef.current.dispose();
          viewerRef.current = null;
        }

        viewer = new skinview3d.SkinViewer({
          canvas: canvasRef.current,
          width: width,
          height: height,
          skin: skinUrl || "/skins/steve.png",
        });

        viewer.camera.position.set(0, 0, 65);
        // If cape is present, rotate player to showcase the 3D cape immediately!
        if (capeUrl) {
          viewer.playerObject.rotation.y = Math.PI * 0.95;
        }
        viewer.autoRotate = isRotating;
        viewer.autoRotateSpeed = 1.2;

        if (capeUrl) {
          try {
            await viewer.loadCape(capeUrl, {
              backEquipment: hasElytra ? "elytra" : "cape"
            });
          } catch (err) {
            console.warn("Could not load cape in 3D viewer:", err);
          }
        }

        if (enableAnimation && isAnimating) {
          anim = viewer.animations.add(skinview3d.WalkingAnimation);
          anim.speed = 0.8;
        }

        viewerRef.current = viewer;
      } catch (e) {
        console.warn("Skin3DViewer initialization fallback:", e);
      }
    }

    initViewer();

    return () => {
      if (viewerRef.current) {
        viewerRef.current.dispose();
        viewerRef.current = null;
      }
    };
  }, [skinUrl, capeUrl, width, height, hasElytra]);

  const toggleAnimation = () => {
    if (!viewerRef.current) return;
    if (isAnimating) {
      viewerRef.current.animations.paused = true;
      setIsAnimating(false);
    } else {
      viewerRef.current.animations.paused = false;
      setIsAnimating(true);
    }
  };

  const toggleRotation = () => {
    if (!viewerRef.current) return;
    const next = !isRotating;
    viewerRef.current.autoRotate = next;
    setIsRotating(next);
  };

  const toggleElytra = () => {
    const next = !hasElytra;
    setHasElytra(next);
    if (viewerRef.current && capeUrl) {
      viewerRef.current.loadCape(capeUrl, {
        backEquipment: next ? "elytra" : "cape"
      });
    }
  };

  return (
    <div className={`relative flex flex-col items-center justify-center ${className}`}>
      <canvas 
        ref={canvasRef} 
        className="rounded-2xl cursor-grab active:cursor-grabbing drop-shadow-[0_15px_30px_rgba(0,0,0,0.5)] transition-all"
      />

      <div className="absolute bottom-2 inset-x-2 flex items-center justify-center gap-1.5 p-1.5 rounded-xl bg-white/90 dark:bg-slate-900/85 backdrop-blur-md border border-slate-200 dark:border-slate-700/60 shadow-lg text-[10px] font-bold text-slate-700 dark:text-slate-300">
        <button
          type="button"
          onClick={toggleRotation}
          className={`p-1.5 rounded-lg transition-all flex items-center gap-1 ${
            isRotating 
              ? "bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/40 font-black" 
              : "hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400"
          }`}
          title="Toggle 360 Auto-Rotation"
        >
          <RotateCw className={`w-3.5 h-3.5 ${isRotating ? "animate-spin" : ""}`} />
          <span className="hidden sm:inline">{isRotating ? "Spinning" : "Paused"}</span>
        </button>

        <button
          type="button"
          onClick={toggleAnimation}
          className={`p-1.5 rounded-lg transition-all flex items-center gap-1 ${
            isAnimating 
              ? "bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/40 font-black" 
              : "hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400"
          }`}
          title="Toggle Walking Animation"
        >
          {isAnimating ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          <span className="hidden sm:inline">{isAnimating ? "Animate" : "Static"}</span>
        </button>

        {capeUrl && (
          <button
            type="button"
            onClick={toggleElytra}
            className={`p-1.5 rounded-lg transition-all flex items-center gap-1 ${
              hasElytra 
                ? "bg-purple-500/20 text-purple-600 dark:text-purple-400 border border-purple-500/40 font-black" 
                : "hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400"
            }`}
            title="Toggle Cape vs Elytra Wings"
          >
            <Shield className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">{hasElytra ? "Elytra" : "Cape"}</span>
          </button>
        )}
      </div>
    </div>
  );
}
