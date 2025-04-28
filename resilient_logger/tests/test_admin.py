from unittest.mock import Mock

import pytest
from django.contrib.admin import AdminSite

from resilient_logger.admin import ResilientLogEntryAdmin
from resilient_logger.models import ResilientLogEntry


@pytest.mark.django_db
def test_resilient_logger_admin_message_prettified(superuser):
    request = Mock(user=superuser)
    model_admin = ResilientLogEntryAdmin(ResilientLogEntry, AdminSite())
    assert list(model_admin.get_fields(request)) == [
        "id",
        "created_at",
        "is_sent",
        "message_prettified",
    ]


@pytest.mark.django_db
def test_resilient_logger_admin_permissions(superuser):
    request = Mock(user=superuser)
    log_entry = ResilientLogEntry.objects.create(message={})
    model_admin = ResilientLogEntryAdmin(ResilientLogEntry, AdminSite())
    # The user should have permission to view, but not modify or delete resilient logs
    assert model_admin.has_view_permission(request, log_entry)
    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_change_permission(request, log_entry)
    assert not model_admin.has_delete_permission(request, log_entry)
