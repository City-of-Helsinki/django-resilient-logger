from base64 import b64encode

import pytest

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
