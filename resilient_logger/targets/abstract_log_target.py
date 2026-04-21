from abc import ABC, abstractmethod

from resilient_logger.sources.abstract_log_source_entry import AbstractLogSourceEntry


class AbstractLogTarget(ABC):
    @abstractmethod
    def is_required(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def submit(self, entry: AbstractLogSourceEntry) -> bool:
        raise NotImplementedError()
