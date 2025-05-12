import logging
import uuid
from typing import Optional, override

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.abstract_log_target import AbstractLogTarget


class ProxyLogTarget(AbstractLogTarget):
    """
    Logger target that sends the resilient log entries to another logger.
    """

    _logger: logging.Logger

    def __init__(self, name: str = __name__) -> None:
        self._logger = logging.getLogger(name)

    @override
    def submit(self, entry: AbstractLogSource) -> Optional[str]:
        self._logger.log(
            entry.get_level(), entry.get_message(), extra=entry.get_context() or {}
        )

        return str(uuid.uuid4())
