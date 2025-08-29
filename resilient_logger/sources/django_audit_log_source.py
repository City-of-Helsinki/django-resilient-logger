from datetime import timedelta
from typing import Iterator, Optional, Union

from auditlog.models import LogEntry
from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from resilient_logger.sources import AbstractLogSource
from resilient_logger.sources.abstract_log_source import AuditLogDocument
from resilient_logger.utils import get_resilient_logger_config


class DjangoAuditLogSource(AbstractLogSource):
    def __init__(self, log: LogEntry):
        self.log = log

    def get_id(self) -> Union[str, int]:
        return self.log.object_pk

    def get_document(self) -> AuditLogDocument:
        config = get_resilient_logger_config()
        actor: Optional[AbstractUser] = self.log.actor
        # Looks up the action tuple [int, str] and uses name of it
        action = LogEntry.Action.choices[self.log.action][1]
        extra = {
            **self.log.additional_data,
            "changes": self.log.changes,
        }

        return {
            "@timestamp": self.log.timestamp,
            "audit_event": {
                "actor": "unknown"
                if actor is None
                else actor.get_full_name() or str(actor.email),
                "date_time": self.log.timestamp,
                "operation": str(action).upper(),
                "origin": config["origin"],
                "target": self.log.object_repr,
                "environment": config["environment"],
                "message": self.log.changes_str,
                "extra": extra,
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
    @transaction.atomic
    def get_unsent_entries(cls, chunk_size: int) -> Iterator["DjangoAuditLogSource"]:
        entries = (
            LogEntry.objects.select_related("actor")
            .filter(
                (
                    ~Q(additional_data__has_key="is_sent")  # support old entries
                    | Q(additional_data__is_sent=False)
                ),
            )
            .order_by("timestamp")
            .iterator(chunk_size=chunk_size)
        )

        for entry in entries:
            yield cls(entry)

    @classmethod
    @transaction.atomic
    def clear_sent_entries(cls, days_to_keep: int = 30) -> list[str]:
        entries = LogEntry.objects.filter(
            ~Q(additional_data__has_key="is_sent")  # support old entries
            | Q(additional_data__is_sent=True),
            timestamp__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("object_pk", flat=True))
        entries.delete()

        return [str(deleted_id) for deleted_id in deleted_ids]
