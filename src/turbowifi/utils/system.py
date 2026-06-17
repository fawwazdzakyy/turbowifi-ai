"""
System-level utilities for network commands.
"""

import subprocess


def run_cmd(cmd: list[str], timeout: float = 5.0) -> subprocess.CompletedProcess[str]:
    """Helper to run a shell command."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
