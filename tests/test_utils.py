import pytest
from django.test import TestCase, override_settings

from resilient_logger.utils import get_resilient_logger_config
from tests.testdata.testconfig import (
    INVALID_CONFIG_MISSING_SOURCES,
    INVALID_CONFIG_MISSING_TARGETS,
    VALID_CONFIG_ALL_FIELDS,
    VALID_CONFIG_MISSING_OPTIONAL,
)


class TestUtils(TestCase):
    def setUp(self):
        get_resilient_logger_config.cache_clear()

    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_valid_config_all_fields(self):
        config = get_resilient_logger_config()
        assert config == VALID_CONFIG_ALL_FIELDS

    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_MISSING_OPTIONAL)
    def test_valid_config_missing_optional(self):
        config = get_resilient_logger_config()
        assert config["batch_limit"] is not None
        assert config["chunk_size"] is not None
        assert config["submit_unsent_entries"] is not None
        assert config["clear_sent_entries"] is not None

    @override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_TARGETS)
    def test_invalid_config_missing_targets(self):
        with pytest.raises(RuntimeError):
            get_resilient_logger_config()

    @override_settings(RESILIENT_LOGGER=INVALID_CONFIG_MISSING_SOURCES)
    def test_invalid_config_missing_sources(self):
        with pytest.raises(RuntimeError):
            get_resilient_logger_config()
