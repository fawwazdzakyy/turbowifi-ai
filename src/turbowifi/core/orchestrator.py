"""
Data structures representing interfaces between modules.
"""

from dataclasses import dataclass


@dataclass
class ScanResult:
    """Output of the network scanner."""

    latency_ms: float
    jitter_ms: float
    packet_loss_pct: float
    dns_latency_ms: float | None
    stability_score: float
    timestamp: float


@dataclass
class BenchmarkResult:
    """Output of the benchmark engine."""

    timestamp: float
    latency_ms: float
    jitter_ms: float
    packet_loss_pct: float
    dns_latency_ms: float
    stability_score: float
    composite_score: float
    grade: str
    throughput_estimate_mbps: float | None = None


@dataclass
class Recommendation:
    """An AI-recommended optimization."""

    module: str
    action: str
    priority: int
    confidence: float
    params: dict
    reason: str


@dataclass
class NetworkBaseline:
    """Rolling baseline computed from scan history."""

    latency_ms: float
    jitter_ms: float
    packet_loss_pct: float
    dns_latency_ms: float
    stability_score: float
    sample_count: int
    last_updated: float
    confidence: float
    latency_p90: float
    jitter_p90: float
    dns_latency_p90: float
