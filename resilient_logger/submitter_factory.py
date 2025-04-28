from resilient_logger.abstract_log_facade import AbstractLogFacade
from resilient_logger.abstract_submitter import AbstractSubmitter
from resilient_logger.utils import dynamic_class, get_resilient_logger_config


class SubmitterFactory:
  @staticmethod
  def create() -> AbstractSubmitter:
      settings = get_resilient_logger_config()

      submitter_args = settings["submitter"].copy()
      submitter_class = submitter_args.pop('class')

      log_facade_args = settings["log_facade"].copy()
      log_facade_class = log_facade_args.pop('class')

      submitter_class = dynamic_class(AbstractSubmitter, submitter_class)
      log_facade_class = dynamic_class(AbstractLogFacade, log_facade_class)

      instance = submitter_class(**submitter_args, log_facade=log_facade_class)
      return instance
