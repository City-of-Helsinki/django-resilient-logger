from abc import abstractmethod
from typing import Any, Generator, List, Optional, Self, Union


class AbstractLogSource:
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something
    that relies on Models too early.
    """

    @abstractmethod
    def get_id(self) -> Union[str, int]:
        return NotImplemented

    @abstractmethod
    def get_level(self) -> Optional[int]:
        return None

    @abstractmethod
    def get_message(self) -> Any:
        return NotImplemented

    @abstractmethod
    def get_context(self) -> Any:
        return NotImplemented

    @abstractmethod
    def is_sent(self) -> bool:
        return NotImplemented

    @abstractmethod
    def mark_sent(self) -> None:
        return NotImplemented

    @classmethod
    @abstractmethod
    def get_unsent_entries(cls, chunk_size: int) -> Generator[Self, None, None]:
        return NotImplemented

    @classmethod
    @abstractmethod
    def clear_sent_entries(cls, days_to_keep: int = 30) -> List[str]:
        return NotImplemented
