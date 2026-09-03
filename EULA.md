# 📜 SIR ModPack — End User License Agreement (EULA)
### *Version 1.0.0 (26.2) • Legally Enforced Software License & Usage Agreement*

---

## ⚖️ 1. Preamble & Acceptance
This End User License Agreement ("EULA") is a legal agreement between you (the "User") and the maintainers of the **SIR ModPack Ecosystem** ("SIR Ahmed", "We", or "Maintainers").

By downloading, installing, launching, executing, or using **SIR Launcher**, **SIR Installer**, **SIR Server Manager**, **SIR ModPack.exe**, custom **SIR Shaders**, **SIR Resource Packs**, or the **SIR Web Platform** (`sir-modpack.web.app`), you unconditionally agree to be bound by the terms and conditions set forth in this EULA. If you disagree with any provision of this EULA, you must immediately cease all usage and delete all installed files and binaries.

---

## 🎮 2. Mojang Studios & Microsoft Brand Compliance
**NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.**

1. **Independent Community Project:** Minecraft is a registered trademark of Mojang AB and Microsoft Corporation. The SIR ModPack Ecosystem is an independent community project and is **NOT an official Minecraft product**, nor is it approved by, associated with, or affiliated with Mojang AB or Microsoft.
2. **Commercial Use Guidelines:** This distribution complies with Mojang Studios' Commercial Usage Guidelines and Brand & Asset Guidelines. No proprietary Minecraft source code, vanilla game JARs, or official assets are sold or commercialized. All vanilla assets are fetched dynamically from official Mojang/Microsoft CDNs.

## 🔧 2.1 Bytecode Modification Acknowledgment
You acknowledge that the SIR Ecosystem performs automated ASM bytecode transformations on mod JAR files and the Minecraft base JAR to ensure cross-version compatibility with Minecraft 26.2. These modifications include:
- **Namespace remapping** from Fabric intermediary to official Mojang mappings
- **Access widener and class tweaker** header updates
- **Mixin injection target** method name corrections
- **Mojang signature stripping** on the base game JAR to allow patched classes

These transformations are performed locally on your machine and do not transmit any data externally.

---

## 🛡️ 3. Grant of License & Permitted Use
1. **Non-Commercial License:** You are granted a personal, non-exclusive, non-transferable, revocable license to download, install, and execute the SIR ModPack binaries and configurations for personal, non-commercial entertainment purposes.
2. **Open-Source Attribution:** Custom launcher scripts, web components, and orchestration tools authored by SIR Ahmed are licensed under open-source terms. Third-party mod JARs, shader passes, and resource pack textures remain under the copyright and license of their respective original authors.

---

## 🚫 4. Restrictions & Prohibited Conduct
You expressly agree NOT to:
- Distribute modified versions of SIR Launcher or Installer under the "SIR ModPack" trademark without prior written consent.
- Inject malicious payloads, spyware, trojans, ransomware, or unauthorized tracking telemetry into the software.
- Use the software in violation of third-party multiplayer server rules, terms of service, or applicable local and international laws.
- Exploit or attempt to bypass security protections, loopback auth tokens, or rate limits on official APIs or the SIR Web Platform.

---

## 🔒 5. Zero-Telemetry & Privacy Guarantee
In accordance with our [Privacy Policy](PRIVACY.md), the SIR Ecosystem operates on a strict **Zero-Telemetry & Privacy-by-Design** standard:
- No tracking cookies, advertising IDs, or background behavioral monitoring scripts are included.
- Microsoft account authentication is delegated securely to official Microsoft identity servers binding to localhost (`127.0.0.1`), with local tokens stored securely on the client machine.
- Desktop-to-web profile pairing utilizes a localized loopback bridge binding strictly to localhost (`127.0.0.1:52136`) with constant-time token verification.
- All user configurations, video presets, and custom profiles are stored locally on your device under `%APPDATA%\SIR ModPack\`.

---

## ⚠️ 6. Disclaimer of Warranties & Limitation of Liability
1. **"AS IS" Basis:** The SIR Ecosystem is provided on an **"AS IS"** and **"AS AVAILABLE"** basis without warranties of any kind, whether express, statutory, or implied, including but not limited to the implied warranties of merchantability, fitness for a particular purpose, title, and non-infringement.
2. **Limitation of Liability:** In no event shall the authors, maintainers, or contributors be held liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including loss of data, save corruption, server bans, or hardware malfunction) arising out of the use or inability to use this software.

---

## 🔄 7. Termination & Updates
This agreement is effective until terminated. Your rights under this license terminate automatically without notice if you fail to comply with any terms. The maintainers reserve the right to update this EULA periodically to reflect new features, security enhancements, and legal standards.

---

## 📬 8. Contact & Legal Inquiries
- **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **Official Web Platform:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **Official Documentation:** [PROJECT_ARCHITECTURE_EXPLANATION.md](PROJECT_ARCHITECTURE_EXPLANATION.md)

*© 2026 SIR ModPack Ecosystem. Developed with craftsmanship by SIR Ahmed.*
