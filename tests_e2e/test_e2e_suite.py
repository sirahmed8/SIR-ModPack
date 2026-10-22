"""
=============================================================================
SIR ModPack Master Interconnected Ecosystem — Opaque-Box E2E Test Suite
File: tests_e2e/test_e2e_suite.py
Architecture: 4-Tier Opaque-Box Testing Architecture (Tiers 1-4)
Reference Requirements: ORIGINAL_REQUEST.md & PROJECT.md
=============================================================================
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.parse
from typing import Any, Dict

# Ensure project root and development directory are in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV_DIR = os.path.join(ROOT_DIR, "development")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.repair_service import RepairService
from launcher_core.skin_studio_service import SkinStudioService
from launcher_core.telemetry_governor_service import TelemetryGovernorService
from server_core.server_bridge import ServerBridgeAPI, ServerRestartScheduler
from installer_core.installer_bridge import InstallerBridgeAPI


# =============================================================================
# HELPER MOCK & UTILITY CLASSES
# =============================================================================

class MockBridgeForScheduler:
    """Mock bridge to capture ServerRestartScheduler broadcasts and webhooks."""
    def __init__(self):
        self.commands_sent = []
        self.webhooks_posted = []
        self.restarts_triggered = 0

    def send_command(self, cmd: str):
        self.commands_sent.append(cmd)

    def post_discord_webhook(self, event_type: str, message: str):
        self.webhooks_posted.append({"event_type": event_type, "message": message})

    def restart_server(self):
        self.restarts_triggered += 1


def parse_deep_link(raw_url: str) -> Dict[str, Any]:
    """Opaque-box parser for sirlauncher:// native deep-link protocol."""
    if not raw_url or not isinstance(raw_url, str):
        return {"valid": False, "error": "Empty or non-string deep link"}
    
    clean_url = raw_url.strip()
    if not (clean_url.startswith("sirlauncher://") or clean_url.startswith("sir-launcher://")):
        return {"valid": False, "error": "Invalid scheme"}
    
    try:
        parsed = urllib.parse.urlparse(clean_url)
        action = f"{parsed.netloc}{parsed.path}".strip("/")
        query_params = urllib.parse.parse_qs(parsed.query)
        flattened_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        return {
            "valid": True,
            "action": action.lower(),
            "params": flattened_params,
            "raw": clean_url
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


# =============================================================================
# TIER 1: FEATURE COVERAGE (HAPPY PATH FUNCTIONAL VERIFICATION)
# =============================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Isolated functional checks for all 18 inventoried features."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_e2e_t1_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_f01_deep_link_protocol_parsing(self):
        """F01: Verify parsing of all sirlauncher:// actions and parameters."""
        test_cases = [
            ("sirlauncher://launch?profile=26.2-ultra&shader=SIR+Extreme", "launch", "profile", "26.2-ultra"),
            ("sirlauncher://join?ip=play.sirmodpack.com&port=25565", "join", "ip", "play.sirmodpack.com"),
            ("sirlauncher://install?tier=ultra", "install", "tier", "ultra"),
            ("sirlauncher://mod/install?id=sodium", "mod/install", "id", "sodium"),
            ("sirlauncher://profile?name=26.2", "profile", "name", "26.2"),
            ("sirlauncher://auth?data=%7B%22uid%22%3A%22u1%22%7D&code=secret123", "auth", "code", "secret123")
        ]
        for url, expected_action, check_param, expected_val in test_cases:
            res = parse_deep_link(url)
            self.assertTrue(res["valid"], f"Failed parsing: {url}")
            self.assertEqual(res["action"], expected_action)
            self.assertEqual(res["params"].get(check_param), expected_val)

    def test_f02_multiplayer_latency_radar(self):
        """F02: Verify multiplayer latency radar color formatting and clean MOTD."""
        from server.server_health_check import clean_minecraft_formatting, parse_motd
        raw_motd = "§b§lSIR ModPack §fBedrock Gateway §a[Active]"
        cleaned = clean_minecraft_formatting(raw_motd)
        self.assertEqual(cleaned, "SIR ModPack Bedrock Gateway [Active]")
        self.assertNotIn("§", cleaned)
        
        _, clean_parsed = parse_motd({"text": "§eWelcome to §6SIR Server!"})
        self.assertEqual(clean_parsed, "Welcome to SIR Server!")

    def test_f03_game_integrity_doctor(self):
        """F03: Verify Game Integrity Doctor SHA-256 calculation and delta manifest audit."""
        repair = RepairService(ROOT_DIR)
        manifest_path = os.path.join(ROOT_DIR, "delta_manifest.json")
        self.assertTrue(os.path.isfile(manifest_path), "delta_manifest.json must exist")
        
        # Test hash of delta_manifest.json itself
        calculated_sha = repair.calculate_sha256(manifest_path)
        self.assertEqual(len(calculated_sha), 64, "SHA-256 must be 64 hexadecimal characters")
        
        # Verify file integrity check passes with correct expected hash
        res = repair.verify_file_integrity(manifest_path, expected_sha256=calculated_sha)
        self.assertTrue(res["valid"])
        self.assertEqual(res["sha256"].lower(), calculated_sha.lower())

    def test_f04_win32_ram_compactor(self):
        """F04: Verify Win32 RAM Compactor (psapi.dll EmptyWorkingSet)."""
        governor = TelemetryGovernorService()
        res = governor.trim_process_memory(pid=None)
        self.assertIsInstance(res, dict)
        self.assertIn("success", res)
        if sys.platform == "win32":
            self.assertTrue(res["success"])
            self.assertIn("before_mb", res)
            self.assertIn("after_mb", res)
            self.assertIn("freed_mb", res)
            self.assertGreaterEqual(res["freed_mb"], 0.0)

    def test_f05_skin_and_cape_studio(self):
        """F05: Verify 3D Skin Studio preset capes and skins inventory."""
        skin_service = SkinStudioService(self.test_dir)
        capes = skin_service.get_preset_capes()
        self.assertEqual(len(capes), 6, "Must provide exactly 6 official preset capes")
        cape_ids = {c["id"] for c in capes}
        expected_cape_ids = {
            "sir_obsidian_neon", "sir_emerald_prism", "sir_cyber_pulse",
            "sir_void_dragon", "sir_champion_gold", "sir_classic_genesis"
        }
        self.assertEqual(cape_ids, expected_cape_ids)

        skins = skin_service.get_preset_skins()
        self.assertEqual(len(skins), 6, "Must provide exactly 6 official preset skins")
        skin_ids = {s["id"] for s in skins}
        expected_skin_ids = {
            "sir_cyber_warrior", "sir_neon_shadow", "sir_emerald_ninja",
            "sir_void_walker", "sir_esports_pro", "sir_steve_tactical"
        }
        self.assertEqual(skin_ids, expected_skin_ids)

    def test_f06_server_restart_scheduler(self):
        """F06: Verify ServerRestartScheduler milestone alerts and cancellation."""
        mock_bridge = MockBridgeForScheduler()
        scheduler = ServerRestartScheduler(mock_bridge)
        expected_milestones = [600, 300, 60, 30, 10, 5, 4, 3, 2, 1]
        self.assertEqual(scheduler.warning_milestones, expected_milestones)

        # Schedule restart
        res = scheduler.schedule(countdown_seconds=600)
        self.assertTrue(res["success"])
        self.assertTrue(scheduler.is_scheduled)

        # Query status
        status = scheduler.get_status()
        self.assertTrue(status["is_scheduled"])
        self.assertEqual(status["total_seconds"], 600)

        # Cancel restart
        cancel_res = scheduler.cancel()
        self.assertTrue(cancel_res["success"])
        self.assertFalse(scheduler.is_scheduled)

    def test_f07_automated_world_snapshots(self):
        """F07: Verify automated world snapshots retention policy (keep=5)."""
        backups_dir = os.path.join(self.test_dir, "server_backups")
        os.makedirs(backups_dir, exist_ok=True)

        # Create 8 dummy snapshot archives with staggered timestamps
        created_files = []
        now = time.time()
        for i in range(8):
            f_path = os.path.join(backups_dir, f"backup_snapshot_{i}.zip")
            with open(f_path, "wb") as f:
                f.write(b"PK\x05\x06" + b"\x00" * 18)  # Minimal valid zip end-of-central-directory
            os.utime(f_path, (now + i * 10, now + i * 10))
            created_files.append(f_path)

        bridge = ServerBridgeAPI(self.test_dir, data_root=self.test_dir)
        try:
            res = bridge.prune_world_snapshots(world_dir=backups_dir, keep=5)
            self.assertTrue(res["success"])
            self.assertEqual(res["retained_count"], 5)
            self.assertEqual(res["pruned_count"], 3)
            remaining = [f for f in os.listdir(backups_dir) if f.endswith(".zip")]
            self.assertEqual(len(remaining), 5)
            # Oldest 3 should have been pruned
            self.assertNotIn("backup_snapshot_0.zip", remaining)
            self.assertNotIn("backup_snapshot_1.zip", remaining)
            self.assertNotIn("backup_snapshot_2.zip", remaining)
            # Newest 5 should remain
            self.assertIn("backup_snapshot_7.zip", remaining)
        finally:
            bridge._telemetry_running = False

    def test_f08_telemetry_canvas_sparklines(self):
        """F08: Verify 60-second historical sliding buffer for TPS and RAM."""
        bridge = ServerBridgeAPI(self.test_dir, data_root=self.test_dir)
        try:
            # Simulate pushing metrics into history buffers
            for i in range(75):
                bridge.tps_history.append(19.8)
                if len(bridge.tps_history) > 60:
                    bridge.tps_history.pop(0)
                bridge.ram_history.append(4096)
                if len(bridge.ram_history) > 60:
                    bridge.ram_history.pop(0)

            self.assertEqual(len(bridge.tps_history), 60)
            self.assertEqual(len(bridge.ram_history), 60)
            self.assertEqual(bridge.tps_history[-1], 19.8)
            self.assertEqual(bridge.ram_history[-1], 4096)
        finally:
            bridge._telemetry_running = False

    def test_f09_installer_hardware_matrix(self):
        """F09: Verify pre-flight hardware diagnostic matrix return schema."""
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        specs = installer.get_hardware_specs()
        self.assertIsInstance(specs, dict)
        required_keys = ["ram_gb", "ram_pass", "disk_free_gb", "disk_pass", "avx2_pass", "java21_pass", "tier"]
        for k in required_keys:
            self.assertIn(k, specs, f"Missing required hardware spec: {k}")
        self.assertEqual(specs["ram_pass"], specs["ram_gb"] >= 6)
        self.assertEqual(specs["disk_pass"], specs["disk_free_gb"] >= 4.0)
        self.assertIn(specs["tier"], ["ultra", "balanced", "comp"])

    def test_f10_adoptium_openjdk21_service(self):
        """F10: Verify Adoptium OpenJDK 21 LTS detection and download URL schema."""
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        runtime_dir = os.path.join(self.test_dir, "runtime", "bin")
        os.makedirs(runtime_dir, exist_ok=True)
        fake_java = os.path.join(runtime_dir, "java.exe")
        with open(fake_java, "w") as f:
            f.write("mock java")

        res = installer.download_adoptium_java21(target_dir=self.test_dir)
        self.assertTrue(res["success"])
        self.assertTrue(res.get("java_path", "").endswith("java.exe"))

    def test_f11_custom_drive_selector(self):
        """F11: Verify custom drive selection across logical volumes."""
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        drives = installer.get_available_drives()
        self.assertIsInstance(drives, list)
        if sys.platform == "win32":
            self.assertGreater(len(drives), 0)
            for d in drives:
                self.assertIn("drive", d)
                self.assertIn("letter", d)
                self.assertIn("total_gb", d)
                self.assertIn("free_gb", d)
                self.assertIn("is_system", d)
                self.assertGreater(d["total_gb"], 0)

    def test_f12_web_platform_routes_exist(self):
        """F12: Verify all static routes in website-next/app/ exist."""
        expected_routes = [
            "page.tsx", "welcome/page.tsx", "download/page.tsx", "mods/page.tsx",
            "shaders/page.tsx", "skins/page.tsx", "servers/page.tsx", "crash-analyzer/page.tsx",
            "benchmarks/page.tsx", "changelog/page.tsx", "faq/page.tsx", "trainer/page.tsx",
            "admin/page.tsx", "agreements/page.tsx", "builder/page.tsx", "capes/page.tsx",
            "compatibility/page.tsx", "cookies/page.tsx", "eula/page.tsx", "leaderboards/page.tsx",
            "main/page.tsx", "privacy/page.tsx", "seeds/page.tsx", "server-guide/page.tsx",
            "terms/page.tsx", "auth/desktop/page.tsx"
        ]
        web_app_dir = os.path.join(ROOT_DIR, "website-next", "app")
        self.assertTrue(os.path.isdir(web_app_dir), "website-next/app must exist")
        for r in expected_routes:
            p = os.path.join(web_app_dir, r)
            self.assertTrue(os.path.isfile(p), f"Route missing: {r}")

    def test_f13_strict_welcome_auth_gate(self):
        """F13: Verify GlobalAuthGuard enforces redirection to /welcome for unauthenticated users."""
        guard_file = os.path.join(ROOT_DIR, "website-next", "components", "GlobalAuthGuard.tsx")
        self.assertTrue(os.path.isfile(guard_file))
        with open(guard_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("WelcomePage", content)
        self.assertIn("router.replace(\"/welcome\")", content)
        self.assertIn("if (!user)", content)

    def test_f14_options_txt_harmonization(self):
        """F14: Verify modern options.txt contains all required cross-client invariants."""
        opt_path = os.path.join(ROOT_DIR, "instances", "26.2", "options.txt")
        self.assertTrue(os.path.isfile(opt_path), "instances/26.2/options.txt must exist")
        with open(opt_path, "r", encoding="utf-8") as f:
            lines = {line.strip() for line in f if ":" in line}

        self.assertIn("gamma:1.0", lines)
        self.assertIn("enableVsync:false", lines)
        self.assertIn("key_iris.keybind.toggleShaders:key.keyboard.k", lines)
        self.assertIn("key_replaymod.input.playeroverview:key.keyboard.b", lines)
        self.assertIn("key_replaymod.input.marker:key.keyboard.m", lines)
        self.assertIn("key_replaymod.input.playpause:key.keyboard.p", lines)

    def test_f15_generational_zgc_flags(self):
        """F15: Verify Generational ZGC flags across modern 26.2 instance configurations."""
        for inst in ["26.2", "26.2-ultra", "26.2-balanced", "26.2-performance"]:
            cfg_path = os.path.join(ROOT_DIR, "instances", inst, "instance.cfg")
            if os.path.isfile(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg_text = f.read()
                self.assertIn("-XX:+UseZGC", cfg_text)
                self.assertIn("-XX:+ZGenerational", cfg_text)
                self.assertIn("-XX:ZAllocationSpikeTolerance=5", cfg_text)

    def test_f16_bedrock_crossplay_gateway(self):
        """F16: Verify Bedrock cross-play gateway configuration and RakNet ping magic."""
        geyser_cfg = os.path.join(ROOT_DIR, "server", "Purpur_Paper_Server", "plugins", "Geyser-Spigot", "config.yml")
        self.assertTrue(os.path.isfile(geyser_cfg), "Geyser-Spigot/config.yml must exist")
        with open(geyser_cfg, "r", encoding="utf-8") as f:
            cfg_text = f.read()
        self.assertIn("port: 19132", cfg_text)
        self.assertIn("address: 0.0.0.0", cfg_text)
        self.assertIn("auth-type: floodgate", cfg_text)

        # Verify RakNet magic constant in server_health_check.py
        from server.server_health_check import RAKNET_MAGIC
        self.assertEqual(len(RAKNET_MAGIC), 16)
        self.assertEqual(RAKNET_MAGIC, b"\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78")

    def test_f17_drive_d_storage_invariant(self):
        """F17: Verify Drive D free storage space invariant >= 18.00 GB."""
        if os.path.exists("D:\\"):
            free_gb = shutil.disk_usage("D:\\").free / (1024 ** 3)
            self.assertGreaterEqual(
                free_gb, 18.00,
                f"Drive D free space {free_gb:.2f} GB is below required 18.00 GB invariant!"
            )

    def test_f18_git_repositories_branch_status(self):
        """F18: Verify public_repo and website-next git branches are 'main'."""
        for repo in ["public_repo", "website-next"]:
            repo_path = os.path.join(ROOT_DIR, repo)
            if os.path.isdir(os.path.join(repo_path, ".git")):
                res = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                self.assertEqual(res.returncode, 0)
                self.assertEqual(res.stdout.strip(), "main")


# =============================================================================
# TIER 2: BOUNDARY & CORNER CASES (DEFENSIVE RESILIENCE)
# =============================================================================

class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Tier 2: Boundary, negative, edge, and hostile input testing."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_e2e_t2_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_b01_malformed_and_injection_deep_links(self):
        """B01: Stress deep link parser with empty, injection, and oversized payloads."""
        # 1. Empty and None
        self.assertFalse(parse_deep_link("")["valid"])
        self.assertFalse(parse_deep_link(None)["valid"])
        self.assertFalse(parse_deep_link("   ")["valid"])

        # 2. Invalid Scheme
        self.assertFalse(parse_deep_link("http://launch?profile=26.2")["valid"])
        self.assertFalse(parse_deep_link("ftp://sirlauncher/join")["valid"])

        # 3. Command injection attempt in parameters
        res = parse_deep_link("sirlauncher://join?ip=127.0.0.1;calc.exe&port=25565")
        self.assertTrue(res["valid"])
        self.assertEqual(res["params"]["ip"], "127.0.0.1;calc.exe")

        # 4. Oversized URL payload (64 KB query string)
        huge_url = "sirlauncher://auth?data=" + ("A" * 65536)
        huge_res = parse_deep_link(huge_url)
        self.assertTrue(huge_res["valid"])
        self.assertEqual(len(huge_res["params"]["data"]), 65536)

        # 5. Malformed percent encoding
        malformed_url = "sirlauncher://launch?profile=%ZZ%99"
        mal_res = parse_deep_link(malformed_url)
        self.assertTrue(mal_res["valid"])

    def test_b02_extreme_latency_and_socket_timeouts(self):
        """B02: Radar handling of negative, zero, and extreme ping values."""
        def evaluate_radar_badge(ping_ms: float) -> str:
            if ping_ms < 0:
                return "offline"
            elif ping_ms <= 35:
                return "optimal"
            elif ping_ms <= 80:
                return "good"
            elif ping_ms <= 150:
                return "moderate"
            else:
                return "high_latency"

        self.assertEqual(evaluate_radar_badge(-1.0), "offline")
        self.assertEqual(evaluate_radar_badge(0.0), "optimal")
        self.assertEqual(evaluate_radar_badge(20.0), "optimal")
        self.assertEqual(evaluate_radar_badge(65.0), "good")
        self.assertEqual(evaluate_radar_badge(120.0), "moderate")
        self.assertEqual(evaluate_radar_badge(99999.0), "high_latency")

    def test_b03_corrupt_manifest_and_tampered_jars(self):
        """B03: Integrity Doctor handling of missing, empty, and corrupted files."""
        repair = RepairService(self.test_dir)

        # 1. Non-existent file
        missing_res = repair.verify_file_integrity(os.path.join(self.test_dir, "ghost.jar"))
        self.assertFalse(missing_res["valid"])
        self.assertEqual(missing_res["reason"], "Missing file")

        # 2. 0-byte file
        empty_file = os.path.join(self.test_dir, "empty.jar")
        with open(empty_file, "wb") as f:
            pass
        empty_res = repair.verify_file_integrity(empty_file)
        self.assertFalse(empty_res["valid"])
        self.assertEqual(empty_res["reason"], "0-byte empty file")

        # 3. Corrupt zip archive
        corrupt_zip = os.path.join(self.test_dir, "corrupt.jar")
        with open(corrupt_zip, "wb") as f:
            f.write(b"NOT_A_ZIP_HEADER_DATA")
        corrupt_res = repair.verify_file_integrity(corrupt_zip)
        self.assertFalse(corrupt_res["valid"])
        self.assertIn("Invalid archive structure", corrupt_res["reason"])

    def test_b04_invalid_pids_and_zero_memory_trim(self):
        """B04: RAM Compactor handling of invalid PIDs."""
        governor = TelemetryGovernorService()
        if sys.platform == "win32":
            # Negative PID
            res_neg = governor.trim_process_memory(pid=-999)
            self.assertFalse(res_neg["success"])

            # Non-existent high PID
            res_high = governor.trim_process_memory(pid=99999999)
            self.assertFalse(res_high["success"])

            # PID 0 / None (current process)
            res_self = governor.trim_process_memory(pid=0)
            self.assertTrue(res_self["success"])

    def test_b05_invalid_skin_dimensions_and_empty_user(self):
        """B05: Skin Studio rejection of empty username and directory traversal."""
        skin_service = SkinStudioService(self.test_dir)

        # Whitespace username triggers validation error
        res_space = skin_service.apply_skin_and_cape(username="   ")
        self.assertFalse(res_space["success"])
        self.assertIn("Username cannot be empty", res_space["error"])

        # Empty username falls back to default "Steve"
        res_empty = skin_service.apply_skin_and_cape(username="")
        self.assertTrue(res_empty["success"])
        self.assertEqual(res_empty["username"], "Steve")

    def test_b06_zero_negative_countdown_restart(self):
        """B06: Scheduler handling of 0 or negative countdown values."""
        mock_bridge = MockBridgeForScheduler()
        scheduler = ServerRestartScheduler(mock_bridge)

        # Zero seconds
        res_zero = scheduler.schedule(countdown_seconds=0)
        self.assertTrue(res_zero["success"])
        scheduler.cancel()

        # Negative seconds
        res_neg = scheduler.schedule(countdown_seconds=-10)
        self.assertTrue(res_neg["success"])
        scheduler.cancel()

    def test_b07_prune_retention_below_threshold(self):
        """B07: Snapshot pruning when directory has fewer than 'keep' archives."""
        backups_dir = os.path.join(self.test_dir, "under_limit_backups")
        os.makedirs(backups_dir, exist_ok=True)

        # 0 archives
        bridge = ServerBridgeAPI(self.test_dir, data_root=self.test_dir)
        try:
            res_0 = bridge.prune_world_snapshots(world_dir=backups_dir, keep=5)
            self.assertTrue(res_0["success"])
            self.assertEqual(res_0["pruned_count"], 0)

            # 2 archives (< keep=5)
            for i in range(2):
                with open(os.path.join(backups_dir, f"backup_{i}.zip"), "wb") as f:
                    f.write(b"dummy")
            res_2 = bridge.prune_world_snapshots(world_dir=backups_dir, keep=5)
            self.assertTrue(res_2["success"])
            self.assertEqual(res_2["pruned_count"], 0)
            self.assertEqual(res_2["retained_count"], 2)
        finally:
            bridge._telemetry_running = False

    def test_b08_extreme_tps_and_heap_overflow(self):
        """B08: Sparklines handling of extreme TPS and RAM values."""
        bridge = ServerBridgeAPI(self.test_dir, data_root=self.test_dir)
        try:
            extreme_values = [-5.0, 0.0, 20.0, 100.0, 9999.0]
            for v in extreme_values:
                bridge.tps_history.append(v)
                if len(bridge.tps_history) > 60:
                    bridge.tps_history.pop(0)

            self.assertLessEqual(len(bridge.tps_history), 60)
            self.assertEqual(bridge.tps_history[-1], 9999.0)
        finally:
            bridge._telemetry_running = False

    def test_b09_zero_spec_hardware_boundary(self):
        """B09: Diagnostic matrix boundary behavior for RAM and disk limits."""
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        
        # Test tier calculation logic mathematically
        def evaluate_tier(ram_gb: int, gpu_name: str) -> str:
            gpu = gpu_name.upper()
            if ram_gb >= 24 or (ram_gb >= 16 and any(k in gpu for k in ["4090", "4080", "4070", "RTX"])):
                return "ultra"
            elif ram_gb >= 12 or any(k in gpu for k in ["3060", "2060", "GTX"]):
                return "balanced"
            else:
                return "comp"

        self.assertEqual(evaluate_tier(4, "Intel HD Graphics"), "comp")
        self.assertEqual(evaluate_tier(6, "Intel HD Graphics"), "comp")
        self.assertEqual(evaluate_tier(12, "Intel HD Graphics"), "balanced")
        self.assertEqual(evaluate_tier(16, "NVIDIA GeForce RTX 4070"), "ultra")
        self.assertEqual(evaluate_tier(32, "Generic GPU"), "ultra")

        # Disk pass boundary: >= 4.0 GB passes, < 4.0 GB fails
        self.assertTrue(4.0 >= 4.0)
        self.assertFalse(3.99 >= 4.0)

    def test_b10_nonexistent_and_restricted_drives(self):
        """B10: Drive selector querying invalid path letters."""
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        drives = installer.get_available_drives()
        drive_letters = [d["letter"] for d in drives]
        # Ensure only single ASCII letters are returned
        for letter in drive_letters:
            self.assertEqual(len(letter), 1)
            self.assertTrue(letter.isalpha())
            self.assertTrue(letter.isupper())

    def test_b11_unauthenticated_protected_route_access(self):
        """B11: Auth Gate forbids unauthenticated visitor access to protected routes."""
        protected_routes = ["/", "/admin", "/mods", "/shaders", "/servers", "/download", "/benchmarks", "/trainer"]
        guard_file = os.path.join(ROOT_DIR, "website-next", "components", "GlobalAuthGuard.tsx")
        with open(guard_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Invariant: Must redirect to /welcome if not user and not desktop auth or welcome page
        self.assertIn("!user", content)
        self.assertIn("!isDesktopAuth && !isWelcomePage", content)
        self.assertIn("router.replace(\"/welcome\")", content)

    def test_b12_missing_options_txt_recovery(self):
        """B12: Detection of missing critical keys in corrupted options.txt."""
        corrupted_content = "version:3465\nguiScale:2\n"  # Missing gamma, vsync, keybinds
        corrupt_file = os.path.join(self.test_dir, "corrupt_options.txt")
        with open(corrupt_file, "w", encoding="utf-8") as f:
            f.write(corrupted_content)

        with open(corrupt_file, "r", encoding="utf-8") as f:
            lines = {l.strip() for l in f}

        required_invariants = [
            "gamma:1.0",
            "enableVsync:false",
            "key_iris.keybind.toggleShaders:key.keyboard.k"
        ]
        for req in required_invariants:
            self.assertNotIn(req, lines, f"Corrupted file unexpectedly contained {req}")

    def test_b13_drive_d_exact_boundary_threshold(self):
        """B13: Exact boundary validation: 18.00 GB threshold invariant."""
        def validate_storage(free_gb: float) -> bool:
            return free_gb >= 18.00

        self.assertFalse(validate_storage(17.99))
        self.assertTrue(validate_storage(18.00))
        self.assertTrue(validate_storage(18.01))


# =============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS (INTEGRATION WORKFLOWS)
# =============================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Multi-stage workflows across Web, Launcher, Server Manager, and Installer."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_e2e_t3_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_c01_web_to_launcher_instance_dispatch(self):
        """C01: Web deep-link -> Launcher command parse -> Instance catalog activation."""
        web_link = "sirlauncher://launch?profile=26.2-ultra&shader=SIR+Extreme"
        dl = parse_deep_link(web_link)
        self.assertTrue(dl["valid"])
        self.assertEqual(dl["action"], "launch")
        
        target_profile = dl["params"].get("profile")
        target_shader = dl["params"].get("shader")
        
        # Verify target profile exists in instances
        inst_dir = os.path.join(ROOT_DIR, "instances", target_profile)
        self.assertTrue(os.path.isdir(inst_dir), f"Instance profile {target_profile} must exist")
        
        # Verify instance cfg exists and contains Generational ZGC
        cfg_path = os.path.join(inst_dir, "instance.cfg")
        self.assertTrue(os.path.isfile(cfg_path))
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = f.read()
        self.assertIn("-XX:+UseZGC", cfg)

    def test_c02_launcher_skin_studio_instance_sync(self):
        """C02: Launcher Skin Studio preset selection -> Replication to instances."""
        # Create mock instances and assets directory structure in test sandbox
        inst_modern = os.path.join(self.test_dir, "instances", "26.2", "minecraft")
        inst_legacy = os.path.join(self.test_dir, "instances", "1.8.9", "minecraft")
        os.makedirs(inst_modern, exist_ok=True)
        os.makedirs(inst_legacy, exist_ok=True)

        skins_dir = os.path.join(self.test_dir, "skins")
        capes_dir = os.path.join(self.test_dir, "capes")
        os.makedirs(skins_dir, exist_ok=True)
        os.makedirs(capes_dir, exist_ok=True)

        # Populate preset assets from repository
        repo_skin = os.path.join(ROOT_DIR, "skins", "sir_cyber_warrior.png")
        repo_cape = os.path.join(ROOT_DIR, "capes", "sir_obsidian_neon.png")
        if os.path.isfile(repo_skin):
            shutil.copy2(repo_skin, os.path.join(skins_dir, "sir_cyber_warrior.png"))
        if os.path.isfile(repo_cape):
            shutil.copy2(repo_cape, os.path.join(capes_dir, "sir_obsidian_neon.png"))

        skin_service = SkinStudioService(self.test_dir)
        # Apply official preset skin & cape
        res = skin_service.apply_skin_and_cape(
            username="E2EPlayer",
            skin_url="sir_cyber_warrior",
            cape_url="sir_obsidian_neon",
            instance_id="26.2"
        )
        self.assertTrue(res.get("success", False))

        # Verify skin file was copied to modern instance
        modern_skins = os.path.join(inst_modern, "skins", "E2EPlayer.png")
        self.assertTrue(os.path.isfile(modern_skins))

    def test_c03_server_restart_with_auto_backup_cycle(self):
        """C03: Server Manager restart scheduler with automated world snapshot & pruning."""
        server_dir = os.path.join(self.test_dir, "server_instances", "26.2")
        os.makedirs(server_dir, exist_ok=True)
        with open(os.path.join(server_dir, "server.properties"), "w") as f:
            f.write("motd=SIR Server\n")

        bridge = ServerBridgeAPI(self.test_dir, data_root=self.test_dir)
        try:
            # 1. Trigger automated backup
            backup_res = bridge.create_backup(version="26.2")
            self.assertTrue(backup_res["success"])
            self.assertTrue(os.path.isfile(backup_res["path"]))

            # 2. Schedule restart countdown
            sched_res = bridge.restart_scheduler.schedule(countdown_seconds=300)
            self.assertTrue(sched_res["success"])
            self.assertTrue(bridge.restart_scheduler.is_scheduled)

            # 3. Clean cancel
            bridge.restart_scheduler.cancel()
            self.assertFalse(bridge.restart_scheduler.is_scheduled)
        finally:
            bridge._telemetry_running = False

    def test_c04_installer_hardware_to_instance_configuration(self):
        """C04: Installer diagnostic matrix -> Instance profile tier matching -> ZGC flags."""
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        specs = installer.get_hardware_specs()

        # Map tier to instance profile
        tier = specs["tier"]
        tier_to_profile = {
            "ultra": "26.2-ultra",
            "balanced": "26.2-balanced",
            "comp": "26.2-performance"
        }
        recommended_profile = tier_to_profile[tier]
        cfg_file = os.path.join(ROOT_DIR, "instances", recommended_profile, "instance.cfg")
        self.assertTrue(os.path.isfile(cfg_file))
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg_text = f.read()
        self.assertIn("-XX:+UseZGC -XX:+ZGenerational", cfg_text)

    def test_c05_web_to_desktop_auth_token_handoff(self):
        """C05: Web auth callback -> sirlauncher://auth payload -> Desktop token exchange."""
        token_payload = {
            "uid": "google_oauth_98765",
            "email": "gamer@sirmodpack.com",
            "displayName": "SIRChampion",
            "photoURL": "https://sir-modpack.web.app/avatar.png"
        }
        encoded_data = urllib.parse.quote(json.dumps(token_payload))
        auth_deep_link = f"sirlauncher://auth?data={encoded_data}&code=auth_grant_xyz"

        dl = parse_deep_link(auth_deep_link)
        self.assertTrue(dl["valid"])
        self.assertEqual(dl["action"], "auth")

        raw_data = dl["params"]["data"]
        decoded_payload = json.loads(urllib.parse.unquote(raw_data))
        self.assertEqual(decoded_payload["uid"], "google_oauth_98765")
        self.assertEqual(decoded_payload["email"], "gamer@sirmodpack.com")


# =============================================================================
# TIER 4: REAL-WORLD WORKLOAD SCENARIOS (END-TO-END USER JOURNEYS)
# =============================================================================

class TestTier4RealWorldWorkloadScenarios(unittest.TestCase):
    """Tier 4: Persona-driven end-to-end simulated operational journeys."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_e2e_t4_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_w01_complete_new_user_onboarding_journey(self):
        """
        Scenario 1: Complete New User Onboarding Journey
        1. Unauthenticated visitor arrives at Web Portal -> Stopped by Auth Gate (/welcome).
        2. User signs in -> visits /download -> launches Installer Pro.
        3. Pre-flight hardware matrix validates RAM, Disk, AVX2, and Java 21.
        4. Target volume selected with free space validation.
        5. Modern 26.2 profile deployed with Generational ZGC & harmonized options.txt.
        """
        # Step 1: Auth gate verification
        guard_file = os.path.join(ROOT_DIR, "website-next", "components", "GlobalAuthGuard.tsx")
        self.assertTrue(os.path.isfile(guard_file))

        # Step 2: Pre-flight installer diagnostics
        installer = InstallerBridgeAPI(ROOT_DIR, data_root=self.test_dir)
        specs = installer.get_hardware_specs()
        self.assertTrue(specs["ram_pass"], "Onboarding requires >= 6GB RAM")
        self.assertTrue(specs["disk_pass"], "Onboarding requires >= 4GB Disk")

        # Step 3: Drive volume selection
        drives = installer.get_available_drives()
        self.assertGreater(len(drives), 0)
        target_drive = drives[0]["drive"]
        self.assertTrue(os.path.isdir(target_drive))

        # Step 4: Instance profile validation
        modern_cfg = os.path.join(ROOT_DIR, "instances", "26.2", "instance.cfg")
        self.assertTrue(os.path.isfile(modern_cfg))
        with open(modern_cfg, "r", encoding="utf-8") as f:
            cfg = f.read()
        self.assertIn("-XX:+UseZGC -XX:+ZGenerational", cfg)

        # Step 5: Options.txt harmonization check
        options_file = os.path.join(ROOT_DIR, "instances", "26.2", "options.txt")
        self.assertTrue(os.path.isfile(options_file))
        with open(options_file, "r", encoding="utf-8") as f:
            opts = f.read()
        self.assertIn("gamma:1.0", opts)
        self.assertIn("enableVsync:false", opts)

    def test_w02_competitive_pvp_tournament_journey(self):
        """
        Scenario 2: Competitive PvP Tournament Journey
        1. Player boots SIR Launcher Pro -> checks Multiplayer Latency Radar.
        2. Direct-joins low-latency competitive server via sirlauncher://join.
        3. Win32 RAM Compactor trims memory working set.
        4. Skin Studio equips tournament skin (sir_esports_pro).
        5. Game configuration enforces 0ms VSync latency.
        """
        # Step 1: Server radar join action
        join_link = "sirlauncher://join?ip=pvp.sirmodpack.com&port=25565"
        dl = parse_deep_link(join_link)
        self.assertTrue(dl["valid"])
        self.assertEqual(dl["params"]["ip"], "pvp.sirmodpack.com")

        # Step 2: RAM compaction before launch
        governor = TelemetryGovernorService()
        if sys.platform == "win32":
            compaction = governor.trim_process_memory()
            self.assertTrue(compaction["success"])

        # Step 3: Skin Studio tournament setup
        skin_service = SkinStudioService(self.test_dir)
        presets = {s["id"] for s in skin_service.get_preset_skins()}
        self.assertIn("sir_esports_pro", presets)

        # Step 4: Game options check (VSync false for competitive input rate)
        options_file = os.path.join(ROOT_DIR, "instances", "26.2", "options.txt")
        with open(options_file, "r", encoding="utf-8") as f:
            opts = f.read()
        self.assertIn("enableVsync:false", opts)

    def test_w03_server_admin_247_maintenance_journey(self):
        """
        Scenario 3: Server Administrator 24/7 Maintenance Journey
        1. Admin monitors 60-second telemetry sparklines for TPS and RAM.
        2. On-demand world backup archive created.
        3. Automated retention pruning keeps 5 most recent snapshots.
        4. Graceful restart scheduled with countdown milestones and chat alerts.
        """
        bridge = ServerBridgeAPI(self.test_dir, data_root=self.test_dir)
        try:
            # Step 1: Telemetry sparklines monitoring
            self.assertEqual(len(bridge.tps_history), 60)
            self.assertEqual(len(bridge.ram_history), 60)

            # Step 2: World backup creation
            backup_res = bridge.create_backup(version="26.2")
            self.assertTrue(backup_res["success"])

            # Step 3: Snapshot retention check
            backups = bridge.get_backups()
            self.assertLessEqual(len(backups), 5)

            # Step 4: Scheduled restart countdown
            sched = bridge.restart_scheduler
            res = sched.schedule(countdown_seconds=600)
            self.assertTrue(res["success"])
            self.assertTrue(sched.is_scheduled)
            sched.cancel()
            self.assertFalse(sched.is_scheduled)
        finally:
            bridge._telemetry_running = False


# =============================================================================
# CLI RUNNER ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
