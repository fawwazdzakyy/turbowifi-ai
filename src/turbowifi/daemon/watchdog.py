"""
Watchdog to ensure the daemon doesn't crash or hang.
"""

import asyncio
import logging
from typing import Awaitable

logger = logging.getLogger("watchdog")


class Watchdog:
    def __init__(self, timeout: float = 300.0):
        self.timeout = timeout

    async def watch(self, task: Awaitable):
        """Wraps a task with a timeout and crash handler."""
        try:
            return await asyncio.wait_for(task, timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.error(f"Task timed out after {self.timeout}s.")
            return None
        except Exception:
            logger.exception("Task crashed.")
            return None
