from abc import ABC, abstractmethod

from resilient_logger.sources import AbstractLogSource


class AbstractLogTarget(ABC):
    @abstractmethod
    def is_required(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def submit(self, entry: AbstractLogSource.Entry) -> bool:
        raise NotImplementedError()
