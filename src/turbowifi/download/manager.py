"""
Main entry point orchestrating the download.
"""

import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import urlparse

from turbowifi.download.protocol import check_capabilities
from turbowifi.download.segment import create_segments, calculate_optimal_segments
from turbowifi.download.scheduler import DownloadScheduler
from turbowifi.download.resume import ResumeManager
from turbowifi.download.storage import StorageManager
from turbowifi.download.downloader import AsyncDownloader
from turbowifi.download.progress import DownloadProgress
from turbowifi.download.verifier import verify_checksum


class DownloadManager:
    def __init__(self, override_connections: int | None = None):
        self.scheduler = DownloadScheduler(override_connections)
        self.progress = DownloadProgress()

    def _get_filename(self, url: str) -> str:
        parsed = urlparse(url)
        name = Path(parsed.path).name
        return name if name else "downloaded_file"

    async def download(
        self, url: str, output: str | None = None, checksum: str | None = None
    ) -> bool:
        """High-level download API."""
        filename = output if output else self._get_filename(url)

        resume_mgr = ResumeManager(filename)
        storage = StorageManager(filename)

        self.progress.start()
        main_task = self.progress.add_task("[cyan]Probing Server...", total=100)

        try:
            # 1. Probing
            async with aiohttp.ClientSession() as session:
                caps = await check_capabilities(url, session)

            # 2. State Resolution (Resume or Fresh)
            state = resume_mgr.load_state()
            if state and state[0] == url:
                segments = state[1]
                total_length = caps.content_length or sum(
                    s.end_byte - s.start_byte + 1 for s in segments
                )
                self.progress.update_absolute(main_task, completed=0)
                self.progress.progress.update(
                    main_task, description=f"[cyan]Resuming {filename}...", total=total_length
                )

                # Update progress bars for resumed data
                for s in segments:
                    self.progress.update(main_task, advance=s.downloaded)
            else:
                total_length = caps.content_length

                if total_length and caps.supports_ranges:
                    concurrency = self.scheduler.determine_concurrency()
                    num_segs = calculate_optimal_segments(total_length, concurrency)
                    segments = create_segments(total_length, num_segs)

                    storage.allocate(total_length)
                    self.progress.progress.update(
                        main_task,
                        description=f"[cyan]Downloading {filename} ({num_segs} threads)...",
                        total=total_length,
                    )
                else:
                    segments = []  # Single thread fallback
                    self.progress.progress.update(
                        main_task,
                        description=f"[yellow]Single-thread download {filename}...",
                        total=total_length or 100,
                    )

            # 3. Download
            concurrency = self.scheduler.determine_concurrency()
            downloader = AsyncDownloader(url, storage, concurrency)

            # Use an event loop trick to throttle disk updates slightly, but for now exact tracking
            def on_progress(segment):
                self.progress.update(
                    main_task, advance=128 * 1024
                )  # approx chunk size, or better use accurate byte counts

            # Let's fix accurate tracking using a closure state
            last_bytes = {s.index: s.downloaded for s in segments} if segments else {-1: 0}

            def accurate_progress(segment):
                nonlocal last_bytes
                idx = segment.index if hasattr(segment, "index") else -1
                diff = segment.downloaded - last_bytes[idx]
                last_bytes[idx] = segment.downloaded
                self.progress.update(main_task, advance=diff)

            downloader.set_progress_callback(accurate_progress)

            if segments:
                # Save state initially
                resume_mgr.save_state(url, segments)

                # Start background save loop
                async def state_saver():
                    while True:
                        await asyncio.sleep(2.0)
                        resume_mgr.save_state(url, segments)

                saver_task = asyncio.create_task(state_saver())

                await downloader.download_segments(segments)

                saver_task.cancel()
                resume_mgr.cleanup()  # Done!
            else:
                await downloader.download_single_thread()

            self.progress.progress.update(main_task, description="[green]Download Complete!")

        except Exception as e:
            self.progress.progress.update(main_task, description=f"[red]Failed: {str(e)}")
            return False
        finally:
            self.progress.stop()
            storage.close()

        # 4. Verify
        if checksum:
            import rich

            console = rich.console.Console()
            with console.status("[cyan]Verifying checksum..."):
                try:
                    verify_checksum(filename, checksum)
                    console.print("[green]✓ Checksum verified successfully.[/green]")
                except Exception as e:
                    console.print(f"[red]✗ Checksum verification failed: {e}[/red]")
                    return False

        return True
