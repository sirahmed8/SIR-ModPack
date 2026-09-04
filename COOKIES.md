# 🍪 SIR ModPack — Cookie & Local Storage Governance Policy
### *Version 1.1.0 (26.2) • Effective September 2026 • Legally Enforced Transparency*

---

## 🧭 1. Overview & Zero-Tracker Guarantee
The SIR Web Platform (`sir-modpack.web.app`) uses **zero advertising cookies**, **zero third-party marketing beacons**, and **zero cross-site tracking scripts**. We only utilize necessary browser storage mechanisms (`localStorage`, `sessionStorage`, and essential functional cookies) to maintain your preferences and accelerate page delivery.

---

## 📋 2. Comprehensive Client Storage Matrix

| Storage Key / Token | Storage Mechanism | Category | Technical Purpose | Lifespan |
|---|---|---|---|---|
| `sir_lang` | Cookie & LocalStorage | Essential | Stores interface language (`ar` or `en`) | 365 Days |
| `sir_theme_mode` | LocalStorage & Cookie | Preferences | Remembers visual theme mode (`dark`, `light`, `system`) | Persistent |
| `sir_perf_mode` | LocalStorage & Cookie | Preferences | Remembers Hardware Eco Mode toggle state | Persistent |
| `sir_sound_fx` | LocalStorage | Preferences | Remembers UI audio feedback and SFX toggle | Persistent |
| `sir_cookie_consent` | LocalStorage | Essential | Stores granular user cookie category permissions | 365 Days |
| `sir_consent_given` | Cookie | Essential | Signals that consent preferences have been recorded | 365 Days |
| `sir_pref_cache` | Cookie | Functional | Quick-check token for high-speed cache enablement | 365 Days |
| `sir_fav_mods` | LocalStorage | Preferences | Stores list of user favorited mod IDs | Persistent |
| `sir_linked_minecraft_user` | LocalStorage | Functional | Caches active display username for fast header rendering | Persistent |
| `sir_linked_account_type` | LocalStorage | Functional | Caches account category (`microsoft` or `offline`) | Persistent |
| `sir_custom_skin_data` | LocalStorage | Functional | Caches active 3D skin texture URL | Persistent |
| `sir_benchmark_records` | LocalStorage | Functional | Caches local CPS, reflex, and aim trainer scores | Persistent |
| `sir_cache_*` | LocalStorage | Functional (TTL) | Stale-While-Revalidate client cache for mods & shader data | 5 Minutes (TTL) |

---

## 🛠️ 3. User Controls & 1-Click Cache Management
- **Interactive Storage Studio:** You can inspect real-time storage usage and prune expired cache items anytime at [`/cookies`](https://sir-modpack.web.app/cookies).
- **1-Click Local Purge:** You can completely clear all cached profiles and local settings directly in your browser or via the desktop launcher settings.

---

## 📬 4. Contact & Legal Inquiries
- **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **Privacy Policy:** [PRIVACY.md](PRIVACY.md)

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
