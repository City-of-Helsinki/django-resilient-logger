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
        """
        Helper method to create a new log entry. This method automatically populates
        some fields when no explicit value is given.

        :param instance: The model instance to log a change for.
        :type instance: Model
        :param force_log: Create a LogEntry even if no changes exist.
        :type force_log: bool
        :param kwargs: Field overrides for the :py:class:`LogEntry` object.
        :return: The new log entry or `None` if there were no changes.
        :rtype: LogEntry
        """
        with self._custom_repr_fn():
            return super().log_create(instance, force_log, **kwargs)

    def log_m2m_changes(
        self, changed_queryset, instance, operation, field_name, **kwargs
    ):
        """Create a new "changed" log entry from m2m record.

        :param changed_queryset: The added or removed related objects.
        :type changed_queryset: QuerySet
        :param instance: The model instance to log a change for.
        :type instance: Model
        :param operation: "add" or "delete".
        :type action: str
        :param field_name: The name of the changed m2m field.
        :type field_name: str
        :param kwargs: Field overrides for the :py:class:`LogEntry` object.
        :return: The new log entry or `None` if there were no changes.
        :rtype: LogEntry
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
