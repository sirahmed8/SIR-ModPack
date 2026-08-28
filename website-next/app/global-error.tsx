"use client";

import React from "react";
import { AlertOctagon, RefreshCw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 text-white min-h-screen flex items-center justify-center p-6 font-sans">
        <div className="max-w-md w-full p-8 bg-zinc-900 border border-red-500/40 rounded-3xl text-center space-y-5 shadow-[0_0_50px_rgba(239,68,68,0.2)]">
          <div className="inline-flex p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400">
            <AlertOctagon className="w-10 h-10" />
          </div>
          <h1 className="text-2xl font-bold text-white">Global Kernel Panic</h1>
          <p className="text-sm text-zinc-400">
            A critical root-level fault occurred. The master process has been isolated safely.
          </p>
          <div className="p-3 bg-black border border-zinc-800 rounded-xl text-left font-mono text-xs text-red-400 overflow-x-auto">
            {error.message || "Root fault"}
          </div>
          <button
            onClick={() => reset()}
            className="w-full inline-flex items-center justify-center gap-2 py-3 font-semibold text-sm text-black bg-cyan-400 hover:bg-cyan-300 rounded-2xl transition-all shadow-[0_0_20px_rgba(0,229,255,0.3)]"
          >
            <RefreshCw className="w-4 h-4" />
            Hard Restart Process
          </button>
        </div>
      </body>
    </html>
  );
}
