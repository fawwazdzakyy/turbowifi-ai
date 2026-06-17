"""
Platform detection.
"""

import os
import platform
from pathlib import Path


def _get_kernel_version() -> str | None:
    try:
        return platform.release()
    except Exception:
        return None


def detect_platform() -> str:
    """
    Detects if running on Termux or standard Linux.
    Returns: "termux" or "linux"
    """
    if Path("/data/data/com.termux").exists():
        return "termux"
    return "linux"


def is_root() -> bool:
    """Check if process has root privileges."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False
