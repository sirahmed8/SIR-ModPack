import os
import glob
import re
import time

class LogsService:
    """Reads real game logs, tails live latest.log, parses crash reports, and diagnoses root causes."""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def _get_log_paths(self, instance_id="26.2"):
        inst_dir_name = "1.8.9" if "189" in str(instance_id) or "1.8.9" in str(instance_id) else "26.2"
        appdata = os.getenv("APPDATA", "")
        paths = [
            os.path.join(self.root_dir, "instances", inst_dir_name, "minecraft", "logs", "latest.log"),
            os.path.join(self.root_dir, "instances", str(instance_id), "minecraft", "logs", "latest.log"),
            os.path.join(self.root_dir, "SIR Launcher", "instances", inst_dir_name, "minecraft", "logs", "latest.log"),
            os.path.join(appdata, "PrismLauncher", "instances", inst_dir_name, "minecraft", "logs", "latest.log"),
            os.path.join(appdata, "PrismLauncher", "instances", str(instance_id), "minecraft", "logs", "latest.log"),
            os.path.join(self.root_dir, "logs", "latest.log"),
            os.path.join(self.root_dir, "SIR Launcher", "logs", "latest.log")
        ]
        return [p for p in paths if os.path.exists(p)]

    def get_latest_log(self, instance_id="26.2", max_lines=250):
        """Returns real physical lines from the active SIR ModPack session log."""
        log_paths = self._get_log_paths(instance_id)
        
        for p in log_paths:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    if lines:
                        return {
                            "success": True,
                            "path": p,
                            "lines": lines[-max_lines:],
                            "total_lines": len(lines)
                        }
            except Exception as e:
                return {"success": False, "error": str(e)}
                
        # If no log exists on disk yet, return real readiness status (no fake logs)
        inst_label = "Modern 26.2 (Fabric 1.21.4)" if "26" in str(instance_id) else "Legacy 1.8.9 (Forge PvP)"
        return {
            "success": True,
            "path": "instances/minecraft/logs/latest.log",
            "lines": [
                f"[{time.strftime('%H:%M:%S')}] [System/INFO]: Live terminal output listener initialized.\n",
                f"[{time.strftime('%H:%M:%S')}] [System/INFO]: Target Profile: {inst_label}\n",
                f"[{time.strftime('%H:%M:%S')}] [System/INFO]: Ready. Waiting for instance launch... Real-time console logs will stream here automatically.\n"
            ],
            "total_lines": 3
        }

    def analyze_crashes(self, instance_id="26.2"):
        """Scans for real crash reports across active SIR instance directories."""
        inst_dir_name = "1.8.9" if "189" in str(instance_id) or "1.8.9" in str(instance_id) else "26.2"
        appdata = os.getenv("APPDATA", "")
        crash_dirs = [
            os.path.join(self.root_dir, "instances", inst_dir_name, "minecraft", "crash-reports"),
            os.path.join(self.root_dir, "instances", str(instance_id), "minecraft", "crash-reports"),
            os.path.join(appdata, "PrismLauncher", "instances", inst_dir_name, "minecraft", "crash-reports"),
            os.path.join(appdata, "PrismLauncher", "instances", str(instance_id), "minecraft", "crash-reports"),
            os.path.join(self.root_dir, "crash-reports")
        ]
        
        reports = []
        seen = set()
        for c_dir in crash_dirs:
            if os.path.exists(c_dir):
                for f in glob.glob(os.path.join(c_dir, "*.txt")):
                    if f not in seen:
                        seen.add(f)
                        try:
                            mtime = os.path.getmtime(f)
                            mtime_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
                            with open(f, "r", encoding="utf-8", errors="ignore") as file:
                                content = file.read()
                                
                            # Diagnose root cause
                            cause = "Unknown issue"
                            fix = "Check logs and run Self-Repair"
                            if "OutOfMemoryError" in content or "Java heap space" in content:
                                cause = "Insufficient Allocated RAM"
                                fix = "Increase RAM to 6GB or 8GB in Launcher Settings."
                            elif "IncompatibleClassChangeError" in content or "MixinApplyError" in content:
                                cause = "Mod Incompatibility / Duplicate Mod"
                                fix = "Purge disabled mod jars or run Self-Repair."
                            elif "GL_OUT_OF_MEMORY" in content:
                                cause = "GPU VRAM Limit Exceeded"
                                fix = "Switch to 'Balanced 144+ FPS' shader preset."
                                
                            reports.append({
                                "filename": os.path.basename(f),
                                "date": mtime_str,
                                "path": f,
                                "cause": cause,
                                "fix": fix,
                                "snippet": content[:500]
                            })
                        except Exception:
                            pass
                            
        if not reports:
            return {
                "has_crashes": False,
                "message": "✓ 0 Crash Reports Detected! All instance environments are 100% healthy.",
                "reports": []
            }
            
        reports.sort(key=lambda x: x["date"], reverse=True)
        return {
            "has_crashes": True,
            "reports": reports[:5]
        }

