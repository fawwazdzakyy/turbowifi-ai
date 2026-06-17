"""
Unit tests for the BenchmarkEngine.
"""

import pytest
from turbowifi.core.benchmark import BenchmarkEngine
from turbowifi.core.orchestrator import BenchmarkResult


@pytest.mark.asyncio
async def test_run_benchmark(mocker):
    # Mock scanner
    from turbowifi.core.orchestrator import ScanResult

    mock_scan = ScanResult(
        latency_ms=15.0,
        jitter_ms=1.0,
        packet_loss_pct=0.0,
        dns_latency_ms=12.0,
        stability_score=0.98,
        timestamp=1000.0,
    )

    mocker.patch("turbowifi.network.scanner.Scanner.scan_network", return_value=mock_scan)

    engine = BenchmarkEngine()
    result = await engine.run_benchmark(count=2)

    assert result.latency_ms == 15.0
    assert result.composite_score > 90.0
    assert result.grade in ("A+", "A")


def test_benchmark_comparison():
    engine = BenchmarkEngine()

    before = BenchmarkResult(
        timestamp=100.0,
        latency_ms=50.0,
        jitter_ms=10.0,
        packet_loss_pct=2.0,
        dns_latency_ms=40.0,
        stability_score=0.5,
        composite_score=60.0,
        grade="D",
    )

    after = BenchmarkResult(
        timestamp=200.0,
        latency_ms=25.0,
        jitter_ms=5.0,
        packet_loss_pct=0.0,
        dns_latency_ms=20.0,
        stability_score=0.9,
        composite_score=85.0,
        grade="B",
    )

    comp = engine.compare(before, after)

    assert comp.latency_delta_pct == 50.0  # (50-25)/50 = 50% improvement
    assert comp.score_delta_pct > 0.0  # Score increased
    assert comp.improved is True
