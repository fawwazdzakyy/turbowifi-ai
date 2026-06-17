"""
Unit tests for the BaselineEngine.
"""

from turbowifi.ai.baseline import BaselineEngine
from turbowifi.storage.models import ScanRecord


class MockQueries:
    def __init__(self, scans):
        self.scans = scans

    def get_recent_scans(self, limit=50):
        return self.scans[:limit]


def test_baseline_not_enough_data():
    queries = MockQueries(scans=[])
    engine = BaselineEngine(queries)
    assert engine.compute_baseline() is None


def test_baseline_computation():
    scans = [
        ScanRecord(
            id=i,
            timestamp=i,
            latency_ms=10.0 + i,
            jitter_ms=2.0,
            packet_loss_pct=0.0,
            dns_latency_ms=15.0,
            stability_score=0.9,
        )
        for i in range(10)
    ]
    queries = MockQueries(scans=scans)
    engine = BaselineEngine(queries)

    baseline = engine.compute_baseline()
    assert baseline is not None
    assert baseline.sample_count == 10
    assert baseline.confidence == 0.5  # 10 / 20
    assert 14.0 <= baseline.latency_ms <= 15.0  # Median of 10..19
    assert baseline.jitter_ms == 2.0
