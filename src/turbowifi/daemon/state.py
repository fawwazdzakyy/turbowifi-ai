"""
Daemon state tracking.
"""

from dataclasses import dataclass
from enum import Enum


class DaemonState(Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"
    STOPPING = "STOPPING"


@dataclass
class DaemonStatus:
    state: str
    pid: int | None
    last_run: float | None
    next_run: float | None
    error_msg: str | None
