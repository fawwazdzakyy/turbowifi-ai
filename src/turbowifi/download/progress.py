"""
Progress reporting using Rich.
"""

from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    TextColumn,
)


class DownloadProgress:
    def __init__(self):
        self.progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )
        self.tasks = {}

    def start(self):
        self.progress.start()

    def stop(self):
        self.progress.stop()

    def add_task(self, name: str, total: int) -> int:
        task_id = self.progress.add_task(name, total=total)
        self.tasks[name] = task_id
        return task_id

    def update(self, name: str, advance: int):
        task_id = self.tasks.get(name)
        if task_id is not None:
            self.progress.update(task_id, advance=advance)

    def update_absolute(self, name: str, completed: int):
        task_id = self.tasks.get(name)
        if task_id is not None:
            self.progress.update(task_id, completed=completed)
