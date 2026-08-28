"use client";

import React from "react";
import { motion } from "framer-motion";
import { Shield, ShieldCheck, ArrowLeft, ArrowRight, Lock, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";

export default function PrivacyPolicyPage() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";

  const sections = [
    {
      num: "01",
      title: isAr ? "جمع البيانات والغرض منها" : "Data Minimization & Purpose",
      body: isAr 
        ? "نلتزم في منظومة SIR بمبدأ التقليل من البيانات (Data Minimization). نجمع فقط البيانات الأساسية اللازمة لتشغيل الميزات الحيوية مثل مزامنة الحسابات: اسم اللاعب (IGN)، الرابط المباشر للسكن ثلاثي الأبعاد، والمعرف الرقمي المجهول. لا نقوم إطلاقاً بجمع أي بيانات سرية أو كلمات مرور الحسابات."
        : "We collect only the bare minimum data required to deliver core launcher and account syncing features: your chosen In-Game Name (IGN), 3D skin render URL, and anonymous auth identifier (UID). We NEVER collect, store, or inspect your Minecraft passwords or private Mojang credentials."
    },
    {
      num: "02",
      title: isAr ? "المزامنة السحابية وقواعد البيانات" : "Cloud & Realtime Synchronization",
      body: isAr
        ? "يتم حفظ بيانات البروفايل المعروضة فقط عبر خوادم Google Cloud Firestore و Firebase Realtime Database المشفرة بالكامل ببروتوكول TLS 1.3 مع شهادات أمان متقدمة. لا يتم تسجيل أو اعتراض أي محادثات داخل اللعبة أو بيانات اللعب الفردية."
        : "Public profile attributes are securely stored in Google Cloud Firestore and Firebase Realtime Database with end-to-end TLS 1.3 encryption. We do not inspect, intercept, log, or harvest private gameplay data, local world saves, or in-game chat messages."
    },
    {
      num: "03",
      title: isAr ? "التخزين المحلي وأمان الحسابات" : "Local Storage & IAS Security",
      body: isAr
        ? "تفضيلات الواجهة (الوضع الليلي/النهاري، اختيار اللغة) وبيانات تسجيل الدخول عبر محول الحسابات InGameAccountSwitcher (IAS) تحفظ محلياً بالكامل على جهاز المستخدم فقط ولا تُرسل لأي خوادم خارجية."
        : "UI preferences (Dark/Light mode, language selection) and account switching tokens via InGameAccountSwitcher (IAS) are saved strictly inside your local device filesystem and browser localStorage."
    },
    {
      num: "04",
      title: isAr ? "انعدام الإعلانات والبيع للطرف الثالث" : "Zero Third-Party Monetization",
      body: isAr
        ? "نضمن لك بنسبة 100% أننا لا نبيع أو نؤجر أو نشارك أي بيانات للمستخدمين مع شركات الإعلانات أو الوسطاء التجاريين أو أي جهات خارجية."
        : "We do not sell, rent, monetize, track, or disclose any user information to third-party advertisers, data brokers, or commercial marketing agencies."
    },
    {
      num: "05",
      title: isAr ? "حقوق المستخدم ومسح البيانات" : "User Rights & Data Erasure",
      body: isAr
        ? "يحق للمستخدم في أي وقت طلب الحذف الفوري والكامل لحسابه أو بيانات البروفايل الخاصة به من خوادم المنظومة عبر مركز الحسابات أو بالتواصل مع الإدارة."
        : "You maintain absolute ownership of your data. You may request total and permanent erasure of your cloud account and linked profile records at any time via the Account Hub."
    },
    {
      num: "06",
      title: isAr ? "الحماية المتقدمة وعزل الواجهات" : "Multi-Layer Security & Input Sanitization",
      body: isAr
        ? "تخضع جميع الاتصالات لحماية متقدمة ضد هجمات XSS وحقن البيانات عبر lib/security.ts، مع ترويسات أمان HTTP صارمة (nosniff, SAMEORIGIN, CSP, Permissions-Policy) وحماية ضد هجمات DDoS عبر Cloudflare وقواعد Firebase الأمنية."
        : "All network traffic and data entries are protected against XSS injection and prototype pollution via lib/security.ts. Military-grade HTTP headers (nosniff, SAMEORIGIN, strict CSP, permissions-policy) and Cloudflare/Firebase security rules safeguard every transaction."
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#070a10] text-slate-900 dark:text-white pt-28 pb-20 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
      <div className="max-w-4xl mx-auto space-y-10">
        
        {/* Header Hero */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-600 dark:text-cyan-400 text-xs font-bold backdrop-blur-md">
            <Shield className="w-4 h-4" />
            <span>{isAr ? "وثيقة حماية الخصوصية 2026.2" : "Universal Privacy Policy 2026.2"}</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 dark:text-white">
            {isAr ? "حماية الخصوصية وأمان البيانات" : "Privacy-by-Design & Data Security"}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
            {isAr
              ? "نؤمن بالشفافية الكاملة. منظومة SIR مصممة لحماية خصوصيتك مع انعدام تام لأي تتبع إعلاني أو جمع لبياناتك الشخصية."
              : "We believe in radical transparency. The SIR Ecosystem is engineered with zero telemetry and complete user privacy."}
          </p>
        </div>

        {/* Sections List */}
        <div className="space-y-6">
          {sections.map((sec) => (
            <div
              key={sec.num}
              className="p-6 rounded-3xl bg-white dark:bg-[#0d121d] border border-slate-200 dark:border-slate-800 hover:border-cyan-500/40 transition-all shadow-md dark:shadow-xl"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-mono font-bold text-xs">
                  {sec.num}
                </span>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">{sec.title}</h2>
              </div>
              <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed pl-11 rtl:pr-11 rtl:pl-0">
                {sec.body}
              </p>
            </div>
          ))}
        </div>

        {/* Back to Home Button */}
        <div className="text-center pt-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-slate-900 border border-slate-800 hover:border-cyan-500 text-slate-300 hover:text-white text-xs font-bold transition-all"
          >
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Return to Home"}</span>
          </Link>
        </div>

      </div>
    </div>
  );
}
