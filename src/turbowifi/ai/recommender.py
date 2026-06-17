"""
Expert Rule-Based Recommendation Engine.
"""

from typing import List

from turbowifi.core.orchestrator import Recommendation, ScanResult, NetworkBaseline
from turbowifi.core.capabilities import PlatformCapabilities, CapabilityMode
from turbowifi.ai.predictor import HeuristicPredictor


class Recommender:
    def __init__(self, capabilities: PlatformCapabilities):
        self.capabilities = capabilities
        self.predictor = HeuristicPredictor()

    def generate_plan(
        self, current: ScanResult, baseline: NetworkBaseline | None
    ) -> List[Recommendation]:
        """Generate an ordered list of recommended optimizations."""
        recs = []

        if self.capabilities.mode == CapabilityMode.ANALYSIS_ONLY:
            # We can only recommend manual actions
            return recs

        # Rule 1: DNS Latency
        # Trigger if DNS is slow (>50ms) or significantly worse than baseline
        dns_threshold = max(50.0, (baseline.dns_latency_p90 * 1.5) if baseline else 50.0)

        if current.dns_latency_ms and current.dns_latency_ms > dns_threshold:
            if self.capabilities.can_modify_dns:
                recs.append(
                    Recommendation(
                        module="dns",
                        action="dns_optimize",
                        priority=100,
                        confidence=0.9,
                        params={},
                        reason=f"DNS latency ({current.dns_latency_ms:.1f}ms) is unusually high.",
                    )
                )

        # Rule 2: TCP Congestion Control
        # Trigger if jitter or loss is high
        jit_threshold = max(20.0, (baseline.jitter_p90 * 1.5) if baseline else 20.0)

        if (
            current.jitter_ms > jit_threshold or current.packet_loss_pct > 0.5
        ) and self.capabilities.can_write_sysctl:
            if "bbr" in self.capabilities.available_congestion:
                recs.append(
                    Recommendation(
                        module="tcp",
                        action="tcp_bbr",
                        priority=80,
                        confidence=0.85,
                        params={"algorithm": "bbr"},
                        reason="High jitter/loss detected. BBR congestion control mitigates this.",
                    )
                )

        # Rule 3: MTU Probing
        # Trigger if consistent small packet loss occurs without high latency
        if (
            current.packet_loss_pct > 0.1
            and current.latency_ms < 100.0
            and self.capabilities.can_modify_mtu
        ):
            recs.append(
                Recommendation(
                    module="mtu",
                    action="mtu_probe",
                    priority=60,
                    confidence=0.7,
                    params={"strategy": "binary_search"},
                    reason="Packet loss on low latency connection suggests MTU fragmentation.",
                )
            )

        # Sort by priority (descending)
        recs.sort(key=lambda r: r.priority, reverse=True)
        return recs
