from abc import ABC, abstractmethod
from typing import Any, Optional

class IAgent(ABC):
    @abstractmethod
    async def run(self) -> Any:
        pass

    @abstractmethod
    def final_result(self) -> str:
        pass

class IBrowser(ABC):
    @abstractmethod
    async def kill(self):
        pass
