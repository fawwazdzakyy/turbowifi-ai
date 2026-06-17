"""
Unit tests for the Auto Orchestrator.
"""

import pytest
from turbowifi.core.auto import AutoOrchestrator
from turbowifi.core.orchestrator import BenchmarkResult, Recommendation


@pytest.mark.asyncio
async def test_auto_pipeline_dry_run(mocker):
    # Mock everything heavy
    mock_bench = BenchmarkResult(
        timestamp=100.0,
        latency_ms=20.0,
        jitter_ms=5.0,
        packet_loss_pct=0.0,
        dns_latency_ms=10.0,
        stability_score=0.9,
        composite_score=90.0,
        grade="A",
    )
    mocker.patch("turbowifi.core.benchmark.BenchmarkEngine.run_benchmark", return_value=mock_bench)
    mocker.patch("turbowifi.storage.queries.Queries.insert_scan")

    mock_plan = [
        Recommendation(
            module="tcp", action="tcp_bbr", priority=100, confidence=0.9, params={}, reason="test"
        )
    ]
    mocker.patch("turbowifi.ai.recommender.Recommender.generate_plan", return_value=mock_plan)

    orchestrator = AutoOrchestrator()
    improved, plan, before, after = await orchestrator.run_pipeline(dry_run=True)

    # In dry run, it returns the plan in the 'applied' tuple position to be displayed
    assert plan == mock_plan
    assert improved is False
    assert before == mock_bench
    assert after == mock_bench


@pytest.mark.asyncio
async def test_auto_pipeline_no_recommendations(mocker):
    # Mock everything heavy
    mock_bench = BenchmarkResult(
        timestamp=100.0,
        latency_ms=20.0,
        jitter_ms=5.0,
        packet_loss_pct=0.0,
        dns_latency_ms=10.0,
        stability_score=0.9,
        composite_score=90.0,
        grade="A",
    )
    mocker.patch("turbowifi.core.benchmark.BenchmarkEngine.run_benchmark", return_value=mock_bench)
    mocker.patch("turbowifi.storage.queries.Queries.insert_scan")

    mocker.patch("turbowifi.ai.recommender.Recommender.generate_plan", return_value=[])

    orchestrator = AutoOrchestrator()
    improved, applied, before, after = await orchestrator.run_pipeline(dry_run=False)

    assert len(applied) == 0
    assert improved is False
