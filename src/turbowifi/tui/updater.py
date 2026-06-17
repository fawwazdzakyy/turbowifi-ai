"""
Async data fetcher for the TUI.
"""

import asyncio
from textual.app import App
from textual.message import Message

from turbowifi.tui.state import DashboardState
from turbowifi.daemon.persistence import DaemonPersistence
from turbowifi.storage.database import Storage
from turbowifi.storage.queries import Queries
from turbowifi.config.settings import get_db_path
from turbowifi.core.capabilities import resolve_capabilities


class StateUpdated(Message):
    """Emitted when the background task fetches new data."""

    def __init__(self, state: DashboardState) -> None:
        self.state = state
        super().__init__()


class DashboardUpdater:
    def __init__(self, app: App):
        self.app = app
        self.db_path = get_db_path()
        self.storage = Storage(self.db_path)
        self.queries = Queries(self.storage)
        self.daemon_persistence = DaemonPersistence()
        self.caps = resolve_capabilities()
        self._running = False

    async def run(self):
        self._running = True
        while self._running:
            state = DashboardState()

            # 1. Fetch daemon state
            state.daemon_status = self.daemon_persistence.get_state()
            state.capability_mode = self.caps.mode.name

            # 2. Fetch latest network metrics
            recent = self.queries.get_recent_scans(limit=1)
            if recent:
                latest = recent[0]
                state.network_metrics = {
                    "latency": latest.latency_ms,
                    "jitter": latest.jitter_ms,
                    "loss": latest.packet_loss_pct,
                    "dns": latest.dns_latency_ms,
                }

                # Derive score and grade using the Scanner logic
                from turbowifi.network.scanner import Scanner

                scanner = Scanner()
                comp = scanner.compute_composite_score(
                    latest.latency_ms,
                    latest.jitter_ms,
                    latest.packet_loss_pct,
                    latest.dns_latency_ms,
                )
                state.optimization_score = comp
                state.network_grade = scanner.score_to_grade(comp)

            # Post message to UI thread
            self.app.post_message(StateUpdated(state))

            await asyncio.sleep(5.0)

    def stop(self):
        self._running = False
