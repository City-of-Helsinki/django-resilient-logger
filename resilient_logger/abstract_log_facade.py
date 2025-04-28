from abc import abstractmethod
from typing import Any, Generator, Self, Union

class AbstractLogFacade:
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something that relies on Models too early.
    """
    @abstractmethod
    def get_id(self) -> Union[str, int]:
        return NotImplemented
    
    @abstractmethod
    def get_level(self) -> int:
        return NotImplemented

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
    def create(cls, level: int, message: Any, context: Any) -> Self:
        return NotImplemented
    
    @classmethod
    @abstractmethod
    def get_unsent_entries(cls, chunk_size: int) -> Generator[Self, None, None]:
        return NotImplemented

    @classmethod
    @abstractmethod
    def clear_sent_entries(cls, days_to_keep: int = 30) -> None:
        return NotImplemented