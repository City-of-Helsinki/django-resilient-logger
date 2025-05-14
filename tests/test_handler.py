import logging
from contextlib import nullcontext as does_not_raise

import pytest
from django.test import TestCase, override_settings

from resilient_logger.handlers import ResilientLogHandler
from resilient_logger.missing_context_error import MissingContextError
from tests.testdata.testconfig import (
    VALID_CONFIG_ALL_FIELDS,
)

without_required_fields_with_extras = ([], {"foo": "bar"}, does_not_raise())
without_required_fields_without_extras = ([], {}, does_not_raise())
with_required_fields_with_extras = (["foo"], {"foo": "bar"}, does_not_raise())
with_required_fields_without_extras = (
    ["foo"],
    {},
    pytest.raises(MissingContextError),
)


class TestHandler(TestCase):
    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_without_required_fields_with_extras(self):
        required_fields, extra, expectation = without_required_fields_with_extras

        logger = logging.Logger(__name__)
        logger.addHandler(
            ResilientLogHandler(logging.INFO, required_fields=required_fields)
        )

        with expectation:
            logger.info("Hello World!", extra=extra)

    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_without_required_fields_without_extras(self):
        required_fields, extra, expectation = without_required_fields_without_extras

        logger = logging.Logger(__name__)
        logger.addHandler(
            ResilientLogHandler(logging.INFO, required_fields=required_fields)
        )

        with expectation:
            logger.info("Hello World!", extra=extra)

    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_with_required_fields_with_extras(self):
        required_fields, extra, expectation = with_required_fields_with_extras

        logger = logging.Logger(__name__)
        logger.addHandler(
            ResilientLogHandler(logging.INFO, required_fields=required_fields)
        )

        with expectation:
            logger.info("Hello World!", extra=extra)

    @override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
    def test_with_required_fields_without_extras(self):
        required_fields, extra, expectation = with_required_fields_without_extras

        logger = logging.Logger(__name__)
        logger.addHandler(
            ResilientLogHandler(logging.INFO, required_fields=required_fields)
        )

        with expectation:
            logger.info("Hello World!", extra=extra)
