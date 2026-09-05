# 🔒 SIR ModPack — Universal Privacy Policy
### *Version 1.0.0 Production Genesis • 100% Free & Independent Platform • Legally Enforced Compliance*

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
- ☁️ **Web Account Synchronization:** Direct Google OAuth login allows you to securely sync your preferences, favorites, and 3D avatar custom textures to Firebase Realtime Database under your secure user profile `/users/{uid}/` using TLS 1.3 encryption.
- ☁️ **Google OAuth Web Sign-In:** Optional sign-in on the web platform processes basic profile information (display name, email, avatar URL) strictly to persist your community bookmarks, scores, and preferences.
- ☁️ **Diagnostic Error Reports:** If you voluntarily submit an error report via the launcher or website, diagnostic logs, technical stack traces, and environment versions are logged to Firestore to help maintainers resolve bugs.
- ☁️ **Gemini AI Assistant:** Queries to the built-in AI assistant are processed securely via the Gemini API without associating conversations with persistent personal profiles.

---

## 🏛️ 3. Legal Basis for Processing (GDPR Article 6)
Under the EU General Data Protection Regulation (GDPR), personal data processing is justified strictly under:
- **Contractual Necessity (Art. 6(1)(b)):** Providing local launcher configuration, authenticating user sessions, and syncing user-requested web profiles.
- **Explicit Consent (Art. 6(1)(a)):** Direct Google OAuth synchronization, voluntary submission of diagnostic error reports, submitting community suggestions, and processing Gemini AI assistant queries.
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
- **Consumer Rights:** California residents have the Right to Know, Right to Delete, Right to Correct, and Right to Non-Discrimination for exercising their privacy rights. Submit requests via the in-app Bug Reporter & Community Feedback portal.

---

## 👶 6. Children’s Online Privacy Protection Policy (COPPA)
Protecting the privacy of young players is of paramount importance:
- **General Audience Service:** The SIR ModPack Ecosystem is a general audience service. We do NOT knowingly collect, solicit, or maintain personal information from children under the age of 13 without verifiable parental consent.
- **Local-First Gameplay:** Children under 13 may freely use the SIR Desktop Launcher for local singleplayer and LAN gameplay without registering a cloud account or transmitting personal data. All configurations remain 100% local on the client device under `%APPDATA%\SIR ModPack\`.
- **Parental Inquiries & Deletion:** If a parent or guardian discovers that their child under 13 has submitted personal information (such as an email or profile) without consent, submit an inquiry via the in-app Bug Reporter & Community Feedback portal. We will promptly and permanently purge all such records from our databases.

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
- **ASM Bytecode Compatibility Processing:** The SIR Launcher performs local-only ASM bytecode transformations on installed mod JAR files to ensure compatibility with Minecraft 26.2's official namespace. This processing occurs entirely on your local machine — no mod bytecode, class data, or transformation results are ever transmitted externally.

---

## 🗑️ 9. Data Retention & User Deletion Rights
- **Instant Local Erase:** Use the built-in Storage Cleaner in the launcher to purge all cache, logs, and stored credentials in 1 click.
- **Cloud Account Deletion:** Permanent deletion of any linked web profiles is available at any time via the Web Account Hub.

---

## 📬 10. Contact & Legal Inquiries
* **Official Support:** In-App Bug Reporter & Community Feedback (accessible in SIR Launcher and SIR Server Manager)
* **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
* **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
* **Official Documentation:** [PROJECT_ARCHITECTURE_EXPLANATION.md](PROJECT_ARCHITECTURE_EXPLANATION.md)

---

# 🔒 وثيقة سياسة الخصوصية الرسمية لمنظومة SIR ModPack
### *الإصدار 1.0.0 Genesis الإنتاجي • منصة مجانية ومستقلة بنسبة 100% • امتثال قانوني وأمان رقمي صارم*

---

## 🛡️ 1. الملخص التنفيذي والخصوصية المدمجة بالتصميم (Privacy-by-Design)
تعتبر خصوصية المستخدم وسيادته الرقمية في **SIR ModPack** مبدأً أصيلاً غير قابل للمساومة. تم بناء وهندسة المنظومة بالكامل — بما في ذلك **مشغل SIR Launcher**، و**مثبت SIR Installer**، و**مدير الخوادم SIR Server Manager**، و**بوابة الويب (`sir-modpack.web.app`)** — وفق مبدأ **انعدام التتبع التام والخصوصية بالتصميم (Zero-Telemetry & Privacy-by-Design)**.

نحن **لا نقوم** بتتبع أو بيع أو تأجير أو تحقيق مكاسب من نشاط لعبك، أو سجل تصفحك، أو محادثات السيرفرات الخاصة، أو بيانات اعتمادك.

---

## 📊 2. تقليل البيانات ونطاق الجمع

### ما لا نقوم بجمعه إطلاقاً:
- ❌ **لا كلمات مرور أو بيانات حساسة:** لا نخزن أو نعالج إطلاقاً كلمات مرور Microsoft أو Xbox Live أو Mojang. تستخدم عمليات تسجيل الدخول الرسمية مصادقة OAuth 2.0 PKCE loopback الآمنة مباشرة مع خوادم هوية Microsoft الرسمية المرتبطة بـ localhost (`127.0.0.1`).
- ❌ **لا تتبع سلوكي أو إعلاني:** تم التخلص بالكامل من جميع أدوات التحليل الخارجية والملفات الإعلانية وحزم التتبع.
- ❌ **لا مراقبة لطريقة اللعب:** لا نفحص العوالم الفردية، أو إحداثيات البلوكات المحلية، أو المخزون، أو محادثات السيرفرات الخاصة.

### ما يتم تخزينه محلياً على جهازك فقط:
- 💾 **الإعدادات المحلية:** السمات المرئية، تخصيص الذاكرة العشوائية RAM، معلمات وقت تشغيل JVM، دقة الشاشة، والتفضيلات المرئية المحفوظة بأمان في مسار `%APPDATA%\SIR ModPack\`.
- 💾 **تكوينات النسخ المحلية:** حالات المودات المفعلة، خيارات الشيدرز، حزم الموارد، وملفات حفظ العوالم الفيزيائية.
- 💾 **محول الحسابات داخل اللعبة (IAS):** رموز البروفايلات المحلية لحسابات الأوفلاين المحفوظة محلياً في مجلد النسخة الخاص بك.

### الميزات السحابية الاختيارية (بموافقة المستخدم الصريحة فقط):
- ☁️ **مزامنة الحسابات السحابية:** ربط الحساب عبر تسجيل الدخول المباشر Google OAuth يتيح مزامنة التفضيلات والإعدادات السحابية بتشفير TLS 1.3 وحفظ السكن ثلاثي الأبعاد والكاب بأمان في Firebase Realtime Database تحت معرفك الآمن `/users/{uid}/`.
- ☁️ **تسجيل الدخول عبر Google OAuth:** تسجيل الدخول المباشر يعالج معلومات الملف الأساسية (الاسم، البريد، الصورة) فقط للاحتفاظ بالمفضلة والنقاط والتفضيلات.
- ☁️ **تقارير الأخطاء التشخيصية:** عند إرسال تقرير خطأ طوعياً، يتم تسجيل تقارير الأعطال وتتبع الأخطاء البرمجية وإصدارات النظام في Firestore لمساعدة المطورين في حل المشكلات.
- ☁️ **مساعد الذكاء الاصطناعي Gemini:** تتم معالجة استفسارات المساعد الذكي بأمان عبر Gemini API دون ربط المحادثات ببروفايلات شخصية دائمة.

---

## 🏛️ 3. الأساس القانوني للمعالجة (GDPR المادة 6)
تتم معالجة البيانات وفقاً للائحة العامة لحماية البيانات (GDPR) استناداً إلى:
- **ضرورة تنفيذ العقد (المادة 6(1)(b)):** توفير تشغيل اللانشر المحلي ومزامنة الإعدادات بطلب المستخدم.
- **الموافقة الصريحة (المادة 6(1)(a)):** تسجيل الدخول عبر Google OAuth وتقديم تقارير الأعطال التشخيصية ومحادثة المساعد الذكي.
- **المصالح المشروعة (المادة 6(1)(f)):** حماية أمن المنظومة ومنع التعديلات الخبيثة وضمان استقرار الملفات محلياً.

---

## 🔒 4. بنية الأمان متعددة الطبقات
- **التخزين الذري الشامل:** كتابة الملفات المؤقتة مع نظام القفل المتدرج لنظام Windows NTFS يحمي من تلف ملفات الإعدادات عند انقطاع الطاقة.
- **تنقية المدخلات:** فحص وتعقيم كافة النصوص عبر `lib/security.ts` ضد هجمات XSS وحقن البيانات.
- **ترويسات أمان HTTP:** تفعيل معايير HSTS و `X-Frame-Options: SAMEORIGIN` و `nosniff` وسياسة أمان المحتوى الصارمة CSP.
- **عزل جسر المعالجة المحلي:** يرتبط الجسر المكتبي حصرياً بـ `127.0.0.1` مع التحقق برمز أمان في زمن ثابت.

---

## 🗑️ 5. الاحتفاظ بالبيانات وحقوق الحذف
- **مسح فوري محلي:** يمكنك استخدام منظف التخزين المدمج في اللانشر لحذف جميع الملفات المؤقتة والسجلات بضغطة زر واحدة.
- **حذف الحساب السحابي:** يمكنك طلب الحذف النهائي والفوري لأي بروفايل سحابي في أي وقت عبر بوابة الويب.

---

## 📬 6. الدعم الفني والاستفسارات
- **الدعم الرسمي:** أداة الإبلاغ عن المشكلات المدمجة (Bug Reporter) وملاحظات المجتمع داخل SIR Launcher و SIR Server Manager.
- **رابط المطور:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **الموقع الرسمي:** [https://sir-modpack.web.app](https://sir-modpack.web.app)

*© 2026 منظومة SIR ModPack. تطوير وإشراف SIR Ahmed.*
