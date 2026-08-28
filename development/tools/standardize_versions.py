import os
import re

def update_file(path, replacements):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    for old, new in replacements:
        content = content.replace(old, new)
    if content != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")

# 1. Update config/ecosystem_manifest.json & website-next/public/ecosystem_manifest.json
for p in ['config/ecosystem_manifest.json', 'website-next/public/ecosystem_manifest.json']:
    update_file(p, [
        ('"version": "2.0.0"', '"version": "1.0.0"'),
        ('"version": "3.0.0"', '"version": "1.0.0"'),
        ('v2.0.0', '1.0.0'),
        ('v3.0.0', '1.0.0'),
    ])

# 2. Update config/sir_core.json
update_file('config/sir_core.json', [
    ('"version": "2.0.0"', '"version": "1.0.0"'),
    ('v2.0.0', '1.0.0')
])

# 3. Update website-next/app/api/updates/route.ts
update_file('website-next/app/api/updates/route.ts', [
    ('v2.0.0', '1.0.0'),
    ('2.0.0', '1.0.0')
])

# 4. Update website-next/lib/firebase.ts
update_file('website-next/lib/firebase.ts', [
    ('v1.0.0 GOLD MASTER', '1.0.0'),
    ('v1.0.0 OFFICIAL', '1.0.0'),
    ('v1.0.0 Official', '1.0.0'),
    ('v2.0.0 Gold Master', '1.0.0'),
    ('v2.0.0', '1.0.0'),
    ('2.0.0', '1.0.0'),
    ('Official Genesis Milestone', '1.0.0'),
    ('الإطلاق التأسيسي الرسمي', '1.0.0'),
    ('v1.0.0 Compliant', '1.0.0')
])

# 5. Update legal pages in website-next/app/
for p in ['website-next/app/privacy/page.tsx', 'website-next/app/terms/page.tsx', 'website-next/app/cookies/page.tsx']:
    update_file(p, [
        ('v2.0.0', '1.0.0'),
        ('v1.0.0', '1.0.0'),
        ('2.0.0', '1.0.0'),
    ])

# 6. Update markdown documentation files
for p in ['README.md', 'CHANGELOG.md', 'PRIVACY.md', 'TERMS.md', 'COOKIES.md', 'PROJECT.md', 'PROJECT_ARCHITECTURE_EXPLANATION.md', 'website-next/README.md']:
    update_file(p, [
        ('v2.0.0 Gold Master', '1.0.0'),
        ('v2.0.0', '1.0.0'),
        ('v1.0.0 Gold Master', '1.0.0'),
        ('v1.0.0 Official', '1.0.0'),
        ('v1.0.0 OFFICIAL', '1.0.0'),
        ('v1.0.0 Genesis Release', '1.0.0'),
        ('2.0.0 Gold Master', '1.0.0'),
        ('1.0.0 Gold Master', '1.0.0'),
        ('2.0.0', '1.0.0'),
        ('v3.0.0', '1.0.0'),
        ('3.0.0', '1.0.0')
    ])

# 7. Update ecosystem scripts
for p in ['ecosystem_doctor.py', 'sync_ecosystem.py']:
    update_file(p, [
        ('v2.0.0', '1.0.0'),
        ('2.0.0', '1.0.0')
    ])

# 8. Update Python app sources
for p in [
    'development/installer_source/SIR_Installer_GUI.py',
    'development/launcher_source/SIR_Launcher_Studio.py',
    'development/server_app/SIR_Server_Manager.py',
    'development/sir_core/config.py'
]:
    update_file(p, [
        ('v1.0.0 OFFICIAL MASTER', '1.0.0'),
        ('v1.0.0 OFFICIAL', '1.0.0'),
        ('v1.0.0 Official', '1.0.0'),
        ('v2.0.0', '1.0.0'),
        ('APP_VERSION = "v1.0.0 OFFICIAL"', 'APP_VERSION = "1.0.0"'),
        ('APP_VERSION = "v1.0.0"', 'APP_VERSION = "1.0.0"')
    ])

print("Standardization complete!")
