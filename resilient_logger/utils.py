from importlib import import_module
import logging
from typing import Type, TypeVar

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