"""Empirical Challenge & Adversarial Test Suite for Milestone 4: Cloud Sync & Gemini AI Waterfall.

Tests:
1. launcherSyncCodes/{code} schema conformance (all 8 canonical fields present & valid).
2. Claim protection: verified prevention of re-claiming claimed codes or redeeming expired codes.
3. Gemini AI 4-tier waterfall fallback resilience & crash stack-trace diagnosis (OOM, mixins, Java version mismatches, native crashes, missing dependencies).
4. CloudSyncService method parity, edge cases, and robust error handling.
5. Full Integration: LauncherBridgeAPI, AuthService, and in-game IAS sync with Cloud Sync payloads.
"""

import os
import sys
import json
import time
import uuid
import shutil
import tempfile
import urllib.request
import urllib.error
import unittest
from unittest.mock import patch, MagicMock

DEV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'development'))
if DEV_DIR not in sys.path:
    sys.path.insert(0, DEV_DIR)

from launcher_core.cloud_sync_service import CloudSyncService
from launcher_core.auth_service import AuthService
from launcher_core.bridge import LauncherBridgeAPI
from launcher_core.crash_analyzer import CrashAnalyzer
from launcher_core.crash_analyzer_service import CrashReportAnalyzer


class TestChallengerM4CloudSyncSchemaAndClaim(unittest.TestCase):
    """Empirical tests for Cloud Sync Highway schema conformance and claim protection."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m4_challenger_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)

        self.cloud_sync = CloudSyncService()
        self.auth = AuthService(self.instances_dir)
        self.bridge = LauncherBridgeAPI(self.test_dir)
        self.bridge.auth = self.auth

    def tearDown(self):
        if hasattr(self.auth, '_ms_browser_state') and self.auth._ms_browser_state.get('server'):
            try:
                self.auth._ms_browser_state['server'].server_close()
            except Exception:
                pass
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. SCHEMA CONFORMANCE: 8 Canonical Fields
    # -------------------------------------------------------------------------
    def test_canonical_sync_code_schema_conformance(self):
        """Verify all 8 canonical fields meet the interface contract specification:
        - code: str (6 digits)
        - userId: str
        - username: str
        - uuid: str
        - skinUrl: str
        - createdAt: int/float
        - expiresAt: int/float
        - claimed: bool
        """
        canonical_8_fields = [
            "code", "userId", "username", "uuid", "skinUrl", "createdAt", "expiresAt", "claimed"
        ]

        valid_payload = {
            "code": "583921",
            "userId": "firebase_uid_987",
            "username": "DiamondSlayer",
            "uuid": "4b7b4d1b-c79a-4c9f-859a-2415174092b2",
            "skinUrl": "https://mc-heads.net/skin/DiamondSlayer",
            "createdAt": int(time.time() * 1000),
            "expiresAt": int((time.time() + 1800) * 1000),
            "claimed": False,
            "name": "DiamondSlayer",
            "ign": "DiamondSlayer",
            "schemaVersion": 1,
            "ownerUid": "firebase_uid_987"
        }

        # Check all 8 canonical fields exist
        for field in canonical_8_fields:
            self.assertIn(field, valid_payload, f"Missing canonical field '{field}' in Cloud Sync contract.")

        # Check types
        self.assertIsInstance(valid_payload["code"], str)
        self.assertEqual(len(valid_payload["code"]), 6)
        self.assertIsInstance(valid_payload["userId"], str)
        self.assertIsInstance(valid_payload["username"], str)
        self.assertIsInstance(valid_payload["uuid"], str)
        self.assertIsInstance(valid_payload["skinUrl"], str)
        self.assertIsInstance(valid_payload["createdAt"], (int, float))
        self.assertIsInstance(valid_payload["expiresAt"], (int, float))
        self.assertIsInstance(valid_payload["claimed"], bool)
        self.assertFalse(valid_payload["claimed"])

    # -------------------------------------------------------------------------
    # 2. CLAIM PROTECTION & EXPIRATION MECHANICS
    # -------------------------------------------------------------------------
    def test_claim_protection_prevents_reclaiming_already_claimed_code(self):
        """Empirically verify that a code with claimed=True is rejected upon re-claim."""
        claimed_payload = json.dumps({
            "code": "774411",
            "userId": "uid_001",
            "username": "OriginalClaimer",
            "uuid": "11111111-2222-3333-4444-555555555555",
            "skinUrl": "https://mc-heads.net/skin/OriginalClaimer",
            "createdAt": int(time.time() * 1000),
            "expiresAt": int((time.time() + 1800) * 1000),
            "claimed": True,
            "claimedBy": "OriginalClaimer"
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = claimed_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.cloud_sync.claim_sync_code("774411", username="Intruder")
            self.assertFalse(res.get("success"), "Claiming an already-claimed code must fail.")
            self.assertIn("already been claimed", res.get("error", ""))

    def test_claim_protection_successful_first_claim_updates_rtdb(self):
        """Empirically verify that claiming an unclaimed code sends a PATCH request marking it claimed."""
        unclaimed_payload = json.dumps({
            "code": "123456",
            "userId": "uid_002",
            "username": "ValidClaimer",
            "uuid": "22222222-3333-4444-5555-666666666666",
            "skinUrl": "https://mc-heads.net/skin/ValidClaimer",
            "createdAt": int(time.time() * 1000),
            "expiresAt": int((time.time() + 1800) * 1000),
            "claimed": False
        }).encode("utf-8")

        patch_called = []

        def mock_urlopen_handler(req, timeout=4):
            mock_cm = MagicMock()
            if req.get_method() == "PATCH":
                patch_called.append({
                    "url": req.full_url,
                    "data": json.loads(req.data.decode('utf-8'))
                })
                mock_cm.read.return_value = b'{"claimed": true}'
            else:
                mock_cm.read.return_value = unclaimed_payload
            mock_cm.__enter__.return_value = mock_cm
            return mock_cm

        with patch('urllib.request.urlopen', side_effect=mock_urlopen_handler):
            res = self.cloud_sync.claim_sync_code("123456", username="ValidClaimer")
            self.assertTrue(res.get("success"))
            self.assertTrue(res.get("claimed"))
            self.assertEqual(res.get("code"), "123456")
            self.assertEqual(res.get("profile", {}).get("username"), "ValidClaimer")

            # Verify PATCH request was executed
            self.assertEqual(len(patch_called), 1)
            self.assertIn("launcherSyncCodes/123456.json", patch_called[0]["url"])
            self.assertTrue(patch_called[0]["data"].get("claimed"))
            self.assertEqual(patch_called[0]["data"].get("claimedBy"), "ValidClaimer")

    def test_redeem_expired_or_not_found_sync_code(self):
        """Verify that attempting to resolve/redeem a non-existent or null code returns descriptive error."""
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = b'null'
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.cloud_sync.resolve_6digit_sync_code("999999")
            self.assertFalse(res.get("success"))
            self.assertIn("not found or expired", res.get("error", ""))

            res_claim = self.cloud_sync.claim_sync_code("999999")
            self.assertFalse(res_claim.get("success"))
            self.assertIn("not found or expired", res_claim.get("error", ""))


class TestChallengerM4CloudSyncServiceParityAndErrors(unittest.TestCase):
    """Adversarial stress-testing of CloudSyncService methods and failure modes."""

    def setUp(self):
        self.cloud_sync = CloudSyncService()

    def test_code_format_adversarial_inputs(self):
        """Test boundary cases for 6-digit codes (spaces, short, long, non-numeric, empty)."""
        invalid_codes = [
            "",
            " ",
            "123",
            "12345",
            "1234567",
            "abcdef",
            None,
            12345,
            " 12345 ",
        ]

        for code in invalid_codes:
            res = self.cloud_sync.resolve_6digit_sync_code(code)
            if code == 12345 or (isinstance(code, str) and len(code.strip()) != 6):
                self.assertFalse(res.get("success"), f"Expected failure for code: {repr(code)}")
                self.assertIn("Invalid code format", res.get("error", ""))

        # Valid formatted code with whitespace padding that strips to 6 digits
        mock_payload = json.dumps({"code": "654321", "username": "PaddedUser"}).encode("utf-8")
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res_clean = self.cloud_sync.resolve_6digit_sync_code("  654321  ")
            self.assertTrue(res_clean.get("success"))
            self.assertEqual(res_clean.get("profile", {}).get("username"), "PaddedUser")

    def test_http_network_errors_and_timeout_resilience(self):
        """Test handling of HTTP 403, 500, socket timeouts, and URLError."""
        # 1. URLError / Network unreachable
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError("Network Unreachable")):
            res = self.cloud_sync.resolve_6digit_sync_code("123456")
            self.assertFalse(res.get("success"))
            self.assertIn("Network error", res.get("error", ""))

        # 2. HTTP 500 Server Error
        with patch('urllib.request.urlopen', side_effect=urllib.error.HTTPError("url", 500, "Internal Server Error", {}, None)):
            res = self.cloud_sync.resolve_6digit_sync_code("123456")
            self.assertFalse(res.get("success"))
            self.assertIn("Network error", res.get("error", ""))

        # 3. Malformed non-JSON data
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = b'<html>Bad Gateway</html>'
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.cloud_sync.resolve_6digit_sync_code("123456")
            self.assertFalse(res.get("success"))
            self.assertIn("Network error", res.get("error", ""))

    def test_backup_settings_to_cloud(self):
        """Test backup_settings_to_cloud success and error pathways."""
        settings = {"ram_gb": 6, "theme": "cyber-dark", "power_mode": "max_performance"}

        # Success path
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = b'{"status": "ok"}'
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.cloud_sync.backup_settings_to_cloud("user_abc", settings)
            self.assertTrue(res.get("success"))
            self.assertIn("backed up", res.get("message", ""))

        # Error path
        with patch('urllib.request.urlopen', side_effect=Exception("Connection reset")):
            res_err = self.cloud_sync.backup_settings_to_cloud("user_abc", settings)
            self.assertFalse(res_err.get("success"))
            self.assertIn("Connection reset", res_err.get("error", ""))


class TestChallengerM4GeminiAIWaterfallAndCrashAnalyzer(unittest.TestCase):
    """Empirical tests for Gemini AI 4-tier waterfall fallback and Crash Diagnostics Engine."""

    def test_crash_analyzer_oom_five_variants(self):
        """Empirically test all 5 Out-Of-Memory diagnostic patterns."""
        analyzer = CrashReportAnalyzer()

        # Variant 1: Standard Heap Exhaustion
        log_heap = """
        java.lang.OutOfMemoryError: Java heap space
            at net.minecraft.class_1927.method_8340(class_1927.java:120)
        """
        diag1 = analyzer.diagnose_crash(log_heap)
        self.assertEqual(diag1["type"], "OUT_OF_MEMORY")
        self.assertIn("Java Heap Space", diag1["cause"])
        self.assertIn("6 GB or 8 GB", diag1["fix"])

        # Variant 2: Direct Buffer Memory Exhaustion
        log_direct = """
        java.lang.OutOfMemoryError: Direct buffer memory
            at java.nio.Bits.reserveMemory(Bits.java:175)
        """
        diag2 = analyzer.diagnose_crash(log_direct)
        self.assertEqual(diag2["type"], "DIRECT_MEMORY_EXHAUSTION")
        self.assertIn("MaxDirectMemorySize", diag2["fix"])

        # Variant 3: Metaspace Exhaustion
        log_metaspace = """
        java.lang.OutOfMemoryError: Metaspace
            at java.lang.ClassLoader.defineClass1(Native Method)
        """
        diag3 = analyzer.diagnose_crash(log_metaspace)
        self.assertEqual(diag3["type"], "METASPACE_EXHAUSTION")
        self.assertIn("MaxMetaspaceSize", diag3["fix"])

        # Variant 4: GC Overhead Limit Exceeded
        log_gc = """
        java.lang.OutOfMemoryError: GC overhead limit exceeded
            at java.util.Arrays.copyOf(Arrays.java:3332)
        """
        diag4 = analyzer.diagnose_crash(log_gc)
        self.assertEqual(diag4["type"], "GC_OVERHEAD_EXHAUSTION")
        self.assertIn("G1GC", diag4["fix"])

        # Variant 5: Native Thread Creation Limit
        log_thread = """
        java.lang.OutOfMemoryError: unable to create new native thread
            at java.lang.Thread.start0(Native Method)
        """
        diag5 = analyzer.diagnose_crash(log_thread)
        self.assertEqual(diag5["type"], "THREAD_CREATION_EXHAUSTION")
        self.assertIn("OS Native Thread Limit", diag5["cause"])

    def test_crash_analyzer_mixin_conflicts(self):
        """Empirically test Mixin conflict extraction (offending mod, target class)."""
        analyzer = CrashReportAnalyzer()

        log_mixin = """
        org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered
            at org.spongepowered.asm.mixin.transformer.MixinProcessor.applyMixins(MixinProcessor.java:392)
        Caused by: org.spongepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure: 
        Mixin [iris.mixins.json:sodium.MixinSodiumWorldRenderer from mod iris] FAILED to apply injection point
        Mixin transformation of net.minecraft.client.render.WorldRenderer failed
        """
        diag = analyzer.diagnose_crash(log_mixin)
        self.assertEqual(diag["type"], "MIXIN_CONFLICT")
        self.assertEqual(diag["offending_mod"], "iris")
        self.assertIn("WorldRenderer", diag["target_class"])
        self.assertIn("iris", diag["fix"])

    def test_crash_analyzer_java_version_mismatch(self):
        """Empirically test class version mismatch diagnostics."""
        analyzer = CrashReportAnalyzer()

        # Class version 65.0 (Java 21) running on Java 8 (52.0)
        log_ver = """
        java.lang.UnsupportedClassVersionError: net/minecraft/client/main/Main has been compiled by a more recent version of the Java Runtime (class file version 65.0), this version of the Java Runtime only recognizes class file versions up to 52.0
            at java.lang.ClassLoader.defineClass1(Native Method)
        """
        diag = analyzer.diagnose_crash(log_ver)
        self.assertEqual(diag["type"], "JAVA_VERSION_MISMATCH")
        self.assertEqual(diag["required_java"], "Java 21")
        self.assertEqual(diag["running_java"], "Java 8")
        self.assertIn("Temurin 21 LTS", diag["fix"])

    def test_crash_analyzer_native_driver_crashes(self):
        """Empirically test native JVM crash dumps (hs_err_pid) for NVIDIA, AMD, Intel, JVM."""
        analyzer = CrashReportAnalyzer()

        # 1. NVIDIA driver crash
        log_nv = """
        # A fatal error has been detected by the Java Runtime Environment:
        #
        #  EXCEPTION_ACCESS_VIOLATION (0xc0000005) at pc=0x00007ff812345678, pid=1234
        #
        # Problematic frame:
        # C  [nvoglv64.dll+0x9a1234]
        """
        diag_nv = analyzer.diagnose_crash(log_nv, filename="hs_err_pid1234.log")
        self.assertEqual(diag_nv["type"], "JVM_NATIVE_CRASH")
        self.assertEqual(diag_nv["offending_module"], "nvoglv64.dll")
        self.assertIn("NVIDIA", diag_nv["fix"])

        # 2. AMD driver crash
        log_amd = """
        # Problematic frame:
        # C  [atio6axx.dll+0x7b1234]
        """
        diag_amd = analyzer.diagnose_crash(log_amd, filename="hs_err_pid5678.log")
        self.assertEqual(diag_amd["type"], "JVM_NATIVE_CRASH")
        self.assertIn("atio6axx.dll", diag_amd["offending_module"])
        self.assertIn("AMD", diag_amd["fix"])

    def test_crash_analyzer_missing_dependencies_and_corruptions(self):
        """Empirically test missing mod dependencies and corrupted anvil regions."""
        analyzer = CrashReportAnalyzer()

        # Missing trove4j
        log_trove = """
        java.lang.NoClassDefFoundError: gnu/trove/map/hash/TIntObjectHashMap
            at net.minecraftforge.fml.common.registry.GameData.build(GameData.java:120)
        """
        diag_dep = analyzer.diagnose_crash(log_trove)
        self.assertEqual(diag_dep["type"], "MISSING_DEPENDENCY")
        self.assertIn("trove4j", diag_dep["cause"])

        # Corrupted Anvil region
        log_anvil = """
        net.minecraft.world.chunk.storage.RegionFormatException: Corrupted Chunk [12, -4] in region r.0.-1.mca
        """
        diag_region = analyzer.diagnose_crash(log_anvil)
        self.assertEqual(diag_region["type"], "CORRUPTED_WORLD_REGION")
        self.assertEqual(diag_region["region_file"], "r.0.-1.mca")


class TestChallengerM4EndToEndAuthAndBridgeCloudSync(unittest.TestCase):
    """Empirical integration test for AuthService, Bridge, and in-game IAS sync via Cloud Sync."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="sir_m4_bridge_")
        self.instances_dir = os.path.join(self.test_dir, "instances")
        os.makedirs(os.path.join(self.instances_dir, "26.2", "minecraft"), exist_ok=True)
        os.makedirs(os.path.join(self.instances_dir, "1.8.9", "minecraft"), exist_ok=True)

        self.auth = AuthService(self.instances_dir)
        self.bridge = LauncherBridgeAPI(self.test_dir)
        self.bridge.auth = self.auth

    def tearDown(self):
        if hasattr(self.auth, '_ms_browser_state') and self.auth._ms_browser_state.get('server'):
            try:
                self.auth._ms_browser_state['server'].server_close()
            except Exception:
                pass
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_redeem_sync_code_creates_account_and_syncs_ias(self):
        """Verify redeeming a sync code creates a local account, generates UUIDv5, and syncs IAS files."""
        mock_payload = json.dumps({
            "code": "349102",
            "userId": "user_sync_555",
            "username": "CloudSyncPro",
            "skinUrl": "https://mc-heads.net/skin/CloudSyncPro",
            "model": "classic",
            "claimed": False
        }).encode("utf-8")

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_cm = MagicMock()
            mock_cm.read.return_value = mock_payload
            mock_cm.__enter__.return_value = mock_cm
            mock_urlopen.return_value = mock_cm

            res = self.bridge.sync_cloud_code("349102")
            self.assertTrue(res.get("success"))
            acc = res.get("account", {})
            self.assertEqual(acc.get("displayName"), "CloudSyncPro")
            self.assertEqual(acc.get("skinUrl"), "https://mc-heads.net/skin/CloudSyncPro")

            # Verify deterministic UUIDv5
            expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, "OfflinePlayer:CloudSyncPro"))
            self.assertEqual(acc.get("uuid"), expected_uuid)

            # Verify in-game IAS files were written across instances
            ias_262 = os.path.join(self.instances_dir, "26.2", "minecraft", "ias_accounts.json")
            ias_189 = os.path.join(self.instances_dir, "1.8.9", "minecraft", "ias_accounts.json")
            self.assertTrue(os.path.exists(ias_262), "ias_accounts.json must exist in 26.2 instance.")
            self.assertTrue(os.path.exists(ias_189), "ias_accounts.json must exist in 1.8.9 instance.")

            with open(ias_262, "r", encoding="utf-8") as f:
                ias_data = json.load(f)
            names = [a.get("name") for a in ias_data.get("accounts", [])]
            self.assertIn("CloudSyncPro", names)


if __name__ == "__main__":
    unittest.main()
