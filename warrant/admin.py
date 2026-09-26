from django.contrib import admin
from .models import Warrant


@admin.register(Warrant)
class WarrantAdmin(admin.ModelAdmin):

    list_display = (
        "warrant_number",
        "warrant_type",
        "suspect",
        "station",
        "status",
        "requested_by",
        "approved_by",
        "issue_date",
        "expiry_date",
    )

    list_filter = (
        "status",
        "warrant_type",
        "station",
    )

    search_fields = (
        "warrant_number",
        "suspect__first_name",
        "suspect__last_name",
    )
