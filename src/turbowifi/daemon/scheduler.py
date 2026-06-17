"""
Daemon scheduler loop.
"""

import asyncio
import logging
from turbowifi.daemon.worker import DaemonWorker
from turbowifi.daemon.watchdog import Watchdog
from turbowifi.daemon.persistence import DaemonPersistence

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("scheduler")

import time


class DaemonScheduler:
    def __init__(self, interval_seconds: int = 300):
        self.interval = interval_seconds
        self.worker = DaemonWorker()
        self.watchdog = Watchdog(timeout=120.0)  # 2 mins max per cycle
        self.persistence = DaemonPersistence()
        self._running = False

    async def start(self):
        self._running = True
        logger.info("Daemon scheduler started.")
        self.persistence.set_status(
            {
                "state": "STARTING",
                "last_run": None,
                "next_run": None,
                "pause_reason": "Initializing",
                "updated_at": time.time(),
            }
        )

        while self._running:
            logger.info("Starting optimization cycle...")
            self.persistence.set_status(
                {
                    "state": "RUNNING",
                    "last_run": time.time(),
                    "next_run": None,
                    "pause_reason": "Optimizing network",
                    "updated_at": time.time(),
                }
            )

            # Watchdog wraps the worker to catch deadlocks/crashes
            try:
                await self.watchdog.watch(self.worker.run_optimization_cycle())
            except Exception as e:
                logger.error(f"Cycle failed: {e}")
                self.persistence.set_status(
                    {
                        "state": "ERROR",
                        "last_run": time.time(),
                        "next_run": time.time() + self.interval,
                        "pause_reason": f"Error: {e}",
                        "updated_at": time.time(),
                    }
                )

            logger.info(f"Cycle complete. Sleeping for {self.interval}s.")
            next_run = time.time() + self.interval
            self.persistence.set_status(
                {
                    "state": "PAUSED",
                    "last_run": time.time(),
                    "next_run": next_run,
                    "pause_reason": "waiting for interval",
                    "updated_at": time.time(),
                }
            )

            # Avoid busy waiting
            try:
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break

        self.persistence.set_status(
            {
                "state": "STOPPED",
                "last_run": time.time(),
                "next_run": None,
                "pause_reason": "Daemon shut down",
                "updated_at": time.time(),
            }
        )
        logger.info("Daemon scheduler stopped.")

    def stop(self):
        self._running = False
