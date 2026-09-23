from django.apps import AppConfig
from django.conf import settings


class ResilientLoggerConfig(AppConfig):
    default = True
    default_auto_field = "django.db.models.BigAutoField"
    name = "resilient_logger"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._restore_fn = None

    def ready(self):
        self.restore()

        if getattr(settings, "RESILIENT_LOGGER_PATCH_DJANGO_AUDITLOG", False):
            from resilient_logger.workarounds.models import DjangoAuditLogEntryManager

            self._restore_fn = DjangoAuditLogEntryManager.patch()

    def restore(self):
        """Restores original state and clears the callback handle."""
        if callable(self._restore_fn):
            self._restore_fn()
            self._restore_fn = None
