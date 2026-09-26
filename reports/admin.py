from django.contrib import admin

from .models import MonthlyReport


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):

    list_display = (
        "report_number",
        "station",
        "district",
        "year",
        "month",
        "prepared_by",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "year",
        "month",
        "district",
        "station",
    )

    search_fields = (
        "report_number",
        "station__name",
        "district__name",
        "prepared_by__username",
        "prepared_by__badge_number",
    )

    readonly_fields = (
        "report_number",
        "created_at",
        "updated_at",
        "reviewed_at",
    )

    ordering = (
        "-year",
        "-month",
        "-created_at",
    )