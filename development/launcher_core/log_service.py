"""
log_service.py — Compatibility alias module forwarding to logs_service.py.
"""
from __future__ import annotations

from .logs_service import LogsService, ProcessLogStreamer

__all__ = ["LogsService", "ProcessLogStreamer"]
