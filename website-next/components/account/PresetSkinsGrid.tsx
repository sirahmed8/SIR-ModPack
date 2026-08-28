"use client";

import React from "react";
import { Sparkles, Check } from "lucide-react";
import { soundFx } from "@/lib/sound";

export interface PresetSkin {
  name: string;
  creator: string;
  skinUrl: string;
  model: "classic" | "slim";
  tag: string;
}

export const PRESET_SKINS: PresetSkin[] = [
  { name: "Steve (Classic)", creator: "Mojang", skinUrl: "https://minotar.net/skin/Steve", model: "classic", tag: "Default" },
  { name: "Alex (Slim)", creator: "Mojang", skinUrl: "https://minotar.net/skin/Alex", model: "slim", tag: "Default" },
  { name: "Technoblade", creator: "Legend", skinUrl: "https://minotar.net/skin/Technoblade", model: "classic", tag: "Creator" },
  { name: "Dream", creator: "Speedrunner", skinUrl: "https://minotar.net/skin/Dream", model: "classic", tag: "Creator" },
  { name: "DanTDM", creator: "Diamond", skinUrl: "https://minotar.net/skin/DanTDM", model: "classic", tag: "Creator" },
  { name: "MumboJumbo", creator: "Redstone", skinUrl: "https://minotar.net/skin/MumboJumbo", model: "classic", tag: "Creator" },
  { name: "Grian", creator: "Builder", skinUrl: "https://minotar.net/skin/Grian", model: "classic", tag: "Creator" },
  { name: "Notch", creator: "Creator", skinUrl: "https://minotar.net/skin/Notch", model: "classic", tag: "Classic" }
];

interface PresetSkinsGridProps {
  selectedSkinUrl: string;
  onSelect: (preset: PresetSkin) => void;
}

export function PresetSkinsGrid({ selectedSkinUrl, onSelect }: PresetSkinsGridProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Curated Creator & Legend Skins</span>
        </h4>
        <span className="text-[10px] text-slate-500 font-mono">1-Click Apply</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {PRESET_SKINS.map((preset) => {
          const isSelected = selectedSkinUrl === preset.skinUrl;
          return (
            <button
              key={preset.name}
              type="button"
              onClick={() => {
                soundFx.playClick();
                onSelect(preset);
              }}
              className={`p-2.5 rounded-2xl border text-left transition-all cursor-pointer flex items-center gap-2.5 ${
                isSelected
                  ? "bg-cyan-500/15 border-cyan-500 ring-1 ring-cyan-500/40"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40"
              }`}
            >
              <img
                src={`https://minotar.net/avatar/${encodeURIComponent(preset.name.split(" ")[0])}/36`}
                alt={preset.name}
                className="w-8 h-8 rounded-lg shadow-sm shrink-0 border border-slate-700"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = "https://minotar.net/avatar/Steve/36";
                }}
              />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold text-white truncate">{preset.name}</p>
                <span className="text-[10px] text-slate-400 font-mono">{preset.tag}</span>
              </div>
              {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}
