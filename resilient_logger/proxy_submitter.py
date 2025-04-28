import logging
import uuid
from typing import Optional, Type, override

from resilient_logger.abstract_log_facade import AbstractLogFacade
from resilient_logger.abstract_submitter import AbstractSubmitter


class ProxySubmitter(AbstractSubmitter):
    """
    Submitter class that sends the resilient log entries to another logger.
    """
    _logger: logging.Logger

    def __init__(self,
            log_facade: Type[AbstractLogFacade],
            name: str = __name__,
            batch_limit: int = 5000,
            chunk_size: int = 500,
    ) -> None:
        super().__init__(log_facade, batch_limit, chunk_size)
        self._logger = logging.getLogger(name)

    @override
    def _submit_entry(self, entry: AbstractLogFacade) -> Optional[str]:
        self._logger.log(
            entry.get_level(),
            entry.get_message(),
            extra=entry.get_context() or {}
        )

        return str(uuid.uuid4())
