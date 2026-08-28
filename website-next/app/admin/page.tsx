"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Users, 
  Download, 
  AlertTriangle, 
  Activity, 
  Server, 
  Database, 
  Radio, 
  Sparkles, 
  ShieldCheck, 
  RefreshCw, 
  CheckCircle, 
  CheckCircle2,
  AlertCircle,
  ExternalLink, 
  Send, 
  Flame, 
  Eye, 
  X,
  Layers,
  ArrowLeft,
  RotateCcw,
  Bot,
  Wand2,
  Sliders,
  Bell,
  Trash2,
  Zap,
  Globe,
  FileText,
  Plus,
  History,
  Tag,
  Link2,
  Languages,
  Monitor,
  Smartphone,
  Copy,
  ChevronUp,
  ChevronDown,
  Clock,
  Share2
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  subscribeToDownloads, 
  subscribeToLivePresence, 
  fetchErrorReports, 
  updateErrorReportStatus, 
  getLatestRelease, 
  publishReleaseToRTDB, 
  toggleMandatoryUpdate,
  resetAllAnalytics,
  publishBroadcastMessage,
  dismissBroadcastMessage,
  subscribeToBroadcast,
  fetchChangelogEntries,
  publishChangelogEntry,
  deleteChangelogEntry,
  DEFAULT_MASTER_CHANGELOG,
  ErrorReportData, 
  ReleaseInfo,
  BroadcastMessage,
  ChangelogEntry
} from "@/lib/firebase";
import { 
  polishAnnouncementWithAI, 
  polishChangelogWithAI, 
  translateBroadcastToArabic, 
  translateChangelogToArabic 
} from "@/lib/gemini";

const CATEGORY_ICONS = ["🖥️", "🌊", "💎", "🌐", "⚡", "🛡️", "🚀", "🎮", "⚙️", "✨", "🔥", "📦"];


export default function AdminDashboard() {
  const [liveUsers, setLiveUsers] = useState<number>(0);
  const [downloads, setDownloads] = useState<{ installer: number; bundle: number }>({ installer: 0, bundle: 0 });
  const [errorReports, setErrorReports] = useState<ErrorReportData[]>([]);
  const [loadingReports, setLoadingReports] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);
  const [selectedReport, setSelectedReport] = useState<ErrorReportData | null>(null);
  const [showResetConfirmModal, setShowResetConfirmModal] = useState(false);
  const [adminToast, setAdminToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = (message: string, type: "success" | "error" = "success") => {
    setAdminToast({ message, type });
    setTimeout(() => {
      setAdminToast((curr) => (curr?.message === message ? null : curr));
    }, 4000);
  };
  
  // -------------------------------------------------------------
  // Studio Mode: "broadcast" | "changelog"
  // -------------------------------------------------------------
  const [studioMode, setStudioMode] = useState<"broadcast" | "changelog">("broadcast");
  const [previewDevice, setPreviewDevice] = useState<"web" | "launcher" | "mobile">("web");
  const [previewLang, setPreviewLang] = useState<"en" | "ar">("en");

  // Release Policy State
  const [releaseInfo, setReleaseInfo] = useState<ReleaseInfo>({
    version: "v1.0.0",
    releaseDate: "2026-08-21",
    installerUrl: "https://sir-modpack.web.app/share/SIR_ModPack.exe",
    bundleUrl: "https://github.com/sir-modpack/sir-modpack-public/releases/download/v1.0.0/SIR_Offline_Bundle_1.1GB.zip",
    isMandatory: false,
    changelog: [
      "Official Master Genesis v1.0.0 Release",
      "Dual Modern 26.2 (Fabric) & Legacy 1.8.9 (Forge) Engines",
      "2048 HD Volumetric SIR Shaders & 32x POM 3D Bump Textures",
      "InGameAccountSwitcher (IAS) with Offline / Cracked & Official Mojang Support",
      "Hardware Power Governor in Silent Installer"
    ]
  });
  const [releaseSuccess, setReleaseSuccess] = useState(false);

  // -------------------------------------------------------------
  // 1. Realtime Broadcast State (Bilingual)
  // -------------------------------------------------------------
  const [broadcastDraft, setBroadcastDraft] = useState<BroadcastMessage>({
    active: true,
    type: "update",
    version: "",
    category: "",
    title: "",
    titleAr: "",
    message: "",
    messageAr: "",
    buttonLabel: "",
    buttonLabelAr: "",
    buttonUrl: ""
  });
  const [liveBroadcast, setLiveBroadcast] = useState<BroadcastMessage | null>(null);
  const [broadcastHistory, setBroadcastHistory] = useState<BroadcastMessage[]>([]);
  const [customAiPrompt, setCustomAiPrompt] = useState("");
  const [aiTone, setAiTone] = useState<"hype" | "professional" | "urgent" | "bilingual">("hype");
  const [isPolishing, setIsPolishing] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [isBroadcasting, setIsBroadcasting] = useState(false);

  // -------------------------------------------------------------
  // 2. Dynamic Changelog Publisher State (Bilingual)
  // -------------------------------------------------------------
  const [changelogList, setChangelogList] = useState<ChangelogEntry[]>([]);
  const [loadingChangelogs, setLoadingChangelogs] = useState(false);
  const [isPublishingChangelog, setIsPublishingChangelog] = useState(false);
  
  const [changelogDraft, setChangelogDraft] = useState<ChangelogEntry>({
    version: "",
    date: "",
    dateAr: "",
    tag: "",
    tagAr: "",
    headline: "",
    headlineAr: "",
    buttonLabel: "",
    buttonLabelAr: "",
    buttonUrl: "",
    categories: []
  });
  const [rawNotesInput, setRawNotesInput] = useState("");
  const [editingChangelogId, setEditingChangelogId] = useState<string | null>(null);
  const [editingBroadcastId, setEditingBroadcastId] = useState<string | null>(null);

  // Load initial data and listeners
  useEffect(() => {
    // 1. Live Presence Listener
    const unsubPresence = subscribeToLivePresence((count) => {
      setLiveUsers(count);
    });

    // 2. Download Counter Listener
    const unsubDownloads = subscribeToDownloads((data) => {
      setDownloads(data);
    });

    // 3. Live Broadcast Listener
    const unsubBroadcast = subscribeToBroadcast((msg) => {
      setLiveBroadcast(msg);
      if (msg && msg.active) {
        setBroadcastDraft(prev => ({
          ...prev,
          ...msg
        }));
        setBroadcastHistory(prev => {
          if (!prev.some(b => b.title === msg.title)) {
            return [msg, ...prev].slice(0, 10);
          }
          return prev;
        });
      }
    });

    // 4. Initial Release Info
    getLatestRelease().then((rel) => {
      if (rel) {
        setReleaseInfo((prev) => ({
          ...prev,
          ...rel
        }));
      }
    });

    // 5. Initial Error Reports & Changelogs
    loadReports();
    loadChangelogs();

    return () => {
      unsubPresence();
      unsubDownloads();
      unsubBroadcast();
    };
  }, []);

  const loadReports = async () => {
    setLoadingReports(true);
    try {
      const reports = await fetchErrorReports(30);
      setErrorReports(reports);
    } catch (err) {
      console.error("Error loading reports:", err);
    } finally {
      setLoadingReports(false);
    }
  };

  const loadChangelogs = async () => {
    setLoadingChangelogs(true);
    try {
      const entries = await fetchChangelogEntries();
      setChangelogList(entries);
    } catch (err) {
      console.error("Error loading changelogs:", err);
    } finally {
      setLoadingChangelogs(false);
    }
  };

  const handleRefreshAll = async () => {
    setIsRefreshing(true);
    try {
      await loadReports();
      await loadChangelogs();
      const rel = await getLatestRelease();
      if (rel) {
        setReleaseInfo((prev) => ({ ...prev, ...rel }));
      }
      showToast("Mission Control synchronized with Firebase live state", "success");
    } finally {
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  const handleResetAnalytics = () => {
    setShowResetConfirmModal(true);
  };

  const executeReset = async () => {
    setIsResetting(true);
    try {
      await resetAllAnalytics();
      setDownloads({ installer: 0, bundle: 0 });
      setResetSuccess(true);
      showToast("All download telemetry counters have been reset to 0!", "success");
      setTimeout(() => setResetSuccess(false), 3000);
    } catch (err: any) {
      showToast("Failed to reset analytics: " + err?.message, "error");
    } finally {
      setIsResetting(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: "open" | "investigating" | "resolved") => {
    try {
      await updateErrorReportStatus(id, newStatus);
      setErrorReports(prev => prev.map(r => r.id === id ? { ...r, status: newStatus } : r));
      if (selectedReport && selectedReport.id === id) {
        setSelectedReport(prev => prev ? { ...prev, status: newStatus } : null);
      }
      showToast(`Report status updated to ${newStatus}`, "success");
    } catch (err: any) {
      showToast("Failed to update status: " + (err?.message || err), "error");
    }
  };

  // AI Polish Broadcast Handler
  const handlePolishBroadcastAI = async () => {
    if (!broadcastDraft.title && !broadcastDraft.message && !customAiPrompt) {
      showToast("Please enter a title, message, or custom AI prompt to polish.", "error");
      return;
    }

    setIsPolishing(true);
    try {
      const polished = await polishAnnouncementWithAI(
        {
          title: broadcastDraft.title,
          message: broadcastDraft.message
        },
        customAiPrompt,
        aiTone
      );

      setBroadcastDraft(prev => ({
        ...prev,
        title: polished.title,
        message: polished.message,
        type: polished.type
      }));

      showToast("Broadcast announcement polished with Gemini AI!", "success");
    } catch (err: any) {
      showToast("AI Polish failed: " + err?.message, "error");
    } finally {
      setIsPolishing(false);
    }
  };

  // AI Auto-Translate Broadcast to Arabic
  const handleTranslateBroadcastAI = async () => {
    if (!broadcastDraft.title && !broadcastDraft.message) {
      showToast("Please write English text first to translate.", "error");
      return;
    }

    setIsTranslating(true);
    try {
      const tr = await translateBroadcastToArabic({
        title: broadcastDraft.title,
        message: broadcastDraft.message,
        buttonLabel: broadcastDraft.buttonLabel
      });

      setBroadcastDraft(prev => ({
        ...prev,
        titleAr: tr.titleAr,
        messageAr: tr.messageAr,
        buttonLabelAr: tr.buttonLabelAr || prev.buttonLabelAr
      }));

      showToast("Translated announcement to Arabic successfully!", "success");
    } catch (err: any) {
      showToast("Translation failed: " + err?.message, "error");
    } finally {
      setIsTranslating(false);
    }
  };

  // AI Polish Changelog Handler
  const handlePolishChangelogAI = async () => {
    const rawNotes = rawNotesInput.trim() || changelogDraft.categories.map(c => c.title + ":\n" + c.items.join("\n")).join("\n\n");
    if (!rawNotes && !customAiPrompt) {
      showToast("Please enter notes or custom instructions for AI.", "error");
      return;
    }

    setIsPolishing(true);
    try {
      const polished = await polishChangelogWithAI(
        {
          version: changelogDraft.version,
          headline: changelogDraft.headline,
          rawNotes: rawNotes
        },
        customAiPrompt
      );

      setChangelogDraft(prev => ({
        ...prev,
        headline: polished.headline,
        categories: polished.categories,
        buttonLabel: polished.buttonLabel || prev.buttonLabel
      }));

      showToast("Changelog categories and notes polished with Gemini AI!", "success");
    } catch (err: any) {
      showToast("AI Changelog Polish failed: " + err?.message, "error");
    } finally {
      setIsPolishing(false);
    }
  };

  // AI Auto-Translate Changelog to Arabic
  const handleTranslateChangelogAI = async () => {
    setIsTranslating(true);
    try {
      const tr = await translateChangelogToArabic({
        headline: changelogDraft.headline,
        tag: changelogDraft.tag,
        buttonLabel: changelogDraft.buttonLabel,
        categories: changelogDraft.categories.map(c => ({ title: c.title, items: c.items }))
      });

      setChangelogDraft(prev => ({
        ...prev,
        headlineAr: tr.headlineAr,
        tagAr: tr.tagAr,
        buttonLabelAr: tr.buttonLabelAr,
        categories: tr.categories
      }));

      showToast("Full changelog translated to Arabic!", "success");
    } catch (err: any) {
      showToast("Changelog translation failed: " + err?.message, "error");
    } finally {
      setIsTranslating(false);
    }
  };

  // 1-Click Pre-Fill Master v1.0.0 Genesis Notes (Bilingual)
  const handlePreFillGenesisChangelog = () => {
    const genesis = DEFAULT_MASTER_CHANGELOG[0];
    setChangelogDraft({
      version: genesis.version,
      date: genesis.date,
      dateAr: genesis.dateAr,
      tag: genesis.tag,
      tagAr: genesis.tagAr,
      headline: genesis.headline,
      headlineAr: genesis.headlineAr,
      buttonLabel: genesis.buttonLabel,
      buttonLabelAr: genesis.buttonLabelAr,
      buttonUrl: genesis.buttonUrl,
      categories: genesis.categories
    });
    setRawNotesInput("");
    showToast("Loaded official bilingual v1.0.0 Genesis Gold changelog template!", "success");
  };

  // Publish Broadcast Handler
  const handlePublishBroadcast = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!broadcastDraft.title || !broadcastDraft.message) {
      showToast("Please provide both a title and message before broadcasting.", "error");
      return;
    }

    setIsBroadcasting(true);
    try {
      await publishBroadcastMessage({
        ...broadcastDraft,
        active: true
      });
      setBroadcastHistory(prev => [broadcastDraft, ...prev.filter(b => b.title !== broadcastDraft.title)].slice(0, 10));
      showToast("Global announcement broadcasted in English & Arabic to all active clients!", "success");
    } catch (err: any) {
      showToast("Broadcast failed: " + err?.message, "error");
    } finally {
      setIsBroadcasting(false);
    }
  };

  // Dismiss Broadcast Handler
  const handleDismissBroadcast = async () => {
    try {
      await dismissBroadcastMessage();
      showToast("Active broadcast dismissed from all clients.", "success");
    } catch (err: any) {
      showToast("Failed to dismiss broadcast: " + err?.message, "error");
    }
  };

  // Publish Dynamic Changelog Handler (Preserves original date if editing)
  const handlePublishChangelog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!changelogDraft.version || !changelogDraft.headline) {
      showToast("Please provide a version and headline for the changelog.", "error");
      return;
    }

    setIsPublishingChangelog(true);
    try {
      const isEdit = Boolean(editingChangelogId);
      const entryToSave: ChangelogEntry = {
        ...changelogDraft,
        id: editingChangelogId || changelogDraft.id || `changelog_${Date.now()}`
      };
      
      await publishChangelogEntry(entryToSave, isEdit);
      await loadChangelogs();
      
      if (isEdit) {
        showToast(`✓ Updated '${changelogDraft.version}' without altering its original publish date (${changelogDraft.date || "original date"})!`, "success");
        setEditingChangelogId(null);
      } else {
        showToast(`✓ Changelog ${changelogDraft.version} published to live feed!`, "success");
      }
    } catch (err: any) {
      showToast("Failed to publish changelog: " + err?.message, "error");
    } finally {
      setIsPublishingChangelog(false);
    }
  };

  // Start Editing an existing changelog entry
  const handleStartEditChangelog = (entry: ChangelogEntry) => {
    setEditingChangelogId(entry.id || entry.version);
    setChangelogDraft({
      id: entry.id,
      version: entry.version,
      date: entry.date,
      dateAr: entry.dateAr || "",
      tag: entry.tag || "",
      tagAr: entry.tagAr || "",
      headline: entry.headline,
      headlineAr: entry.headlineAr || "",
      buttonLabel: entry.buttonLabel || "",
      buttonLabelAr: entry.buttonLabelAr || "",
      buttonUrl: entry.buttonUrl || "",
      categories: entry.categories || []
    });
    showToast(`Loaded '${entry.version}' for editing — original publish date (${entry.date}) is preserved!`, "success");
    window.scrollTo({ top: 400, behavior: "smooth" });
  };

  // Cancel Editing
  const handleCancelEditChangelog = () => {
    setEditingChangelogId(null);
    setChangelogDraft({
      version: "",
      date: "",
      dateAr: "",
      tag: "",
      tagAr: "",
      headline: "",
      headlineAr: "",
      buttonLabel: "",
      buttonLabelAr: "",
      buttonUrl: "",
      categories: []
    });
    showToast("Cancelled editing mode.", "success");
  };

  const handleDeleteChangelog = async (id: string) => {
    try {
      await deleteChangelogEntry(id);
      await loadChangelogs();
      showToast("Changelog entry removed from live feed.", "success");
    } catch (err: any) {
      showToast("Failed to delete changelog: " + err?.message, "error");
    }
  };

  // Move Category Up / Down
  const moveCategory = (index: number, direction: "up" | "down") => {
    const updated = [...changelogDraft.categories];
    const targetIdx = direction === "up" ? index - 1 : index + 1;
    if (targetIdx < 0 || targetIdx >= updated.length) return;
    const temp = updated[index];
    updated[index] = updated[targetIdx];
    updated[targetIdx] = temp;
    setChangelogDraft({ ...changelogDraft, categories: updated });
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-[#07090e] text-slate-900 dark:text-zinc-100 p-4 sm:p-8 font-sans selection:bg-[#00e5ff] selection:text-black transition-colors duration-200">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Top Breadcrumb & Actions */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-2.5 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 hover:border-cyan-500/50 rounded-2xl text-slate-600 dark:text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white transition-all cursor-pointer shadow-sm"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                  SIR Ecosystem Mission Control
                </h1>
                <span className="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-full">
                  Executive Cloud Console
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Real-Time Telemetry, AI Bilingual Studio & Multi-Platform Fleet Operations
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleResetAnalytics}
              disabled={isResetting}
              className="flex items-center gap-2 px-4 py-2 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-500/40 hover:border-red-400 text-xs font-bold text-red-600 dark:text-red-300 hover:text-red-700 dark:hover:text-red-200 rounded-2xl transition-all cursor-pointer shadow-sm disabled:opacity-50"
              title="Reset all download counters and analytics back to zero"
            >
              <RotateCcw className={`w-3.5 h-3.5 text-red-400 ${isResetting ? "animate-spin" : ""}`} />
              <span>{isResetting ? "Resetting..." : "Reset Analytics (0)"}</span>
            </button>

            <button
              onClick={handleRefreshAll}
              disabled={isRefreshing}
              className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 hover:border-cyan-500 text-xs font-semibold text-slate-700 dark:text-slate-700 dark:text-zinc-300 hover:text-slate-900 dark:hover:text-white rounded-2xl transition-all cursor-pointer shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isRefreshing ? "animate-spin" : ""}`} />
              <span>{isRefreshing ? "Refreshing..." : "Refresh Live Data"}</span>
            </button>

            <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
              <ShieldCheck className="w-4 h-4" />
              <span>Owner Authenticated</span>
            </span>
          </div>
        </div>

        {/* Global Reset Success Toast */}
        <div className={`transition-all duration-300 overflow-hidden ${resetSuccess ? "max-h-16 opacity-100" : "max-h-0 opacity-0"}`}>
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl text-emerald-400 text-xs font-bold flex items-center gap-2 shadow-sm">
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>All download analytics and telemetry counters have been successfully reset to 0!</span>
          </div>
        </div>

        {/* Real-time Telemetry Metrics Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* Live Connected Users */}
          <div className="p-5 bg-white dark:bg-zinc-950/80 border border-slate-200 dark:border-zinc-800 hover:border-emerald-500/40 rounded-3xl relative overflow-hidden transition-colors shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold font-mono tracking-wider uppercase text-cyan-400">
                Live Active Users
              </span>
              <div className="relative flex items-center justify-center w-6 h-6">
                <span className="w-3 h-3 bg-emerald-400 rounded-full animate-ping absolute" />
                <span className="w-3 h-3 bg-emerald-400 rounded-full" />
              </div>
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-black text-slate-900 dark:text-white">{liveUsers}</span>
              <span className="text-xs text-zinc-500 font-mono">connected</span>
            </div>
            <p className="mt-2 text-[11px] text-slate-500 dark:text-slate-500 dark:text-zinc-400">
              Real-time presence socket via Firebase RTDB
            </p>
          </div>

          {/* Installer Downloads */}
          <div className="p-5 bg-white dark:bg-zinc-950/80 border border-slate-200 dark:border-zinc-800 hover:border-cyan-500/40 rounded-3xl relative overflow-hidden transition-colors shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold font-mono tracking-wider uppercase text-slate-500 dark:text-zinc-400">
                Installer Downloads
              </span>
              <Download className="w-5 h-5 text-cyan-400" />
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-black text-slate-900 dark:text-white">{downloads.installer.toLocaleString()}</span>
              <span className="text-xs text-cyan-400 font-mono">RTDB Telemetry</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 dark:text-zinc-400">
                          <span>SIR_ModPack.exe</span>
              <span className="text-[10px] text-zinc-500 font-mono">Production Stream</span>
            </div>
          </div>

          {/* Full Standalone Bundle Downloads */}
          <div className="p-5 bg-white dark:bg-zinc-950/80 border border-slate-200 dark:border-zinc-800 hover:border-emerald-500/40 rounded-3xl relative overflow-hidden transition-colors shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold font-mono tracking-wider uppercase text-slate-500 dark:text-zinc-400">
                Offline Bundle (690 MB)
              </span>
              <Layers className="w-5 h-5 text-emerald-400" />
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-black text-slate-900 dark:text-white">{downloads.bundle.toLocaleString()}</span>
              <span className="text-xs text-emerald-400 font-mono">RTDB Telemetry</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 dark:text-zinc-400">
              <span>SIR_Offline_Bundle.zip</span>
              <span className="text-[10px] text-zinc-500 font-mono">Production Stream</span>
            </div>
          </div>

          {/* Error Diagnostics Count */}
          <div className="p-5 bg-white dark:bg-zinc-950/80 border border-slate-200 dark:border-zinc-800 hover:border-red-500/40 rounded-3xl relative overflow-hidden transition-colors shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold font-mono tracking-wider uppercase text-slate-500 dark:text-zinc-400">
                Diagnostic Reports
              </span>
              <AlertTriangle className="w-5 h-5 text-red-400" />
            </div>
            <div className="mt-4 flex items-baseline gap-2">
              <span className="text-4xl font-black text-slate-900 dark:text-white">{errorReports.length}</span>
              <span className="text-xs text-zinc-500 font-mono">in Firestore</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 dark:text-zinc-400">
              <span>{errorReports.filter(r => r.status === "open").length} open tickets</span>
              <span className="text-[10px] text-emerald-400 font-mono">Live Sync</span>
            </div>
          </div>
        </section>

        {/* ============================================================= */}
        {/* 🌟 UNIFIED BILINGUAL BROADCAST & CHANGELOG STUDIO             */}
        {/* ============================================================= */}
        <section className="p-6 sm:p-8 bg-white dark:bg-zinc-950/90 border border-slate-200 dark:border-cyan-500/40 rounded-3xl space-y-6 shadow-xl dark:shadow-[0_0_40px_rgba(0,229,255,0.1)]">
          
          {/* Header & Mode Selector Tabs */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-zinc-800">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-sm">
                {studioMode === "broadcast" ? <Radio className="w-6 h-6 animate-pulse" /> : <FileText className="w-6 h-6 text-emerald-400" />}
              </div>
              <div>
                <h2 className="text-lg sm:text-xl font-black text-slate-900 dark:text-white flex items-center gap-2">
                  <span>{studioMode === "broadcast" ? "AI Live Broadcast Studio" : "Dynamic Release & Changelog Engine"}</span>
                  <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-[10px] font-bold uppercase tracking-wider">
                    Gemini AI Pro • Multi-Device
                  </span>
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-500 dark:text-zinc-400">
                  {studioMode === "broadcast" 
                    ? "Broadcast instant alerts across Web, Mobile & Launcher News page simultaneously." 
                    : "Create, polish & publish official ecosystem changelogs to the public feed and launcher."}
                </p>
              </div>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="flex p-1 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800">
              <button
                type="button"
                onClick={() => setStudioMode("broadcast")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
                  studioMode === "broadcast"
                    ? "bg-cyan-500 text-black shadow-md"
                    : "text-slate-500 dark:text-zinc-400 hover:text-white"
                }`}
              >
                <Radio className="w-4 h-4" />
                <span>Live Broadcast</span>
              </button>

              <button
                type="button"
                onClick={() => setStudioMode("changelog")}
                className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-black transition-all cursor-pointer ${
                  studioMode === "changelog"
                    ? "bg-emerald-500 text-black shadow-md"
                    : "text-slate-500 dark:text-zinc-400 hover:text-white"
                }`}
              >
                <History className="w-4 h-4" />
                <span>Changelog Publisher</span>
              </button>
            </div>
          </div>

          {/* TAB 1: REAL-TIME BROADCAST ANNOUNCEMENT                     */}
          {/* =========================================================== */}
          {studioMode === "broadcast" && (
            <form onSubmit={handlePublishBroadcast} className="space-y-6">
              
              {/* Active Broadcast Status Banner */}
              {liveBroadcast && liveBroadcast.active ? (
                <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between gap-3 flex-wrap">
                  <div className="flex items-center gap-2.5 text-xs text-emerald-300 font-bold">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                    <span>Active Announcement: <strong>{liveBroadcast.title}</strong> (AR: <em>{liveBroadcast.titleAr || "None"}</em>)</span>
                  </div>
                  <button
                    type="button"
                    onClick={handleDismissBroadcast}
                    className="px-3.5 py-1.5 rounded-xl bg-red-950/60 hover:bg-red-900 border border-red-500/40 text-red-300 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Dismiss Active</span>
                  </button>
                </div>
              ) : null}

              {/* AI Polish & Auto-Translate Bar */}
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-zinc-900/90 border border-slate-200 dark:border-zinc-800 space-y-4 shadow-inner">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <label className="text-xs font-black uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    <span>Gemini AI Polish & Auto-Translator Engine</span>
                  </label>
                  
                  {/* Action Buttons */}
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={handleTranslateBroadcastAI}
                      disabled={isTranslating}
                      className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                    >
                      <Globe className={`w-3.5 h-3.5 ${isTranslating ? "animate-spin" : ""}`} />
                      <span>{isTranslating ? "Translating..." : "Auto-Translate to Arabic"}</span>
                    </button>

                    {/* Tone Selectors */}
                    <div className="flex items-center gap-1 p-0.5 rounded-xl bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-[11px] font-bold">
                      {(["hype", "professional", "urgent", "bilingual"] as const).map((tone) => (
                        <button
                          key={tone}
                          type="button"
                          onClick={() => setAiTone(tone)}
                          className={`px-2.5 py-1 rounded-lg capitalize transition-all cursor-pointer ${
                            aiTone === tone 
                              ? "bg-cyan-500 text-black font-black shadow-sm" 
                              : "text-slate-500 dark:text-zinc-400 hover:text-white"
                          }`}
                        >
                          {tone === "hype" ? "⚡ Hype" : tone === "professional" ? "💼 Pro" : tone === "urgent" ? "🚨 Urgent" : "🌍 AR/EN"}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Custom AI Prompt Input Field */}
                <div className="relative">
                  <input
                    type="text"
                    value={customAiPrompt}
                    onChange={(e) => setCustomAiPrompt(e.target.value)}
                    placeholder="Custom AI prompt (e.g. 'Announce new shader caustics in Arabic and English with emojis')..."
                    className="w-full pl-4 pr-32 py-3 rounded-xl bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-cyan-400 transition-colors"
                  />
                  <button
                    type="button"
                    onClick={handlePolishBroadcastAI}
                    disabled={isPolishing}
                    className="absolute right-1.5 top-1.5 bottom-1.5 px-4 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-black text-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shadow-sm"
                  >
                    <Wand2 className={`w-3.5 h-3.5 ${isPolishing ? "animate-spin" : ""}`} />
                    <span>{isPolishing ? "Polishing..." : "Polish with AI"}</span>
                  </button>
                </div>
              </div>

              {/* Version & Subject / Category */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Target Version (Optional)
                  </label>
                  <input
                    type="text"
                    value={broadcastDraft.version || ""}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, version: e.target.value })}
                    placeholder="e.g. v1.0.0, v1.0.1"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-cyan-400"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Subject / Category
                  </label>
                  <input
                    type="text"
                    value={broadcastDraft.category || ""}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, category: e.target.value })}
                    placeholder="e.g. Master Release, Shaders, PvP Engine"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-cyan-400"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Alert Severity
                  </label>
                  <select
                    value={broadcastDraft.type}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, type: e.target.value as any })}
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-cyan-400 cursor-pointer"
                  >
                    <option value="info">🔵 Information</option>
                    <option value="update">🚀 New Update / Release</option>
                    <option value="warning">🟡 Maintenance / Notice</option>
                    <option value="event">🌟 Community Event</option>
                  </select>
                </div>
              </div>

              {/* Bilingual Title Fields: English & Arabic */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider flex items-center justify-between">
                    <span>Title (English)</span>
                    <span className="text-[10px] text-cyan-400 font-mono">LTR</span>
                  </label>
                  <input
                    type="text"
                    value={broadcastDraft.title}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, title: e.target.value })}
                    placeholder="e.g. ⚡ Critical Update: SIR ModPack v1.0.0 is Live!"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-cyan-400"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center justify-between">
                    <span>العنوان (باللغة العربية)</span>
                    <span className="text-[10px] text-emerald-400 font-mono">RTL</span>
                  </label>
                  <input
                    type="text"
                    dir="rtl"
                    value={broadcastDraft.titleAr || ""}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, titleAr: e.target.value })}
                    placeholder="مثال: ⚡ إطلاق النسخة الذهبية الرسمية v1.0.0 لمنظومة SIR"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-emerald-400 text-right"
                  />
                </div>
              </div>

              {/* Bilingual Message Body Fields: English & Arabic */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Message Body (English)
                  </label>
                  <textarea
                    value={broadcastDraft.message}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, message: e.target.value })}
                    rows={3}
                    placeholder="Write English broadcast text..."
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-cyan-400 resize-none"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-emerald-400 uppercase tracking-wider text-right block">
                    نص الإعلان (باللغة العربية)
                  </label>
                  <textarea
                    dir="rtl"
                    value={broadcastDraft.messageAr || ""}
                    onChange={(e) => setBroadcastDraft({ ...broadcastDraft, messageAr: e.target.value })}
                    rows={3}
                    placeholder="اكتب نص الإعلان باللغة العربية..."
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-emerald-400 resize-none text-right"
                  />
                </div>
              </div>

              {/* Bilingual Custom Action Button & Link */}
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-zinc-900/60 border border-slate-200 dark:border-zinc-800 space-y-3">
                <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Link2 className="w-4 h-4" />
                  <span>Call-to-Action Button (Bilingual & Optional)</span>
                </span>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="text-[11px] text-slate-500 dark:text-zinc-400 font-mono">Button Text (EN)</label>
                    <input
                      type="text"
                      value={broadcastDraft.buttonLabel || ""}
                      onChange={(e) => setBroadcastDraft({ ...broadcastDraft, buttonLabel: e.target.value })}
                      placeholder="e.g. ⚡ Download Installer"
                      className="w-full mt-1 px-3.5 py-2.5 rounded-xl bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-cyan-400"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] text-emerald-400 font-mono">نص الزر (العربية)</label>
                    <input
                      type="text"
                      dir="rtl"
                      value={broadcastDraft.buttonLabelAr || ""}
                      onChange={(e) => setBroadcastDraft({ ...broadcastDraft, buttonLabelAr: e.target.value })}
                      placeholder="مثال: ⚡ تحميل المثبت"
                      className="w-full mt-1 px-3.5 py-2.5 rounded-xl bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-emerald-400 text-right"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] text-slate-500 dark:text-zinc-400 font-mono">Button Target URL</label>
                    <input
                      type="text"
                      value={broadcastDraft.buttonUrl || ""}
                      onChange={(e) => setBroadcastDraft({ ...broadcastDraft, buttonUrl: e.target.value })}
                      placeholder="e.g. /#downloads, https://github.com/..."
                      className="w-full mt-1 px-3.5 py-2.5 rounded-xl bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-cyan-400"
                    />
                  </div>
                </div>
              </div>

              {/* 🌟 MULTI-DEVICE REALTIME VISUAL SIMULATOR */}
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-zinc-900/50 border border-slate-200 dark:border-zinc-800 space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className="text-xs font-black uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                    <Eye className="w-4 h-4" />
                    <span>Real-time Multi-Platform Output Simulator</span>
                  </span>

                  {/* Simulator Controls */}
                  <div className="flex items-center gap-2">
                    {/* Device Selector */}
                    <div className="flex p-0.5 rounded-xl bg-slate-100 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-[11px]">
                      <button
                        type="button"
                        onClick={() => setPreviewDevice("web")}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-black transition-all cursor-pointer ${
                          previewDevice === "web" ? "bg-cyan-500 text-slate-950 shadow-xs" : "text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
                        }`}
                      >
                        <Globe className="w-3 h-3" /> Web Ribbon
                      </button>
                      <button
                        type="button"
                        onClick={() => setPreviewDevice("launcher")}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-black transition-all cursor-pointer ${
                          previewDevice === "launcher" ? "bg-cyan-500 text-slate-950 shadow-xs" : "text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
                        }`}
                      >
                        <Monitor className="w-3 h-3" /> Launcher News
                      </button>
                      <button
                        type="button"
                        onClick={() => setPreviewDevice("mobile")}
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-black transition-all cursor-pointer ${
                          previewDevice === "mobile" ? "bg-cyan-500 text-slate-950 shadow-xs" : "text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"
                        }`}
                      >
                        <Smartphone className="w-3 h-3" /> Mobile Card
                      </button>
                    </div>

                    {/* Lang Switcher */}
                    <div className="flex p-0.5 rounded-xl bg-slate-100 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-[11px]">
                      <button
                        type="button"
                        onClick={() => setPreviewLang("en")}
                        className={`px-2.5 py-1 rounded-lg font-black transition-all cursor-pointer ${previewLang === "en" ? "bg-cyan-500 text-slate-950 shadow-xs" : "text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"}`}
                      >
                        EN
                      </button>
                      <button
                        type="button"
                        onClick={() => setPreviewLang("ar")}
                        className={`px-2.5 py-1 rounded-lg font-black transition-all cursor-pointer ${previewLang === "ar" ? "bg-cyan-500 text-slate-950 shadow-xs" : "text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white"}`}
                      >
                        AR
                      </button>
                    </div>
                  </div>
                </div>

                {/* Simulation Canvas */}
                <div className="p-4 rounded-2xl bg-slate-100 dark:bg-black/60 border border-slate-200 dark:border-zinc-800/80 flex items-center justify-center min-h-[100px] shadow-inner">
                  {previewDevice === "web" && (
                    <div
                      dir={previewLang === "ar" ? "rtl" : "ltr"}
                      className="w-full p-3.5 rounded-xl bg-gradient-to-r from-cyan-600 via-emerald-600 to-cyan-600 text-white text-xs font-bold flex items-center justify-between shadow-md flex-wrap gap-2"
                    >
                      <div className="flex items-center gap-2">
                        <Radio className="w-3.5 h-3.5 animate-pulse shrink-0 text-white" />
                        <span className="text-white drop-shadow-xs">
                          {broadcastDraft.version && <strong className="px-1.5 py-0.5 rounded bg-black/30 mr-1.5 font-mono text-[10px] text-cyan-200">{broadcastDraft.version}</strong>}
                          <strong>
                            {previewLang === "ar" 
                              ? (broadcastDraft.titleAr || "إعلان منظومة SIR الحي") 
                              : (broadcastDraft.title || "Live SIR Ecosystem Alert")}:
                          </strong>{" "}
                          {previewLang === "ar" 
                            ? (broadcastDraft.messageAr || "هذا نموذج لمعاينة شريط الإعلانات المباشر على الموقع الرسمي.") 
                            : (broadcastDraft.message || "This is a real-time preview of your broadcast banner on the official web platform.")}
                        </span>
                      </div>
                      {((previewLang === "ar" && (broadcastDraft.buttonLabelAr || broadcastDraft.buttonLabel)) || broadcastDraft.buttonLabel) && (
                        <span className="px-2.5 py-1 rounded-lg bg-black/80 text-white text-[10px] font-black shrink-0 border border-white/30 shadow-xs">
                          {previewLang === "ar" && broadcastDraft.buttonLabelAr ? broadcastDraft.buttonLabelAr : (broadcastDraft.buttonLabel || "Action Link")}
                        </span>
                      )}
                    </div>
                  )}

                  {previewDevice === "launcher" && (
                    <div
                      dir={previewLang === "ar" ? "rtl" : "ltr"}
                      className="w-full max-w-lg p-4 rounded-2xl bg-white dark:bg-[#0e131d] border border-slate-200 dark:border-cyan-500/40 text-slate-900 dark:text-white space-y-3 shadow-xl"
                    >
                      <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-zinc-800">
                        <span className="text-xs font-black text-cyan-600 dark:text-cyan-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Monitor className="w-3.5 h-3.5" />
                          <span>SIR Launcher News Feed</span>
                        </span>
                        <span className="text-[10px] font-mono text-slate-400 dark:text-zinc-500">Live Socket</span>
                      </div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                        {previewLang === "ar" ? (broadcastDraft.titleAr || "عنوان الإشعار للّانشر") : (broadcastDraft.title || "Launcher Notification Title")}
                      </h4>
                      <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                        {previewLang === "ar" ? (broadcastDraft.messageAr || "نص الإعلان الذي سيظهر لجميع لاعبي ومستخدمي لانشر SIR.") : (broadcastDraft.message || "Notification text that will be received by all desktop SIR Launcher players.")}
                      </p>
                      {((previewLang === "ar" && (broadcastDraft.buttonLabelAr || broadcastDraft.buttonLabel)) || broadcastDraft.buttonLabel) && (
                        <span className="inline-block px-3 py-1.5 rounded-lg bg-cyan-500 text-slate-950 font-black text-xs shadow-xs">
                          {previewLang === "ar" && broadcastDraft.buttonLabelAr ? broadcastDraft.buttonLabelAr : (broadcastDraft.buttonLabel || "Action Button")}
                        </span>
                      )}
                    </div>
                  )}

                  {previewDevice === "mobile" && (
                    <div
                      dir={previewLang === "ar" ? "rtl" : "ltr"}
                      className="w-full max-w-xs p-4 rounded-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 text-slate-900 dark:text-white space-y-2.5 shadow-xl"
                    >
                      <div className="flex items-center gap-2 text-[10px] font-bold text-cyan-600 dark:text-cyan-400">
                        <Bell className="w-3 h-3" />
                        <span>SIR MODPACK ALERT</span>
                      </div>
                      <p className="text-xs font-bold text-slate-900 dark:text-white">
                        {previewLang === "ar" ? (broadcastDraft.titleAr || "إشعار الجوال") : (broadcastDraft.title || "Mobile Push Title")}
                      </p>
                      <p className="text-[11px] text-slate-600 dark:text-zinc-400 line-clamp-2">
                        {previewLang === "ar" ? (broadcastDraft.messageAr || "نص رسالة الإشعار الفوري للمستخدمين.") : (broadcastDraft.message || "Push notification payload sent across clients.")}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Publish Action Button */}
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={isBroadcasting}
                  className="flex-1 py-4 px-6 rounded-2xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-black text-sm shadow-lg hover:shadow-cyan-500/20 transition-all cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <Send className={`w-4 h-4 ${isBroadcasting ? "animate-spin" : ""}`} />
                  <span>{isBroadcasting ? "Broadcasting to RTDB & Launcher..." : "🚀 Publish Live Global Broadcast (Web & Launcher)"}</span>
                </button>
              </div>

              {/* Broadcast Archive / History */}
              {broadcastHistory.length > 0 && (
                <div className="pt-4 border-t border-zinc-800 space-y-3">
                  <span className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Recent Broadcast Archive (1-Click Re-Publish):</span>
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {broadcastHistory.map((b, idx) => (
                      <div key={idx} className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 flex items-center justify-between gap-3">
                        <div className="truncate">
                          <p className="text-xs font-bold text-white truncate">{b.title}</p>
                          <p className="text-[10px] text-slate-500 dark:text-zinc-400 truncate">{b.message}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => {
                            setBroadcastDraft(b);
                            showToast("Loaded broadcast template from history!", "success");
                          }}
                          className="px-2.5 py-1 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-cyan-400 text-xs font-bold transition-all shrink-0 cursor-pointer"
                        >
                          Load
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </form>
          )}

          {/* =========================================================== */}
          {/* TAB 2: DYNAMIC CHANGELOG PUBLISHER                          */}
          {/* =========================================================== */}
          {studioMode === "changelog" && (
            <form onSubmit={handlePublishChangelog} className="space-y-6">
              
              {/* Editing Notification Banner */}
              {editingChangelogId && (
                <div className="p-4 rounded-2xl bg-amber-500/15 border border-amber-500/40 text-amber-300 text-xs flex items-center justify-between shadow-lg">
                  <div className="flex items-center gap-2.5">
                    <span className="text-base">✏️</span>
                    <div>
                      <span className="font-bold">Editing Active Changelog: </span>
                      <span className="font-mono">{changelogDraft.version}</span>
                      <p className="text-[11px] text-amber-200/80">
                        Applying edits will <strong>preserve the original publication date</strong> ({changelogDraft.date || "August 2026"}) without overwriting it!
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleCancelEditChangelog}
                    className="px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 text-xs font-bold transition-all cursor-pointer shrink-0"
                  >
                    Cancel Edit
                  </button>
                </div>
              )}

              {/* Quick Template & AI Polish Toolbar */}
              <div className="p-5 rounded-2xl bg-slate-50 dark:bg-zinc-900/90 border border-slate-200 dark:border-zinc-800 space-y-4 shadow-inner">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <label className="text-xs font-black uppercase tracking-wider text-emerald-400 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    <span>Changelog AI Architect & Bilingual Templates</span>
                  </label>

                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={handleTranslateChangelogAI}
                      disabled={isTranslating}
                      className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                    >
                      <Globe className={`w-3.5 h-3.5 ${isTranslating ? "animate-spin" : ""}`} />
                      <span>{isTranslating ? "Translating Changelog..." : "Auto-Translate to Arabic"}</span>
                    </button>

                    <button
                      type="button"
                      onClick={handlePreFillGenesisChangelog}
                      className="px-3.5 py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      <span>Pre-Fill v1.0.0 Genesis (Bilingual)</span>
                    </button>
                  </div>
                </div>

                <div className="relative">
                  <input
                    type="text"
                    value={customAiPrompt}
                    onChange={(e) => setCustomAiPrompt(e.target.value)}
                    placeholder="Custom AI instruction (e.g. 'Format my raw notes into 4 clean categories with icons in English and Arabic')..."
                    className="w-full pl-4 pr-36 py-3 rounded-xl bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-emerald-400 transition-colors"
                  />
                  <button
                    type="button"
                    onClick={handlePolishChangelogAI}
                    disabled={isPolishing}
                    className="absolute right-1.5 top-1.5 bottom-1.5 px-4 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-black text-xs transition-all flex items-center gap-1.5 cursor-pointer disabled:opacity-50 shadow-sm"
                  >
                    <Wand2 className={`w-3.5 h-3.5 ${isPolishing ? "animate-spin" : ""}`} />
                    <span>{isPolishing ? "Structuring..." : "AI Format Notes"}</span>
                  </button>
                </div>
              </div>

              {/* Version, Date & Milestone Tag (Bilingual) */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Release Version
                  </label>
                  <input
                    type="text"
                    value={changelogDraft.version}
                    onChange={(e) => setChangelogDraft({ ...changelogDraft, version: e.target.value })}
                    placeholder="e.g. 1.0.0, 1.1.0"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-emerald-400"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Release Date (EN / AR)
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={changelogDraft.date}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, date: e.target.value })}
                      placeholder="August 2026"
                      className="w-1/2 px-3 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs text-slate-900 dark:text-white outline-none focus:border-emerald-400"
                      required
                    />
                    <input
                      type="text"
                      dir="rtl"
                      value={changelogDraft.dateAr || ""}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, dateAr: e.target.value })}
                      placeholder="أغسطس 2026"
                      className="w-1/2 px-3 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs text-slate-900 dark:text-white outline-none focus:border-emerald-400 text-right"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Milestone Tag (EN / AR)
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={changelogDraft.tag}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, tag: e.target.value })}
                      placeholder="Official Milestone"
                      className="w-1/2 px-3 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs text-slate-900 dark:text-white outline-none focus:border-emerald-400"
                    />
                    <input
                      type="text"
                      dir="rtl"
                      value={changelogDraft.tagAr || ""}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, tagAr: e.target.value })}
                      placeholder="الإطلاق الرسمي"
                      className="w-1/2 px-3 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-xs text-slate-900 dark:text-white outline-none focus:border-emerald-400 text-right"
                    />
                  </div>
                </div>
              </div>

              {/* Release Headline Subtitle (EN & AR) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Release Headline (English)
                  </label>
                  <input
                    type="text"
                    value={changelogDraft.headline}
                    onChange={(e) => setChangelogDraft({ ...changelogDraft, headline: e.target.value })}
                    placeholder="e.g. The Complete Cross-Engine Ecosystem Release"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-emerald-400"
                    required
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-emerald-400 uppercase tracking-wider text-right block">
                    العنوان الرئيسي للإصدار (باللغة العربية)
                  </label>
                  <input
                    type="text"
                    dir="rtl"
                    value={changelogDraft.headlineAr || ""}
                    onChange={(e) => setChangelogDraft({ ...changelogDraft, headlineAr: e.target.value })}
                    placeholder="مثال: الإطلاق الشامل لمنظومة ماين كرافت فائقة الأداء"
                    className="w-full px-4 py-3 rounded-2xl bg-slate-100 dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 text-sm text-slate-900 dark:text-white outline-none focus:border-emerald-400 text-right"
                  />
                </div>
              </div>

              {/* Bilingual Custom Button Link for Changelog */}
              <div className="p-4 rounded-2xl bg-zinc-900/60 border border-zinc-800 space-y-3">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Link2 className="w-4 h-4" />
                  <span>Download / Action Button for this Changelog (Bilingual)</span>
                </span>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="text-[11px] text-slate-500 dark:text-zinc-400 font-mono">Button Label (EN)</label>
                    <input
                      type="text"
                      value={changelogDraft.buttonLabel || ""}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, buttonLabel: e.target.value })}
                      placeholder="e.g. ⚡ Download Installer v1.0.0"
                      className="w-full mt-1 px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-xs text-white outline-none focus:border-emerald-400"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] text-emerald-400 font-mono">نص الزر (العربية)</label>
                    <input
                      type="text"
                      dir="rtl"
                      value={changelogDraft.buttonLabelAr || ""}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, buttonLabelAr: e.target.value })}
                      placeholder="مثال: ⚡ تحميل المثبت v1.0.0"
                      className="w-full mt-1 px-3.5 py-2.5 rounded-xl bg-white dark:bg-zinc-950 border border-slate-300 dark:border-zinc-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-zinc-500 outline-none focus:border-emerald-400 text-right"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] text-slate-500 dark:text-zinc-400 font-mono">Button Target URL</label>
                    <input
                      type="text"
                      value={changelogDraft.buttonUrl || ""}
                      onChange={(e) => setChangelogDraft({ ...changelogDraft, buttonUrl: e.target.value })}
                      placeholder="e.g. /#downloads, https://github.com/..."
                      className="w-full mt-1 px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-xs text-white outline-none focus:border-emerald-400"
                    />
                  </div>
                </div>
              </div>

              {/* Structured Categorized Categories Preview / Editor with Reordering */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
                    Categorized Sections ({changelogDraft.categories.length})
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setChangelogDraft({
                        ...changelogDraft,
                        categories: [
                          ...changelogDraft.categories,
                          { 
                            title: "✨ New Category", 
                            titleAr: "✨ قسم جديد",
                            items: ["Added new optimization feature."],
                            itemsAr: ["إضافة ميزة تحسين جديدة."]
                          }
                        ]
                      });
                    }}
                    className="px-3.5 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-emerald-400 text-xs font-bold hover:bg-zinc-800 transition-all cursor-pointer flex items-center gap-1.5"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Section</span>
                  </button>
                </div>

                <div className="space-y-4">
                  {changelogDraft.categories.map((cat, cIdx) => (
                    <div key={cIdx} className="p-4 rounded-2xl bg-zinc-900/80 border border-zinc-800 space-y-3">
                      
                      {/* Bilingual Category Titles & Reordering */}
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-1">
                          <button
                            type="button"
                            disabled={cIdx === 0}
                            onClick={() => moveCategory(cIdx, "up")}
                            className="p-1 rounded-lg bg-zinc-950 text-slate-500 dark:text-zinc-400 hover:text-white disabled:opacity-30 cursor-pointer"
                            title="Move Up"
                          >
                            <ChevronUp className="w-3.5 h-3.5" />
                          </button>
                          <button
                            type="button"
                            disabled={cIdx === changelogDraft.categories.length - 1}
                            onClick={() => moveCategory(cIdx, "down")}
                            className="p-1 rounded-lg bg-zinc-950 text-slate-500 dark:text-zinc-400 hover:text-white disabled:opacity-30 cursor-pointer"
                            title="Move Down"
                          >
                            <ChevronDown className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        <input
                          type="text"
                          value={cat.title}
                          onChange={(e) => {
                            const updated = [...changelogDraft.categories];
                            updated[cIdx].title = e.target.value;
                            setChangelogDraft({ ...changelogDraft, categories: updated });
                          }}
                          placeholder="Category Title (English)"
                          className="flex-1 min-w-[180px] px-3 py-2 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-xs font-bold text-white outline-none focus:border-emerald-400"
                        />

                        <input
                          type="text"
                          dir="rtl"
                          value={cat.titleAr || ""}
                          onChange={(e) => {
                            const updated = [...changelogDraft.categories];
                            updated[cIdx].titleAr = e.target.value;
                            setChangelogDraft({ ...changelogDraft, categories: updated });
                          }}
                          placeholder="عنوان القسم (بالعربية)"
                          className="flex-1 min-w-[180px] px-3 py-2 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-xs font-bold text-white outline-none focus:border-emerald-400 text-right"
                        />

                        <button
                          type="button"
                          onClick={() => {
                            const updated = changelogDraft.categories.filter((_, idx) => idx !== cIdx);
                            setChangelogDraft({ ...changelogDraft, categories: updated });
                          }}
                          className="p-2 text-slate-500 dark:text-zinc-400 hover:text-red-400 transition-colors cursor-pointer"
                          title="Remove Category"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {/* Bilingual Items Textareas */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="text-[10px] font-mono text-zinc-500 uppercase">Items (English - 1 per line)</label>
                          <textarea
                            value={cat.items.join("\n")}
                            onChange={(e) => {
                              const updated = [...changelogDraft.categories];
                              updated[cIdx].items = e.target.value.split("\n").filter(Boolean);
                              setChangelogDraft({ ...changelogDraft, categories: updated });
                            }}
                            rows={3}
                            placeholder="English bullet points..."
                            className="w-full mt-1 px-3 py-2 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-xs text-slate-700 dark:text-zinc-300 outline-none focus:border-emerald-400 font-mono"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] font-mono text-emerald-500 uppercase text-right block">العناصر (عربي - عنصر لكل سطر)</label>
                          <textarea
                            dir="rtl"
                            value={(cat.itemsAr || []).join("\n")}
                            onChange={(e) => {
                              const updated = [...changelogDraft.categories];
                              updated[cIdx].itemsAr = e.target.value.split("\n").filter(Boolean);
                              setChangelogDraft({ ...changelogDraft, categories: updated });
                            }}
                            rows={3}
                            placeholder="النقاط باللغة العربية..."
                            className="w-full mt-1 px-3 py-2 rounded-xl bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 text-xs text-slate-700 dark:text-zinc-300 outline-none focus:border-emerald-400 font-mono text-right"
                          />
                        </div>
                      </div>

                    </div>
                  ))}
                </div>
              </div>

              {/* Publish Action Button */}
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={isPublishingChangelog}
                  className="flex-1 py-4 px-6 rounded-2xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-black font-black text-sm shadow-lg hover:shadow-emerald-500/20 transition-all cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <FileText className={`w-4 h-4 ${isPublishingChangelog ? "animate-spin" : ""}`} />
                  <span>{isPublishingChangelog ? "Publishing to Live Feed..." : `📜 Publish ${changelogDraft.version} to Bilingual Live Changelog`}</span>
                </button>
              </div>

              {/* Currently Published Live Changelogs Feed */}
              <div className="pt-6 border-t border-zinc-800 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-black text-white flex items-center gap-2">
                    <History className="w-4 h-4 text-emerald-400" />
                    <span>Published Changelogs History & Archive ({changelogList.length})</span>
                  </h3>
                  {editingChangelogId && (
                    <button
                      type="button"
                      onClick={handleCancelEditChangelog}
                      className="px-3 py-1 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/40 text-xs font-bold transition-all cursor-pointer"
                    >
                      ✖ Cancel Edit Mode
                    </button>
                  )}
                </div>

                <div className="space-y-3">
                  {changelogList.map((entry) => {
                    const isBeingEdited = editingChangelogId === (entry.id || entry.version);
                    return (
                      <div 
                        key={entry.id || entry.version} 
                        className={`p-4 rounded-2xl transition-all border flex items-center justify-between gap-4 ${
                          isBeingEdited 
                            ? "bg-amber-500/10 border-amber-500/60 shadow-[0_0_20px_rgba(245,158,11,0.2)]" 
                            : "bg-zinc-900/60 border-zinc-800 hover:border-zinc-700"
                        }`}
                      >
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-bold text-white text-xs">{entry.version}</span>
                            {entry.tag && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                                {entry.tag}
                              </span>
                            )}
                            {entry.tagAr && (
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                                {entry.tagAr}
                              </span>
                            )}
                            <span className="text-[10px] text-zinc-500 font-mono">📅 {entry.date || "August 2026"}</span>
                            {isBeingEdited && (
                              <span className="px-2 py-0.5 rounded-full text-[9px] font-black bg-amber-500 text-black uppercase">
                                Currently Editing
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-slate-300 dark:text-zinc-400 mt-1 truncate">
                            {entry.headline} {entry.headlineAr && `• (${entry.headlineAr})`}
                          </p>
                          <p className="text-[10px] text-zinc-500 mt-0.5">
                            {entry.categories?.length || 0} Categories • {entry.categories?.reduce((acc, c) => acc + (c.items?.length || 0), 0) || 0} Feature Items
                          </p>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            type="button"
                            onClick={() => handleStartEditChangelog(entry)}
                            className="px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5"
                            title="Edit this changelog without changing its original publish date"
                          >
                            <span>✏️ Edit</span>
                          </button>

                          {entry.id && entry.id !== "v1_0_0_genesis" && (
                            <button
                              type="button"
                              onClick={() => handleDeleteChangelog(entry.id!)}
                              className="p-2 text-slate-500 dark:text-zinc-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-colors cursor-pointer"
                              title="Delete from Live Feed"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

            </form>
          )}

        </section>

        {/* 2-Column Split: Submitted User Error Reports & Push Release Manager */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Submitted Error Reports (2 cols) */}
          <section className="lg:col-span-2 p-6 bg-slate-100/90 dark:bg-zinc-950/90 border border-slate-200 dark:border-zinc-800 rounded-3xl space-y-4 shadow-lg">
            <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200 dark:border-zinc-800">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <h2 className="text-base font-bold text-white">
                  Live Firestore Error Reports
                </h2>
              </div>
              <span className="text-xs font-mono text-slate-500 dark:text-zinc-400">
                {errorReports.length} records retrieved
              </span>
            </div>

            {loadingReports ? (
              <div className="py-12 text-center text-zinc-500 font-mono text-xs flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                Querying Cloud Firestore collection...
              </div>
            ) : errorReports.length === 0 ? (
              <div className="py-12 text-center text-zinc-500 text-xs">
                ✨ Zero unhandled errors reported. Clean operational slate!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-zinc-800/80 text-zinc-500 font-mono uppercase text-[10px]">
                      <th className="py-2.5 px-3">Severity</th>
                      <th className="py-2.5 px-3">Error Summary</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Environment</th>
                      <th className="py-2.5 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/40">
                    {errorReports.map((report) => (
                      <tr key={report.id} className="hover:bg-zinc-900/40 transition-colors">
                        <td className="py-3 px-3">
                          <span
                            className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                              report.severity === "critical"
                                ? "bg-red-500/20 text-red-400 border border-red-500/40"
                                : report.severity === "low"
                                ? "bg-zinc-800 text-slate-700 dark:text-zinc-300"
                                : "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                            }`}
                          >
                            {report.severity || "medium"}
                          </span>
                        </td>
                        <td className="py-3 px-3 max-w-[220px]">
                          <p className="font-semibold text-slate-800 dark:text-zinc-200 truncate" title={report.errorMessage}>
                            {report.errorMessage}
                          </p>
                          {report.clientNotes && (
                            <p className="text-[11px] text-slate-500 dark:text-zinc-400 truncate italic">
                              "{report.clientNotes}"
                            </p>
                          )}
                        </td>
                        <td className="py-3 px-3">
                          <select
                            value={report.status || "open"}
                            onChange={(e) => handleStatusChange(report.id!, e.target.value as any)}
                            className={`px-2 py-1 text-[10px] rounded-lg font-bold uppercase bg-zinc-900 border cursor-pointer ${
                              report.status === "resolved"
                                ? "text-emerald-400 border-emerald-500/30"
                                : report.status === "investigating"
                                ? "text-cyan-400 border-cyan-500/30"
                                : "text-amber-400 border-amber-500/30"
                            }`}
                          >
                            <option value="open">Open</option>
                            <option value="investigating">In Review</option>
                            <option value="resolved">Resolved</option>
                          </select>
                        </td>
                        <td className="py-3 px-3 text-[11px] text-slate-500 dark:text-zinc-400 font-mono">
                          {report.userAgent ? "Desktop Browser" : "Direct Client"}
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => setSelectedReport(report)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium text-cyan-400 hover:text-cyan-300 bg-cyan-950/40 border border-cyan-500/30 rounded-lg transition-colors cursor-pointer"
                          >
                            <Eye className="w-3 h-3" /> Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Launcher Mandatory Update Policy Controller (1 col) */}
          <section className="p-6 bg-white dark:bg-zinc-950/90 border border-slate-200 dark:border-cyan-500/30 rounded-3xl space-y-5 shadow-xl dark:shadow-[0_0_30px_rgba(0,229,255,0.06)] flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-zinc-800">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
                <div>
                  <h2 className="text-base font-bold text-slate-900 dark:text-white">Launcher Update Policy</h2>
                  <p className="text-[10px] text-slate-500 dark:text-zinc-400 font-mono">RTDB: /releases/latest/isMandatory</p>
                </div>
              </div>

              <div className="mt-5 space-y-4">
                {/* Modern Animated Toggle Switch for Mandatory Auto-Update */}
                <div className="p-5 bg-slate-50 dark:bg-zinc-900/90 border border-slate-200 dark:border-zinc-800 rounded-2xl space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-extrabold text-slate-900 dark:text-white text-sm">Enforce Mandatory Auto-Update</p>
                      <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">Launchers will require updating before launch</p>
                    </div>
                    <button
                      type="button"
                      onClick={async () => {
                        const newMandatory = !releaseInfo.isMandatory;
                        setReleaseInfo({ ...releaseInfo, isMandatory: newMandatory });
                        try {
                          await toggleMandatoryUpdate(newMandatory);
                          setReleaseSuccess(true);
                          showToast(`Mandatory update policy: ${newMandatory ? "Enforced" : "Optional"}`, "success");
                          setTimeout(() => setReleaseSuccess(false), 3000);
                        } catch (err: any) {
                          showToast("Failed to update policy: " + err?.message, "error");
                        }
                      }}
                      className={`relative w-14 h-7 rounded-full transition-colors duration-300 focus:outline-none cursor-pointer shrink-0 ${
                        releaseInfo.isMandatory ? "bg-cyan-500 shadow-[0_0_15px_rgba(0,229,255,0.6)]" : "bg-zinc-700"
                      }`}
                    >
                      <span
                        className={`absolute top-1 left-1 w-5 h-5 rounded-full bg-white transition-transform duration-300 ${
                          releaseInfo.isMandatory ? "translate-x-7" : "translate-x-0"
                        }`}
                      />
                    </button>
                  </div>

                  <div className="pt-2 flex items-center gap-2 text-[11px] font-mono">
                    <span className={`w-2 h-2 rounded-full ${releaseInfo.isMandatory ? "bg-cyan-400 animate-pulse" : "bg-zinc-500"}`} />
                    <span className={releaseInfo.isMandatory ? "text-cyan-400 font-bold" : "text-zinc-500"}>
                      {releaseInfo.isMandatory
                        ? "ENFORCED — Outdated clients cannot launch until upgraded."
                        : "OPTIONAL — Background notification only, updates are voluntary."}
                    </span>
                  </div>
                </div>

                <div
                  className={`p-4 rounded-2xl bg-cyan-950/20 border border-cyan-500/30 flex items-center gap-3 transition-all duration-300 ${
                    releaseSuccess ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-1 pointer-events-none"
                  }`}
                >
                  <Sparkles className="w-4 h-4 text-[#00e5ff] shrink-0" />
                  <p className="text-xs text-cyan-300 font-semibold">
                    Auto-update rule synchronized with Realtime Database!
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>

        {/* Selected Error Report Modal */}
        {selectedReport && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="relative w-full max-w-2xl max-h-[85vh] flex flex-col bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 rounded-3xl p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-zinc-800 shrink-0">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-mono font-bold uppercase ${
                      selectedReport.status === "open"
                        ? "bg-red-950/60 text-red-400 border border-red-800"
                        : selectedReport.status === "investigating"
                        ? "bg-amber-950/60 text-amber-400 border border-amber-800"
                        : "bg-emerald-950/60 text-emerald-400 border border-emerald-800"
                    }`}
                  >
                    {selectedReport.status}
                  </span>
                  <h3 className="font-bold text-white text-sm truncate max-w-sm">
                    {selectedReport.errorMessage}
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedReport(null)}
                  className="p-1.5 text-slate-500 dark:text-zinc-400 hover:text-white bg-zinc-900 rounded-xl cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3 text-xs overflow-y-auto pr-1">
                <div>
                  <span className="text-zinc-500 font-mono uppercase text-[10px]">Client / User Details</span>
                  <p className="mt-1 font-semibold text-slate-800 dark:text-zinc-200">
                    {selectedReport.userEmail || "Anonymous Visitor"} • {selectedReport.timestamp ? new Date(selectedReport.timestamp).toLocaleString() : "Unknown date"}
                  </p>
                  <p className="font-mono text-[11px] text-slate-500 dark:text-zinc-400">
                    {selectedReport.url || "/"} • {selectedReport.userAgent}
                  </p>
                </div>

                {selectedReport.clientNotes && (
                  <div>
                    <span className="text-zinc-500 font-mono uppercase text-[10px]">User Remarks</span>
                    <p className="mt-1 p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-slate-700 dark:text-zinc-300 italic">
                      "{selectedReport.clientNotes}"
                    </p>
                  </div>
                )}

                {selectedReport.errorStack && (
                  <div>
                    <span className="text-zinc-500 font-mono uppercase text-[10px]">Stack Trace</span>
                    <pre className="mt-1 p-3 bg-zinc-900 border border-zinc-800 rounded-xl font-mono text-[11px] text-slate-500 dark:text-zinc-400 overflow-x-auto whitespace-pre-wrap max-h-40">
                      {selectedReport.errorStack}
                    </pre>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-zinc-800 flex justify-end gap-2 shrink-0">
                <button
                  type="button"
                  onClick={() => handleStatusChange(selectedReport.id!, "resolved")}
                  className="px-4 py-2 text-xs font-semibold text-black bg-emerald-400 hover:bg-emerald-300 rounded-xl transition-colors cursor-pointer"
                >
                  Mark as Resolved
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedReport(null)}
                  className="px-4 py-2 text-xs text-slate-500 dark:text-zinc-400 hover:text-white bg-zinc-900 hover:bg-zinc-800 rounded-xl transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Custom In-App Reset Analytics Confirmation Modal */}
        <AnimatePresence>
          {showResetConfirmModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowResetConfirmModal(false)}
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 15 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 15 }}
                transition={{ type: "spring", stiffness: 350, damping: 25 }}
                className="relative w-full max-w-md rounded-3xl bg-zinc-900 border border-red-500/40 p-6 sm:p-8 z-10 shadow-2xl space-y-5"
              >
                <div className="flex items-center gap-3.5">
                  <div className="p-3 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 shrink-0">
                    <RotateCcw className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-black text-white">Reset Analytics & Telemetry?</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-500 dark:text-zinc-400">Zero out all telemetry counters</p>
                  </div>
                </div>

                <p className="text-xs text-slate-700 dark:text-zinc-300 leading-relaxed">
                  Are you sure you want to reset all download analytics and telemetry counters back to 0? This will immediately synchronize with Realtime Database across all clients.
                </p>

                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowResetConfirmModal(false)}
                    className="px-4 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 font-bold text-xs transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={async () => {
                      setShowResetConfirmModal(false);
                      await executeReset();
                    }}
                    className="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-500 text-white font-black text-xs transition-colors cursor-pointer shadow-md"
                  >
                    Yes, Reset to 0
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Custom In-App Notification Toast */}
        <AnimatePresence>
          {adminToast && (
            <motion.div
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              className={`fixed top-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-2xl shadow-2xl backdrop-blur-xl border ${
                adminToast.type === "success"
                  ? "bg-emerald-950/90 border-emerald-500/40 text-emerald-300"
                  : "bg-red-950/90 border-red-500/40 text-red-300"
              }`}
            >
              {adminToast.type === "success" ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
              )}
              <span className="text-xs font-bold">{adminToast.message}</span>
              <button
                onClick={() => setAdminToast(null)}
                className="ml-2 text-slate-500 dark:text-zinc-400 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </main>
  );
}
