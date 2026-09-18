from typing import Any

from django.db import models
from django.utils.encoding import smart_str


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
