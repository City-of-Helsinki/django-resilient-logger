from functools import cache

from django.db import models
from django.utils.translation import gettext_lazy as _

from resilient_logger.utils import get_resilient_logger_source_config


@cache
def parse_table_name() -> str:
    class_name = "resilient_logger.sources.CustomAuditLogSource"
    table_name = "table_name_missing"

    try:
        config = get_resilient_logger_source_config(class_name)
        table_name = config.get("table_name", table_name)
    except Exception:
        pass

    return table_name


class CustomAuditLogEntryModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        managed = False
        db_table = parse_table_name()
        verbose_name = _("custom audit log entry")
        verbose_name_plural = _("custom audit log entries")

    def save(self, *args, **kwargs):
        if self._state.adding:
            raise ValueError("Creation of new records is not allowed.")
        return super().save(*args, **kwargs)
