from abc import ABC, abstractmethod
from typing import Any

class LLMClient(ABC):
    @abstractmethod
    def call(self, *args, **kwargs) -> Any:
        pass