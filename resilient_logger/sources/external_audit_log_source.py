from datetime import timedelta
from functools import cache
from typing import Any, Iterator, Optional, Union

from django.db import transaction
from django.utils import timezone

from resilient_logger.models.external_audit_log_entry import ExternalAuditLogEntry
from resilient_logger.sources.abstract_log_source import AbstractLogSource
from resilient_logger.utils import get_resilient_logger_source_config, parse_class_path


class ExternalAuditLogSource(AbstractLogSource):
    date_path_parts: list[str]

    def __init__(self, log: ExternalAuditLogEntry):
        self._initialize()
        self.log = log

    @classmethod
    @cache
    def _initialize(cls) -> None:
        source_name = parse_class_path(cls)
        config = get_resilient_logger_source_config(source_name)

        table_name: str = config.get("table_name", None)
        date_time_field: str = config.get("date_time_field", None)

        if not table_name:
            raise RuntimeError(
                f"table_name is not found from {source_name} source definition"
            )

        if not date_time_field:
            raise RuntimeError(
                f"date_time_field is not found from {source_name} source definition"
            )

        cls.date_path_parts = date_time_field.split(".")

    def get_id(self) -> Union[str, int]:
        return self.log.id

    def get_level(self) -> Optional[int]:
        return None

    def get_message(self) -> Any:
        message = self.log.message.copy()
        message["@timestamp"] = self._parse_timestamp()

        return message

    def get_context(self) -> Any:
        return None

    def is_sent(self) -> bool:
        return self.log.is_sent

    def mark_sent(self) -> None:
        self.log.is_sent = True
        self.log.save(update_fields=["is_sent"])

    def _parse_timestamp(self) -> str:
        current = self.log

        for path_part in self.date_path_parts:
            current = (
                current.get(path_part)
                if isinstance(current, dict)
                else getattr(current, path_part)
            )

        return str(current)

    @classmethod
    @transaction.atomic
    def get_unsent_entries(cls, chunk_size: int) -> Iterator["ExternalAuditLogSource"]:
        entries = (
            ExternalAuditLogEntry.objects.filter(is_sent=False)
            .order_by("created_at")
            .iterator(chunk_size=chunk_size)
        )

        for entry in entries:
            yield cls(entry)

    @classmethod
    @transaction.atomic
    def clear_sent_entries(cls, days_to_keep: int = 30) -> list[str]:
        entries = ExternalAuditLogEntry.objects.filter(
            is_sent=True,
            created_at__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return [str(deleted_id) for deleted_id in deleted_ids]
