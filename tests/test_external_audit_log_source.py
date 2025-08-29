import logging
from datetime import datetime

import pytest

from resilient_logger.models.external_audit_log_entry import (
    ExternalAuditLogEntry,
)
from resilient_logger.models.resilient_log_entry import (
    ResilientLogEntry,
)
from resilient_logger.sources import ExternalAuditLogSource
from resilient_logger.utils import get_resilient_logger_config

table_name = ResilientLogEntry._meta.db_table
fake_date_time = datetime(2025, 1, 1, 0, 0, 0)


@pytest.fixture(autouse=True)
def setup():
    get_resilient_logger_config.cache_clear()


def create_objects(count: int) -> list[ResilientLogEntry]:
    results: list[ResilientLogEntry] = []

    for i in range(count):
        results.append(
            ResilientLogEntry.objects.create(
                message={"msg": str(i), "date_time": str(fake_date_time)}
            )
        )

    return results


def object_to_auditlog_source(model: ResilientLogEntry) -> ExternalAuditLogSource:
    entry = ExternalAuditLogEntry.objects.get(id=model.id)
    return ExternalAuditLogSource(entry)


@pytest.mark.django_db
def test_mark_sent():
    [object] = create_objects(1)

    source = object_to_auditlog_source(object)
    assert not source.is_sent()

    message = source.get_message()
    assert message["@timestamp"] == str(fake_date_time)

    source.mark_sent()
    assert source.is_sent()


@pytest.mark.django_db
def test_get_unsent_entries():
    num_objects = 3
    objects = create_objects(num_objects)

    all_log_entries = ExternalAuditLogEntry.objects.filter()
    assert len(all_log_entries) == num_objects

    for log_entry in all_log_entries:
        assert not log_entry.is_sent

    actual_entries = [object_to_auditlog_source(obj) for obj in objects]
    unsent_entries = list(ExternalAuditLogSource.get_unsent_entries(500))

    assert len(actual_entries) == len(unsent_entries)

    for i in range(num_objects):
        assert actual_entries[i].get_id() == unsent_entries[i].get_id()
        assert actual_entries[i].get_message() == unsent_entries[i].get_message()
        actual_entries[i].mark_sent()

    unsent_entries = list(ExternalAuditLogSource.get_unsent_entries(500))
    assert len(unsent_entries) == 0

    for log_entry in all_log_entries:
        log_entry.refresh_from_db()
        assert log_entry.is_sent


@pytest.mark.django_db
def test_clear_sent_entries():
    logger = logging.getLogger(__name__)
    logger.error(ResilientLogEntry._meta.db_table)

    num_objects = 3
    objects = create_objects(num_objects)
    actual_entries = [object_to_auditlog_source(obj) for obj in objects]

    for actual_entry in actual_entries:
        actual_entry.mark_sent()

    actual_ids = [str(entry.get_id()) for entry in actual_entries]
    cleaned_ids = ExternalAuditLogSource.clear_sent_entries(0)

    assert len(actual_ids) == num_objects
    assert len(cleaned_ids) == num_objects

    for cleaned_id in cleaned_ids:
        assert cleaned_id in actual_ids

    cleaned_ids = ExternalAuditLogSource.clear_sent_entries(0)
    assert len(cleaned_ids) == 0
