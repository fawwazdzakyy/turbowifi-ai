"""
Benchmark Engine.

Evaluates current network performance using the same mechanics as the scanner,
but formats it specifically as a pre/post benchmark for optimization.
"""

from dataclasses import dataclass

from turbowifi.network.scanner import Scanner
from turbowifi.core.orchestrator import BenchmarkResult


@dataclass
class BenchmarkComparison:
    before: BenchmarkResult
    after: BenchmarkResult
    latency_delta_pct: float
    jitter_delta_pct: float
    loss_delta_pct: float
    dns_delta_pct: float
    score_delta_pct: float
    improved: bool


class BenchmarkEngine:
    def __init__(self):
        self.scanner = Scanner()

    async def run_benchmark(self, count: int = 20) -> BenchmarkResult:
        """
        Run a full benchmark.
        Uses 20 pings per target by default for higher accuracy than a standard scan.
        """
        scan = await self.scanner.scan_network(count=count)

        # Handle DNS latency formatting
        dns_lat = scan.dns_latency_ms if scan.dns_latency_ms is not None else 1000.0

        composite = self.scanner.compute_composite_score(
            latency_ms=scan.latency_ms,
            jitter_ms=scan.jitter_ms,
            packet_loss_pct=scan.packet_loss_pct,
            dns_latency_ms=dns_lat,
        )
        grade = self.scanner.score_to_grade(composite)

        return BenchmarkResult(
            timestamp=scan.timestamp,
            latency_ms=scan.latency_ms,
            jitter_ms=scan.jitter_ms,
            packet_loss_pct=scan.packet_loss_pct,
            dns_latency_ms=dns_lat,
            stability_score=scan.stability_score,
            composite_score=composite,
            grade=grade,
            throughput_estimate_mbps=None,  # Bandwidth estimation is deferred as per TDR
        )

    def compare(self, before: BenchmarkResult, after: BenchmarkResult) -> BenchmarkComparison:
        """Compare two benchmarks and calculate deltas."""

        def _delta_pct(old: float, new: float, lower_is_better: bool = True) -> float:
            if old == 0:
                return 0.0 if new == 0 else (-100.0 if lower_is_better else 100.0)

            # If lower is better (latency), then (old-new)/old is positive when improved
            # If higher is better (score), then (new-old)/old is positive when improved
            diff = (old - new) if lower_is_better else (new - old)
            return (diff / old) * 100.0

        score_delta = _delta_pct(
            before.composite_score, after.composite_score, lower_is_better=False
        )

        return BenchmarkComparison(
            before=before,
            after=after,
            latency_delta_pct=_delta_pct(before.latency_ms, after.latency_ms),
            jitter_delta_pct=_delta_pct(before.jitter_ms, after.jitter_ms),
            loss_delta_pct=_delta_pct(before.packet_loss_pct, after.packet_loss_pct),
            dns_delta_pct=_delta_pct(before.dns_latency_ms, after.dns_latency_ms),
            score_delta_pct=score_delta,
            improved=score_delta > 0.0 or (score_delta == 0.0 and after.composite_score >= 95.0),
        )
