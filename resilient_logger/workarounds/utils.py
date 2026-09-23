from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import smart_str
from django.utils.module_loading import import_string

from resilient_logger.workarounds.types import ObjectReprFn


def safe_object_repr(input: Any):
    """
    Safely builds a string representation without invoking input.__str__().
    Formats as 'ModelName (pk)'.
    """
    if isinstance(input, models.Model):
        model_name = input._meta.object_name
        pk_val = input.pk

        return f"{model_name} ({pk_val})"

    return smart_str(input)


def resolve_object_repr_fn() -> ObjectReprFn:
    setting_name = "RESILIENT_LOGGER_DJANGO_AUDITLOG_REPR_FN"
    object_repr = getattr(settings, setting_name, None)

    if not object_repr:
        return safe_object_repr

    if isinstance(object_repr, str):
        try:
            resolved = import_string(object_repr)
        except (ImportError, AttributeError) as e:
            raise ImproperlyConfigured(
                f"{setting_name} setting points to invalid target '{object_repr}'"
            ) from e
    elif callable(object_repr):
        resolved = object_repr
    else:
        type_name = type(object_repr).__name__
        raise ImproperlyConfigured(
            f"{setting_name} must be a dotted string path or callable, got {type_name}."
        )

    if not callable(resolved):
        raise ImproperlyConfigured(
            f"{setting_name} resolved target '{object_repr}' is not callable."
        )

    return resolved
