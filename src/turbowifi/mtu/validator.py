"""
Validator to weed out unsafe MTU changes.
"""

from turbowifi.mtu.scanner import MTUScanResult


class MTUValidator:
    def validate(self, current_mtu: int, scan_result: MTUScanResult) -> bool:
        """
        Validates if the scanned MTU is safe to apply.
        """
        if not scan_result.success:
            return False

        optimal = scan_result.optimal_mtu

        # Unsafe ranges
        if optimal < 576 or optimal > 1500:
            return False

        # If the scan result is exactly what we have, it's valid but requires no change
        if optimal == current_mtu:
            return True

        # Low confidence
        if scan_result.confidence < 0.5:
            return False

        return True
