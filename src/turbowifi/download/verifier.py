"""
Checksum verification logic.
"""

import hashlib
from pathlib import Path
from turbowifi.download.exceptions import ChecksumMismatchError


def verify_checksum(filepath: str, expected_hash: str, algorithm: str = "sha256") -> bool:
    """Verifies the checksum of a downloaded file."""
    path = Path(filepath)
    if not path.exists():
        return False

    expected_hash = expected_hash.lower()
    algorithm = algorithm.lower()

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    # Read in chunks to avoid memory spike
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096 * 1024), b""):
            hasher.update(chunk)

    calculated = hasher.hexdigest()

    if calculated != expected_hash:
        raise ChecksumMismatchError(f"Expected {expected_hash}, got {calculated}")

    return True
