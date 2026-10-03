# SIR ModPack: Cookie & Local Storage Governance Policy
### *Version 1.0.1 Official Release | Legally Enforced Transparency (October 2026)*

---

## 1. Overview & Zero-Tracker Guarantee
The SIR Web Platform (`sir-modpack.web.app`) operated by **SIR ModPack Gaming Technologies & Digital Media** (Cairo, Egypt) uses **zero advertising cookies**, **zero third-party marketing beacons**, and **zero cross-site tracking scripts**. We only utilize necessary browser storage mechanisms (`localStorage`, `sessionStorage`, and essential functional cookies) to maintain your preferences and accelerate page delivery.

---

## 2. Comprehensive Client Storage Matrix

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

## 3. User Controls & 1-Click Cache Management
- **Interactive Storage Studio:** You can inspect real-time storage usage and prune expired cache items anytime at [`/cookies`](https://sir-modpack.web.app/cookies).
- **1-Click Local Purge:** You can completely clear all cached profiles and local settings directly in your browser or via the desktop launcher settings.

---

## 4. Operating Entity & Legal Inquiries
- **Operating Legal Entity:** **SIR ModPack Gaming Technologies & Digital Media**
- **Headquarters & Jurisdiction:** Cairo, Arab Republic of Egypt
- **Legal & Governance Official Email:** [a7medorabe7@gmail.com](mailto:a7medorabe7@gmail.com)
- **Official Support Phone / Hotline:** [+20 102 717 9040](tel:+201027179040)
- **Official In-App Support:** In-App Bug Reporter & Community Feedback (accessible in SIR Launcher and SIR Server Manager)
- **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **Privacy Policy:** [PRIVACY.md](PRIVACY.md)

---

# وثيقة سياسة ملفات تعريف الارتباط والتخزين المحلي لمنظومة SIR ModPack
### *الإصدار v1.0.1 الرسمي | منظومة برمجية متطورة ومستقلة | شفافية تقنية كاملة وانعدام تام للتتبع (أكتوبر 2026)*

---

## 1. نظرة عامة وضمان انعدام التتبع الإعلاني
تستخدم منصة SIR ModPack (`sir-modpack.web.app`) المشغلة بواسطة **شركة SIR ModPack Gaming Technologies & Digital Media** (القاهرة، مصر) **صفر ملفات تعريف ارتباط إعلانية**، و**صفر أدوات تتبع تسويقية**، و**صفر سكريبتات مراقبة عبر المواقع**. نستخدم حصرياً آليات التخزين المحلية الضرورية في المتصفح (`localStorage`، و`sessionStorage`، وكوكيز وظيفية أساسية) لتذكر تفضيلاتك وتسريع استجابة الواجهة.

---

## 2. جدول عناصر التخزين المحلي والتقني

| المفتاح البرمجي | آلية التخزين | الفئة | الغرض التقني والوظيفي | فترة الصلاحية |
|---|---|---|---|---|
| `sir_lang` | Cookie & LocalStorage | أساسي | حفظ لغة الواجهة (`ar` أو `en`) | 365 يوماً |
| `sir_theme_mode` | LocalStorage & Cookie | تفضيلات | تذكر نمط المظهر المفضل (`dark`، `light`، `system`) | دائم |
| `sir_perf_mode` | LocalStorage & Cookie | تفضيلات | حفظ تفعيل نمط توفير الموارد واستهلاك العتاد | دائم |
| `sir_sound_fx` | LocalStorage | تفضيلات | تذكر خيار تفعيل أو كتم المؤثرات الصوتية | دائم |
| `sir_cookie_consent` | LocalStorage | أساسي | تسجيل موافقة المستخدم وخيارات الخصوصية | 365 يوماً |
| `sir_consent_given` | Cookie | أساسي | إشارة سريعة لتسجيل الموافقة وتخطي النافذة | 365 يوماً |
| `sir_pref_cache` | Cookie | وظيفي | تمكين التخزين المؤقت فائق السرعة للبيانات | 365 يوماً |
| `sir_fav_mods` | LocalStorage | تفضيلات | قائمة المودات المفضلة المحفوظة للمستخدم | دائم |
| `sir_linked_minecraft_user` | LocalStorage | وظيفي | حفظ اسم اللاعب المعروض لتسريع رسم الترويسة | دائم |
| `sir_linked_account_type` | LocalStorage | وظيفي | نوع الحساب المرتبط (`microsoft` أو `offline`) | دائم |
| `sir_custom_skin_data` | LocalStorage | وظيفي | حفظ رابط نسيج السكن ثلاثي الأبعاد المطبق | دائم |
| `sir_benchmark_records` | LocalStorage | وظيفي | تخزين نتائج اختبارات CPS وسرعة رد الفعل محلياً | دائم |
| `sir_cache_*` | LocalStorage | وظيفي (مؤقت) | تخزين بيانات المودات والشيدرز مؤقتاً لتسريع التصفح | 5 دقائق |

---

## 3. التحكم الإداري ومسح التخزين بضغطة زر
- **استوديو التخزين التفاعلي:** يمكنك فحص وتعديل أو حذف أي عنصر من عناصر التخزين في أي وقت عبر صفحة [`/cookies`](https://sir-modpack.web.app/cookies).
- **المسح الشامل الفوري:** يمكنك تفريغ كافة البيانات المؤقتة والإعدادات بضغطة زر واحدة من داخل إعدادات اللانشر المكتبي أو المتصفح.

---

## 4. الكيان المشغل وقنوات الدعم والتواصل
- **الكيان القانوني المشغل:** **SIR ModPack Gaming Technologies & Digital Media**
- **المقر القضائي والإداري:** القاهرة، جمهورية مصر العربية
- **البريد الإلكتروني الرسمي للحوكمة والشؤون القانونية:** [a7medorabe7@gmail.com](mailto:a7medorabe7@gmail.com)
- **الهاتف والخط الساخن الرسمي:** [+20 102 717 9040](tel:+201027179040)
- **الدعم الفني الرسمي:** أداة الإبلاغ المدمجة في اللانشر (Bug Reporter) وملاحظات المجتمع.
- **رابط المطور:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **الموقع الرسمي:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **سياسة الخصوصية:** [PRIVACY.md](PRIVACY.md)

---
*© 2026 شركة SIR ModPack Gaming Technologies & Digital Media. تطوير وإشراف SIR Ahmed.*
