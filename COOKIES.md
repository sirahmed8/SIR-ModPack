# 🍪 SIR ModPack — Cookie & Local Storage Governance Policy
### *Version 1.0.0 Production Genesis • 100% Free & Independent Platform • Legally Enforced Transparency*

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
- **Official Support:** In-App Bug Reporter & Community Feedback (accessible in SIR Launcher and SIR Server Manager)
- **Developer Linktree:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **Official Website:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **Privacy Policy:** [PRIVACY.md](PRIVACY.md)

---

# 🍪 وثيقة سياسة ملفات تعريف الارتباط والتخزين المحلي لمنظومة SIR ModPack
### *الإصدار 1.0.0 Genesis الإنتاجي • منصة مجانية ومستقلة بنسبة 100% • شفافية تقنية كاملة وانعدام تام للتتبع*

---

## 🧭 1. نظرة عامة وضمان انعدام التتبع الإعلاني
تستخدم منصة SIR ModPack (`sir-modpack.web.app`) **صفر ملفات تعريف ارتباط إعلانية**، و**صفر أدوات تتبع تسويقية**، و**صفر سكريبتات مراقبة عبر المواقع**. نستخدم حصرياً آليات التخزين المحلية الضرورية في المتصفح (`localStorage`، و`sessionStorage`، وكوكيز وظيفية أساسية) لتذكر تفضيلاتك وتسريع استجابة الواجهة.

---

## 📋 2. جدول عناصر التخزين المحلي والتقني

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

## 🛠️ 3. التحكم الإداري ومسح التخزين بضغطة زر
- **استوديو التخزين التفاعلي:** يمكنك فحص وتعديل أو حذف أي عنصر من عناصر التخزين في أي وقت عبر صفحة [`/cookies`](https://sir-modpack.web.app/cookies).
- **المسح الشامل الفوري:** يمكنك تفريغ كافة البيانات المؤقتة والإعدادات بضغطة زر واحدة من داخل إعدادات اللانشر المكتبي أو المتصفح.

---

## 📬 4. قنوات الدعم والتواصل
- **الدعم الفني الرسمي:** أداة الإبلاغ المدمجة في اللانشر (Bug Reporter) وملاحظات المجتمع.
- **رابط المطور:** [https://linktr.ee/sir.ahmed](https://linktr.ee/sir.ahmed)
- **الموقع الرسمي:** [https://sir-modpack.web.app](https://sir-modpack.web.app)
- **سياسة الخصوصية:** [PRIVACY.md](PRIVACY.md)

*© 2026 منظومة SIR ModPack. تطوير وإشراف SIR Ahmed.*
