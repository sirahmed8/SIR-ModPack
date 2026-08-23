# 🔒 SIR ModPack — Universal Privacy Policy
### *Version 1.0.0 • Effective August 2026*

---

## 🛡️ 1. Executive Summary & Privacy-by-Design
At **SIR ModPack**, we hold privacy as a fundamental human right. The entire SIR Ecosystem—including the **SIR Launcher**, **SIR Installer**, **SIR Server Host Studio**, **Web Platform**, and in-game mods—is engineered from the ground up on the principle of **Zero-Telemetry & Privacy-by-Design**.

We do **NOT** track, monetize, sell, rent, or collect your personal gameplay data, browsing history, chat logs, or private credentials.

---

## 📊 2. Data Minimization & Collection Scope

### What We DO NOT Collect:
- ❌ **No Passwords or Credentials:** We never see or store your Microsoft / Mojang passwords. Official logins use secure OAuth 2.0 loopback redirects (`127.0.0.1:52135`).
- ❌ **No Telemetry or Tracking Cookies:** All external Prism tracking and analytics have been completely purged.
- ❌ **No Gameplay Surveillance:** We do not inspect singleplayer worlds, local block placements, or private server chats.

### What Is Stored Locally on Your PC:
- 💾 **Local Settings (`sir_settings.json`):** Your chosen theme, RAM allocation, resolution, and window state.
- 💾 **Local Instance Configurations (`instance.cfg`):** Java path, JVM flags, and active mods.
- 💾 **In-Game Account Switcher Tokens (IAS):** Encrypted local credentials for fast alt switching.

### Optional Cloud Features (With Explicit Consent):
- ☁️ **Web Account Sync & 3D Skins:** If you claim an In-Game Name (IGN) or upload a custom skin on `sir-modpack.web.app`, it is stored in Google Cloud Firestore with TLS 1.3 encryption to sync with your desktop launcher.
- ☁️ **Crash Reports & Suggestions:** If you explicitly click *"Send Error Report to Owner"* or *"Send a Suggestion"*, the error stack trace, hardware summary, and notes are logged in Firestore so our development team can diagnose issues.

---

## 🌐 3. Network Communication & Third-Party Endpoints
The launcher only connects to essential community endpoints:
1. **Mojang API & Cloudflare CDN:** To download authentic Minecraft release manifests and asset libraries.
2. **Modrinth API & CurseForge Catalog:** For in-launcher mod browsing and 1-click modpack updates.
3. **Firebase Cloud Highway:** For real-time broadcast announcements and optional web profile synchronization.

---

## 🗑️ 4. User Rights & Data Deletion
You maintain complete sovereignty over your data:
- **Instant Local Erase:** Use the built-in **`🧹 Deep Storage Cleaner`** to purge all cache, logs, and stored credentials with 1 click.
- **Cloud Account Deletion:** You may delete your cloud roster or claimed usernames at any time via the Web Account Hub.

---

## 📬 5. Contact & Inquiries
For privacy questions or data deletion requests, contact the project maintainer:
* **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
* **Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
