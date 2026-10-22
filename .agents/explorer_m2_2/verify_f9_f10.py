import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "development")))

from launcher_core.native_runner import NativeMinecraftRunner
from launcher_core.java_service import JavaService

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
runner = NativeMinecraftRunner(root_dir, root_dir)
java_svc = JavaService(root_dir)

print("=== 26.2 Instance Inspection ===")
cfg_262 = runner.inspect_instance_config(os.path.join(root_dir, "instances", "26.2"))
print("26.2 Config:", json.dumps(cfg_262, indent=2))

print("\n=== 1.8.9 Instance Inspection ===")
cfg_189 = runner.inspect_instance_config(os.path.join(root_dir, "instances", "1.8.9"))
print("1.8.9 Config:", json.dumps(cfg_189, indent=2))

print("\n=== Java Installations Discovery ===")
j_res = java_svc.discover_java_installations()
count = j_res.get("count", 0)
print(f"Found {count} Java runtimes:")
for inst in j_res.get("installations", [])[:8]:
    name = inst.get("name")
    path = inst.get("path")
    is_64 = inst.get("is_64bit")
    major = inst.get("major_version")
    temurin = inst.get("is_temurin_21")
    print(f" - {name} -> {path} (64bit={is_64}, major={major}, temurin21={temurin})")

best_modern = java_svc.get_best_runtime_for_version("26.2")
print("\nBest Modern Java (26.2):")
if best_modern:
    print(f"  Name: {best_modern.get('name')}")
    print(f"  Path: {best_modern.get('path')}")
    print(f"  Major: {best_modern.get('major_version')}")
    print(f"  Temurin21: {best_modern.get('is_temurin_21')}")
else:
    print("  None found.")

best_legacy = java_svc.get_best_runtime_for_version("1.8.9")
print("\nBest Legacy Java (1.8.9):")
if best_legacy:
    print(f"  Name: {best_legacy.get('name')}")
    print(f"  Path: {best_legacy.get('path')}")
    print(f"  Major: {best_legacy.get('major_version')}")
else:
    print("  None found.")

print("\n=== Dynamic Classpath Assembly Verification ===")
v_json_262 = runner.resolve_version_json("26.2", loader="fabric") or {"id": "26.2", "libraries": []}
cp_262 = runner.build_classpath(v_json_262, "26.2", loader="fabric", instance_dir=os.path.join(root_dir, "instances", "26.2"))
print(f"Fabric 26.2 Classpath contains {len(cp_262)} jars.")
for j in cp_262[:5]:
    print("  [26.2 CP]", j)

v_json_189 = runner.resolve_version_json("1.8.9", loader="forge") or {"id": "1.8.9", "libraries": []}
cp_189 = runner.build_classpath(v_json_189, "1.8.9", loader="forge", instance_dir=os.path.join(root_dir, "instances", "1.8.9"))
print(f"\nForge 1.8.9 Classpath contains {len(cp_189)} jars.")
for j in cp_189[:5]:
    print("  [1.8.9 CP]", j)
