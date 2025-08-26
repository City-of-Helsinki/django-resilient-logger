import pytest
from django.test import override_settings

from resilient_logger.resilient_logger import ResilientLogger
from resilient_logger.utils import get_resilient_logger_config
from tests.testdata.testconfig import (
    INVALID_CONFIG_INVALID_SOURCE,
    INVALID_CONFIG_MISSING_FACTORY_TABLE_NAME,
    VALID_CONFIG_ALL_FIELDS,
    VALID_CONFIG_ALL_FIELDS_FACTORY,
)


@pytest.fixture(autouse=True)
def setup():
    get_resilient_logger_config.cache_clear()


@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_create_normal():
    ResilientLogger.create()


@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS_FACTORY)
def test_create_source_factory():
    ResilientLogger.create()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_INVALID_SOURCE)
def test_create_source_factory_invalid_source():
    with pytest.raises(TypeError) as ex:
        ResilientLogger.create()

    assert ex.match("is not sub-class of")


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_FACTORY_TABLE_NAME)
def test_create_source_factory_missing_required_prop():
    with pytest.raises(RuntimeError) as ex:
        ResilientLogger.create()

    assert ex.match(r"create is missing required fields: \[table_name\]")
