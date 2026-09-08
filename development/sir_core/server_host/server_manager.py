import os
import subprocess
from ..config import SERVER_HOST_EXE

def start_dedicated_server():
    if os.path.exists(SERVER_HOST_EXE):
        subprocess.Popen([SERVER_HOST_EXE])
        return True, "SIR Server Host process spawned."
    return False, f"Missing server host binary: {SERVER_HOST_EXE}"

def stop_dedicated_server():
    return True
