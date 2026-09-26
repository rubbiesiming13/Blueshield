from django.contrib import admin

from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):

    list_display = (
        "evidence_number",
        "case",
        "evidence_type",
        "collected_by",
        "status",
        "date_collected",
    )

    list_filter = (
        "evidence_type",
        "status",
        "date_collected",
    )

    search_fields = (
        "evidence_number",
        "description",
        "case__case_number",
        "case__title",
    )

    ordering = (
        "-created_at",
    )