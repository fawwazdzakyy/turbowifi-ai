"""
Network measurement utilities (ping, dns, routing).
"""

import asyncio
import re
import time
import dns.resolver
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PingResult:
    target: str
    sent: int
    received: int
    packet_loss_pct: float
    rtts: List[float]  # All round-trip times in ms


async def async_ping(target: str, count: int = 10, timeout: int = 1) -> PingResult:
    """
    Asynchronously ping a target and parse the output.
    Uses asyncio.create_subprocess_exec to avoid blocking the event loop.
    """
    cmd = ["ping", "-c", str(count), "-W", str(timeout), target]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode()
    except (FileNotFoundError, PermissionError):
        # Fallback if ping isn't available or fails
        return PingResult(target=target, sent=count, received=0, packet_loss_pct=100.0, rtts=[])

    # Parse ping output
    # Example Linux output:
    # 64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=16.1 ms
    # 10 packets transmitted, 10 received, 0% packet loss, time 9015ms

    rtts = []
    for line in output.splitlines():
        # Match time=xx.x ms
        m = re.search(r"time=([\d\.]+)\s*ms", line)
        if m:
            rtts.append(float(m.group(1)))

    sent = count
    received = len(rtts)

    # Try to parse exact packet loss from summary line
    loss_pct = 100.0
    loss_match = re.search(r"([\d\.]+)%\s*packet\s*loss", output)
    if loss_match:
        loss_pct = float(loss_match.group(1))
    elif sent > 0:
        loss_pct = ((sent - received) / sent) * 100.0

    return PingResult(
        target=target, sent=sent, received=received, packet_loss_pct=loss_pct, rtts=rtts
    )


def resolve_dns_latency(domain: str) -> Optional[float]:
    """Measure latency to resolve a specific domain using system DNS."""
    start = time.perf_counter()
    try:
        # Use default system resolver
        dns.resolver.resolve(domain, "A", lifetime=2.0)
        return (time.perf_counter() - start) * 1000.0
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
    ):
        return None


async def async_resolve_dns_latency(domain: str) -> Optional[float]:
    """Async wrapper for dns resolution."""
    return await asyncio.to_thread(resolve_dns_latency, domain)
