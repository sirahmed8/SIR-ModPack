# 🍪 SIR ModPack — Cookie & Local Storage Policy
### *Version 1.0.0 • Effective August 2026*

---

## 🔍 1. Our Cookie Philosophy: Zero Tracking
**SIR ModPack** does **NOT** use tracking cookies, advertising beacons, or third-party behavioral profiling trackers.

---

## 💾 2. Essential Local Storage & Session State
Our Web Platform (`sir-modpack.web.app`) and Desktop Launchers utilize modern HTML5 `localStorage` and local JSON files strictly for essential functional operations:

| Storage Key / File | Scope | Purpose | Retention |
| :--- | :--- | :--- | :--- |
| `sir_lang` | Web Browser | Stores your interface language preference (`en` / `ar`) | Persistent |
| `sir_theme` | Web Browser | Stores your appearance preference (`dark` / `light`) | Persistent |
| `sir_linked_minecraft_user` | Web Browser | Caches your active claimed Minecraft IGN for 3D preview | Persistent |
| `sir_settings.json` | Desktop Launcher | Stores allocated RAM, resolution, and launch flags | Local File |
| `accounts.json` | Desktop Launcher | Stores your local offline and Microsoft account profiles | Local File |

---

## 🛡️ 3. Third-Party Services
- **Firebase Authentication:** When signing in with Google, Firebase creates secure session tokens (`auth_token`) solely to maintain your authenticated state.
- **Cloudflare CDN:** May set technical security cookies (`__cf_bm`) to distinguish legitimate human users from automated DDoS bots.

---

## 🧹 4. How to Manage or Clear Local Storage
You can clear all stored preferences at any time:
1. **In Browser:** Open Developer Tools (`F12`) ➔ *Application* ➔ *Storage* ➔ *Clear site data*.
2. **In SIR Launcher:** Navigate to *Settings* ➔ *Storage & Retention* ➔ click **`🧹 Deep Cache & Junk Cleaner`**.
