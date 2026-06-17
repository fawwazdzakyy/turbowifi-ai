"""
Custom exceptions for the Download Engine.
"""


class DownloadError(Exception):
    """Base class for download-related errors."""

    pass


class RangeNotSupportedError(DownloadError):
    """Raised when the server does not support HTTP Range requests."""

    pass


class ChecksumMismatchError(DownloadError):
    """Raised when the downloaded file's checksum does not match the expected hash."""

    pass


class NetworkConnectionError(DownloadError):
    """Raised when there is a critical network failure during download."""

    pass
