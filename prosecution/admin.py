from django.contrib import admin

from .models import Prosecution


@admin.register(Prosecution)
class ProsecutionAdmin(admin.ModelAdmin):

    list_display = (
        "prosecution_number",
        "case",
        "investigation",
        "prosecutor",
        "status",
        "committal_status",
        "summary_trial_status",
        "forwarded_to_court",
        "created_at",
    )

    list_filter = (
        "status",
        "committal_status",
        "summary_trial_status",
        "forwarded_to_court",
        "created_at",
    )

    search_fields = (
        "prosecution_number",
        "case__case_number",
        "case__title",
        "investigation__investigation_number",
    )

    ordering = (
        "-created_at",
    )