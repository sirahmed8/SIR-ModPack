"use client";

import React from "react";
import { Radio } from "lucide-react";

interface BroadcastProps {
  broadcast: {
    active?: boolean;
    version?: string;
    title?: string;
    titleAr?: string;
    message?: string;
    messageAr?: string;
    buttonLabel?: string;
    buttonLabelAr?: string;
    buttonUrl?: string;
  } | null;
  lang: string;
}

export function BroadcastBanner({ broadcast, lang }: BroadcastProps) {
  if (!broadcast || !broadcast.active) return null;

  const isAr = lang === "ar";
  const title = isAr && broadcast.titleAr ? broadcast.titleAr : broadcast.title;
  const message = isAr && broadcast.messageAr ? broadcast.messageAr : broadcast.message;
  const btnLabel = isAr && broadcast.buttonLabelAr ? broadcast.buttonLabelAr : broadcast.buttonLabel;

  return (
    <div className="w-full bg-gradient-to-r from-cyan-600 via-emerald-600 to-cyan-600 text-white px-3 sm:px-4 py-1.5 sm:py-2 text-[11px] sm:text-xs font-bold flex items-center justify-center gap-2 sm:gap-3 shadow-md flex-wrap">
      <div className="flex items-center gap-1.5">
        <Radio className="w-3.5 h-3.5 animate-pulse shrink-0" />
        <span>
          {broadcast.version && (
            <strong className="px-1.5 py-0.5 rounded bg-black/30 mr-1 font-mono text-[9px] sm:text-[10px]">
              {broadcast.version}
            </strong>
          )}
          <strong>{title}:</strong> {message}
        </span>
      </div>
      {btnLabel && broadcast.buttonUrl && (
        <a
          href={broadcast.buttonUrl}
          target={broadcast.buttonUrl.startsWith("http") ? "_blank" : undefined}
          rel="noopener noreferrer"
          className="px-2 py-0.5 sm:py-1 rounded-lg bg-black text-white hover:bg-slate-900 transition-all text-[10px] sm:text-[11px] font-black shrink-0 shadow-sm border border-white/20"
        >
          {btnLabel}
        </a>
      )}
    </div>
  );
}
