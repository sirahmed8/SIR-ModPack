# 🍪 SIR ModPack — Cookie & Local Storage Governance Policy
### *Version 2026.2 • Effective August 2026 • Legally Enforced Transparency*

---

## 🧭 1. Overview & Zero-Tracker Guarantee
The SIR Web Platform (`sir-modpack.web.app`) uses **zero advertising cookies**, **zero third-party marketing beacons**, and **zero cross-site tracking scripts**. We only utilize necessary browser storage mechanisms (`localStorage`, `sessionStorage`, and essential functional cookies) to maintain your preferences and accelerate page delivery.

---

## 📋 2. Storage Matrix & Purpose

| Key / Token | Storage Type | Purpose | Lifespan |
|---|---|---|---|
| `sir_lang` | Cookie / LocalStorage | Stores selected interface language (`ar` or `en`) | 365 Days |
| `sir_theme` | LocalStorage | Remembers visual theme mode (`dark`, `light`, `system`) | Persistent |
| `sir_perf_mode` | LocalStorage | Remembers Hardware Eco Mode toggle state | Persistent |
| `sir_cookies_consent` | LocalStorage | Stores cookie governance and consent settings | 365 Days |
| `swr_cache_*` | SessionStorage | Client-side cache accelerating repeat subpage loads | 5 Minutes (TTL) |

---

## 🛠️ 3. User Controls & 1-Click Cache Management
- **Interactive Storage Studio:** You can inspect real-time storage usage and prune expired cache items anytime at [`/cookies`](https://sir-modpack.web.app/cookies).
- **1-Click Local Purge:** You can completely clear all cached profiles and local settings directly in your browser or via the desktop launcher settings.

---

*© 2026 SIR ModPack Ecosystem. Developed by SIR Ahmed.*
