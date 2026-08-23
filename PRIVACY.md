# 🔒 SIR ModPack — Universal Privacy Policy
### *Version 2026.1 • Effective August 2026 • Legally Enforced Compliance*

---

## 🛡️ 1. Executive Summary & Privacy-by-Design
At **SIR ModPack**, user privacy and digital sovereignty are absolute principles. The entire SIR Ecosystem—including the **SIR Desktop Launcher**, **SIR Installer Suite**, **SIR Server Orchestrator Pro**, **Web Platform (`sir-modpack.web.app`)**, and associated client-side modules—is built on the strict principle of **Zero-Telemetry & Privacy-by-Design**.

We do **NOT** track, monetize, sell, lease, or aggregate your personal gameplay activity, private browsing history, multiplayer chat logs, or personal credentials.

---

## 📊 2. Data Minimization & Collection Scope

### What We DO NOT Collect:
- ❌ **No Passwords or Credentials:** We never store or handle your Microsoft, Xbox Live, or Mojang passwords. Official logins use secure OAuth 2.0 PKCE loopback authentication directly with Microsoft servers.
- ❌ **No Telemetry or Tracking Trackers:** All third-party analytics, behavioral profiling, and tracking beacons have been completely eliminated.
- ❌ **No Gameplay Surveillance:** We do not inspect singleplayer worlds, local block coordinates, inventories, or private server communications.

### What Is Stored Exclusively on Your PC:
- 💾 **Local Settings:** Visual themes, RAM allocations, JVM runtime flags, screen resolutions, and audio preferences.
- 💾 **Local Instance Configurations:** Configured mod states, shader options, resource packs, and physical world save files.
- 💾 **In-Game Account Switcher (IAS):** Local profile tokens for offline/cracked alts stored locally in your `.minecraft` instance directory.

### Optional Cloud Features (Explicit User Consent Only):
- ☁️ **Web Account Synchronization:** Linking an in-game name (IGN) on `sir-modpack.web.app` creates a temporary 6-digit sync code in Firebase Realtime Database (RTDB) with TLS 1.3 encryption to pre-sync your 3D avatar head and capes.
- ☁️ **Diagnostic Error Reports:** If you explicitly choose to submit an error report via the launcher or website, only technical stack traces and environment versions are logged to Firestore to assist developers in troubleshooting.

---

## 🌐 3. Network Communication Endpoints
The software communicates exclusively with verified endpoints:
1. **Mojang API & Cloudflare CDN:** Verification of official UUIDs and download of authentic Minecraft libraries.
2. **Firebase Cloud Gateway:** Checking for optional client updates and real-time announcements.
3. **Player Head API (`mc-heads.net`):** Dynamic retrieval of public player skin avatars.

---

## 🗑️ 4. Data Retention & User Deletion Rights
- **Instant Local Erase:** Use the built-in Deep Storage Cleaner in the launcher to purge all cache, logs, and stored credentials in 1 click.
- **Cloud Account Deletion:** Permanent deletion of any linked web profiles is available at any time via the Web Account Hub.

---

## ⚖️ 5. Legal Compliance & Limitation of Liability
By using the SIR Ecosystem, you acknowledge and agree that your data is processed strictly in accordance with this Privacy Policy and international privacy standards (GDPR, CCPA).

---

## 📬 6. Contact & Legal Inquiries
* **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
* **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)\n