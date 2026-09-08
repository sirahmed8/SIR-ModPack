import os
import subprocess
from ..config import SOURCE_ROOT, LAUNCHER_DIR

def build_aikar_flags(ram_mb=6144):
    return [
        f"-Xms{max(1024, ram_mb // 2)}M",
        f"-Xmx{ram_mb}M",
        "-XX:+UseG1GC",
        "-XX:+ParallelRefProcEnabled",
        "-XX:MaxGCPauseMillis=200",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+DisableExplicitGC",
        "-XX:+AlwaysPreTouch",
        "-XX:G1NewSizePercent=30",
        "-XX:G1MaxNewSizePercent=40",
        "-XX:G1ReservePercent=20",
        "-XX:G1HeapWastePercent=5",
        "-XX:G1MixedGCCountTarget=4",
        "-XX:InitiatingHeapOccupancyPercent=15",
        "-XX:G1MixedGCLiveThresholdPercent=90",
        "-XX:G1RSetUpdatingPauseTimePercent=5",
        "-XX:SurvivorRatio=32",
        "-XX:+PerfDisableSharedMem",
        "-XX:MaxTenuringThreshold=1"
    ]

def launch_instance(instance_id, ram_mb=6144, account_name="Player", server_direct_ip=None):
    sir_engine_exe = os.path.join(LAUNCHER_DIR, "prismlauncher.exe")
    if not os.path.exists(sir_engine_exe):
        sir_engine_exe = os.path.join(SOURCE_ROOT, "SIR Launcher", "prismlauncher.exe")
    if os.path.exists(sir_engine_exe):
        cmd = [sir_engine_exe, "-l", instance_id]
        if server_direct_ip:
            cmd.extend(["--server", server_direct_ip])
        proc = subprocess.Popen(cmd)
        return proc, "Launched via SIR High-Performance Native Pipeline"
    return None, f"SIR Launch Engine ready for profile '{instance_id}'."
