"""
Segmentation logic for splitting downloads.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Segment:
    index: int
    start_byte: int
    end_byte: int
    downloaded: int = 0
    status: str = "PENDING"  # PENDING, DOWNLOADING, COMPLETE, FAILED


def create_segments(total_length: int, num_segments: int) -> List[Segment]:
    """Divides a file of total_length into num_segments."""
    if total_length <= 0:
        return []

    if num_segments <= 0:
        num_segments = 1

    chunk_size = total_length // num_segments
    segments = []

    for i in range(num_segments):
        start = i * chunk_size
        # The last segment takes the remainder
        end = total_length - 1 if i == num_segments - 1 else start + chunk_size - 1
        segments.append(Segment(index=i, start_byte=start, end_byte=end))

    return segments


def calculate_optimal_segments(total_length: int, base_concurrency: int) -> int:
    """Dynamically determine how many segments to use."""
    if total_length < 1024 * 1024:  # < 1MB
        return 1
    if total_length < 10 * 1024 * 1024:  # < 10MB
        return min(base_concurrency, 2)
    if total_length < 100 * 1024 * 1024:  # < 100MB
        return min(base_concurrency, 8)

    # > 100MB
    return min(base_concurrency, 16)
