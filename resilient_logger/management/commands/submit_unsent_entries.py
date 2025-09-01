import logging

from django.core.management.base import BaseCommand, CommandError

from resilient_logger.resilient_logger import ResilientLogger
from resilient_logger.utils import get_resilient_logger_config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send django-resilient-logger entries to centralized log center"

    def __init__(self):
        settings = get_resilient_logger_config()
        self.should_submit = settings["submit_unsent_entries"] or False
        self.resilient_logger = ResilientLogger.create()

    def handle(self, *args, **options):
        if not self.should_submit:
            raise CommandError("submit_unsent_entries is disabled in config")

        logger.info("Begin submit_unsent_entries job.")
        result = self.resilient_logger.submit_unsent_entries()
        logger.info("Finished submit_unsent_entries done.", extra={"result": result})
