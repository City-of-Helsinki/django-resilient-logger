import datetime

import pytest
from django.test import override_settings

from resilient_logger.utils import (
    get_resilient_logger_config,
    unavailable_class,
    value_as_dict,
)
from tests.testdata.testconfig import (
    INVALID_CONFIG_EMPTY_ENVIRONMENT,
    INVALID_CONFIG_EMPTY_ORIGIN,
    INVALID_CONFIG_EMPTY_SOURCES,
    INVALID_CONFIG_EMPTY_TARGETS,
    INVALID_CONFIG_MISSING_ENVIRONMENT,
    INVALID_CONFIG_MISSING_ORIGIN,
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
    with pytest.raises(RuntimeError, match="missing required key: 'targets'"):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_EMPTY_TARGETS)
def test_invalid_config_empty_targets():
    with pytest.raises(
        RuntimeError, match=r"RESILIENT_LOGGER\['targets'\] failed validation"
    ):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_SOURCES)
def test_invalid_config_missing_sources():
    with pytest.raises(RuntimeError, match="missing required key: 'sources'"):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_EMPTY_SOURCES)
def test_invalid_config_empty_sources():
    with pytest.raises(
        RuntimeError, match=r"RESILIENT_LOGGER\['sources'\] failed validation"
    ):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_ENVIRONMENT)
def test_invalid_config_missing_environment():
    with pytest.raises(RuntimeError, match="missing required key: 'environment'"):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_EMPTY_ENVIRONMENT)
def test_invalid_config_empty_environment():
    with pytest.raises(
        RuntimeError, match=r"RESILIENT_LOGGER\['environment'\] failed validation"
    ):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_ORIGIN)
def test_invalid_config_missing_origin():
    with pytest.raises(RuntimeError, match="missing required key: 'origin'"):
        get_resilient_logger_config()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_EMPTY_ORIGIN)
def test_invalid_config_empty_origin():
    with pytest.raises(
        RuntimeError, match=r"RESILIENT_LOGGER\['origin'\] failed validation"
    ):
        get_resilient_logger_config()


def test_unavailable_class():
    with pytest.raises(
        ImportError,
        match="ClassName requires the optional dependencies: 'library-name'.",
    ):
        placeholder_class = unavailable_class("ClassName", ["library-name"])
        placeholder_class()


def test_value_as_dict():
    as_str = "hello"
    as_dict = {"value": as_str}
    invalid = datetime.datetime(2025, 10, 10)

    assert value_as_dict(as_str) == as_dict
    assert value_as_dict(as_dict) == as_dict

    with pytest.raises(TypeError) as ex:
        value_as_dict(invalid)

    assert ex.match("Expected 'str | dict', got 'datetime'")
