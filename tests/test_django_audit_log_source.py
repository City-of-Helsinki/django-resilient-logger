import importlib
from unittest.mock import patch

import pytest
from auditlog.context import set_actor
from auditlog.models import LogEntry
from django.contrib.auth.models import User
from django.test import override_settings

from resilient_logger.sources import DjangoAuditLogSource
from resilient_logger.sources.django_audit_log_source_entry import (
    DjangoAuditLogSourceEntry,
)
from tests.models import DummyModel, M2MChild, M2MParent, M2OChild, M2OParent
from tests.testdata.testconfig import VALID_CONFIG_ALL_FIELDS


@pytest.fixture
def log_source():
    return DjangoAuditLogSource()


def create_objects(count: int) -> list[DummyModel]:
    results: list[DummyModel] = []

    for i in range(count):
        results.append(DummyModel.objects.create(message=str(i)))

    return results


def object_to_auditlog_source(
    obj: DummyModel | M2MParent | M2OChild,
) -> DjangoAuditLogSourceEntry:
    entry = LogEntry.objects.get_for_object(obj).order_by("pk").last()
    return DjangoAuditLogSourceEntry(entry)


@pytest.mark.django_db
def test_mark_sent():
    [object] = create_objects(1)

    source = object_to_auditlog_source(object)
    assert not source.is_sent()

    source.mark_sent()
    assert source.is_sent()


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_get_unsent_entries(log_source):
    num_objects = 3
    objects = create_objects(num_objects)

    all_log_entries = LogEntry.objects.filter()
    assert len(all_log_entries) == num_objects

    for log_entry in all_log_entries:
        assert not log_entry.additional_data

    actual_entries = [object_to_auditlog_source(obj) for obj in objects]
    unsent_entries = list(log_source.get_unsent_entries(500))

    assert len(actual_entries) == len(unsent_entries)

    for i in range(num_objects):
        assert actual_entries[i].get_id() == unsent_entries[i].get_id()
        assert actual_entries[i].get_document() == unsent_entries[i].get_document()
        actual_entries[i].mark_sent()

    unsent_entries = list(log_source.get_unsent_entries(500))
    assert len(unsent_entries) == 0

    for log_entry in all_log_entries:
        log_entry.refresh_from_db()
        assert log_entry.additional_data["is_sent"]


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_clear_sent_entries(log_source):
    num_objects = 3
    objects = create_objects(num_objects)
    actual_entries = [object_to_auditlog_source(obj) for obj in objects]

    for actual_entry in actual_entries:
        actual_entry.mark_sent()

    actual_ids = [str(entry.get_id()) for entry in actual_entries]
    cleaned_ids = log_source.clear_sent_entries(0)

    assert len(actual_ids) == num_objects
    assert len(cleaned_ids) == num_objects

    for cleaned_id in cleaned_ids:
        assert cleaned_id in actual_ids

    cleaned_ids = log_source.clear_sent_entries(0)
    assert len(cleaned_ids) == 0


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_changes_str_fallback():
    [object] = create_objects(1)
    entry = LogEntry.objects.log_create(
        object,
        force_log=True,
        action=LogEntry.Action.UPDATE,
        changes={
            "internal_key": [
                None,
                "NewValue",
            ]
        },
    )

    wrapped = DjangoAuditLogSourceEntry(entry)
    wrapped.get_document()

    assert True


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_m2m():
    parent = M2MParent.objects.create(message="parent")
    children: list[M2MChild] = []

    for i in range(3):
        children.append(M2MChild.objects.create(message=str(i)))

    parent.children.set(children)
    entry = object_to_auditlog_source(parent)
    event = entry.get_document().get("audit_event")

    children_strings = sorted([f"'{str(obj)}'" for obj in children])
    child_list_str = ", ".join(children_strings)
    expected = f"children: add [{child_list_str}]"

    assert expected == event.get("message")


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_m2o():
    arrow = "\u2192"
    parent1 = M2OParent.objects.create(message="parent")
    children = M2OChild.objects.create(message="child", parent=parent1)

    entry1 = object_to_auditlog_source(children)
    event1 = entry1.get_document().get("audit_event")
    expected1 = f"parent: None {arrow} {parent1.id}"
    assert expected1 in event1.get("message")

    parent2 = M2OParent.objects.create(message="parent")
    children.parent = parent2
    children.save()

    entry2 = object_to_auditlog_source(children)
    event2 = entry2.get_document().get("audit_event")
    expected2 = f"parent: {parent1.id} {arrow} {parent2.id}"
    assert expected2 in event2.get("message")


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_actor():
    user = User.objects.create(
        email="admin@localhost", first_name="Test", last_name="User"
    )

    with set_actor(user):
        [object] = create_objects(1)

    entry = object_to_auditlog_source(object)
    event = entry.get_document().get("audit_event")

    assert event.get("actor") == {"email": "admin@localhost", "name": "Test User"}


def test_optional_django_audit_log():
    with patch.dict(
        "sys.modules", {"resilient_logger.sources.django_audit_log_source": None}
    ):
        import resilient_logger.sources as sources

        importlib.reload(sources)

        with pytest.raises(ImportError):
            sources.DjangoAuditLogSource()
