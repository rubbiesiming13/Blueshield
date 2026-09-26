
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "timestamp",
        "user",
        "action",
        "target_model",
        "target_id",
        "ip_address",
    )

    list_filter = (
        "action",
        "target_model",
        "timestamp",
    )

    search_fields = (
        "user__username",
        "target_model",
        "target_id",
        "details",
        "ip_address",
    )

    readonly_fields = (
        "timestamp",
    )

    ordering = (
        "-timestamp",
    )

