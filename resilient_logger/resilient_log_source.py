from datetime import timedelta
from typing import Any, Generator

from django.db import transaction
from django.utils import timezone

from resilient_logger.abstract_log_source import AbstractLogSource, TAbstractLogSource
from resilient_logger.models import ResilientLogEntry


class ResilientLogSource(AbstractLogSource):
    log: ResilientLogEntry

    def __init__(self, log: ResilientLogEntry):
        self.log = log

    @classmethod
    @transaction.atomic
    def create(
        cls: TAbstractLogSource, level: int, message: Any, context: Any
    ) -> TAbstractLogSource:
        entry = ResilientLogEntry.objects.create(
            level=level,
            message=message,
            context=context,
        )

        return cls(entry)

    def get_id(self) -> str | int:
        return self.log.id

    def get_level(self) -> int | None:
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
    def get_unsent_entries(
        cls: TAbstractLogSource, chunk_size: int
    ) -> Generator[
        TAbstractLogSource,
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

    @classmethod
    @transaction.atomic
    def clear_sent_entries(
        cls: TAbstractLogSource, days_to_keep: int = 30
    ) -> list[str]:
        entries = ResilientLogEntry.objects.filter(
            is_sent=True,
            created_at__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return deleted_ids
