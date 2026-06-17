"""
MTU Recommendation Engine.
"""

from dataclasses import dataclass
from turbowifi.mtu.scanner import MTUScanResult


@dataclass
class MTURecommendation:
    action: str  # "No Change", "Minor Reduction", "Recommended Change", "Unsafe Result"
    recommended_mtu: int
    why: str
    expected_benefits: str
    risks: str
    confidence: float


class MTURecommendationEngine:
    def generate(self, current_mtu: int, scan_result: MTUScanResult) -> MTURecommendation:
        if not scan_result.success:
            return MTURecommendation(
                action="Unsafe Result",
                recommended_mtu=current_mtu,
                why="MTU discovery probe failed or timed out.",
                expected_benefits="None",
                risks="Applying unknown MTU could cause severe packet loss.",
                confidence=0.0,
            )

        optimal = scan_result.optimal_mtu

        if optimal == current_mtu:
            return MTURecommendation(
                action="No Change",
                recommended_mtu=current_mtu,
                why=f"Your current MTU ({current_mtu}) is already optimal for this network.",
                expected_benefits="Stability is maintained.",
                risks="None",
                confidence=scan_result.confidence,
            )

        if current_mtu - optimal < 40 and current_mtu - optimal > 0:
            return MTURecommendation(
                action="Minor Reduction",
                recommended_mtu=optimal,
                why=f"Discovered slight fragmentation at {current_mtu}. Dropping to {optimal}.",
                expected_benefits="May prevent rare packet drops on specific routes.",
                risks="Slightly increased overhead.",
                confidence=scan_result.confidence,
            )

        return MTURecommendation(
            action="Recommended Change",
            recommended_mtu=optimal,
            why=f"Current MTU {current_mtu} is causing fragmentation. Discovered optimal is {optimal}.",
            expected_benefits="Eliminates IP fragmentation, reducing jitter and stabilizing connections.",
            risks="Lower MTU means slightly higher protocol overhead, but prevents drops.",
            confidence=scan_result.confidence,
        )
