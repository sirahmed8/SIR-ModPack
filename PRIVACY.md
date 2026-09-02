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
- ☁️ **Web Account Synchronization:** Linking an in-game name (IGN) on `sir-modpack.web.app` generates a temporary 6-digit sync code in Firebase Realtime Database (RTDB) with TLS 1.3 encryption (automatically expiring in 15 minutes) to pre-sync your 3D avatar and capes.
- ☁️ **Google OAuth Web Sign-In:** Optional sign-in on the web platform processes basic profile information (display name, email, avatar URL) strictly to persist your community bookmarks, scores, and preferences.
- ☁️ **Diagnostic Error Reports:** If you voluntarily submit an error report via the launcher or website, diagnostic logs, technical stack traces, and environment versions are logged to Firestore to help maintainers resolve bugs.
- ☁️ **Gemini AI Assistant:** Queries to the built-in AI assistant are processed securely via the Gemini API without associating conversations with persistent personal profiles.

---

## 🏛️ 3. Legal Basis for Processing (GDPR Article 6)
Under the EU General Data Protection Regulation (GDPR), personal data processing is justified strictly under:
- **Contractual Necessity (Art. 6(1)(b)):** Providing local launcher configuration, authenticating user sessions, and syncing user-requested web profiles.
- **Explicit Consent (Art. 6(1)(a)):** Generating temporary 6-digit synchronization codes, voluntary submission of diagnostic error reports, submitting community suggestions, and processing Gemini AI assistant queries.
- **Legitimate Interests (Art. 6(1)(f)):** Safeguarding ecosystem security, mitigating DDoS attacks, preventing malicious modifications, and maintaining local atomic file persistence.

---

## ⚖️ 4. Comprehensive Data Subject Rights (GDPR & International)
In accordance with GDPR (Articles 15–22) and international privacy frameworks, you have the right to:
1. **Right of Access (Art. 15):** Request a copy of all profile and diagnostic data associated with your account.
2. **Right to Rectification (Art. 16):** Update or correct inaccurate gamertags, skin links, or UI preferences.
3. **Right to Erasure ("Right to be Forgotten", Art. 17):** Request the immediate, permanent deletion of your cloud account and linked profiles.
4. **Right to Restriction of Processing (Art. 18):** Limit how your data is processed during disputes.
5. **Right to Data Portability (Art. 20):** Export your saved configurations and profiles in a standard JSON format.
6. **Right to Object (Art. 21):** Object at any time to processing based on legitimate interests.
7. **Automated Decision-Making (Art. 22):** We conduct ZERO automated decision-making or behavioral profiling.
8. **Right to Lodge a Complaint (Art. 77):** You hold the statutory right to file a complaint with your local EU Data Protection Authority.

---

## 🌴 5. California Consumer Privacy Notice (CCPA / CPRA)
*Pursuant to the California Consumer Privacy Act and California Privacy Rights Act:*
- **Notice at Collection:** In the preceding 12 months, we have collected:
  - *Identifiers:* In-Game Name (IGN), Google OAuth name and email (web account holders only), avatar image URLs, and device user-agent strings (voluntary error reports only).
  - *Internet/Network Activity:* Technical crash traces, display resolutions, and application error logs.
- **Do Not Sell or Share My Personal Information:** We do NOT sell personal information, and we do NOT share personal information with third parties for cross-context behavioral advertising.
- **Consumer Rights:** California residents have the Right to Know, Right to Delete, Right to Correct, and Right to Non-Discrimination for exercising their privacy rights. Submit requests via `privacy@sir-modpack.web.app`.

---

## 👶 6. Children’s Online Privacy Protection Policy (COPPA)
Protecting the privacy of young players is of paramount importance:
- **General Audience Service:** The SIR ModPack Ecosystem is a general audience service. We do NOT knowingly collect, solicit, or maintain personal information from children under the age of 13 without verifiable parental consent.
- **Local-First Gameplay:** Children under 13 may freely use the SIR Desktop Launcher for local singleplayer and LAN gameplay without registering a cloud account or transmitting personal data. All configurations remain 100% local on the client device under `%APPDATA%\SIR ModPack\`.
- **Parental Inquiries & Deletion:** If a parent or guardian discovers that their child under 13 has submitted personal information (such as an email or profile) without consent, contact us immediately at `privacy@sir-modpack.web.app`. We will promptly and permanently purge all such records from our databases.

---

## 🌐 7. Sub-Processors & International Data Transfers
Data is processed using industry-standard sub-processors under compliant Data Processing Agreements (DPAs) and Standard Contractual Clauses (SCCs):
- **Google Cloud Platform & Firebase (Google Ireland Ltd. / Google LLC):** Cloud Firestore, Realtime Database (europe-west1), and Firebase Authentication.
- **Cloudflare, Inc.:** Content Delivery Network (CDN) caching, SSL termination, and DDoS mitigation.
- **Cloudinary Ltd.:** Optimized delivery of non-personal graphical assets and 3D skin renders.
- **Google Gemini API (Alphabet Inc.):** Natural language AI assistant queries (processed statelessly without persistent user profiling).
- **Crafatar / MC-Heads:** Public Minecraft avatar and cape render mirrors.

---

## 🔒 8. Multi-Layer Security Architecture
- **Universal Atomic Persistence:** Staging temp files with Windows NTFS exponential backoff locking protects against data corruption.
- **Input Sanitization:** All text strings and player identifiers are filtered against XSS injection, prototype pollution, and malformed characters via `lib/security.ts`.
- **HTTP Security Headers:** Strict transport security (HSTS), frame-guard protection (`X-Frame-Options: SAMEORIGIN`), and MIME-sniffing prevention (`nosniff`) protect every web transaction.
- **Loopback Bridge Isolation:** Desktop local endpoints bind strictly to `127.0.0.1` and verify origin integrity with constant-time token comparison.

---

## 🗑️ 9. Data Retention & User Deletion Rights
- **Instant Local Erase:** Use the built-in Storage Cleaner in the launcher to purge all cache, logs, and stored credentials in 1 click.
- **Cloud Account Deletion:** Permanent deletion of any linked web profiles is available at any time via the Web Account Hub.

---

## 📬 10. Contact & Legal Inquiries
* **Data Protection & Legal Email:** [a7medorabe7@gmail.com](mailto:a7medorabe7@gmail.com)
* **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
* **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
* **Official Documentation:** [PROJECT_ARCHITECTURE_EXPLANATION.md](PROJECT_ARCHITECTURE_EXPLANATION.md)

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
