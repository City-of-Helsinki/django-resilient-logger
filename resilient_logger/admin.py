import json
import logging

from django.contrib import admin
from django.core.paginator import Paginator
from django.utils.html import escape
from django.utils.safestring import mark_safe

from resilient_logger.models import ResilientLogEntry

logger = logging.getLogger(__name__)

@admin.register(ResilientLogEntry)
class ResilientLogEntryAdmin(admin.ModelAdmin):
    exclude = ("message",)
    readonly_fields = ("id", "created_at", "is_sent", "message_prettified")
    list_display = ("id", "__str__", "created_at", "is_sent")
    list_filter = ("created_at", "is_sent")

    # For increasing listing performance
    show_full_result_count = False
    paginator = Paginator

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
