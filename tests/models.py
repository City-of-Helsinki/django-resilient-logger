from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _


class DummyModel(models.Model):
    message = models.JSONField(verbose_name=_("message"))

    class Meta:
        verbose_name = _("dummy model")
        verbose_name_plural = _("dummy models")


auditlog.register(DummyModel)
