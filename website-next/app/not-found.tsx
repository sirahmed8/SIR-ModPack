"use client";

import React from "react";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";
import { AlertCircle, Home, Send } from "lucide-react";

export default function NotFound() {
  const { t, triggerErrorReport } = useEcosystem();

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <div className="glass-panel rounded-3xl p-8 sm:p-12 max-w-lg w-full text-center border-red-500/30 shadow-[0_0_50px_rgba(239,68,68,0.2)]">
        <div className="w-16 h-16 rounded-3xl bg-red-500/20 text-red-400 border border-red-500/40 flex items-center justify-center mx-auto mb-6">
          <AlertCircle className="w-9 h-9" />
        </div>

        <h1 className="text-3xl sm:text-4xl font-black text-white mb-3">
          {t.errors.notFoundTitle}
        </h1>
        <p className="text-xs sm:text-sm text-gray-400 mb-8 leading-relaxed">
          {t.errors.notFoundSubtitle}
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-3">
          <Link
            href="/"
            className="w-full flex-1 flex items-center justify-center gap-2 py-3 px-5 rounded-2xl bg-[#00e5ff] text-[#0a0d14] font-bold text-xs shadow-[0_0_20px_rgba(0,229,255,0.4)] hover:shadow-[0_0_30px_rgba(0,229,255,0.7)] transition-all"
          >
            <Home className="w-4 h-4" />
            <span>{t.errors.returnHomeBtn}</span>
          </Link>

          <button
            onClick={() => triggerErrorReport("404 Not Found triggered on non-existent route")}
            className="w-full sm:w-auto flex items-center justify-center gap-2 py-3 px-5 rounded-2xl bg-white/5 border border-gray-700 text-gray-300 hover:text-white text-xs font-semibold transition-all"
          >
            <Send className="w-4 h-4" />
            <span>{t.errors.reportErrorBtn}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
