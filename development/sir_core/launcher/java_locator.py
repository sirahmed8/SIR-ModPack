import os
import shutil

def locate_java_runtimes():
    runtimes = []
    sys_java = shutil.which("java") or shutil.which("javaw")
    if sys_java:
        runtimes.append({"path": sys_java, "name": "System Default Java (PATH)", "ver": 21})

    search_dirs = [
        r"C:\Program Files\Java",
        r"C:\Program Files\Eclipse Adoptium",
        r"C:\Program Files\Microsoft\jdk",
        r"C:\Program Files\BellSoft",
        r"C:\Program Files (x86)\Java",
        os.path.expanduser(r"~\.jdks")
    ]
    for base in search_dirs:
        if os.path.exists(base):
            try:
                for entry in os.scandir(base):
                    if entry.is_dir():
                        javaw = os.path.join(entry.path, "bin", "javaw.exe")
                        if not os.path.exists(javaw):
                            javaw = os.path.join(entry.path, "bin", "java.exe")
                        if os.path.exists(javaw):
                            ver_name = entry.name
                            ver_num = 21 if "21" in ver_name or "22" in ver_name else (8 if "8" in ver_name else 17)
                            runtimes.append({"path": javaw, "name": f"Java {ver_num} ({ver_name})", "ver": ver_num})
            except Exception:
                pass
    if not runtimes:
        runtimes.append({"path": "javaw", "name": "System Default Java (Auto)", "ver": 21})
    return runtimes

def get_recommended_java_path(mc_version="26.2"):
    runtimes = locate_java_runtimes()
    is_legacy = any(k in str(mc_version) for k in ["1.8", "1.7", "1.12"])
    target_ver = 8 if is_legacy else 21
    matched = next((r["path"] for r in runtimes if r.get("ver") == target_ver), None)
    if matched:
        return matched
    return runtimes[0]["path"]
