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
    """
    _client: Elasticsearch
    _index: str

    def __init__(self,
            log_facade: Type[AbstractLogFacade],
            client: Elasticsearch,
            index: str,
            batch_limit: int = 5000,
            chunk_size: int = 500,
    ) -> None:
        super().__init__(log_facade, batch_limit, chunk_size)

        if not client:
            raise Exception(f"ElasticsearchSubmitter is missing required argument client.")

        if not index:
            raise Exception(f"ElasticsearchSubmitter is missing required argument index.")
        
        self._index = index
        self._client = client
    
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