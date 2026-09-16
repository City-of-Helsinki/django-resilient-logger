import pytest

from resilient_logger.utils import parse_actor_resolver
from tests.models import DummyUser


def custom_callable_parser(user):
    return {"custom_id": f"user_{user.pk}", "email": user.email}


def custom_scalar_parser(user):
    return user.email


@pytest.fixture
def dummy_user():
    user = DummyUser.objects.create(email="test@example.com", username="testuser")
    return user


def test_parse_actor_resolver_none():
    extractor = parse_actor_resolver(None)
    assert extractor is None


@pytest.mark.django_db
def test_parse_actor_resolver_callable_dict(dummy_user):
    extractor = parse_actor_resolver(custom_callable_parser)
    assert extractor(dummy_user) == {
        "custom_id": f"user_{dummy_user.pk}",
        "email": dummy_user.email,
    }


@pytest.mark.django_db
def test_parse_actor_resolver_callable_scalar(dummy_user):
    extractor = parse_actor_resolver(custom_scalar_parser)
    assert extractor(dummy_user) == {"value": dummy_user.email}


@pytest.mark.django_db
def test_parse_actor_resolver_import_path(dummy_user):
    extractor = parse_actor_resolver("tests.test_actor_resolver.custom_callable_parser")
    assert extractor(dummy_user) == {
        "custom_id": f"user_{dummy_user.pk}",
        "email": dummy_user.email,
    }


@pytest.mark.django_db
def test_parse_actor_resolver_field_string(dummy_user):
    extractor = parse_actor_resolver("email")
    assert extractor(dummy_user) == {"value": dummy_user.email}


@pytest.mark.django_db
def test_parse_actor_resolver_missing_field(dummy_user):
    extractor = parse_actor_resolver("non_existent_field")
    assert extractor(dummy_user) == {"value": None}


@pytest.mark.django_db
def test_parse_actor_resolver_none_user():
    extractor = parse_actor_resolver("email")
    assert extractor(None) == {"value": None}


@pytest.mark.django_db
def test_parse_actor_resolver_invalid_type():
    with pytest.raises(TypeError, match="Invalid actor_extractor configuration type"):
        parse_actor_resolver(12345)
