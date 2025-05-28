import hashlib
import json
import logging
from functools import cache
from importlib import import_module
from typing import Any, Optional, TypedDict, TypeVar

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.missing_context_error import MissingContextError


class ResilientLoggerConfig(TypedDict):
    origin: str
    environment: str
    batch_limit: int
    chunk_size: int
    submit_unsent_entries: bool
    clear_sent_entries: bool
    sources: list[dict[str, Any]]
    targets: list[dict[str, Any]]


_default_config: ResilientLoggerConfig = {
    "origin": "",
    "environment": "",
    "batch_limit": 5000,
    "chunk_size": 500,
    "clear_sent_entries": True,
    "submit_unsent_entries": True,
    "sources": [],
    "targets": [],
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
    config: Optional[ResilientLoggerConfig] = getattr(
        settings, "RESILIENT_LOGGER", None
    )

    if not config:
        raise RuntimeError("RESILIENT_LOGGER setting is missing")

    if not isinstance(config, dict):
        raise RuntimeError("RESILIENT_LOGGER is not proper dictionary")

    if not isinstance(config.get("sources", None), list):
        raise RuntimeError("RESILIENT_LOGGER['sources'] is not instance of list")

    if not isinstance(config.get("targets", None), list):
        raise RuntimeError("RESILIENT_LOGGER['targets'] is not instance of list")

    for key, default_value in _default_config.items():
        # Add default values to jobs section if it skipped some.
        config.setdefault(key, default_value)  # type: ignore

    return config


def content_hash(contents: dict[str, Any]) -> str:
    json_repr = json.dumps(contents, sort_keys=True, cls=DjangoJSONEncoder)
    return hashlib.sha256(json_repr.encode()).hexdigest()


def create_target_document(
    entry: AbstractLogSource, fallback_level=logging.INFO
) -> dict[str, Any]:
    message = entry.get_message()
    document = entry.get_context() or {}
    log_level = entry.get_level() or fallback_level

    document["entry_id"] = entry.get_id()

    if message is not None:
        document["log_message"] = message

    if log_level is not None:
        document["log_level"] = log_level

    return document
