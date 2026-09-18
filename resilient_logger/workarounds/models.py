from contextlib import contextmanager

import auditlog.models
from auditlog.models import LogEntry, LogEntryManager

from resilient_logger.workarounds.utils import safe_object_repr


class DjangoAuditLogEntryManager(LogEntryManager):
    def log_create(self, instance, force_log: bool = False, **kwargs):
        with self._custom_repr_fn():
            return super().log_create(instance, force_log, **kwargs)

    def log_m2m_changes(
        self, changed_queryset, instance, operation, field_name, **kwargs
    ):
        with self._custom_repr_fn():
            return super().log_m2m_changes(
                changed_queryset, instance, operation, field_name, **kwargs
            )

    @contextmanager
    def _custom_repr_fn(self):
        original_smart_str = auditlog.models.smart_str
        auditlog.models.smart_str = safe_object_repr

        try:
            yield
        finally:
            auditlog.models.smart_str = original_smart_str

    @staticmethod
    def patch():
        """Extractable helper intended for AppConfig.ready() or test setup."""
        original_objects = LogEntry.objects
        original_base = LogEntry._meta.base_manager
        original_default = LogEntry._meta.default_manager

        manager = DjangoAuditLogEntryManager()
        manager.model = LogEntry

        LogEntry.objects = manager
        LogEntry._meta.base_manager = manager
        LogEntry._meta.default_manager = manager

        def restore():
            LogEntry.objects = original_objects
            LogEntry._meta.base_manager = original_base
            LogEntry._meta.default_manager = original_default

        return restore
