from dataclasses import dataclass
from typing import Any

from django.contrib.auth.models import AbstractUser

from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources.abstract_log_source_entry import (
    AbstractLogSourceEntry,
    AuditLogDocument,
)
from resilient_logger.utils import (
    format_audit_time,
    get_resilient_logger_config,
    value_as_dict,
)


@dataclass
class ResilientLogEntryData:
    level: int
    message: Any
    context: dict


@dataclass
class StructuredResilientLogEntryData:
    message: Any
    level: int = 0
    operation: str = "MANUAL"
    actor: dict | None = None
    target: dict | None = None
    extra: dict | None = None


class ResilientLogSourceEntry(AbstractLogSourceEntry):
    def __init__(self, log: ResilientLogEntry):
        self.log = log

    def get_id(self) -> str | int:
        return self.log.id

    def get_document(self) -> AuditLogDocument:
        config = get_resilient_logger_config()
        context = (self.log.context or {}).copy()
        actor = context.pop("actor", value_as_dict("unknown"))
        operation = context.pop("operation", "MANUAL")
        target = context.pop("target", value_as_dict("unknown"))
        iso_date = format_audit_time(self.log.created_at)

        extra = {
            **context,
            "source_pk": self.get_id(),
        }

        resolve_actor = config["_actor_resolver_fn"] or self._resolve_default_actor

        return {
            "@timestamp": iso_date,
            "audit_event": {
                "actor": resolve_actor(actor),
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

    def _resolve_default_actor(self, actor: AbstractUser | None) -> dict:
        return actor
