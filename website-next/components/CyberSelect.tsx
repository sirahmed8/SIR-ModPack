"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check } from "lucide-react";

export interface CyberSelectOption<T = string | number> {
  value: T;
  label: string;
  badge?: string;
  icon?: React.ReactNode;
}

interface CyberSelectProps<T = string | number> {
  options: CyberSelectOption<T>[];
  value: T;
  onChange: (val: T) => void;
  label?: string;
  icon?: React.ReactNode;
  accentColor?: "cyan" | "emerald" | "amber" | "rose" | "indigo";
  className?: string;
}

export function CyberSelect<T extends string | number>({
  options,
  value,
  onChange,
  label,
  icon,
  accentColor = "cyan",
  className = ""
}: CyberSelectProps<T>) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find(o => o.value === value) || options[0];

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const accentClasses = {
    cyan: {
      btn: "border-slate-200 dark:border-cyan-500/40 hover:border-cyan-400 focus:border-cyan-400 focus:ring-cyan-500/20",
      activeText: "text-cyan-700 dark:text-cyan-400",
      selectedBg: "bg-cyan-50 dark:bg-cyan-950/60 text-cyan-900 dark:text-cyan-300 border-cyan-300 dark:border-cyan-500/40",
      pill: "bg-cyan-100 dark:bg-cyan-500/20 text-cyan-800 dark:text-cyan-400 border-cyan-300 dark:border-cyan-500/40"
    },
    emerald: {
      btn: "border-slate-200 dark:border-emerald-500/40 hover:border-emerald-400 focus:border-emerald-400 focus:ring-emerald-500/20",
      activeText: "text-emerald-700 dark:text-emerald-400",
      selectedBg: "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-900 dark:text-emerald-300 border-emerald-300 dark:border-emerald-500/40",
      pill: "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-800 dark:text-emerald-400 border-emerald-300 dark:border-emerald-500/40"
    },
    amber: {
      btn: "border-slate-200 dark:border-amber-500/40 hover:border-amber-400 focus:border-amber-400 focus:ring-amber-500/20",
      activeText: "text-amber-700 dark:text-amber-400",
      selectedBg: "bg-amber-50 dark:bg-amber-950/60 text-amber-900 dark:text-amber-300 border-amber-300 dark:border-amber-500/40",
      pill: "bg-amber-100 dark:bg-amber-500/20 text-amber-800 dark:text-amber-400 border-amber-300 dark:border-amber-500/40"
    },
    rose: {
      btn: "border-slate-200 dark:border-rose-500/40 hover:border-rose-400 focus:border-rose-400 focus:ring-rose-500/20",
      activeText: "text-rose-700 dark:text-rose-400",
      selectedBg: "bg-rose-50 dark:bg-rose-950/60 text-rose-900 dark:text-rose-300 border-rose-300 dark:border-rose-500/40",
      pill: "bg-rose-100 dark:bg-rose-500/20 text-rose-800 dark:text-rose-400 border-rose-300 dark:border-rose-500/40"
    },
    indigo: {
      btn: "border-slate-200 dark:border-indigo-500/40 hover:border-indigo-400 focus:border-indigo-400 focus:ring-indigo-500/20",
      activeText: "text-indigo-700 dark:text-indigo-400",
      selectedBg: "bg-indigo-50 dark:bg-indigo-950/60 text-indigo-900 dark:text-indigo-300 border-indigo-300 dark:border-indigo-500/40",
      pill: "bg-indigo-100 dark:bg-indigo-500/20 text-indigo-800 dark:text-indigo-400 border-indigo-300 dark:border-indigo-500/40"
    }
  }[accentColor];

  return (
    <div ref={containerRef} className={`relative inline-block text-left ${className}`}>
      {label && (
        <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400 block mb-1.5 font-bold">
          {label}
        </span>
      )}

      {/* Button Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`w-full px-4 py-2.5 rounded-2xl bg-white dark:bg-[#080d16]/90 border text-slate-900 dark:text-slate-100 text-xs font-bold font-mono transition-all flex items-center justify-between gap-3 shadow-xs dark:shadow-lg cursor-pointer backdrop-blur-xl ${accentClasses.btn} ${
          isOpen ? "ring-2 ring-cyan-500/30 border-cyan-400" : ""
        }`}
      >
        <div className="flex items-center gap-2 min-w-0">
          {icon && <span className="shrink-0">{icon}</span>}
          <span className="truncate">{selectedOption?.label}</span>
          {selectedOption?.badge && (
            <span className={`text-[9px] px-2 py-0.5 rounded-full border font-mono font-bold ${accentClasses.pill}`}>
              {selectedOption.badge}
            </span>
          )}
        </div>
        <motion.span
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2, ease: "easeInOut" }}
          className="text-slate-400 dark:text-slate-400 shrink-0"
        >
          <ChevronDown className="w-4 h-4" />
        </motion.span>
      </button>

      {/* Animated Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="cyber-dropdown-menu absolute z-[9999] mt-2 w-full min-w-[240px] max-h-64 overflow-y-auto rounded-2xl bg-white dark:bg-[#090e1a] border border-slate-200 dark:border-slate-700 shadow-2xl dark:shadow-[0_25px_60px_rgba(0,0,0,0.98),0_0_20px_rgba(0,229,255,0.15)] p-1.5 custom-scrollbar transition-colors duration-150"
          >
            <div className="space-y-1">
              {options.map(opt => {
                const isSelected = opt.value === value;
                return (
                  <button
                    key={String(opt.value)}
                    type="button"
                    onClick={() => {
                      onChange(opt.value);
                      setIsOpen(false);
                    }}
                    className={`w-full px-3.5 py-2.5 rounded-xl text-left text-xs font-mono font-bold transition-all flex items-center justify-between gap-2 cursor-pointer ${
                      isSelected
                        ? `${accentClasses.selectedBg} border shadow-xs font-extrabold`
                        : "text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-[#12192c] hover:text-slate-900 dark:hover:text-white"
                    }`}
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      {opt.icon && <span className="shrink-0">{opt.icon}</span>}
                      <span className="truncate">{opt.label}</span>
                      {opt.badge && (
                        <span className={`text-[9px] px-2 py-0.5 rounded-full border font-mono font-bold shrink-0 ${accentClasses.pill}`}>
                          {opt.badge}
                        </span>
                      )}
                    </div>
                    {isSelected && <Check className="w-4 h-4 shrink-0 text-cyan-600 dark:text-cyan-400 font-black" />}
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
