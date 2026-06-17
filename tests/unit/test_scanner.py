"""
Unit tests for the scanner engine.
"""

import pytest
from turbowifi.network.scanner import Scanner


def test_stability_score():
    scanner = Scanner()

    # Perfect network
    assert scanner.calculate_stability_score(latency=10.0, jitter=2.0, loss=0.0) >= 0.95

    # High loss network (50% loss means 0 stability)
    assert scanner.calculate_stability_score(latency=10.0, jitter=2.0, loss=50.0) == 0.0

    # 10% loss
    assert scanner.calculate_stability_score(latency=20.0, jitter=5.0, loss=10.0) <= 0.50

    # High latency
    assert scanner.calculate_stability_score(latency=500.0, jitter=5.0, loss=0.0) < 0.80


def test_composite_score():
    scanner = Scanner()

    # Perfect
    score = scanner.compute_composite_score(
        latency_ms=10.0, jitter_ms=2.0, packet_loss_pct=0.0, dns_latency_ms=15.0
    )
    assert score >= 95.0

    # Terrible
    score = scanner.compute_composite_score(
        latency_ms=800.0, jitter_ms=80.0, packet_loss_pct=10.0, dns_latency_ms=200.0
    )
    assert score < 20.0


def test_grade_assignment():
    scanner = Scanner()
    assert scanner.score_to_grade(96.0) == "A+"
    assert scanner.score_to_grade(85.0) == "B"
    assert scanner.score_to_grade(50.0) == "F"


@pytest.mark.asyncio
async def test_scan_network(mocker):
    # Mock network tools so we don't actually ping/dns in unit tests
    from turbowifi.utils.network import PingResult

    async def mock_ping(*args, **kwargs):
        return PingResult(
            target="8.8.8.8", sent=10, received=10, packet_loss_pct=0.0, rtts=[20.0] * 10
        )

    async def mock_dns(*args, **kwargs):
        return 30.0

    mocker.patch("turbowifi.network.scanner.async_ping", side_effect=mock_ping)
    mocker.patch("turbowifi.network.scanner.async_resolve_dns_latency", side_effect=mock_dns)

    scanner = Scanner()
    result = await scanner.scan_network(count=10)

    assert result.latency_ms == 20.0
    assert result.jitter_ms == 0.0
    assert result.packet_loss_pct == 0.0
    assert result.dns_latency_ms == 30.0
    assert result.stability_score >= 0.95
