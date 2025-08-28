from functools import cache

from django.db import models
from django.utils.translation import gettext_lazy as _

from resilient_logger.managers import LazyInitTableManager


class CustomAuditLogEntryModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    objects = LazyInitTableManager["CustomAuditLogEntryModel"]()

    class Meta:
        managed = False
        verbose_name = _("custom audit log entry")
        verbose_name_plural = _("custom audit log entries")

    # Needed for LazyInitTableManager
    _initialized: bool = False

    @classmethod
    @cache
    def init_model(cls) -> None:
        from resilient_logger.sources import CustomAuditLogSource
        from resilient_logger.utils import (
            get_resilient_logger_source_config,
            parse_class_path,
        )

        class_name = parse_class_path(CustomAuditLogSource)
        config = get_resilient_logger_source_config(class_name)
        table_name = config.get("table_name", None)

        if not table_name:
            raise RuntimeError(f"No table name found for {class_name}")

        cls._meta.db_table = table_name
        return True

    def save(self, *args, **kwargs):
        if self._state.adding:
            raise ValueError("Creation of new records is not allowed.")
        return super().save(*args, **kwargs)
