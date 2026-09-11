"""
crash_analyzer.py — Deep Diagnostic Crash Stack-Trace & Native Dump Analyzer.
Implements 7 diagnostic pattern matchers:
1. Mixin conflicts with offending mod extraction
2. Java class major version mismatches (e.g. 65.0 vs 52.0)
3. 5 Out-Of-Memory (OOM) variants (Heap, Direct, Metaspace, GC Overhead, Native Thread)
4. Native driver & fatal JVM crashes (nvoglv64.dll, atio6axx.dll, ig9icd64.dll, jvm.dll, lwjgl64)
5. Missing mod dependencies & class loading errors (trove4j, Fabric API, etc.)
6. Corrupted world regions & NBT payload exceptions
7. Shader pipeline & OpenGL context errors
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional


class CrashAnalyzer:
    """Zero-dependency root-cause stack-trace diagnostic engine."""

    JAVA_VERSION_MAP: Dict[str, tuple[str, int]] = {
        "69.0": ("Java 25", 25),
        "68.0": ("Java 24", 24),
        "67.0": ("Java 23", 23),
        "66.0": ("Java 22", 22),
        "65.0": ("Java 21", 21),
        "64.0": ("Java 20", 20),
        "63.0": ("Java 19", 19),
        "62.0": ("Java 18", 18),
        "61.0": ("Java 17", 17),
        "60.0": ("Java 16", 16),
        "55.0": ("Java 11", 11),
        "52.0": ("Java 8", 8),
    }

    KNOWN_LIBRARIES_MAP: Dict[str, str] = {
        "gnu/trove": "trove4j (Legacy Forge dependency)",
        "net/fabricmc/fabric/api": "Fabric API",
        "me/shedaniel/clothconfig2": "Cloth Config v2",
        "dev/architectury": "Architectury API",
        "fuzs/puzzleslib": "Puzzles Lib",
        "org/spongepowered/asm": "Mixin Subsystem",
        "com/electronwill/nightconfig": "Night Config",
        "net/minecraftforge/fml": "Forge Mod Loader",
        "org/lwjgl": "LWJGL Core Libraries",
    }

    @classmethod
    def diagnose_crash(cls, content: str, filename: str = "") -> Dict[str, Any]:
        """Runs multi-pass pattern matching over crash logs and hs_err_pid dumps."""
        if not content:
            return {
                "type": "UNKNOWN",
                "cause": "Empty crash report content",
                "fix": "Check latest.log for details or run Launcher Self-Repair.",
            }

        # -------------------------------------------------------------
        # 0a. Java Version Mismatch (e.g. Java 21 vs 25 on 26.2)
        # -------------------------------------------------------------
        if (
            "requires version 25 or later of 'OpenJDK 64-Bit Server VM'" in content
            or ("Replace 'OpenJDK 64-Bit Server VM'" in content and "version 25" in content)
        ):
            return {
                "type": "JAVA_VERSION_MISMATCH",
                "cause": "Minecraft 26.2 requires 64-bit Java 25 or later (Java 21 detected)",
                "conflicting_mods": [],
                "solutions": ["Switch instance Java runtime to Java 25 (Azul Zulu 25)"],
                "auto_fixable": True,
                "fix": "Switch instance Java runtime to Java 25 and relaunch.",
            }

        # -------------------------------------------------------------
        # 0b. Incompatible Fabric Mods (Lunar-like ModResolutionException)
        # -------------------------------------------------------------
        if (
            "ModResolutionException" in content
            or "Incompatible mods found" in content
            or "Some of your mods are incompatible" in content
            or "Mod resolution failed" in content
        ):
            conflicting_mods = []
            solutions = []
            sol_match = re.search(r"A potential solution has been determined, this may resolve your problem:\s*\n((?:\s*-\s*[^\n\r]+\n?)+)", content)
            if sol_match:
                for s_line in sol_match.group(1).splitlines():
                    clean_s = s_line.strip().lstrip("-").strip()
                    if clean_s and clean_s not in solutions:
                        solutions.append(clean_s)
            detail_matches = re.findall(r"Mod '([^']+)' \(([^)]+)\)", content)
            for d_name, d_id in detail_matches:
                if d_id not in conflicting_mods and d_id.lower() not in ("minecraft", "fabricloader", "java"):
                    conflicting_mods.append(d_id)
            if not conflicting_mods:
                raw_mods = re.findall(r"(?:Install|Replace mod|Remove mod)\s+'?([a-zA-Z0-9_\-]+)'?", content)
                for rm in raw_mods:
                    if rm not in conflicting_mods and rm.lower() not in ("fabric", "minecraft", "java"):
                        conflicting_mods.append(rm)
            return {
                "type": "INCOMPATIBLE_MODS",
                "cause": "Incompatible Fabric Mods Detected",
                "conflicting_mods": conflicting_mods,
                "solutions": solutions,
                "auto_fixable": True,
                "fix": "Disable or update conflicting mods to ensure seamless launch.",
            }

        # -------------------------------------------------------------
        # 1. Native JVM Crash (hs_err_pid*.log / fatal OS signal)
        # -------------------------------------------------------------
        if filename.startswith("hs_err_pid") or "fatal error has been detected by the Java Runtime" in content:
            prob_frame_match = re.search(r"#\s*Problematic frame:\s*\n\s*#\s*([^\n\r]+)", content)
            if prob_frame_match:
                frame_line = prob_frame_match.group(1)
                dll_m = re.search(r"([a-zA-Z0-9_\.\-]+\.(?:dll|so|dylib|jnilib))", frame_line, re.IGNORECASE)
                failing_module = dll_m.group(1) if dll_m else frame_line.strip()
            else:
                dll_fallback = re.search(r"\b([a-zA-Z0-9_\.\-]+\.(?:dll|so|dylib|jnilib))\b", content, re.IGNORECASE)
                failing_module = dll_fallback.group(1) if dll_fallback else "Native Subsystem"


            if "nvoglv64" in failing_module or "nvd3dum" in failing_module:
                fix = "NVIDIA OpenGL driver crash. Perform a clean graphics driver update from NVIDIA GeForce Experience."
            elif "atio6axx" in failing_module or "amdrsscs" in failing_module:
                fix = "AMD Radeon driver crash. Update AMD Adrenalin graphics drivers or disable custom shader pack."
            elif "ig9icd" in failing_module or "ig10icd" in failing_module:
                fix = "Intel Integrated GPU driver crash. Update Intel Arc/UHD graphics drivers or lower render distance."
            elif "jvm.dll" in failing_module:
                fix = "JVM engine crashed. Verify Java runtime installation integrity and allocate 6GB-8GB RAM."
            else:
                fix = f"Native runtime crash in {failing_module}. Check GPU drivers and run Launcher Self-Repair."

            return {
                "type": "JVM_NATIVE_CRASH",
                "cause": f"Native Access Violation in {failing_module}",
                "offending_module": failing_module,
                "fix": fix,
            }

        # -------------------------------------------------------------
        # 2. Fabric / Forge Mixin Conflicts & Injection Failures
        # -------------------------------------------------------------
        mixin_match = re.search(
            r"Mixin \[(?:([^:\]]+):)?([^\]]+) from mod ([a-zA-Z0-9_\-]+)\]\s*FAILED", content, re.IGNORECASE
        )
        mod_match = re.search(r"from mod ([a-zA-Z0-9_\-]+)", content)
        invalid_mixin_match = re.search(
            r"InvalidMixinException:.*from mod ([a-zA-Z0-9_\-]+)", content
        )
        if mixin_match or invalid_mixin_match or mod_match or "MixinTransformerError" in content or "InjectionError" in content or "MixinApplyError" in content:
            offending_mod = (
                mixin_match.group(3)
                if mixin_match
                else (mod_match.group(1) if mod_match else (invalid_mixin_match.group(1) if invalid_mixin_match else "Unknown Mod"))
            )
            mixin_config = (mixin_match.group(1) or mixin_match.group(2)) if mixin_match else "Mixin Configuration"

            target_class_match = re.search(
                r"Mixin transformation of ([a-zA-Z0-9_\.\$]+) failed", content
            )
            target_class = target_class_match.group(1) if target_class_match else "Target Game Class"

            return {
                "type": "MIXIN_CONFLICT",
                "cause": f"Mixin Conflict in Mod '{offending_mod}' on {target_class}",
                "offending_mod": offending_mod,
                "target_class": target_class,
                "mixin_config": mixin_config,
                "fix": f"Update or disable mod '{offending_mod}', or remove conflicting optimization mods.",
            }

        # -------------------------------------------------------------
        # 3. Java Class Version Mismatch (UnsupportedClassVersionError)
        # -------------------------------------------------------------
        ver_match = re.search(
            r"UnsupportedClassVersionError: .* \(class file version (\d+\.\d+)\), this version of the Java Runtime only recognizes class file versions up to (\d+\.\d+)",
            content,
        )
        if ver_match:
            req_cf, run_cf = ver_match.group(1), ver_match.group(2)
            req_name, _ = cls.JAVA_VERSION_MAP.get(req_cf, (f"Class Ver {req_cf}", 0))
            run_name, _ = cls.JAVA_VERSION_MAP.get(run_cf, (f"Class Ver {run_cf}", 0))
            return {
                "type": "JAVA_VERSION_MISMATCH",
                "cause": f"Java Version Incompatibility (Requires {req_name}, Running on {run_name})",
                "required_java": req_name,
                "running_java": run_name,
                "fix": f"Switch Java Runtime to {req_name} (Temurin 21 LTS) in Launcher Settings.",
            }

        # -------------------------------------------------------------
        # 4. Unsatisfied Link Error (Missing Native DLLs)
        # -------------------------------------------------------------
        link_match = re.search(
            r"UnsatisfiedLinkError: (?:no ([a-zA-Z0-9_\-]+) in java\.library\.path|([a-zA-Z0-9_\.\-]+): The specified module could not be found)",
            content,
        )
        if link_match:
            missing_lib = link_match.group(1) or link_match.group(2) or "Native Library"
            return {
                "type": "NATIVE_LINKAGE_ERROR",
                "cause": f"Missing Native Dynamic Library: '{missing_lib}'",
                "missing_native": missing_lib,
                "fix": f"Run Launcher Self-Repair to extract LWJGL natives into instance directory.",
            }

        # -------------------------------------------------------------
        # 5. Out Of Memory (5 Variants)
        # -------------------------------------------------------------
        if "OutOfMemoryError" in content or "Java heap space" in content:
            if "Direct buffer memory" in content:
                return {
                    "type": "DIRECT_MEMORY_EXHAUSTION",
                    "cause": "Off-Heap Direct Buffer Memory Exhaustion",
                    "fix": "Add '-XX:MaxDirectMemorySize=2G' to custom JVM Arguments in Launcher Settings.",
                }
            elif "Metaspace" in content:
                return {
                    "type": "METASPACE_EXHAUSTION",
                    "cause": "JVM Metaspace Class Metadata Exhaustion",
                    "fix": "Add '-XX:MaxMetaspaceSize=512M' to JVM arguments or disable redundant mod libraries.",
                }
            elif "GC overhead limit exceeded" in content or "gc overhead" in content.lower():
                return {
                    "type": "GC_OVERHEAD_EXHAUSTION",
                    "cause": "Garbage Collector Thrashing (GC Overhead Limit Exceeded)",
                    "fix": "Increase Allocated RAM to 6 GB or 8 GB and switch to G1GC garbage collection preset.",
                }
            elif "unable to create new native thread" in content or "create new native thread" in content.lower():
                return {
                    "type": "THREAD_CREATION_EXHAUSTION",
                    "cause": "OS Native Thread Limit Exceeded",
                    "fix": "Reduce concurrent background tasks, lower render distance, or reboot operating system.",
                }
            else:
                return {
                    "type": "OUT_OF_MEMORY",
                    "cause": "Java Heap Space Exhaustion (OutOfMemoryError)",
                    "fix": "Increase Allocated RAM to 6 GB or 8 GB in Launcher Settings slider.",
                }

        # -------------------------------------------------------------
        # 6. Missing Mod Dependencies & Class Loading Errors
        # -------------------------------------------------------------
        class_not_found = re.search(
            r"(?:ClassNotFoundException|NoClassDefFoundError): ([a-zA-Z0-9_\.\$/]+)", content
        )
        if class_not_found:
            raw_class = class_not_found.group(1).replace(".", "/")
            lib_name = "Unknown Library"
            for prefix, mapped_name in cls.KNOWN_LIBRARIES_MAP.items():
                if raw_class.startswith(prefix):
                    lib_name = mapped_name
                    break
            if lib_name == "Unknown Library":
                lib_name = raw_class.split("/")[-1]
            return {
                "type": "MISSING_DEPENDENCY",
                "cause": f"Missing Mod Dependency: '{lib_name}' ({class_not_found.group(1)})",
                "missing_class": class_not_found.group(1),
                "fix": f"Ensure required dependency '{lib_name}' is downloaded and enabled in mods folder.",
            }

        # -------------------------------------------------------------
        # 7. Corrupted World Regions & NBT Format Exceptions
        # -------------------------------------------------------------
        if (
            "Corrupted Chunk" in content
            or "RegionFormatException" in content
            or "NBTTagCompound" in content
            or "AnvilException" in content
            or "wrong location" in content.lower()
        ):
            region_match = re.search(r"r\.-?\d+\.-?\d+\.mca", content)
            region_file = region_match.group(0) if region_match else "world region"
            return {
                "type": "CORRUPTED_WORLD_REGION",
                "cause": f"Corrupted World Chunk or Anvil Region File ({region_file})",
                "region_file": region_file,
                "fix": f"Restore world backup from Worlds tab or use MCA Selector to prune corrupted region {region_file}.",
            }

        # -------------------------------------------------------------
        # 8. Shader & OpenGL Driver Errors
        # -------------------------------------------------------------
        if (
            "OpenGLException" in content
            or "GL_OUT_OF_MEMORY" in content
            or "GLFW error 6554" in content
            or "Shader compilation failed" in content
            or "Iris shader" in content
        ):
            return {
                "type": "OPENGL_GPU_ERROR",
                "cause": "OpenGL Context Creation or Shader VRAM Limit",
                "fix": "Switch Shader Preset to 'SIR Balanced' ('Balanced 144+ FPS') or update graphics card drivers.",
            }

        # -------------------------------------------------------------
        # 9. Bytecode Verification & ClassFormat Exceptions
        # -------------------------------------------------------------
        if "VerifyError" in content or "ClassFormatError" in content:
            cls_match = re.search(r"(?:VerifyError|ClassFormatError):\s*([^\n\r]+)", content)
            cls_detail = cls_match.group(1).strip() if cls_match else "Bytecode verification mismatch"
            return {
                "type": "BYTECODE_VERIFY_ERROR",
                "cause": f"JVM Bytecode Verification Failure ({cls_detail})",
                "fix": "Run Launcher Self-Repair to regenerate patched mod classes or verify Java 25 compatibility.",
            }

        # -------------------------------------------------------------
        # 10. Legacy 1.8.9 Forge / OptiFine / LaunchWrapper Crashes
        # -------------------------------------------------------------
        if (
            "net.minecraft.launchwrapper.Launch" in content
            or "cpw.mods.fml.common.LoaderException" in content
            or "net.minecraftforge.fml.common.LoaderException" in content
            or "1.8.9" in content and "NullPointerException: Rendering screen" in content
        ):
            coremod_match = re.search(r"The following coremods are not present:[^\n\r]*\n\s*([^\n\r]+)", content)
            culprit = coremod_match.group(1).strip() if coremod_match else "Legacy Forge CoreMod Conflict"
            return {
                "type": "LEGACY_189_FORGE_ERROR",
                "cause": f"Legacy 1.8.9 Modloader / CoreMod Exception ({culprit})",
                "auto_fixable": True,
                "fix": "Switch Java Runtime to Java 8 (Adoptium OpenJDK 8) or disable conflicting 1.8.9 CoreMod in Mods Manager.",
            }

        # -------------------------------------------------------------
        # 11. Modern 26.2 Fabric / NeoForge Shader Pipeline & Pipeline Stalls
        # -------------------------------------------------------------
        if (
            "net.irisshaders.iris.gl.shader.ShaderCompileException" in content
            or "Program link failed" in content
            or "Uniform not found" in content
            or "Iris has encountered an error" in content
        ):
            shader_match = re.search(r"Failed to compile shader\s*([^\n\r]+)", content)
            shader_info = shader_match.group(1).strip() if shader_match else "Shaderpack GLSL Syntax / Driver Error"
            return {
                "type": "MODERN_SHADER_PIPELINE_ERROR",
                "cause": f"Shader Pipeline Compilation Error ({shader_info})",
                "auto_fixable": True,
                "fix": "Switch Shaderpack to 'SIR Fast High-FPS' or disable current custom shaderpack from the Shaders tab.",
            }

        # Generic Catch-All
        return {
            "type": "GENERIC_CRASH",
            "cause": "Runtime Exception during game execution",
            "fix": "Check latest.log for details or run Launcher 1-Click Game Integrity Doctor.",
        }


# Consolidated Alias for architectural contracts
CrashReportAnalyzer = CrashAnalyzer

__all__ = ["CrashAnalyzer", "CrashReportAnalyzer"]

