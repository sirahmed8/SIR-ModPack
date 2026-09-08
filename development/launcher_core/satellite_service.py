"""
satellite_service.py — Global Cloud & Minecraft Infrastructure Telemetry.
Zero-Mock Implementation with Real Multi-Threaded TCP Socket Latency & Endpoint Health.
"""
from __future__ import annotations

import socket
import threading
import time
from typing import Any, Dict, List, Optional


class SatelliteService:
    """Provides live TCP socket latency testing and cloud endpoint health diagnostics."""

    def __init__(self) -> None:
        self.nodes = [
            {
                "id": "mojang-auth",
                "host": "authserver.mojang.com",
                "port": 443,
                "location": "Mojang Auth Gateway (Global)",
                "latency_ms": None,
                "status": "Pending",
            },
            {
                "id": "mojang-session",
                "host": "sessionserver.mojang.com",
                "port": 443,
                "location": "Mojang Session Gateway",
                "latency_ms": None,
                "status": "Pending",
            },
            {
                "id": "modrinth-api",
                "host": "api.modrinth.com",
                "port": 443,
                "location": "Modrinth API & CDN (Global)",
                "latency_ms": None,
                "status": "Pending",
            },
            {
                "id": "mc-resources",
                "host": "resources.download.minecraft.net",
                "port": 443,
                "location": "Minecraft Asset Highway",
                "latency_ms": None,
                "status": "Pending",
            },
            {
                "id": "cf-edge",
                "host": "1.1.1.1",
                "port": 443,
                "location": "Cloudflare Anycast Edge",
                "latency_ms": None,
                "status": "Pending",
            },
            {
                "id": "google-edge",
                "host": "8.8.8.8",
                "port": 443,
                "location": "Google Global Anycast DNS",
                "latency_ms": None,
                "status": "Pending",
            },
        ]

    def _ping_node_tcp(self, node: Dict[str, Any]) -> None:
        t0 = time.perf_counter()
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((node["host"], node["port"]))
            elapsed_ms = max(1, int((time.perf_counter() - t0) * 1000))
            node["latency_ms"] = elapsed_ms
            node["status"] = (
                "Optimal"
                if elapsed_ms < 100
                else ("Operational" if elapsed_ms < 250 else "High Latency")
            )
        except socket.timeout:
            node["latency_ms"] = None
            node["status"] = "Timed Out"
        except Exception:
            node["latency_ms"] = None
            node["status"] = "Unreachable"
        finally:
            if s:
                try:
                    s.close()
                except Exception:
                    pass


    def get_satellite_status(self) -> Dict[str, Any]:
        """Performs live parallel TCP ping sweeps across all configured endpoints."""
        threads = []
        node_results = [dict(n) for n in self.nodes]

        for n in node_results:
            t = threading.Thread(target=self._ping_node_tcp, args=(n,), daemon=True)
            t.start()
            threads.append(t)

        for t in threads:
            t.join(timeout=1.2)

        reachable_nodes = [n for n in node_results if n["latency_ms"] is not None]

        if reachable_nodes:
            best = min(reachable_nodes, key=lambda x: x["latency_ms"])  # type: ignore
            avg_latency = round(
                sum(n["latency_ms"] for n in reachable_nodes) / len(reachable_nodes), 1  # type: ignore
            )
            network_status = (
                "Optimal" if len(reachable_nodes) == len(node_results) else "Degraded"
            )
        else:
            best = {"id": "none", "latency_ms": None}
            avg_latency = None
            network_status = "Offline"

        return {
            "satellite_mesh": f"LIVE MESH ({len(reachable_nodes)}/{len(node_results)} Nodes Online)",
            "network_status": network_status,
            "reachable_nodes_count": len(reachable_nodes),
            "total_nodes_count": len(node_results),
            "average_latency_ms": avg_latency,
            "best_node": best["id"],
            "best_latency_ms": best["latency_ms"],
            "nodes": node_results,
            "timestamp": time.strftime("%H:%M:%S"),
        }
