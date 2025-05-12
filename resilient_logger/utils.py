import logging
from importlib import import_module
from typing import Any, Dict, List, Type, TypedDict, TypeVar

from django.conf import settings
from functools import cache

from resilient_logger.missing_context_error import MissingContextError


class ResilientLoggerConfig(TypedDict):
    origin: str
    environment: str
    batch_limit: int
    chunk_size: int
    submit_unsent_entries: bool
    clear_sent_entries: bool
    sources: List[Dict[str, Any]]
    targets: List[Dict[str, Any]]


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


def dynamic_class(type: Type[TClass], class_path: str) -> Type[TClass]:
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
        raise Exception(f"Class '{class_path}' is not sub-class of the {type}.")

    return cls


def get_log_record_extra(record: logging.LogRecord):
    """Returns `extra` passed to the logger."""
    return {
        name: record.__dict__[name]
        for name in record.__dict__
        if name not in BUILTIN_LOG_RECORD_ATTRS
    }


def assert_required_extras(extra: Dict[str, Any], required_fields: List[str]) -> None:
    missing_fields: List[str] = []

    for required_field in required_fields:
        if extra.get(required_field, None) is None:
            missing_fields.append(required_field)

    if missing_fields:
        raise MissingContextError(missing_fields)


@cache
def get_resilient_logger_config() -> ResilientLoggerConfig:
    config: ResilientLoggerConfig = settings.RESILIENT_LOGGER

    if not config:
        raise Exception("RESILIENT_LOGGER setting is missing")

    if not isinstance(config, Dict):
        raise Exception("RESILIENT_LOGGER is not proper dictionary")

    if not isinstance(config["sources"], List):
        raise Exception(f"RESILIENT_LOGGER['sources'] is not instance of list")

    if not isinstance(config["targets"], List):
        raise Exception(f"RESILIENT_LOGGER['targets'] is not instance of list")

    for key, default_value in _default_config.items():
        # Add default values to jobs section if it skipped some.
        config[key] = config.get(key, default_value)

    return config
