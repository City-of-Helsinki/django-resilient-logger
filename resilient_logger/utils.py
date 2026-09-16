import datetime
import hashlib
import json
import logging
import uuid
from collections.abc import Callable, Sequence
from functools import cache
from importlib import import_module
from typing import Any, TypedDict, TypeVar, cast

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.module_loading import import_string

from resilient_logger.errors.missing_context_error import MissingContextError

# Type alias for clarity across the codebase
ActorResolverCallable = Callable[[Any], dict]
ActorResolverConfig = str | ActorResolverCallable | None


class ResilientLoggerConfig(TypedDict):
    origin: str
    environment: str
    batch_limit: int
    chunk_size: int
    submit_unsent_entries: bool
    clear_sent_entries: bool
    sources: list[dict[str, Any]]
    targets: list[dict[str, Any]]
    # Raw config value (fn, dotted string, or field name)
    actor_resolver: ActorResolverConfig
    # Pre-compiled callable cached in memory
    _actor_resolver_fn: ActorResolverCallable | None


def _non_empty_string(input: str) -> bool:
    return bool(input.strip())


def _non_empty_list(input: list) -> bool:
    return len(input) > 0


def _normalize_actor(actor: Any) -> dict:
    """Ensures actor output is always wrapped in a dictionary."""
    if isinstance(actor, dict):
        return actor

    return {"value": actor}


_required_fields: tuple[tuple[str, type[Any], Callable[[Any], bool] | None], ...] = (
    ("environment", str, _non_empty_string),
    ("origin", str, _non_empty_string),
    ("sources", list, _non_empty_list),
    ("targets", list, _non_empty_list),
)

_default_config: ResilientLoggerConfig = {
    "batch_limit": 5000,
    "chunk_size": 500,
    "clear_sent_entries": False,
    "submit_unsent_entries": False,
    "actor_resolver": None,
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
            expected_type = expected_type.__name__
            raise RuntimeError(
                f"RESILIENT_LOGGER['{key}'] must be {expected_type}, got {actual_type}"
            )

        if validator and not validator(value):
            raise RuntimeError(f"RESILIENT_LOGGER['{key}'] failed validation")

    # Resolve raw config (fn/string/field) into a pre-compiled function once at startup
    config["_actor_resolver_fn"] = parse_actor_resolver(config.get("actor_resolver"))

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


def parse_uuid(value: str | None) -> uuid.UUID | None:
    if not value:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return None


def parse_actor_resolver(target: Any) -> ActorResolverCallable | None:
    """
    Resolves an actor extraction setting into a single callable returning a dict.

    Supported formats:
    - None: Return None (use per class default instead)
    - Callable: Direct execution (wrapped if it returns non-dict)
    - Import path string: Imported at runtime via import_string (wrapped if non-dict)
    - Field name string: Direct attribute lookup (wrapped via _normalize_actor)
    """
    if target is None:
        return None

    if callable(target):
        return lambda user: _normalize_actor(target(user))

    if isinstance(target, str):
        try:
            resolved_fn = import_string(target)

            if callable(resolved_fn):
                return lambda user: _normalize_actor(resolved_fn(user))

        except (ImportError, ValueError):

            def _field_getter(user: Any) -> dict:
                if user is None:
                    return _normalize_actor(None)

                if isinstance(user, dict):
                    val = user.get(target)
                else:
                    val = getattr(user, target, None)

                    if callable(val):
                        val = val()

                return _normalize_actor(val)

            return _field_getter

    raise TypeError(f"Invalid actor_extractor configuration type: {type(target)}")


def format_audit_time(time: datetime.datetime) -> str:
    return (
        time.astimezone(datetime.timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )
