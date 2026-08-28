"use client";

import React, { useState, useEffect } from "react";
import { useEcosystem } from "@/lib/context";
import { 
  saveCrackedProfileToUser,
  generateLauncherSyncCode
} from "@/lib/firebase";
import {
  saveClaimedAccountToCloud,
  getClaimedAccountsFromCloud,
  deleteClaimedAccountFromCloud,
  ClaimedAccountItem
} from "@/lib/multiAccounts";
import { 
  Sparkles, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  ShieldCheck, 
  Loader2, 
  Search, 
  KeyRound 
} from "lucide-react";
import { SkinViewer3D } from "./account/SkinViewer3D";
import { PresetSkinsGrid } from "./account/PresetSkinsGrid";
import { MultiAccountManager } from "./account/MultiAccountManager";
import { isValidMinecraftIgn, sanitizeInput } from "@/lib/security";

export function AccountLinking() {
  const { user, userProfile, setUserProfile } = useEcosystem();

  const [crackedIgn, setCrackedIgn] = useState("");
  const [customSkinData, setCustomSkinData] = useState<string | null>(null);
  const [modelType, setModelType] = useState<"classic" | "slim">("classic");
  const [skinStealerQuery, setSkinStealerQuery] = useState("");
  const [fetchingSkin, setFetchingSkin] = useState(false);
  const [savingCracked, setSavingCracked] = useState(false);
  const [crackedSuccess, setCrackedSuccess] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const [claimedAccounts, setClaimedAccounts] = useState<ClaimedAccountItem[]>([]);
  const [syncCode, setSyncCode] = useState<string | null>(null);
  const [generatingCode, setGeneratingCode] = useState(false);

  const reloadClaimedAccounts = async () => {
    if (user) {
      try {
        const accounts = await getClaimedAccountsFromCloud(user.uid);
        setClaimedAccounts(accounts);
      } catch (e) {
        console.warn("Error loading claimed accounts:", e);
      }
    }
  };

  useEffect(() => {
    reloadClaimedAccounts();
  }, [user]);

  const activeSkinUrl = customSkinData || (userProfile?.minecraftUsername ? `https://mc-heads.net/skin/${encodeURIComponent(userProfile.minecraftUsername)}` : "https://mc-heads.net/skin/Steve");

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.includes("png")) {
      setValidationError("Please upload a valid 64x64 or 64x32 PNG Minecraft skin.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target?.result as string;
      setCustomSkinData(dataUrl);
      setValidationError(null);
    };
    reader.readAsDataURL(file);
  };

  const handleStealSkin = async () => {
    const cleanQuery = sanitizeInput(skinStealerQuery, 24);
    if (!cleanQuery) return;
    if (!isValidMinecraftIgn(cleanQuery)) {
      setValidationError("Please enter a valid Minecraft username (3-16 alphanumeric characters).");
      return;
    }

    setFetchingSkin(true);
    try {
      const skinUrl = `https://minotar.net/skin/${encodeURIComponent(cleanQuery)}`;
      setCustomSkinData(skinUrl);
      setCrackedIgn(cleanQuery);
      setValidationError(null);
    } catch {
      setValidationError("Failed to resolve skin for this player.");
    } finally {
      setFetchingSkin(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanIgn = sanitizeInput(crackedIgn, 16);
    if (!cleanIgn) {
      setValidationError("Please enter your Minecraft username.");
      return;
    }
    if (!isValidMinecraftIgn(cleanIgn)) {
      setValidationError("Invalid username format. Must be 3 to 16 letters, numbers, or underscores.");
      return;
    }

    setSavingCracked(true);
    setValidationError(null);
    try {
      if (user) {
        await saveCrackedProfileToUser(user.uid, {
          ign: cleanIgn,
          skinUrl: customSkinData || activeSkinUrl,
          model: modelType
        });
        await saveClaimedAccountToCloud(user.uid, user.email, {
          ign: cleanIgn,
          skinUrl: customSkinData || activeSkinUrl,
          model: modelType,
          accountType: "offline"
        });
        await reloadClaimedAccounts();
      }

      setUserProfile(prev => prev ? {
        ...prev,
        minecraftUsername: cleanIgn,
        skinUrl: customSkinData || activeSkinUrl,
        accountType: "offline"
      } : {
        uid: user?.uid || "guest",
        displayName: user?.displayName || "Player",
        email: user?.email || "",
        photoURL: user?.photoURL || "",
        minecraftUsername: cleanIgn,
        skinUrl: customSkinData || activeSkinUrl,
        accountType: "offline"
      });

      setCrackedSuccess(true);
      setTimeout(() => setCrackedSuccess(false), 4000);
    } catch (err: any) {
      setValidationError(err.message || "Failed to save profile.");
    } finally {
      setSavingCracked(false);
    }
  };

  const handleGenerateSyncCode = async () => {
    const targetIgn = sanitizeInput(userProfile?.minecraftUsername || crackedIgn.trim(), 16);
    if (!targetIgn || !isValidMinecraftIgn(targetIgn)) {
      setValidationError("Please enter a valid username (3-16 alphanumeric characters) before generating a sync code.");
      return;
    }
    if (!user) {
      setValidationError("Please sign in with Google to generate a cloud sync code.");
      return;
    }
    setGeneratingCode(true);
    try {
      const code = await generateLauncherSyncCode({
        ign: targetIgn,
        skinUrl: activeSkinUrl,
        model: modelType,
        accountType: "offline"
      }, user.uid);
      setSyncCode(code);
    } catch {
      setValidationError("Could not generate cloud sync code.");
    } finally {
      setGeneratingCode(false);
    }
  };

  return (
    <section id="account" className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-500/30 text-xs font-mono uppercase tracking-wider">
          Identity Hub
        </span>
        <h2 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
          Minecraft Account & 3D Skin Studio
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Link your official or custom Minecraft account with real-time 3D skin previews and 1-click cloud sync to SIR Launcher.
        </p>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: 3D Skin Viewer */}
        <div className="lg:col-span-5 flex justify-center">
          <SkinViewer3D
            skinUrl={activeSkinUrl}
            modelType={modelType}
            onModelChange={setModelType}
          />
        </div>

        {/* Right: Account Form & Preset Hub */}
        <div className="lg:col-span-7 space-y-6">
          {/* Username & Skin Grabber Form */}
          <form onSubmit={handleSaveProfile} className="p-6 rounded-3xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 space-y-4 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
              <span>Link Minecraft Account</span>
            </h3>

            {validationError && (
              <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-600 dark:text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{validationError}</span>
              </div>
            )}

            {crackedSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>✓ Profile successfully connected and synced to cloud!</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 dark:text-slate-300">Minecraft Username (IGN)</label>
              <input
                type="text"
                value={crackedIgn}
                onChange={(e) => setCrackedIgn(e.target.value)}
                placeholder="e.g. Notch, SirAhmed, Dream"
                className="w-full px-4 py-2.5 rounded-2xl bg-slate-50 dark:bg-slate-950/80 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white text-sm focus:border-cyan-500 focus:outline-none"
              />
            </div>

            {/* Fetch by IGN or Upload Custom PNG */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">Skin Stealer / Grabber</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={skinStealerQuery}
                    onChange={(e) => setSkinStealerQuery(e.target.value)}
                    placeholder="Fetch from player..."
                    className="flex-1 px-3 py-2 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 text-xs text-slate-900 dark:text-white"
                  />
                  <button
                    type="button"
                    onClick={handleStealSkin}
                    disabled={fetchingSkin}
                    className="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-cyan-700 dark:text-cyan-400 border border-slate-300 dark:border-slate-700 text-xs font-bold transition-all flex items-center gap-1 cursor-pointer"
                  >
                    <Search className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-300">Custom Skin (PNG)</label>
                <label className="flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 border-dashed text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white cursor-pointer hover:border-cyan-500 transition-all">
                  <Upload className="w-3.5 h-3.5" />
                  <span>Choose PNG File</span>
                  <input type="file" accept="image/png" onChange={handleFileUpload} className="hidden" />
                </label>
              </div>
            </div>

            {/* Submit & Sync Buttons */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-200 dark:border-slate-800">
              <button
                type="submit"
                disabled={savingCracked}
                className="px-5 py-2.5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2 cursor-pointer"
              >
                {savingCracked ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                <span>Save Profile</span>
              </button>

              <button
                type="button"
                onClick={handleGenerateSyncCode}
                disabled={generatingCode}
                className="px-4 py-2.5 rounded-2xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-cyan-700 dark:text-cyan-400 border border-slate-300 dark:border-slate-700 text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-sm"
              >
                <KeyRound className="w-4 h-4" />
                <span>Launcher Sync Code</span>
              </button>
            </div>
          </form>

          {/* Sync Code Display Banner */}
          {syncCode && (
            <div className="p-4 rounded-2xl bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-300 dark:border-cyan-500/30 flex items-center justify-between shadow-sm">
              <div>
                <p className="text-xs font-bold text-cyan-800 dark:text-cyan-300">Your 6-Digit Launcher Sync Code:</p>
                <p className="text-2xl font-black font-mono tracking-widest text-cyan-600 dark:text-cyan-400 mt-1">{syncCode}</p>
                <p className="text-[10px] text-slate-600 dark:text-slate-400 mt-1">Enter this code inside SIR Launcher to sync your profile in 1 second.</p>
              </div>
            </div>
          )}

          {/* Preset Skins Grid */}
          <PresetSkinsGrid
            selectedSkinUrl={activeSkinUrl}
            onSelect={(preset) => {
              setCustomSkinData(preset.skinUrl);
              setCrackedIgn(preset.name.split(" ")[0]);
              setModelType(preset.model);
            }}
          />
        </div>
      </div>

      {/* Multi-Account Manager */}
      <MultiAccountManager
        accounts={claimedAccounts}
        activeIgn={userProfile?.minecraftUsername || ""}
        onSelectAccount={(acc) => {
          setUserProfile(prev => prev ? {
            ...prev,
            minecraftUsername: acc.ign,
            skinUrl: acc.skinUrl,
            accountType: acc.accountType === "microsoft" ? "microsoft" : "offline"
          } : {
            uid: user?.uid || "guest",
            displayName: user?.displayName || "Player",
            email: user?.email || "",
            photoURL: user?.photoURL || "",
            minecraftUsername: acc.ign,
            skinUrl: acc.skinUrl,
            accountType: acc.accountType === "microsoft" ? "microsoft" : "offline"
          });
          setCustomSkinData(acc.skinUrl);
          setModelType(acc.model || "classic");
        }}
        onDeleteAccount={async (ign) => {
          if (user) {
            await deleteClaimedAccountFromCloud(user.uid, user.email, ign);
            await reloadClaimedAccounts();
          }
        }}
        onGenerateSyncCode={handleGenerateSyncCode}
        generatingCode={generatingCode}
      />
    </section>
  );
}
