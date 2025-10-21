import asyncio
from typing import Awaitable

from livekit_voice_call_runner.logger import CallLogger

Task = Awaitable[None]


class ConcurrentTasksRunner:
    """
    Async task runner with concurrency control.
    """

    def __init__(self, logger: CallLogger):
        self._logger = logger

    async def run(self, tasks: list[Task], concurrency: int) -> None:
        semaphore = asyncio.Semaphore(concurrency)

        async def _run_with_semaphore(task: Task) -> None:
            async with semaphore:
                await task

        coroutines = [_run_with_semaphore(task=task) for task in tasks]
        self._logger.info(
            "Running concurrent tasks.",
            extra={"count": len(tasks), "concurrency": concurrency},
        )

        await asyncio.gather(*coroutines, return_exceptions=True)
