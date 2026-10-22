import os
import sys
import json
import tempfile
import shutil

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "development"))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.instance_service import InstanceService
from launcher_core.shaders_service import ShadersService

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
instances_dir = os.path.join(root_dir, "instances")

print(f"Testing root_dir: {root_dir}")
print(f"Instances dir: {instances_dir}")

service = InstanceService(root_dir, instances_dir)
shaders_service = ShadersService(root_dir)
bridge = LauncherBridgeAPI(root_dir)

print("\n--- TEST 1: Default Instances List ---")
for inst in service.instances:
    inst_id = inst.get("id")
    instance_id = inst.get("instance_id")
    dir_name = inst.get("dir_name")
    p1 = os.path.join(instances_dir, instance_id) if instance_id else None
    p2 = os.path.join(instances_dir, dir_name) if dir_name else None
    exists1 = os.path.exists(p1) if p1 else False
    exists2 = os.path.exists(p2) if p2 else False
    print(f"ID: {inst_id} | instance_id: {instance_id} (exists: {exists1}) | dir_name: {dir_name} (exists: {exists2})")

print("\n--- TEST 2: apply_video_preset across various presets on sir-26-ultra ---")
presets_to_test = ["balanced", "ultra", "performance", "competitive", "potato", "extreme", "cinematic", "low"]
for p in presets_to_test:
    res = service.apply_video_preset("sir-26-ultra", p)
    print(f"Preset '{p}' -> {res}")

print("\n--- TEST 3: apply_video_preset on non-existent instance_id (e.g. sir-26-balanced) ---")
res_bal = service.apply_video_preset("sir-26-balanced", "balanced")
print(f"sir-26-balanced result: {res_bal}")

print("\n--- TEST 4: apply_video_preset on 1.8.9 (sir-189-pvp) ---")
res_189 = service.apply_video_preset("sir-189-pvp", "performance")
print(f"sir-189-pvp performance result: {res_189}")

print("\n--- TEST 5: Checking options.txt, sodium-options.json, iris.properties in 26.2 and 26.2-ultra ---")
for path_check in [
    os.path.join(instances_dir, "26.2", "options.txt"),
    os.path.join(instances_dir, "26.2", "config", "sodium-options.json"),
    os.path.join(instances_dir, "26.2", "config", "iris.properties"),
    os.path.join(instances_dir, "26.2-ultra", "options.txt"),
    os.path.join(instances_dir, "26.2-ultra", "config", "sodium-options.json"),
    os.path.join(instances_dir, "26.2-ultra", "config", "iris.properties"),
    os.path.join(instances_dir, "1.8.9", "minecraft", "options.txt"),
    os.path.join(instances_dir, "1.8.9", "minecraft", "optionsshaders.txt"),
]:
    exists = os.path.isfile(path_check)
    print(f"File: {path_check} exists: {exists}")
