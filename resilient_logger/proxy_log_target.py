import logging
import uuid

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.abstract_log_target import AbstractLogTarget


class ProxyLogTarget(AbstractLogTarget):
    """
    Logger target that sends the resilient log entries to another logger.
    """

    _logger: logging.Logger

    def __init__(self, name: str = __name__) -> None:
        self._logger = logging.getLogger(name)

    def submit(self, entry: AbstractLogSource) -> str | None:
        level = entry.get_level() or logging.INFO
        message = entry.get_message()
        context = entry.get_context() or {}

        self._logger.log(level, message, extra=context)
        return str(uuid.uuid4())
