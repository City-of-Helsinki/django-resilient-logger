from collections.abc import Iterator
from datetime import datetime
from typing import Protocol, TypedDict, runtime_checkable


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


@runtime_checkable
class AbstractLogSource(Protocol):
    """
    Abstract base class (interface) that defines the method signatures.
    This is required because Django will not work if we import something
    that relies on Models too early.
    """

    @runtime_checkable
    class Entry(Protocol):
        """Represents a single log entry contract."""

        def get_id(self) -> str | int:
            """Retrieve the unique identifier for the log entry."""
            ...

        def get_document(self) -> AuditLogDocument:
            """Serialize the entry into a document format."""
            ...

        def is_sent(self) -> bool:
            """Check if the entry has already been processed."""
            ...

        def mark_sent(self) -> None:
            """Update the entry state to 'sent' in the persistent store."""
            ...

    def get_unsent_entries(
        self, chunk_size: int
    ) -> Iterator["AbstractLogSource.Entry"]:
        """
        Queries and returns iterator for unsent log entries.
        """
        ...

    def clear_sent_entries(self, days_to_keep: int = 30) -> list[str]:
        """
        Clears the old entries that are older than days_to_keep days
        and returns the list of the cleared object ids.
        """
        ...
