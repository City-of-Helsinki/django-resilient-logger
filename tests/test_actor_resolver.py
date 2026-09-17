import pytest

from resilient_logger.utils import parse_actor_resolver
from tests.models import DummyUser


def custom_callable_parser(user):
    return {"custom_id": f"user_{user.pk}", "email": user.email}


def custom_scalar_parser(user):
    return user.email


@pytest.fixture
def dummy_user(db):
    return DummyUser.objects.create(email="test@example.com", username="testuser")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "actor_resolver, expected_output",
    [
        (  # Direct callable returning dict
            custom_callable_parser,
            lambda u: {"custom_id": f"user_{u.pk}", "email": "test@example.com"},
        ),
        (  # Direct callable returning scalar -> wrapped
            custom_scalar_parser,
            lambda u: {"value": "test@example.com"},
        ),
        (  # String import path
            "tests.test_actor_resolver.custom_callable_parser",
            lambda u: {"custom_id": f"user_{u.pk}", "email": "test@example.com"},
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
    actor_resolver, expected_output, dummy_user
):
    actor_resolver_fn = parse_actor_resolver(actor_resolver)
    assert actor_resolver_fn(dummy_user) == expected_output(dummy_user)


def test_parse_actor_resolver_field_on_none():
    resolver = parse_actor_resolver("email")
    assert resolver(None) == {"value": None}


def test_parse_actor_resolver_none_target():
    assert parse_actor_resolver(None) is None


def test_parse_actor_resolver_invalid_type():
    with pytest.raises(TypeError, match="Invalid actor_extractor configuration type"):
        parse_actor_resolver(12345)
