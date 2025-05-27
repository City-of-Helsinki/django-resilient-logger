import json
import logging

from django.contrib import admin
from django.utils.html import escape
from django.utils.safestring import mark_safe

from resilient_logger.models import ResilientLogEntry

logger = logging.getLogger(__name__)


@admin.register(ResilientLogEntry)
class ResilientLogEntryAdmin(admin.ModelAdmin):
    exclude = ("message", "context")
    readonly_fields = (
        "id",
        "is_sent",
        "level",
        "created_at",
        "message_prettified",
        "context_prettified",
    )
    list_display = ("id", "__str__", "created_at", "is_sent")
    list_filter = ("created_at", "is_sent")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="message")
    def message_prettified(self, instance):
        """Format the message to be a bit a more user-friendly."""
        message = json.dumps(instance.message, indent=2, sort_keys=True)
        content = f"<pre>{escape(message)}</pre>"
        return mark_safe(content)

    @admin.display(description="context")
    def context_prettified(self, instance):
        """Format the context to be a bit a more user-friendly."""
        context = json.dumps(instance.context, indent=2, sort_keys=True)
        content = f"<pre>{escape(context)}</pre>"
        return mark_safe(content)
