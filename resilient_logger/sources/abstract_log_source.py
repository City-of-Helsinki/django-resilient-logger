from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterator, Optional, TypedDict, TypeVar, Union

AuditLogEvent = TypedDict(
    "AuditLogEvent",
    {
        "actor": str,
        "date_time": datetime,
        "operation": str,
        "origin": str,
        "target": str,
        "environment": str,
        "message": str,
        "level": Optional[int],
        "extra": Optional[dict],
    },
)

AuditLogDocument = TypedDict(
    "AuditLogDocument",
    {
        "@timestamp": str,
        "audit_event": AuditLogEvent,
    },
)

TAbstractLogSource = TypeVar("TAbstractLogSource", bound="AbstractLogSource")


class AbstractLogSource(ABC):
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something
    that relies on Models too early.
    """

    @abstractmethod
    def get_id(self) -> Union[str, int]:
        raise NotImplementedError()

    @abstractmethod
    def get_document(self) -> AuditLogDocument:
        raise NotImplementedError()

    @abstractmethod
    def is_sent(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def mark_sent(self) -> None:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def get_unsent_entries(
        cls: type[TAbstractLogSource], chunk_size: int
    ) -> Iterator[TAbstractLogSource]:
        """
        Queries and returns iterator for unsent log entries.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def clear_sent_entries(cls, days_to_keep: int = 30) -> list[str]:
        """
        Clears the old entries that are older than days_to_keep days
        and returns the list of the cleared object ids.
        """
        raise NotImplementedError()
