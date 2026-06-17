"""
Unit tests for AI components (Predictor and Recommender).
"""

from turbowifi.ai.predictor import HeuristicPredictor
from turbowifi.ai.recommender import Recommender
from turbowifi.core.orchestrator import ScanResult, NetworkBaseline
from turbowifi.core.capabilities import PlatformCapabilities, CapabilityMode


def test_heuristic_predictor():
    predictor = HeuristicPredictor()

    current = ScanResult(
        timestamp=100.0,
        latency_ms=250.0,
        jitter_ms=50.0,
        packet_loss_pct=5.0,
        dns_latency_ms=100.0,
        stability_score=0.2,
    )
    baseline = NetworkBaseline(
        latency_ms=20.0,
        jitter_ms=5.0,
        packet_loss_pct=0.0,
        dns_latency_ms=15.0,
        stability_score=0.9,
        sample_count=10,
        last_updated=50.0,
        confidence=1.0,
        latency_p90=30.0,
        jitter_p90=10.0,
        dns_latency_p90=25.0,
    )

    trend = predictor.predict_trend(current, baseline)
    assert trend == "DEGRADING"


def test_recommender():
    caps = PlatformCapabilities(
        platform="linux",
        has_root=True,
        mode=CapabilityMode.FULL_OPTIMIZATION,
        can_ping=True,
        can_traceroute=True,
        can_resolve_dns=True,
        can_modify_dns=True,
        can_read_sysctl=True,
        can_write_sysctl=True,
        can_modify_mtu=True,
        can_bind_port=True,
        can_run_async=True,
        kernel_version="6.8",
        available_congestion=["cubic", "bbr"],
        dns_manager="systemd-resolved",
        default_interface="eth0",
        python_version="3.12",
    )

    recommender = Recommender(caps)

    # Fast network - no recommendations needed
    current_fast = ScanResult(
        timestamp=100.0,
        latency_ms=15.0,
        jitter_ms=2.0,
        packet_loss_pct=0.0,
        dns_latency_ms=10.0,
        stability_score=0.95,
    )
    baseline_fast = NetworkBaseline(
        latency_ms=15.0,
        jitter_ms=2.0,
        packet_loss_pct=0.0,
        dns_latency_ms=10.0,
        stability_score=0.95,
        sample_count=10,
        last_updated=50.0,
        confidence=1.0,
        latency_p90=20.0,
        jitter_p90=5.0,
        dns_latency_p90=15.0,
    )

    plan_fast = recommender.generate_plan(current_fast, baseline_fast)
    assert len(plan_fast) == 0

    # Slow DNS network -> recommend DNS optimization
    current_slow_dns = ScanResult(
        timestamp=100.0,
        latency_ms=15.0,
        jitter_ms=2.0,
        packet_loss_pct=0.0,
        dns_latency_ms=150.0,
        stability_score=0.8,
    )
    plan_slow_dns = recommender.generate_plan(current_slow_dns, baseline_fast)
    assert len(plan_slow_dns) == 1
    assert plan_slow_dns[0].module == "dns"

    # Lossy network -> recommend BBR and MTU
    current_lossy = ScanResult(
        timestamp=100.0,
        latency_ms=30.0,
        jitter_ms=25.0,
        packet_loss_pct=2.0,
        dns_latency_ms=15.0,
        stability_score=0.5,
    )
    plan_lossy = recommender.generate_plan(current_lossy, baseline_fast)
    modules = [r.module for r in plan_lossy]
    assert "tcp" in modules
    assert "mtu" in modules
