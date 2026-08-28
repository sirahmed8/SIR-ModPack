"use client";

import React from "react";
import { useEcosystem } from "@/lib/context";
import { signInWithGoogle } from "@/lib/firebase";
import { Lock, ArrowRight, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface AuthGateProps {
  children: React.ReactNode;
  featureName?: string;
  featureNameAr?: string;
}

export function AuthGate({ children, featureName = "this feature", featureNameAr = "هذه الميزة" }: AuthGateProps) {
  const { user, lang } = useEcosystem();
  const isAr = lang === "ar";

  if (!user) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center px-4 py-16">
        <div className="max-w-md w-full p-8 rounded-3xl bg-white dark:bg-[#101624]/90 border border-cyan-500/30 backdrop-blur-2xl text-center space-y-6 shadow-2xl shadow-cyan-500/10">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mx-auto shadow-inner">
            <Lock className="w-8 h-8" />
          </div>
          
          <div className="space-y-2">
            <span className="badge-tag px-3 py-1 rounded-full text-xs font-bold font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              🔒 {isAr ? "تسجيل الدخول مطلوب" : "Authentication Required"}
            </span>
            <h2 className="text-xl font-black text-slate-900 dark:text-white">
              {isAr ? `سجل دخولك للوصول إلى ${featureNameAr}` : `Sign In to Access ${featureName}`}
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              {isAr 
                ? "للحفاظ على أمان المنظومة ومزامنة حساباتك وأوشحتك وإعداداتك السحابية، يرجى تسجيل الدخول بحساب Google مجاناً."
                : "To ensure ecosystem integrity and sync your cloud accounts, capes, and settings, please sign in with your Google account."}
            </p>
          </div>

          <button
            onClick={() => signInWithGoogle()}
            className="w-full py-3.5 rounded-2xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-black text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/25 cursor-pointer active:scale-98"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
            </svg>
            <span>{isAr ? "تسجيل الدخول السريع عبر Google" : "Continue with Google"}</span>
          </button>

          <div className="pt-2">
            <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-cyan-400 transition-colors">
              {isAr ? <ArrowRight className="w-3.5 h-3.5" /> : <ArrowLeft className="w-3.5 h-3.5" />}
              <span>{isAr ? "العودة للصفحة الرئيسية" : "Back to Home"}</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
