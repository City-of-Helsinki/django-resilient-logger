import logging
from base64 import b64encode
from unittest.mock import MagicMock, patch

import pytest
from elasticsearch8 import ApiError

from resilient_logger.targets import ElasticsearchLogTarget

scheme = "https"
host = "host"
port = 1234

username = "user"
password = "password"
index = "index"

credentials_string = f"{username}:{password}"
credentials_bytes = credentials_string.encode("utf-8")
expected_authorization = f"Basic {b64encode(credentials_bytes).decode('utf-8')}"


@pytest.mark.django_db
def test_create_url_complete():
    target = ElasticsearchLogTarget(
        es_url=f"{scheme}://{host}:{port}",
        es_username=username,
        es_password=password,
        es_index=index,
    )

    client = target._client
    node = client.transport.node_pool.get()
    authorization = client._headers.get("authorization")

    assert node.scheme == scheme
    assert node.host == host
    assert node.port == port
    assert target._index == index
    assert authorization == expected_authorization


@pytest.mark.django_db
def test_create_url_without_scheme():
    target = ElasticsearchLogTarget(
        es_url=f"{host}:{port}",
        es_username=username,
        es_password=password,
        es_index=index,
    )

    client = target._client
    node = client.transport.node_pool.get()
    authorization = client._headers.get("authorization")

    assert node.scheme == scheme
    assert node.host == host
    assert node.port == port
    assert target._index == index
    assert authorization == expected_authorization


@pytest.mark.django_db
def test_create_parts_with_scheme_host_port():
    target = ElasticsearchLogTarget(
        es_scheme=scheme,
        es_host=host,
        es_port=port,
        es_username=username,
        es_password=password,
        es_index=index,
    )

    client = target._client
    node = client.transport.node_pool.get()
    authorization = client._headers.get("authorization")

    assert node.scheme == scheme
    assert node.host == host
    assert node.port == port
    assert target._index == index
    assert authorization == expected_authorization


@pytest.mark.django_db
def test_create_parts_without_scheme():
    target = ElasticsearchLogTarget(
        es_host=host,
        es_port=port,
        es_username=username,
        es_password=password,
        es_index=index,
    )

    client = target._client
    node = client.transport.node_pool.get()
    authorization = client._headers.get("authorization")

    assert node.scheme == scheme
    assert node.host == host
    assert node.port == port
    assert target._index == index
    assert authorization == expected_authorization


@patch("resilient_logger.targets.elasticsearch_log_target.Elasticsearch")
def test_http_compression_is_enabled(mock_elasticsearch):
    """
    Ensure that http_compress=True is explicitly passed to the Elasticsearch client
    when es_compress is set to True.
    """
    mock_client_instance = MagicMock()
    mock_elasticsearch.return_value = mock_client_instance

    ElasticsearchLogTarget(
        es_username="test_user",
        es_password="test_password",
        es_index="test_index",
        es_host="localhost",
        es_compress=True,
    )

    mock_elasticsearch.assert_called_once()
    _, kwargs = mock_elasticsearch.call_args

    assert "http_compress" in kwargs, "http_compress keyword argument missing"
    assert kwargs["http_compress"] is True, "http_compress should be set to True"


@patch("resilient_logger.targets.elasticsearch_log_target.Elasticsearch")
def test_http_compression_is_disabled_by_default(mock_elasticsearch):
    """
    Ensure that http_compress defaults to False when es_compress is omitted.
    """
    ElasticsearchLogTarget(
        es_username="test_user",
        es_password="test_password",
        es_index="test_index",
        es_host="localhost",
    )

    # Assert
    _, kwargs = mock_elasticsearch.call_args
    assert kwargs.get("http_compress") is False, "http_compress should default to False"


@patch("resilient_logger.targets.elasticsearch_log_target.Elasticsearch")
def test_es_exception(mock_elasticsearch, caplog):
    mock_client_instance = MagicMock()
    mock_elasticsearch.return_value = mock_client_instance

    mock_meta = MagicMock()
    mock_meta.status = 500
    api_error = ApiError(
        message="Blabla",
        meta=mock_meta,
        body={"error": "Blabla"},
    )
    mock_client_instance.index.side_effect = api_error

    target = ElasticsearchLogTarget(
        es_username="test_user",
        es_password="test_password",
        es_index="test_index",
        es_host="localhost",
    )

    mock_entry = MagicMock()
    mock_entry.get_document.return_value = {"message": "exception"}
    mock_entry.get_id.return_value = "source_pk_123"

    with caplog.at_level(
        logging.ERROR, logger="resilient_logger.targets.elasticsearch_log_target"
    ):
        target.submit(mock_entry)

    assert len(caplog.records) == 1, "Expected exactly one error log record"
    log_record = caplog.records[0]

    assert log_record.levelname == "ERROR"
    assert log_record.message.startswith("Entry with key ")
    assert log_record.message.endswith("failed. Source PK: source_pk_123")


@patch("resilient_logger.targets.elasticsearch_log_target.Elasticsearch")
def test_413_payload_too_big(mock_elasticsearch, caplog):
    mock_client_instance = MagicMock()
    mock_elasticsearch.return_value = mock_client_instance

    mock_meta = MagicMock()
    mock_meta.status = 413
    api_error = ApiError(
        message="Request Entity Too Large",
        meta=mock_meta,
        body={"error": "Payload too big"},
    )
    mock_client_instance.index.side_effect = api_error

    target = ElasticsearchLogTarget(
        es_username="test_user",
        es_password="test_password",
        es_index="test_index",
        es_host="localhost",
    )

    mock_entry = MagicMock()
    mock_entry.get_document.return_value = {"message": "massive_log_payload"}
    mock_entry.get_id.return_value = "source_pk_123"

    with caplog.at_level(
        logging.ERROR, logger="resilient_logger.targets.elasticsearch_log_target"
    ):
        target.submit(mock_entry)

    assert len(caplog.records) == 1, "Expected exactly one error log record"
    log_record = caplog.records[0]

    assert log_record.levelname == "ERROR"
    assert log_record.message.startswith("Payload is too big for ")
    assert log_record.message.endswith("Source PK: source_pk_123")
