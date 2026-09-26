from django.contrib import admin

from .models import District, PoliceStation


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "province",
        "is_active",
        "created_at",
    )

    list_filter = (
        "province",
        "is_active",
    )

    search_fields = (
        "name",
        "province",
    )

    ordering = (
        "name",
    )


@admin.register(PoliceStation)
class PoliceStationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "district",
        "province",
        "commander_name",
        "phone_number",
        "is_active",
    )

    list_filter = (
        "district",
        "province",
        "is_active",
    )

    search_fields = (
        "name",
        "district__name",
        "commander_name",
        "phone_number",
    )

    ordering = (
        "district__name",
        "name",
    )