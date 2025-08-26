import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class CustomAuditLogEntryModelBase(models.Model):
    id = models.BigAutoField(primary_key=True)
    is_sent = models.BooleanField(default=False, verbose_name=_("is sent"))
    message = models.JSONField(verbose_name=_("message"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self._state.adding:
            raise ValueError("Creation of new records is not allowed.")
        return super().save(*args, **kwargs)


_model_cache: dict[str, CustomAuditLogEntryModelBase] = {}


def create_custom_audit_log_entry_model(
    table_name: str,
) -> CustomAuditLogEntryModelBase:
    if table_name in _model_cache:
        return _model_cache[table_name]

    # Need to do this the hard way to avoid Django's model registry conflicts.
    # See: https://www.w3schools.com/python/ref_func_type.asp

    model_class = type(
        f"CustomAuditLogEntryModel_{table_name}",
        (CustomAuditLogEntryModelBase,),
        {
            "__module__": __name__,
            "Meta": type("Meta", (), {"db_table": table_name, "managed": False}),
        },
    )

    _model_cache[table_name] = model_class
    return model_class
