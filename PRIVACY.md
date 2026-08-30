# 🔒 SIR ModPack — Universal Privacy Policy
### *Version 1.0.0 (2026.2) • Effective August 2026 • Legally Enforced Compliance*

---

## 🛡️ 1. Executive Summary & Privacy-by-Design
At **SIR ModPack**, user privacy and digital sovereignty are non-negotiable principles. The entire SIR Ecosystem—including the **SIR Desktop Launcher**, **SIR Installer Suite**, **SIR Server Orchestrator**, **Web Platform (`sir-modpack.web.app`)**, and associated modules—is engineered on the strict foundation of **Zero-Telemetry & Privacy-by-Design**.

We do **NOT** track, monetize, sell, lease, or aggregate your personal gameplay activity, private browsing history, multiplayer chat logs, or personal credentials.

---

## 📊 2. Data Minimization & Collection Scope

### What We DO NOT Collect:
- ❌ **No Passwords or Sensitive Credentials:** We never store or handle your Microsoft, Xbox Live, or Mojang passwords. Official logins use secure OAuth 2.0 PKCE loopback authentication directly with official Microsoft identity servers binding to localhost (`127.0.0.1`).
- ❌ **No Behavioral Telemetry:** All third-party analytics, behavioral profiling, and tracking beacons have been completely eliminated.
- ❌ **No Gameplay Surveillance:** We do not inspect singleplayer worlds, local block coordinates, inventories, or private server communications.

### What Is Stored Exclusively on Your PC:
- 💾 **Local Settings:** Visual themes, RAM allocations, JVM runtime flags, screen resolutions, and visual preferences stored safely under `%APPDATA%\SIR ModPack\`.
- 💾 **Local Instance Configurations:** Configured mod states, shader options, resource packs, and physical world save files.
- 💾 **In-Game Account Switcher (IAS):** Local profile tokens for offline/cracked alts stored locally in your `.minecraft` instance directory.

### Optional Cloud Features (Explicit User Consent Only):
- ☁️ **Web Account Synchronization:** Linking an in-game name (IGN) on `sir-modpack.web.app` creates a temporary 6-digit sync code in Firebase Realtime Database (RTDB) with TLS 1.3 encryption to pre-sync your 3D avatar head and capes.
- ☁️ **Diagnostic Error Reports:** If you explicitly choose to submit an error report via the launcher or website, only technical stack traces and environment versions are logged to Firestore to assist developers in troubleshooting.
- ☁️ **Gemini AI Assistant:** Queries to the built-in AI assistant are processed securely via the Gemini API without associating conversations with persistent personal profiles.

---

## 🔒 3. Multi-Layer Security Architecture
- **Universal Atomic Persistence:** Staging temp files with Windows NTFS exponential backoff locking protects against data corruption.
- **Input Sanitization:** All text strings and player identifiers are filtered against XSS injection, prototype pollution, and malformed characters via `lib/security.ts`.
- **HTTP Security Headers:** Strict transport security (HSTS), frame-guard protection (`X-Frame-Options: SAMEORIGIN`), and MIME-sniffing prevention (`nosniff`) protect every web transaction.
- **Loopback Bridge Isolation:** Desktop local endpoints bind strictly to `127.0.0.1` and verify origin integrity with constant-time token comparison.

---

## 🗑️ 4. Data Retention & User Deletion Rights
- **Instant Local Erase:** Use the built-in Storage Cleaner in the launcher to purge all cache, logs, and stored credentials in 1 click.
- **Cloud Account Deletion:** Permanent deletion of any linked web profiles is available at any time via the Web Account Hub.

---

## 📬 5. Contact & Legal Inquiries
* **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
* **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
* **Official Documentation:** [PROJECT_ARCHITECTURE_EXPLANATION.md](PROJECT_ARCHITECTURE_EXPLANATION.md)

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
