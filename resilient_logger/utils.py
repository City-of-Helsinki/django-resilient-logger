import hashlib
import json
import logging
from collections.abc import Callable, Sequence
from functools import cache
from importlib import import_module
from typing import Any, TypedDict, TypeVar, cast

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from resilient_logger.errors.missing_context_error import MissingContextError


class ResilientLoggerConfig(TypedDict):
    origin: str
    environment: str
    batch_limit: int
    chunk_size: int
    submit_unsent_entries: bool
    clear_sent_entries: bool
    sources: list[dict[str, Any]]
    targets: list[dict[str, Any]]


def _non_empty_string(input: str) -> bool:
    return bool(input.strip())


def _non_empty_list(input: list) -> bool:
    return len(input) > 0


_required_fields: tuple[tuple[str, type[Any], Callable[[Any], bool] | None], ...] = (
    ("environment", str, _non_empty_string),
    ("origin", str, _non_empty_string),
    ("sources", list, _non_empty_list),
    ("targets", list, _non_empty_list),
)

_default_config: ResilientLoggerConfig = {
    "batch_limit": 5000,
    "chunk_size": 500,
    "clear_sent_entries": True,
    "submit_unsent_entries": True,
}

BUILTIN_LOG_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "taskName",
    "thread",
    "threadName",
}

TClass = TypeVar("TClass")


def dynamic_class(type: type[TClass], class_path: str) -> type[TClass]:
    """
    Loads dynamically class of given type from class_path
    and ensures it's sub-class of given input type.
    """
    parts = class_path.split(".")
    class_name = parts.pop()
    module_name = ".".join(parts)
    module = import_module(module_name)
    cls = getattr(module, class_name)

    if not issubclass(cls, type):
        raise TypeError(f"Class '{class_path}' is not sub-class of the {type}.")

    return cls


def get_log_record_extra(record: logging.LogRecord):
    """Returns `extra` passed to the logger."""
    return {
        name: record.__dict__[name]
        for name in record.__dict__
        if name not in BUILTIN_LOG_RECORD_ATTRS
    }


def assert_required_extras(extra: dict[str, Any], required_fields: list[str]) -> None:
    missing_fields = [field for field in required_fields if extra.get(field) is None]
    if missing_fields:
        raise MissingContextError(missing_fields)


@cache
def get_resilient_logger_config() -> ResilientLoggerConfig:
    raw_config: ResilientLoggerConfig | None = getattr(
        settings, "RESILIENT_LOGGER", None
    )

    if raw_config is None:
        raise RuntimeError("RESILIENT_LOGGER setting is missing")

    if not isinstance(raw_config, dict):
        raise RuntimeError("RESILIENT_LOGGER is not a proper dictionary")

    config = {**_default_config, **raw_config}

    for key, expected_type, validator in _required_fields:
        if key not in config:
            raise RuntimeError(f"RESILIENT_LOGGER is missing required key: '{key}'")

        value = config[key]

        if not isinstance(value, expected_type):
            actual_type = type(value).__name__
            raise RuntimeError(
                f"RESILIENT_LOGGER['{key}'] must be {expected_type.__name__}, "
                f"got {actual_type}"
            )

        if validator and not validator(value):
            raise RuntimeError(f"RESILIENT_LOGGER['{key}'] failed validation")

    return cast(ResilientLoggerConfig, config)


def content_hash(contents: dict[str, Any]) -> str:
    json_repr = json.dumps(contents, sort_keys=True, cls=DjangoJSONEncoder)
    return hashlib.sha256(json_repr.encode()).hexdigest()


def unavailable_class(name: str, dependencies: Sequence[str]):
    """
    Creates a placeholder class that raises ImportError on instantiation.

    Parameters:
        name (str): Name of the class (for nicer repr).
        dependency (str): The missing dependency to mention in the error.
    """
    deps = ", ".join(f"'{d}'" for d in dependencies)

    class _UnavailableClass:
        def __init__(self, *args, **kwargs):
            raise ImportError(f"{name} requires the optional dependencies: {deps}. ")

        def __repr__(self):
            return f"<Unavailable class {name} (missing dependencies: {deps})>"

    _UnavailableClass.__name__ = name
    return _UnavailableClass


def value_as_dict(value: str | dict) -> dict:
    if isinstance(value, str):
        return {"value": value}

    if isinstance(value, dict):
        return value

    value_type = type(value).__name__

    raise TypeError(
        f"Invalid value_as_dict input. Expected 'str | dict', got '{value_type}'"
    )
