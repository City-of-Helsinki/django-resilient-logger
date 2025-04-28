import logging

from django_extensions.management.jobs import QuarterHourlyJob

from resilient_logger.abstract_submitter import AbstractSubmitter
from resilient_logger.submitter_factory import SubmitterFactory
from resilient_logger.utils import get_resilient_logger_config

logger = logging.getLogger(__name__)


class Job(QuarterHourlyJob):
    help = (
        "Send django-resilient-logger entries to "
        "centralized log center every 15 minutes"
    )

    should_submit: bool
    submitter: AbstractSubmitter

    def __init__(self):
        settings = get_resilient_logger_config()
        self.should_submit = settings["jobs"]["submit_unsent_entries"] or False
        self.submitter = SubmitterFactory.create()

    def execute(self):
        if self.should_submit:
            logger.info("Begin submit_unsent_entries job.")
            self.submitter.submit_unsent_entries()
            logger.info("Finished submit_unsent_entries done.")
        else:
            logger.info("Skipping submit_unsent_entries, disabled in config")
