"""
Core async downloader pool.
"""

import asyncio
import aiohttp
import logging
from typing import List, Callable

from turbowifi.download.segment import Segment
from turbowifi.download.storage import StorageManager
from turbowifi.download.exceptions import NetworkConnectionError

logger = logging.getLogger("downloader")


class AsyncDownloader:
    def __init__(self, url: str, storage: StorageManager, max_connections: int = 4):
        self.url = url
        self.storage = storage
        self.max_connections = max_connections
        self._on_progress = None

    def set_progress_callback(self, callback: Callable[[Segment], None]):
        self._on_progress = callback

    async def _download_segment(self, session: aiohttp.ClientSession, segment: Segment):
        """Downloads a single segment and writes to storage."""
        if segment.status == "COMPLETE":
            return

        segment.status = "DOWNLOADING"
        start = segment.start_byte + segment.downloaded
        end = segment.end_byte

        headers = {"Range": f"bytes={start}-{end}"}

        try:
            async with session.get(self.url, headers=headers) as response:
                if response.status not in (200, 206):
                    raise NetworkConnectionError(f"HTTP {response.status}")

                chunk_size = 128 * 1024  # 128KB chunks

                async for chunk in response.content.iter_chunked(chunk_size):
                    if not chunk:
                        break

                    # Write to sparse file
                    offset = segment.start_byte + segment.downloaded
                    self.storage.write_chunk(offset, chunk)

                    # Update state
                    segment.downloaded += len(chunk)

                    if self._on_progress:
                        self._on_progress(segment)

                segment.status = "COMPLETE"

        except Exception as e:
            segment.status = "FAILED"
            logger.error(f"Segment {segment.index} failed: {e}")
            raise

    async def download_segments(self, segments: List[Segment]):
        """Executes segment downloads concurrently."""
        connector = aiohttp.TCPConnector(limit=self.max_connections)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []

            for seg in segments:
                if seg.status != "COMPLETE":
                    task = asyncio.create_task(self._download_segment(session, seg))
                    tasks.append(task)

            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        raise res

    async def download_single_thread(self):
        """Fallback for servers that don't support Range requests."""
        # We simulate a single segment
        segment = Segment(index=0, start_byte=0, end_byte=-1)
        segment.status = "DOWNLOADING"

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status != 200:
                    raise NetworkConnectionError(f"HTTP {response.status}")

                chunk_size = 128 * 1024
                async for chunk in response.content.iter_chunked(chunk_size):
                    if not chunk:
                        break

                    offset = segment.downloaded
                    self.storage.write_chunk(offset, chunk)
                    segment.downloaded += len(chunk)

                    if self._on_progress:
                        self._on_progress(segment)

        segment.status = "COMPLETE"
