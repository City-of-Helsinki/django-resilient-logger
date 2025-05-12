from typing import override

from elasticsearch import Elasticsearch

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.abstract_log_target import AbstractLogTarget
import logging

# Constants
ES_STATUS_CREATED = "created"

logger = logging.getLogger(__name__)


class ElasticsearchLogTarget(AbstractLogTarget):
    """
    Log target that sends entries to Elasticsearch.
    """

    _client: Elasticsearch
    _index: str

    def __init__(
        self,
        es_host: str,
        es_port: int,
        es_scheme: str,
        es_username: str,
        es_password: str,
        es_index: str,
        required: bool = True,
    ) -> None:
        super().__init__(required)

        self._index = es_index
        self._client = Elasticsearch(
            [{"host": es_host, "port": es_port, "scheme": es_scheme}],
            basic_auth=(es_username, es_password),
        )

    @override
    def submit(self, entry: AbstractLogSource) -> bool:
        document = entry.get_context()
        message = entry.get_message()
        log_level = entry.get_level()

        if message is not None:
            document["message"] = message

        if log_level is not None:
            document["log_level"] = log_level

        response = self._client.index(
            index=self._index,
            id=str(entry.get_id()),
            document=document,
            op_type="create",
        )

        logger.info(f"Sending status: {response}")

        if response.get("result") == ES_STATUS_CREATED:
            return True

        return False
