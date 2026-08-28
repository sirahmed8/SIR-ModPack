"use client";

import React from "react";
import { Gamepad2, CheckCheck, Trash2, KeyRound } from "lucide-react";
import { ClaimedAccountItem } from "@/lib/multiAccounts";
import { soundFx } from "@/lib/sound";

interface MultiAccountManagerProps {
  accounts: ClaimedAccountItem[];
  activeIgn: string;
  onSelectAccount: (acc: ClaimedAccountItem) => void;
  onDeleteAccount: (ign: string) => void;
  onGenerateSyncCode: () => void;
  generatingCode: boolean;
}

export function MultiAccountManager({
  accounts,
  activeIgn,
  onSelectAccount,
  onDeleteAccount,
  onGenerateSyncCode,
  generatingCode,
}: MultiAccountManagerProps) {
  if (!accounts || accounts.length === 0) {
    return null;
  }

  return (
    <div className="p-5 rounded-3xl bg-slate-900/60 border border-slate-800 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Gamepad2 className="w-5 h-5 text-cyan-400" />
          <h4 className="text-sm font-bold text-white">Connected Minecraft Profiles</h4>
          <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-[10px] font-mono">
            {accounts.length} Profiles
          </span>
        </div>

        <button
          onClick={() => {
            soundFx.playClick();
            onGenerateSyncCode();
          }}
          disabled={generatingCode}
          className="px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 text-xs font-bold border border-cyan-500/30 flex items-center gap-1.5 transition-all cursor-pointer"
        >
          <KeyRound className="w-3.5 h-3.5" />
          <span>{generatingCode ? "Generating Code..." : "6-Digit Sync Code"}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {accounts.map((acc) => {
          const isActive = acc.ign.toLowerCase() === activeIgn.toLowerCase();
          return (
            <div
              key={acc.ign}
              className={`p-3 rounded-2xl border transition-all flex items-center justify-between gap-2.5 ${
                isActive
                  ? "bg-cyan-500/10 border-cyan-500 ring-1 ring-cyan-500/40"
                  : "bg-slate-950/60 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <img
                  src={`https://minotar.net/avatar/${encodeURIComponent(acc.ign)}/36`}
                  alt={acc.ign}
                  className="w-9 h-9 rounded-xl border border-slate-700 shrink-0"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = "https://minotar.net/avatar/Steve/36";
                  }}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-bold text-white truncate">@{acc.ign}</p>
                  <span className="text-[10px] text-slate-400 font-mono capitalize">
                    {acc.accountType || "offline"} • {acc.model || "classic"}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                {!isActive && (
                  <button
                    onClick={() => {
                      soundFx.playClick();
                      onSelectAccount(acc);
                    }}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-500 hover:text-slate-950 text-slate-300 text-xs font-bold transition-all"
                    title="Activate Profile"
                  >
                    <CheckCheck className="w-3.5 h-3.5" />
                  </button>
                )}
                <button
                  onClick={() => {
                    soundFx.playClick();
                    onDeleteAccount(acc.ign);
                  }}
                  className="p-1.5 rounded-lg bg-rose-500/15 text-rose-400 hover:bg-rose-500 hover:text-white transition-all"
                  title="Remove Profile"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
