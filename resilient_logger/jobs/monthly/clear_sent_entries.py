import logging

from django_extensions.management.jobs import MonthlyJob

from resilient_logger.abstract_submitter import AbstractSubmitter
from resilient_logger.submitter_factory import SubmitterFactory
from resilient_logger.utils import get_resilient_logger_config

logger = logging.getLogger(__name__)

class Job(MonthlyJob):
    help = (
        "Clear django-resilient-logger entries which is already submitter,"
        "only clear if settings.CLEAR_SENT_ENTRIES is set to True (default: False)"
    )

    should_clear: bool
    submitter: AbstractSubmitter

    def __init__(self):
        settings = get_resilient_logger_config()
        self.should_clear = settings["jobs"]["clear_sent_entries"] or False
        self.submitter = SubmitterFactory.create()

    def execute(self):
        if self.should_clear:
            logger.info("Begin clear_sent_entries job")
            self.submitter.clear_sent_entries()
            logger.info("Finished clear_sent_entries job done")
        else:
            logger.info("Skipping clear_sent_entries, disabled in config")
