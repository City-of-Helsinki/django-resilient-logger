from unittest.mock import Mock

from django.test import TestCase
import pytest
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from resilient_logger.admin import ResilientLogEntryAdmin
from resilient_logger.models import ResilientLogEntry


class TestAdmin(TestCase):
    user: AbstractUser

    def setUp(self):
        User = get_user_model()  # noqa: N806
        self.user = User.objects.create_superuser("admin", "admin@example.com", "admin")

    @pytest.mark.django_db
    def test_resilient_logger_admin_message_prettified(self):
        request = Mock(user=self.user)
        model_admin = ResilientLogEntryAdmin(ResilientLogEntry, AdminSite())
        assert list(model_admin.get_fields(request)) == [
            "id",
            "is_sent",
            "level",
            "created_at",
            "message_prettified",
            "context_prettified",
        ]

    @pytest.mark.django_db
    def test_resilient_logger_admin_permissions(self):
        request = Mock(user=self.user)
        log_entry = ResilientLogEntry.objects.create(message={})
        model_admin = ResilientLogEntryAdmin(ResilientLogEntry, AdminSite())
        # The user should have permission to view, but not modify or delete resilient logs
        assert model_admin.has_view_permission(request, log_entry)
        assert not model_admin.has_add_permission(request)
        assert not model_admin.has_change_permission(request, log_entry)
        assert not model_admin.has_delete_permission(request, log_entry)
