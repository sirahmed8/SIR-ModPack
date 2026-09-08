import os
import json
from shared_core.runtime import atomic_write_text

class ShadersService:

    """Manages SIR Shaders 2.0 configuration, POM normal/specular maps, and in-game presets."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.shaderpacks_dir = os.path.join(self.root_dir, "shaderpacks")

    def get_shader_presets(self):
        return [
            {
                "id": "modern_shader",
                "name": "SIR Modern Shader (Enhanced Visuals)",
                "file": "SIR Modern Shader.zip",
                "tag": "✨ Enhanced Fidelity",
                "fps": "Standard",
                "desc": "Volumetric atmosphere, Screen-Space Reflections, Subsurface Scattering, physics circular glowing sun & 3D POM blocks.",
                "profile": "modern"
            },
            {
                "id": "legacy_shader",
                "name": "SIR Legacy Shader (Classic Enhanced)",
                "file": "SIR Legacy Shader.zip",
                "tag": "🎬 Classic Fidelity",
                "fps": "Standard",
                "desc": "OptiFine 1.8.9 tuned shaders with crisp lighting and crystal water.",
                "profile": "legacy"
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
        return "SIR Modern Shader.zip"

    def apply_shader_preset(self, preset_id_or_file, instance_dir="26.2"):
        filename = "SIR Modern Shader.zip"
        pname = "SIR Modern Shader (Enhanced Visuals)"
        low = str(preset_id_or_file).lower()
        if "legacy" in low or "189" in low or "1.8" in low:
            filename = "SIR Legacy Shader.zip"
            pname = "SIR Legacy Shader (Classic Enhanced)"
        elif "off" in low or "competitive" in low:
            filename = "OFF"
            pname = "Internal Shaders (OFF)"
        elif "modern" in low or "ultra" in low or "extreme" in low or "balanced" in low:
            filename = "SIR Modern Shader.zip"
            pname = "SIR Modern Shader (Enhanced Visuals)"
        else:
            filename = str(preset_id_or_file)
            pname = filename

        target_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "optionsshaders.txt")
        try:
            if filename != "OFF":
                content = f"shaderPack={filename}\nantialiasing=0\nshadowMapResolution=2048\n"
            else:
                content = "shaderPack=OFF\n"
            atomic_write_text(target_cfg, content)
            return {"success": True, "active_shader": filename, "name": pname, "message": f"Activated {pname}!"}
        except Exception as ex:
            return {"success": False, "error": str(ex)}

    def get_fine_shader_options(self, instance_dir="26.2"):
        shader_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "config", "sir_shader_config.txt")
        defaults = {
            "motion_blur": False,
            "sun_glow_scale": 1.5,
            "water_wave_intensity": "Medium",
            "ssr_reflections": True,
            "subsurface_scattering": True
        }
        
        if os.path.exists(shader_cfg):
            try:
                with open(shader_cfg, "r", encoding="utf-8") as f:
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
        shader_cfg = os.path.join(self.root_dir, "instances", instance_dir, "minecraft", "config", "sir_shader_config.txt")
        try:
            content = (
                f"MOTION_BLUR={'1' if options_dict.get('motion_blur') else '0'}\n"
                f"SUN_GLOW_SCALE={options_dict.get('sun_glow_scale', 1.5)}\n"
                f"WATER_WAVE_INTENSITY={options_dict.get('water_wave_intensity', 'Medium')}\n"
                f"SSR={'1' if options_dict.get('ssr_reflections', True) else '0'}\n"
                f"SSS={'1' if options_dict.get('subsurface_scattering', True) else '0'}\n"
            )
            atomic_write_text(shader_cfg, content)
            return {"success": True, "message": "✓ Saved SIR Shader configuration!"}
        except Exception as e:
            return {"success": False, "error": str(e)}

