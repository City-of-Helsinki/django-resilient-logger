import logging
from typing import Optional, Type, override

from elasticsearch import Elasticsearch

from resilient_logger.abstract_log_facade import AbstractLogFacade
from resilient_logger.abstract_submitter import AbstractSubmitter

logger = logging.getLogger(__name__)

# Constants
ES_STATUS_CREATED = "created"

class ElasticsearchSubmitter(AbstractSubmitter):
    """
    Submitter class that sends the resilient log entries to Elasticsearch.
    Every other argument should be provided by user, log_facade is provided
    by ResilientLogHandler's constructor after loading and validating it.
    """
    _client: Elasticsearch
    _index: str

    def __init__(self,
            log_facade: Type[AbstractLogFacade],
            es_host: str,
            es_port: int,
            es_scheme: str,
            es_username: str,
            es_password: str,
            es_index: str,
            batch_limit: int = 5000,
            chunk_size: int = 500,
    ) -> None:
        super().__init__(log_facade, batch_limit, chunk_size)

        elasticsearch_host = {"host": es_host, "port": es_port, "scheme": es_scheme}
        elasticsearch_auth = (es_username, es_password)

        self._index = es_index
        self._client = Elasticsearch([elasticsearch_host], basic_auth=elasticsearch_auth)

    @override
    def _submit_entry(self, entry: AbstractLogFacade) -> Optional[str]:
        document = entry.get_context()
        document["level"] = entry.get_level()
        document["message"] = entry.get_message()

        response = self._client.index(
            index=self._index,
            id=str(entry.get_id()),
            document=document,
            op_type="create",
        )

        logger.info(f"Sending status: {response}")

        if response.get("result") == ES_STATUS_CREATED:
            return response.get("_id")

        return None
