"""
Binary Search Discovery Algorithm for Path MTU.
"""

import subprocess
import logging

logger = logging.getLogger("mtu.binary_search")


class MTUBinarySearch:
    def __init__(self, target_host: str = "8.8.8.8"):
        self.target_host = target_host

    def _probe(self, size: int) -> bool:
        """
        Sends an ICMP probe with the DF (Don't Fragment) bit set.
        Returns True if successful, False if fragmented or lost.
        Note: The actual MTU = ICMP payload + 28 bytes (20 IP header + 8 ICMP header).
        So we probe with payload_size = size - 28.
        """
        payload_size = size - 28
        if payload_size < 0:
            return False

        try:
            # -c 1 (1 ping)
            # -M do (prohibit fragmentation)
            # -s <size> (payload size)
            # -W 1 (1 sec timeout)
            cmd = [
                "ping",
                "-c",
                "1",
                "-M",
                "do",
                "-s",
                str(payload_size),
                "-W",
                "1",
                self.target_host,
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # If exit code is 0, it went through without fragmentation
            if result.returncode == 0:
                return True

            # Exit code non-zero means fragmented or dropped
            return False
        except Exception as e:
            logger.warning(f"Probe failed for size {size}: {e}")
            return False

    def discover(self, low: int = 576, high: int = 1500) -> int:
        """
        Runs a binary search to find the highest MTU that passes without fragmentation.
        """
        optimal = low

        while low <= high:
            mid = (low + high) // 2

            # We want high confidence, so require 2 consecutive successes to consider it good
            successes = 0
            for _ in range(2):
                if self._probe(mid):
                    successes += 1
                else:
                    break

            if successes == 2:
                # Passes! Try a higher MTU
                optimal = mid
                low = mid + 1
            else:
                # Failed/Fragmented! Try a lower MTU
                high = mid - 1

        # Final sanity check on optimal
        if optimal > 576 and not self._probe(optimal):
            # If the determined optimal fails a final check, fallback safely
            optimal = 1492  # Safe default for many connections, or simply don't change

        return optimal
