"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  Trash2, 
  Copy, 
  Check, 
  Cpu, 
  Zap, 
  Flame, 
  Wrench, 
  Sword,
  Volume2,
  VolumeX,
  Maximize2,
  Minimize2,
  Share2,
  ExternalLink
} from "lucide-react";
import { askSirAIDetailed, ChatMessage } from "@/lib/gemini";
import { useEcosystem } from "@/lib/context";
import { signInWithGoogle } from "@/lib/firebase";
import { soundFx } from "@/lib/sound";

interface Message {
  id: string;
  role: "user" | "model" | "assistant";
  text: string;
  timestamp: string;
  source?: string;
  modelUsed?: string;
  suggestedAction?: {
    labelEn: string;
    labelAr: string;
    href: string;
  };
}

const QUICK_PROMPTS = [
  { labelEn: "⚡ Best RAM Settings", labelAr: "⚡ أفضل إعدادات للرام", icon: Zap, promptEn: "What are the best RAM settings and Java GC flags for SIR ModPack?", promptAr: "ما هي أفضل إعدادات الرام وأوامر Java GC للحصول على أعلى أداء وسلاسة؟" },
  { labelEn: "✨ SIR Shaders Setup", labelAr: "✨ ضبط شيدرز SIR", icon: Sparkles, promptEn: "How do I configure SIR Extreme Shaders for max graphics and 144 FPS?", promptAr: "كيف أقوم بضبط شيدرز SIR Extreme للحصول على أعلى جودة و144 فريم ثابتة؟" },
  { labelEn: "⚔️ 1.8.9 PvP Boost", labelAr: "⚔️ تسريع 1.8.9 PvP", icon: Sword, promptEn: "How is the 1.8.9 PvP engine optimized for 1000Hz polling rate and hit registration?", promptAr: "كيف تم تحسين محرك 1.8.9 لدعم 1000Hz وسرعة استجابة الضربات بدون تأخير؟" },
  { labelEn: "🚀 HAVOC Roadmap", labelAr: "🚀 مشروع هافوك HAVOC", icon: Flame, promptEn: "Tell me about the HAVOC PvP Injector project and release timeline.", promptAr: "أخبرني عن مشروع هافوك (HAVOC PvP Injector) وموعد إطلاقه." },
  { labelEn: "🎮 Offline Accounts", labelAr: "🎮 الحسابات المكركة", icon: Cpu, promptEn: "How do I add and switch cracked/offline accounts using InGameAccountSwitcher (IAS)?", promptAr: "كيف أضيف وأبدل بين الحسابات المكركة والرسمية من داخل اللعبة عبر IAS؟" },
  { labelEn: "🔧 Fix Crash / Lag", labelAr: "🔧 حل اللاق والأعطال", icon: Wrench, promptEn: "My game crashed or dropped frames. What should I check first?", promptAr: "لعبتي واجهت كراش أو هبوط في الفريمات، ما هي الخطوات الأولى للإصلاح؟" }
];

export default function AiChatbot() {
  const { lang, user } = useEcosystem();
  const isAr = lang === "ar";

  const [isOpen, setIsOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);

  // Dynamic Window Dimensions (Responsive default)
  const [dimensions, setDimensions] = useState({ width: 440, height: 600 });
  const isResizingRef = useRef<"top" | "left" | "corner" | null>(null);
  const resizeStartRef = useRef<{ startX: number; startY: number; startW: number; startH: number }>({
    startX: 0,
    startY: 0,
    startW: 440,
    startH: 600
  });

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "model",
      text: isAr
        ? "🌟 **مرحباً بك!** أنا **مساعد الذكاء الاصطناعي لمنظومة SIR (Gemini 3.6 Flash)**.\n\nاسألني أي شيء حول **SIR ModPack v1.0.0**، شيدرز SIR 2.0، ميكانيكا الـ PvP 1.8.9، تخصيص الرام، أو مشروع **HAVOC**!"
        : "🌟 **Greetings!** I am the **SIR Ecosystem AI Assistant (powered by Gemini 3.6 Flash)**.\n\nAsk me anything about **SIR ModPack v1.0.0**, SIR Shaders 2.0, 1.8.9 PvP hit mechanics, RAM optimization, or the upcoming **HAVOC** injector!",
      timestamp: "Now",
      source: "gemini-3.6-flash",
      modelUsed: "gemini-3.6-flash"
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Initialize responsive dimensions on mount / resize
  useEffect(() => {
    const updateDefaultDimensions = () => {
      if (typeof window !== "undefined") {
        const isMobile = window.innerWidth < 640;
        const initialW = isMobile ? Math.min(window.innerWidth - 20, 420) : 440;
        const initialH = isMobile ? Math.min(window.innerHeight - 90, 560) : 600;
        setDimensions({ width: initialW, height: initialH });
      }
    };
    updateDefaultDimensions();
    window.addEventListener("resize", updateDefaultDimensions);
    return () => window.removeEventListener("resize", updateDefaultDimensions);
  }, []);

  useEffect(() => {
    try {
      const alreadyOpened = localStorage.getItem("sir_ai_chat_opened");
      if (!alreadyOpened) {
        setUnreadCount(1);
      }
    } catch {}
  }, []);

  const handleOpenChat = () => {
    soundFx.playClick();
    setIsOpen(true);
    setUnreadCount(0);
    try {
      localStorage.setItem("sir_ai_chat_opened", "true");
    } catch {}
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      setUnreadCount(0);
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, messages]);

  // Text-To-Speech (Web Speech API)
  const speakMessage = (text: string, msgId: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    if (speakingMessageId === msgId) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
      return;
    }

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#_`\[\]()]/g, "").replace(/https?:\/\/\S+/g, "");
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;

    const hasArabic = /[\u0600-\u06FF]/.test(cleanText);
    utterance.lang = hasArabic ? "ar-SA" : "en-US";

    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    setSpeakingMessageId(msgId);
    window.speechSynthesis.speak(utterance);
  };

  // Window Resizing Handlers (Mouse & Touch compatible)
  const handleStartResize = (clientX: number, clientY: number, direction: "top" | "left" | "corner") => {
    if (isFullscreen) return;
    isResizingRef.current = direction;
    resizeStartRef.current = {
      startX: clientX,
      startY: clientY,
      startW: dimensions.width,
      startH: dimensions.height
    };
    document.body.style.userSelect = "none";
  };

  const handleMoveResize = useCallback((clientX: number, clientY: number) => {
    if (!isResizingRef.current || isFullscreen) return;

    const { startX, startY, startW, startH } = resizeStartRef.current;
    const deltaX = startX - clientX;
    const deltaY = startY - clientY;

    const maxW = Math.min(window.innerWidth - 16, 950);
    const maxH = Math.min(window.innerHeight - 20, 920);

    setDimensions(prev => {
      let newW = prev.width;
      let newH = prev.height;

      if (isResizingRef.current === "left" || isResizingRef.current === "corner") {
        newW = Math.max(300, Math.min(maxW, startW + deltaX));
      }
      if (isResizingRef.current === "top" || isResizingRef.current === "corner") {
        newH = Math.max(380, Math.min(maxH, startH + deltaY));
      }

      return { width: newW, height: newH };
    });
  }, [isFullscreen]);

  const handleEndResize = useCallback(() => {
    isResizingRef.current = null;
    document.body.style.userSelect = "";
  }, []);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => handleMoveResize(e.clientX, e.clientY);
    const onTouchMove = (e: TouchEvent) => {
      if (isResizingRef.current) {
        if (e.cancelable) e.preventDefault();
        if (e.touches.length > 0) {
          handleMoveResize(e.touches[0].clientX, e.touches[0].clientY);
        }
      }
    };

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", handleEndResize);
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("touchend", handleEndResize);
    window.addEventListener("touchcancel", handleEndResize);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", handleEndResize);
      window.removeEventListener("touchmove", onTouchMove);
      window.removeEventListener("touchend", handleEndResize);
      window.removeEventListener("touchcancel", handleEndResize);
    };
  }, [handleMoveResize, handleEndResize]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || input.trim();
    if (!query || loading) return;

    soundFx.playClick();

    const userMessage: Message = {
      id: "usr_" + Date.now(),
      role: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const historyPayload: ChatMessage[] = messages
        .filter(m => m.id !== "welcome")
        .map(m => ({
          role: m.role,
          text: m.text
        }));

      const aiResponse = await askSirAIDetailed(query, historyPayload);

      const botMessage: Message = {
        id: "bot_" + Date.now(),
        role: "model",
        text: aiResponse.text,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        source: aiResponse.source,
        modelUsed: aiResponse.modelUsed,
        suggestedAction: aiResponse.suggestedAction
      };

      setMessages(prev => [...prev, botMessage]);
      soundFx.playCelebration();
    } catch (err: any) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          id: "err_" + Date.now(),
          role: "model",
          text: isAr
            ? "⚠️ حدث انقطاع في الاتصال بالذكاء الاصطناعي. يرجى إعادة المحاولة."
            : "⚠️ Neural link interrupted. Please try asking again in a moment.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          source: "error"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    soundFx.playClick();
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearChat = () => {
    soundFx.playClick();
    setMessages([
      {
        id: "welcome_" + Date.now(),
        role: "model",
        text: isAr
          ? "🧹 تم تنظيف سجل المحادثة. كيف يمكنني مساعدتك الآن؟"
          : "🧹 Chat history cleared. How can I assist you with SIR ModPack?",
        timestamp: "Now"
      }
    ]);
  };

  const exportChatTranscript = () => {
    const text = messages.map(m => `[${m.timestamp}] ${m.role === "user" ? "User" : "SIR AI"}: ${m.text}`).join("\n\n");
    navigator.clipboard.writeText(text);
    setCopiedId("transcript_export");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const renderFormattedText = (text: string) => {
    const lines = text.split("\n");
    return lines.map((line, idx) => {
      if (line.startsWith("```")) return null;
      return (
        <p key={idx} className={line.startsWith("*") || line.startsWith("-") ? "ml-3 list-disc my-1" : "my-1.5"}>
          {line.split(/(\*\*.*?\*\*|`.*?`|\[.*?\]\(.*?\))/g).map((part, pIdx) => {
            if (part.startsWith("**") && part.endsWith("**")) {
              return <strong key={pIdx} className="text-white font-bold">{part.slice(2, -2)}</strong>;
            }
            if (part.startsWith("`") && part.endsWith("`")) {
              return <code key={pIdx} className="px-1.5 py-0.5 rounded-md bg-[#06090e] border border-cyan-500/30 text-cyan-300 font-mono text-[11px]">{part.slice(1, -1)}</code>;
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
                  className="text-cyan-400 underline hover:text-cyan-300 transition-colors"
                >
                  {label}
                </a>
              );
            }
            return part;
          })}
        </p>
      );
    });
  };

  // Calculated styles based on fullscreen mode (Perfect dynamic centering on mobile, 0 overflow)
  const currentStyles: React.CSSProperties = isFullscreen
    ? { 
        width: "calc(100vw - 20px)", 
        height: "calc(100dvh - 20px)", 
        bottom: "10px", 
        right: "10px", 
        left: "10px", 
        margin: "auto",
        maxWidth: "100vw"
      }
    : { 
        width: `min(calc(100vw - 24px), ${dimensions.width}px)`, 
        height: `${dimensions.height}px`, 
        maxHeight: "calc(100dvh - 24px)", 
        bottom: "12px", 
        right: "12px",
        left: "12px",
        margin: "0 auto",
        maxWidth: "100vw"
      };

  const setMobileSizePreset = (pct: number) => {
    if (typeof window !== "undefined") {
      const h = Math.round((window.innerHeight - 30) * pct);
      setDimensions(prev => ({ ...prev, height: Math.max(320, h) }));
      setIsFullscreen(false);
    }
  };

  return (
    <>
      {/* Floating Launcher Button */}
      {!isOpen && (
        <div className="fixed bottom-5 right-5 sm:bottom-6 sm:right-6 z-40">
          <button
            onClick={handleOpenChat}
            className="group relative flex items-center gap-2.5 sm:gap-3 px-4 sm:px-5 py-3 sm:py-3.5 bg-white/95 dark:bg-[#0a0f1d]/95 border border-slate-200 dark:border-cyan-500/40 hover:border-cyan-400 rounded-full shadow-2xl dark:shadow-[0_0_30px_rgba(0,229,255,0.25)] transition-all duration-200 hover:scale-105 active:scale-95 text-slate-900 dark:text-white cursor-pointer backdrop-blur-xl"
            aria-label="Open SIR AI Assistant"
          >
            <div className="relative flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-cyan-500/20 text-cyan-400">
              <Bot className="w-4 h-4 sm:w-5 sm:h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400 ring-2 ring-slate-900"></span>
                </span>
              )}
            </div>
            <div className="text-left">
              <div className="text-xs font-black tracking-wider text-cyan-400 uppercase">
                {isAr ? "مساعد SIR" : "SIR AI"}
              </div>
              <div className="text-[10px] text-slate-400 font-mono hidden sm:block">
                {isAr ? "متصل بـ Gemini 3.6" : "Gemini 3.6 Neural Link"}
              </div>
            </div>
          </button>
        </div>
      )}

      {/* Main Resizable Chat Window */}
      {isOpen && (
        <div
          style={currentStyles}
          className="fixed z-50 flex flex-col bg-white/95 dark:bg-[#070b14]/95 border border-slate-200 dark:border-cyan-500/40 rounded-3xl shadow-2xl dark:shadow-[0_0_50px_rgba(0,229,255,0.25)] text-slate-900 dark:text-white backdrop-blur-2xl overflow-hidden select-none transition-[height] duration-75 ease-out"
        >
          {/* Top Resizing Drag Handle (Mouse & Touch with Pull-To-Refresh Prevention) */}
          {!isFullscreen && (
            <div
              onMouseDown={(e) => handleStartResize(e.clientX, e.clientY, "top")}
              onTouchStart={(e) => {
                e.stopPropagation();
                if (e.touches.length > 0) {
                  handleStartResize(e.touches[0].clientX, e.touches[0].clientY, "top");
                }
              }}
              style={{ touchAction: "none", overscrollBehavior: "contain" }}
              className="w-full h-6 cursor-ns-resize flex items-center justify-center group bg-slate-900/80 hover:bg-cyan-500/20 active:bg-cyan-500/30 transition-colors shrink-0 touch-none select-none"
              title="Drag to resize height (اسحب لتغيير الارتفاع)"
            >
              <div className="w-16 h-1.5 rounded-full bg-slate-500 group-hover:bg-cyan-400 group-active:bg-cyan-300 transition-colors shadow-sm" />
            </div>
          )}

          {/* Left Edge Resizing Handle */}
          {!isFullscreen && (
            <div
              onMouseDown={(e) => handleStartResize(e.clientX, e.clientY, "left")}
              onTouchStart={(e) => {
                e.stopPropagation();
                if (e.touches.length > 0) handleStartResize(e.touches[0].clientX, e.touches[0].clientY, "left");
              }}
              style={{ touchAction: "none" }}
              className="absolute top-0 bottom-0 left-0 w-3 cursor-ew-resize hover:bg-cyan-500/20 z-10 transition-colors touch-none"
              title="Drag to resize width"
            />
          )}

          {/* Top-Left Corner Resizing Handle */}
          {!isFullscreen && (
            <div
              onMouseDown={(e) => handleStartResize(e.clientX, e.clientY, "corner")}
              onTouchStart={(e) => {
                e.stopPropagation();
                if (e.touches.length > 0) handleStartResize(e.touches[0].clientX, e.touches[0].clientY, "corner");
              }}
              style={{ touchAction: "none" }}
              className="absolute top-0 left-0 w-6 h-6 cursor-nwse-resize hover:bg-cyan-400/40 z-20 transition-colors rounded-tl-3xl touch-none flex items-center justify-center"
              title="Drag to resize width & height"
            />
          )}

          {/* Header */}
          <div className="relative flex items-center justify-between px-4 sm:px-5 py-3 border-b border-slate-200 dark:border-slate-800 bg-slate-50/90 dark:bg-[#0a0f1d]/90 shrink-0">
            <div className="flex items-center gap-2.5 sm:gap-3">
              <div className="p-1.5 sm:p-2 bg-cyan-500/10 border border-cyan-500/40 rounded-2xl text-cyan-400 shadow-sm shadow-cyan-500/20">
                <Bot className="w-4 h-4 sm:w-5 sm:h-5 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <h3 className="text-xs sm:text-sm font-black text-slate-900 dark:text-white tracking-tight">
                    {isAr ? "ذكاء SIR الاصطناعي" : "SIR Intelligence"}
                  </h3>
                  <span className="px-1.5 py-0.5 text-[8px] sm:text-[9px] font-mono font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-full flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    Gemini 3.6
                  </span>
                </div>
                <p className="text-[9px] sm:text-[10px] text-slate-400 font-mono">
                  {isAr ? "مساعد فني مباشر وتحسين الأداء" : "Live Master Intelligence & Advisor"}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {/* Quick Mobile Height Presets (Visible on Mobile) */}
              <div className="flex items-center gap-1 sm:hidden mr-1">
                <button
                  onClick={() => setMobileSizePreset(0.45)}
                  className="px-1.5 py-1 text-[9px] font-bold rounded-lg bg-slate-800/80 text-slate-300 hover:text-cyan-400 hover:bg-slate-700 transition-all cursor-pointer"
                  title="Compact size (45vh)"
                >
                  📱 S
                </button>
                <button
                  onClick={() => setMobileSizePreset(0.72)}
                  className="px-1.5 py-1 text-[9px] font-bold rounded-lg bg-slate-800/80 text-slate-300 hover:text-cyan-400 hover:bg-slate-700 transition-all cursor-pointer"
                  title="Medium size (72vh)"
                >
                  📖 M
                </button>
                <button
                  onClick={() => setMobileSizePreset(0.95)}
                  className="px-1.5 py-1 text-[9px] font-bold rounded-lg bg-slate-800/80 text-slate-300 hover:text-cyan-400 hover:bg-slate-700 transition-all cursor-pointer"
                  title="Large size (95vh)"
                >
                  🚀 L
                </button>
              </div>

              {/* Maximize / Restore Toggle */}
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-1.5 sm:p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-xl transition-all cursor-pointer"
                title={isFullscreen ? "Restore size" : "Maximize window"}
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>

              <button
                onClick={exportChatTranscript}
                className="p-1.5 sm:p-2 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-xl transition-all cursor-pointer hidden sm:block"
                title={copiedId === "transcript_export" ? "Copied!" : "Export Transcript"}
              >
                {copiedId === "transcript_export" ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
              </button>
              <button
                onClick={clearChat}
                className="p-1.5 sm:p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-xl transition-all cursor-pointer"
                title="Clear Chat History"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 sm:p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-all cursor-pointer"
                title="Close Window"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 p-3 sm:p-4 overflow-y-auto space-y-3 sm:space-y-4 font-sans select-text custom-scrollbar">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex gap-2 sm:gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {m.role !== "user" && (
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center shrink-0 mt-1 shadow-sm">
                    <Bot className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </div>
                )}

                <div
                  className={`relative max-w-[88%] sm:max-w-[84%] p-3 sm:p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                    m.role === "user"
                      ? "bg-cyan-500 text-slate-950 font-bold rounded-tr-sm shadow-md shadow-cyan-500/20"
                      : "bg-slate-100 dark:bg-[#0d1322] text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-800 rounded-tl-sm shadow-xs dark:shadow-md"
                  }`}
                >
                  <div className="break-words">
                    {renderFormattedText(m.text)}
                  </div>

                  {/* Smart Suggested Action Button */}
                  {m.suggestedAction && (
                    <div className="mt-2.5 pt-2 border-t border-slate-800">
                      <Link
                        href={m.suggestedAction.href}
                        onClick={() => setIsOpen(false)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-cyan-500/20 border border-cyan-500/50 hover:bg-cyan-500/30 text-cyan-300 font-bold text-xs transition-all"
                      >
                        <ExternalLink className="w-3 h-3 text-cyan-400" />
                        <span>{isAr ? m.suggestedAction.labelAr : m.suggestedAction.labelEn}</span>
                      </Link>
                    </div>
                  )}

                  <div
                    className={`mt-1.5 flex items-center justify-between text-[10px] ${
                      m.role === "user" ? "text-cyan-900 font-bold" : "text-slate-400 font-mono"
                    }`}
                  >
                    <span>{m.timestamp}</span>
                    {m.role !== "user" && (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => speakMessage(m.text, m.id)}
                          className="p-1 hover:text-cyan-400 transition-colors cursor-pointer"
                          title={speakingMessageId === m.id ? "Stop voice" : "Read aloud (TTS)"}
                        >
                          {speakingMessageId === m.id ? <VolumeX className="w-3.5 h-3.5 text-cyan-400 animate-pulse" /> : <Volume2 className="w-3.5 h-3.5" />}
                        </button>
                        <button
                          onClick={() => copyToClipboard(m.text, m.id)}
                          className="p-1 hover:text-cyan-400 transition-colors cursor-pointer"
                          title="Copy message"
                        >
                          {copiedId === m.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-2.5 justify-start items-center">
                <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center shrink-0">
                  <Bot className="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin" />
                </div>
                <div className="p-3 rounded-2xl rounded-tl-sm bg-slate-100 dark:bg-[#0d1322] border border-slate-200 dark:border-slate-800 text-cyan-600 dark:text-cyan-400 text-xs flex items-center gap-2 shadow-md">
                  <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 animate-bounce" />
                  <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 animate-bounce [animation-delay:0.2s]" />
                  <span className="w-2 h-2 rounded-full bg-cyan-500 dark:bg-cyan-400 animate-bounce [animation-delay:0.4s]" />
                  <span className="text-[11px] font-mono text-slate-600 dark:text-slate-400 ml-1">Thinking with Gemini 3.6...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Preset Prompts Bar */}
          <div className="px-2.5 sm:px-3 py-2 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#080d18] overflow-x-auto flex gap-2 no-scrollbar shrink-0">
            {QUICK_PROMPTS.map((qp, idx) => {
              const Icon = qp.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(isAr ? qp.promptAr : qp.promptEn)}
                  disabled={loading}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:text-cyan-600 dark:hover:text-cyan-400 text-[10px] sm:text-[11px] font-bold border border-slate-200 dark:border-slate-700/80 whitespace-nowrap transition-all cursor-pointer shadow-xs hover:border-cyan-500/40"
                >
                  <Icon className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-cyan-600 dark:text-cyan-400" />
                  <span>{isAr ? qp.labelAr : qp.labelEn}</span>
                </button>
              );
            })}
          </div>

          {/* Input Footer / Auth Gate */}
          {!user ? (
            <div className="p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#0a0f1d] flex flex-col sm:flex-row items-center justify-between gap-2.5 shrink-0">
              <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 font-mono">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                <span>{isAr ? "تسجيل الدخول مطلوب للتحدث مع الذكاء الاصطناعي" : "Sign in to chat with SIR AI Assistant"}</span>
              </div>
              <button
                type="button"
                onClick={() => signInWithGoogle()}
                className="w-full sm:w-auto px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-md shadow-cyan-500/20 cursor-pointer active:scale-95"
              >
                <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                </svg>
                <span>{isAr ? "تسجيل الدخول" : "Sign In with Google"}</span>
              </button>
            </div>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="p-2.5 sm:p-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#0a0f1d] flex items-center gap-2 shrink-0"
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={isAr ? "اسأل أي سؤال حول المنظومة، المودات، أو الشيدرز..." : "Ask any question about SIR ModPack, Shaders, or PvP..."}
                disabled={loading}
                className="flex-1 px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-2xl bg-white dark:bg-[#06090e] border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 outline-none focus:border-cyan-500 dark:focus:border-cyan-400 transition-all font-mono shadow-inner"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="p-2 sm:p-2.5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black disabled:opacity-40 transition-all cursor-pointer shadow-lg shadow-cyan-500/20 active:scale-95 flex items-center justify-center shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          )}
        </div>
      )}
    </>
  );
}
