# 💎 SIR ModPack — Unified Minecraft Ecosystem
### *Unified Minecraft Platform • Desktop Suite • Shaders • Web Platform (v1.0.0)*

[![Next.js 16](https://img.shields.io/badge/Next.js-16.3-black?logo=next.js)](https://nextjs.org/)
[![React 19](https://img.shields.io/badge/React-19.0-61dafb?logo=react)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-38bdf8?logo=tailwindcss)](https://tailwindcss.com/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776ab?logo=python)](https://python.org/)
[![Java 25](https://img.shields.io/badge/Java-25-ed8b00?logo=openjdk)](https://openjdk.org/)
[![Fabric 0.19.4](https://img.shields.io/badge/Fabric-0.19.4-dbb183)](https://fabricmc.net/)
[![Platform: Official](https://img.shields.io/badge/Platform-Official%20Ecosystem-blue.svg)](LICENSE.md)
[![Privacy: Zero-Telemetry](https://img.shields.io/badge/Privacy-Zero--Telemetry-cyan.svg)](PRIVACY.md)
[![Tests: 403 Passing](https://img.shields.io/badge/Tests-403%2F403%20Passed-brightgreen.svg)](walkthrough.md)
[![Live: sir-modpack.web.app](https://img.shields.io/badge/Live-sir--modpack.web.app-orange.svg)](https://sir-modpack.web.app)


---

## 🌟 What is SIR ModPack?

**SIR ModPack** is an enterprise-grade, high-throughput Minecraft distribution and desktop suite unifying **Modern 26.2 (Fabric 0.19.4 with 221 active mods + ASM compatibility engine)** and **Legacy 1.8.9 (Forge PvP with 28 mods)** into a single cohesive experience. GitHub is utilized exclusively as a reliable distribution channel for high-speed download mirrors of the standalone desktop binaries, installer, and offline packages.

The suite provides standalone desktop binaries, direct native JVM execution, real-time Task Manager hardware telemetry, dedicated isolated dual shaders (**`SIR Modern Shader.zip`** and **`SIR Legacy Shader.zip`**), dual resource packs (**`SIR Modern.zip`** with Patrix 3D POM models and **`SIR Legacy.zip`** 32x PvP), dynamic ocean physics waves, zero-port multiplayer server hosting, and a Next.js 16 web hub.

---

## 📦 Core Applications

| Application | Binary / Portal | Description |
| :--- | :--- | :--- |
| **SIR Launcher** | `SIR Launcher.exe` | Standalone desktop launcher with native Direct JVM Launch Pipeline, Win32 Kernel Telemetry, 3D Skin Studio, Quick Presets, and GitHub Single-File Delta Auto-Healer. |
| **SIR Installer** | `SIR Installer.exe` | Autonomous auto-healing installer with CSS spring animations, cloud payload streaming, GitHub Delta Fetcher, and zero-data-loss upgrades. |
| **SIR Server Manager** | `SIR Server Manager.exe` | Dedicated multiplayer server manager with CSS spring animations, custom CyberSelect menus, live TPS gauges, and Playit.gg zero-port public tunneling. |
| **In-Game SIR Mod** | `sir-mod-26.2-1.0.0.jar` | Native client Fabric mod (Right-Shift) providing 9 competitive HUD overlays, 1.7 block-hitting, and instant latency polling. |
| **SIR Web Platform** | [sir-modpack.web.app](https://sir-modpack.web.app) | Next.js 16 web hub with 37 prerendered static routes, AI assistant, live server radar, and skin wardrobe. |

---

## 🎮 Profile Matrix & Presets

SIR ModPack is physically provisioned across **6 consolidated high-performance instance profiles**:

```
+-------------------------------------------------------------------------------------------------------------------------------+
| ARCHETYPE              | DIRECTORY          | MC VERSION | LOADER       | MODS COUNT | MEMORY ALLOC | SHADER PACK          | TARGET FPS |
+------------------------+--------------------+------------+--------------+------------+--------------+----------------------+------------+
| 26.2 Ultra Visuals     | 26.2-ultra         | 26.2       | Fabric 0.19  | 131 Mods   | 6GB – 12GB   | SIR Modern Shader    | 144+ FPS   |
| 26.2 Balanced          | 26.2-balanced      | 26.2       | Fabric 0.19  | 91 Mods    | 4GB – 8GB    | SIR Modern Shader    | 180+ FPS   |
| 26.2 Performance       | 26.2-performance   | 26.2       | Fabric 0.19  | 41 Mods    | 3GB – 6GB    | OFF (Sodium Boost)   | 350+ FPS   |
| 1.8.9 Ultra Visuals    | 1.8.9-ultra        | 1.8.9      | Forge 2318   | 28 Mods    | 3GB – 6GB    | SIR Legacy Shader    | 300+ FPS   |
| 1.8.9 Balanced PvP     | 1.8.9-balanced     | 1.8.9      | Forge 2318   | 28 Mods    | 2GB – 4GB    | SIR Legacy Shader    | 450+ FPS   |
| 1.8.9 Performance      | 1.8.9-performance  | 1.8.9      | Forge 2318   | 28 Mods    | 1.5GB – 3GB  | OFF (0ms RawInput)   | 600+ FPS   |
+------------------------+--------------------+------------+--------------+------------+--------------+----------------------+------------+
```

### 1-Click Video Preset Tiers:
- **Ultra Cinematic:** 16-chunk render distance, Patrix 3D POM models, volumetric raytraced shaders (`SIR Modern Shader.zip` / `SIR Legacy Shader.zip`).
- **Balanced (144Hz):** 12-chunk view, smooth lighting, crystal water refraction, and optimized shader pass (`SIR Modern Shader.zip` / `SIR Legacy Shader.zip`).
- **Performance (High FPS):** 8-chunk view, disabled shaders, immediate chunk builder (350+ FPS).
- **Competitive PvP (0ms):** 8-chunk view, disabled particle passes, raw mouse input, and instantaneous hit detection (500+ FPS).
- **Potato PC:** 4-chunk view, disabled shadows, fast leaves, and minimal overhead for low-end hardware (150+ FPS).

---

## ⚡ Quickstart Guide

### 1. Launch the Desktop Launcher:
Double-click `SIR Launcher.exe` or execute `SIR ModPack.exe --mode launcher`.

### 2. Deploy or Repair via Installer:
Double-click `SIR Installer.exe` to deploy or verify instances in `%APPDATA%\SIR ModPack\` with automatic cloud payload streaming.

### 3. Host a Dedicated Server:
Double-click `SIR Server Manager.exe` to manage local server instances with 1-click zero-port Playit.gg tunnels.

### 4. Access the Live Web Platform:
Visit [sir-modpack.web.app](https://sir-modpack.web.app) to browse servers, customize skins, explore shader galleries, and access live cloud synchronization.

---

## 🩺 Diagnostics & Health Verification

Run the automated 6-layer ecosystem doctor to verify binaries, shaders, packs, mods, and instance profiles:

```powershell
# Run ecosystem diagnostics (100% automated health check)
python ecosystem_doctor.py

# Run the complete automated test harness (368 tests across 26 suites)
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📜 Documentation & Legal Policies

- [🏗️ Architectural Blueprint & Specification](PROJECT_ARCHITECTURE_EXPLANATION.md)
- [💎 Full Engineering Walkthrough (v1.0.0)](walkthrough.md)
- [📜 Official Changelog & Release Notes](CHANGELOG.md)
- [🔒 Universal Privacy Policy](PRIVACY.md)
- [⚖️ Terms of Service](TERMS.md)
- [🍪 Cookie Policy](COOKIES.md)
- [📜 End User License Agreement (EULA)](EULA.md)
- [🤝 Master Community Agreements](AGREEMENTS.md)
- [📄 Software License](LICENSE.md)

---

## 📬 Contact & Community

- **Legal & Governance Official Email:** [a7medorabe7@gmail.com](mailto:a7medorabe7@gmail.com)
- **Official Support:** In-App Bug Reporter & Community Feedback (accessible in SIR Launcher and SIR Server Manager)
- **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **Web Platform:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **GitHub Organization:** [https://github.com/sirahmed8/SIR-ModPack](https://github.com/sirahmed8/SIR-ModPack)

---

# 💎 دليل منظومة SIR ModPack الشامل
### *المنصة الموحدة لماينكرافت • التطبيقات المكتبية • الشيدرز • بوابة الويب (الإصدار v1.0.0)*

---

## 🌟 ما هي منظومة SIR ModPack؟
**SIR ModPack** هي بيئة تشغيل موحدة فائقة الأداء للألعاب، تجمع بين نسختين متطورتين: **Modern 26.2 (Fabric مع 221 مود ومحرك معالجة بايتكود ASM)** و **Legacy 1.8.9 (Forge PvP مع 28 مود)** في تجربة استثنائية واحدة.

تتضمن المنظومة تطبيقات مكتبية تنفيذية مستقلة، وإطلاقاً مباشراً عبر بيئات JVM الأصلية، وشيدرز حصرية معزولة (**`SIR Modern Shader.zip`** و **`SIR Legacy Shader.zip`**)، وحزم موارد متطورة (**`SIR Modern.zip`** مع مجسمات 3D POM وحزمة **`SIR Legacy.zip`** 32x PvP)، ومحاكاة فيزيائية واقعية للأمواج والمياه، واستضافة خوادم متكاملة بضغطة زر واحدة بدون فتح بورتات، وبوابة ويب Next.js 16 كاملة.

---

## 📦 التطبيقات الأساسية

| التطبيق | الملف التنفيذي | الوصف |
| :--- | :--- | :--- |
| **مشغل SIR Launcher Pro** | `SIR Launcher.exe` | مشغل مكتبي فائق السرعة مع استوديو سكنات ثلاثي الأبعاد، وأنماط فيديو سريعة، واستشفاء ذاتي سحابي. |
| **مثبت الحزمة SIR Installer** | `SIR Installer.exe` | مثبت ذكي مع فحص استباقي للعتاد، وسرعة استخراج لحظية، وعدم فقدان لأي بيانات. |
| **مدير الخوادم SIR Server Manager** | `SIR Server Manager.exe` | مدير خوادم احترافي يدعم أنفاق Playit.gg المدمجة، ورسم بياني لـ TPS، ومراقبة الذاكرة. |
| **بوابة الويب الرسمية** | [sir-modpack.web.app](https://sir-modpack.web.app) | بوابة Next.js 16 تضم 32 مساراً ساكناً، ومساعد ذكاء اصطناعي، ورادار سيرفرات حي، واستوديو سكنات. |

---

## 🎮 مصفوفة البروفايلات (8 بروفايلات فيزيائية مجهزة)
- **Modern 26.2:** بروفايل Ultra للواقعية السينمائية (144+ FPS)، بروفايل Balanced المتوازن (180+ FPS)، بروفايل Performance عالي الأداء (350+ FPS)، وبروفايل Vanilla+ الأصيل (240+ FPS).
- **Legacy 1.8.9:** بروفايل PvP Battle Suite التنافسي (500+ FPS)، بروفايل Ultra Visuals، بروفايل Balanced Bedwars، وبروفايل Zero-Delay Max FPS (600+ FPS).

---

## ⚡ دليل البدء السريع
1. **تشغيل المشغل:** شغّل `SIR Launcher.exe` مباشرة من سطح المكتب.
2. **التثبيت والإصلاح:** شغّل `SIR Installer.exe` للتحقق من سلامة كافة الملفات محلياً.
3. **استضافة سيرفر مخصص:** شغّل `SIR Server Manager.exe` لتشغيل خادمك ومشاركة الرابط العام فوراً.
4. **زيارة بوابة الويب:** افتح [sir-modpack.web.app](https://sir-modpack.web.app) لاستعراض السكنات والأوشحة ومزامنة الحسابات.

---

## 📬 التواصل والدعم
- **البريد الإلكتروني الرسمي للحوكمة والشؤون القانونية:** [a7medorabe7@gmail.com](mailto:a7medorabe7@gmail.com)
- **الدعم الفني الرسمي:** أداة الإبلاغ عن المشكلات المدمجة (Bug Reporter) داخل مشغل SIR Launcher ومدير الخوادم.
- **رابط المطور:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **بوابة الويب:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **منظمة GitHub:** [https://github.com/sirahmed8/SIR-ModPack](https://github.com/sirahmed8/SIR-ModPack)

*© 2026 منظومة SIR ModPack. تطوير وإشراف SIR Ahmed.*
