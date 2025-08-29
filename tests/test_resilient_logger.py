import pytest
from django.test import override_settings

from resilient_logger.resilient_logger import ResilientLogger
from resilient_logger.utils import get_resilient_logger_config
from tests.testdata.testconfig import INVALID_CONFIG_INVALID_SOURCE


@pytest.fixture(autouse=True)
def setup():
    get_resilient_logger_config.cache_clear()


def test_create_normal():
    ResilientLogger.create()


@override_settings(RESILIENT_LOGGER=INVALID_CONFIG_INVALID_SOURCE)
def test_create_source_invalid_source_type():
    with pytest.raises(TypeError) as ex:
        logger = ResilientLogger.create()
        logger.clear_sent_entries()

    assert ex.match("is not sub-class of")
