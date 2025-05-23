import pytest
from auditlog.models import LogEntry
from django.test import override_settings

from resilient_logger.django_audit_log_source import DjangoAuditLogSource
from tests.models import DummyModel
from tests.testdata.testconfig import VALID_CONFIG_ALL_FIELDS


def create_models(count: int) -> list[DummyModel]:
    results: list[DummyModel] = []

    for i in range(count):
        results.append(DummyModel.objects.create(message=str(i)))

    return results


def model_to_auditlog_source(model: DummyModel) -> DjangoAuditLogSource:
    entry = LogEntry.objects.get(object_pk=model.id)
    assert entry is not None
    return DjangoAuditLogSource(entry)


@pytest.mark.django_db
def test_mark_sent():
    [model] = create_models(1)

    source = model_to_auditlog_source(model)
    assert not source.is_sent()

    source.mark_sent()
    assert source.is_sent()


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_get_unsent_entries():
    num_models = 3
    models = create_models(num_models)

    all_log_entries = LogEntry.objects.filter()
    assert len(all_log_entries) == num_models

    for log_entry in all_log_entries:
        assert not log_entry.additional_data

    actual_entries = list(map(model_to_auditlog_source, models))
    unsent_entries = list(DjangoAuditLogSource.get_unsent_entries(500))

    assert len(actual_entries) == len(unsent_entries)

    for i in range(num_models):
        assert actual_entries[i].get_id() == unsent_entries[i].get_id()
        assert actual_entries[i].get_context() == unsent_entries[i].get_context()
        assert actual_entries[i].get_level() == unsent_entries[i].get_level()
        assert actual_entries[i].get_message() == unsent_entries[i].get_message()
        actual_entries[i].mark_sent()

    unsent_entries = list(DjangoAuditLogSource.get_unsent_entries(500))
    assert len(unsent_entries) == 0

    for log_entry in all_log_entries:
        log_entry.refresh_from_db()
        assert log_entry.additional_data["is_sent"]


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_clear_sent_entries():
    num_models = 3
    models = create_models(num_models)
    actual_entries = list(map(model_to_auditlog_source, models))

    for actual_entry in actual_entries:
        actual_entry.mark_sent()

    actual_ids = list(map(lambda entry: entry.get_id(), actual_entries))
    cleaned_ids = DjangoAuditLogSource.clear_sent_entries(0)

    assert len(actual_ids) == num_models
    assert len(cleaned_ids) == num_models

    for cleaned_id in cleaned_ids:
        assert cleaned_id in actual_ids

    cleaned_ids = DjangoAuditLogSource.clear_sent_entries(0)
    assert len(cleaned_ids) == 0
