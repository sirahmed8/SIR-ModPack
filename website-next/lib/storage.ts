"use client";

/**
 * =============================================================================
 *   SIR ECOSYSTEM — HIGH-PERFORMANCE CLIENT STORAGE & CACHE ENGINE v1.0.0
 * =============================================================================
 * Provides:
 * 1. Synchronous Cookie Engine with SameSite & Expiry helpers.
 * 2. TTL-based LocalStorage cache with Stale-While-Revalidate (SWR) support.
 * 3. Personalization Matrix (Theme, Language, Eco Mode, Sound FX, Favorites).
 * 4. LocalStorage Usage & Optimization Telemetry.
 * =============================================================================
 */

// --- 1. COOKIE ENGINE ---
export function setCookie(name: string, value: string, days: number = 365): void {
  if (typeof document === "undefined") return;
  try {
    const d = new Date();
    d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
    const expires = "expires=" + d.toUTCString();
    const secure = window.location.protocol === "https:" ? ";Secure" : "";
    document.cookie = `${name}=${encodeURIComponent(value)};${expires};path=/;SameSite=Lax${secure}`;
  } catch (e) {
    console.warn("setCookie failed:", e);
  }
}

export function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  try {
    const cname = name + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === " ") {
        c = c.substring(1);
      }
      if (c.indexOf(cname) === 0) {
        return c.substring(cname.length, c.length);
      }
    }
  } catch (e) {
    console.warn("getCookie failed:", e);
  }
  return null;
}

export function deleteCookie(name: string): void {
  if (typeof document === "undefined") return;
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;SameSite=Lax`;
}

// --- 2. TTL-BASED STALE-WHILE-REVALIDATE CACHE ---
interface CacheEnvelope<T> {
  timestamp: number;
  ttl: number; // in milliseconds
  data: T;
}

export function cacheSet<T>(key: string, data: T, ttlSeconds: number = 300): void {
  if (typeof window === "undefined") return;
  try {
    const envelope: CacheEnvelope<T> = {
      timestamp: Date.now(),
      ttl: ttlSeconds * 1000,
      data
    };
    localStorage.setItem(`sir_cache_${key}`, JSON.stringify(envelope));
  } catch (e) {
    // If quota exceeded, prune oldest caches
    pruneExpiredCaches();
  }
}

export function cacheGet<T>(key: string): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(`sir_cache_${key}`);
    if (!raw) return null;
    const envelope: CacheEnvelope<T> = JSON.parse(raw);
    const isExpired = Date.now() - envelope.timestamp > envelope.ttl;
    if (isExpired) {
      return envelope.data; // Stale-while-revalidate pattern
    }
    return envelope.data;
  } catch (e) {
    return null;
  }
}

export function cacheRemove(key: string): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(`sir_cache_${key}`);
}

export function pruneExpiredCaches(): number {
  if (typeof window === "undefined") return 0;
  let prunedCount = 0;
  try {
    const now = Date.now();
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith("sir_cache_")) {
        try {
          const envelope: CacheEnvelope<any> = JSON.parse(localStorage.getItem(key) || "{}");
          if (envelope.timestamp && envelope.ttl && now - envelope.timestamp > envelope.ttl * 2) {
            localStorage.removeItem(key);
            prunedCount++;
          }
        } catch {
          localStorage.removeItem(key);
          prunedCount++;
        }
      }
    }
  } catch {}
  return prunedCount;
}

export function getStorageUsage(): { usedKb: number; itemsCount: number; cacheRatio: string } {
  if (typeof window === "undefined") return { usedKb: 0, itemsCount: 0, cacheRatio: "0%" };
  let totalBytes = 0;
  let cacheBytes = 0;
  const count = localStorage.length;

  for (let i = 0; i < count; i++) {
    const key = localStorage.key(i);
    if (key) {
      const val = localStorage.getItem(key) || "";
      const bytes = (key.length + val.length) * 2;
      totalBytes += bytes;
      if (key.startsWith("sir_cache_")) {
        cacheBytes += bytes;
      }
    }
  }

  const usedKb = Math.round(totalBytes / 1024);
  const cacheRatio = totalBytes > 0 ? `${Math.round((cacheBytes / totalBytes) * 100)}%` : "0%";
  return { usedKb, itemsCount: count, cacheRatio };
}

// --- 3. PERSONALIZATION & CONSENT MATRIX ---
export interface CookieConsentState {
  essential: boolean;
  preferences: boolean;
  cache: boolean;
  analytics: boolean;
  timestamp: number;
}

export const DEFAULT_CONSENT: CookieConsentState = {
  essential: true,
  preferences: true,
  cache: true,
  analytics: true,
  timestamp: Date.now()
};

export function getCookieConsent(): CookieConsentState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("sir_cookie_consent");
    if (raw) return JSON.parse(raw);
    const cookieRaw = getCookie("sir_consent_given");
    if (cookieRaw === "true") return DEFAULT_CONSENT;
  } catch {}
  return null;
}

export function saveCookieConsent(consent: CookieConsentState): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem("sir_cookie_consent", JSON.stringify(consent));
    setCookie("sir_consent_given", "true", 365);
    setCookie("sir_pref_cache", consent.cache ? "1" : "0", 365);
  } catch {}
}

// --- 4. FAVORITES & PERSONALIZATIONS ---
export function getFavoriteMods(): string[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem("sir_fav_mods") || "[]");
  } catch {
    return [];
  }
}

export function toggleFavoriteMod(modId: string): string[] {
  const current = getFavoriteMods();
  const next = current.includes(modId)
    ? current.filter(id => id !== modId)
    : [...current, modId];
  try {
    localStorage.setItem("sir_fav_mods", JSON.stringify(next));
  } catch {}
  return next;
}
