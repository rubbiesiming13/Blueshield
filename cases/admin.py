from django.contrib import admin
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):

    list_display = (
        "case_number",
        "title",
        "suspect",
        "offence",
        "investigating_officer",
        "station",
        "status",
        "incident_date",
    )

    list_filter = (
        "status",
        "station",
        "offence",
    )

    search_fields = (
        "case_number",
        "title",
        "suspect__first_name",
        "suspect__last_name",
    )
