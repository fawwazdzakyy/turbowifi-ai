"""
Unit tests for TCP tuning.
"""

from turbowifi.network.tcp import SysctlManager, TCPOptimizer


def test_sysctl_read(mocker, tmp_path):
    # Mock /proc/sys
    sys_dir = tmp_path / "sys"
    sys_dir.mkdir()

    ipv4_dir = sys_dir / "net" / "ipv4"
    ipv4_dir.mkdir(parents=True)

    cc_file = ipv4_dir / "tcp_congestion_control"
    cc_file.write_text("cubic\n")

    mocker.patch(
        "turbowifi.network.tcp.Path", side_effect=lambda p: sys_dir / p.replace("/proc/sys/", "")
    )

    manager = SysctlManager()
    assert manager.read("net.ipv4.tcp_congestion_control") == "cubic"
    assert manager.read("net.ipv4.nonexistent") is None


def test_sysctl_write_no_root(mocker):
    mocker.patch("turbowifi.network.tcp.is_root", return_value=False)

    manager = SysctlManager()
    assert manager.write("net.ipv4.tcp_congestion_control", "bbr") is False


def test_tcp_optimizer_enable_bbr(mocker):
    mocker.patch("turbowifi.network.tcp.is_root", return_value=True)
    mock_write = mocker.patch("turbowifi.network.tcp.SysctlManager.write", return_value=True)

    opt = TCPOptimizer()
    success = opt.enable_bbr()

    assert success is True
    # Should write qdisc fq and cc bbr
    assert mock_write.call_count == 2
    mock_write.assert_any_call("net.ipv4.tcp_congestion_control", "bbr")
