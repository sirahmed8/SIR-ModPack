"""
1-Click Video Preset Engine for SIR Minecraft Ecosystem.
Implements tri-layer graphics injection across:
  Layer 1: Vanilla options.txt (renderDistance, simulationDistance, graphicsMode, smoothLighting, particles, etc.)
  Layer 2: Sodium / Embeddium sodium-options.json (leaves_quality, cloud_distance, weather_quality, chunk_builder, etc.)
  Layer 3: Iris / Oculus / OptiFine iris.properties & optionsshaders.txt (enableShaders, shaderPack)

Supports Ultra, Balanced, Performance, Competitive, and Potato tiers for Modern (26.2 / 1.21.x) and Legacy (1.8.9).
"""

import os
import json
import re
import threading
from typing import Any, Dict, List, Optional

try:
    from shared_core.runtime import atomic_write_json, atomic_write_text
except ImportError:
    def atomic_write_json(path: str, value: Any) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as h:
            json.dump(value, h, indent=2, ensure_ascii=False)
        os.replace(temp, path)

    def atomic_write_text(path: str, text: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as h:
            h.write(text)
        os.replace(temp, path)


class VideoPresetService:
    """Manages high-performance tri-layer video presets across modern and legacy instances."""

    _lock = threading.RLock()

    PRESET_METADATA = {
        "ultra": {
            "id": "ultra",
            "name": "Enhanced Visuals",
            "tag": "✨ High Fidelity & POM",
            "render_distance": 16,
            "simulation_distance": 10,
            "shaders": True,
            "shader_pack": "SIR Modern Shader.zip",
            "target_fps": "Enhanced",
            "desc": "Maximum visual fidelity: 16-chunk render distance, 4x mipmaps, POM 3D textures, and SIR Modern volumetric shaders."
        },
        "balanced": {
            "id": "balanced",
            "name": "Balanced Performance & Visuals",
            "tag": "⚡ High Refresh Standard",
            "render_distance": 12,
            "simulation_distance": 8,
            "shaders": True,
            "shader_pack": "SIR Modern Shader.zip",
            "target_fps": "Standard",
            "desc": "Optimal balance: 12-chunk render distance, smooth lighting, and SIR Modern Shader pass tuned for fluid high-refresh displays."
        },
        "performance": {
            "id": "performance",
            "name": "Competitive Engine (Performance)",
            "tag": "🚀 Low Latency",
            "render_distance": 8,
            "simulation_distance": 6,
            "shaders": False,
            "shader_pack": "OFF",
            "target_fps": "Direct",
            "desc": "Optimized Sodium pipeline with disabled shaders, 8-chunk view, and immediate chunk building for responsive gameplay."
        },
        "competitive": {
            "id": "competitive",
            "name": "Competitive PvP (Zero Latency)",
            "tag": "🏆 0ms Input Latency",
            "render_distance": 8,
            "simulation_distance": 6,
            "shaders": False,
            "shader_pack": "OFF",
            "target_fps": "400+ FPS",
            "desc": "Ranked BedWars & PvP preset: 0ms render latency, disabled shaders, fast particle passes, and instantaneous hit registration."
        },
        "potato": {
            "id": "potato",
            "name": "Potato PC / Low-End Hardware",
            "tag": "🥔 Ultra Low Overhead",
            "render_distance": 4,
            "simulation_distance": 4,
            "shaders": False,
            "shader_pack": "OFF",
            "target_fps": "120+ FPS",
            "desc": "Aggressive optimizations: 4-chunk view distance, minimal particle effects, fast leaves, and disabled ambient occlusion for low-spec systems."
        }
    }

    def __init__(self, instances_dir: str):
        self.instances_dir = os.path.abspath(instances_dir)

    def get_available_presets(self) -> List[Dict[str, Any]]:
        """Returns catalog of all available video presets with rich UI metadata."""
        return list(self.PRESET_METADATA.values())

    def normalize_preset_name(self, raw_preset: str) -> str:
        """Normalizes preset aliases to canonical preset keys."""
        p = str(raw_preset or "").lower().strip()
        if "potato" in p or "low" in p or "min" in p:
            return "potato"
        if "comp" in p or "pvp" in p or "speed" in p:
            return "competitive"
        if "perf" in p or "fps" in p or "boost" in p:
            return "performance"
        if "ultra" in p or "extreme" in p or "high" in p or "cinematic" in p or "raytrace" in p:
            return "ultra"
        return "balanced"

    def _resolve_instance_dirs(self, inst_id: str, instance_info: Optional[Dict[str, Any]] = None) -> List[str]:
        """Resolves target directory candidates for an instance ID."""
        dir_name = None
        if instance_info and isinstance(instance_info, dict):
            dir_name = instance_info.get("instance_id") or instance_info.get("dir_name") or instance_info.get("id")

        if not dir_name:
            cand = os.path.join(self.instances_dir, str(inst_id))
            if os.path.isdir(cand):
                dir_name = str(inst_id)
            elif "189" in str(inst_id) or "1.8" in str(inst_id):
                dir_name = "1.8.9"
            elif "ultra" in str(inst_id) and os.path.isdir(os.path.join(self.instances_dir, "26.2-ultra")):
                dir_name = "26.2-ultra"
            elif str(inst_id).startswith("custom-") and os.path.isdir(os.path.join(self.instances_dir, str(inst_id))):
                dir_name = str(inst_id)
            else:
                dir_name = "26.2"

        inst_root = os.path.join(self.instances_dir, dir_name)
        if not os.path.exists(inst_root):
            if os.path.isdir(os.path.join(self.instances_dir, str(inst_id))):
                dir_name = str(inst_id)
                inst_root = os.path.join(self.instances_dir, dir_name)
            else:
                os.makedirs(os.path.join(inst_root, "minecraft"), exist_ok=True)

        target_dirs = [
            os.path.join(self.instances_dir, dir_name),
            os.path.join(self.instances_dir, dir_name, "minecraft")
        ]

        existing = [d for d in target_dirs if os.path.exists(d)]
        if not existing:
            mc_dir = os.path.join(self.instances_dir, dir_name, "minecraft")
            os.makedirs(mc_dir, exist_ok=True)
            existing = [mc_dir]

        return existing, dir_name

    def apply_video_preset(
        self,
        inst_id: str = "sir-26-ultra",
        preset_name: str = "balanced",
        instance_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Applies tri-layer video presets across options.txt, sodium-options.json, and iris.properties."""
        with self._lock:
            canonical_preset = self.normalize_preset_name(preset_name)
            raw_clean = str(preset_name).lower().strip()
            existing_targets, dir_name = self._resolve_instance_dirs(inst_id, instance_info)

            is_189 = "1.8" in dir_name or "189" in str(inst_id) or (
                instance_info and ("1.8" in str(instance_info.get("version", "")) or instance_info.get("category") == "legacy")
            )

            applied_files: List[str] = []

            for g_dir in existing_targets:
                cfg_dir = os.path.join(g_dir, "config")
                os.makedirs(cfg_dir, exist_ok=True)
                options_file = os.path.join(g_dir, "options.txt")

                existing_options: Dict[str, str] = {}
                if os.path.exists(options_file):
                    try:
                        with open(options_file, "r", encoding="utf-8", errors="ignore") as f:
                            for line in f:
                                if ":" in line:
                                    parts = line.strip().split(":", 1)
                                    existing_options[parts[0]] = parts[1]
                    except Exception:
                        pass

                if is_189:
                    # Legacy 1.8.9 (OptiFine + Vanilla)
                    cur_fps = existing_options.get("maxFps", "")
                    try:
                        fps_val = int(cur_fps)
                        target_fps = str(fps_val) if fps_val > 0 else "260"
                    except (ValueError, TypeError):
                        target_fps = "260"

                    new_opts = {
                        "guiScale": existing_options.get("guiScale", "2"),
                        "gamma": existing_options.get("gamma", "1.0"),
                        "fullscreen": existing_options.get("fullscreen", "true"),
                        "maxFps": target_fps,
                        "enableVsync": existing_options.get("enableVsync", "false"),
                        "resourcePacks": existing_options.get("resourcePacks", '["SIR Legacy.zip"]')
                    }
                    if canonical_preset == "potato":
                        new_opts.update({"renderDistance": "4", "maxFps": target_fps, "particles": "2", "smoothLighting": "false", "clouds": "false", "anisotropicFiltering": "1", "fancyGraphics": "false", "ao": "0"})
                        of_content = "ofRenderDistanceChunks:4\nofFastRender:true\nofFastMath:true\nofSmoothFps:false\nofSmoothWorld:false\nofAo:0\nofClouds:3\nofTrees:1\nofDroppedItems:1\nofDynamicLights:3\nofDynamicFov:false\n"
                        shader_content = "shaderPack=OFF\n"
                    elif canonical_preset in ("competitive", "performance"):
                        new_opts.update({"renderDistance": "8", "maxFps": target_fps, "particles": "2", "smoothLighting": "false", "clouds": "false", "anisotropicFiltering": "1", "fancyGraphics": "false", "ao": "1"})
                        of_content = "ofRenderDistanceChunks:8\nofFastRender:true\nofFastMath:true\nofSmoothFps:false\nofSmoothWorld:false\nofAo:1\nofClouds:3\nofTrees:1\nofDroppedItems:1\nofDynamicLights:3\n"
                        shader_content = "shaderPack=OFF\n"
                    elif canonical_preset == "ultra":
                        new_opts.update({"renderDistance": "16", "maxFps": target_fps, "particles": "0", "smoothLighting": "true", "clouds": "true", "anisotropicFiltering": "8", "fancyGraphics": "true", "ao": "2"})
                        of_content = "ofRenderDistanceChunks:16\nofFastRender:false\nofFastMath:false\nofSmoothFps:true\nofSmoothWorld:true\nofAo:2\nofClouds:1\nofTrees:2\nofDroppedItems:2\nofDynamicLights:1\n"
                        shader_content = "shaderPack=SIR Legacy Shader.zip\n"
                    else:  # balanced
                        new_opts.update({"renderDistance": "12", "maxFps": target_fps, "particles": "0", "smoothLighting": "true", "clouds": "true", "anisotropicFiltering": "4", "fancyGraphics": "true", "ao": "2"})
                        of_content = "ofRenderDistanceChunks:12\nofFastRender:false\nofFastMath:true\nofSmoothFps:true\nofSmoothWorld:true\nofAo:2\nofClouds:1\nofTrees:2\nofDroppedItems:2\nofDynamicLights:1\n"
                        shader_content = "shaderPack=SIR Legacy Shader.zip\n"

                    existing_options.update(new_opts)
                    options_str = "\n".join(f"{k}:{v}" for k, v in existing_options.items()) + "\n"
                    atomic_write_text(options_file, options_str)
                    atomic_write_text(os.path.join(g_dir, "optionsof.txt"), of_content)
                    atomic_write_text(os.path.join(g_dir, "optionsshaders.txt"), shader_content)

                    for fname in ["options.txt", "optionsof.txt", "optionsshaders.txt"]:
                        if fname not in applied_files:
                            applied_files.append(fname)
                else:
                    # Modern 26.2 / 1.21.x (Vanilla + Sodium + Iris)
                    cur_fps = existing_options.get("maxFramerate", "")
                    try:
                        fps_val = int(cur_fps)
                        target_fps = str(fps_val) if fps_val > 0 else "260"
                    except (ValueError, TypeError):
                        target_fps = "260"

                    if "maxFps" in existing_options:
                        del existing_options["maxFps"]

                    new_opts = {
                        "version": "3465",
                        "guiScale": "2",
                        "gamma": "0.0" if canonical_preset in ("balanced", "ultra") else "1.0",
                        "maxFramerate": target_fps,
                        "enableVsync": "false",
                        "fullscreen": "true",
                        "autoSaveIndicator": "true",
                        "attackIndicator": "1",
                        "resourcePacks": '["vanilla","file/SIR Modern.zip"]',
                        "skipMultiplayerWarning": "true",
                        "onboardAccessibility": "false"
                    }

                    if canonical_preset == "potato":
                        new_opts.update({
                            "renderDistance": "4", "simulationDistance": "4", "smoothLighting": "false",
                            "graphicsMode": "1", "biomeBlendRadius": "0", "entityDistanceScaling": "0.5",
                            "entityShadows": "false", "particles": "2", "mipmapLevels": "0", "clouds": "false"
                        })
                        sodium_cfg = {
                            "quality": {"leaves_quality": "FAST", "weather_quality": "FAST", "cloud_distance": 16, "menu_background_blur": 0, "improved_transparency": False, "weather_radius": 2},
                            "performance": {"chunk_builder": "IMMEDIATE", "animate_only_visible_textures": True},
                            "notifications": {"hide_donation_prompt": True}
                        }
                        iris_content = "enableShaders=false\nshaderPack=OFF\n"
                    elif canonical_preset in ("competitive", "performance"):
                        new_opts.update({
                            "renderDistance": "8", "simulationDistance": "6", "smoothLighting": "false",
                            "graphicsMode": "1", "biomeBlendRadius": "3", "entityDistanceScaling": "0.8",
                            "entityShadows": "false", "particles": "2", "mipmapLevels": "0", "clouds": "false"
                        })
                        sodium_cfg = {
                            "quality": {"leaves_quality": "FAST", "weather_quality": "FAST", "cloud_distance": 32, "menu_background_blur": 0, "improved_transparency": False, "weather_radius": 5},
                            "performance": {"chunk_builder": "IMMEDIATE", "animate_only_visible_textures": True},
                            "notifications": {"hide_donation_prompt": True}
                        }
                        iris_content = "enableShaders=false\nshaderPack=OFF\n"
                    elif canonical_preset == "ultra":
                        new_opts.update({
                            "renderDistance": "16", "simulationDistance": "10", "smoothLighting": "true",
                            "graphicsMode": "0", "biomeBlendRadius": "15", "entityDistanceScaling": "1.5",
                            "entityShadows": "true", "particles": "0", "mipmapLevels": "4", "clouds": "fancy"
                        })
                        sodium_cfg = {
                            "quality": {"leaves_quality": "CUTOUT", "weather_quality": "HIGH", "cloud_distance": 128, "menu_background_blur": 5, "improved_transparency": True, "weather_radius": 10},
                            "performance": {"chunk_builder": "SEMI_BLOCKING", "animate_only_visible_textures": True},
                            "notifications": {"hide_donation_prompt": True}
                        }
                        iris_content = "enableShaders=true\nshaderPack=SIR Modern Shader.zip\n"
                    else:  # balanced
                        new_opts.update({
                            "renderDistance": "12", "simulationDistance": "8", "smoothLighting": "true",
                            "graphicsMode": "0", "biomeBlendRadius": "7", "entityDistanceScaling": "1.0",
                            "entityShadows": "true", "particles": "0", "mipmapLevels": "4", "clouds": "fancy"
                        })
                        sodium_cfg = {
                            "quality": {"leaves_quality": "CUTOUT", "weather_quality": "HIGH", "cloud_distance": 128, "menu_background_blur": 5, "improved_transparency": True, "weather_radius": 10},
                            "performance": {"chunk_builder": "SEMI_BLOCKING", "animate_only_visible_textures": True},
                            "notifications": {"hide_donation_prompt": True}
                        }
                        iris_content = "enableShaders=true\nshaderPack=SIR Modern Shader.zip\n"

                    existing_options.update(new_opts)
                    options_str = "\n".join(f"{k}:{v}" for k, v in existing_options.items()) + "\n"
                    atomic_write_text(options_file, options_str)
                    atomic_write_json(os.path.join(cfg_dir, "sodium-options.json"), sodium_cfg)
                    atomic_write_text(os.path.join(cfg_dir, "iris.properties"), iris_content)

                    for fname in ["options.txt", "sodium-options.json", "iris.properties"]:
                        if fname not in applied_files:
                            applied_files.append(fname)

            preset_info = self.PRESET_METADATA.get(canonical_preset, self.PRESET_METADATA["balanced"])
            target_label = (instance_info.get("name") if instance_info else None) or dir_name

            return {
                "success": True,
                "preset": raw_clean,
                "canonical_preset": canonical_preset,
                "applied": applied_files,
                "error": "",
                "message": f"✓ Applied {preset_info['name']} preset to {target_label}!"
            }


def apply_video_preset(instances_dir: str, inst_id: str = "sir-26-ultra", preset_name: str = "balanced") -> Dict[str, Any]:
    """Top-level convenience function for applying video presets."""
    service = VideoPresetService(instances_dir)
    return service.apply_video_preset(inst_id, preset_name)
