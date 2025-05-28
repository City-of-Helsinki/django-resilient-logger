from datetime import timedelta
from typing import Any, Iterator, Optional, Union

from auditlog.models import LogEntry
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.utils import timezone

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.utils import get_resilient_logger_config


class DjangoAuditLogSource(AbstractLogSource):
    log: LogEntry

    def __init__(self, log: LogEntry):
        self.log = log

    def get_id(self) -> Union[str, int]:
        return self.log.object_pk

    def get_level(self) -> Optional[int]:
        return None

    def get_message(self) -> Any:
        return self.log.changes_str

    def get_context(self) -> Any:
        config = get_resilient_logger_config()
        actor: Optional[AbstractUser] = self.log.actor

        return {
            "@timestamp": self.log.timestamp,
            "audit_event": {
                "actor": "unknown"
                if actor is None
                else actor.get_full_name() or str(actor.email),
                "date_time": self.log.timestamp,
                "operation": str(self.log.action),
                "origin": config["origin"],
                "target": self.log.object_repr,
                "environment": config["environment"],
                "message": self.log.changes,
            },
        }

    def is_sent(self) -> bool:
        if self.log.additional_data is None:
            return False

        if isinstance(self.log.additional_data, dict):
            return self.log.additional_data.get("is_sent", False)

        return False

    def mark_sent(self) -> None:
        if self.log.additional_data is None:
            self.log.additional_data = {}

        self.log.additional_data["is_sent"] = True
        self.log.save(update_fields=["additional_data"])

    @classmethod
    def get_unsent_entries(cls, chunk_size: int) -> Iterator["DjangoAuditLogSource"]:
        entries = (
            LogEntry.objects.select_related("actor")
            .filter(
                (
                    ~Q(additional_data__has_key="is_sent")  # support old entries
                    | Q(additional_data__is_sent=False)
                ),
            )
            .select_for_update(of=("self",))
            .order_by("timestamp")
            .iterator(chunk_size=chunk_size)
        )

        for entry in entries:
            yield cls(entry)

    @classmethod
    def clear_sent_entries(cls, days_to_keep: int = 30) -> list[str]:
        entries = LogEntry.objects.filter(
            ~Q(additional_data__has_key="is_sent")  # support old entries
            | Q(additional_data__is_sent=True),
            timestamp__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("object_pk", flat=True))
        entries.delete()

        return deleted_ids
