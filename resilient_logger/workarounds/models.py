from contextlib import contextmanager
from contextvars import ContextVar

import auditlog.models
from auditlog.models import LogEntry, LogEntryManager

from resilient_logger.workarounds.types import ObjectReprFn
from resilient_logger.workarounds.utils import resolve_object_repr_fn

_object_repr_var: ContextVar[ObjectReprFn | None] = ContextVar(
    "_object_repr_var", default=None
)


class DjangoAuditLogEntryManager(LogEntryManager):
    def __init__(self, object_repr_fn: ObjectReprFn):
        """Use the given callback for object representations in audit entries."""
        self._object_repr_fn = object_repr_fn
        super().__init__()

    def log_create(self, instance, force_log: bool = False, **kwargs):
        """Log an instance using the configured representation callback.

        Return the new entry, or ``None`` when ``changes`` is absent and
        ``force_log`` is false. AuditLog substitutes fallback text if the
        callback raises ``ObjectDoesNotExist`` for the instance; other callback
        and manager errors propagate.
        """
        with self._custom_repr_fn():
            return super().log_create(instance, force_log, **kwargs)

    def log_m2m_changes(
        self, changed_queryset, instance, operation, field_name, **kwargs
    ):
        """Log a many-to-many change using the configured representation callback.

        The callback also represents each changed related object. Return the
        new entry, or ``None`` for an empty ``changed_queryset``. AuditLog
        substitutes fallback text if the callback raises ``ObjectDoesNotExist``
        for the primary instance; other callback and manager errors propagate.
        """
        with self._custom_repr_fn():
            return super().log_m2m_changes(
                changed_queryset, instance, operation, field_name, **kwargs
            )

    @contextmanager
    def _custom_repr_fn(self):
        """Use this manager's callback for the block, then restore the prior one."""
        token = _object_repr_var.set(self._object_repr_fn)

        try:
            yield
        finally:
            _object_repr_var.reset(token)

    @staticmethod
    def patch(object_repr_fn: ObjectReprFn | None = None):
        """Patch AuditLog entry managers and string conversion for entry creation.

        Use ``object_repr_fn`` during ``log_create`` and ``log_m2m_changes``;
        a falsey value selects the configured or default callback instead.
        Return a callable that restores the manager references and conversion
        function captured before this patch. Invalid representation settings
        raise ``ImproperlyConfigured`` when resolving that fallback.
        """
        original_objects = LogEntry.objects
        original_base = LogEntry._meta.base_manager
        original_default = LogEntry._meta.default_manager
        original_smart_str = auditlog.models.smart_str

        def _smart_str_proxy(s):
            """Use the active callback, or the original converter outside one."""
            custom_fn = _object_repr_var.get()

            if custom_fn is not None:
                return custom_fn(s)

            return original_smart_str(s)

        manager = DjangoAuditLogEntryManager(object_repr_fn or resolve_object_repr_fn())
        manager.model = LogEntry

        LogEntry.objects = manager
        LogEntry._meta.base_manager = manager
        LogEntry._meta.default_manager = manager
        auditlog.models.smart_str = _smart_str_proxy

        def restore():
            """Restore the AuditLog managers and converter saved by this patch."""
            LogEntry.objects = original_objects
            LogEntry._meta.base_manager = original_base
            LogEntry._meta.default_manager = original_default
            auditlog.models.smart_str = original_smart_str

        return restore
