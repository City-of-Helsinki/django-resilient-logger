import logging

import pytest
from django.core.management import call_command
from django.test import override_settings

from resilient_logger.sources import ResilientLogSource
from tests.testdata.testconfig import VALID_CONFIG_ALL_FIELDS

logger = logging.getLogger(__name__)


def extract_result(record: logging.LogRecord):
    # Can change, but for now the command stored the result in extra["result"]
    return record.__dict__["result"]


def create_resilient_log_entries(count: int, mark_sent: bool):
    for idx in range(count):
        entry = ResilientLogSource.create_structured(
            message="Hello world", extra={"index": idx}
        )

        if mark_sent:
            entry.mark_sent()


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_submit_unsent_entries(caplog: pytest.LogCaptureFixture):
    logger_name = "resilient_logger.management.commands.submit_unsent_entries"
    num_log_entries = 10
    create_resilient_log_entries(num_log_entries, False)

    with caplog.at_level(logging.INFO, logger=logger_name):
        call_command("submit_unsent_entries")
        result = extract_result(caplog.records[1])
        assert len(result) == num_log_entries
        caplog.clear()

    with caplog.at_level(logging.INFO, logger=logger_name):
        call_command("submit_unsent_entries")
        result = extract_result(caplog.records[1])
        assert len(result) == 0
        caplog.clear()


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_clear_sent_entries(caplog: pytest.LogCaptureFixture):
    logger_name = "resilient_logger.management.commands.clear_sent_entries"
    num_log_entries = 10
    create_resilient_log_entries(num_log_entries, True)

    with caplog.at_level(logging.INFO, logger=logger_name):
        call_command("clear_sent_entries", days_to_keep=0)
        result = extract_result(caplog.records[1])
        assert len(result) == num_log_entries
        caplog.clear()

    with caplog.at_level(logging.INFO, logger=logger_name):
        call_command("clear_sent_entries", days_to_keep=0)
        result = extract_result(caplog.records[1])
        assert len(result) == 0
        caplog.clear()
