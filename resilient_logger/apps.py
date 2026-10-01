from django.apps import AppConfig
from django.conf import settings


class ResilientLoggerConfig(AppConfig):
    default = True
    default_auto_field = "django.db.models.BigAutoField"
    name = "resilient_logger"

    def __init__(self, *args, **kwargs):
        """Initialize the app with no AuditLog patch to restore."""
        super().__init__(*args, **kwargs)
        self._restore_fn = None

    def ready(self):
        """Apply the AuditLog patch when enabled, replacing any earlier patch.

        Invalid representation settings raise ``ImproperlyConfigured``. If
        enabled without django-auditlog installed, its import error propagates.
        """
        self.restore()

        if getattr(settings, "RESILIENT_LOGGER_PATCH_DJANGO_AUDITLOG", False):
            from resilient_logger.workarounds.models import DjangoAuditLogEntryManager

            self._restore_fn = DjangoAuditLogEntryManager.patch()

    def restore(self):
        """Restores original state and clears the callback handle."""
        if callable(self._restore_fn):
            self._restore_fn()
            self._restore_fn = None
