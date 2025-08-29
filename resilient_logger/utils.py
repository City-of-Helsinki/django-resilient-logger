import hashlib
import json
import logging
from functools import cache
from importlib import import_module
from typing import Any, Optional, TypedDict, TypeVar

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from resilient_logger.errors import MissingContextError


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


def get_resilient_logger_source_config(class_name: str) -> dict:
    config = get_resilient_logger_config()

    for source in config["sources"]:
        source_class = source.get("class", None)

        if class_name_matches(class_name, source_class):
            return source

    raise RuntimeError(f"Unable to find source definition for class {class_name}")


def class_name_matches(actual_name: str, expected_name: str) -> bool:
    """
    Checks if the class name matches to absolute path
    or path without the filename attached.

    E.g. following values will be considered the same:
     - resilient_logger.sources.custom_audit_log_source.CustomAuditLogSource
     - resilient_logger.sources.CustomAuditLogSource
    """
    if actual_name == expected_name:
        return True

    actual_parts = actual_name.split(".")
    path_without_filename = ".".join(actual_parts[:-2] + [actual_parts[-1]])
    return path_without_filename == expected_name


def parse_class_path(model_class: type[models.Model]) -> str:
    return f"{model_class.__module__}.{model_class.__qualname__}"


def content_hash(contents: dict[str, Any]) -> str:
    json_repr = json.dumps(contents, sort_keys=True, cls=DjangoJSONEncoder)
    return hashlib.sha256(json_repr.encode()).hexdigest()


def create_target_document(
    entry: models.Model, fallback_level=logging.INFO
) -> dict[str, Any]:
    from resilient_logger.sources import AbstractLogSource

    if not isinstance(entry, AbstractLogSource):
        raise RuntimeError("entry is not based on AbstractLogSource")

    message = entry.get_message()
    document = entry.get_context() or {}
    log_level = entry.get_level() or fallback_level

    document["entry_id"] = entry.get_id()

    if message is not None:
        document["log_message"] = message

    if log_level is not None:
        document["log_level"] = log_level

    return document
