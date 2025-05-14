import logging

import pytest
from django.core.management import call_command
from django.test import TestCase, override_settings

from resilient_logger.resilient_log_source import ResilientLogSource
from tests.testdata.testconfig import VALID_CONFIG_ALL_FIELDS

logger = logging.getLogger(__name__)


class TestCommands(TestCase):
    def extract_result(self, record: logging.LogRecord):
        # Can change, but for now the command stored the result in extra["result"]
        return record.__dict__["result"]

    def create_resilient_log_entries(self, count: int, mark_sent: bool):
        for idx in range(count):
            entry = ResilientLogSource.create(
                logging.INFO, "Hello world", {"index": idx}
            )

            if mark_sent:
                entry.mark_sent()

    @pytest.mark.django_db
    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_submit_unsent_entries(self):
        logger_name = "resilient_logger.management.commands.submit_unsent_entries"
        num_log_entries = 10
        self.create_resilient_log_entries(num_log_entries, False)

        with self.assertLogs(logger_name) as cm:
            call_command("submit_unsent_entries")
            result = self.extract_result(cm.records[1])
            self.assertEqual(len(result), num_log_entries)

        with self.assertLogs(logger_name) as cm:
            call_command("submit_unsent_entries")
            result = self.extract_result(cm.records[1])
            self.assertEqual(len(result), 0)

    @pytest.mark.django_db
    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_clear_sent_entries(self):
        logger_name = "resilient_logger.management.commands.clear_sent_entries"
        num_log_entries = 10
        self.create_resilient_log_entries(num_log_entries, True)

        with self.assertLogs(logger_name) as cm:
            call_command("clear_sent_entries", days_to_keep=0)
            result = self.extract_result(cm.records[1])
            self.assertEqual(len(result), num_log_entries)

        with self.assertLogs(logger_name) as cm:
            call_command("clear_sent_entries", days_to_keep=0)
            result = self.extract_result(cm.records[1])
            self.assertEqual(len(result), 0)
