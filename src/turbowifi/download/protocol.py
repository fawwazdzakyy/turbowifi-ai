"""
Protocol sniffer to detect server capabilities.
"""

import aiohttp
from dataclasses import dataclass


@dataclass
class ServerCapabilities:
    url: str
    content_length: int | None
    supports_ranges: bool
    is_resumable: bool
    final_url: str


async def check_capabilities(url: str, session: aiohttp.ClientSession) -> ServerCapabilities:
    """Pre-flight check to see what the server supports."""
    try:
        # Use GET with stream to safely get headers without downloading
        # Some servers block HEAD requests
        async with session.get(url, allow_redirects=True) as resp:
            content_length_str = resp.headers.get("Content-Length")
            accept_ranges = resp.headers.get("Accept-Ranges", "").lower()

            content_length = (
                int(content_length_str)
                if content_length_str and content_length_str.isdigit()
                else None
            )

            supports_ranges = "bytes" in accept_ranges

            # If server didn't send Accept-Ranges, it still might support it. We'd have to test it,
            # but usually servers that support it will send it.

            return ServerCapabilities(
                url=url,
                content_length=content_length,
                supports_ranges=supports_ranges,
                is_resumable=supports_ranges and content_length is not None,
                final_url=str(resp.url),
            )
    except Exception as e:
        import logging

        logging.error(f"Failed to check capabilities: {e}")
        return ServerCapabilities(url, None, False, False, url)
