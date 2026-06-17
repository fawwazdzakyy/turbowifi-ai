"""
Daemon lifecycle manager.
"""

import os
import signal
import subprocess
from pathlib import Path

from turbowifi.config.settings import get_db_path


class DaemonManager:
    def __init__(self):
        self.pid_file = Path(get_db_path()).parent / "turbowifi.pid"
        self.log_file = Path(get_db_path()).parent / "daemon.log"

    def get_pid(self) -> int | None:
        try:
            if self.pid_file.exists():
                pid = int(self.pid_file.read_text().strip())
                # Check if process is actually running
                os.kill(pid, 0)
                return pid
        except (ValueError, OSError):
            pass
        return None

    def start(self) -> bool:
        if self.get_pid() is not None:
            return False

        # Start process in background
        cmd = ["turbowifi", "daemon", "run-foreground"]

        # We use Popen with creationflags or preexec_fn depending on OS,
        # but a simple setsid works for unix
        try:
            with open(self.log_file, "a") as f:
                process = subprocess.Popen(cmd, stdout=f, stderr=f, start_new_session=True)
            self.pid_file.write_text(str(process.pid))
            return True
        except Exception:
            return False

    def stop(self) -> bool:
        pid = self.get_pid()
        if not pid:
            return False

        try:
            os.kill(pid, signal.SIGTERM)
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True
        except OSError:
            return False
