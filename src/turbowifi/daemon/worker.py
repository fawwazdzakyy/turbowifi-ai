"""
Background worker that runs the actual orchestration.
"""

from turbowifi.core.auto import AutoOrchestrator
from turbowifi.daemon.persistence import DaemonPersistence


class DaemonWorker:
    def __init__(self):
        self.orchestrator = AutoOrchestrator()
        self.persistence = DaemonPersistence()

    async def run_optimization_cycle(self):
        """Runs the orchestrator and saves state safely."""
        self.persistence.set_state("RUNNING")
        try:
            # Run without dry_run so it actually optimizes if needed
            improved, applied, before, after = await self.orchestrator.run_pipeline(dry_run=False)
            # Cleanup old DB rows
            self.persistence.cleanup_old_scans()
            return improved, applied
        except Exception as e:
            self.persistence.set_state("ERROR")
            raise e
        finally:
            self.persistence.set_state("IDLE")
