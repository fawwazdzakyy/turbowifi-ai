"""
Configuration and paths.
"""

import os
from pathlib import Path

from turbowifi.constants import APP_NAME


def get_data_dir() -> Path:
    """Get the standard data directory for the application."""
    # Check if running in Termux
    is_termux = os.path.exists("/data/data/com.termux")
    if is_termux:
        # Termux environment doesn't strictly follow XDG
        base_dir = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))
        data_dir = base_dir / "var" / "lib" / APP_NAME
    else:
        # Standard XDG base directory for Linux
        if os.geteuid() == 0:
            # If running as root, store in system-wide state dir
            data_dir = Path("/var/lib") / APP_NAME
        else:
            # If running as user, use XDG_DATA_HOME
            xdg_data_home = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
            data_dir = Path(xdg_data_home) / APP_NAME

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_db_path() -> Path:
    """Get the path to the SQLite database."""
    return get_data_dir() / "turbowifi.db"


def get_config_dir() -> Path:
    """Get the standard configuration directory."""
    is_termux = os.path.exists("/data/data/com.termux")
    if is_termux:
        base_dir = Path(os.environ.get("PREFIX", "/data/data/com.termux/files/usr"))
        config_dir = base_dir / "etc" / APP_NAME
    else:
        if os.geteuid() == 0:
            config_dir = Path("/etc") / APP_NAME
        else:
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
            config_dir = Path(xdg_config_home) / APP_NAME

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
