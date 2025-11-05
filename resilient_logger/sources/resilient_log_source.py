import datetime
from collections.abc import Iterator
from typing import Any, TypeVar

from django.db import transaction
from django.utils import timezone

from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import AbstractLogSource
from resilient_logger.sources.abstract_log_source import AuditLogDocument
from resilient_logger.utils import get_resilient_logger_config, value_as_dict

TResilientLogSource = TypeVar("TResilientLogSource", bound="ResilientLogSource")


class ResilientLogSource(AbstractLogSource):
    def __init__(self, log: ResilientLogEntry):
        self.log = log

    @classmethod
    def create(
        cls: type[TResilientLogSource], *, level: int, message: Any, context: dict
    ) -> TResilientLogSource:
        entry = ResilientLogEntry.objects.create(
            level=level,
            message=message,
            context=context,
        )

        return cls(entry)

    @classmethod
    def create_structured(
        cls: type[TResilientLogSource],
        *,
        message: Any,
        level: int = 0,
        operation: str = "MANUAL",
        actor: dict | None = None,
        target: dict | None = None,
        extra: dict | None = None,
    ) -> TResilientLogSource:
        return cls.create(
            level=level,
            message=message,
            context={
                **(extra or {}),
                "actor": actor or {},
                "operation": operation,
                "target": target or {},
            },
        )

    def get_id(self) -> str | int:
        return self.log.id

    def get_document(self) -> AuditLogDocument:
        config = get_resilient_logger_config()
        context = (self.log.context or {}).copy()
        actor = context.pop("actor", "unknown")
        operation = context.pop("operation", "MANUAL")
        target = context.pop("target", "unknown")
        iso_date = (
            self.log.created_at.astimezone(datetime.timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )

        extra = {
            **context,
            "source_pk": self.get_id(),
        }

        return {
            "@timestamp": iso_date,
            "audit_event": {
                "actor": value_as_dict(actor),
                "date_time": iso_date,
                "operation": operation,
                "origin": config["origin"],
                "target": value_as_dict(target),
                "environment": config["environment"],
                "message": self.log.message,
                "level": self.log.level,
                "extra": extra,
            },
        }

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
            created_at__lte=(timezone.now() - datetime.timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return [str(deleted_id) for deleted_id in deleted_ids]
