from auditlog.registry import auditlog
from django.db import models
from django.utils.translation import gettext_lazy as _


class DummyModel(models.Model):
    message = models.JSONField(verbose_name=_("message"))

    class Meta:
        verbose_name = _("dummy model")
        verbose_name_plural = _("dummy models")


auditlog.register(DummyModel)


class M2MChild(models.Model):
    message = models.JSONField(verbose_name=_("message"))

    class Meta:
        verbose_name = _("m2m child")
        verbose_name_plural = _("m2m child")


auditlog.register(M2MChild)


class M2MParent(models.Model):
    message = models.JSONField(verbose_name=_("message"))
    children = models.ManyToManyField(M2MChild, verbose_name=_("children"))

    class Meta:
        verbose_name = _("m2m parent")
        verbose_name_plural = _("m2m parent")


auditlog.register(M2MParent, m2m_fields={"children"})


class M2OParent(models.Model):
    message = models.JSONField(verbose_name=_("message"))

    class Meta:
        verbose_name = _("m2o parent")
        verbose_name_plural = _("m2o parent")


auditlog.register(M2OParent)


class M2OChild(models.Model):
    message = models.JSONField(verbose_name=_("message"))
    parent = models.ForeignKey(M2OParent, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("m2o child")
        verbose_name_plural = _("m2o child")


auditlog.register(M2OChild)
