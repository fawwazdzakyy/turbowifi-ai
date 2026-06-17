"""
Platform interactions to Get/Set MTU safely.
"""

import subprocess
import re


class MTUPlatform:
    @staticmethod
    def get_default_interface() -> str | None:
        """Finds the default active network interface."""
        try:
            res = subprocess.run(["ip", "route"], stdout=subprocess.PIPE, text=True)
            for line in res.stdout.splitlines():
                if "default via" in line or "default" in line:
                    match = re.search(r"dev\s+(\S+)", line)
                    if match:
                        return match.group(1)
        except Exception:
            pass
        return None

    @staticmethod
    def get_current_mtu(interface: str) -> int | None:
        """Reads current MTU for a specific interface."""
        try:
            res = subprocess.run(
                ["ip", "link", "show", "dev", interface], stdout=subprocess.PIPE, text=True
            )
            match = re.search(r"mtu\s+(\d+)", res.stdout)
            if match:
                return int(match.group(1))
        except Exception:
            pass
        return None

    @staticmethod
    def set_mtu(interface: str, mtu: int) -> bool:
        """
        Applies MTU to an interface.
        Requires root. We assume the caller checks capabilities.
        """
        try:
            res = subprocess.run(
                ["ip", "link", "set", "dev", interface, "mtu", str(mtu)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return res.returncode == 0
        except Exception:
            return False
