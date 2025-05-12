import logging
from typing import List

from resilient_logger.utils import get_log_record_extra, assert_required_extras

logger = logging.getLogger(__name__)


class ResilientLogHandler(logging.Handler):
    required_fields: List[str]

    def __init__(self, level: int = logging.NOTSET, required_fields: List[str] = []):
        super().__init__(level)
        self.required_fields = required_fields

    def emit(self, record: logging.LogRecord):
        """
        ResilientLoggerSource rely on Django's DB models and cannot be imported during
        init since Django app registry is not ready by then.

        To work around this, import it here when the logger is used first time.
        """
        from resilient_logger.resilient_log_source import ResilientLogSource

        extra = get_log_record_extra(record)
        assert_required_extras(extra, self.required_fields)

        return ResilientLogSource.create(
            level=record.levelno, message=record.getMessage(), context=extra
        )
