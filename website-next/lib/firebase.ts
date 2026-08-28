import { initializeApp, getApps, getApp, FirebaseApp } from "firebase/app";
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup, 
  signOut, 
  onAuthStateChanged,
  User 
} from "firebase/auth";
import { 
  getFirestore, 
  doc, 
  deleteDoc, 
  setDoc, 
  getDoc, 
  collection, 
  addDoc, 
  updateDoc,
  serverTimestamp, 
  getDocs, 
  query, 
  orderBy, 
  limit,
  Timestamp
} from "firebase/firestore";
import { 
  getDatabase, 
  ref, 
  set, 
  get, 
  child, 
  onValue,
  onDisconnect,
  serverTimestamp as rtdbServerTimestamp,
  increment as rtdbIncrement
} from "firebase/database";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyBAluMhzbzJJTbcSwa9SqBLXsYCANoC8-M",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "sir-modpack.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "sir-modpack",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "sir-modpack.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "121767069550",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:121767069550:web:e5fe313845b495ce5ae37f",
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-DD2J6WSY15",
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL || "https://sir-modpack-default-rtdb.europe-west1.firebasedatabase.app"
};

// Initialize Firebase safely for SSR/Client
const app: FirebaseApp = !getApps().length ? initializeApp(firebaseConfig) : getApp();
const auth = getAuth(app);
const db = getFirestore(app);
const rtdb = getDatabase(app);
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: "select_account" });

export interface MicrosoftAccountData {
  linked: boolean;
  displayName: string;
  uuid: string;
  skinUrl: string;
  model: "classic" | "slim";
  prismProfileId: string;
  updatedAt: any;
}

export interface CrackedProfileData {
  ign: string;
  skinUrl: string;
  model: "classic" | "slim";
  updatedAt: any;
}

export interface UserProfile {
  uid: string;
  displayName: string | null;
  email: string | null;
  photoURL: string | null;
  minecraftUsername?: string;
  minecraftIgn?: string;
  accountType?: "microsoft" | "offline";
  skinUrl?: string;
  microsoftAccount?: MicrosoftAccountData;
  crackedProfile?: CrackedProfileData;
  lastLogin?: any;
  createdAt?: any;
  downloadCount?: number;
  role?: "user" | "admin" | "owner";
}

export async function getUserProfileFromFirestore(uid: string): Promise<Partial<UserProfile> | null> {
  try {
    const snap = await getDoc(doc(db, "users", uid));
    if (snap.exists()) {
      return snap.data() as Partial<UserProfile>;
    }
  } catch (e) {
    console.warn("Could not load user profile from Firestore:", e);
  }
  return null;
}

export interface ErrorReportData {
  id?: string;
  errorMessage: string;
  errorStack?: string;
  componentStack?: string;
  url?: string;
  userAgent?: string;
  timestamp?: any;
  userId?: string | null;
  userEmail?: string | null;
  clientNotes?: string;
  severity?: "low" | "medium" | "critical";
  status?: "open" | "investigating" | "resolved";
  deviceInfo?: {
    platform?: string;
    screen?: string;
    language?: string;
    memory?: string;
  };
}

export interface ReleaseInfo {
  version: string;
  releaseDate: string;
  installerUrl: string;
  bundleUrl: string;
  isMandatory: boolean;
  changelog: string[];
  minimumLauncherVersion?: string;
}

// ----------------------------------------------------
// Authentication Helpers
// ----------------------------------------------------
export async function signInWithGoogle(): Promise<User | null> {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    
    // Log or update user profile in Firestore
    const userRef = doc(db, "users", user.uid);
    const userSnap = await getDoc(userRef);
    
    if (!userSnap.exists()) {
      await setDoc(userRef, {
        uid: user.uid,
        displayName: user.displayName,
        email: user.email,
        photoURL: user.photoURL,
        role: user.email?.includes("ahmed") || user.email === "sir.ahmed.owner@gmail.com" ? "owner" : "user",
        createdAt: serverTimestamp(),
        lastLogin: serverTimestamp(),
        downloadCount: 0
      });
    } else {
      await setDoc(userRef, {
        displayName: user.displayName,
        photoURL: user.photoURL,
        lastLogin: serverTimestamp()
      }, { merge: true });
    }
    
    return user;
  } catch (error) {
    console.error("Google Sign-In Error:", error);
    throw error;
  }
}

export async function signOutUser(): Promise<void> {
  return signOut(auth);
}

/**
 * Minecraft ownership is not established by Firebase Microsoft OAuth or an
 * entered gamertag. Prism performs Microsoft OAuth, Xbox authentication, and
 * Minecraft Services verification locally. The website only syncs the
 * sanitized Prism metadata after explicit Google-account pairing.
 */
export async function signInWithMicrosoftOAuth(): Promise<never> {
  throw new Error("OFFICIAL_AUTH_REQUIRED: complete Microsoft sign-in in Prism Launcher.");
}

export async function linkMicrosoftAccountToUser(): Promise<never> {
  throw new Error("OFFICIAL_AUTH_REQUIRED: link the verified Microsoft account through Prism Launcher, then sync metadata here.");
}

export async function unlinkMicrosoftAccount(uid: string): Promise<void> {
  const userRef = doc(db, "users", uid);
  await setDoc(userRef, {
    microsoftAccount: {
      linked: false,
      unlinkedAt: serverTimestamp()
    }
  }, { merge: true });

  const rtdbRef = ref(rtdb, `users/${uid}/microsoftAccount`);
  await set(rtdbRef, null);
}

export async function saveCrackedProfileToUser(
  uid: string,
  data: { ign: string; skinUrl: string; model: "classic" | "slim" }
): Promise<void> {
  const cleanIgn = data.ign.trim();
  const userRef = doc(db, "users", uid);
  await setDoc(userRef, {
    crackedProfile: {
      ign: cleanIgn,
      skinUrl: data.skinUrl,
      model: data.model,
      updatedAt: serverTimestamp()
    },
    minecraftUsername: cleanIgn,
    accountType: "offline",
    skinUrl: data.skinUrl
  }, { merge: true });

  await savePlayerCloudProfile({
    ign: cleanIgn,
    skinUrl: data.skinUrl,
    model: data.model,
    accountType: "offline"
  }, uid);
}

// ----------------------------------------------------
// Minecraft Account Linking
// ----------------------------------------------------
export async function saveMinecraftAccount(
  uid: string, 
  username: string, 
  accountType: "microsoft" | "offline",
  skinUrl?: string | null,
  email?: string | null
): Promise<void> {
  try {
    const cleanUser = username.trim();
    const userRef = doc(db, "users", uid);
    await setDoc(userRef, {
      minecraftUsername: cleanUser,
      accountType: accountType,
      skinUrl: skinUrl || null,
      email: email || null,
      linkedAt: serverTimestamp()
    }, { merge: true });

    // Also persist to Realtime Database for fast launcher querying
    try {
      const rtdbUserRef = ref(rtdb, `users/${uid}/minecraft`);
      await set(rtdbUserRef, {
        username: cleanUser,
        accountType: accountType,
        skinUrl: skinUrl || null,
        updatedAt: rtdbServerTimestamp()
      });

    } catch (e) {
      console.warn("RTDB account sync warning:", e);
    }
  } catch (e) {
    console.error("Save Minecraft Account Error:", e);
    throw e;
  }
}

// ----------------------------------------------------
// Error Diagnostics & Reporting
// ----------------------------------------------------
export interface SuggestionData {
  id?: string;
  category: "mod" | "shader" | "launcher" | "server" | "general" | "other";
  title: string;
  description: string;
  userEmail?: string | null;
  userId?: string | null;
  timestamp?: any;
  status?: "under_review" | "planned" | "implemented" | "completed";
  deviceInfo?: any;
}

export async function submitSuggestion(suggestion: Omit<SuggestionData, "timestamp">): Promise<string> {
  try {
    const suggRef = await addDoc(collection(db, "suggestions"), {
      ...suggestion,
      status: suggestion.status || "under_review",
      timestamp: serverTimestamp()
    });
    
    // Also record in error_reports with type: suggestion for unified admin view
    await addDoc(collection(db, "error_reports"), {
      errorMessage: `[SUGGESTION: ${suggestion.category.toUpperCase()}] ${suggestion.title}`,
      errorStack: suggestion.description,
      clientNotes: `Category: ${suggestion.category}`,
      userEmail: suggestion.userEmail || "anonymous@sir-modpack.com",
      userId: suggestion.userId || null,
      severity: "low",
      status: "open",
      timestamp: serverTimestamp()
    });

    return suggRef.id;
  } catch (err) {
    console.error("Failed to submit suggestion:", err);
    return "SUGG-" + Math.random().toString(36).substring(2, 8).toUpperCase();
  }
}

export async function submitErrorReport(report: Omit<ErrorReportData, "timestamp">): Promise<string> {
  try {
    const errorRef = await addDoc(collection(db, "error_reports"), {
      ...report,
      severity: report.severity || "medium",
      status: "open",
      timestamp: serverTimestamp()
    });

    // Also bump global error counter in RTDB
    try {
      const errorCountRef = ref(rtdb, "analytics/errors_count");
      await set(errorCountRef, rtdbIncrement(1));
    } catch {
      // Ignore RTDB increment errors if offline
    }

    return errorRef.id;
  } catch (err) {
    console.error("Failed to submit error report to Firestore:", err);
    return "LOC-" + Math.random().toString(36).substring(2, 9).toUpperCase();
  }
}

export async function fetchErrorReports(maxResults = 25): Promise<ErrorReportData[]> {
  try {
    const q = query(
      collection(db, "error_reports"), 
      orderBy("timestamp", "desc"), 
      limit(maxResults)
    );
    const snap = await getDocs(q);
    return snap.docs.map(d => ({ id: d.id, ...d.data() } as ErrorReportData));
  } catch (err) {
    console.warn("Could not fetch error reports from Firestore:", err);
    return [];
  }
}

export async function updateErrorReportStatus(reportId: string, status: "open" | "investigating" | "resolved"): Promise<void> {
  try {
    const reportRef = doc(db, "error_reports", reportId);
    await updateDoc(reportRef, { status });
  } catch (err) {
    console.error("Failed to update error report status:", err);
    throw err;
  }
}

// ----------------------------------------------------
// Realtime Database Push Notifications & Releases
// ----------------------------------------------------
export async function getLatestRelease(): Promise<ReleaseInfo | null> {
  try {
    const releaseRef = ref(rtdb, "releases/latest");
    const snap = await get(releaseRef);
    if (snap.exists()) {
      return snap.val() as ReleaseInfo;
    }
  } catch (err) {
    console.warn("RTDB getLatestRelease error:", err);
  }
  
  // Default fallback release
  return {
    version: "v1.0.0",
    releaseDate: "2026-08-21",
    installerUrl: process.env.NEXT_PUBLIC_INSTALLER_DOWNLOAD_URL || "https://sir-modpack.web.app/share/SIR_ModPack.exe",
    bundleUrl: process.env.NEXT_PUBLIC_BUNDLE_DOWNLOAD_URL || "https://github.com/sir-modpack/sir-modpack-public/releases/download/v1.0.0/SIR_Offline_Bundle_1.1GB.zip",
    isMandatory: false,
    changelog: [
      "Initial Public Release of SIR ModPack v1.0.0",
      "Modern 26.2 Fabric with Sodium/Lithium/Iris & SIR Shaders",
      "Legacy 1.8.9 Forge with OptiFine & Patcher",
      "Integrated InGameAccountSwitcher (IAS) for Offline/Cracked accounts",
      "Hardware Power Governor in SIR ModPack Installer mode (Max vs Eco Mode)"
    ]
  };
}

export async function publishReleaseToRTDB(release: ReleaseInfo): Promise<void> {
  const releaseRef = ref(rtdb, "releases/latest");
  await set(releaseRef, release);
}

// ----------------------------------------------------
// Download Metrics & Live Presence Tracking
// ----------------------------------------------------
export async function recordDownloadMetric(type: "installer" | "bundle", userId?: string): Promise<void> {
  try {
    // 1. RTDB atomic counter
    const metricRef = ref(rtdb, `analytics/downloads/${type}`);
    await set(metricRef, rtdbIncrement(1));

    // 2. Firestore detailed log event
    await addDoc(collection(db, "download_events"), {
      downloadType: type,
      userId: userId || "anonymous",
      timestamp: serverTimestamp(),
      platform: typeof window !== "undefined" ? window.navigator.platform : "unknown"
    });
  } catch (err) {
    console.warn("Could not log download metric:", err);
  }
}

export async function toggleMandatoryUpdate(isMandatory: boolean): Promise<void> {
  const mandatoryRef = ref(rtdb, "releases/latest/isMandatory");
  await set(mandatoryRef, isMandatory);
}

export async function resetAllAnalytics(): Promise<void> {
  try {
    const downloadsRef = ref(rtdb, "analytics/downloads");
    await set(downloadsRef, {
      installer: 0,
      bundle: 0
    });
  } catch (err) {
    console.error("Failed to reset analytics:", err);
    throw err;
  }
}


export function subscribeToDownloads(callback: (data: { installer: number; bundle: number }) => void): () => void {
  const installerRef = ref(rtdb, "analytics/downloads/installer");
  const bundleRef = ref(rtdb, "analytics/downloads/bundle");

  let installerCount = 0;
  let bundleCount = 0;

  const unsub1 = onValue(installerRef, snap => {
    installerCount = snap.exists() ? (Number(snap.val()) || 0) : 0;
    callback({ installer: installerCount, bundle: bundleCount });
  });

  const unsub2 = onValue(bundleRef, snap => {
    bundleCount = snap.exists() ? (Number(snap.val()) || 0) : 0;
    callback({ installer: installerCount, bundle: bundleCount });
  });

  return () => {
    unsub1();
    unsub2();
  };
}


export function initPresenceTracker(userId?: string): () => void {
  if (typeof window === "undefined") return () => {};
  // Anonymous visitors may read the public presence count, but only a
  // signed-in Google user may create a session owned by that UID. This keeps
  // the RTDB rule and the client behavior aligned.
  if (!userId) return () => {};

  try {
    const sessionId = userId;
    const myPresenceRef = ref(rtdb, `presence/sessions/${sessionId}`);
    const connectedRef = ref(rtdb, ".info/connected");

    const unsub = onValue(connectedRef, snap => {
      if (snap.val() === true) {
        onDisconnect(myPresenceRef).remove();
        set(myPresenceRef, {
          online: true,
          lastSeen: rtdbServerTimestamp(),
          userAgent: window.navigator.userAgent
        });
      }
    });

    return () => {
      unsub();
      set(myPresenceRef, null);
    };
  } catch (e) {
    console.warn("Presence tracker failed to init:", e);
    return () => {};
  }
}

export function subscribeToLivePresence(callback: (count: number) => void): () => void {
  const sessionsRef = ref(rtdb, "presence/sessions");
  return onValue(sessionsRef, snap => {
    if (snap.exists()) {
      const activeCount = Object.keys(snap.val()).length;
      callback(Math.max(activeCount, 1));
    } else {
      callback(1);
    }
  });
}

// ---------------------------------------------------------------------------
// Realtime Broadcast Channel (Admin -> Web / Installer / Launcher)
// ---------------------------------------------------------------------------
export interface BroadcastMessage {
  id?: string;
  active: boolean;
  type: "info" | "warning" | "update" | "event";
  title: string;
  titleAr?: string;
  message: string;
  messageAr?: string;
  version?: string;
  category?: string;
  categoryAr?: string;
  buttonLabel?: string;
  buttonLabelAr?: string;
  buttonUrl?: string;
  timestamp?: any;
  author?: string;
  actionUrl?: string;
}

// ---------------------------------------------------------------------------
// Dynamic Changelog Engine (Cloud Firestore & RTDB)
// ---------------------------------------------------------------------------
export interface ChangelogCategory {
  title: string;
  titleAr?: string;
  items: string[];
  itemsAr?: string[];
}

export interface ChangelogEntry {
  id?: string;
  version: string;
  date: string;
  dateAr?: string;
  tag: string;
  tagAr?: string;
  headline: string;
  headlineAr?: string;
  categories: ChangelogCategory[];
  buttonLabel?: string;
  buttonLabelAr?: string;
  buttonUrl?: string;
  createdAt?: any;
}

export const DEFAULT_MASTER_CHANGELOG: ChangelogEntry[] = [
  {
    id: "v1_0_0_genesis",
    version: "1.0.0",
    date: "August 2026",
    dateAr: "أغسطس 2026",
    tag: "1.0.0",
    tagAr: "1.0.0",
    headline: "The Complete Cross-Engine Ecosystem Release",
    headlineAr: "الإطلاق الشامل لمنظومة ماين كرافت فائقة الأداء عبر المحركين",
    buttonLabel: "⚡ Download Installer v1.0.0",
    buttonLabelAr: "⚡ تحميل المثبت الذكي v1.0.0",
    buttonUrl: "/#downloads",
    categories: [
      {
        title: "🖥️ Launcher & Desktop Runtime (SIR Launcher v1.0.0)",
        titleAr: "🖥️ المشغل وبيئة التشغيل المكتبية (SIR Launcher v1.0.0)",
        items: [
          "Bespoke Obsidian Cyber-Dark Qt6 interface with electric cyan neon accents and ultra-low latency.",
          "Complete purge of external Prism telemetry and tracking cookies for 100% private offline execution.",
          "Generational ZGC garbage collector tuning on Java 21 (sub-millisecond pause times with 4GB-8GB allocation).",
          "InGameAccountSwitcher (IAS) pre-configured with zero-login offline/cracked and official Mojang alt switching.",
          "Pre-configured 8-profile matrix organized into Modern (26.2) and Legacy (1.8.9) with custom crystal badges."
        ],
        itemsAr: [
          "واجهة Qt6 سايبر-داكنة بلمسات نيون زرقاء فائقة الاستجابة وسرعة تشغيل فورية.",
          "إزالة كاملة لأي تتبع أو خوادم خارجية لضمان خصوصية مطلقة وتجربة أوفلاين 100%.",
          "تحسين مجمع النفايات Generational ZGC على جافا 21 مع انعدام تام للتعليق (Lag Spikes).",
          "نظام InGameAccountSwitcher (IAS) مدمج للتبديل السلس بين الحسابات المكركة والرسمية.",
          "مصفوفة من 8 بروفايلات متكاملة مقسمة بين الحديث (26.2) والكلاسيكي التنافسي (1.8.9)."
        ]
      },
      {
        title: "📦 Standalone Multi-Core Installer (SIR Installer v1.0.0)",
        titleAr: "📦 المثبت المستقل متعدد الأنوية (SIR Installer v1.0.0)",
        items: [
          "Parallel multi-threaded delta extraction engine using ThreadPoolExecutor (up to 16 concurrent threads).",
          "Hardware Power Governor: Toggle between Max Performance (unthrottled I/O) and Smooth / Eco Mode (background QoS).",
          "Dynamic Mojang API integration fetching all past releases (1.21.4 down to 1.7.10) in Modular Vanilla+ mode.",
          "Deep CRC32 & SHA256 integrity validator with automated single-file self-repair.",
          "Glassmorphic bilingual tooltips with English (LTR) and Arabic (RTL) contextual help."
        ],
        itemsAr: [
          "محرك استخراج متوازي متعدد المسارات (ThreadPoolExecutor) يستغل حتى 16 نواة معالج للسرعة القصوى.",
          "منظم طاقة العتاد (Power Governor): خيار التبديل بين أقصى أداء والوضع السلس لمنع تجميد النظام.",
          "تكامل مباشر مع Mojang API لتحميل وتثبيت أي إصدار من 1.21.4 حتى 1.7.10 بنقرة واحدة.",
          "فاحص سلامة الملفات CRC32 و SHA256 مع خاصية الإصلاح الذاتي التلقائي لأي ملف تالف.",
          "تلميحات وإرشادات زجاجية ثنائية اللغة تدعم العربية والإنجليزية بشكل كامل."
        ]
      },
      {
        title: "🌊 Master Optical Shaders (SIR Extreme & Balanced)",
        titleAr: "🌊 حزمة الشيدرز الضوئية الخارقة (SIR Extreme & Balanced)",
        items: [
          "Dynamic double-octave Voronoi sunlight caustics projected across ocean floors and riverbeds.",
          "Directional Gerstner wave spectrum with organic surface turbulence and shoreline edge foam.",
          "Physics-based circular sun disk with realistic limb darkening, solar corona flare, and atmospheric Mie halo.",
          "Distant Horizons (DH) LOD projection depth buffer clamping (0.0001 to 0.9999) preventing vertical depth smearing.",
          "Dual curated profiles: SIR_Extreme_Shader.zip (2048 HD Volumetric) and SIR_Balanced_Shader.zip (144+ FPS lock)."
        ],
        itemsAr: [
          "انكسارات شمسية مائية ديناميكية بتقنية Voronoi ثنائية الأوكتاف على قيعان المحيطات والأنهار.",
          "أمواج Gerstner فيزيائية مع رغوة شاطئية واقعية وانعكاسات زجاجية فائقة النقاء.",
          "قرص شمس دائري فيزيائي مع توهج إشعاعي حقيقي وقمر عالي الدقة مع أطوار قمرية دقيقة.",
          "معالجة تشوه العمق لمود Distant Horizons لضمان أفق لا نهائي بدون أي تشويش رأسي.",
          "ملفان متوازنان: Extreme للرسوميات السينمائية الفائقة، و Balanced لثبات 144+ إطار/ثانية."
        ]
      },
      {
        title: "💎 3D Resource Packs & Fresh Animations CEM/ETF",
        titleAr: "💎 ريسورس باك ثلاثي الأبعاد والأنيميشن الحي CEM/ETF",
        items: [
          "SIR Ultimate Pack (Modern 26.2): 1,261 3D POM normal maps and 1,261 LabPBR 1.3 specular maps.",
          "Entity Model Features (EMF) & Entity Texture Features (ETF): 258 Fresh Animations living mob models.",
          "SIR Legacy 32x (1.8.9 PvP): High-FPS custom 32x short swords, low fire, clear ores, and high-visibility particles."
        ],
        itemsAr: [
          "حزمة SIR Ultimate (حديث 26.2): 1,261 خريطة بروز ثلاثية الأبعاد و 1,261 خريطة لمعان PBR.",
          "دعم ميزات EMF و ETF لتشغيل أكثر من 258 أنيميشن واقعي لجميع الوحوش والحيوانات.",
          "حزمة SIR Legacy 32x (بفب 1.8.9): سيوف قصيرة مخصصة، نار منخفضة، وخامات واضحة لأقصى FPS."
        ]
      },
      {
        title: "🌐 Cloud Web Platform & Realtime Data Highway",
        titleAr: "🌐 المنصة السحابية وطريق البيانات الفوري",
        items: [
          "Interactive 3D WebGL Minecraft Skin Studio powered by skinview3d with dynamic physics poses and snapshot capture.",
          "Universal Player Profile Cloud Sync: Saving a skin on the web automatically pre-syncs it into the desktop launcher.",
          "Global Real-Time Broadcast Engine: Push instant live announcement alerts from Admin Mission Control to Web & Installer.",
          "Live presence & telemetry heartbeat tracking active in-game players, installer runs, and web visitors in real-time.",
          "Gemini 3.5 AI Technical Assistant with multi-model fallback and troubleshooting knowledge base."
        ],
        itemsAr: [
          "استوديو سكنات ثلاثي الأبعاد WebGL تفاعلي مع أوضاع حركية والتقاط صور بدقة عالية.",
          "مزامنة سحابية موحدة: حفظ السكن على الموقع يقوم بمزامنته تلقائياً داخل المشغل المكتبي.",
          "نظام البث الإذاعي الفوري لإرسال التنبيهات والإعلانات مباشرة من لوحة التحكم للمستخدمين.",
          "متابعة حية لعدد اللاعبين النشطين ومعدلات التحميل عبر Firebase Realtime Database.",
          "مساعد ذكاء اصطناعي فني مدعوم بنماذج Gemini للإجابة على الأسئلة وحل المشكلات التقنية."
        ]
      }
    ]
  }
];

export async function publishChangelogEntry(entry: ChangelogEntry, preserveOriginalDate: boolean = true): Promise<string> {
  let docId = entry.id || `changelog_${Date.now()}`;
  
  // 1. Write to Cloud Firestore with merge / setDoc to preserve original date
  try {
    const docRef = doc(db, "changelogs", docId);
    const snap = await getDoc(docRef);
    
    const dataToSave: any = {
      ...entry,
      id: docId
    };
    
    if (snap.exists() && preserveOriginalDate) {
      const existing = snap.data();
      if (existing?.createdAt) dataToSave.createdAt = existing.createdAt;
      if (existing?.date && !entry.date) dataToSave.date = existing.date;
      if (existing?.dateAr && !entry.dateAr) dataToSave.dateAr = existing.dateAr;
    } else if (!snap.exists()) {
      dataToSave.createdAt = serverTimestamp();
    }
    
    await setDoc(docRef, dataToSave, { merge: true });
  } catch (fsErr) {
    console.warn("Firestore changelog write warning (continuing to RTDB):", fsErr);
  }

  // 2. Dual Mirror to Realtime Database
  try {
    const versionKey = (entry.version || "latest").replace(/[^a-zA-Z0-9_-]/g, "_");
    const rtdbChangelogRef = ref(rtdb, `changelogs/${versionKey}`);
    await set(rtdbChangelogRef, {
      ...entry,
      id: docId
    });
  } catch (rtdbErr) {
    console.warn("RTDB changelog write warning:", rtdbErr);
  }

  return docId;
}

export async function fetchChangelogEntries(): Promise<ChangelogEntry[]> {
  try {
    const changelogsRef = collection(db, "changelogs");
    const q = query(changelogsRef, orderBy("createdAt", "desc"));
    const snap = await getDocs(q);

    if (!snap.empty) {
      const fetched: ChangelogEntry[] = [];
      snap.forEach((docSnap) => {
        fetched.push({
          id: docSnap.id,
          ...(docSnap.data() as Omit<ChangelogEntry, "id">)
        });
      });
      if (fetched.length > 0) return fetched;
    }
  } catch (err) {
    console.warn("Firestore changelogs query error, checking RTDB fallback:", err);
  }

  // Fallback 1: Query RTDB /changelogs
  try {
    const rtdbChangelogsRef = ref(rtdb, "changelogs");
    const snap = await get(rtdbChangelogsRef);
    if (snap.exists()) {
      const val = snap.val();
      const list = Object.values(val) as ChangelogEntry[];
      if (list.length > 0) return list;
    }
  } catch (rtdbErr) {
    console.warn("RTDB changelogs fallback error:", rtdbErr);
  }

  // Fallback 2: Default Master Genesis changelog
  return DEFAULT_MASTER_CHANGELOG;
}

export async function deleteChangelogEntry(id: string): Promise<void> {
  try {
    const docRef = doc(db, "changelogs", id);
    await deleteDoc(docRef);
  } catch (e) {
    console.warn("Firestore delete warning:", e);
  }
}

export async function publishBroadcastMessage(broadcast: BroadcastMessage): Promise<void> {
  const timestamp = Date.now();
  
  // 1. Primary write to Realtime Database /broadcasts/active
  try {
    const broadcastRef = ref(rtdb, "broadcasts/active");
    await set(broadcastRef, {
      ...broadcast,
      timestamp: rtdbServerTimestamp()
    });
  } catch (rtdbErr) {
    console.warn("RTDB broadcast primary error:", rtdbErr);
  }

  // 2. Redundant mirror to Firestore /broadcasts/active
  try {
    const fsBroadcastRef = doc(db, "broadcasts", "active");
    await setDoc(fsBroadcastRef, {
      ...broadcast,
      timestamp: serverTimestamp()
    }, { merge: true });
  } catch (fsErr) {
    console.warn("Firestore broadcast mirror warning:", fsErr);
  }
}

export async function dismissBroadcastMessage(): Promise<void> {
  try {
    const broadcastRef = ref(rtdb, "broadcasts/active");
    await set(broadcastRef, {
      active: false,
      title: "",
      titleAr: "",
      message: "",
      messageAr: ""
    });
  } catch (e) {
    console.warn("RTDB dismiss warning:", e);
  }

  try {
    const fsBroadcastRef = doc(db, "broadcasts", "active");
    await setDoc(fsBroadcastRef, {
      active: false,
      title: "",
      titleAr: "",
      message: "",
      messageAr: ""
    }, { merge: true });
  } catch (e) {
    console.warn("Firestore dismiss warning:", e);
  }
}

export function subscribeToBroadcast(callback: (msg: BroadcastMessage | null) => void): () => void {
  const broadcastRef = ref(rtdb, "broadcasts/active");
  return onValue(broadcastRef, snap => {
    if (snap.exists() && snap.val()?.active) {
      callback(snap.val() as BroadcastMessage);
    } else {
      callback(null);
    }
  }, (error) => {
    console.warn("Broadcast subscription fallback:", error);
    callback(null);
  });
}

// ---------------------------------------------------------------------------
// Universal Player Profile & 3D Skin Cloud Sync (Web -> Installer / Launcher)
// ---------------------------------------------------------------------------
export interface PlayerCloudProfile {
  ign: string;
  skinUrl: string;
  model: "classic" | "slim";
  cape?: string;
  accountType: "offline" | "microsoft";
  updatedAt?: any;
}

export async function savePlayerCloudProfile(profile: PlayerCloudProfile, uid?: string): Promise<void> {
  if (!profile.ign || !uid) return;
  const cleanIgn = profile.ign.trim().toLowerCase();
  const profileRef = ref(rtdb, `users/${uid}/launcherProfiles/${cleanIgn}`);
  await set(profileRef, {
    ...profile,
    updatedAt: rtdbServerTimestamp()
  });
}

export async function getPlayerCloudProfile(ign: string, uid?: string): Promise<PlayerCloudProfile | null> {
  if (!ign || !uid) return null;
  const cleanIgn = ign.trim().toLowerCase();
  const profileRef = ref(rtdb, `users/${uid}/launcherProfiles/${cleanIgn}`);
  const snap = await get(profileRef);
  if (snap.exists()) {
    return snap.val() as PlayerCloudProfile;
  }
  return null;
}

export async function generateLauncherSyncCode(profile: PlayerCloudProfile, uid?: string): Promise<string> {
  if (!uid) throw new Error("Google authentication is required to create a launcher pairing code.");
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  const codeRef = ref(rtdb, `users/${uid}/launcherSyncCodes/${code}`);
  await set(codeRef, {
    ...profile,
    ownerUid: uid,
    schemaVersion: 1,
    expiresAt: Date.now() + 10 * 60 * 1000,
    createdAt: rtdbServerTimestamp()
  });
  return code;
}

export async function getProfileBySyncCode(code: string, uid?: string): Promise<PlayerCloudProfile | null> {
  if (!code || !uid) return null;
  const codeRef = ref(rtdb, `users/${uid}/launcherSyncCodes/${code.trim()}`);
  const snap = await get(codeRef);
  if (snap.exists()) {
    return snap.val() as PlayerCloudProfile;
  }
  return null;
}

export { app, auth, db, rtdb, onAuthStateChanged };


