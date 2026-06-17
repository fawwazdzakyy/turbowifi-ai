"""
Unit tests for DNS optimization.
"""

import pytest
from turbowifi.network.dns import SystemdResolvedManager, ResolvConfManager


def test_systemd_resolved_manager(mocker):
    # Mock subprocess
    mock_run = mocker.patch("subprocess.run")

    manager = SystemdResolvedManager()
    success = manager.apply("eth0", "8.8.8.8", "8.8.4.4")

    assert success is True
    assert mock_run.call_count == 2
    mock_run.assert_any_call(
        ["resolvectl", "dns", "eth0", "8.8.8.8", "8.8.4.4"], check=True, capture_output=True
    )


def test_resolv_conf_manager_no_root(mocker):
    # Should fail if not root
    mocker.patch("turbowifi.network.dns.is_root", return_value=False)

    manager = ResolvConfManager()
    success = manager.apply("8.8.8.8", "8.8.4.4")

    assert success is False


def test_resolv_conf_manager_with_root(mocker, tmp_path):
    mocker.patch("turbowifi.network.dns.is_root", return_value=True)

    # Override FILE_PATH to write to tmp dir instead of actual /etc/resolv.conf
    test_file = tmp_path / "resolv.conf"
    ResolvConfManager.FILE_PATH = str(test_file)

    manager = ResolvConfManager()
    success = manager.apply("1.1.1.1", "1.0.0.1")

    assert success is True
    content = test_file.read_text()
    assert "nameserver 1.1.1.1" in content
    assert "nameserver 1.0.0.1" in content


@pytest.mark.asyncio
async def test_dns_benchmark(mocker):
    from turbowifi.network.dns import benchmark_dns_providers

    # Mock network calls
    async def mock_test_dns(ip, **kwargs):
        if "8.8.8.8" in ip or "8.8.4.4" in ip:
            return 20.0
        elif "1.1.1.1" in ip or "1.0.0.1" in ip:
            return 10.0
        return 50.0

    mocker.patch("turbowifi.network.dns._test_dns_server", side_effect=mock_test_dns)

    results = await benchmark_dns_providers()
    assert len(results) > 0
    # Cloudflare should be fastest based on our mock
    assert results[0].name == "Cloudflare"
    assert results[0].latency_ms == 10.0

    # Google should be second
    assert results[1].name == "Google"
    assert results[1].latency_ms == 20.0
