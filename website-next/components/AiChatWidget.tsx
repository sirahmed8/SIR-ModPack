"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useEcosystem } from "@/lib/context";
import { askSirAI } from "@/lib/gemini";
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  Lock,
  Crown,
  Trash2,
  Copy,
  Check,
  Zap,
  Sword,
  Flame,
  Cpu,
  Wrench
} from "lucide-react";

interface ChatMessage {
  id: string;
  role: "user" | "model";
  text: string;
  timestamp: string;
}

const QUICK_PROMPTS = [
  { label: "⚡ Best RAM Settings", icon: Zap, prompt: "What are the best RAM settings and Java GC flags for SIR ModPack?" },
  { label: "✨ SIR Shaders Setup", icon: Sparkles, prompt: "How do I configure SIR Extreme SIR Shaders for max graphics and 144 FPS?" },
  { label: "⚔️ 1.8.9 PvP Boost", icon: Sword, prompt: "How is the 1.8.9 PvP engine optimized for 1000Hz polling rate and hit registration?" },
  { label: "🚀 HAVOC Roadmap", icon: Flame, prompt: "Tell me about the HAVOC PvP Injector project and release timeline." },
  { label: "🎮 Cracked & IAS Hub", icon: Cpu, prompt: "How do I add and switch cracked/offline accounts using InGameAccountSwitcher (IAS)?" },
  { label: "🔧 Fix Crash / Lag", icon: Wrench, prompt: "My game crashed or dropped frames. What should I check first?" }
];

export function AiChatWidget() {
  const { t, dir, user } = useEcosystem();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [queriesLeft, setQueriesLeft] = useState<number>(10);
  
  const [dimensions, setDimensions] = useState({ width: 420, height: 580 });
  const isResizingRef = useRef<"top" | "left" | "corner" | null>(null);
  const resizeStartRef = useRef<{ startX: number; startY: number; startW: number; startH: number }>({
    startX: 0,
    startY: 0,
    startW: 420,
    startH: 580
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const adminEmail = process.env.NEXT_PUBLIC_ADMIN_EMAIL || "a7medorabe7@gmail.com";
  const isAdmin = user?.email?.toLowerCase() === adminEmail.toLowerCase();

  useEffect(() => {
    try {
      const today = new Date().toISOString().slice(0, 10);
      const storedDate = localStorage.getItem("sir_ai_usage_date");
      const storedCount = Number(localStorage.getItem("sir_ai_usage_count") || "0");

      if (storedDate !== today) {
        localStorage.setItem("sir_ai_usage_date", today);
        localStorage.setItem("sir_ai_usage_count", "0");
        setQueriesLeft(10);
      } else {
        setQueriesLeft(Math.max(0, 10 - storedCount));
      }
    } catch {}
  }, []);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          role: "model",
          text: t.ai?.welcomeMsg || "🌟 **Greetings!** I am the **SIR Ecosystem AI Assistant**.\n\nAsk me anything about **SIR ModPack v1.0.0**, SIR Shaders, 1.8.9 PvP hit mechanics, RAM allocation, or the upcoming **HAVOC** injector!",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
    }
  }, [isOpen, t.ai?.welcomeMsg, messages.length]);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages, loading]);

  const handleMouseDownResize = (e: React.MouseEvent, direction: "top" | "left" | "corner") => {
    e.preventDefault();
    isResizingRef.current = direction;
    resizeStartRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      startW: dimensions.width,
      startH: dimensions.height
    };
    document.body.style.userSelect = "none";
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizingRef.current) return;

    const { startX, startY, startW, startH } = resizeStartRef.current;
    const deltaX = dir === "rtl" ? e.clientX - startX : startX - e.clientX;
    const deltaY = startY - e.clientY;

    const maxW = Math.min(window.innerWidth - 32, 750);
    const maxH = Math.min(window.innerHeight - 32, 850);

    setDimensions(prev => {
      let newW = prev.width;
      let newH = prev.height;

      if (isResizingRef.current === "left" || isResizingRef.current === "corner") {
        newW = Math.max(340, Math.min(maxW, startW + deltaX));
      }
      if (isResizingRef.current === "top" || isResizingRef.current === "corner") {
        newH = Math.max(420, Math.min(maxH, startH + deltaY));
      }

      return { width: newW, height: newH };
    });
  }, [dir]);

  const handleMouseUp = useCallback(() => {
    isResizingRef.current = null;
    document.body.style.userSelect = "";
  }, []);

  useEffect(() => {
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [handleMouseMove, handleMouseUp]);

  const handleSend = async (userPrompt?: string) => {
    const query = userPrompt || input.trim();
    if (!query || loading) return;

    if (!isAdmin && queriesLeft <= 0) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "model",
          text: "🔒 **Daily Free AI Quota Reached (10/10 queries)**.\n\nYour queries reset tomorrow at midnight. To request higher limits, connect with **SIR Ahmed** via the [Linktree](https://linktr.ee/sir.ahmed)!",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
      return;
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!userPrompt) setInput("");
    setLoading(true);

    if (!isAdmin) {
      try {
        const today = new Date().toISOString().slice(0, 10);
        const storedCount = Number(localStorage.getItem("sir_ai_usage_count") || "0") + 1;
        localStorage.setItem("sir_ai_usage_date", today);
        localStorage.setItem("sir_ai_usage_count", storedCount.toString());
        setQueriesLeft(Math.max(0, 10 - storedCount));
      } catch {}
    }

    try {
      const history = messages.map(m => ({ role: m.role, text: m.text }));
      const aiReply = await askSirAI(query, history);

      const botMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "model",
        text: typeof aiReply === "string" ? aiReply : (aiReply as any)?.text || "I am processing your request...",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "model",
          text: "I encountered a network issue. Please check your connection or contact the developer via Linktree.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome-reset",
        role: "model",
        text: "✨ **Chat cleared!** How can I assist you with SIR ModPack today?",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      }
    ]);
  };

  const formatMarkdown = (rawText: string) => {
    const lines = rawText.split("\n");
    return lines.map((line, idx) => {
      const isBullet = line.trim().startsWith("* ") || line.trim().startsWith("- ");
      const cleanLine = isBullet ? line.trim().substring(2) : line;

      const parts = cleanLine.split(/(\*\*.*?\*\*|\[.*?\]\(.*?\))/g);
      const renderedParts = parts.map((part, pIdx) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return <strong key={pIdx} className="font-bold text-cyan-600 dark:text-cyan-400">{part.slice(2, -2)}</strong>;
        }
        if (part.startsWith("[") && part.includes("](") && part.endsWith(")")) {
          const label = part.match(/\[(.*?)\]/)?.[1] || "Link";
          const href = part.match(/\((.*?)\)/)?.[1] || "#";
          return (
            <a 
              key={pIdx} 
              href={href} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-cyan-600 dark:text-cyan-400 underline hover:opacity-80 transition-opacity"
            >
              {label}
            </a>
          );
        }
        return part;
      });

      if (isBullet) {
        return (
          <li key={idx} className="ml-4 list-disc my-1">
            {renderedParts}
          </li>
        );
      }

      return (
        <span key={idx} className="block my-0.5">
          {renderedParts}
        </span>
      );
    });
  };

  return (
    <div className={`fixed bottom-6 z-50 ${dir === "rtl" ? "left-6" : "right-6"}`}>
      <AnimatePresence mode="wait">
        {!isOpen && (
          <motion.button
            key="chat-trigger-btn"
            initial={{ scale: 0, opacity: 0, rotate: -25 }}
            animate={{ scale: 1, opacity: 1, rotate: 0 }}
            exit={{ scale: 0, opacity: 0, rotate: 25 }}
            transition={{ type: "spring", stiffness: 350, damping: 22 }}
            onClick={() => setIsOpen(true)}
            className="relative flex items-center justify-center w-14 h-14 rounded-2xl bg-white dark:bg-[#0a0d14] border-2 border-cyan-500/60 dark:border-cyan-400/50 shadow-[0_10px_30px_rgba(0,229,255,0.4)] hover:scale-110 active:scale-95 transition-all duration-300 group cursor-pointer"
            title="SIR AI Assistant"
          >
            <Bot className="w-7 h-7 text-cyan-600 dark:text-[#00e5ff] group-hover:text-emerald-500 transition-colors" />
          </motion.button>
        )}

        {isOpen && (
          <motion.div
            key="chat-expanded-drawer"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: "spring", stiffness: 320, damping: 25 }}
            style={{ width: `${dimensions.width}px`, height: `${dimensions.height}px` }}
            className="ai-chatbot-window relative max-w-[96vw] max-h-[92vh] rounded-3xl bg-white/95 dark:bg-[#0a0e17]/95 border border-slate-200 dark:border-cyan-500/30 shadow-[0_20px_60px_rgba(0,0,0,0.25)] dark:shadow-[0_20px_70px_rgba(0,0,0,0.9)] backdrop-blur-2xl flex flex-col overflow-hidden select-none"
          >
            <div 
              onMouseDown={(e) => handleMouseDownResize(e, "top")}
              className="w-full py-2 flex justify-center cursor-ns-resize hover:bg-cyan-500/10 dark:hover:bg-cyan-500/20 transition-colors group bg-slate-100/90 dark:bg-[#0f1422]/90 shrink-0 border-b border-slate-200/60 dark:border-slate-800/60"
              title="Drag up/down freely to resize height"
            >
              <div className="w-14 h-1.5 rounded-full bg-slate-300 dark:bg-slate-600 group-hover:bg-cyan-500 dark:group-hover:bg-cyan-400 transition-all" />
            </div>

            <div
              onMouseDown={(e) => handleMouseDownResize(e, "left")}
              className={`absolute top-0 bottom-0 ${dir === "rtl" ? "right-0" : "left-0"} w-2.5 cursor-ew-resize hover:bg-cyan-500/20 z-20 transition-colors`}
              title="Drag left/right to resize width"
            />

            <div
              onMouseDown={(e) => handleMouseDownResize(e, "corner")}
              className={`absolute top-0 ${dir === "rtl" ? "right-0" : "left-0"} w-5 h-5 cursor-nwse-resize hover:bg-cyan-400/40 z-30 transition-colors rounded-tl-3xl`}
              title="Drag freely to resize width & height"
            />

            <div className="px-5 py-3.5 bg-slate-50/95 dark:bg-[#0e1320]/95 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-2xl bg-cyan-500/10 dark:bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-600 dark:text-cyan-400">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-xs sm:text-sm font-extrabold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <span>{t.ai?.widgetTitle || "SIR Intelligence"}</span>
                    <Sparkles className="w-3.5 h-3.5 text-cyan-500 dark:text-cyan-400" />
                  </h4>
                  <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono font-bold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                    <span>Online • AI Assistant</span>
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {isAdmin ? (
                  <span className="px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 text-[10px] font-bold flex items-center gap-1" title="Owner: Unlimited Access">
                    <Crown className="w-3 h-3" /> Owner (∞)
                  </span>
                ) : (
                  <span className="px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-700 dark:text-cyan-400 text-[10px] font-mono font-bold" title="Free daily quota">
                    {queriesLeft}/10 Left
                  </span>
                )}

                <button
                  onClick={clearChat}
                  className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-xl transition-all"
                  title="Clear Chat History"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-slate-800 rounded-xl transition-all"
                  title="Close Window"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-4 font-sans select-text text-slate-800 dark:text-slate-200">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {m.role !== "user" && (
                    <div className="w-7 h-7 rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 border border-cyan-500/30 text-cyan-600 dark:text-cyan-300 flex items-center justify-center shrink-0 mt-1">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`relative max-w-[85%] p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                      m.role === "user"
                        ? "bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-semibold rounded-tr-sm shadow-md"
                        : "bg-slate-100 dark:bg-[#121826] text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-800 rounded-tl-sm shadow-sm"
                    }`}
                  >
                    <div className="break-words">
                      {formatMarkdown(m.text)}
                    </div>

                    <div
                      className={`mt-2 flex items-center justify-between text-[10px] ${
                        m.role === "user" ? "text-cyan-100" : "text-slate-400 dark:text-slate-500 font-mono"
                      }`}
                    >
                      <span>{m.timestamp}</span>
                      {m.role !== "user" && (
                        <button
                          onClick={() => copyToClipboard(m.text, m.id)}
                          className="p-1 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors"
                          title="Copy message"
                        >
                          {copiedId === m.id ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-7 h-7 rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 border border-cyan-500/30 text-cyan-600 dark:text-cyan-300 flex items-center justify-center shrink-0">
                    <Bot className="w-4 h-4 animate-spin" />
                  </div>
                  <div className="p-3.5 rounded-2xl rounded-tl-sm bg-slate-100 dark:bg-[#121826] border border-slate-200 dark:border-slate-800 text-cyan-600 dark:text-cyan-400 text-xs flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce" />
                    <span className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce [animation-delay:0.2s]" />
                    <span className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="px-3 py-2 border-t border-slate-200/80 dark:border-slate-800/80 bg-slate-50/80 dark:bg-[#0c101a]/80 overflow-x-auto flex gap-2 no-scrollbar shrink-0">
              {QUICK_PROMPTS.map((qp, idx) => {
                const Icon = qp.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSend(qp.prompt)}
                    disabled={loading}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-700/80 text-slate-700 dark:text-slate-200 text-[11px] font-medium border border-slate-200 dark:border-slate-700 whitespace-nowrap transition-all cursor-pointer shadow-sm"
                  >
                    <Icon className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
                    <span>{qp.label}</span>
                  </button>
                );
              })}
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/95 dark:bg-[#0e1320]/95 flex items-center gap-2 shrink-0"
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about SIR ModPack..."
                disabled={loading}
                className="flex-1 px-4 py-2.5 rounded-2xl bg-white dark:bg-[#07090e] border border-slate-300 dark:border-slate-700 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 outline-none focus:border-cyan-500 transition-all shadow-inner"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="p-2.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold disabled:opacity-40 transition-all cursor-pointer shadow-md"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
