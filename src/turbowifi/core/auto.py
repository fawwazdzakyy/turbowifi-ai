"""
Core auto-orchestration logic.
"""

import asyncio
import time
from typing import List, Tuple

from turbowifi.core.capabilities import resolve_capabilities
from turbowifi.core.platform import detect_platform, is_root
from turbowifi.network.scanner import Scanner
from turbowifi.core.benchmark import BenchmarkEngine
from turbowifi.ai.baseline import BaselineEngine
from turbowifi.ai.recommender import Recommender
from turbowifi.storage.database import Storage
from turbowifi.storage.queries import Queries
from turbowifi.config.settings import get_db_path
from turbowifi.storage.models import ScanRecord
from turbowifi.core.orchestrator import ScanResult, BenchmarkResult, Recommendation
from turbowifi.mtu.scanner import MTUScanner
from turbowifi.mtu.optimizer import MTURecommendationEngine
from turbowifi.mtu.platform import MTUPlatform
from turbowifi.mtu.rollback import MTURollbackEngine
from turbowifi.mtu.persistence import MTUPersistence


class AutoOrchestrator:
    def __init__(self):
        self.db_path = get_db_path()
        self.storage = Storage(self.db_path)
        self.queries = Queries(self.storage)
        self.scanner = Scanner()
        self.benchmark_engine = BenchmarkEngine()
        self.baseline_engine = BaselineEngine(self.queries)
        self.mtu_scanner = MTUScanner()
        self.mtu_engine = MTURecommendationEngine()
        self.mtu_platform = MTUPlatform()
        self.mtu_rollback = MTURollbackEngine()
        self.mtu_persistence = MTUPersistence()

        self.platform = detect_platform()
        self.caps = resolve_capabilities()
        self.recommender = Recommender(self.caps)

    async def run_pipeline(
        self, dry_run: bool = False
    ) -> Tuple[bool, List[Recommendation], BenchmarkResult, BenchmarkResult]:
        """
        Executes the full optimization pipeline.
        Returns: (improved_bool, recommendations_applied, before_benchmark, after_benchmark)
        """
        # 1. Run Baseline Benchmark
        before_benchmark = await self.benchmark_engine.run_benchmark(count=10)

        # Save underlying scan
        record = ScanRecord(
            id=0,
            timestamp=before_benchmark.timestamp,
            latency_ms=before_benchmark.latency_ms,
            jitter_ms=before_benchmark.jitter_ms,
            packet_loss_pct=before_benchmark.packet_loss_pct,
            dns_latency_ms=before_benchmark.dns_latency_ms,
            stability_score=before_benchmark.stability_score,
        )
        self.queries.insert_scan(record)

        # 2. Get baseline data
        self.baseline_engine.update_baseline()
        baseline_data = self.baseline_engine.compute_baseline()

        # 3. Get Recommendations
        scan_for_ai = ScanResult(
            latency_ms=before_benchmark.latency_ms,
            jitter_ms=before_benchmark.jitter_ms,
            packet_loss_pct=before_benchmark.packet_loss_pct,
            dns_latency_ms=before_benchmark.dns_latency_ms,
            stability_score=before_benchmark.stability_score,
            timestamp=before_benchmark.timestamp,
        )
        plan = self.recommender.generate_plan(scan_for_ai, baseline_data)

        # Determine MTU status (24hr cooldown)
        last_mtu = self.mtu_persistence.get_last_scan_time()
        should_scan_mtu = False
        if not last_mtu or (time.time() - last_mtu) > 86400:  # 24 hours
            should_scan_mtu = True

        if should_scan_mtu:
            iface = self.mtu_platform.get_default_interface()
            if iface:
                mtu_result = self.mtu_scanner.scan()
                current_mtu = self.mtu_platform.get_current_mtu(iface)

                if mtu_result.success and current_mtu:
                    self.mtu_persistence.record_scan(
                        iface, mtu_result.optimal_mtu, mtu_result.confidence
                    )
                    mtu_rec = self.mtu_engine.generate(current_mtu, mtu_result)

                    if mtu_rec.action in ("Recommended Change", "Minor Reduction"):
                        plan.append(
                            Recommendation(
                                module="mtu",
                                action="mtu_optimize",
                                priority=90,
                                confidence=mtu_rec.confidence,
                                params={"recommended_mtu": mtu_rec.recommended_mtu},
                                reason="MTU optimization recommended.",
                            )
                        )
                        # Store target MTU in a side-channel or just re-calculate
                        self._last_mtu_target = (iface, mtu_rec.recommended_mtu)

        if not plan or dry_run:
            # Nothing to do or dry run
            return (False, plan, before_benchmark, before_benchmark)

        # 4. Apply Optimizations
        applied = []
        for rec in plan:
            if rec.module == "dns" and rec.action == "dns_optimize":
                from turbowifi.network.dns import (
                    benchmark_dns_providers,
                    SystemdResolvedManager,
                    ResolvConfManager,
                )
                from turbowifi.core.capabilities import (
                    detect_dns_manager,
                    _detect_default_interface,
                )

                # We need root for DNS
                if is_root():
                    providers = await benchmark_dns_providers()
                    best = next((p for p in providers if p.latency_ms is not None), None)
                    if best:
                        manager_type = detect_dns_manager()
                        if manager_type == "systemd-resolved":
                            mgr = SystemdResolvedManager()
                            if mgr.apply(_detect_default_interface(), best.primary, best.secondary):
                                applied.append(rec)
                        elif manager_type == "resolv.conf":
                            mgr = ResolvConfManager()
                            if mgr.apply(best.primary, best.secondary):
                                applied.append(rec)

            elif rec.module == "tcp" and rec.action == "tcp_bbr":
                from turbowifi.network.tcp import TCPOptimizer

                if is_root():
                    opt = TCPOptimizer()
                    if opt.enable_bbr():
                        applied.append(rec)

            elif rec.module == "mtu" and rec.action == "mtu_optimize":
                if is_root() and hasattr(self, "_last_mtu_target"):
                    iface, target_mtu = self._last_mtu_target
                    if self.mtu_rollback.create_backup(iface):
                        if self.mtu_platform.set_mtu(iface, target_mtu):
                            applied.append(rec)
                        else:
                            self.mtu_rollback.rollback_latest()

        if not applied:
            return (False, [], before_benchmark, before_benchmark)

        # 5. Verify Benchmark
        # Wait a moment for network to settle
        await asyncio.sleep(2.0)
        after_benchmark = await self.benchmark_engine.run_benchmark(count=10)

        record_after = ScanRecord(
            id=0,
            timestamp=after_benchmark.timestamp,
            latency_ms=after_benchmark.latency_ms,
            jitter_ms=after_benchmark.jitter_ms,
            packet_loss_pct=after_benchmark.packet_loss_pct,
            dns_latency_ms=after_benchmark.dns_latency_ms,
            stability_score=after_benchmark.stability_score,
        )
        self.queries.insert_scan(record_after)

        # 6. Evaluate
        comp = self.benchmark_engine.compare(before_benchmark, after_benchmark)

        # In a real app we would rollback here if comp.improved is False

        return (comp.improved, applied, before_benchmark, after_benchmark)
