"""
Capability probing and matrix definitions.
"""

import sys
import subprocess
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path

from turbowifi.core.platform import detect_platform, is_root, _get_kernel_version


class CapabilityMode(Enum):
    ANALYSIS_ONLY = auto()  # Can scan, benchmark, recommend — cannot modify
    PARTIAL_OPTIMIZATION = auto()  # Can modify some things
    FULL_OPTIMIZATION = auto()  # Can modify everything


@dataclass
class PlatformCapabilities:
    platform: str  # "linux" | "termux"
    has_root: bool
    mode: CapabilityMode

    # Granular capabilities (probed at runtime)
    can_ping: bool  # Can execute ping command
    can_traceroute: bool  # Can execute traceroute
    can_resolve_dns: bool  # Can do DNS lookups
    can_modify_dns: bool  # Can change system DNS
    can_read_sysctl: bool  # Can read /proc/sys/net/*
    can_write_sysctl: bool  # Can write /proc/sys/net/*
    can_modify_mtu: bool  # Can change interface MTU
    can_bind_port: bool  # Can bind to proxy port
    can_run_async: bool  # asyncio works (always True on supported Python)

    # System information
    kernel_version: str | None
    available_congestion: list[str]
    dns_manager: str  # systemd-resolved | networkmanager | resolv.conf | none
    default_interface: str | None
    python_version: str


def _test_command(cmd: list[str]) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=2)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        return False


def _can_read(path: str) -> bool:
    try:
        Path(path).read_text()
        return True
    except (PermissionError, FileNotFoundError, OSError):
        return False


def _test_bind(port: int) -> bool:
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", port))
        s.close()
        return True
    except OSError:
        return False


def detect_dns_manager() -> str:
    # A simplified version, to be fully implemented in dns optimizer
    if _test_command(["systemctl", "is-active", "systemd-resolved"]):
        return "systemd-resolved"
    elif _test_command(["systemctl", "is-active", "NetworkManager"]):
        return "networkmanager"
    elif Path("/etc/resolv.conf").exists():
        return "resolv.conf"
    return "none"


def _detect_default_interface() -> str | None:
    try:
        res = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            parts = res.stdout.strip().split()
            if "dev" in parts:
                idx = parts.index("dev")
                return parts[idx + 1]
    except (FileNotFoundError, IndexError):
        pass
    return None


def resolve_capabilities() -> PlatformCapabilities:
    """Probes runtime capabilities and returns PlatformCapabilities."""
    platform_name = detect_platform()
    is_termux = platform_name == "termux"
    root = is_root()

    # Probe ping
    can_ping = _test_command(["ping", "-c", "1", "-W", "1", "127.0.0.1"])

    # Probe sysctl read/write
    tcp_cc_path = "/proc/sys/net/ipv4/tcp_congestion_control"
    can_read_sysctl = _can_read(tcp_cc_path)
    # Testing write safely is hard without modifying; root + readable is a good proxy
    can_write_sysctl = root and can_read_sysctl

    # Probe DNS modification
    if root:
        dns_manager = detect_dns_manager()
        can_modify_dns = dns_manager != "none"
    else:
        dns_manager = "none"
        can_modify_dns = False

    # Probe MTU modification (termux might lack ip tool even with root, but let's assume root linux has it)
    can_modify_mtu = root and not is_termux

    # Available congestion algorithms
    available_congestion = []
    try:
        data = Path("/proc/sys/net/ipv4/tcp_available_congestion_control").read_text().strip()
        available_congestion = data.split()
    except (FileNotFoundError, PermissionError, OSError):
        pass

    # Determine capability mode
    if can_modify_dns and can_write_sysctl and can_modify_mtu:
        mode = CapabilityMode.FULL_OPTIMIZATION
    elif can_modify_dns or can_write_sysctl:
        mode = CapabilityMode.PARTIAL_OPTIMIZATION
    else:
        mode = CapabilityMode.ANALYSIS_ONLY

    return PlatformCapabilities(
        platform=platform_name,
        has_root=root,
        mode=mode,
        can_ping=can_ping,
        can_traceroute=_test_command(["traceroute", "-m", "1", "127.0.0.1"]),
        can_resolve_dns=True,  # user space works
        can_modify_dns=can_modify_dns,
        can_read_sysctl=can_read_sysctl,
        can_write_sysctl=can_write_sysctl,
        can_modify_mtu=can_modify_mtu,
        can_bind_port=_test_bind(8080),
        can_run_async=True,
        kernel_version=_get_kernel_version(),
        available_congestion=available_congestion,
        dns_manager=dns_manager,
        default_interface=_detect_default_interface(),
        python_version=sys.version,
    )
