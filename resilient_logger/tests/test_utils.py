from django.test import override_settings
import pytest

from resilient_logger.utils import get_resilient_logger_config

valid_config_all_fields = {
    'submitter': {
        'class': 'resilient_logger.proxy_submitter.ProxySubmitter',
        'name': 'proxy-submitter'
    },
    'log_facade': {
        'class': 'resilient_logger.resilient_log_facade.ResilientLogFacade',
    },
    'jobs': {
        'submit_unsent_entries': True,
        'clear_sent_entries': True,
    }
}

valid_config_missing_jobs = {
    'submitter': {
        'class': 'resilient_logger.proxy_submitter.ProxySubmitter',
        'name': 'proxy-submitter'
    },
    'log_facade': {
        'class': 'resilient_logger.resilient_log_facade.ResilientLogFacade',
    }
}

invalid_config_missing_submitter = {
    'log_facade': {
        'class': 'resilient_logger.resilient_log_facade.ResilientLogFacade',
    },
    'jobs': {
        'submit_unsent_entries': True,
        'clear_sent_entries': True,
    }
}

invalid_config_missing_log_facade = {
    'submitter': {
        'class': 'resilient_logger.proxy_submitter.ProxySubmitter',
        'name': 'proxy-submitter'
    },
    'jobs': {
        'submit_unsent_entries': True,
        'clear_sent_entries': True,
    }
}

@override_settings(RESILIENT_LOGGER=valid_config_all_fields)
def test_valid_config_all_fields():
  config = get_resilient_logger_config()
  assert config == valid_config_all_fields

@override_settings(RESILIENT_LOGGER=valid_config_missing_jobs)
def test_valid_config_missing_jobs():
  config = get_resilient_logger_config()
  assert config == valid_config_all_fields

@override_settings(RESILIENT_LOGGER=invalid_config_missing_submitter)
def test_invalid_config_missing_submitter():
  with pytest.raises(Exception):
    get_resilient_logger_config()

@override_settings(RESILIENT_LOGGER=invalid_config_missing_log_facade)
def test_invalid_config_missing_log_facade():
  with pytest.raises(Exception):
    get_resilient_logger_config()