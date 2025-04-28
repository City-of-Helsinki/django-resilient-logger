import logging
from importlib import import_module
from typing import Any, Dict, Type, TypedDict, TypeVar

from django.conf import settings


class ResilientLoggerJobsConfig(TypedDict):
  submit_unsent_entries: bool
  clear_sent_entries: bool

class ResilientLoggerConfig(TypedDict):
  submitter: Dict[str, Any]
  log_facade: Dict[str, Any]
  jobs: ResilientLoggerJobsConfig

_default_jobs_config: ResilientLoggerJobsConfig = {
    'clear_sent_entries': True,
    'submit_unsent_entries': True,
}

BUILTIN_LOG_RECORD_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'taskName',
    'thread',
    'threadName',
}

RESILIENT_LOGGER_CONFIG_REQUIRED_KEYS = [
    "submitter",
    "log_facade",
]

TClass = TypeVar("TClass")

def dynamic_class(type: Type[TClass], class_path: str) -> Type[TClass]:
    """
    Loads dynamically class of given type from class_path
    and ensures it's sub-class of given input type.
    """
    parts = class_path.split('.')
    class_name = parts.pop()
    module_name = '.'.join(parts)
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

def get_resilient_logger_config() -> ResilientLoggerConfig:
    config: ResilientLoggerConfig = settings.RESILIENT_LOGGER

    if not config:
        raise Exception("RESILIENT_LOGGER setting is missing")

    if not isinstance(config, Dict):
        raise Exception("RESILIENT_LOGGER is not proper dictionary")

    for key in RESILIENT_LOGGER_CONFIG_REQUIRED_KEYS:
        value = config.get(key, None)

        if not value:
            raise Exception(f"RESILIENT_LOGGER is missing required '{key}' config")

        if not isinstance(value, Dict):
            raise Exception(f"RESILIENT_LOGGER[{key}] is not proper dictionary")

    # Add default values to jobs section if it skipped some.
    config['jobs'] = _default_jobs_config | config.get('jobs', {})

    return config
