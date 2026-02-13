from collections.abc import Iterator
from datetime import timedelta

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

    def get_id(self) -> str | int:
        return self.log.id

    def get_document(self) -> AuditLogDocument:
        config = get_resilient_logger_config()
        actor: AbstractUser | None = self.log.actor

        # Looks up the action tuple [int, str] and uses name of it
        action = LogEntry.Action.choices[self.log.action][1]
        additional_data = (self.log.additional_data or {}).copy()

        # Remove is_sent variable from additional_data, it's only for local tracking
        additional_data.pop("is_sent", None)

        extra = {
            **additional_data,
            "changes": self.log.changes,
            "source_pk": self.get_id(),
        }

        return {
            "@timestamp": self.log.timestamp,
            "audit_event": {
                "actor": self._parse_actor(actor),
                "date_time": self.log.timestamp,
                "operation": str(action).upper(),
                "origin": config["origin"],
                "target": {
                    "value": self.log.object_repr,
                },
                "environment": config["environment"],
                "message": self._parse_changes(self.log),
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

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return [str(deleted_id) for deleted_id in deleted_ids]

    @classmethod
    def _parse_actor(cls, raw_actor: AbstractUser | None) -> dict:
        if raw_actor:
            return {"name": raw_actor.get_full_name(), "email": raw_actor.email}

        return {"name": None, "email": None}

    @classmethod
    def _parse_changes(cls, log: LogEntry) -> str:
        try:
            return log.changes_str
        except TypeError:
            return cls._changes_str_fallback(log.changes_dict)

    @classmethod
    def _changes_str_fallback(
        cls, changes_dict: dict, colon=": ", arrow=" \u2192 ", separator="; "
    ) -> str:
        """
        Reconstruction of django-auditlog's LogEntry.changes_str that does not enforce
        old and new value formats as string.
        """
        substrings = []

        for field, value in sorted(changes_dict.items()):
            if isinstance(value, (list, tuple)) and len(value) == 2:
                # handle regular field change
                substrings.append(f"{field:s}{colon:s}{value[0]}{arrow:s}{value[1]}")
            elif isinstance(value, dict) and value.get("type") == "m2m":
                # handle m2m change
                substrings.append(
                    f"{field}{colon}{value['operation']} {sorted(value['objects'])}"
                )

        return separator.join(substrings)
