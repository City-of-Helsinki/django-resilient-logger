import typing

from resilient_logger.utils import unavailable_class

from .abstract_log_source import AbstractLogSource as AbstractLogSource
from .resilient_log_source import ResilientLogSource as ResilientLogSource

if typing.TYPE_CHECKING:
    from .django_audit_log_source import DjangoAuditLogSource as DjangoAuditLogSource
else:
    try:
        from .django_audit_log_source import (
            DjangoAuditLogSource as DjangoAuditLogSource,
        )
    except ImportError:
        DjangoAuditLogSource = unavailable_class(
            "DjangoAuditLogSource", ["django-auditlog"]
        )
