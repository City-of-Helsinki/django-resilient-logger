from datetime import timedelta
from typing import Any, Iterator, Optional, Union

from django.db import transaction
from django.utils import timezone

from resilient_logger.models import (
    CustomAuditLogEntryModelBase,
    create_custom_audit_log_entry_model,
)
from resilient_logger.sources import AbstractLogSource, AbstractLogSourceFactory


class CustomAuditLogSourceFactory(AbstractLogSourceFactory):
    @staticmethod
    def create(**kwargs) -> type[AbstractLogSource]:
        args = {
            "table_name": kwargs.get("table_name", None),
            "date_time_field": kwargs.get("date_time_field", "date_time"),
        }

        required_fields = ["table_name", "date_time_field"]
        missing_fields: list[str] = []

        for required_field in required_fields:
            if not args[required_field]:
                missing_fields.append(required_field)

        if len(missing_fields) > 0:
            missing_fields_str = ", ".join(missing_fields)

            raise RuntimeError(
                f"create is missing required fields: [{missing_fields_str}]"
            )

        custom_audit_log_entry = create_custom_audit_log_entry_model(args["table_name"])

        class CustomAuditLogSource(AbstractLogSource):
            log: CustomAuditLogEntryModelBase

            def __init__(self, log: CustomAuditLogEntryModelBase):
                self.log = log

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
                field: str = args["date_time_field"]
                path_parts = field.split(".")
                current = self.log

                for path_part in path_parts:
                    current = (
                        current.get(path_part)
                        if isinstance(current, dict)
                        else getattr(current, path_part)
                    )

                return str(current)

            @classmethod
            @transaction.atomic
            def get_unsent_entries(
                cls, chunk_size: int
            ) -> Iterator["CustomAuditLogSource"]:
                entries = (
                    custom_audit_log_entry.objects.filter(is_sent=False)
                    .order_by("created_at")
                    .iterator(chunk_size=chunk_size)
                )

                for entry in entries:
                    yield cls(entry)

            @classmethod
            @transaction.atomic
            def clear_sent_entries(cls, days_to_keep: int = 30) -> list[str]:
                entries = custom_audit_log_entry.objects.filter(
                    is_sent=True,
                    created_at__lte=(timezone.now() - timedelta(days=days_to_keep)),
                ).select_for_update()

                deleted_ids = list(entries.values_list("id", flat=True))
                entries.delete()

                return [str(deleted_id) for deleted_id in deleted_ids]

        return CustomAuditLogSource
