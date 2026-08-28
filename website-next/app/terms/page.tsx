"use client";

import React from "react";
import { motion } from "framer-motion";
import { FileText, ArrowLeft, ArrowRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { useEcosystem } from "@/lib/context";

export default function TermsOfServicePage() {
  const { lang } = useEcosystem();
  const isAr = lang === "ar";

  const sections = [
    {
      num: "01",
      title: isAr ? "قبول الشروط" : "Acceptance of Terms",
      body: isAr
        ? "باستخدامك أو تحميلك أو تشغيلك لأي جزء من منظومة SIR (بما في ذلك SIR Launcher، مثبت SIR Installer، الشيدرز المخصصة، حزم التكستشر، أو الموقع الإلكتروني)، فإنك توافق على الالتزام الكامل بهذه الشروط."
        : "By downloading, installing, launching, or accessing any component of the SIR Ecosystem (including SIR Launcher, SIR Installer, custom Shaders, 3D Resource Packs, and Web Platform), you acknowledge and agree to be bound by these Terms."
    },
    {
      num: "02",
      title: isAr ? "الامتثال لقوانين Mojang Studios و Microsoft" : "Mojang Studios Compliance",
      body: isAr
        ? "ماينكرافت علامة تجارية مسجلة لشركة Mojang AB و Microsoft. منظومة SIR هي مشروع مستقل مفتوح المصدر تم تطويره من قِبل مجتمع اللاعبين، وليس منتجاً رسمياً من Mojang أو Microsoft. يلتزم المشروع التزاماً تاماً بإرشادات العلامة التجارية والاستخدام التجاري لموجانج."
        : "Minecraft is a registered trademark of Mojang AB / Microsoft. The SIR Ecosystem is an independent, community-driven open-source project and is NOT an official Minecraft product, nor is it endorsed by, affiliated with, or associated with Mojang AB or Microsoft."
    },
    {
      num: "03",
      title: isAr ? "التراخيص والمصادر المفتوحة" : "Open-Source & Attribution",
      body: isAr
        ? "كافة الأدوات البرمجية الخاصة بالمشروع (المشغل، المثبت، وبوابة الويب) مرخصة ومحمية برخص المصادر المفتوحة. تظل المودات والشيدرز والتكستشرات الخارجية ملكاً لأصحابها ومطوريها الأصليين مع الحفاظ على كامل حقوقهم الأدبية."
        : "Custom launcher modules, installer utilities, and web source codes are distributed under open-source licenses. Bundled third-party mods, shaders, and textures remain the intellectual property of their respective creators."
    },
    {
      num: "04",
      title: isAr ? "النزاهة واللعب العادل" : "Fair Play & Competitive Integrity",
      body: isAr
        ? "يتحمل المستخدم المسؤولية الكاملة عن الامتثال لقوانين السيرفرات التي ينضم إليها. ميزات التبديل بين الحسابات وأدوات تسريع الأداء مخصصة لتحسين تجربة اللعب بشكل عادل وقانوني."
        : "Users are expected to utilize the SIR Ecosystem in accordance with standard fair play rules. While the client provides advanced rendering optimizations and account switching tools, server-specific rules regarding modifications and alts must be respected by the user."
    },
    {
      num: "05",
      title: isAr ? "إخلاء المسؤولية" : "Disclaimer of Warranties",
      body: isAr
        ? "يتم توفير منظومة SIR 'كما هي' دون أي ضمانات صريحة أو ضمنية. لا يتحمل المطورون أي مسؤولية عن أي حظر من سيرفرات خارجية أو تعارض في ملفات الحفظ ناتج عن تعديلات شخصية يقوم بها المستخدم."
        : "The SIR Ecosystem is provided 'AS IS', without warranty of any kind, express or implied. Maintainers shall not be liable for any third-party server sanctions, hardware incompatibilities, or save data corruption resulting from unauthorized user modifications."
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#070a10] text-slate-900 dark:text-white pt-28 pb-20 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
      <div className="max-w-4xl mx-auto space-y-10">
        
        {/* Header Hero */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-bold backdrop-blur-md">
            <FileText className="w-4 h-4" />
            <span>{isAr ? "شروط الخدمة واتفاقية المستخدم 2026.2" : "Terms of Service & EULA 2026.2"}</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-slate-900 dark:text-white">
            {isAr ? "اتفاقية الاستخدام وشروط الخدمة" : "User License & Fair Play Terms"}
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto text-sm sm:text-base">
            {isAr
              ? "إرشادات الاستخدام العادل والامتثال لقوانين الألعاب والمصادر المفتوحة."
              : "Guidelines for fair play, open-source attribution, and community standards."}
          </p>
        </div>

        {/* Sections List */}
        <div className="space-y-6">
          {sections.map((sec) => (
            <div
              key={sec.num}
              className="p-6 rounded-3xl bg-white dark:bg-[#0d121d] border border-slate-200 dark:border-slate-800 hover:border-emerald-500/40 transition-all shadow-md dark:shadow-xl"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-mono font-bold text-xs">
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
            className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs transition-all shadow-lg shadow-emerald-500/20 active:scale-95"
          >
            {isAr ? <ArrowRight className="w-4 h-4" /> : <ArrowLeft className="w-4 h-4" />}
            <span>{isAr ? "العودة للرئيسية" : "Return to Home"}</span>
          </Link>
        </div>

      </div>
    </div>
  );
}
