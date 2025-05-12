from datetime import timedelta
from typing import Any, Generator, List, Optional, Self, Union, override

from django.db import transaction
from django.utils import timezone

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.models import ResilientLogEntry


class ResilientLogSource(AbstractLogSource):
    log: ResilientLogEntry

    def __init__(self, log: ResilientLogEntry):
        self.log = log

    @classmethod
    @transaction.atomic
    def create(cls, level: int, message: Any, context: Any) -> Self:
        entry = ResilientLogEntry.objects.create(
            level=level,
            message=message,
            context=context,
        )

        return cls(entry)

    @override
    def get_id(self) -> Union[str, int]:
        return self.log.id

    @override
    def get_level(self) -> Optional[int]:
        return self.log.level

    @override
    def get_message(self) -> Any:
        return self.log.message

    @override
    def get_context(self) -> Any:
        return self.log.context

    @override
    def is_sent(self) -> bool:
        return self.log.is_sent

    @override
    def mark_sent(self) -> None:
        self.log.is_sent = True
        self.log.save(update_fields=["is_sent"])

    @override
    @classmethod
    @transaction.atomic
    def get_unsent_entries(
        cls, chunk_size: int
    ) -> Generator[
        AbstractLogSource,
        None,
        None,
    ]:
        entries = (
            ResilientLogEntry.objects.filter(is_sent=False)
            .order_by("created_at")
            .iterator(chunk_size=chunk_size)
        )

        for entry in entries:
            yield ResilientLogSource(entry)

    @override
    @classmethod
    @transaction.atomic
    def clear_sent_entries(cls, days_to_keep: int = 30) -> List[str]:
        entries = ResilientLogEntry.objects.filter(
            is_sent=True,
            created_at__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return deleted_ids
