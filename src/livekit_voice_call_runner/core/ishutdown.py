from abc import ABC, abstractmethod


class IShutdown(ABC):
    @abstractmethod
    async def shutdown(self) -> None: ...
