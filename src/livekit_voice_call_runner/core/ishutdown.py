import asyncio
from abc import ABC, abstractmethod
from typing import Any


class IShutdown(ABC):
    @abstractmethod
    async def shutdown(self) -> None: ...


class ShutdownEvent(asyncio.Event):
    def __init__(self):
        super().__init__()

    def do_set(self, reason: dict[str, Any]):
        super().set()
        self._reason = reason

    async def do_wait(self) -> dict[str, Any]:
        await super().wait()
        return self._reason
