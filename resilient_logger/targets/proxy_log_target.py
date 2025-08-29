import logging

from resilient_logger.sources import AbstractLogSource
from resilient_logger.targets import AbstractLogTarget
from resilient_logger.utils import create_target_document


class ProxyLogTarget(AbstractLogTarget):
    """
    Logger target that sends the resilient log entries to another logger.
    """

    def __init__(self, name: str = __name__) -> None:
        self._logger = logging.getLogger(name)

    def submit(self, entry: AbstractLogSource) -> bool:
        level = entry.get_level() or logging.INFO
        message = entry.get_message()
        document = create_target_document(entry)

        self._logger.log(level, message, extra=document)
        return True
