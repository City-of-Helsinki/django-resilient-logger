import datetime

import pytest
from django.test import override_settings

from resilient_logger.utils import (
    get_resilient_logger_config,
    unavailable_class,
    value_as_dict,
)
from tests.testdata.testconfig import (
    INVALID_CONFIG_MISSING_SOURCES,
    INVALID_CONFIG_MISSING_TARGETS,
    VALID_CONFIG_ALL_FIELDS,
    VALID_CONFIG_MISSING_OPTIONAL,
)


@pytest.fixture(autouse=True)
def setup():
    get_resilient_logger_config.cache_clear()


@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_valid_config_all_fields():
    config = get_resilient_logger_config()
    assert config == VALID_CONFIG_ALL_FIELDS


@override_settings(RESILIENT_LOGGER=VALID_CONFIG_MISSING_OPTIONAL)
def test_valid_config_missing_optional():
    config = get_resilient_logger_config()
    assert config["batch_limit"] is not None
    assert config["chunk_size"] is not None
    assert config["submit_unsent_entries"] is not None
    assert config["clear_sent_entries"] is not None


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_TARGETS)
def test_invalid_config_missing_targets():
    with pytest.raises(RuntimeError):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_SOURCES)
def test_invalid_config_missing_sources():
    with pytest.raises(RuntimeError):
        get_resilient_logger_config()


def test_unavailable_class():
    with pytest.raises(ImportError) as ex:
        placeholder_class = unavailable_class("ClassName", ["library-name"])
        placeholder_class()

    assert ex.match("ClassName requires the optional dependencies: 'library-name'.")


def test_value_as_dict():
    as_str = "hello"
    as_dict = {"value": as_str}
    invalid = datetime.datetime(2025, 10, 10)

    assert value_as_dict(as_str) == as_dict
    assert value_as_dict(as_dict) == as_dict

    with pytest.raises(TypeError) as ex:
        value_as_dict(invalid)

    assert ex.match("Expected 'str | dict', got 'datetime'")
