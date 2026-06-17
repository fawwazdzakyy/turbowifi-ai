"""
TCP Tuning Module.
"""

from pathlib import Path
from typing import Dict, Optional

from turbowifi.core.platform import is_root


class SysctlManager:
    """Manages reading and writing to /proc/sys values safely."""

    def read(self, key: str) -> Optional[str]:
        """Read a sysctl value (e.g., 'net.ipv4.tcp_congestion_control')."""
        path = Path("/proc/sys") / key.replace(".", "/")
        try:
            return path.read_text().strip()
        except OSError:
            return None

    def write(self, key: str, value: str) -> bool:
        """Write a sysctl value. Requires root."""
        if not is_root():
            return False

        path = Path("/proc/sys") / key.replace(".", "/")
        try:
            path.write_text(f"{value}\n")
            return True
        except OSError:
            return False


class TCPOptimizer:
    def __init__(self):
        self.sysctl = SysctlManager()

    def get_current_settings(self) -> Dict[str, Optional[str]]:
        return {
            "congestion_control": self.sysctl.read("net.ipv4.tcp_congestion_control"),
            "rmem": self.sysctl.read("net.ipv4.tcp_rmem"),
            "wmem": self.sysctl.read("net.ipv4.tcp_wmem"),
            "fastopen": self.sysctl.read("net.ipv4.tcp_fastopen"),
        }

    def enable_bbr(self) -> bool:
        """
        Enables BBR congestion control. BBR performs much better
        on high-latency or packet-loss-prone networks.
        """
        # Ensure fq queuing discipline is active (required for BBR on older kernels)
        self.sysctl.write("net.core.default_qdisc", "fq")
        return self.sysctl.write("net.ipv4.tcp_congestion_control", "bbr")
