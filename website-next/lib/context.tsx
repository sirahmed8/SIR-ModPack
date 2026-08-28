"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { Language, translations } from "./i18n";
import { auth, onAuthStateChanged, UserProfile, getUserProfileFromFirestore, signInWithGoogle, signOutUser } from "./firebase";
import { User } from "firebase/auth";
import { setCookie, getCookie, getCookieConsent, saveCookieConsent, CookieConsentState, DEFAULT_CONSENT } from "./storage";

interface EcosystemContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  dir: "ltr" | "rtl";
  t: typeof translations.en;
  theme: "dark" | "light";
  themeMode: "system" | "dark" | "light";
  setThemeMode: (mode: "system" | "dark" | "light") => void;
  toggleTheme: () => void;
  perfMode: "cinematic" | "eco";
  togglePerfMode: () => void;
  soundFx: boolean;
  toggleSoundFx: () => void;
  cookieConsent: CookieConsentState;
  setConsent: (consent: CookieConsentState) => void;
  user: User | null;
  userProfile: UserProfile | null;
  setUserProfile: React.Dispatch<React.SetStateAction<UserProfile | null>>;
  welcomeOpen: boolean;
  setWelcomeOpen: (open: boolean) => void;
  errorModalOpen: boolean;
  setErrorModalOpen: (open: boolean) => void;
  activeErrorData: { message: string; stack?: string } | null;
  triggerErrorReport: (message?: string, stack?: string) => void;
  triggerSuggestion: (initialCategory?: string) => void;
  feedbackTab: 'issue' | 'suggestion';
  setFeedbackTab: (tab: 'issue' | 'suggestion') => void;
  loginWithGoogle: () => Promise<User | null>;
  logout: () => Promise<void>;
}

const EcosystemContext = createContext<EcosystemContextType | null>(null);

export function EcosystemProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Language>("en");
  const [themeMode, setThemeModeState] = useState<"system" | "dark" | "light">("system");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [perfMode, setPerfMode] = useState<"cinematic" | "eco">("cinematic");
  const [soundFx, setSoundFx] = useState<boolean>(true);
  const [cookieConsent, setCookieConsentState] = useState<CookieConsentState>(DEFAULT_CONSENT);
  const [user, setUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [welcomeOpen, setWelcomeOpen] = useState(false);
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [activeErrorData, setActiveErrorData] = useState<{ message: string; stack?: string } | null>(null);
  const [feedbackTab, setFeedbackTab] = useState<'issue' | 'suggestion'>('issue');

  // Load language, theme, perf mode, and cookies on mount
  useEffect(() => {
    try {
      const savedLang = (localStorage.getItem("sir_lang") || getCookie("sir_lang")) as Language;
      if (savedLang === "ar" || savedLang === "en") {
        setLangState(savedLang);
      }
      const savedThemeMode = (localStorage.getItem("sir_theme_mode") || getCookie("sir_theme_mode") || "dark") as "system" | "dark" | "light";
      setThemeModeState(savedThemeMode);
      if (savedThemeMode === "system") {
        const isDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        setTheme("dark");
      } else {
        setTheme(savedThemeMode);
      }
      const savedPerf = (localStorage.getItem("sir_perf_mode") || getCookie("sir_perf_mode")) as "cinematic" | "eco";
      if (savedPerf === "cinematic" || savedPerf === "eco") {
        setPerfMode(savedPerf);
      }
      const savedSound = localStorage.getItem("sir_sound_fx");
      if (savedSound !== null) {
        setSoundFx(savedSound === "true");
      }
      const existingConsent = getCookieConsent();
      if (existingConsent) {
        setCookieConsentState(existingConsent);
      }

      // Load linked Minecraft account from local cache initially
      const savedUser = localStorage.getItem("sir_linked_minecraft_user");
      const savedType = localStorage.getItem("sir_linked_account_type") as "microsoft" | "offline";
      const savedSkin = localStorage.getItem("sir_custom_skin_data");
      if (savedUser) {
        setUserProfile({
          uid: "guest",
          displayName: savedUser,
          email: null,
          photoURL: null,
          minecraftUsername: savedUser,
          accountType: savedType || "offline",
          skinUrl: savedSkin || undefined
        });
      }

      // Check if first visit
      const hasVisited = localStorage.getItem("sir_visited");
      if (!hasVisited) {
        setWelcomeOpen(true);
        localStorage.setItem("sir_visited", "true");
      }
    } catch (e) {
      console.warn("Storage access failed:", e);
    }
  }, []);

  // Sync document direction, theme, and eco mode classes
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
      document.documentElement.lang = lang;
      document.documentElement.setAttribute("data-perf-mode", perfMode);
      if (theme === "light") {
        document.documentElement.classList.add("light-theme");
        document.documentElement.classList.remove("dark");
        document.body.classList.add("light-theme");
        document.body.classList.remove("dark");
      } else {
        document.documentElement.classList.remove("light-theme");
        document.documentElement.classList.add("dark");
        document.body.classList.remove("light-theme");
        document.body.classList.add("dark");
      }
    }
  }, [lang, theme, perfMode]);

  // Listen to Firebase Auth state & fetch genuine user Firestore data
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);
      if (firebaseUser) {
        let mcUser = localStorage.getItem("sir_linked_minecraft_user") || "";
        let accType = (localStorage.getItem("sir_linked_account_type") as "microsoft" | "offline") || "offline";
        let skinUrl = localStorage.getItem("sir_custom_skin_data") || "";

        try {
          const docData = await getUserProfileFromFirestore(firebaseUser.uid);
          if (docData) {
            if (docData.minecraftUsername) mcUser = docData.minecraftUsername;
            if (docData.accountType) accType = docData.accountType;
            if (docData.skinUrl) skinUrl = docData.skinUrl;
          }
        } catch (e) {
          console.warn("Firestore fetch error:", e);
        }

        if (mcUser) {
          localStorage.setItem("sir_linked_minecraft_user", mcUser);
          localStorage.setItem("sir_linked_account_type", accType);
        }
        if (skinUrl) {
          localStorage.setItem("sir_custom_skin_data", skinUrl);
        }

        setUserProfile({
          uid: firebaseUser.uid,
          displayName: firebaseUser.displayName,
          email: firebaseUser.email,
          photoURL: firebaseUser.photoURL,
          minecraftUsername: mcUser || undefined,
          accountType: mcUser ? accType : undefined,
          skinUrl: skinUrl || undefined
        });
      } else {
        const savedUser = localStorage.getItem("sir_linked_minecraft_user");
        const savedType = localStorage.getItem("sir_linked_account_type") as "microsoft" | "offline";
        const savedSkin = localStorage.getItem("sir_custom_skin_data");
        if (savedUser) {
          setUserProfile({
            uid: "guest",
            displayName: savedUser,
            email: null,
            photoURL: null,
            minecraftUsername: savedUser,
            accountType: savedType || "offline",
            skinUrl: savedSkin || undefined
          });
        } else {
          setUserProfile(null);
        }
      }
    });

    return () => unsubscribe();
  }, []);

  const setLang = (newLang: Language) => {
    setLangState(newLang);
    try {
      localStorage.setItem("sir_lang", newLang);
      setCookie("sir_lang", newLang, 365);
    } catch {}
  };

  const applyThemeClasses = (resolvedTheme: "dark" | "light") => {
    if (typeof document !== "undefined") {
      if (resolvedTheme === "light") {
        document.documentElement.classList.add("light-theme");
        document.documentElement.classList.remove("dark");
        document.body.classList.add("light-theme");
        document.body.classList.remove("dark");
      } else {
        document.documentElement.classList.remove("light-theme");
        document.documentElement.classList.add("dark");
        document.body.classList.remove("light-theme");
        document.body.classList.add("dark");
      }
    }
  };

  const setThemeMode = (mode: "system" | "dark" | "light") => {
    setThemeModeState(mode);
    try {
      localStorage.setItem("sir_theme_mode", mode);
      setCookie("sir_theme_mode", mode, 365);
    } catch {}
    if (mode === "system") {
      const isDark = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      const resolved = isDark ? "dark" : "light";
      setTheme(resolved);
      applyThemeClasses(resolved);
    } else {
      setTheme(mode);
      applyThemeClasses(mode);
    }
  };

  const toggleTheme = () => {
    const next = themeMode === "system" ? "dark" : themeMode === "dark" ? "light" : "system";
    setThemeMode(next);
  };

  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = (e: MediaQueryListEvent) => {
      if (themeMode === "system") {
        const resolved = e.matches ? "dark" : "light";
        setTheme(resolved);
        applyThemeClasses(resolved);
      }
    };
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, [themeMode]);

  const togglePerfMode = () => {
    const next = perfMode === "cinematic" ? "eco" : "cinematic";
    setPerfMode(next);
    try {
      localStorage.setItem("sir_perf_mode", next);
      setCookie("sir_perf_mode", next, 365);
    } catch {}
  };

  const toggleSoundFx = () => {
    const next = !soundFx;
    setSoundFx(next);
    try {
      localStorage.setItem("sir_sound_fx", String(next));
    } catch {}
  };

  const setConsent = (consent: CookieConsentState) => {
    setCookieConsentState(consent);
    saveCookieConsent(consent);
  };

  const triggerErrorReport = (message?: string, stack?: string) => {
    setFeedbackTab("issue");
    setActiveErrorData({ message: message || "Manual User Diagnostic Report", stack });
    setErrorModalOpen(true);
  };

  const triggerSuggestion = (initialCategory?: string) => {
    setFeedbackTab("suggestion");
    setErrorModalOpen(true);
  };

  const loginWithGoogle = async () => {
    return signInWithGoogle();
  };

  const logout = async () => {
    return signOutUser();
  };

  const dir = lang === "ar" ? "rtl" : "ltr";
  const t = translations[lang];

  return (
    <EcosystemContext.Provider
      value={{
        lang,
        setLang,
        dir,
        t,
        theme,
        themeMode,
        setThemeMode,
        toggleTheme,
        perfMode,
        togglePerfMode,
        soundFx,
        toggleSoundFx,
        cookieConsent,
        setConsent,
        user,
        userProfile,
        setUserProfile,
        welcomeOpen,
        setWelcomeOpen,
        errorModalOpen,
        setErrorModalOpen,
        activeErrorData,
        triggerErrorReport,
        triggerSuggestion,
        feedbackTab,
        setFeedbackTab,
        loginWithGoogle,
        logout
      }}
    >
      {children}
    </EcosystemContext.Provider>
  );
}

export function useEcosystem() {
  const context = useContext(EcosystemContext);
  if (!context) {
    throw new Error("useEcosystem must be used within an EcosystemProvider");
  }
  return context;
}
