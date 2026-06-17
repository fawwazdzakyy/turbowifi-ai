"""
Resume logic and state persistence.
"""

import json
from pathlib import Path
from typing import List

from turbowifi.download.segment import Segment


class ResumeManager:
    def __init__(self, target_file: str):
        self.target_file = Path(target_file)
        self.state_file = Path(f"{target_file}.turbodownload")

    def save_state(self, url: str, segments: List[Segment]):
        state = {
            "url": url,
            "segments": [
                {
                    "index": s.index,
                    "start_byte": s.start_byte,
                    "end_byte": s.end_byte,
                    "downloaded": s.downloaded,
                    "status": s.status,
                }
                for s in segments
            ],
        }
        self.state_file.write_text(json.dumps(state, indent=2))

    def load_state(self) -> tuple[str, List[Segment]] | None:
        if not self.state_file.exists():
            return None

        try:
            data = json.loads(self.state_file.read_text())
            url = data["url"]
            segments = []
            for s in data["segments"]:
                segments.append(
                    Segment(
                        index=s["index"],
                        start_byte=s["start_byte"],
                        end_byte=s["end_byte"],
                        downloaded=s["downloaded"],
                        status=s["status"],
                    )
                )
            return url, segments
        except Exception:
            return None

    def cleanup(self):
        if self.state_file.exists():
            self.state_file.unlink()
