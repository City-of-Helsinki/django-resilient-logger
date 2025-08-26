import logging
from contextlib import nullcontext as does_not_raise

import pytest
from django.test import override_settings

from resilient_logger.errors import MissingContextError
from resilient_logger.handlers import ResilientLogHandler
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


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_without_required_fields_with_extras():
    required_fields, extra, expectation = without_required_fields_with_extras

    logger = logging.Logger(__name__)
    logger.addHandler(
        ResilientLogHandler(logging.INFO, required_fields=required_fields)
    )

    with expectation:
        logger.info("Hello World!", extra=extra)


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_without_required_fields_without_extras():
    required_fields, extra, expectation = without_required_fields_without_extras

    logger = logging.Logger(__name__)
    logger.addHandler(
        ResilientLogHandler(logging.INFO, required_fields=required_fields)
    )

    with expectation:
        logger.info("Hello World!", extra=extra)


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_with_required_fields_with_extras():
    required_fields, extra, expectation = with_required_fields_with_extras

    logger = logging.Logger(__name__)
    logger.addHandler(
        ResilientLogHandler(logging.INFO, required_fields=required_fields)
    )

    with expectation:
        logger.info("Hello World!", extra=extra)


@pytest.mark.django_db
@override_settings(RESILIENT_LOGGER=VALID_CONFIG_ALL_FIELDS)
def test_with_required_fields_without_extras():
    required_fields, extra, expectation = with_required_fields_without_extras

    logger = logging.Logger(__name__)
    logger.addHandler(
        ResilientLogHandler(logging.INFO, required_fields=required_fields)
    )

    with expectation:
        logger.info("Hello World!", extra=extra)
