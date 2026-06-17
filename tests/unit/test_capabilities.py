"""
Unit tests for capability resolution.
"""

from turbowifi.core.capabilities import resolve_capabilities, CapabilityMode


def test_resolve_capabilities_linux_root(mocker):
    mocker.patch("turbowifi.core.capabilities.detect_platform", return_value="linux")
    mocker.patch("turbowifi.core.capabilities.is_root", return_value=True)
    mocker.patch("turbowifi.core.capabilities._test_command", return_value=True)
    mocker.patch("turbowifi.core.capabilities._can_read", return_value=True)
    mocker.patch("turbowifi.core.capabilities.detect_dns_manager", return_value="systemd-resolved")

    caps = resolve_capabilities()
    assert caps.has_root is True
    assert caps.mode == CapabilityMode.FULL_OPTIMIZATION
    assert caps.can_modify_dns is True
    assert caps.can_modify_mtu is True


def test_resolve_capabilities_termux_no_root(mocker):
    mocker.patch("turbowifi.core.capabilities.detect_platform", return_value="termux")
    mocker.patch("turbowifi.core.capabilities.is_root", return_value=False)
    mocker.patch("turbowifi.core.capabilities._can_read", return_value=False)

    caps = resolve_capabilities()
    assert caps.has_root is False
    assert caps.mode == CapabilityMode.ANALYSIS_ONLY
    assert caps.can_modify_dns is False
    assert caps.can_modify_mtu is False
