"""
Network scanner implementation.
"""

import time
import asyncio
import statistics
from typing import List

from turbowifi.core.orchestrator import ScanResult
from turbowifi.utils.network import async_ping, async_resolve_dns_latency


class Scanner:
    PING_TARGETS = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
    DNS_TEST_DOMAINS = ["google.com", "cloudflare.com", "github.com", "amazon.com", "wikipedia.org"]

    async def scan_network(self, count: int = 10) -> ScanResult:
        """Run a standard network condition scan."""
        # Ping targets concurrently
        ping_tasks = [async_ping(target, count=count) for target in self.PING_TARGETS]
        ping_results = await asyncio.gather(*ping_tasks)

        all_rtts = []
        total_sent = 0
        total_recv = 0

        for result in ping_results:
            all_rtts.extend(result.rtts)
            total_sent += result.sent
            total_recv += result.received

        latency_ms = statistics.median(all_rtts) if all_rtts else 999.0
        jitter_ms = statistics.stdev(all_rtts) if len(all_rtts) > 1 else 999.0
        packet_loss_pct = (
            ((total_sent - total_recv) / total_sent * 100) if total_sent > 0 else 100.0
        )

        # DNS latency
        dns_tasks = [async_resolve_dns_latency(domain) for domain in self.DNS_TEST_DOMAINS]
        dns_results = await asyncio.gather(*dns_tasks)
        valid_dns = [d for d in dns_results if d is not None]
        dns_latency_ms = statistics.median(valid_dns) if valid_dns else None

        stability = self.calculate_stability_score(latency_ms, jitter_ms, packet_loss_pct)

        return ScanResult(
            latency_ms=latency_ms,
            jitter_ms=jitter_ms,
            packet_loss_pct=packet_loss_pct,
            dns_latency_ms=dns_latency_ms,
            stability_score=stability,
            timestamp=time.time(),
        )

    def calculate_stability_score(self, latency: float, jitter: float, loss: float) -> float:
        """
        Calculates a 0.0-1.0 stability score.
        High latency, jitter, or loss will rapidly degrade the score.
        """
        if loss >= 50.0:
            return 0.0

        loss_factor = max(0.0, 1.0 - (loss / 10.0))  # 10% loss = 0.0

        # Latency factor: 0ms=1.0, 200ms=0.5, 500ms=0.0
        lat_factor = max(0.0, 1.0 - (latency / 500.0))

        # Jitter factor: 0ms=1.0, 50ms=0.5, 100ms=0.0
        jit_factor = max(0.0, 1.0 - (jitter / 100.0))

        return round(loss_factor * 0.5 + lat_factor * 0.3 + jit_factor * 0.2, 2)

    def score_to_grade(self, composite_score: float) -> str:
        if composite_score >= 95:
            return "A+"
        if composite_score >= 90:
            return "A"
        if composite_score >= 80:
            return "B"
        if composite_score >= 70:
            return "C"
        if composite_score >= 60:
            return "D"
        return "F"

    def compute_composite_score(
        self, latency_ms: float, jitter_ms: float, packet_loss_pct: float, dns_latency_ms: float
    ) -> float:
        """Returns 0-100 score based on piecewise linear scaling."""

        def _piecewise(val: float, points: List[tuple[float, float]]) -> float:
            if val <= points[0][0]:
                return points[0][1]
            if val >= points[-1][0]:
                return points[-1][1]
            for i in range(len(points) - 1):
                x0, y0 = points[i]
                x1, y1 = points[i + 1]
                if x0 <= val <= x1:
                    t = (val - x0) / (x1 - x0)
                    return y0 + t * (y1 - y0)
            return 0.0

        lat_score = _piecewise(latency_ms, [(0, 100), (50, 80), (150, 50), (500, 10), (1000, 0)])
        jit_score = _piecewise(jitter_ms, [(0, 100), (5, 90), (20, 60), (50, 30), (100, 0)])
        loss_score = _piecewise(packet_loss_pct, [(0, 100), (0.5, 80), (2, 50), (5, 20), (10, 0)])

        # Handle cases where DNS failed completely
        dns_val = dns_latency_ms if dns_latency_ms is not None else 1000.0
        dns_score = _piecewise(dns_val, [(0, 100), (20, 90), (50, 70), (100, 40), (200, 0)])

        return round(lat_score * 0.30 + jit_score * 0.25 + loss_score * 0.25 + dns_score * 0.20, 1)
