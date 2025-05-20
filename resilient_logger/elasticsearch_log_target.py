import logging

from elasticsearch import ConflictError, Elasticsearch

from resilient_logger.abstract_log_source import AbstractLogSource
from resilient_logger.abstract_log_target import AbstractLogTarget
from resilient_logger.utils import content_hash, create_target_document

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

    def submit(self, entry: AbstractLogSource) -> bool:
        document = create_target_document(entry)

        try:
            response = self._client.index(
                index=self._index,
                id=content_hash(document),
                document=document,
                op_type="create",
            )

            logger.info(f"Sending status: {response}")
            result = response["result"]

            if result == ES_STATUS_CREATED:
                return True

        except ConflictError:
            """
            The document key used to store log entry is the hash of the contents.
            If we receive conflict error, it means that the given entry is already
            sent to the Elasticsearch.
            """
            return True

        return False
