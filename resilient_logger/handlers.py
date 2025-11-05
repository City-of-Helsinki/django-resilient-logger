import logging

from resilient_logger.utils import assert_required_extras, get_log_record_extra

logger = logging.getLogger(__name__)


class ResilientLogHandler(logging.Handler):
    def __init__(
        self,
        level: int = logging.NOTSET,
        required_fields: list[str] | None = None,
    ):
        super().__init__(level)
        self.required_fields = required_fields or []

    def emit(self, record: logging.LogRecord):
        """
        ResilientLoggerSource rely on Django's DB models and cannot be imported during
        init since Django app registry is not ready by then.

        To work around this, import it here when the logger is used first time.
        """
        from resilient_logger.sources import ResilientLogSource

        extra = get_log_record_extra(record)
        assert_required_extras(extra, self.required_fields)

        return ResilientLogSource.create(
            level=record.levelno, message=record.getMessage(), context=extra
        )
