"""
Unit tests for platform detection.
"""

from turbowifi.core.platform import detect_platform, is_root


def test_detect_platform(mocker):
    """Test platform detection logic."""
    mocker.patch("pathlib.Path.exists", return_value=True)
    assert detect_platform() == "termux"

    mocker.patch("pathlib.Path.exists", return_value=False)
    assert detect_platform() == "linux"


def test_is_root(mocker):
    """Test root detection logic."""
    mocker.patch("os.geteuid", return_value=0)
    assert is_root() is True

    mocker.patch("os.geteuid", return_value=1000)
    assert is_root() is False
