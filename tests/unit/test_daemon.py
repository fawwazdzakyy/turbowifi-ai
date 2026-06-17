"""
Unit tests for the Background Daemon.
"""

import pytest
import asyncio
from turbowifi.daemon.persistence import DaemonPersistence
from turbowifi.daemon.watchdog import Watchdog


def test_daemon_persistence_set_get_state(mocker):
    # Mock storage so it uses an in-memory DB or simple connection
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # We must also create the daemon_state table since we bypassed Storage init
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daemon_state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at REAL NOT NULL
        )
    """)

    mocker.patch("turbowifi.storage.database.Storage.get_connection", return_value=conn)

    # Needs a hack for context manager if get_connection returns bare conn
    class MockConn:
        def __init__(self, c):
            self.c = c

        def __enter__(self):
            return self.c

        def __exit__(self, *args):
            pass

    mocker.patch("turbowifi.storage.database.Storage.get_connection", return_value=MockConn(conn))

    persistence = DaemonPersistence()

    assert persistence.get_state() == "STOPPED"

    persistence.set_state("RUNNING")
    assert persistence.get_state() == "RUNNING"


@pytest.mark.asyncio
async def test_watchdog_timeout():
    watchdog = Watchdog(timeout=0.1)

    async def slow_task():
        await asyncio.sleep(0.5)
        return "success"

    result = await watchdog.watch(slow_task())
    assert result is None


@pytest.mark.asyncio
async def test_watchdog_crash():
    watchdog = Watchdog(timeout=1.0)

    async def crashing_task():
        raise ValueError("Simulated crash")

    result = await watchdog.watch(crashing_task())
    assert result is None


@pytest.mark.asyncio
async def test_watchdog_success():
    watchdog = Watchdog(timeout=1.0)

    async def fast_task():
        return "success"

    result = await watchdog.watch(fast_task())
    assert result == "success"
