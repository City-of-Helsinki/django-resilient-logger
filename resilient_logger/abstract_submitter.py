import logging
import os
from abc import abstractmethod
from typing import Any, Dict, Generator, List, Optional, Type, TypedDict

from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction

from resilient_logger.abstract_log_facade import AbstractLogFacade

logger = logging.getLogger(__name__)

class IntervalOptions(TypedDict):
    """
    Defines internal format for apscheduler trigger definitions (trigger, trigger_args).
    See: https://apscheduler.readthedocs.io/en/3.x/modules/schedulers/base.html#apscheduler.schedulers.base.BaseScheduler.add_job
    """
    trigger: str
    args: Dict[str, Any]

_default_submit_unsent_entries_trigger = IntervalOptions({
    'trigger': 'interval',
    'args': { 'minutes': 15 }
})

_default_clear_sent_entries_trigger = IntervalOptions({
    'trigger': 'cron',
    'args': {
        'month':"*",
        'day': "1",
        'hour': "0",
        'minute': "0",
        'second': "0",
    }
})

class AbstractSubmitter:
    """
    Abstract base class for different submitters. By design, does not use
    any implementation specific storages or submit targets. Those are defined
    by sub-classes and runtime provided log_facade class.
    """
    _batch_limit: int
    _chunk_size: int
    _log_facade: Type[AbstractLogFacade]

    def __init__(
            self,
            log_facade: Type[AbstractLogFacade],
            batch_limit: int = 5000,
            chunk_size: int = 500,
            submit_unsent_entries_trigger: Optional[IntervalOptions] =
                _default_submit_unsent_entries_trigger,
            clear_sent_entries_trigger: Optional[IntervalOptions] =
                _default_clear_sent_entries_trigger,
    ) -> None:
        self._log_facade = log_facade
        self._batch_limit = batch_limit
        self._chunk_size = chunk_size

        if not submit_unsent_entries_trigger:
            logger.info("Skipping submit_entries scheduling.")

        if not clear_sent_entries_trigger:
            logger.info("Skipping clear_old_entries scheduling.")

        have_some_trigger = submit_unsent_entries_trigger or clear_sent_entries_trigger

        if have_some_trigger and self.should_schedule():
            scheduler = BackgroundScheduler()
            scheduler.start()

            if submit_unsent_entries_trigger:
                scheduler.add_job(
                    self.submit_unsent_entries,
                    id="submit_unsent_entries",
                    name="submit_unsent_entries",
                    max_instances=1,
                    replace_existing=True,
                    trigger=submit_unsent_entries_trigger.get('trigger'),
                    **submit_unsent_entries_trigger.get('args'),
                )

            if clear_sent_entries_trigger:
                scheduler.add_job(
                    self.clear_sent_entries,
                    id="clear_sent_entries",
                    name="clear_sent_entries",
                    max_instances=1,
                    replace_existing=True,
                    trigger=clear_sent_entries_trigger.get('trigger'),
                    **clear_sent_entries_trigger.get('args'),
                )

    @abstractmethod
    def _submit_entry(self, entry: AbstractLogFacade) -> Optional[str]:
        """
        This method is different for each submitter,
        so it's required to override this.
        """
        return NotImplemented

    @transaction.atomic
    def submit_entry(self, entry: AbstractLogFacade) -> Optional[str]:
        result_id = self._submit_entry(entry)
        if result_id is not None:
            entry.mark_sent()
            return result_id

        return None

    def submit(self, level: int, message: Any, context: Any) -> Optional[str]:
        entry = self.get_log_facade().create(level, message, context)
        return self.submit_entry(entry)

    @transaction.atomic
    def submit_unsent_entries(self) -> Optional[List[str]]:
        result_ids: List[str] = []

        for count, entry in enumerate(self.get_unsent_entries()):
            if count >= self._batch_limit:
                logger.info(f"Job limit of {self._batch_limit} logs reached.")
                break

            result_id = self.submit_entry(entry)

            if result_id is not None:
                entry.mark_sent()
                result_ids.append(result_id)

        return result_ids

    def get_unsent_entries(self) -> Generator[AbstractLogFacade, None, None]:
        return self.get_log_facade().get_unsent_entries(self._chunk_size)

    def clear_sent_entries(self, days_to_keep: int = 30) -> None:
        return self.get_log_facade().clear_sent_entries(days_to_keep)

    def get_log_facade(self) -> Type[AbstractLogFacade]:
        if not self._log_facade:
            raise Exception("self._log_facade is None, cannot proceed without it.")

        return self._log_facade

    @staticmethod
    def should_schedule():
        if os.environ.get("SUBMITTER_SCHEDULED", None) is None:
            os.environ['SUBMITTER_SCHEDULED'] = 'True'
            return True

        return False
