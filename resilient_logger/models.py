from django.db import models
from django.utils.translation import gettext_lazy as _


class ResilientLogEntry(models.Model):
    id = models.AutoField(primary_key=True)
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    level = models.IntegerField(verbose_name=_("level"), default=0)
    message = models.JSONField(verbose_name=_("message"))
    context = models.JSONField(verbose_name=_("context"), null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        verbose_name_plural = "resilient log entries"
