import pytest
from django.test import override_settings

from resilient_logger.utils import get_resilient_logger_config
from tests.testdata.testconfig import (
    INVALID_CONFIG_MISSING_SOURCES,
    INVALID_CONFIG_MISSING_TARGETS,
    VALID_CONFIG_MISSING_OPTIONAL,
)


@pytest.fixture(autouse=True)
def setup():
    get_resilient_logger_config.cache_clear()


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
