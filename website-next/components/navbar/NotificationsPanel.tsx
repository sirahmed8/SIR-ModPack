"use client";

import React, { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Radio, Package, Sparkles, CheckCircle2, ExternalLink } from "lucide-react";
import { soundFx } from "@/lib/sound";

export interface NotificationItem {
  id: string;
  type: "broadcast" | "update" | "cloud";
  title: string;
  message: string;
  time: string;
  read: boolean;
  actionLabel?: string;
  actionUrl?: string;
}

interface NotificationsPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
  notifications: NotificationItem[];
  unreadCount: number;
  onMarkRead: (id: string) => void;
  onMarkAllRead: () => void;
}

export function NotificationsPanel({
  isOpen,
  onToggle,
  onClose,
  notifications,
  unreadCount,
  onMarkRead,
  onMarkAllRead,
}: NotificationsPanelProps) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => {
          soundFx.playClick();
          onToggle();
        }}
        className="relative p-2 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 hover:border-cyan-500 text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-[#00e5ff] transition-all cursor-pointer shadow-sm active:scale-95"
        title="Notifications / الإشعارات"
        aria-label="Toggle notifications menu"
      >
        <Bell className="w-4 h-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 logical-end-badge flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 border-2 border-white dark:border-[#090b10]"></span>
          </span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.96 }}
            transition={{ type: "spring", stiffness: 380, damping: 26 }}
            className="fixed inset-x-3 top-20 max-w-sm mx-auto sm:inset-auto sm:absolute sm:top-full sm:mt-2 sm:w-96 rounded-3xl bg-white dark:bg-[#0e131f] border border-slate-200 dark:border-slate-800 shadow-2xl z-[60] overflow-hidden sm-logical-popover-end"
          >
            {/* Popover Header */}
            <div className="flex items-center justify-between px-4 sm:px-5 py-3 sm:py-4 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/80 dark:bg-slate-950/40">
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-cyan-600 dark:text-[#00e5ff]" />
                <span className="text-xs font-black text-slate-900 dark:text-white uppercase tracking-wider">
                  Ecosystem Alerts
                </span>
                {unreadCount > 0 && (
                  <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-600 dark:text-[#00e5ff] text-[10px] font-black">
                    {unreadCount} NEW
                  </span>
                )}
              </div>

              {unreadCount > 0 && (
                <button
                  onClick={() => {
                    soundFx.playClick();
                    onMarkAllRead();
                  }}
                  className="text-[11px] font-bold text-cyan-600 dark:text-[#00e5ff] hover:underline cursor-pointer transition-colors"
                >
                  Mark all read
                </button>
              )}
            </div>

            {/* Notification List */}
            <div className="divide-y divide-slate-100 dark:divide-slate-800/60 max-h-72 overflow-y-auto custom-scrollbar">
              {notifications.map((notif) => (
                <div
                  key={notif.id}
                  onClick={() => onMarkRead(notif.id)}
                  className={`p-3.5 sm:p-4 transition-all cursor-pointer flex items-start gap-3 hover:bg-slate-50 dark:hover:bg-slate-900/60 ${
                    !notif.read
                      ? "bg-cyan-500/[0.04] dark:bg-cyan-500/[0.06]"
                      : "opacity-75 hover:opacity-100"
                  }`}
                >
                  <div
                    className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center border shadow-sm mt-0.5 ${
                      notif.type === "broadcast"
                        ? "bg-amber-500/10 border-amber-500/30 text-amber-500"
                        : notif.type === "update"
                        ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-600 dark:text-[#00e5ff]"
                        : "bg-emerald-500/10 border-emerald-500/30 text-emerald-500"
                    }`}
                  >
                    {notif.type === "broadcast" && <Radio className="w-4 h-4" />}
                    {notif.type === "update" && <Package className="w-4 h-4" />}
                    {notif.type === "cloud" && <Sparkles className="w-4 h-4" />}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <h4
                        className={`text-xs font-black truncate ${
                          !notif.read ? "text-slate-900 dark:text-white" : "text-slate-700 dark:text-gray-300"
                        }`}
                      >
                        {notif.title}
                      </h4>
                      <span className="text-[10px] font-mono text-slate-400 dark:text-gray-500 shrink-0">
                        {notif.time}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 dark:text-gray-400 leading-relaxed line-clamp-2">
                      {notif.message}
                    </p>

                    {notif.actionUrl && notif.actionLabel && (
                      <div className="mt-2">
                        <a
                          href={notif.actionUrl}
                          onClick={(e) => {
                            e.stopPropagation();
                            onMarkRead(notif.id);
                            onClose();
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-600 dark:text-[#00e5ff] text-[10px] font-bold border border-cyan-500/30 transition-all"
                        >
                          <span>{notif.actionLabel}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      </div>
                    )}
                  </div>

                  {!notif.read && (
                    <span className="w-2 h-2 rounded-full bg-cyan-500 shrink-0 mt-1.5 shadow-[0_0_8px_rgba(0,229,255,0.8)]" />
                  )}
                </div>
              ))}
            </div>

            <div className="px-4 py-2.5 bg-slate-50/80 dark:bg-slate-950/60 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 dark:text-gray-500">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                <span>Live Realtime Connected</span>
              </span>
              <span className="font-mono text-[10px]">Max 3 Alerts</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
