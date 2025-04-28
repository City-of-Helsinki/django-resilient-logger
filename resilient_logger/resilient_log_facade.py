from datetime import datetime, timedelta
from typing import Any, Generator, Self, Union, override

from django.db import transaction

from resilient_logger.abstract_log_facade import AbstractLogFacade
from resilient_logger.models import ResilientLogEntry


class ResilientLogFacade(AbstractLogFacade):
    _log: ResilientLogEntry

    def __init__(self, log: ResilientLogEntry):
        self._log = log

    @override
    def get_id(self) -> Union[str, int]:
        return self._log.id

    @override
    def get_level(self) -> int:
        return self._log.level

    @override
    def get_message(self) -> Any:
        return self._log.message

    @override
    def get_context(self) -> Any:
        return self._log.context

    @override
    def is_sent(self) -> bool:
        return self._log.is_sent

    @override
    def mark_sent(self) -> None:
        self._log.is_sent = True
        self._log.save(update_fields=["is_sent"])

    @override
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
    @classmethod
    @transaction.atomic
    def get_unsent_entries(cls, chunk_size: int) -> Generator[
        AbstractLogFacade,
        None,
        None,
    ]:
        entries = (
            ResilientLogEntry
                .objects
                .filter(is_sent=False)
                .order_by("created_at")
                .iterator(chunk_size=chunk_size)
        )

        for entry in entries:
            yield ResilientLogFacade(entry)

    @override
    @classmethod
    @transaction.atomic
    def clear_sent_entries(cls, days_to_keep: int = 30) -> None:
        ResilientLogEntry.objects.filter(
            is_sent=True,
            created_at__lte=(datetime.now() - timedelta(days=days_to_keep)),
        ).select_for_update().delete()
