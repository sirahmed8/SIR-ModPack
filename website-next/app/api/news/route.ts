import { NextResponse } from "next/server";

export const dynamic = "force-static";

interface BroadcastData {
  active?: boolean;
  type?: string;
  title?: string;
  titleAr?: string;
  message?: string;
  messageAr?: string;
  version?: string;
  category?: string;
  buttonLabel?: string;
  buttonUrl?: string;
  timestamp?: number;
}

interface ChangelogData {
  id?: string;
  version: string;
  date: string;
  dateAr?: string;
  tag?: string;
  tagAr?: string;
  headline: string;
  headlineAr?: string;
  categories: { title: string; titleAr?: string; items: string[]; itemsAr?: string[] }[];
  buttonLabel?: string;
  buttonUrl?: string;
}

export async function GET(request: Request) {
  let format = "xml";
  let lang = "en";
  try {
    const { searchParams } = new URL(request.url);
    format = searchParams.get("format") || "xml";
    lang = searchParams.get("lang") || "en";
  } catch {}

  let broadcast: BroadcastData | null = null;
  let changelogs: ChangelogData[] = [];

  // 1. Fetch active broadcast from Firebase RTDB
  try {
    const res = await fetch("https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/broadcasts/active.json");
    if (res.ok) {
      const data = await res.json();
      if (data && data.active) {
        broadcast = data;
      }
    }
  } catch (e) {
    console.warn("Failed to fetch broadcast from RTDB:", e);
  }

  // 2. Fetch changelogs from Firebase RTDB
  try {
    const res = await fetch("https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app/changelogs.json");
    if (res.ok) {
      const data = await res.json();
      if (data) {
        changelogs = Object.values(data);
      }
    }
  } catch (e) {
    console.warn("Failed to fetch changelogs from RTDB:", e);
  }

  // Fallback if no changelogs in RTDB yet
  if (changelogs.length === 0) {
    changelogs = [
      {
        version: "1.0.0",
        date: "August 2026",
        dateAr: "أغسطس 2026",
        tag: "1.0.0",
        tagAr: "الإطلاق التأسيسي الرسمي",
        headline: "The Complete Cross-Engine Ecosystem Release",
        headlineAr: "الإطلاق الشامل لمنظومة ماين كرافت فائقة الأداء",
        categories: [
          {
            title: "🖥️ Launcher & Desktop Runtime",
            titleAr: "🖥️ المشغل وبيئة التشغيل المكتبية",
            items: [
              "Bespoke Obsidian Cyber-Dark Qt6 interface with electric cyan neon accents.",
              "Generational ZGC garbage collector tuning on Java 21."
            ]
          }
        ]
      }
    ];
  }

  // If format=json requested, return clean JSON
  if (format === "json") {
    return NextResponse.json({
      broadcast,
      changelogs,
      timestamp: Date.now()
    });
  }

  // Build RSS 2.0 XML
  const itemsXml: string[] = [];

  // Item 1: Active Broadcast (if any)
  if (broadcast && broadcast.active) {
    const title = lang === "ar" && broadcast.titleAr ? broadcast.titleAr : (broadcast.title || "SIR Global Broadcast");
    const desc = lang === "ar" && broadcast.messageAr ? broadcast.messageAr : (broadcast.message || "");
    const link = broadcast.buttonUrl || "https://sir-modpack.firebaseapp.com";
    
    itemsXml.push(`
    <item>
      <title><![CDATA[📢 [ANNOUNCEMENT] ${title}]]></title>
      <link>${link}</link>
      <guid isPermaLink="false">broadcast_${broadcast.timestamp || Date.now()}</guid>
      <pubDate>${new Date(broadcast.timestamp || Date.now()).toUTCString()}</pubDate>
      <description><![CDATA[<p><strong>${title}</strong></p><p>${desc}</p>]]></description>
      <category>${broadcast.category || "Announcement"}</category>
    </item>`);
  }

  // Items 2..N: Changelogs
  for (const ch of changelogs) {
    const headline = lang === "ar" && ch.headlineAr ? ch.headlineAr : ch.headline;
    const catHtml = ch.categories.map(c => {
      const cTitle = lang === "ar" && c.titleAr ? c.titleAr : c.title;
      const cItems = (lang === "ar" && c.itemsAr && c.itemsAr.length > 0 ? c.itemsAr : c.items).map(i => `<li>${i}</li>`).join("");
      return `<h4>${cTitle}</h4><ul>${cItems}</ul>`;
    }).join("");

    itemsXml.push(`
    <item>
      <title><![CDATA[📜 [RELEASE] ${ch.version} — ${headline}]]></title>
      <link>${ch.buttonUrl || "https://sir-modpack.firebaseapp.com/#changelog"}</link>
      <guid isPermaLink="false">changelog_${ch.version.replace(/[^a-zA-Z0-9]/g, "_")}</guid>
      <pubDate>${new Date().toUTCString()}</pubDate>
      <description><![CDATA[<h3>${ch.version} (${ch.date})</h3><p><em>${headline}</em></p>${catHtml}]]></description>
      <category>Release</category>
    </item>`);
  }

  const rssXml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>SIR Ecosystem Official News &amp; Releases</title>
    <link>https://sir-modpack.firebaseapp.com</link>
    <description>Live Announcements, Shader Updates, and Master Changelog Releases for SIR ModPack and SIR Launcher.</description>
    <language>${lang === "ar" ? "ar" : "en-US"}</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="https://sir-modpack.firebaseapp.com/api/news" rel="self" type="application/rss+xml"/>
    ${itemsXml.join("\n")}
  </channel>
</rss>`;

  return new NextResponse(rssXml, {
    headers: {
      "Content-Type": "application/xml; charset=utf-8",
      "Cache-Control": "public, max-age=60, s-maxage=300",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "SAMEORIGIN",
      "X-XSS-Protection": "1; mode=block",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
