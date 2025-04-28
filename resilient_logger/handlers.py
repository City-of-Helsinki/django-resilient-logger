import logging
from collections.abc import Callable
from functools import cached_property
from typing import Dict, Optional

from resilient_logger.abstract_log_facade import AbstractLogFacade
from resilient_logger.abstract_submitter import AbstractSubmitter
from resilient_logger.utils import dynamic_class, get_log_record_extra

logger = logging.getLogger(__name__)

class ResilientLogHandler(logging.Handler):
    _submitter_construct: Optional[Callable[[], AbstractSubmitter]]

    def __init__(self, submitter: Dict, log_facade: Dict, level: int = logging.NOTSET):
        super().__init__(level)

        def submitter_construct():
            """
            Submitter rely on Django's DB models and cannot be instantiated during
            init since Django app registry is not ready by then.

            To work around this by doing lazy initialization when the submitter
            is used first time.
            """

            submitter_args = submitter.copy()
            submitter_class = submitter_args.pop('class')

            log_facade_args = log_facade.copy()
            log_facade_class = log_facade_args.pop('class')

            submitter_class = dynamic_class(AbstractSubmitter, submitter_class)
            log_facade_class = dynamic_class(AbstractLogFacade, log_facade_class)

            instance = submitter_class(**submitter_args, log_facade=log_facade_class)
            return instance

        self._submitter_construct = submitter_construct

    def emit(self, record: logging.LogRecord):
        self._submitter.submit(
            record.levelno,
            record.getMessage(),
            get_log_record_extra(record)
        )

    @cached_property
    def _submitter(self) -> AbstractSubmitter:
        if self._submitter_construct is None:
            raise Exception("Unable to proceed without lazy constructor")

        instance = self._submitter_construct()
        self._submitter_construct = None
        return instance

