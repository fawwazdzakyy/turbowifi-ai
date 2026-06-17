"""
MTU Discovery Orchestrator.
"""

from dataclasses import dataclass
from turbowifi.mtu.binary_search import MTUBinarySearch


@dataclass
class MTUScanResult:
    target_host: str
    optimal_mtu: int
    success: bool
    confidence: float


class MTUScanner:
    def __init__(self, target_host: str = "8.8.8.8"):
        self.target_host = target_host
        self.search_engine = MTUBinarySearch(target_host)

    def scan(self) -> MTUScanResult:
        """
        Runs the binary search to find optimal MTU.
        """
        try:
            optimal = self.search_engine.discover(low=576, high=1500)

            # If the discovered MTU is 1500, we have 100% confidence.
            # If it's very low, confidence might be lower because of potential intermediary nodes.
            confidence = 1.0 if optimal >= 1400 else 0.8

            return MTUScanResult(
                target_host=self.target_host,
                optimal_mtu=optimal,
                success=True,
                confidence=confidence,
            )
        except Exception:
            return MTUScanResult(self.target_host, 1500, False, 0.0)
