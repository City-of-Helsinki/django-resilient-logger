import logging
from typing import Generator, TypeVar

from django.db import transaction

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.abstract_log_target import AbstractLogTarget
from resilient_logger.utils import dynamic_class, get_resilient_logger_config

logger = logging.getLogger(__name__)

TResilientLogger = TypeVar("ResilientLogger")


class ResilientLogger:
    _batch_limit: int
    _chunk_size: int
    _log_sources: list[type[AbstractLogSource]]
    _log_targets: list[AbstractLogTarget]

    def __init__(
        self,
        batch_limit: int,
        chunk_size: int,
        log_sources: list[type[AbstractLogSource]],
        log_targets: list[AbstractLogTarget],
    ) -> None:
        self._batch_limit = batch_limit
        self._chunk_size = chunk_size
        self._log_sources = log_sources
        self._log_targets = log_targets

    @classmethod
    def create(cls: TResilientLogger) -> TResilientLogger:
        settings = get_resilient_logger_config()
        batch_limit = settings.get("batch_limit")
        chunk_size = settings.get("chunk_size")
        sources = settings.get("sources", []).copy()
        targets = settings.get("targets", []).copy()

        list_sources: list[type[AbstractLogSource]] = []
        list_targets: list[AbstractLogTarget] = []

        for source in sources:
            source_args = source.copy()
            source_class_name = source_args.pop("class", None)
            source_class = dynamic_class(AbstractLogSource, source_class_name)
            list_sources.append(source_class)

        for target in targets:
            target_args = target.copy()
            target_class_name = target_args.pop("class", None)
            target_class = dynamic_class(AbstractLogTarget, target_class_name)
            list_targets.append(target_class(**target_args))

        return cls(
            batch_limit=batch_limit,
            chunk_size=chunk_size,
            log_sources=list_sources,
            log_targets=list_targets,
        )

    @transaction.atomic
    def submit(self, source: AbstractLogSource) -> bool:
        for log_target in self._log_targets:
            submitted = log_target.submit(source)

            if not submitted and log_target.is_required():
                return False

        return True

    @transaction.atomic
    def submit_unsent_entries(self) -> dict[str, bool]:
        results: dict[str, bool] = {}

        for count, entry in enumerate(self.get_unsent_entries()):
            if count >= self._batch_limit:
                logger.info(f"Job limit of {self._batch_limit} logs reached.")
                break

            result = self.submit(entry)
            results[entry.get_id()] = result

            if result:
                entry.mark_sent()

        return results

    def get_unsent_entries(self) -> Generator[AbstractLogSource, None, None]:
        for log_source in self._log_sources:
            for entry in log_source.get_unsent_entries(self._chunk_size):
                yield entry

    def clear_sent_entries(self, days_to_keep: int = 30) -> list[str]:
        deleted_ids: list[str] = []

        for log_source in self._log_sources:
            deleted_ids += log_source.clear_sent_entries(days_to_keep)

        return deleted_ids
