import logging

from django.core.management.base import BaseCommand, CommandError

from resilient_logger.resilient_logger import ResilientLogger
from resilient_logger.utils import get_resilient_logger_config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Clear django-resilient-logger entries which are already submitted,"
        "only clear if settings.CLEAR_SENT_ENTRIES is set to True (default: False)"
    )

    def __init__(self):
        settings = get_resilient_logger_config()
        self.should_clear = settings["clear_sent_entries"] or False
        self.resilient_logger = ResilientLogger.create()

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-to-keep",
            action="store",
            dest="days_to_keep",
            type=int,
            default=30,
            help="Days to keep the old values stored",
        )

    def handle(self, *args, **options):
        days_to_keep = options.get("days_to_keep", 30)

        if not self.should_clear:
            raise CommandError("clear_sent_entries is disabled in config")

        logger.info("Begin clear_sent_entries job")
        result = self.resilient_logger.clear_sent_entries(days_to_keep)
        logger.info("Finished clear_sent_entries job done", extra={"result": result})
