import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def superuser():
    User = get_user_model()  # noqa: N806
    return User.objects.create_superuser("admin", "admin@example.com", "admin")
