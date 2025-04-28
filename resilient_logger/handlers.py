import logging
from functools import cached_property

from resilient_logger.abstract_submitter import AbstractSubmitter
from resilient_logger.submitter_factory import SubmitterFactory
from resilient_logger.utils import get_log_record_extra

logger = logging.getLogger(__name__)

class ResilientLogHandler(logging.Handler):
    def __init__(self, level: int = logging.NOTSET):
        super().__init__(level)

    def emit(self, record: logging.LogRecord):
        self.submitter.submit(
            record.levelno,
            record.getMessage(),
            get_log_record_extra(record)
        )

    @cached_property
    def submitter(self) -> AbstractSubmitter:
        """
        Submitter rely on Django's DB models and cannot be instantiated during
        init since Django app registry is not ready by then.

        To work around this by doing lazy initialization when the submitter
        is used first time.
        """
        return SubmitterFactory.create()

