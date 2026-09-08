"""
crash_analyzer_service.py — Deep Diagnostic Crash Stack-Trace & Native Dump Analyzer Service.
Provides automated root-cause diagnosis across Mixin conflicts, Java version mismatches,
OutOfMemory spectrum (Heap, Direct, Metaspace, GC Overhead, Native Thread),
native crash logs (hs_err_pid*.log), mod dependency conflicts, corrupted region files,
and shader compilation failures.
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from .crash_analyzer import CrashAnalyzer


class CrashReportAnalyzer(CrashAnalyzer):
    """Crash Report Analyzer service class matching architecture contracts."""
    pass


__all__ = ["CrashReportAnalyzer", "CrashAnalyzer"]
