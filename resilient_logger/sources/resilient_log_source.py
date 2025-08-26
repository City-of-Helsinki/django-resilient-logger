from datetime import timedelta
from typing import Any, Iterator, Optional, TypeVar, Union

from django.db import transaction
from django.utils import timezone

from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import AbstractLogSource

TResilientLogSource = TypeVar("TResilientLogSource", bound="ResilientLogSource")


class ResilientLogSource(AbstractLogSource):
    log: ResilientLogEntry

    def __init__(self, log: ResilientLogEntry):
        self.log = log

    @classmethod
    def create(
        cls: type[TResilientLogSource], level: int, message: Any, context: Any
    ) -> TResilientLogSource:
        entry = ResilientLogEntry.objects.create(
            level=level,
            message=message,
            context=context,
        )

        return cls(entry)

    def get_id(self) -> Union[str, int]:
        return self.log.id

    def get_level(self) -> Optional[int]:
        return self.log.level

    def get_message(self) -> Any:
        return self.log.message

    def get_context(self) -> Any:
        return self.log.context

    def is_sent(self) -> bool:
        return self.log.is_sent

    def mark_sent(self) -> None:
        self.log.is_sent = True
        self.log.save(update_fields=["is_sent"])

    @classmethod
    @transaction.atomic
    def get_unsent_entries(cls, chunk_size: int) -> Iterator["ResilientLogSource"]:
        entries = (
            ResilientLogEntry.objects.filter(is_sent=False)
            .order_by("created_at")
            .iterator(chunk_size=chunk_size)
        )

        for entry in entries:
            yield cls(entry)

    @classmethod
    @transaction.atomic
    def clear_sent_entries(cls, days_to_keep: int = 30) -> list[str]:
        entries = ResilientLogEntry.objects.filter(
            is_sent=True,
            created_at__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return [str(deleted_id) for deleted_id in deleted_ids]
