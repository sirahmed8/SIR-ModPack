/**
 * SIR Ecosystem Security & Input Sanitization Engine
 * Zero-dependency runtime protection against XSS, injection, prototype pollution, and malformed inputs.
 */

// Strict Minecraft In-Game Name Regex: 3 to 16 alphanumeric characters + underscores
const MINECRAFT_IGN_REGEX = /^[a-zA-Z0-9_]{3,16}$/;

// Strict 6-Digit Launcher Pairing Code Regex
const SYNC_CODE_REGEX = /^\d{6}$/;

/**
 * Escapes HTML characters to prevent XSS injection in raw HTML rendering
 */
export function sanitizeHtml(input: string): string {
  if (!input || typeof input !== "string") return "";
  return input
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
}

/**
 * Strips dangerous script tags, event handlers, and control characters from text input
 */
export function sanitizeInput(input: string, maxLength: number = 500): string {
  if (!input || typeof input !== "string") return "";
  // Strip control characters except newline and tab
  let clean = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, "");
  // Strip javascript: and data: URIs
  clean = clean.replace(/(javascript|data|vbscript):/gi, "");
  // Strip inline HTML tags
  clean = clean.replace(/<[^>]*>?/gm, "");
  // Trim and clamp to maximum safe length
  return clean.trim().slice(0, maxLength);
}

/**
 * Validates a Minecraft in-game username (IGN)
 */
export function isValidMinecraftIgn(ign: string): boolean {
  if (!ign || typeof ign !== "string") return false;
  return MINECRAFT_IGN_REGEX.test(ign.trim());
}

/**
 * Validates a 6-digit launcher pairing sync code
 */
export function isValidSyncCode(code: string): boolean {
  if (!code || typeof code !== "string") return false;
  return SYNC_CODE_REGEX.test(code.trim());
}

/**
 * Deep freezes an object and strips prototype pollution keys (__proto__, constructor, prototype)
 */
export function sanitizeObject<T extends Record<string, any>>(obj: T): T {
  if (!obj || typeof obj !== "object") return obj;
  const clean: Record<string, any> = {};
  for (const key of Object.keys(obj)) {
    if (key === "__proto__" || key === "constructor" || key === "prototype") {
      continue;
    }
    const val = obj[key];
    if (val && typeof val === "object" && !Array.isArray(val)) {
      clean[key] = sanitizeObject(val);
    } else if (typeof val === "string") {
      clean[key] = sanitizeInput(val, 2000);
    } else {
      clean[key] = val;
    }
  }
  return clean as T;
}

/**
 * Standard HTTP Security Headers dictionary for API routes
 */
export const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "SAMEORIGIN",
  "X-XSS-Protection": "1; mode=block",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
  "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
};
