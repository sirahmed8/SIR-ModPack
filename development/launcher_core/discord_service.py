import os
import sys
import json
import time
import struct
import threading

class DiscordRPCService:
    """Lightweight standalone Discord Rich Presence client via Windows Named Pipes."""
    
    CLIENT_ID = "1217670695503462441"
    
    def __init__(self):
        self.pipe = None
        self.connected = False
        self.enabled = True
        self.start_time = int(time.time())
        self.current_state = "In Launcher"
        self.current_details = "Exploring Modpacks & Shaders"

    def connect(self):
        if not self.enabled or sys.platform != "win32":
            return False
            
        for i in range(10):
            pipe_name = rf"\\.\pipe\discord-ipc-{i}"
            try:
                self.pipe = open(pipe_name, "w+b")
                self.connected = True
                self._send_handshake()
                return True
            except Exception:
                continue
        self.connected = False
        return False

    def _send_handshake(self):
        payload = json.dumps({"v": 1, "client_id": self.CLIENT_ID}).encode("utf-8")
        header = struct.pack("<II", 0, len(payload))
        self.pipe.write(header + payload)
        self.pipe.flush()

    def update_presence(self, state="Browsing Modpacks", details="SIR Launcher Pro", instance_name=""):
        self.current_state = state
        self.current_details = f"{instance_name} • {details}" if instance_name else details
        
        if not self.connected:
            if not self.connect():
                return {"success": False, "status": "Discord not running"}
                
        activity = {
            "state": self.current_state,
            "details": self.current_details,
            "timestamps": {"start": self.start_time},
            "assets": {
                "large_image": "sir_logo",
                "large_text": "SIR ModPack v1.0.0",
                "small_image": "verified_badge",
                "small_text": "Ultra-HD Minecraft"
            }
        }
        
        packet = json.dumps({
            "cmd": "SET_ACTIVITY",
            "args": {"pid": os.getpid(), "activity": activity},
            "nonce": str(time.time())
        }).encode("utf-8")
        
        try:
            header = struct.pack("<II", 1, len(packet))
            self.pipe.write(header + packet)
            self.pipe.flush()
            return {"success": True, "activity": activity}
        except Exception:
            self.connected = False
            return {"success": False, "status": "Pipe disconnected"}

    def set_enabled(self, enabled):
        self.enabled = enabled
        if not enabled and self.pipe:
            try:
                self.pipe.close()
            except Exception:
                pass
            self.connected = False
        return {"success": True, "enabled": self.enabled}
