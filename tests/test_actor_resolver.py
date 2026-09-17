import pytest
from django.db import models

from resilient_logger.utils import get_user_value, parse_actor_resolver
from tests.models import DummyUser


def custom_callable_parser(user: models.Model | dict) -> dict:
    pk = get_user_value(user, "pk")
    email = get_user_value(user, "email")
    return {"custom_id": f"user_{pk}", "email": email}


def custom_scalar_parser(user: models.Model):
    return get_user_value(user, "email")


@pytest.fixture
def dummy_orm_user():
    return DummyUser.objects.create(email="test@example.com", username="testuser")


@pytest.fixture
def dummy_dict_user():
    return {"email": "test@example.com", "username": "testuser"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "actor_resolver, expected_output",
    [
        (  # Direct callable returning dict
            custom_callable_parser,
            lambda u: {
                "custom_id": f"user_{get_user_value(u, 'pk')}",
                "email": "test@example.com",
            },
        ),
        (  # Direct callable returning scalar -> wrapped
            custom_scalar_parser,
            lambda u: {"value": "test@example.com"},
        ),
        (  # String import path
            "tests.test_actor_resolver.custom_callable_parser",
            lambda u: {
                "custom_id": f"user_{get_user_value(u, 'pk')}",
                "email": "test@example.com",
            },
        ),
        (  # Direct model field string -> wrapped
            "email",
            lambda u: {"value": "test@example.com"},
        ),
        (  # Non-existent model field -> wrapped None
            "non_existent_field",
            lambda u: {"value": None},
        ),
    ],
)
def test_parse_actor_resolver_valid_targets(
    actor_resolver, expected_output, dummy_orm_user, dummy_dict_user
):
    actor_resolver_fn = parse_actor_resolver(actor_resolver)
    assert actor_resolver_fn(dummy_orm_user) == expected_output(dummy_orm_user)
    assert actor_resolver_fn(dummy_dict_user) == expected_output(dummy_dict_user)


def test_parse_actor_resolver_field_on_none():
    resolver = parse_actor_resolver("email")
    assert resolver(None) == {"value": None}


def test_parse_actor_resolver_none_target():
    assert parse_actor_resolver(None) is None


def test_parse_actor_resolver_invalid_type():
    with pytest.raises(TypeError, match="Invalid actor_extractor configuration type"):
        parse_actor_resolver(12345)
