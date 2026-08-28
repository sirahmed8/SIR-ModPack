"use client";

import React, { useEffect } from "react";
import { useEcosystem } from "@/lib/context";
import { AlertOctagon, RefreshCw, Send } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { triggerErrorReport, t } = useEcosystem();

  useEffect(() => {
    console.error("Global Error Caught:", error);
  }, [error]);

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <div className="glass-panel rounded-3xl p-8 sm:p-12 max-w-lg w-full text-center border-red-500/40 shadow-[0_0_60px_rgba(239,68,68,0.3)]">
        <div className="w-16 h-16 rounded-3xl bg-red-500/20 text-red-400 border border-red-500/40 flex items-center justify-center mx-auto mb-6">
          <AlertOctagon className="w-9 h-9" />
        </div>

        <h2 className="text-2xl sm:text-3xl font-black text-white mb-2">
          System Interruption
        </h2>
        <p className="text-xs sm:text-sm text-gray-400 mb-4 leading-relaxed">
          An unexpected runtime anomaly occurred within the platform.
        </p>

        <div className="p-3 mb-6 rounded-2xl bg-black/60 border border-gray-800 text-[11px] font-mono text-red-300 text-left overflow-x-auto max-h-32">
          {error.message || "Unknown error"}
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          <button
            onClick={() => reset()}
            className="w-full flex-1 flex items-center justify-center gap-2 py-3 px-5 rounded-2xl bg-[#00e5ff] text-[#0a0d14] font-bold text-xs shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_35px_rgba(0,229,255,0.7)] transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </button>

          <button
            onClick={() => triggerErrorReport(error.message, error.stack)}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-3 px-5 rounded-2xl bg-gradient-to-r from-red-500 to-rose-600 text-white font-bold text-xs shadow-[0_0_20px_rgba(239,68,68,0.4)] transition-all"
          >
            <Send className="w-4 h-4" />
            <span>{t.errors.reportErrorBtn}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
