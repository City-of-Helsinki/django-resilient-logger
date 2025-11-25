import pytest

from resilient_logger.models import ResilientLogEntry
from resilient_logger.sources import ResilientLogSource
from resilient_logger.sources.resilient_log_source import (
    StructuredResilientLogEntryData,
)


@pytest.mark.django_db
def test_bulk_create_resilient_log_entries(django_assert_max_num_queries):
    with django_assert_max_num_queries(1):
        ResilientLogSource.bulk_create_structured(
            [
                StructuredResilientLogEntryData(
                    message="Hello world", extra={"index": idx}
                )
                for idx in range(10)
            ]
        )

    for idx in range(10):
        ResilientLogEntry.objects.get(message="Hello world", context__index=idx)
