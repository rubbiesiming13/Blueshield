from django.contrib import admin

from .models import CustodyRecord


@admin.register(CustodyRecord)
class CustodyRecordAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_suspect",
        "arrest",
        "get_station",
        "custody_officer",
        "status",
        "cell_number",
        "detention_start",
        "created_at",
    )

    list_filter = (
        "status",
        "arrest__station",
        "detention_start",
        "created_at",
    )

    search_fields = (
        "arrest__arrest_tracking_id",
        "arrest__occurrence_book_no",
        "arrest__suspect__first_name",
        "arrest__suspect__last_name",
        "cell_number",
        "bail_receipt_number",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(
        description="Suspect",
        ordering="arrest__suspect__last_name"
    )
    def get_suspect(self, obj):
        return obj.arrest.suspect.full_name

    @admin.display(
        description="Station",
        ordering="arrest__station"
    )
    def get_station(self, obj):
        return obj.arrest.station