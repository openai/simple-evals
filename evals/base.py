from abc import ABC, abstractmethod
from typing import Any, Dict

class EvalBase(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError