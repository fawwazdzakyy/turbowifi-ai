"""
Unit tests for the MTU Optimizer Engine.
"""

from turbowifi.mtu.scanner import MTUScanResult
from turbowifi.mtu.binary_search import MTUBinarySearch
from turbowifi.mtu.validator import MTUValidator
from turbowifi.mtu.optimizer import MTURecommendationEngine


def test_binary_search_logic():
    engine = MTUBinarySearch("127.0.0.1")

    # Mock _probe so that anything <= 1400 works, > 1400 fails
    def mock_probe(size):
        return size <= 1400

    engine._probe = mock_probe
    optimal = engine.discover(low=576, high=1500)
    assert optimal == 1400


def test_validator_unsafe():
    validator = MTUValidator()

    # Out of bounds
    res1 = MTUScanResult("127.0.0.1", 500, True, 1.0)
    assert not validator.validate(1500, res1)

    # Low confidence
    res2 = MTUScanResult("127.0.0.1", 1400, True, 0.4)
    assert not validator.validate(1500, res2)

    # Failed scan
    res3 = MTUScanResult("127.0.0.1", 1400, False, 1.0)
    assert not validator.validate(1500, res3)


def test_recommendation_engine():
    engine = MTURecommendationEngine()

    # No Change
    res1 = MTUScanResult("127.0.0.1", 1500, True, 1.0)
    rec = engine.generate(1500, res1)
    assert rec.action == "No Change"

    # Minor Reduction
    res2 = MTUScanResult("127.0.0.1", 1480, True, 1.0)
    rec = engine.generate(1500, res2)
    assert rec.action == "Minor Reduction"
    assert rec.recommended_mtu == 1480

    # Recommended Change
    res3 = MTUScanResult("127.0.0.1", 1400, True, 0.9)
    rec = engine.generate(1500, res3)
    assert rec.action == "Recommended Change"
    assert rec.recommended_mtu == 1400

    # Failed Scan
    res4 = MTUScanResult("127.0.0.1", 1500, False, 0.0)
    rec = engine.generate(1500, res4)
    assert rec.action == "Unsafe Result"
