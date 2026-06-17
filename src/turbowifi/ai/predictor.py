"""
Network Condition Predictor.

Uses heuristics and statistical baselines rather than heavy ML
to keep the installation lightweight for Termux/Android.
"""

from turbowifi.core.orchestrator import ScanResult, NetworkBaseline


class HeuristicPredictor:
    """
    Simple predictor that estimates future network states based on
    current degradation vs the historical baseline.
    """

    def predict_trend(self, current: ScanResult, baseline: NetworkBaseline | None) -> str:
        """
        Predicts the near-term trend of the network.
        Returns: "STABLE", "DEGRADING", "IMPROVING", "UNKNOWN"
        """
        if not baseline or baseline.sample_count < 5:
            return "UNKNOWN"

        # Compare current against rolling 90th percentile (worst-case normal)
        lat_spike = current.latency_ms > (baseline.latency_p90 * 1.2)
        jit_spike = current.jitter_ms > (baseline.jitter_p90 * 1.5)
        loss_spike = current.packet_loss_pct > max(baseline.packet_loss_pct * 2, 1.0)

        degradations = sum([lat_spike, jit_spike, loss_spike])

        if degradations >= 2:
            return "DEGRADING"
        elif current.stability_score > baseline.stability_score * 1.1:
            return "IMPROVING"

        return "STABLE"

    def estimate_improvement(
        self, action: str, current: ScanResult, baseline: NetworkBaseline | None
    ) -> float:
        """
        Rough heuristic for how much a specific action might improve the stability score.
        Returns expected delta (e.g., +0.05).
        """
        if action == "dns_optimize":
            if current.dns_latency_ms and current.dns_latency_ms > 50.0:
                # High DNS latency is easy to fix
                return 0.15
            return 0.02

        elif action == "tcp_bbr":
            # BBR handles packet loss and jitter well
            if current.packet_loss_pct > 0.5 or current.jitter_ms > 20.0:
                return 0.10
            return 0.01

        elif action == "mtu_probe":
            # MTU helps with packet fragmentation/loss
            if current.packet_loss_pct > 0.1:
                return 0.08
            return 0.01

        return 0.0
