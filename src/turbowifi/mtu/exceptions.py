"""
MTU custom exceptions.
"""


class MTUError(Exception):
    """Base class for MTU engine errors."""

    pass


class MTUScanError(MTUError):
    """Raised when the binary search scan fails completely."""

    pass


class MTUApplyError(MTUError):
    """Raised when applying an MTU fails (e.g. permission denied)."""

    pass


class MTURollbackError(MTUError):
    """Raised when a rollback fails, this is critical."""

    pass
