import importlib
from unittest.mock import patch

import pytest
from auditlog.models import LogEntry
from django.test import override_settings

from resilient_logger.sources import DjangoAuditLogSource
from tests.models import DummyModel
from tests.testdata.testconfig import VALID_CONFIG_ALL_FIELDS


def create_objects(count: int) -> list[DummyModel]:
    results: list[DummyModel] = []

    for i in range(count):
        results.append(DummyModel.objects.create(message=str(i)))

    return results


def object_to_auditlog_source(model: DummyModel) -> DjangoAuditLogSource:
    entry = LogEntry.objects.get(object_pk=model.id)
    return DjangoAuditLogSource(entry)


@pytest.mark.django_db
def test_mark_sent():
    [object] = create_objects(1)

    source = object_to_auditlog_source(object)
    assert not source.is_sent()

    source.mark_sent()
    assert source.is_sent()


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_get_unsent_entries():
    num_objects = 3
    objects = create_objects(num_objects)

    all_log_entries = LogEntry.objects.filter()
    assert len(all_log_entries) == num_objects

    for log_entry in all_log_entries:
        assert not log_entry.additional_data

    actual_entries = [object_to_auditlog_source(obj) for obj in objects]
    unsent_entries = list(DjangoAuditLogSource.get_unsent_entries(500))

    assert len(actual_entries) == len(unsent_entries)

    for i in range(num_objects):
        assert actual_entries[i].get_id() == unsent_entries[i].get_id()
        assert actual_entries[i].get_document() == unsent_entries[i].get_document()
        actual_entries[i].mark_sent()

    unsent_entries = list(DjangoAuditLogSource.get_unsent_entries(500))
    assert len(unsent_entries) == 0

    for log_entry in all_log_entries:
        log_entry.refresh_from_db()
        assert log_entry.additional_data["is_sent"]


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_clear_sent_entries():
    num_objects = 3
    objects = create_objects(num_objects)
    actual_entries = [object_to_auditlog_source(obj) for obj in objects]

    for actual_entry in actual_entries:
        actual_entry.mark_sent()

    actual_ids = [str(entry.get_id()) for entry in actual_entries]
    cleaned_ids = DjangoAuditLogSource.clear_sent_entries(0)

    assert len(actual_ids) == num_objects
    assert len(cleaned_ids) == num_objects

    for cleaned_id in cleaned_ids:
        assert cleaned_id in actual_ids

    cleaned_ids = DjangoAuditLogSource.clear_sent_entries(0)
    assert len(cleaned_ids) == 0


def test_optional_django_audit_log():
    with patch.dict(
        "sys.modules", {"resilient_logger.sources.django_audit_log_source": None}
    ):
        import resilient_logger.sources as sources

        importlib.reload(sources)

        with pytest.raises(ImportError):
            sources.DjangoAuditLogSource()
