from collections.abc import Iterator
from datetime import timedelta

from auditlog.models import LogEntry
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from resilient_logger.sources import AbstractLogSource
from resilient_logger.sources.django_audit_log_source_entry import (
    DjangoAuditLogSourceEntry,
)


class DjangoAuditLogSource(AbstractLogSource):
    @transaction.atomic
    def get_unsent_entries(
        self, chunk_size: int
    ) -> Iterator["DjangoAuditLogSourceEntry"]:
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
            yield DjangoAuditLogSourceEntry(entry)

    @transaction.atomic
    def clear_sent_entries(self, days_to_keep: int = 30) -> list[str]:
        entries = LogEntry.objects.filter(
            ~Q(additional_data__has_key="is_sent")  # support old entries
            | Q(additional_data__is_sent=True),
            timestamp__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).select_for_update()

        deleted_ids = list(entries.values_list("id", flat=True))
        entries.delete()

        return [str(deleted_id) for deleted_id in deleted_ids]
