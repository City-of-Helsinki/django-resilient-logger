from django.db import models
from django.utils.translation import gettext_lazy as _


class ResilientLogEntry(models.Model):
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    level = models.IntegerField(verbose_name=_("level"), default=0)
    message = models.JSONField(verbose_name=_("message"))
    context = models.JSONField(verbose_name=_("context"), null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created at"), db_index=True
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = _("resilient log entry")
        verbose_name_plural = _("resilient log entries")
