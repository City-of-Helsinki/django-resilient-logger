from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypedDict


class AuditLogEvent(TypedDict):
    actor: dict
    date_time: datetime
    operation: str
    origin: str
    target: dict
    environment: str
    message: str
    level: int | None
    extra: dict | None


AuditLogDocument = TypedDict(
    "AuditLogDocument",
    {
        "@timestamp": str,
        "audit_event": AuditLogEvent,
    },
)


class AbstractLogSourceEntry(ABC):
    """Represents a single log entry contract."""

    @abstractmethod
    def get_id(self) -> str | int:
        """Retrieve the unique identifier for the log entry."""
        raise NotImplementedError()

    @abstractmethod
    def get_document(self) -> AuditLogDocument:
        """Serialize the entry into a document format."""
        raise NotImplementedError()

    @abstractmethod
    def is_sent(self) -> bool:
        """Check if the entry has already been processed."""
        raise NotImplementedError()

    @abstractmethod
    def mark_sent(self) -> None:
        """Update the entry state to 'sent' in the persistent store."""
        raise NotImplementedError()
