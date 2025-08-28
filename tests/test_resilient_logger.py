import pytest
from django.test import override_settings

from resilient_logger.models.custom_audit_log_entry import CustomAuditLogEntryModel
from resilient_logger.resilient_logger import ResilientLogger
from resilient_logger.utils import get_resilient_logger_config
from tests.testdata.testconfig import (
    INVALID_CONFIG_INVALID_SOURCE,
    INVALID_CONFIG_MISSING_TABLE_NAME,
    VALID_CONFIG_ALL_FIELDS,
    VALID_CONFIG_ALL_FIELDS_WITH_TABLE_NAME,
)


@pytest.fixture(autouse=True)
def setup():
    get_resilient_logger_config.cache_clear()
    CustomAuditLogEntryModel.init_model.cache_clear()


@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_create_normal():
    ResilientLogger.create()


@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS_WITH_TABLE_NAME)
def test_create_source_custom_props():
    ResilientLogger.create()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_INVALID_SOURCE)
def test_create_source_invalid_source_type():
    with pytest.raises(TypeError) as ex:
        ResilientLogger.create()

    assert ex.match("is not sub-class of")


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_TABLE_NAME)
def test_create_source_missing_props():
    with pytest.raises(RuntimeError) as ex:
        logger = ResilientLogger.create()
        logger.clear_sent_entries()

    assert ex.match(r"No table name found for")
