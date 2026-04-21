from abc import ABC, abstractmethod
from collections.abc import Iterator

from resilient_logger.sources.abstract_log_source_entry import AbstractLogSourceEntry


class AbstractLogSource(ABC):
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something
    that relies on Models too early.
    """

    @abstractmethod
    def get_unsent_entries(self, chunk_size: int) -> Iterator["AbstractLogSourceEntry"]:
        """
        Queries and returns iterator for unsent log entries.
        """
        raise NotImplementedError()

    @abstractmethod
    def clear_sent_entries(self, days_to_keep: int = 30) -> list[str]:
        """
        Clears the old entries that are older than days_to_keep days
        and returns the list of the cleared object ids.
        """
        raise NotImplementedError()
