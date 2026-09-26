from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        "complaint_number",
        "complainant_name",
        "complaint_type",
        "incident_date",
        "station",
        "reported_by",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "complaint_type",
        "station",
        "created_at",
    )

    search_fields = (
        "complaint_number",
        "complainant_name",
        "complainant_phone",
        "complaint_type",
        "incident_location",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )