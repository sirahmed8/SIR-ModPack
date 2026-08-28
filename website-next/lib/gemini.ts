import { GoogleGenerativeAI } from "@google/generative-ai";

const GOOGLE_API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY || "AIzaSyC0yjHj3_6WPh76vkslhwjXZVLjSfV0rYg";
const OPENROUTER_API_KEY = process.env.NEXT_PUBLIC_OPENROUTER_API_KEY || "";

const genAI = new GoogleGenerativeAI(GOOGLE_API_KEY);

export const SIR_SYSTEM_INSTRUCTION = `You are the SIR Ecosystem AI Intelligence — the official master AI assistant for SIR ModPack, SIR Launcher v1.0.0, SIR Shaders 2.0, HAVOC PvP, and high-performance Minecraft optimization.

### 🌟 Technical Master Knowledge Base:
1. **SIR ModPack Dual Engine Architecture:**
   - **Modern 26.2 (Fabric Engine):** Powered by Sodium, Lithium, Iris, Indium, ModernFix, FerriteCore, Dynamic FPS, Continuity, Bobby, Distant Horizons, and Entity Culling. 240+ verified bundled mods.
   - **Legacy 1.8.9 (Forge Engine):** Engineered for ultra-competitive 1.8.9 PvP. Powered by OptiFine, Patcher, Essential, KeystrokesMod, HitDelayFix, 1000Hz polling rate raw mouse input, and full 144Hz/240Hz/360Hz motion clarity.

2. **Custom Shader Suite (SIR Shaders 2.0):**
   - **SIR Extreme Shader:** Base engine is Bliss Shader with enhancements from Solas, BSL, Photon, and Complementary. Features: 2048 Shadowmap, Volumetric atmospheric Godrays, Subsurface Scattering (SSS), Screen Space Reflections (SSR), 3D Parallax Occlusion Mapping (POM), Ultra HD Lunar Phases & Starfield, Pure Crystal Water Caustics, and ACES Filmic Tonemapping.
   - **SIR Balanced Shader:** 1024 Shadowmap, identical circular glowing sun disk & detailed moon phases, optimized for steady 144+ FPS on mid-range GTX/RTX & Radeon GPUs.
   - **Distant Horizons Fix:** Depth buffer clearing is configured so LOD terrain renders seamlessly with zero vertical smearing.

3. **SIR Launcher & Installer v1.0.0:**
   - **1-Click GUI Installer:** Features a **Hardware Power Governor** toggle:
     * *Max Performance Mode:* Utilizes 100% CPU threads for fast extraction.
     * *Smooth / Eco Mode:* Dynamically sets process priority to Below Normal / Low I/O to ensure the user's PC never freezes during install.
   - **Firebase Low-Read Push Updater:** Listens to Firebase Realtime Database (/releases/latest) with zero polling overhead.
   - **Cracked & Microsoft Support:** Built-in InGameAccountSwitcher (IAS) allows instant switching between official Microsoft and offline/cracked accounts.

4. **Optimal RAM & Java Tuning:**
   - Recommended RAM: **4 GB to 6 GB** for standard clients (e.g. \`-Xms4G -Xmx6G\`).
   - Warning: Allocating >8GB can cause Java Garbage Collection (G1GC) latency spikes.
   - Flags: Optimized G1GC parameters (\`-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200\`).

5. **Cloud Hosting & HAVOC Project:**
   - **Cloud Server Hosting SaaS:** Interactive tier configurator is coming soon with a **SOON** badge. For free hosting, direct players to Aternos or Cloudflared zero-port tunnels.
   - **HAVOC PvP Injector:** Companion project created by the owner's brother (Ahmed's brother), focused on advanced PvP hit mechanics and movement mechanics (coming soon).
   - **Creator & Owner:** SIR Ahmed. Linktree: https://linktr.ee/sir.ahmed

### 💬 Guidelines:
- Respond in high-tech, enthusiastic, cyberpunk cyber-neon tone.
- Answer in the **same language** as the user's inquiry (Arabic or English).
- Always provide genuine, accurate, deeply helpful answers with markdown formatting, code snippets, and emojis.`;

export interface ChatMessage {
  role: "user" | "model" | "assistant";
  text: string;
}

export interface AiResponse {
  text: string;
  source: "gemini-3.6-flash" | "gemini-3.5-flash-lite" | "gemini-fallback" | "openrouter" | "offline-expert";
  modelUsed: string;
  suggestedAction?: {
    labelEn: string;
    labelAr: string;
    href: string;
  };
}

/**
 * Detect smart quick action link from text content
 */
function detectSuggestedAction(text: string): { labelEn: string; labelAr: string; href: string } | undefined {
  const t = text.toLowerCase();
  if (t.includes("shader") || t.includes("شيدر") || t.includes("bliss") || t.includes("raytracing")) {
    return { labelEn: "Open Shaders Optical Lab", labelAr: "فتح مختبر الشيدرز الضوئي", href: "/shaders" };
  }
  if (t.includes("mod") || t.includes("مود") || t.includes("fabric") || t.includes("forge")) {
    return { labelEn: "Browse 240+ Mods Suite", labelAr: "تصفح كتالوج المودات (240+)", href: "/mods" };
  }
  if (t.includes("download") || t.includes("installer") || t.includes("تحميل") || t.includes("تثبيت")) {
    return { labelEn: "Download SIR Launcher v1.0.0", labelAr: "تحميل لانشر SIR v1.0.0", href: "/#downloads" };
  }
  if (t.includes("trainer") || t.includes("cps") || t.includes("aim") || t.includes("reflex") || t.includes("تدريب") || t.includes("كليك")) {
    return { labelEn: "Open PvP Reflex Trainer", labelAr: "فتح مدرب الـ PvP ورد الفعل", href: "/trainer" };
  }
  if (t.includes("fps") || t.includes("benchmark") || t.includes("gpu") || t.includes("cpu") || t.includes("عتاد") || t.includes("فريم")) {
    return { labelEn: "Calculate Rig FPS", labelAr: "حساب فريمات جهازك بدقة", href: "/benchmarks" };
  }
  if (t.includes("skin") || t.includes("سكن") || t.includes("cape") || t.includes("كيب")) {
    return { labelEn: "Open 3D Skin Studio", labelAr: "فتح استوديو السكنات ثلاثي الأبعاد", href: "/skins" };
  }
  if (t.includes("server") || t.includes("سيرفر") || t.includes("hypixel") || t.includes("pika")) {
    return { labelEn: "Explore Multiplayer Servers", labelAr: "استكشاف سيرفرات اللعب الجماعي", href: "/servers" };
  }
  return undefined;
}

/**
 * Master AI query engine connecting to official Gemini 3.6 Flash / 3.5 Flash-Lite
 */
export async function askSirAIDetailed(prompt: string, history: ChatMessage[] = []): Promise<AiResponse> {
  const primaryModels = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite"
  ];

  // 1. Try Google AI SDK with official active Gemini models
  for (const modelName of primaryModels) {
    try {
      const model = genAI.getGenerativeModel({
        model: modelName,
        systemInstruction: SIR_SYSTEM_INSTRUCTION
      });

      const formattedHistory = history.map(item => ({
        role: item.role === "assistant" ? "model" : (item.role as "user" | "model"),
        parts: [{ text: item.text }]
      }));

      const chat = model.startChat({
        history: formattedHistory
      });

      const result = await chat.sendMessage(prompt);
      const response = await result.response;
      const responseText = response.text();

      if (responseText && responseText.trim().length > 0) {
        return {
          text: responseText,
          source: modelName as any,
          modelUsed: modelName,
          suggestedAction: detectSuggestedAction(responseText)
        };
      }
    } catch (err: any) {
      console.warn(`[SIR AI] Google AI model '${modelName}' attempt failed:`, err?.message || err);
    }
  }

  // 2. Try OpenRouter API Fallback
  if (OPENROUTER_API_KEY) {
    try {
      const openRouterResponse = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${OPENROUTER_API_KEY}`,
          "HTTP-Referer": "https://sir-modpack.firebaseapp.com",
          "X-Title": "SIR Ecosystem AI",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: "meta-llama/llama-3.3-70b-instruct",
          messages: [
            { role: "system", content: SIR_SYSTEM_INSTRUCTION },
            ...history.map(h => ({
              role: h.role === "model" ? "assistant" : h.role,
              content: h.text
            })),
            { role: "user", content: prompt }
          ],
          temperature: 0.7,
          max_tokens: 1024
        })
      });

      if (openRouterResponse.ok) {
        const data = await openRouterResponse.json();
        const answer = data.choices?.[0]?.message?.content;
        if (answer && answer.trim().length > 0) {
          return {
            text: answer,
            source: "openrouter",
            modelUsed: "openrouter/llama-3.3-70b",
            suggestedAction: detectSuggestedAction(answer)
          };
        }
      }
    } catch (orErr) {
      console.warn("[SIR AI] OpenRouter fallback failed:", orErr);
    }
  }

  // 3. Fallback to Autonomous Rule Engine
  const offlineText = getOfflineExpertResponse(prompt);
  return {
    text: offlineText,
    source: "offline-expert",
    modelUsed: "SIR-Autonomous-Expert-Engine",
    suggestedAction: detectSuggestedAction(offlineText)
  };
}

export async function askSirAI(prompt: string, history: any[] = []): Promise<AiResponse> {
  return askSirAIDetailed(prompt, history);
}

export async function polishAnnouncementWithAI(
  rawDraft: { title: string; message: string },
  customInstruction: string = "",
  tone: "hype" | "professional" | "urgent" | "bilingual" = "hype"
): Promise<{ title: string; message: string; type: "info" | "warning" | "update" | "event" }> {
  const prompt = `You are the Executive Chief of Communications for the SIR Ecosystem.
Task: Polish and optimize the following raw broadcast announcement for all players.
Raw Title: "${rawDraft.title}"
Raw Message: "${rawDraft.message}"
Tone: ${tone}
${customInstruction ? `Custom Instruction: ${customInstruction}` : ""}

Respond with a strict JSON object:
{
  "title": "Polished concise headline with emojis",
  "message": "Polished engaging broadcast text",
  "type": "info"
}`;
  try {
    const res = await askSirAIDetailed(prompt);
    const cleaned = res.text.replace(/```json/gi, "").replace(/```/g, "").trim();
    const parsed = JSON.parse(cleaned);
    return {
      title: parsed.title || rawDraft.title,
      message: parsed.message || rawDraft.message,
      type: parsed.type || "info"
    };
  } catch (e) {
    return {
      title: rawDraft.title,
      message: rawDraft.message,
      type: "info"
    };
  }
}

export async function polishChangelogWithAI(
  draft: { version?: string; headline?: string; rawNotes: string },
  customInstruction: string = ""
): Promise<{ headline: string; tag: string; buttonLabel?: string; categories: { title: string; items: string[] }[] }> {
  const version = draft.version || "v1.0.0";
  const prompt = `You are the Lead Release Architect for SIR ModPack.
Transform raw commit notes into a structured release changelog:
Version: ${version}
Headline: "${draft.headline || `SIR Release ${version}`}"
Notes: "${draft.rawNotes}"
${customInstruction ? `Custom Instruction: ${customInstruction}` : ""}

Respond with strict JSON:
{
  "headline": "Release headline with emojis",
  "tag": "Gold Release",
  "buttonLabel": "Install v1.0.0",
  "categories": [
    {
      "title": "Category Name",
      "items": ["Item 1", "Item 2"]
    }
  ]
}`;
  try {
    const res = await askSirAIDetailed(prompt);
    const cleaned = res.text.replace(/```json/gi, "").replace(/```/g, "").trim();
    const parsed = JSON.parse(cleaned);
    return {
      headline: parsed.headline || draft.headline || `SIR Release ${version}`,
      tag: parsed.tag || "Update",
      buttonLabel: parsed.buttonLabel || "Install Update",
      categories: parsed.categories || [{ title: "General Improvements", items: [draft.rawNotes] }]
    };
  } catch (e) {
    return {
      headline: draft.headline || `SIR Release ${version}`,
      tag: "Update",
      buttonLabel: "Install Update",
      categories: [{ title: "General Improvements", items: [draft.rawNotes] }]
    };
  }
}

export async function translateBroadcastToArabic(
  draft: { title: string; message: string; buttonLabel?: string }
): Promise<{ titleAr: string; messageAr: string; buttonLabelAr?: string }> {
  const prompt = `Translate this announcement to high-tech Arabic:
Title: "${draft.title}"
Message: "${draft.message}"

Respond with strict JSON:
{
  "titleAr": "العنوان بالعربية",
  "messageAr": "النص بالعربية",
  "buttonLabelAr": "نص الزر"
}`;
  try {
    const res = await askSirAIDetailed(prompt);
    const cleaned = res.text.replace(/```json/gi, "").replace(/```/g, "").trim();
    const parsed = JSON.parse(cleaned);
    return {
      titleAr: parsed.titleAr || draft.title,
      messageAr: parsed.messageAr || draft.message,
      buttonLabelAr: parsed.buttonLabelAr || draft.buttonLabel
    };
  } catch (e) {
    return {
      titleAr: draft.title,
      messageAr: draft.message,
      buttonLabelAr: draft.buttonLabel
    };
  }
}

export async function translateChangelogToArabic(
  changelog: { headline: string; tag: string; buttonLabel?: string; categories: { title: string; items: string[] }[] }
): Promise<{ headlineAr: string; tagAr: string; buttonLabelAr?: string; categories: { title: string; titleAr: string; items: string[]; itemsAr: string[] }[] }> {
  const prompt = `Translate this changelog to Arabic:
Headline: "${changelog.headline}"
Tag: "${changelog.tag}"
Categories: ${JSON.stringify(changelog.categories)}

Respond with strict JSON:
{
  "headlineAr": "العنوان بالعربية",
  "tagAr": "الوسم بالعربية",
  "categories": [
    {
      "title": "Original Title",
      "titleAr": "العنوان بالعربية",
      "items": ["item"],
      "itemsAr": ["الترجمة"]
    }
  ]
}`;
  try {
    const res = await askSirAIDetailed(prompt);
    const cleaned = res.text.replace(/```json/gi, "").replace(/```/g, "").trim();
    const parsed = JSON.parse(cleaned);
    return {
      headlineAr: parsed.headlineAr || changelog.headline,
      tagAr: parsed.tagAr || changelog.tag,
      buttonLabelAr: parsed.buttonLabelAr || changelog.buttonLabel,
      categories: parsed.categories || changelog.categories.map(c => ({ ...c, titleAr: c.title, itemsAr: c.items }))
    };
  } catch (e) {
    return {
      headlineAr: changelog.headline,
      tagAr: changelog.tag,
      buttonLabelAr: changelog.buttonLabel,
      categories: changelog.categories.map(c => ({ ...c, titleAr: c.title, itemsAr: c.items }))
    };
  }
}

function getOfflineExpertResponse(query: string): string {
  const q = query.toLowerCase();

  if (q.includes("ram") || q.includes("memory") || q.includes("رام")) {
    return "⚡ **SIR Ecosystem RAM & Performance Recommendation:**\n\n* **Optimal allocation:** `4 GB` to `6 GB` (e.g. `-Xms4G -Xmx6G`).\n* **Why not 8GB+?** Excessive heap allocation causes Java Garbage Collection (G1GC) micro-stutters during intense PvP.\n* **Modern 26.2 Fabric:** Runs smoothly on just 3GB-4GB with FerriteCore & Sodium!";
  }

  if (q.includes("shader") || q.includes("sir shader") || q.includes("شيدر")) {
    return "✨ **SIR Shaders 2.0 & Optical Graphics Suite:**\n\n* **SIR Extreme Shader:** 2048 Shadowmap, Volumetric atmospheric fog, Subsurface Scattering, Screen Space Reflections, 3D Parallax Occlusion Mapping, and ACES Film Tonemapping.\n* **SIR Balanced Shader:** 1024 Shadowmap, locking 144+ FPS on mid-range GPUs.\n* **Activation:** Press `ESC` ➔ `Video Settings` ➔ `Shader Packs` ➔ Select `SIR_Extreme_Shader.zip`!";
  }

  if (q.includes("1.8.9") || q.includes("pvp") || q.includes("بفب")) {
    return "⚔️ **Legacy 1.8.9 PvP Battle Engine:**\n\n* Optimized Forge profile with Patcher, HitDelayFix, and raw mouse input.\n* 1000Hz polling rate support with zero hit registration drop.\n* Fully calibrated for Hypixel, Minemen, and competitive tournaments.";
  }

  if (q.includes("havoc") || q.includes("هافوك")) {
    return "🚀 **HAVOC PvP Injector Portal:**\n\n* HAVOC is a proprietary PvP enhancement engine developed by Ahmed's brother.\n* Status: Currently under active development (**SOON**).\n* Keep an eye on the official SIR ecosystem dashboard for beta access announcements!";
  }

  if (q.includes("offline") || q.includes("cracked") || q.includes("مكرك") || q.includes("حساب")) {
    return "🎮 **Cracked & Offline Account Support:**\n\n* SIR ModPack comes with pre-integrated **InGameAccountSwitcher (IAS)**.\n* You can add offline usernames or Microsoft accounts seamlessly inside the main menu without restarting the launcher.";
  }

  return "🌟 **SIR AI Intelligence Active:** I am standing by to assist with any questions regarding **SIR ModPack v1.0.0**, SIR Shaders, 1.8.9 PvP configurations, RAM optimization, or HAVOC.\n\n🔗 **Developer Contact:** [SIR Ahmed Linktree](https://linktr.ee/sir.ahmed)";
}
