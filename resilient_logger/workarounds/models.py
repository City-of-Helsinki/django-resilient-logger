from contextlib import contextmanager

import auditlog.models
from auditlog.models import LogEntry, LogEntryManager

from resilient_logger.workarounds.types import ObjectReprFn
from resilient_logger.workarounds.utils import resolve_object_repr_fn


class DjangoAuditLogEntryManager(LogEntryManager):
    def __init__(self, object_repr_fn: ObjectReprFn):
        self._object_repr_fn = object_repr_fn
        self._original_smart_str = auditlog.models.smart_str
        super().__init__()

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
        auditlog.models.smart_str = self._object_repr_fn

        try:
            yield
        finally:
            auditlog.models.smart_str = self._original_smart_str

    @staticmethod
    def patch(object_repr_fn: ObjectReprFn | None = None):
        """Extractable helper intended for AppConfig.ready() or test setup."""
        original_objects = LogEntry.objects
        original_base = LogEntry._meta.base_manager
        original_default = LogEntry._meta.default_manager

        manager = DjangoAuditLogEntryManager(object_repr_fn or resolve_object_repr_fn())
        manager.model = LogEntry

        LogEntry.objects = manager
        LogEntry._meta.base_manager = manager
        LogEntry._meta.default_manager = manager

        def restore():
            LogEntry.objects = original_objects
            LogEntry._meta.base_manager = original_base
            LogEntry._meta.default_manager = original_default

        return restore
