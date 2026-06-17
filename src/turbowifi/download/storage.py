"""
Sparse file storage manager.
"""

import os
from pathlib import Path


class StorageManager:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.fd = None

    def allocate(self, size: int):
        """Pre-allocate a sparse file instantly."""
        # Touch file
        self.filepath.touch(exist_ok=True)
        # Open for writing
        self.fd = os.open(str(self.filepath), os.O_RDWR | os.O_CREAT)
        # Truncate to desired size (sparse allocation on linux/ext4/btrfs)
        os.ftruncate(self.fd, size)

    def write_chunk(self, offset: int, data: bytes):
        """Write bytes at a specific offset safely using pwrite."""
        if self.fd is None:
            self.fd = os.open(str(self.filepath), os.O_RDWR | os.O_CREAT)

        # os.pwrite is atomic for the file offset, ideal for async
        # without needing an asyncio.Lock() over the file pointer.
        os.pwrite(self.fd, data, offset)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __del__(self):
        self.close()
