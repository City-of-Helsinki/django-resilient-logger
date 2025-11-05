import logging
from urllib.parse import urlparse

from elasticsearch import ConflictError, Elasticsearch

from resilient_logger.sources import AbstractLogSource
from resilient_logger.targets import AbstractLogTarget
from resilient_logger.utils import content_hash

# Constants
ES_STATUS_CREATED = "created"

logger = logging.getLogger(__name__)


class ElasticsearchLogTarget(AbstractLogTarget):
    """
    Log target that sends entries to Elasticsearch.

    The constructor requires connection details, including `es_username`, `es_password`,
    and `es_index`.

    You can specify the connection using either a full `es_url` or separate fields:
    `es_host`, `es_port`, and `es_scheme`.

    If `es_url` is provided but lacks a scheme or port, the values from `es_scheme` and
    `es_port` will be used.

    Defaults:
    - `es_scheme`: https
    - `es_port`: 9200
    """

    def __init__(
        self,
        *,
        es_username: str,
        es_password: str,
        es_index: str,
        es_url: str | None = None,
        es_host: str | None = None,
        es_port: int | None = 9200,
        es_scheme: str | None = "https",
        required: bool = True,
    ) -> None:
        super().__init__(required)

        if not es_url:
            scheme = es_scheme
            host = es_host
            port = es_port
        else:
            if "://" not in es_url:
                es_url = f"{es_scheme}://{es_url}"

            parsed = urlparse(es_url)
            scheme: str | None = parsed.scheme
            host: str | None = parsed.hostname
            port: int | None = parsed.port or es_port

        self._index = es_index
        self._client = Elasticsearch(
            [{"host": host, "port": port, "scheme": scheme}],
            basic_auth=(es_username, es_password),
        )

    def submit(self, entry: AbstractLogSource) -> bool:
        document = entry.get_document()
        hash = content_hash(document)

        try:
            response = self._client.index(
                index=self._index,
                id=hash,
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
            logger.warning(
                f"""Skipping the document with key {hash}, it's already submitted.""",
                extra=document,
            )

            return True
        except Exception:
            """
            Unknown exception, log it and keep going to avoid transaction rollbacks.
            """
            logger.exception(f"Entry with key {hash} failed.")

        return False
