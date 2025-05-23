from abc import abstractmethod
from typing import Any, Generator, TypeVar

TAbstractLogSource = TypeVar("AbstractLogSource")


class AbstractLogSource:
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something
    that relies on Models too early.
    """

    @abstractmethod
    def get_id(self) -> str | int:
        return NotImplemented

    @abstractmethod
    def get_level(self) -> int | None:
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
    def get_unsent_entries(
        cls: type[TAbstractLogSource], chunk_size: int
    ) -> Generator[TAbstractLogSource, None, None]:
        return NotImplemented

    @classmethod
    @abstractmethod
    def clear_sent_entries(
        cls: type[TAbstractLogSource], days_to_keep: int = 30
    ) -> list[str]:
        return NotImplemented
