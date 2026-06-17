"""
TurboWiFi AI Core Exceptions.
"""


class TurboWiFiError(Exception):
    """Base exception for all TurboWiFi errors."""

    pass


class PlatformError(TurboWiFiError):
    """Platform detection or capability errors."""

    pass


class CapabilityError(PlatformError):
    """Operation attempted without required capabilities."""

    pass


class StorageError(TurboWiFiError):
    """Database or filesystem storage errors."""

    pass


class NetworkError(TurboWiFiError):
    """Network scanning, benchmark, or connection errors."""

    pass


class OptimizationError(TurboWiFiError):
    """Errors during optimization application or rollback."""

    pass


class SafetyError(TurboWiFiError):
    """Errors in safety manager (e.g. simulation or backup failures)."""

    pass


class DaemonAlreadyRunningError(TurboWiFiError):
    """Attempted to start daemon when already running."""

    pass
