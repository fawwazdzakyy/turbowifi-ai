"""
MTU State Machine.
"""

from enum import Enum, auto


class MTUState(Enum):
    IDLE = auto()
    SCANNING = auto()
    VALIDATING = auto()
    BENCHMARKING = auto()
    RECOMMENDING = auto()
    APPLYING = auto()
    VERIFYING = auto()
    ROLLBACK = auto()
    COMPLETED = auto()
    ERROR = auto()
