"""
Baseline tracking to learn the user's specific network conditions.
"""

import time
import statistics
from typing import List, Optional

from turbowifi.core.orchestrator import NetworkBaseline
from turbowifi.storage.queries import Queries
from turbowifi.storage.models import BaselineRecord


class BaselineEngine:
    MINIMUM_SAMPLES = 5
    ROLLING_WINDOW = 50
    CONFIDENCE_FULL = 20

    def __init__(self, queries: Queries):
        self.queries = queries

    def compute_baseline(self) -> Optional[NetworkBaseline]:
        """Computes a baseline from the most recent scans in the database."""
        scans = self.queries.get_recent_scans(limit=self.ROLLING_WINDOW)
        if len(scans) < self.MINIMUM_SAMPLES:
            return None

        # Filter out completely broken scans if possible, but for baseline,
        # persistent badness IS the baseline.
        latencies = [s.latency_ms for s in scans]
        jitters = [s.jitter_ms for s in scans]
        losses = [s.packet_loss_pct for s in scans]

        # DNS might be None in some scans if it failed completely
        dns_lats = [s.dns_latency_ms for s in scans if s.dns_latency_ms is not None]
        if not dns_lats:
            # Fallback if every single scan failed DNS
            dns_lats = [1000.0]

        return NetworkBaseline(
            latency_ms=statistics.median(latencies),
            jitter_ms=statistics.median(jitters),
            packet_loss_pct=statistics.median(losses),
            dns_latency_ms=statistics.median(dns_lats),
            stability_score=statistics.mean([s.stability_score for s in scans]),
            sample_count=len(scans),
            last_updated=time.time(),
            confidence=min(len(scans) / self.CONFIDENCE_FULL, 1.0),
            latency_p90=self._percentile(latencies, 90),
            jitter_p90=self._percentile(jitters, 90),
            dns_latency_p90=self._percentile(dns_lats, 90),
        )

    def update_baseline(self) -> Optional[NetworkBaseline]:
        """Recomputes and saves a new baseline."""
        baseline = self.compute_baseline()
        if baseline:
            record = BaselineRecord(
                id=0,
                computed_at=baseline.last_updated,
                sample_count=baseline.sample_count,
                confidence=baseline.confidence,
                latency_ms=baseline.latency_ms,
                jitter_ms=baseline.jitter_ms,
                packet_loss_pct=baseline.packet_loss_pct,
                dns_latency_ms=baseline.dns_latency_ms,
                stability_score=baseline.stability_score,
                latency_p90=baseline.latency_p90,
                jitter_p90=baseline.jitter_p90,
                dns_latency_p90=baseline.dns_latency_p90,
            )
            self.queries.insert_baseline(record)
        return baseline

    def _percentile(self, data: List[float], p: float) -> float:
        if not data:
            return 0.0
        s = sorted(data)
        k = (len(s) - 1) * (p / 100.0)
        f = int(k)
        c = int(k) + 1 if int(k) + 1 < len(s) else int(k)
        if f == c:
            return float(s[f])
        d0 = s[f] * (c - k)
        d1 = s[c] * (k - f)
        return float(d0 + d1)
