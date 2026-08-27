import pytest
from logger_extra.logger_context import logger_context

from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import ResilientLogSource
from resilient_logger.sources.resilient_log_source import (
    ResilientLogEntryData,
    StructuredResilientLogEntryData,
)
from resilient_logger.sources.resilient_log_source_entry import ResilientLogSourceEntry


@pytest.mark.django_db
def test_bulk_create_structured_injects_logger_context(
    django_assert_max_num_queries,
):
    with logger_context({"ctx_key": "ctx_value"}):
        with django_assert_max_num_queries(1):
            ResilientLogSource.bulk_create_structured(
                [
                    StructuredResilientLogEntryData(
                        message="Hello world",
                        extra={"index": idx},
                        actor={"user_id": idx, "role": "test"},
                        target={"id": idx},
                    )
                    for idx in range(10)
                ]
            )

    for idx in range(10):
        obj = ResilientLogEntry.objects.get(message="Hello world", context__index=idx)
        entry = ResilientLogSourceEntry(obj)
        event = entry.get_document().get("audit_event") or {}

        assert event.get("actor") == {"user_id": idx, "role": "test"}
        assert event.get("target") == {"id": idx}

        actual_extra = event.get("extra") or {}
        assert actual_extra | {"index": idx, "ctx_key": "ctx_value"} == actual_extra


@pytest.mark.django_db
def test_bulk_create_raw_injects_logger_context(django_assert_max_num_queries):
    with logger_context({"ambient_key": "ambient_val"}):
        with django_assert_max_num_queries(1):
            ResilientLogSource.bulk_create(
                [
                    ResilientLogEntryData(
                        level=20,
                        message="Raw batch item",
                        context={"item_idx": idx},
                    )
                    for idx in range(5)
                ]
            )

    for idx in range(5):
        obj = ResilientLogEntry.objects.get(
            message="Raw batch item", context__item_idx=idx
        )
        entry = ResilientLogSourceEntry(obj)
        event = entry.get_document().get("audit_event") or {}

        actual_extra = event.get("extra") or {}
        assert (
            actual_extra | {"ambient_key": "ambient_val", "item_idx": idx}
            == actual_extra
        )


@pytest.mark.django_db
def test_bulk_create_raw_precedence_and_empty_list():
    # 1. Precedence test: explicit item context overrides ambient keys
    with logger_context({"conflict_key": "ambient", "shared_key": "keep_me"}):
        ResilientLogSource.bulk_create(
            [
                ResilientLogEntryData(
                    level=10,
                    message="Collision raw item",
                    context={"conflict_key": "explicit"},
                )
            ]
        )

    obj = ResilientLogEntry.objects.get(message="Collision raw item")
    entry = ResilientLogSourceEntry(obj)
    event = entry.get_document().get("audit_event") or {}

    actual_extra = event.get("extra") or {}
    assert (
        actual_extra | {"conflict_key": "explicit", "shared_key": "keep_me"}
        == actual_extra
    )

    # 2. Edge case: passing an empty iterable should complete cleanly
    created_entries = ResilientLogSource.bulk_create([])
    assert list(created_entries) == []


@pytest.mark.django_db
def test_bulk_create_structured_logger_context_precedence():
    ambient_context = {
        "operation": "AMBIENT_OP",
        "actor": {"user_id": 999, "role": "ambient"},
        "ctx_key": "ctx_value",
    }

    with logger_context(ambient_context):
        ResilientLogSource.bulk_create_structured(
            [
                StructuredResilientLogEntryData(
                    message="Collision test",
                    operation="EXPLICIT_OP",
                    actor={"user_id": 1, "role": "explicit"},
                    extra={"custom_extra": "foo"},
                )
            ]
        )

    obj = ResilientLogEntry.objects.get(message="Collision test")
    entry = ResilientLogSourceEntry(obj)
    doc = entry.get_document()
    event = doc.get("audit_event") or {}

    # Explicit fields take precedence
    assert event.get("operation") == "EXPLICIT_OP"
    assert event.get("actor") == {"user_id": 1, "role": "explicit"}

    # Context variables merge into extra
    actual_extra = event.get("extra") or {}
    assert (
        actual_extra | {"ctx_key": "ctx_value", "custom_extra": "foo"} == actual_extra
    )


@pytest.mark.django_db
def test_single_create_paths_inject_logger_context():
    with logger_context({"trace_id": "abc-123"}):
        # 1. Standard create()
        ResilientLogSource.create(
            level=20,
            message="Single raw log",
            context={"user_ip": "127.0.0.1"},
        )

        # 2. Structured create_structured()
        ResilientLogSource.create_structured(
            message="Single structured log",
            level=30,
            operation="UPDATE",
            actor={"id": 42},
            extra={"feature_flag": True},
        )

    # Verify standard create()
    raw_obj = ResilientLogEntry.objects.get(message="Single raw log")
    raw_entry = ResilientLogSourceEntry(raw_obj)
    raw_event = raw_entry.get_document().get("audit_event") or {}

    raw_extra = raw_event.get("extra") or {}
    assert raw_extra | {"trace_id": "abc-123", "user_ip": "127.0.0.1"} == raw_extra

    # Verify create_structured()
    struct_obj = ResilientLogEntry.objects.get(message="Single structured log")
    struct_entry = ResilientLogSourceEntry(struct_obj)
    struct_event = struct_entry.get_document().get("audit_event") or {}

    assert struct_event.get("operation") == "UPDATE"
    assert struct_event.get("actor") == {"id": 42}
    assert struct_event.get("target") == {}

    struct_extra = struct_event.get("extra") or {}
    assert struct_extra | {"trace_id": "abc-123", "feature_flag": True} == struct_extra


@pytest.mark.django_db
def test_bulk_create_structured_with_none_fields():
    with logger_context({"env": "test"}):
        ResilientLogSource.bulk_create_structured(
            [
                StructuredResilientLogEntryData(
                    message="Sparse payload",
                    actor=None,
                    target=None,
                    extra=None,
                )
            ]
        )

    obj = ResilientLogEntry.objects.get(message="Sparse payload")
    entry = ResilientLogSourceEntry(obj)
    doc = entry.get_document()
    event = doc.get("audit_event") or {}

    assert event.get("operation") == "MANUAL"
    assert event.get("actor") == {}
    assert event.get("target") == {}

    actual_extra = event.get("extra") or {}
    assert actual_extra | {"env": "test"} == actual_extra
