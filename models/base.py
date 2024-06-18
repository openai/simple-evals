from abc import ABC, abstractmethod

from typings import MessageList

class SamplerBase(ABC):
    @abstractmethod
    def __call__(self, message_list: MessageList) -> str:
        raise NotImplementedError
