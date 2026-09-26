from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Division


# ============================================================
# DIVISION ADMIN
# ============================================================

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "description",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )


# ============================================================
# USER ADMIN
# ============================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "badge_number",
        "get_full_name",
        "role",
        "rank",
        "district",
        "station",
        "division",
        "sevispass_verified",
        "is_active",
    )

    list_filter = (
        "role",
        "district",
        "station",
        "division",
        "sevispass_verified",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "badge_number",
        "email",
        "sevispass_id",
    )

    ordering = (
        "last_name",
        "first_name",
    )

    # ========================================================
    # EDIT EXISTING USER
    # ========================================================

    fieldsets = (

        (
            "Login Information",
            {
                "fields": (
                    "username",
                    "password",
                )
            }
        ),

        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                )
            }
        ),

        (
            "Police and Assignment Information",
            {
                "fields": (
                    "badge_number",
                    "rank",
                    "role",
                    "district",
                    "station",
                    "division",
                )
            }
        ),

        (
            "SevisPass Verification",
            {
                "fields": (
                    "sevispass_id",
                    "sevispass_verified",
                    "sevispass_verified_at",
                )
            }
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            }
        ),

        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            }
        ),
    )

    # ========================================================
    # ADD NEW USER
    # ========================================================

    add_fieldsets = (

        (
            None,
            {
                "classes": ("wide",),

                "fields": (

                    # Login
                    "username",
                    "password1",
                    "password2",

                    # Personal
                    "first_name",
                    "last_name",
                    "email",

                    # Police
                    "badge_number",
                    "rank",
                    "role",

                    # Assignment
                    "district",
                    "station",
                    "division",

                    # SevisPass
                    "sevispass_id",
                    "sevispass_verified",
                ),
            }
        ),
    )

    readonly_fields = (
        "last_login",
        "date_joined",
    )