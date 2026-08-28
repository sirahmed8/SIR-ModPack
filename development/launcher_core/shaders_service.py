import os
import json

class ShadersService:
    """Manages SIR Shaders 2.0 configuration, POM normal/specular maps, and in-game presets."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.shaderpacks_dir = os.path.join(self.root_dir, "shaderpacks")

    def get_shader_presets(self):
        return [
            {
                "id": "cinematic_extreme",
                "name": "Cinematic Master SIR Shader (Extreme)",
                "file": "SIR_Extreme_Shader.zip",
                "tag": "✨ Max Visuals",
                "fps": "144+ FPS",
                "desc": "Volumetric atmosphere, Screen-Space Reflections, Subsurface Scattering, physics circular glowing sun & 3D POM blocks.",
                "profile": "extreme"
            },
            {
                "id": "balanced_144",
                "name": "Balanced 144+ FPS SIR Shader",
                "file": "SIR_Balanced_Shader.zip",
                "tag": "⚡ High Framerate",
                "fps": "180+ FPS",
                "desc": "Same crystal water, physics sun & 3D blocks with an optimized lighting pass for high-refresh monitors.",
                "profile": "balanced"
            },
            {
                "id": "competitive_pvp",
                "name": "Competitive PvP (Pure Speed)",
                "file": "OFF",
                "tag": "🏆 0ms Latency",
                "fps": "400+ FPS",
                "desc": "Shaders turned off, maximum Sodium pipeline efficiency for instantaneous hit registration.",
                "profile": "off"
            }
        ]

    def get_active_shader(self, instance_dir="26.2"):
        target_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "optionsshaders.txt")
        if not os.path.exists(target_cfg):
            target_cfg = os.path.join(self.root_dir, "instances", "26.2", "minecraft", "optionsshaders.txt")
        if os.path.exists(target_cfg):
            try:
                with open(target_cfg, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("shaderPack="):
                            val = line.split("=", 1)[1].strip()
                            return val
            except Exception:
                pass
        return "SIR_Extreme_Shader.zip"

    def apply_shader_preset(self, preset_id_or_file, instance_dir="26.2"):
        filename = "SIR_Extreme_Shader.zip"
        pname = "SIR Extreme Shader (Ultra Raytracing)"
        low = str(preset_id_or_file).lower()
        if "balanced" in low:
            filename = "SIR_Balanced_Shader.zip"
            pname = "SIR Balanced Shader (High FPS 144Hz+)"
        elif "off" in low or "competitive" in low:
            filename = "OFF"
            pname = "Internal Shaders (OFF)"
        elif "extreme" in low or "ultra" in low:
            filename = "SIR_Extreme_Shader.zip"
            pname = "SIR Extreme Shader (Ultra Raytracing)"
        else:
            filename = str(preset_id_or_file)
            pname = filename

        target_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "optionsshaders.txt")
        try:
            os.makedirs(os.path.dirname(target_cfg), exist_ok=True)
            with open(target_cfg, "w", encoding="utf-8") as f:
                if filename != "OFF":
                    f.write(f"shaderPack={filename}\n")
                    f.write("antialiasing=0\n")
                    f.write("shadowMapResolution=2048\n")
                else:
                    f.write("shaderPack=OFF\n")
            return {"success": True, "active_shader": filename, "name": pname, "message": f"Activated {pname}!"}
        except Exception as ex:
            return {"success": False, "error": str(ex)}

    def get_fine_shader_options(self, instance_dir="26.2"):
        bliss_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "config", "bliss.txt")
        defaults = {
            "motion_blur": False,
            "sun_glow_scale": 1.5,
            "water_wave_intensity": "Medium",
            "ssr_reflections": True,
            "subsurface_scattering": True
        }
        
        if os.path.exists(bliss_cfg):
            try:
                with open(bliss_cfg, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            if k == "MOTION_BLUR": defaults["motion_blur"] = (v == "1")
                            elif k == "SUN_GLOW_SCALE": defaults["sun_glow_scale"] = float(v)
                            elif k == "WATER_WAVE_INTENSITY": defaults["water_wave_intensity"] = v
                            elif k == "SSR": defaults["ssr_reflections"] = (v == "1")
                            elif k == "SSS": defaults["subsurface_scattering"] = (v == "1")
            except Exception:
                pass
        return defaults

    def save_fine_shader_options(self, options_dict, instance_dir="26.2"):
        bliss_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "config", "bliss.txt")
        os.makedirs(os.path.dirname(bliss_cfg), exist_ok=True)
        try:
            with open(bliss_cfg, "w", encoding="utf-8") as f:
                f.write(f"MOTION_BLUR={'1' if options_dict.get('motion_blur') else '0'}\n")
                f.write(f"SUN_GLOW_SCALE={options_dict.get('sun_glow_scale', 1.5)}\n")
                f.write(f"WATER_WAVE_INTENSITY={options_dict.get('water_wave_intensity', 'Medium')}\n")
                f.write(f"SSR={'1' if options_dict.get('ssr_reflections', True) else '0'}\n")
                f.write(f"SSS={'1' if options_dict.get('subsurface_scattering', True) else '0'}\n")
            return {"success": True, "message": "✓ Fine-grained shader parameters saved to bliss.txt!"}
        except Exception as e:
            return {"success": False, "error": str(e)}
