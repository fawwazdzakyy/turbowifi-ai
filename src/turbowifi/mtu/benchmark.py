"""
MTU Benchmarking integration.
"""

from turbowifi.core.benchmark import BenchmarkEngine, BenchmarkResult


class MTUBenchmark:
    def __init__(self):
        self.engine = BenchmarkEngine()

    def run_benchmark(self) -> BenchmarkResult | None:
        """Runs a deep network benchmark to measure latency/jitter/loss."""
        import asyncio
        return asyncio.run(self.engine.run_benchmark())

    def compare(self, before: BenchmarkResult, after: BenchmarkResult):
        """Compares two benchmarks to see if MTU change helped."""
        return self.engine.compare(before, after)
